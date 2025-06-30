"""
Sync engine for coordinating synchronization between local and remote reference managers.
Handles conflict resolution, bulk operations, and sync monitoring.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User

from apps.scholar_app.models import SearchIndex, Author, Journal, Topic
from ..models import (
    ReferenceManagerAccount,
    SyncProfile,
    SyncSession,
    ReferenceMapping,
    ConflictResolution,
    SyncLog,
    SyncStatistics
)
from .base_service import BaseReferenceService, ReferenceServiceException
from .mendeley_service import MendeleyService
from .zotero_service import ZoteroService


logger = logging.getLogger(__name__)


class SyncEngine:
    """
    Main synchronization engine that coordinates sync operations
    between local Scholar database and external reference managers.
    """
    
    def __init__(self, sync_profile: SyncProfile):
        """
        Initialize sync engine with a sync profile.
        
        Args:
            sync_profile: SyncProfile instance defining sync settings
        """
        self.profile = sync_profile
        self.user = sync_profile.user
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # Initialize services for all accounts in the profile
        self.services = {}
        for account in sync_profile.accounts.filter(is_active=True):
            service = self._create_service(account)
            if service:
                self.services[account.id] = service
    
    def _create_service(self, account: ReferenceManagerAccount) -> Optional[BaseReferenceService]:
        """Create appropriate service instance for an account."""
        try:
            if account.service == 'mendeley':
                return MendeleyService(account)
            elif account.service == 'zotero':
                return ZoteroService(account)
            else:
                self.logger.error(f"Unknown service type: {account.service}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to create service for {account}: {e}")
            return None
    
    def start_sync(self, trigger: str = 'manual') -> SyncSession:
        """
        Start a new synchronization session.
        
        Args:
            trigger: What triggered the sync (manual, scheduled, webhook, startup)
            
        Returns:
            SyncSession instance
        """
        session = SyncSession.objects.create(
            profile=self.profile,
            status='pending',
            trigger=trigger
        )
        
        self._log(session, 'INFO', 'startup', f'Starting sync session {session.id}')
        
        try:
            self._perform_sync(session)
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            session.mark_failed(str(e))
            self._log(session, 'ERROR', 'error', f'Sync failed: {e}')
        
        return session
    
    def _perform_sync(self, session: SyncSession):
        """Perform the actual synchronization."""
        session.status = 'running'
        session.save()
        
        self._log(session, 'INFO', 'startup', 'Sync session started')
        
        # Collect all items to sync
        all_items = []
        
        # Get remote items from all services
        for account_id, service in self.services.items():
            try:
                remote_items = self._fetch_remote_items(session, service)
                all_items.extend(remote_items)
            except Exception as e:
                self.logger.error(f"Failed to fetch items from {service}: {e}")
                self._log(session, 'ERROR', 'fetch', f'Failed to fetch from {service}: {e}')
        
        # Get local items that need syncing
        local_items = self._get_local_items_for_sync(session)
        
        session.total_items = len(all_items) + len(local_items)
        session.save()
        
        # Process remote items (import/update)
        if self.profile.sync_direction in ['bidirectional', 'import_only']:
            self._process_remote_items(session, all_items)
        
        # Process local items (export/update)
        if self.profile.sync_direction in ['bidirectional', 'export_only']:
            self._process_local_items(session, local_items)
        
        # Update sync statistics
        self._update_statistics(session)
        
        session.mark_completed()
        self._log(session, 'INFO', 'cleanup', 'Sync session completed successfully')
    
    def _fetch_remote_items(self, session: SyncSession, service: BaseReferenceService) -> List[Dict[str, Any]]:
        """Fetch items from a remote service."""
        self._log(session, 'INFO', 'fetch', f'Fetching items from {service.service_name}')
        
        all_items = []
        
        # Get collections to sync
        collections = self._get_collections_to_sync(service)
        
        for collection in collections:
            try:
                # Fetch items from this collection
                items = service.get_references(
                    collection_id=collection.get('id'),
                    limit=100,
                    offset=0
                )
                
                # Add service info to each item
                for item in items:
                    item['_service'] = service.service_name
                    item['_account_id'] = service.account.id
                    item['_collection_id'] = collection.get('id')
                
                all_items.extend(items)
                
                self._log(session, 'INFO', 'fetch', 
                         f'Fetched {len(items)} items from {collection["name"]}')
                
            except Exception as e:
                self.logger.error(f"Failed to fetch from collection {collection['name']}: {e}")
                self._log(session, 'ERROR', 'fetch', 
                         f'Failed to fetch from {collection["name"]}: {e}')
        
        return all_items
    
    def _get_collections_to_sync(self, service: BaseReferenceService) -> List[Dict[str, Any]]:
        """Get list of collections to sync based on profile settings."""
        collections = service.get_collections()
        
        # Filter collections based on profile settings
        if self.profile.sync_collections:
            # Only sync specified collections
            filtered = []
            for collection in collections:
                if (collection['id'] in self.profile.sync_collections or 
                    collection['name'] in self.profile.sync_collections):
                    filtered.append(collection)
            return filtered
        
        return collections
    
    def _get_local_items_for_sync(self, session: SyncSession) -> List[SearchIndex]:
        """Get local items that need to be synced."""
        queryset = SearchIndex.objects.filter(
            saved_by_users__user=self.user
        ).distinct()
        
        # Apply date filters
        if self.profile.sync_after_date:
            queryset = queryset.filter(publication_date__gte=self.profile.sync_after_date)
        
        if self.profile.sync_before_date:
            queryset = queryset.filter(publication_date__lte=self.profile.sync_before_date)
        
        # Apply tag filters
        if self.profile.sync_tags:
            # Filter by user library tags
            queryset = queryset.filter(
                saved_by_users__tags__icontains=','.join(self.profile.sync_tags)
            )
        
        if self.profile.exclude_tags:
            # Exclude items with certain tags
            for tag in self.profile.exclude_tags:
                queryset = queryset.exclude(saved_by_users__tags__icontains=tag)
        
        return list(queryset[:1000])  # Limit to prevent memory issues
    
    def _process_remote_items(self, session: SyncSession, remote_items: List[Dict[str, Any]]):
        """Process items from remote services (import to local)."""
        self._log(session, 'INFO', 'create', f'Processing {len(remote_items)} remote items')
        
        for item in remote_items:
            try:
                self._process_single_remote_item(session, item)
                session.items_processed += 1
                session.save()
            except Exception as e:
                self.logger.error(f"Failed to process remote item {item.get('id')}: {e}")
                self._log(session, 'ERROR', 'create', f'Failed to process item {item.get("id")}: {e}')
                session.items_skipped += 1
                session.save()
    
    def _process_single_remote_item(self, session: SyncSession, item: Dict[str, Any]):
        """Process a single remote item."""
        account_id = item['_account_id']
        service_name = item['_service']
        external_id = item['id']
        
        # Check if mapping already exists
        try:
            mapping = ReferenceMapping.objects.get(
                service=service_name,
                external_id=external_id,
                account_id=account_id
            )
            # Update existing item
            self._update_existing_item(session, mapping, item)
        except ReferenceMapping.DoesNotExist:
            # Create new item
            self._create_new_item(session, item)
    
    def _create_new_item(self, session: SyncSession, item: Dict[str, Any]):
        """Create a new local item from remote data."""
        with transaction.atomic():
            # Create or get authors
            authors = self._create_or_get_authors(item.get('authors', []))
            
            # Create or get journal
            journal = None
            journal_name = item.get('journal', '').strip()
            if journal_name:
                journal, _ = Journal.objects.get_or_create(
                    name=journal_name,
                    defaults={'abbreviation': journal_name[:50]}
                )
            
            # Create SearchIndex entry
            search_index = SearchIndex.objects.create(
                title=item.get('title', ''),
                abstract=item.get('abstract', ''),
                document_type=self._map_document_type(item.get('type', 'article')),
                publication_date=self._parse_publication_date(item.get('year')),
                journal=journal,
                doi=item.get('doi', ''),
                external_url=item.get('url', ''),
                keywords=','.join(item.get('keywords', [])),
                source='imported',
            )
            
            # Add authors
            for i, author in enumerate(authors):
                from apps.scholar_app.models import AuthorPaper
                AuthorPaper.objects.create(
                    author=author,
                    paper=search_index,
                    author_order=i + 1
                )
            
            # Create mapping
            mapping = ReferenceMapping.objects.create(
                local_paper=search_index,
                service=item['_service'],
                external_id=item['id'],
                account_id=item['_account_id'],
                remote_hash=self._calculate_item_hash(item),
                sync_status='synced'
            )
            
            # Add to user's library
            from apps.scholar_app.models import UserLibrary
            user_library, created = UserLibrary.objects.get_or_create(
                user=self.user,
                paper=search_index,
                defaults={
                    'tags': ','.join(item.get('tags', [])),
                    'personal_notes': item.get('notes', ''),
                    'reading_status': 'to_read'
                }
            )
            
            session.items_created += 1
            session.save()
            
            self._log(session, 'INFO', 'create', 
                     f'Created new item: {search_index.title[:50]}')
    
    def _update_existing_item(self, session: SyncSession, mapping: ReferenceMapping, item: Dict[str, Any]):
        """Update an existing local item with remote data."""
        new_hash = self._calculate_item_hash(item)
        
        if mapping.remote_hash == new_hash:
            # No changes, skip
            return
        
        # Check for conflicts
        local_paper = mapping.local_paper
        conflicts = self._detect_conflicts(local_paper, item)
        
        if conflicts and self.profile.conflict_resolution == 'ask':
            # Create conflict records for manual resolution
            for conflict_type, (local_val, remote_val) in conflicts.items():
                ConflictResolution.objects.create(
                    sync_session=session,
                    reference_mapping=mapping,
                    conflict_type=conflict_type,
                    local_value=local_val,
                    remote_value=remote_val
                )
            
            session.conflicts_found += len(conflicts)
            mapping.sync_status = 'conflict'
            mapping.save()
            
            self._log(session, 'WARNING', 'conflict', 
                     f'Conflicts found for {local_paper.title[:50]}')
            
        else:
            # Auto-resolve conflicts
            self._auto_resolve_conflicts(session, mapping, item, conflicts)
    
    def _detect_conflicts(self, local_paper: SearchIndex, remote_item: Dict[str, Any]) -> Dict[str, Tuple[Any, Any]]:
        """Detect conflicts between local and remote data."""
        conflicts = {}
        
        # Check title
        if local_paper.title != remote_item.get('title', ''):
            conflicts['title'] = (local_paper.title, remote_item.get('title', ''))
        
        # Check abstract
        local_abstract = local_paper.abstract or ''
        remote_abstract = remote_item.get('abstract', '')
        if local_abstract != remote_abstract and local_abstract and remote_abstract:
            conflicts['abstract'] = (local_abstract, remote_abstract)
        
        # Check publication date
        local_year = local_paper.publication_date.year if local_paper.publication_date else None
        remote_year = remote_item.get('year')
        if local_year != remote_year and local_year and remote_year:
            conflicts['publication_date'] = (local_year, remote_year)
        
        # Check DOI
        local_doi = local_paper.doi or ''
        remote_doi = remote_item.get('doi', '')
        if local_doi != remote_doi and local_doi and remote_doi:
            conflicts['doi'] = (local_doi, remote_doi)
        
        return conflicts
    
    def _auto_resolve_conflicts(self, session: SyncSession, mapping: ReferenceMapping, 
                               remote_item: Dict[str, Any], conflicts: Dict[str, Tuple[Any, Any]]):
        """Automatically resolve conflicts based on profile settings."""
        local_paper = mapping.local_paper
        resolution_strategy = self.profile.conflict_resolution
        
        if resolution_strategy == 'remote_wins':
            # Update local with remote data
            self._update_local_paper_from_remote(local_paper, remote_item)
            session.items_updated += 1
            
        elif resolution_strategy == 'local_wins':
            # Keep local data, update remote hash
            mapping.remote_hash = self._calculate_item_hash(remote_item)
            
        elif resolution_strategy == 'merge':
            # Try to merge data intelligently
            self._merge_paper_data(local_paper, remote_item)
            session.items_updated += 1
        
        elif resolution_strategy == 'skip':
            # Skip updates when conflicts exist
            session.items_skipped += 1
            mapping.sync_status = 'conflict'
        
        mapping.save()
        session.save()
        
        # Log conflicts resolved
        for conflict_type in conflicts:
            ConflictResolution.objects.create(
                sync_session=session,
                reference_mapping=mapping,
                conflict_type=conflict_type,
                local_value=conflicts[conflict_type][0],
                remote_value=conflicts[conflict_type][1],
                resolution=resolution_strategy,
                resolved_at=timezone.now()
            )
            
        session.conflicts_resolved += len(conflicts)
        session.save()
    
    def _process_local_items(self, session: SyncSession, local_items: List[SearchIndex]):
        """Process local items for export to remote services."""
        self._log(session, 'INFO', 'update', f'Processing {len(local_items)} local items')
        
        for item in local_items:
            try:
                self._process_single_local_item(session, item)
                session.items_processed += 1
                session.save()
            except Exception as e:
                self.logger.error(f"Failed to process local item {item.id}: {e}")
                self._log(session, 'ERROR', 'update', f'Failed to process item {item.title[:50]}: {e}')
                session.items_skipped += 1
                session.save()
    
    def _process_single_local_item(self, session: SyncSession, local_item: SearchIndex):
        """Process a single local item for export."""
        # Check if item is already mapped to any service
        existing_mappings = ReferenceMapping.objects.filter(local_paper=local_item)
        
        for account_id, service in self.services.items():
            # Check if already mapped to this service
            mapping = existing_mappings.filter(
                service=service.service_name,
                account_id=account_id
            ).first()
            
            if mapping:
                # Update existing remote item
                self._update_remote_item(session, mapping, service)
            else:
                # Create new remote item
                self._create_remote_item(session, local_item, service)
    
    def _create_remote_item(self, session: SyncSession, local_item: SearchIndex, service: BaseReferenceService):
        """Create a new remote item from local data."""
        try:
            # Convert local item to normalized format
            normalized_data = self._convert_local_to_normalized(local_item)
            
            # Create remote item
            remote_item = service.create_reference(normalized_data)
            
            # Create mapping
            ReferenceMapping.objects.create(
                local_paper=local_item,
                service=service.service_name,
                external_id=remote_item['id'],
                account=service.account,
                local_hash=self._calculate_local_hash(local_item),
                remote_hash=self._calculate_item_hash(remote_item),
                sync_status='synced'
            )
            
            session.items_created += 1
            session.save()
            
            self._log(session, 'INFO', 'create', 
                     f'Created remote item in {service.service_name}: {local_item.title[:50]}')
            
        except Exception as e:
            self.logger.error(f"Failed to create remote item: {e}")
            raise
    
    def _update_remote_item(self, session: SyncSession, mapping: ReferenceMapping, service: BaseReferenceService):
        """Update an existing remote item with local data."""
        local_item = mapping.local_paper
        current_hash = self._calculate_local_hash(local_item)
        
        if mapping.local_hash == current_hash:
            # No local changes, skip
            return
        
        try:
            # Convert local item to normalized format
            normalized_data = self._convert_local_to_normalized(local_item)
            
            # Update remote item
            updated_item = service.update_reference(mapping.external_id, normalized_data)
            
            # Update mapping
            mapping.local_hash = current_hash
            mapping.remote_hash = self._calculate_item_hash(updated_item)
            mapping.sync_status = 'synced'
            mapping.save()
            
            session.items_updated += 1
            session.save()
            
            self._log(session, 'INFO', 'update', 
                     f'Updated remote item in {service.service_name}: {local_item.title[:50]}')
            
        except Exception as e:
            self.logger.error(f"Failed to update remote item: {e}")
            session.errors_count += 1
            session.save()
    
    # Utility methods
    
    def _create_or_get_authors(self, author_names: List[str]) -> List[Author]:
        """Create or get Author objects from names."""
        authors = []
        for name in author_names:
            if not name.strip():
                continue
            
            # Simple name parsing - could be improved
            parts = name.strip().split()
            if len(parts) >= 2:
                first_name = ' '.join(parts[:-1])
                last_name = parts[-1]
            else:
                first_name = ''
                last_name = parts[0] if parts else ''
            
            author, _ = Author.objects.get_or_create(
                first_name=first_name,
                last_name=last_name
            )
            authors.append(author)
        
        return authors
    
    def _map_document_type(self, type_str: str) -> str:
        """Map external document type to internal type."""
        mapping = {
            'article': 'article',
            'book': 'book',
            'chapter': 'chapter',
            'conference': 'conference',
            'thesis': 'thesis',
            'report': 'report',
            'preprint': 'preprint',
            'dataset': 'dataset',
        }
        return mapping.get(type_str.lower(), 'article')
    
    def _parse_publication_date(self, year: Any) -> Optional[timezone.datetime.date]:
        """Parse publication year into date."""
        if year:
            try:
                year_int = int(year)
                return timezone.datetime(year_int, 1, 1).date()
            except (ValueError, TypeError):
                pass
        return None
    
    def _calculate_item_hash(self, item: Dict[str, Any]) -> str:
        """Calculate hash for an item dictionary."""
        import hashlib
        
        # Create a simplified version for hashing
        hash_data = {
            'title': item.get('title', ''),
            'authors': sorted(item.get('authors', [])),
            'year': item.get('year'),
            'doi': item.get('doi', ''),
            'abstract': item.get('abstract', ''),
        }
        
        json_str = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def _calculate_local_hash(self, local_item: SearchIndex) -> str:
        """Calculate hash for a local SearchIndex item."""
        import hashlib
        
        # Get authors
        authors = [ap.author.full_name for ap in local_item.authorpaper_set.all()]
        
        hash_data = {
            'title': local_item.title,
            'authors': sorted(authors),
            'year': local_item.publication_date.year if local_item.publication_date else None,
            'doi': local_item.doi,
            'abstract': local_item.abstract,
        }
        
        json_str = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def _convert_local_to_normalized(self, local_item: SearchIndex) -> Dict[str, Any]:
        """Convert local SearchIndex to normalized format."""
        # Get authors
        authors = [ap.author.full_name for ap in local_item.authorpaper_set.all()]
        
        # Get user library info
        user_library = local_item.saved_by_users.filter(user=self.user).first()
        
        return {
            'title': local_item.title,
            'abstract': local_item.abstract,
            'authors': authors,
            'year': local_item.publication_date.year if local_item.publication_date else None,
            'journal': local_item.journal.name if local_item.journal else '',
            'doi': local_item.doi,
            'url': local_item.external_url,
            'type': local_item.document_type,
            'keywords': local_item.keywords.split(',') if local_item.keywords else [],
            'tags': user_library.get_tags_list() if user_library else [],
            'notes': user_library.personal_notes if user_library else '',
        }
    
    def _update_local_paper_from_remote(self, local_paper: SearchIndex, remote_item: Dict[str, Any]):
        """Update local paper with remote data."""
        local_paper.title = remote_item.get('title', local_paper.title)
        
        if remote_item.get('abstract'):
            local_paper.abstract = remote_item['abstract']
        
        if remote_item.get('doi'):
            local_paper.doi = remote_item['doi']
        
        if remote_item.get('url'):
            local_paper.external_url = remote_item['url']
        
        if remote_item.get('year'):
            try:
                year = int(remote_item['year'])
                local_paper.publication_date = timezone.datetime(year, 1, 1).date()
            except (ValueError, TypeError):
                pass
        
        local_paper.save()
    
    def _merge_paper_data(self, local_paper: SearchIndex, remote_item: Dict[str, Any]):
        """Intelligently merge local and remote data."""
        # Prefer non-empty values
        if not local_paper.abstract and remote_item.get('abstract'):
            local_paper.abstract = remote_item['abstract']
        
        if not local_paper.doi and remote_item.get('doi'):
            local_paper.doi = remote_item['doi']
        
        if not local_paper.external_url and remote_item.get('url'):
            local_paper.external_url = remote_item['url']
        
        # Merge keywords
        local_keywords = set(local_paper.keywords.split(',')) if local_paper.keywords else set()
        remote_keywords = set(remote_item.get('keywords', []))
        merged_keywords = local_keywords.union(remote_keywords)
        local_paper.keywords = ','.join(sorted(merged_keywords))
        
        local_paper.save()
    
    def _update_statistics(self, session: SyncSession):
        """Update sync statistics."""
        today = timezone.now().date()
        stats, created = SyncStatistics.objects.get_or_create(
            user=self.user,
            date=today,
            defaults={
                'sync_sessions': 0,
                'successful_syncs': 0,
                'failed_syncs': 0,
            }
        )
        
        stats.sync_sessions += 1
        if session.status == 'completed':
            stats.successful_syncs += 1
        else:
            stats.failed_syncs += 1
        
        stats.items_synced += session.items_processed
        stats.items_created += session.items_created
        stats.items_updated += session.items_updated
        stats.items_deleted += session.items_deleted
        
        stats.conflicts_found += session.conflicts_found
        stats.conflicts_resolved += session.conflicts_resolved
        
        stats.total_sync_time += session.duration()
        stats.api_calls_made += session.api_calls_made
        
        stats.save()
    
    def _log(self, session: SyncSession, level: str, operation: str, message: str, 
             reference_mapping: ReferenceMapping = None, extra_data: Dict = None):
        """Log sync operation."""
        SyncLog.objects.create(
            sync_session=session,
            level=level,
            operation=operation,
            message=message,
            reference_mapping=reference_mapping,
            extra_data=extra_data or {}
        )
        
        # Also log to Python logger
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"[{session.id}] {operation}: {message}")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status for the profile."""
        recent_sessions = SyncSession.objects.filter(
            profile=self.profile
        ).order_by('-started_at')[:5]
        
        return {
            'profile': {
                'name': self.profile.name,
                'auto_sync': self.profile.auto_sync,
                'last_sync': self.profile.last_sync,
                'next_sync': self.profile.next_sync,
            },
            'recent_sessions': [
                {
                    'id': str(session.id),
                    'status': session.status,
                    'started_at': session.started_at,
                    'completed_at': session.completed_at,
                    'items_processed': session.items_processed,
                    'conflicts_found': session.conflicts_found,
                }
                for session in recent_sessions
            ],
            'services': [
                {
                    'service': service.service_name,
                    'account': service.account.account_name,
                    'status': service.account.status,
                    'authenticated': service.is_authenticated(),
                }
                for service in self.services.values()
            ]
        }
#!/usr/bin/env python3
"""
Services for arXiv API integration and submission management.
"""

import requests
import xml.etree.ElementTree as ET
import feedparser
import os
import zipfile
import tarfile
import tempfile
import subprocess
import shutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import (
    ArxivSubmission, ArxivCategory, ArxivSubmissionFile, 
    ArxivSubmissionLog, ArxivSearchCache, ArxivPaperMapping
)

logger = logging.getLogger(__name__)


class ArxivAPIService:
    """Service for interacting with arXiv API."""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    OAI_URL = "http://export.arxiv.org/oai2"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SciTeX-Cloud/1.0 (https://scitex.ai)'
        })
    
    def search_papers(self, query: str, category: str = None, max_results: int = 100, 
                     start: int = 0, sort_by: str = 'relevance') -> Dict[str, Any]:
        """Search arXiv papers using the API."""
        try:
            # Check cache first
            cached = self._get_cached_search(query, category)
            if cached:
                return cached
            
            # Build search query
            search_query = query
            if category:
                search_query = f"cat:{category} AND ({query})"
            
            params = {
                'search_query': search_query,
                'start': start,
                'max_results': max_results,
                'sortBy': sort_by,
                'sortOrder': 'descending'
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse the Atom feed
            feed = feedparser.parse(response.content)
            
            papers = []
            for entry in feed.entries:
                paper = self._parse_arxiv_entry(entry)
                papers.append(paper)
            
            result = {
                'papers': papers,
                'total_results': int(getattr(feed.feed, 'opensearch_totalresults', len(papers))),
                'start_index': int(getattr(feed.feed, 'opensearch_startindex', start)),
                'items_per_page': int(getattr(feed.feed, 'opensearch_itemsperpage', len(papers)))
            }
            
            # Cache the results
            self._cache_search_results(query, category, result)
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"Error searching arXiv: {e}")
            return {'papers': [], 'total_results': 0, 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in arXiv search: {e}")
            return {'papers': [], 'total_results': 0, 'error': str(e)}
    
    def get_paper_by_id(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific paper by arXiv ID."""
        try:
            params = {
                'id_list': arxiv_id,
                'max_results': 1
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.entries:
                return self._parse_arxiv_entry(feed.entries[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching arXiv paper {arxiv_id}: {e}")
            return None
    
    def get_categories(self) -> List[Dict[str, str]]:
        """Get list of arXiv categories."""
        categories = [
            # Computer Science
            {'code': 'cs.AI', 'name': 'Artificial Intelligence', 'parent': 'cs'},
            {'code': 'cs.CL', 'name': 'Computation and Language', 'parent': 'cs'},
            {'code': 'cs.CV', 'name': 'Computer Vision and Pattern Recognition', 'parent': 'cs'},
            {'code': 'cs.LG', 'name': 'Machine Learning', 'parent': 'cs'},
            {'code': 'cs.NE', 'name': 'Neural and Evolutionary Computing', 'parent': 'cs'},
            {'code': 'cs.RO', 'name': 'Robotics', 'parent': 'cs'},
            
            # Mathematics
            {'code': 'math.ST', 'name': 'Statistics Theory', 'parent': 'math'},
            {'code': 'math.PR', 'name': 'Probability', 'parent': 'math'},
            {'code': 'math.NA', 'name': 'Numerical Analysis', 'parent': 'math'},
            {'code': 'math.OC', 'name': 'Optimization and Control', 'parent': 'math'},
            
            # Physics
            {'code': 'physics.data-an', 'name': 'Data Analysis, Statistics and Probability', 'parent': 'physics'},
            {'code': 'physics.comp-ph', 'name': 'Computational Physics', 'parent': 'physics'},
            
            # Statistics
            {'code': 'stat.ML', 'name': 'Machine Learning', 'parent': 'stat'},
            {'code': 'stat.AP', 'name': 'Applications', 'parent': 'stat'},
            {'code': 'stat.CO', 'name': 'Computation', 'parent': 'stat'},
            {'code': 'stat.ME', 'name': 'Methodology', 'parent': 'stat'},
            
            # Quantitative Biology
            {'code': 'q-bio.BM', 'name': 'Biomolecules', 'parent': 'q-bio'},
            {'code': 'q-bio.GN', 'name': 'Genomics', 'parent': 'q-bio'},
            {'code': 'q-bio.QM', 'name': 'Quantitative Methods', 'parent': 'q-bio'},
            
            # Economics
            {'code': 'econ.EM', 'name': 'Econometrics', 'parent': 'econ'},
            {'code': 'econ.TH', 'name': 'Theoretical Economics', 'parent': 'econ'},
        ]
        
        return categories
    
    def _parse_arxiv_entry(self, entry) -> Dict[str, Any]:
        """Parse an arXiv entry from the API response."""
        # Extract arXiv ID
        arxiv_id = entry.id.split('/')[-1]
        if 'v' in arxiv_id:
            arxiv_id, version = arxiv_id.split('v')
        else:
            version = '1'
        
        # Extract categories
        categories = []
        if hasattr(entry, 'tags'):
            categories = [tag.term for tag in entry.tags if tag.scheme == 'http://arxiv.org/schemas/atom']
        
        # Extract authors
        authors = []
        if hasattr(entry, 'authors'):
            authors = [author.name for author in entry.authors]
        
        # Extract DOI if available
        doi = None
        if hasattr(entry, 'arxiv_doi'):
            doi = entry.arxiv_doi
        
        return {
            'arxiv_id': arxiv_id,
            'version': int(version),
            'title': entry.title.replace('\n', ' ').strip(),
            'authors': authors,
            'abstract': entry.summary.replace('\n', ' ').strip(),
            'categories': categories,
            'primary_category': categories[0] if categories else None,
            'published': entry.published,
            'updated': entry.updated,
            'doi': doi,
            'pdf_url': f"https://arxiv.org/pdf/{arxiv_id}.pdf",
            'abs_url': f"https://arxiv.org/abs/{arxiv_id}",
            'comment': getattr(entry, 'arxiv_comment', ''),
            'journal_ref': getattr(entry, 'arxiv_journal_ref', ''),
        }
    
    def _get_cached_search(self, query: str, category: str = None) -> Optional[Dict[str, Any]]:
        """Get cached search results if available and not expired."""
        try:
            cache_entry = ArxivSearchCache.objects.filter(
                query=query,
                category=category or '',
                expires_at__gt=timezone.now()
            ).first()
            
            if cache_entry:
                return cache_entry.results
            
        except Exception as e:
            logger.warning(f"Error checking search cache: {e}")
        
        return None
    
    def _cache_search_results(self, query: str, category: str = None, results: Dict[str, Any]):
        """Cache search results for future use."""
        try:
            # Clean up old cache entries
            ArxivSearchCache.objects.filter(expires_at__lt=timezone.now()).delete()
            
            # Create new cache entry (expires in 1 hour)
            expires_at = timezone.now() + timedelta(hours=1)
            
            ArxivSearchCache.objects.create(
                query=query,
                category=category or '',
                results=results,
                total_results=results.get('total_results', 0),
                expires_at=expires_at
            )
            
        except Exception as e:
            logger.warning(f"Error caching search results: {e}")


class ArxivSubmissionService:
    """Service for managing arXiv submissions."""
    
    def __init__(self):
        self.api_service = ArxivAPIService()
    
    def prepare_submission(self, submission: ArxivSubmission) -> bool:
        """Prepare submission files and validate them."""
        try:
            self._log_submission(submission, 'info', 'Starting submission preparation')
            
            # Update status
            submission.status = 'preparing'
            submission.save()
            
            # Collect and validate files
            if not self._collect_source_files(submission):
                return False
            
            # Validate LaTeX compilation
            if not self._validate_latex(submission):
                return False
            
            # Create submission package
            if not self._create_submission_package(submission):
                return False
            
            submission.status = 'validating'
            submission.save()
            
            # Run final validation
            if not self._validate_submission_package(submission):
                return False
            
            submission.validation_status = 'valid'
            submission.status = 'draft'
            submission.save()
            
            self._log_submission(submission, 'info', 'Submission preparation completed successfully')
            return True
            
        except Exception as e:
            self._log_submission(submission, 'error', f'Preparation failed: {str(e)}')
            submission.status = 'error'
            submission.last_error = str(e)
            submission.save()
            return False
    
    def submit_to_arxiv(self, submission: ArxivSubmission) -> bool:
        """Submit paper to arXiv (mock implementation)."""
        try:
            if not submission.can_submit():
                raise ValueError("Submission is not ready for arXiv")
            
            self._log_submission(submission, 'info', 'Starting arXiv submission')
            
            submission.status = 'submitting'
            submission.save()
            
            # Mock submission process (in real implementation, this would use arXiv's submission API)
            import time
            import random
            
            # Simulate submission time
            time.sleep(2)
            
            # Generate mock arXiv ID
            year = datetime.now().year
            month = datetime.now().month
            sequence = random.randint(1000, 9999)
            arxiv_id = f"{year}{month:02d}.{sequence}"
            
            # Update submission
            submission.arxiv_id = arxiv_id
            submission.status = 'submitted'
            submission.submitted_at = timezone.now()
            submission.save()
            
            self._log_submission(submission, 'info', f'Successfully submitted to arXiv: {arxiv_id}')
            
            # Create Scholar mapping if possible
            self._create_scholar_mapping(submission)
            
            return True
            
        except Exception as e:
            self._log_submission(submission, 'error', f'Submission failed: {str(e)}')
            submission.status = 'error'
            submission.last_error = str(e)
            submission.save()
            return False
    
    def check_submission_status(self, submission: ArxivSubmission) -> bool:
        """Check status of submitted paper on arXiv."""
        try:
            if not submission.arxiv_id:
                return False
            
            # Get paper info from arXiv
            paper_info = self.api_service.get_paper_by_id(submission.arxiv_id)
            
            if paper_info:
                # Update submission with arXiv data
                if paper_info.get('published'):
                    published_date = datetime.fromisoformat(paper_info['published'].replace('Z', '+00:00'))
                    submission.published_at = published_date
                    submission.status = 'published'
                
                submission.version = paper_info.get('version', 1)
                submission.save()
                
                self._log_submission(submission, 'info', f'Status updated from arXiv: {submission.status}')
                return True
            
            return False
            
        except Exception as e:
            self._log_submission(submission, 'warning', f'Could not check status: {str(e)}')
            return False
    
    def _collect_source_files(self, submission: ArxivSubmission) -> bool:
        """Collect source files from Writer project."""
        try:
            if not submission.writer_project:
                raise ValueError("No Writer project associated with submission")
            
            # Get project files from Writer module
            project_path = submission.writer_project.get_project_path()
            if not os.path.exists(project_path):
                raise ValueError("Writer project path does not exist")
            
            # Create temporary directory for submission files
            temp_dir = tempfile.mkdtemp(prefix='arxiv_submission_')
            submission.source_files_path = temp_dir
            submission.save()
            
            # Copy relevant files
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith(('.tex', '.bib', '.cls', '.sty', '.pdf', '.png', '.jpg', '.eps')):
                        src = os.path.join(root, file)
                        dst = os.path.join(temp_dir, file)
                        shutil.copy2(src, dst)
                        
                        # Create file record
                        file_type = self._determine_file_type(file)
                        ArxivSubmissionFile.objects.create(
                            submission=submission,
                            filename=file,
                            file_type=file_type,
                            file_path=dst,
                            file_size=os.path.getsize(dst),
                            is_main_file=(file_type == 'main_tex')
                        )
            
            return True
            
        except Exception as e:
            logger.error(f"Error collecting source files: {e}")
            return False
    
    def _validate_latex(self, submission: ArxivSubmission) -> bool:
        """Validate LaTeX compilation."""
        try:
            main_file = submission.files.filter(is_main_file=True).first()
            if not main_file:
                # Try to find main .tex file
                tex_files = submission.files.filter(file_type='tex')
                if tex_files:
                    main_file = tex_files.first()
                    main_file.is_main_file = True
                    main_file.save()
            
            if not main_file:
                raise ValueError("No main LaTeX file found")
            
            # Run pdflatex compilation
            result = subprocess.run([
                'pdflatex', '-interaction=nonstopmode', '-output-directory', 
                submission.source_files_path, main_file.file_path
            ], capture_output=True, text=True, timeout=300)
            
            # Check if PDF was generated
            pdf_path = os.path.join(submission.source_files_path, 
                                   main_file.filename.replace('.tex', '.pdf'))
            
            if os.path.exists(pdf_path):
                submission.compiled_pdf_path = pdf_path
                submission.validation_status = 'valid'
                submission.validation_log = result.stdout
                submission.save()
                return True
            else:
                submission.validation_status = 'errors'
                submission.validation_log = result.stderr
                submission.save()
                return False
            
        except subprocess.TimeoutExpired:
            submission.validation_status = 'errors'
            submission.validation_log = 'LaTeX compilation timed out'
            submission.save()
            return False
        except Exception as e:
            submission.validation_status = 'errors'
            submission.validation_log = str(e)
            submission.save()
            return False
    
    def _create_submission_package(self, submission: ArxivSubmission) -> bool:
        """Create submission package (tar.gz) for arXiv."""
        try:
            if not submission.source_files_path:
                return False
            
            # Create package file
            package_path = f"{submission.source_files_path}.tar.gz"
            
            with tarfile.open(package_path, 'w:gz') as tar:
                tar.add(submission.source_files_path, arcname='.')
            
            submission.submission_package_path = package_path
            submission.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating submission package: {e}")
            return False
    
    def _validate_submission_package(self, submission: ArxivSubmission) -> bool:
        """Validate the submission package."""
        try:
            if not submission.submission_package_path:
                return False
            
            # Check package size (arXiv has limits)
            package_size = os.path.getsize(submission.submission_package_path)
            max_size = 50 * 1024 * 1024  # 50MB limit
            
            if package_size > max_size:
                submission.validation_log = f"Package too large: {package_size} bytes (max: {max_size})"
                submission.validation_status = 'errors'
                submission.save()
                return False
            
            # Validate package contents
            with tarfile.open(submission.submission_package_path, 'r:gz') as tar:
                members = tar.getnames()
                
                # Check for main .tex file
                tex_files = [m for m in members if m.endswith('.tex')]
                if not tex_files:
                    submission.validation_log = "No .tex files found in package"
                    submission.validation_status = 'errors'
                    submission.save()
                    return False
            
            return True
            
        except Exception as e:
            submission.validation_log = f"Package validation failed: {str(e)}"
            submission.validation_status = 'errors'
            submission.save()
            return False
    
    def _determine_file_type(self, filename: str) -> str:
        """Determine file type based on extension."""
        ext = filename.lower().split('.')[-1]
        
        type_map = {
            'tex': 'tex',
            'cls': 'cls',
            'sty': 'sty',
            'bst': 'bst',
            'bib': 'bib',
            'pdf': 'pdf',
            'eps': 'eps',
            'png': 'png',
            'jpg': 'jpg',
            'jpeg': 'jpg',
            'gif': 'gif',
        }
        
        return type_map.get(ext, 'other')
    
    def _create_scholar_mapping(self, submission: ArxivSubmission):
        """Create mapping between submission and Scholar paper if exists."""
        try:
            from apps.scholar_app.models import SearchIndex
            
            # Try to find matching paper in Scholar
            papers = SearchIndex.objects.filter(
                title__icontains=submission.title[:50]
            )
            
            for paper in papers:
                # Check title similarity
                if self._calculate_similarity(paper.title, submission.title) > 0.8:
                    ArxivPaperMapping.objects.get_or_create(
                        local_paper=paper,
                        arxiv_id=submission.arxiv_id,
                        defaults={
                            'confidence_score': 0.9,
                            'mapping_source': 'title',
                            'is_verified': False
                        }
                    )
                    break
            
        except Exception as e:
            logger.warning(f"Could not create Scholar mapping: {e}")
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (simple implementation)."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _log_submission(self, submission: ArxivSubmission, log_type: str, message: str, details: Dict = None):
        """Log submission activity."""
        from .models import ArxivSubmissionLog
        
        ArxivSubmissionLog.objects.create(
            submission=submission,
            log_type=log_type,
            message=message,
            details=details or {},
            user=submission.user
        )


class ArxivIntegrationService:
    """Service for integrating arXiv with other SciTeX modules."""
    
    def __init__(self):
        self.api_service = ArxivAPIService()
    
    def sync_with_scholar(self, user) -> Dict[str, int]:
        """Sync arXiv papers with Scholar module."""
        try:
            from apps.scholar_app.models import SearchIndex, Author
            
            stats = {'imported': 0, 'updated': 0, 'skipped': 0}
            
            # Get user's arXiv submissions
            submissions = ArxivSubmission.objects.filter(
                user=user,
                status='published',
                arxiv_id__isnull=False
            )
            
            for submission in submissions:
                # Check if already in Scholar
                existing = SearchIndex.objects.filter(
                    title__icontains=submission.title[:50]
                ).first()
                
                if existing:
                    # Update with arXiv info
                    if not existing.arxiv_id:
                        existing.arxiv_id = submission.arxiv_id
                        existing.save()
                        stats['updated'] += 1
                    else:
                        stats['skipped'] += 1
                else:
                    # Create new Scholar entry
                    paper = SearchIndex.objects.create(
                        title=submission.title,
                        abstract=submission.abstract,
                        arxiv_id=submission.arxiv_id,
                        publication_date=submission.published_at.date() if submission.published_at else None,
                        paper_type='preprint',
                        source='arxiv'
                    )
                    
                    # Add authors
                    for author_data in submission.authors:
                        if isinstance(author_data, dict):
                            author_name = f"{author_data.get('first_name', '')} {author_data.get('last_name', '')}".strip()
                        else:
                            author_name = str(author_data)
                        
                        if author_name:
                            author, created = Author.objects.get_or_create(
                                name=author_name
                            )
                            paper.authors.add(author)
                    
                    stats['imported'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error syncing with Scholar: {e}")
            return {'imported': 0, 'updated': 0, 'skipped': 0, 'error': str(e)}
    
    def enhance_scholar_papers(self, user) -> int:
        """Enhance Scholar papers with arXiv data."""
        try:
            from apps.scholar_app.models import SearchIndex
            
            enhanced_count = 0
            
            # Get Scholar papers without arXiv data
            papers = SearchIndex.objects.filter(
                arxiv_id__isnull=True
            )[:50]  # Limit to avoid API overload
            
            for paper in papers:
                # Search arXiv for similar papers
                search_results = self.api_service.search_papers(
                    query=paper.title,
                    max_results=5
                )
                
                for arxiv_paper in search_results.get('papers', []):
                    # Check similarity
                    similarity = self._calculate_title_similarity(
                        paper.title, arxiv_paper['title']
                    )
                    
                    if similarity > 0.8:
                        # Create mapping
                        mapping, created = ArxivPaperMapping.objects.get_or_create(
                            local_paper=paper,
                            arxiv_id=arxiv_paper['arxiv_id'],
                            defaults={
                                'confidence_score': similarity,
                                'mapping_source': 'automatic',
                                'is_verified': False
                            }
                        )
                        
                        if created:
                            # Update Scholar paper with arXiv data
                            paper.arxiv_id = arxiv_paper['arxiv_id']
                            if not paper.abstract and arxiv_paper.get('abstract'):
                                paper.abstract = arxiv_paper['abstract']
                            paper.save()
                            
                            enhanced_count += 1
                        break
            
            return enhanced_count
            
        except Exception as e:
            logger.error(f"Error enhancing Scholar papers: {e}")
            return 0
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles."""
        import re
        
        # Normalize titles
        def normalize(text):
            # Remove special characters and extra spaces
            text = re.sub(r'[^\w\s]', '', text.lower())
            return ' '.join(text.split())
        
        norm1 = normalize(title1)
        norm2 = normalize(title2)
        
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
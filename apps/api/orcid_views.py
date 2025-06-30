#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORCID API Views

RESTful API endpoints for ORCID integration functionality.
"""

import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from apps.orcid_app.models import OrcidProfile, OrcidOAuth2Token, OrcidPublication, OrcidWork, OrcidSyncLog
from apps.orcid_app.services import (
    OrcidAuthService, OrcidSyncService, OrcidIntegrationService, 
    OrcidAPIError, is_orcid_configured
)


@login_required
@require_http_methods(["GET"])
def auth_status(request):
    """Get ORCID authentication status for user"""
    try:
        token = OrcidOAuth2Token.objects.get(user=request.user)
        profile = OrcidProfile.objects.get(user=request.user)
        
        return JsonResponse({
            'success': True,
            'connected': True,
            'orcid_id': profile.orcid_id,
            'profile': {
                'display_name': profile.get_display_name(),
                'given_name': profile.given_name,
                'family_name': profile.family_name,
                'credit_name': profile.credit_name,
                'biography': profile.biography,
                'current_affiliation': profile.current_affiliation,
                'keywords': profile.keywords,
                'researcher_urls': profile.researcher_urls,
                'is_synced': profile.is_synced,
                'last_sync_at': profile.last_sync_at.isoformat() if profile.last_sync_at else None,
                'needs_sync': profile.needs_sync(),
                'publications_count': profile.get_publication_count(),
                'public_profile': profile.public_profile,
                'show_publications': profile.show_publications,
            },
            'token': {
                'expires_at': token.expires_at.isoformat(),
                'is_expired': token.is_expired(),
                'is_expiring_soon': token.is_expiring_soon(),
                'scope': token.scope,
            },
            'orcid_url': profile.get_orcid_url(),
        })
        
    except (OrcidOAuth2Token.DoesNotExist, OrcidProfile.DoesNotExist):
        return JsonResponse({
            'success': True,
            'connected': False,
            'is_configured': is_orcid_configured(),
        })


@login_required
@require_http_methods(["POST"])
def connect(request):
    """Initiate ORCID OAuth2 connection"""
    if not is_orcid_configured():
        return JsonResponse({
            'success': False,
            'error': 'ORCID integration is not configured'
        }, status=400)
    
    try:
        # Generate state parameter for security
        import uuid
        state = str(uuid.uuid4())
        request.session['orcid_oauth_state'] = state
        
        # Generate authorization URL
        auth_url = OrcidAuthService.get_authorization_url(state=state)
        
        return JsonResponse({
            'success': True,
            'auth_url': auth_url,
            'state': state,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def disconnect(request):
    """Disconnect ORCID account"""
    try:
        data = json.loads(request.body) if request.body else {}
        delete_profile = data.get('delete_profile', False)
        
        # Delete token
        OrcidOAuth2Token.objects.filter(user=request.user).delete()
        
        if delete_profile:
            # Delete profile and all related data
            OrcidProfile.objects.filter(user=request.user).delete()
        else:
            # Just mark as not synced
            try:
                profile = OrcidProfile.objects.get(user=request.user)
                profile.is_synced = False
                profile.save()
            except OrcidProfile.DoesNotExist:
                pass
        
        return JsonResponse({
            'success': True,
            'message': 'ORCID account disconnected successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def profile_detail(request):
    """Get detailed ORCID profile information"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        
        return JsonResponse({
            'success': True,
            'profile': {
                'id': str(profile.id),
                'orcid_id': profile.orcid_id,
                'display_name': profile.get_display_name(),
                'given_name': profile.given_name,
                'family_name': profile.family_name,
                'credit_name': profile.credit_name,
                'biography': profile.biography,
                'current_affiliation': profile.current_affiliation,
                'affiliations': profile.affiliations,
                'keywords': profile.keywords,
                'researcher_urls': profile.researcher_urls,
                'is_synced': profile.is_synced,
                'last_sync_at': profile.last_sync_at.isoformat() if profile.last_sync_at else None,
                'needs_sync': profile.needs_sync(),
                'public_profile': profile.public_profile,
                'show_publications': profile.show_publications,
                'sync_publications': profile.sync_publications,
                'auto_sync_enabled': profile.auto_sync_enabled,
                'created_at': profile.created_at.isoformat(),
                'updated_at': profile.updated_at.isoformat(),
                'orcid_url': profile.get_orcid_url(),
                'publications_count': profile.get_publication_count(),
            }
        })
        
    except OrcidProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'ORCID profile not found'
        }, status=404)


@login_required
@require_http_methods(["POST"])
def sync_profile(request):
    """Sync ORCID profile data"""
    try:
        sync_service = OrcidSyncService(request.user)
        success = sync_service.sync_profile()
        
        if success:
            # Get updated profile
            profile = OrcidProfile.objects.get(user=request.user)
            return JsonResponse({
                'success': True,
                'message': 'Profile synced successfully',
                'profile': {
                    'display_name': profile.get_display_name(),
                    'is_synced': profile.is_synced,
                    'last_sync_at': profile.last_sync_at.isoformat() if profile.last_sync_at else None,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Profile sync failed'
            }, status=400)
            
    except OrcidAPIError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def publications_list(request):
    """List ORCID publications with filtering and pagination"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        publications = profile.orcid_publications.all()
        
        # Filtering
        pub_type = request.GET.get('type')
        if pub_type:
            publications = publications.filter(publication_type=pub_type)
        
        search = request.GET.get('search')
        if search:
            publications = publications.filter(
                Q(title__icontains=search) |
                Q(journal__icontains=search) |
                Q(authors__icontains=search)
            )
        
        imported_only = request.GET.get('imported_only', '').lower() == 'true'
        if imported_only:
            publications = publications.filter(is_imported=True)
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)  # Max 100 per page
        
        paginator = Paginator(publications, page_size)
        page_obj = paginator.get_page(page)
        
        publications_data = []
        for pub in page_obj.object_list:
            publications_data.append({
                'id': str(pub.id),
                'title': pub.title,
                'publication_type': pub.publication_type,
                'publication_type_display': pub.get_publication_type_display(),
                'publication_year': pub.publication_year,
                'publication_date': pub.publication_date.isoformat() if pub.publication_date else None,
                'journal': pub.journal,
                'volume': pub.volume,
                'issue': pub.issue,
                'pages': pub.pages,
                'doi': pub.doi,
                'pmid': pub.pmid,
                'url': pub.url,
                'authors': pub.authors,
                'authors_display': pub.get_authors_display(),
                'is_imported': pub.is_imported,
                'scholar_paper_id': str(pub.scholar_paper.id) if pub.scholar_paper else None,
                'can_import': pub.can_import_to_scholar(),
                'created_at': pub.created_at.isoformat(),
                'updated_at': pub.updated_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'publications': publications_data,
            'pagination': {
                'page': page_obj.number,
                'pages': paginator.num_pages,
                'total': paginator.count,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            },
            'filters': {
                'type': pub_type,
                'search': search,
                'imported_only': imported_only,
            }
        })
        
    except OrcidProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'ORCID profile not found'
        }, status=404)


@login_required
@require_http_methods(["POST"])
def sync_publications(request):
    """Sync ORCID publications"""
    try:
        sync_service = OrcidSyncService(request.user)
        success = sync_service.sync_works()
        
        if success:
            profile = OrcidProfile.objects.get(user=request.user)
            return JsonResponse({
                'success': True,
                'message': 'Publications synced successfully',
                'publications_count': profile.get_publication_count(),
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Publications sync failed'
            }, status=400)
            
    except OrcidAPIError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def publication_detail(request, publication_id):
    """Get detailed publication information"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        publication = get_object_or_404(OrcidPublication, id=publication_id, profile=profile)
        
        return JsonResponse({
            'success': True,
            'publication': {
                'id': str(publication.id),
                'title': publication.title,
                'publication_type': publication.publication_type,
                'publication_type_display': publication.get_publication_type_display(),
                'publication_year': publication.publication_year,
                'publication_date': publication.publication_date.isoformat() if publication.publication_date else None,
                'journal': publication.journal,
                'volume': publication.volume,
                'issue': publication.issue,
                'pages': publication.pages,
                'doi': publication.doi,
                'pmid': publication.pmid,
                'isbn': publication.isbn,
                'issn': publication.issn,
                'url': publication.url,
                'abstract': publication.abstract,
                'authors': publication.authors,
                'authors_display': publication.get_authors_display(),
                'orcid_put_code': publication.orcid_put_code,
                'orcid_raw_data': publication.orcid_raw_data,
                'is_imported': publication.is_imported,
                'scholar_paper_id': str(publication.scholar_paper.id) if publication.scholar_paper else None,
                'can_import': publication.can_import_to_scholar(),
                'citation_apa': publication.get_citation_format('apa'),
                'created_at': publication.created_at.isoformat(),
                'updated_at': publication.updated_at.isoformat(),
            }
        })
        
    except OrcidProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'ORCID profile not found'
        }, status=404)


@login_required
@require_http_methods(["POST"])
def import_publication(request, publication_id):
    """Import ORCID publication to Scholar module"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        publication = get_object_or_404(OrcidPublication, id=publication_id, profile=profile)
        
        if publication.is_imported:
            return JsonResponse({
                'success': False,
                'error': 'Publication is already imported'
            }, status=400)
        
        scholar_paper = OrcidIntegrationService.import_publication_to_scholar(publication)
        
        if scholar_paper:
            return JsonResponse({
                'success': True,
                'message': 'Publication imported successfully',
                'scholar_paper_id': str(scholar_paper.id),
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to import publication'
            }, status=400)
            
    except OrcidProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'ORCID profile not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def bulk_import_publications(request):
    """Bulk import ORCID publications to Scholar"""
    try:
        data = json.loads(request.body)
        publication_ids = data.get('publication_ids', [])
        
        if not publication_ids:
            return JsonResponse({
                'success': False,
                'error': 'No publication IDs provided'
            }, status=400)
        
        imported_count = OrcidIntegrationService.bulk_import_publications(
            request.user, 
            publication_ids
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully imported {imported_count} publications',
            'imported_count': imported_count,
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def works_list(request):
    """List ORCID works"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        works = profile.orcid_works.all()
        
        # Filtering
        work_type = request.GET.get('type')
        if work_type:
            works = works.filter(work_type=work_type)
        
        search = request.GET.get('search')
        if search:
            works = works.filter(
                Q(title__icontains=search) |
                Q(journal_title__icontains=search)
            )
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        
        paginator = Paginator(works, page_size)
        page_obj = paginator.get_page(page)
        
        works_data = []
        for work in page_obj.object_list:
            works_data.append({
                'id': str(work.id),
                'title': work.title,
                'work_type': work.work_type,
                'work_type_display': work.get_work_type_display(),
                'publication_date': work.publication_date.isoformat() if work.publication_date else None,
                'journal_title': work.journal_title,
                'short_description': work.short_description,
                'url': work.url,
                'doi': work.get_doi(),
                'is_imported': work.is_imported,
                'created_at': work.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'works': works_data,
            'pagination': {
                'page': page_obj.number,
                'pages': paginator.num_pages,
                'total': paginator.count,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
        
    except OrcidProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'ORCID profile not found'
        }, status=404)


@login_required
@require_http_methods(["GET"])
def work_detail(request, work_id):
    """Get detailed work information"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        work = get_object_or_404(OrcidWork, id=work_id, profile=profile)
        
        return JsonResponse({
            'success': True,
            'work': {
                'id': str(work.id),
                'title': work.title,
                'work_type': work.work_type,
                'work_type_display': work.get_work_type_display(),
                'publication_date': work.publication_date.isoformat() if work.publication_date else None,
                'journal_title': work.journal_title,
                'short_description': work.short_description,
                'external_ids': work.external_ids,
                'url': work.url,
                'put_code': work.put_code,
                'raw_data': work.raw_data,
                'is_imported': work.is_imported,
                'doi': work.get_doi(),
                'created_at': work.created_at.isoformat(),
                'updated_at': work.updated_at.isoformat(),
            }
        })
        
    except OrcidProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'ORCID profile not found'
        }, status=404)


@login_required
@require_http_methods(["GET"])
def sync_logs(request):
    """Get ORCID sync logs"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        logs = profile.sync_logs.order_by('-started_at')
        
        # Filtering
        sync_type = request.GET.get('type')
        if sync_type:
            logs = logs.filter(sync_type=sync_type)
        
        status = request.GET.get('status')
        if status:
            logs = logs.filter(status=status)
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        
        paginator = Paginator(logs, page_size)
        page_obj = paginator.get_page(page)
        
        logs_data = []
        for log in page_obj.object_list:
            logs_data.append({
                'id': str(log.id),
                'sync_type': log.sync_type,
                'sync_type_display': log.get_sync_type_display(),
                'status': log.status,
                'status_display': log.get_status_display(),
                'items_processed': log.items_processed,
                'items_created': log.items_created,
                'items_updated': log.items_updated,
                'items_skipped': log.items_skipped,
                'error_message': log.error_message,
                'started_at': log.started_at.isoformat(),
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'duration_seconds': log.duration_seconds,
                'success_rate': log.get_success_rate(),
            })
        
        return JsonResponse({
            'success': True,
            'logs': logs_data,
            'pagination': {
                'page': page_obj.number,
                'pages': paginator.num_pages,
                'total': paginator.count,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
        
    except OrcidProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'ORCID profile not found'
        }, status=404)


@login_required
@require_http_methods(["GET"])
def sync_log_detail(request, log_id):
    """Get detailed sync log information"""
    try:
        profile = OrcidProfile.objects.get(user=request.user)
        log = get_object_or_404(OrcidSyncLog, id=log_id, profile=profile)
        
        return JsonResponse({
            'success': True,
            'log': {
                'id': str(log.id),
                'sync_type': log.sync_type,
                'sync_type_display': log.get_sync_type_display(),
                'status': log.status,
                'status_display': log.get_status_display(),
                'items_processed': log.items_processed,
                'items_created': log.items_created,
                'items_updated': log.items_updated,
                'items_skipped': log.items_skipped,
                'error_message': log.error_message,
                'error_details': log.error_details,
                'started_at': log.started_at.isoformat(),
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'duration_seconds': log.duration_seconds,
                'success_rate': log.get_success_rate(),
            }
        })
        
    except OrcidProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'ORCID profile not found'
        }, status=404)


@login_required
@require_http_methods(["POST"])
def full_sync(request):
    """Perform full ORCID synchronization"""
    try:
        sync_service = OrcidSyncService(request.user)
        success = sync_service.full_sync()
        
        if success:
            profile = OrcidProfile.objects.get(user=request.user)
            return JsonResponse({
                'success': True,
                'message': 'Full synchronization completed successfully',
                'profile': {
                    'is_synced': profile.is_synced,
                    'last_sync_at': profile.last_sync_at.isoformat() if profile.last_sync_at else None,
                    'publications_count': profile.get_publication_count(),
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Full synchronization completed with errors'
            }, status=400)
            
    except OrcidAPIError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=500)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.writer_app.models import (
    DocumentTemplate, Manuscript, ManuscriptSection, 
    Figure, Table, Citation, CompilationJob, AIAssistanceLog
)
from apps.api.serializers import (
    DocumentTemplateSerializer, ManuscriptSerializer
)
import os
import subprocess
import uuid

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def compile_document(request):
    """Compile LaTeX document using SciTeX-Doc."""
    manuscript_id = request.data.get('manuscript_id')
    
    try:
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create compilation job
        job = CompilationJob.objects.create(
            manuscript=manuscript,
            initiated_by=request.user,
            compilation_type='full'
        )
        
        # Generate LaTeX content
        latex_content = manuscript.generate_latex()
        
        # Create temporary directory for compilation
        compile_dir = f'/tmp/scitex-compile-{job.id}'
        os.makedirs(compile_dir, exist_ok=True)
        
        # Write LaTeX file
        tex_path = os.path.join(compile_dir, 'manuscript.tex')
        with open(tex_path, 'w') as f:
            f.write(latex_content)
        
        # Compile LaTeX (simplified for now)
        try:
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 'manuscript.tex'],
                cwd=compile_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                job.status = 'completed'
                job.completed_at = timezone.now()
                job.output_path = os.path.join(compile_dir, 'manuscript.pdf')
                job.save()
                
                return Response({
                    'compile_id': str(job.id),
                    'status': 'completed',
                    'message': 'Document compiled successfully',
                    'pdf_url': f'/api/v1/doc/download/{job.id}/'
                }, status=status.HTTP_200_OK)
            else:
                job.status = 'failed'
                job.error_log = result.stderr
                job.save()
                
                return Response({
                    'compile_id': str(job.id),
                    'status': 'failed',
                    'error': 'Compilation failed',
                    'details': result.stderr
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except subprocess.TimeoutExpired:
            job.status = 'failed'
            job.error_log = 'Compilation timeout'
            job.save()
            
            return Response({
                'compile_id': str(job.id),
                'status': 'failed',
                'error': 'Compilation timeout'
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
            
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_templates(request):
    """List available document templates."""
    templates = DocumentTemplate.objects.filter(is_public=True) | DocumentTemplate.objects.filter(created_by=request.user)
    serializer = DocumentTemplateSerializer(templates, many=True)
    return Response({
        'templates': serializer.data,
        'total': templates.count()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_revisions(request, manuscript_id):
    """List document revisions."""
    manuscript = get_object_or_404(Manuscript, id=manuscript_id)
    
    # Check permissions
    if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Get compilation history as revisions
    compilations = CompilationJob.objects.filter(
        manuscript=manuscript
    ).order_by('-created_at')
    
    revisions = []
    for job in compilations:
        revisions.append({
            'id': str(job.id),
            'created_at': job.created_at.isoformat(),
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'status': job.status,
            'initiated_by': job.initiated_by.username,
            'type': job.compilation_type
        })
    
    return Response({
        'revisions': revisions,
        'total': compilations.count()
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_document(request):
    """Export document to various formats."""
    manuscript_id = request.data.get('manuscript_id')
    export_format = request.data.get('format', 'pdf')
    
    manuscript = get_object_or_404(Manuscript, id=manuscript_id)
    
    # Check permissions
    if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    export_id = str(uuid.uuid4())
    
    if export_format == 'latex':
        # Return raw LaTeX
        return Response({
            'export_id': export_id,
            'status': 'completed',
            'format': 'latex',
            'content': manuscript.generate_latex()
        })
    elif export_format == 'pdf':
        # Trigger PDF compilation
        return compile_document(request)
    else:
        return Response({
            'error': 'Unsupported format'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_citations(request):
    """Manage document citations."""
    if request.method == 'GET':
        manuscript_id = request.GET.get('manuscript_id')
        if not manuscript_id:
            return Response({
                'error': 'manuscript_id required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        citations = Citation.objects.filter(manuscript=manuscript)
        citation_data = []
        for cite in citations:
            citation_data.append({
                'id': str(cite.id),
                'key': cite.citation_key,
                'type': cite.entry_type,
                'authors': cite.authors,
                'title': cite.title,
                'year': cite.year,
                'journal': cite.journal,
                'doi': cite.doi
            })
        
        return Response({
            'citations': citation_data,
            'total': citations.count()
        })
    
    else:  # POST
        manuscript_id = request.data.get('manuscript_id')
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create citation
        citation = Citation.objects.create(
            manuscript=manuscript,
            citation_key=request.data.get('key', f'cite{Citation.objects.filter(manuscript=manuscript).count() + 1}'),
            entry_type=request.data.get('type', 'article'),
            authors=request.data.get('authors', ''),
            title=request.data.get('title', ''),
            year=request.data.get('year'),
            journal=request.data.get('journal', ''),
            doi=request.data.get('doi', ''),
            url=request.data.get('url', ''),
            bibtex_entry=request.data.get('bibtex', '')
        )
        
        return Response({
            'citation_id': str(citation.id),
            'key': citation.citation_key,
            'status': 'added'
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_section(request):
    """Generate section content using AI assistance."""
    manuscript_id = request.data.get('manuscript_id')
    section_type = request.data.get('section_type')
    prompt = request.data.get('prompt', '')
    
    manuscript = get_object_or_404(Manuscript, id=manuscript_id)
    
    # Check permissions
    if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Log AI assistance request
    ai_log = AIAssistanceLog.objects.create(
        manuscript=manuscript,
        user=request.user,
        assistance_type='generate_section',
        section_type=section_type,
        prompt=prompt
    )
    
    # Placeholder for AI generation (would integrate with actual AI service)
    generated_content = f"This is a placeholder for AI-generated {section_type} content based on: {prompt}"
    
    ai_log.generated_text = generated_content
    ai_log.tokens_used = len(generated_content.split())
    ai_log.save()
    
    return Response({
        'content': generated_content,
        'section_type': section_type,
        'tokens_used': ai_log.tokens_used
    }, status=status.HTTP_200_OK)
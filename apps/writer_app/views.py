from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse, Http404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import models
from django.utils.text import slugify
from .models import (
    DocumentTemplate, Manuscript, ManuscriptSection,
    Figure, Table, Citation, CompilationJob, AIAssistanceLog
)
from apps.core_app.models import Project
from apps.core_app.directory_manager import get_user_directory_manager
import json
import uuid
import subprocess
import os
from pathlib import Path
from datetime import datetime


def index(request):
    """SciTeX Writer MVP landing page."""
    # Get popular templates
    popular_templates = DocumentTemplate.objects.filter(
        is_public=True
    ).order_by('-usage_count')[:6]
    
    # MVP stats for landing page
    stats = {
        'total_manuscripts': Manuscript.objects.count(),
        'total_compilations': CompilationJob.objects.filter(status='completed').count(),
        'active_users': Manuscript.objects.values('owner').distinct().count(),
    }
    
    context = {
        'popular_templates': popular_templates,
        'stats': stats,
        'is_mvp': True,  # MVP flag for templates
    }
    return render(request, 'writer_app/index.html', context)


def features(request):
    """Doc features view."""
    return render(request, 'writer_app/features.html')


def pricing(request):
    """Doc pricing view."""
    return render(request, 'writer_app/pricing.html')


@login_required
def dashboard(request):
    """Doc dashboard for authenticated users."""
    # Get user's manuscripts
    manuscripts = Manuscript.objects.filter(
        models.Q(owner=request.user) | models.Q(collaborators=request.user)
    ).distinct()
    
    # Recent activity
    recent_manuscripts = manuscripts.order_by('-updated_at')[:5]
    
    # Statistics
    total_manuscripts = manuscripts.count()
    draft_count = manuscripts.filter(status='draft').count()
    submitted_count = manuscripts.filter(status='submitted').count()
    published_count = manuscripts.filter(status='published').count()
    
    context = {
        'recent_manuscripts': recent_manuscripts,
        'total_manuscripts': total_manuscripts,
        'draft_count': draft_count,
        'submitted_count': submitted_count,
        'published_count': published_count,
    }
    
    return render(request, 'writer_app/dashboard.html', context)


@login_required
def manuscript_list(request):
    """List all user's manuscripts."""
    # Get manuscripts
    manuscripts = Manuscript.objects.filter(
        models.Q(owner=request.user) | models.Q(collaborators=request.user)
    ).distinct()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        manuscripts = manuscripts.filter(status=status)
    
    # Search
    query = request.GET.get('q')
    if query:
        manuscripts = manuscripts.filter(
            models.Q(title__icontains=query) |
            models.Q(abstract__icontains=query) |
            models.Q(keywords__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(manuscripts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status,
        'search_query': query,
    }
    
    return render(request, 'writer_app/manuscript_list.html', context)


@login_required
def project_writer(request, project_id):
    """Project-linked Writer interface."""
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
    except Project.DoesNotExist:
        messages.error(request, 'Project not found or access denied.')
        return redirect('core:dashboard')
    
    # Get or create manuscript for this project
    manuscript, created = Manuscript.objects.get_or_create(
        project=project,
        owner=request.user,
        defaults={
            'title': f'{project.name} Manuscript',
            'slug': f'{project.name.lower().replace(" ", "-")}-manuscript-{uuid.uuid4().hex[:8]}',
            'is_modular': True
        }
    )
    
    if created:
        # Create modular structure for new manuscript
        manuscript.create_modular_structure()
    
    # Get sections if modular
    sections_data = {}
    if manuscript.is_modular:
        paper_path = manuscript.get_project_paper_path()
        if paper_path:
            section_files = {
                'abstract': 'manuscript/src/abstract.tex',
                'introduction': 'manuscript/src/introduction.tex', 
                'methods': 'manuscript/src/methods.tex',
                'results': 'manuscript/src/results.tex',
                'discussion': 'manuscript/src/discussion.tex',
                'conclusion': 'manuscript/src/conclusion.tex'
            }
            
            for section, file_path in section_files.items():
                full_path = paper_path / file_path
                if full_path.exists():
                    with open(full_path, 'r') as f:
                        sections_data[section] = f.read()
                else:
                    sections_data[section] = ''
    
    # Update word counts
    manuscript.update_word_counts()
    
    context = {
        'project': project,
        'manuscript': manuscript,
        'sections': sections_data,
        'is_modular': manuscript.is_modular
    }
    
    return render(request, 'writer_app/project_writer.html', context)


@login_required
def manuscript_create(request):
    """Create a new manuscript."""
    if request.method == 'POST':
        title = request.POST.get('title')
        template_id = request.POST.get('template')
        
        # Create manuscript
        manuscript = Manuscript.objects.create(
            title=title,
            slug=slugify(title),
            owner=request.user,
            template_id=template_id if template_id else None,
            content="""\\documentclass{article}
\\usepackage{amsmath}
\\usepackage{graphicx}

\\title{%s}
\\author{%s}
\\date{\\today}

\\begin{document}

\\maketitle

\\begin{abstract}
Your abstract here...
\\end{abstract}

\\section{Introduction}
Start writing your introduction here...

\\section{Methods}

\\section{Results}

\\section{Discussion}

\\section{Conclusion}

\\bibliographystyle{plain}
\\bibliography{references}

\\end{document}""" % (title, request.user.get_full_name() or request.user.username)
        )
        
        # Create default sections
        sections = [
            ('abstract', 'Abstract', 1),
            ('introduction', 'Introduction', 2),
            ('methods', 'Methods', 3),
            ('results', 'Results', 4),
            ('discussion', 'Discussion', 5),
            ('conclusion', 'Conclusion', 6),
        ]
        
        for section_type, title, order in sections:
            ManuscriptSection.objects.create(
                manuscript=manuscript,
                section_type=section_type,
                title=title,
                order=order,
                content=''
            )
        
        messages.success(request, 'Manuscript created successfully!')
        return redirect('doc:manuscript-edit', slug=manuscript.slug)
    
    # Get available templates
    templates = DocumentTemplate.objects.filter(is_public=True)
    
    context = {
        'templates': templates,
    }
    
    return render(request, 'writer_app/manuscript_create.html', context)


@login_required
def manuscript_edit(request, slug):
    """Edit a manuscript."""
    # Get manuscript and check permissions
    try:
        manuscript = Manuscript.objects.get(slug=slug)
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            messages.error(request, 'You do not have permission to edit this manuscript.')
            return redirect('doc:manuscript-list')
    except Manuscript.DoesNotExist:
        raise Http404("Manuscript not found")
    
    if request.method == 'POST':
        # Update manuscript
        manuscript.title = request.POST.get('title', manuscript.title)
        manuscript.abstract = request.POST.get('abstract', manuscript.abstract)
        manuscript.keywords = request.POST.get('keywords', manuscript.keywords)
        manuscript.content = request.POST.get('content', manuscript.content)
        manuscript.save()
        
        messages.success(request, 'Manuscript saved successfully!')
        return redirect('doc:manuscript-edit', slug=manuscript.slug)
    
    # Get sections
    sections = manuscript.sections.all()
    
    # Get figures and tables
    figures = manuscript.figures.all()
    tables = manuscript.tables.all()
    
    # Get citations
    citations = manuscript.citations.all()
    
    context = {
        'manuscript': manuscript,
        'sections': sections,
        'figures': figures,
        'tables': tables,
        'citations': citations,
    }
    
    return render(request, 'writer_app/manuscript_edit.html', context)


@login_required
def compile_modular_manuscript(request, project_id):
    """Compile modular manuscript using paper/compile.sh."""
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        manuscript = Manuscript.objects.get(project=project, owner=request.user)
    except (Project.DoesNotExist, Manuscript.DoesNotExist):
        return JsonResponse({'error': 'Project or manuscript not found'}, status=404)
    
    if not manuscript.is_modular:
        return JsonResponse({'error': 'Manuscript is not modular'}, status=400)
    
    paper_path = manuscript.get_project_paper_path()
    if not paper_path or not paper_path.exists():
        return JsonResponse({'error': 'Paper directory not found'}, status=404)
    
    compile_script = paper_path / 'compile.sh'
    if not compile_script.exists():
        return JsonResponse({'error': 'Compile script not found'}, status=404)
    
    # Create compilation job
    job = CompilationJob.objects.create(
        manuscript=manuscript,
        status='queued',
        compilation_type='modular'
    )
    
    # Run compilation in background
    import threading
    
    def run_modular_compilation():
        try:
            job.status = 'running'
            job.started_at = timezone.now()
            job.save()
            
            # Run compile.sh script
            result = subprocess.run(
                ['bash', 'compile.sh'],
                cwd=paper_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # Check if PDF was created
                pdf_path = paper_path / 'manuscript' / 'main.pdf'
                if pdf_path.exists():
                    # Copy PDF to media directory for serving
                    import shutil
                    from django.conf import settings
                    
                    pdf_dir = Path(settings.MEDIA_ROOT) / 'compilations'
                    pdf_dir.mkdir(exist_ok=True)
                    output_path = pdf_dir / f'{job.job_id}.pdf'
                    
                    shutil.copy2(pdf_path, output_path)
                    
                    job.status = 'completed'
                    job.output_path = str(output_path.relative_to(settings.MEDIA_ROOT))
                    job.log_file = result.stdout
                    
                    # Count pages in PDF
                    try:
                        import PyPDF2
                        with open(output_path, 'rb') as f:
                            reader = PyPDF2.PdfReader(f)
                            job.page_count = len(reader.pages)
                    except:
                        pass
                else:
                    job.status = 'failed'
                    job.error_message = 'PDF file not generated'
                    job.error_log = result.stdout + '\n' + result.stderr
            else:
                job.status = 'failed'
                job.error_message = f'Compilation failed with exit code {result.returncode}'
                job.error_log = result.stderr
                job.log_file = result.stdout
                
        except subprocess.TimeoutExpired:
            job.status = 'failed'
            job.error_message = 'Compilation timed out'
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
        finally:
            job.completed_at = timezone.now()
            if job.started_at:
                job.compilation_time = (job.completed_at - job.started_at).total_seconds()
            job.save()
    
    compilation_thread = threading.Thread(target=run_modular_compilation)
    compilation_thread.daemon = True
    compilation_thread.start()
    
    return JsonResponse({
        'success': True,
        'job_id': str(job.job_id),
        'message': 'Modular compilation started'
    })


@login_required
def save_section(request, project_id):
    """Save a section of modular manuscript."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        manuscript = Manuscript.objects.get(project=project, owner=request.user)
    except (Project.DoesNotExist, Manuscript.DoesNotExist):
        return JsonResponse({'error': 'Project or manuscript not found'}, status=404)
    
    if not manuscript.is_modular:
        return JsonResponse({'error': 'Manuscript is not modular'}, status=400)
    
    try:
        data = json.loads(request.body)
        section = data.get('section')
        content = data.get('content', '')
        
        if section not in ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion']:
            return JsonResponse({'error': 'Invalid section'}, status=400)
        
        paper_path = manuscript.get_project_paper_path()
        if not paper_path:
            return JsonResponse({'error': 'Paper directory not found'}, status=404)
        
        # Save section content
        section_file = paper_path / 'manuscript' / 'src' / f'{section}.tex'
        with open(section_file, 'w') as f:
            f.write(content)
        
        # Update word counts
        manuscript.update_word_counts()
        
        return JsonResponse({
            'success': True,
            'word_count': getattr(manuscript, f'word_count_{section}', 0),
            'total_words': manuscript.word_count_total
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def load_latex_section(request, project_id):
    """Load actual LaTeX file content for direct editing."""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=405)
    
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        manuscript = Manuscript.objects.get(project=project, owner=request.user)
    except (Project.DoesNotExist, Manuscript.DoesNotExist):
        return JsonResponse({'error': 'Project or manuscript not found'}, status=404)
    
    if not manuscript.is_modular:
        return JsonResponse({'error': 'Manuscript is not modular'}, status=400)
    
    section = request.GET.get('section')
    if section not in ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion']:
        return JsonResponse({'error': 'Invalid section'}, status=400)
    
    paper_path = manuscript.get_project_paper_path()
    if not paper_path:
        return JsonResponse({'error': 'Paper directory not found'}, status=404)
    
    # Load actual LaTeX file content
    section_file = paper_path / 'manuscript' / 'src' / f'{section}.tex'
    if section_file.exists():
        with open(section_file, 'r') as f:
            latex_content = f.read()
    else:
        latex_content = f'% {section.title()}\n'
    
    return JsonResponse({
        'success': True,
        'latex_content': latex_content
    })


@login_required
def save_latex_section(request, project_id):
    """Save LaTeX content directly to file and sync with text content."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        manuscript = Manuscript.objects.get(project=project, owner=request.user)
    except (Project.DoesNotExist, Manuscript.DoesNotExist):
        return JsonResponse({'error': 'Project or manuscript not found'}, status=404)
    
    if not manuscript.is_modular:
        return JsonResponse({'error': 'Manuscript is not modular'}, status=400)
    
    try:
        data = json.loads(request.body)
        section = data.get('section')
        latex_content = data.get('latex_content', '')
        
        if section not in ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion']:
            return JsonResponse({'error': 'Invalid section'}, status=400)
        
        paper_path = manuscript.get_project_paper_path()
        if not paper_path:
            return JsonResponse({'error': 'Paper directory not found'}, status=404)
        
        # Save LaTeX content directly to file
        section_file = paper_path / 'manuscript' / 'src' / f'{section}.tex'
        with open(section_file, 'w') as f:
            f.write(latex_content)
        
        # Update word counts based on the LaTeX content
        manuscript.update_word_counts()
        
        return JsonResponse({
            'success': True,
            'word_count': getattr(manuscript, f'word_count_{section}', 0),
            'total_words': manuscript.word_count_total
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def manuscript_compile(request, slug):
    """Compile a manuscript to PDF."""
    # Get manuscript and check permissions
    try:
        manuscript = Manuscript.objects.get(slug=slug)
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except Manuscript.DoesNotExist:
        return JsonResponse({'error': 'Manuscript not found'}, status=404)
    
    # Create compilation job
    job = CompilationJob.objects.create(
        manuscript=manuscript,
        status='queued'
    )
    
    # Start compilation asynchronously
    import threading
    from .utils import compile_latex_document
    
    def run_compilation():
        compile_latex_document(job)
    
    # Run compilation in background thread
    compilation_thread = threading.Thread(target=run_compilation)
    compilation_thread.daemon = True
    compilation_thread.start()
    
    return JsonResponse({
        'success': True,
        'job_id': str(job.job_id),
        'message': 'Compilation started successfully'
    })


@login_required
def compilation_status(request, job_id):
    """Check compilation job status."""
    job = get_object_or_404(CompilationJob, job_id=job_id)
    
    # Check permissions
    if job.manuscript.owner != request.user and request.user not in job.manuscript.collaborators.all():
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Calculate progress percentage
    progress = 0
    if job.status == 'queued':
        progress = 10
    elif job.status == 'running':
        progress = 50
    elif job.status == 'completed':
        progress = 100
    elif job.status == 'failed':
        progress = 0
    
    response_data = {
        'job_id': str(job.job_id),
        'status': job.status,
        'progress': progress,
        'message': f'Compilation {job.status}',
        'compilation_type': job.compilation_type,
        'created_at': job.created_at.isoformat(),
        'compilation_time': job.compilation_time,
        'page_count': job.page_count,
    }
    
    # Add PDF URL if available
    if job.output_pdf:
        response_data['pdf_url'] = job.output_pdf.url
        response_data['download_url'] = f'/writer/manuscript/{job.manuscript.slug}/download/{job.job_id}/'
    
    # Add error information if failed
    if job.status == 'failed':
        response_data['error'] = job.error_message
        response_data['error_details'] = job.error_log[:1000] if job.error_log else None  # Limit error log size
    
    # Add log information for debugging
    if job.log_file and request.user.is_staff:
        response_data['log'] = job.log_file[:1000]  # Only for staff users
    
    return JsonResponse(response_data)


@login_required
def toggle_editing_mode(request, project_id):
    """Toggle between text-based and LaTeX editing modes."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        manuscript = Manuscript.objects.get(project=project, owner=request.user)
    except (Project.DoesNotExist, Manuscript.DoesNotExist):
        return JsonResponse({'error': 'Project or manuscript not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        mode = data.get('mode')  # 'text' or 'latex'
        
        if mode not in ['text', 'latex']:
            return JsonResponse({'error': 'Invalid mode'}, status=400)
        
        return JsonResponse({
            'success': True,
            'mode': mode,
            'message': f'Switched to {mode} editing mode'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def mvp_editor(request):
    """MVP simplified manuscript editor."""
    # Get or create a draft manuscript for the user
    manuscript, created = Manuscript.objects.get_or_create(
        owner=request.user,
        title="Draft Manuscript",
        defaults={
            'slug': f"draft-{request.user.username}-{uuid.uuid4().hex[:8]}",
            'content': """% SciTeX Writer MVP - Quick Start Template
\\documentclass[12pt]{article}
\\usepackage[utf8]{inputenc}
\\usepackage{amsmath}
\\usepackage{graphicx}
\\usepackage[margin=1in]{geometry}

\\title{Your Manuscript Title}
\\author{Your Name}
\\date{\\today}

\\begin{document}

\\maketitle

\\begin{abstract}
Write your abstract here...
\\end{abstract}

\\section{Introduction}
Write your introduction here...

\\section{Methods}
Describe your methodology...

\\section{Results}
Present your results...

\\section{Discussion}
Discuss your findings...

\\section{Conclusion}
Conclude your work...

\\end{document}"""
        }
    )
    
    # Get recent compilation jobs
    recent_jobs = CompilationJob.objects.filter(
        manuscript__owner=request.user
    ).order_by('-created_at')[:5]
    
    context = {
        'manuscript': manuscript,
        'recent_jobs': recent_jobs,
        'is_mvp': True
    }
    return render(request, 'writer_app/mvp_editor.html', context)


@login_required
def get_manuscript_stats(request, project_id):
    """Get manuscript statistics including word counts and citation info."""
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        manuscript = Manuscript.objects.get(project=project, owner=request.user)
    except (Project.DoesNotExist, Manuscript.DoesNotExist):
        return JsonResponse({'error': 'Project or manuscript not found'}, status=404)
    
    # Update word counts before returning stats
    manuscript.update_word_counts()
    
    # Count citations in references.bib
    citation_count = 0
    unique_citations = 0
    
    if manuscript.is_modular:
        paper_path = manuscript.get_project_paper_path()
        if paper_path:
            bib_file = paper_path / 'references' / 'references.bib'
            if bib_file.exists():
                with open(bib_file, 'r') as f:
                    content = f.read()
                    # Count @article, @book, etc. entries
                    import re
                    entries = re.findall(r'@\w+\s*\{', content)
                    citation_count = len(entries)
                    unique_citations = citation_count  # For now, assume all are unique
    
    manuscript.citation_count = citation_count
    manuscript.unique_citation_count = unique_citations
    manuscript.save()
    
    stats = {
        'word_counts': {
            'abstract': manuscript.word_count_abstract,
            'introduction': manuscript.word_count_introduction,
            'methods': manuscript.word_count_methods,
            'results': manuscript.word_count_results,
            'discussion': manuscript.word_count_discussion,
            'total': manuscript.word_count_total
        },
        'citations': {
            'total': manuscript.citation_count,
            'unique': manuscript.unique_citation_count
        },
        'progress': {
            'sections_completed': sum(1 for count in [
                manuscript.word_count_abstract,
                manuscript.word_count_introduction,
                manuscript.word_count_methods,
                manuscript.word_count_results,
                manuscript.word_count_discussion
            ] if count > 0),
            'total_sections': 5
        }
    }
    
    return JsonResponse({
        'success': True,
        'stats': stats
    })


@login_required
def quick_compile(request):
    """MVP quick compile endpoint."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content', '')
            title = data.get('title', 'Quick Document')
            
            # Create or update a quick manuscript
            manuscript, created = Manuscript.objects.get_or_create(
                owner=request.user,
                title=title,
                defaults={
                    'slug': f"quick-{request.user.username}-{uuid.uuid4().hex[:8]}",
                    'content': content
                }
            )
            
            if not created:
                manuscript.content = content
                manuscript.save()
            
            # Create compilation job
            job = CompilationJob.objects.create(
                manuscript=manuscript,
                status='queued',
                compilation_type='quick'
            )
            
            # Start compilation
            import threading
            from .utils import compile_latex_document
            
            def run_compilation():
                compile_latex_document(job)
            
            compilation_thread = threading.Thread(target=run_compilation)
            compilation_thread.daemon = True
            compilation_thread.start()
            
            return JsonResponse({
                'success': True,
                'job_id': str(job.job_id),
                'message': 'Quick compilation started!'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def mvp_dashboard(request):
    """MVP dashboard with simplified interface."""
    # User's manuscripts
    manuscripts = Manuscript.objects.filter(owner=request.user).order_by('-updated_at')
    
    # Recent compilations
    recent_jobs = CompilationJob.objects.filter(
        manuscript__owner=request.user
    ).order_by('-created_at')[:10]
    
    # MVP metrics
    metrics = {
        'manuscripts_count': manuscripts.count(),
        'successful_compilations': recent_jobs.filter(status='completed').count(),
        'failed_compilations': recent_jobs.filter(status='failed').count(),
        'total_pages': sum([job.page_count or 0 for job in recent_jobs if job.page_count])
    }
    
    context = {
        'manuscripts': manuscripts[:10],  # Show only first 10 for MVP
        'recent_jobs': recent_jobs,
        'metrics': metrics,
        'is_mvp': True
    }
    return render(request, 'writer_app/mvp_dashboard.html', context)


@login_required
def templates(request):
    """Browse document templates."""
    template_list = DocumentTemplate.objects.filter(is_public=True)
    
    # Filter by type
    template_type = request.GET.get('type')
    if template_type:
        template_list = template_list.filter(template_type=template_type)
    
    # Search
    query = request.GET.get('q')
    if query:
        template_list = template_list.filter(
            models.Q(name__icontains=query) |
            models.Q(journal_name__icontains=query) |
            models.Q(description__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(template_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'type_filter': template_type,
        'search_query': query,
        'template_types': DocumentTemplate.TEMPLATE_TYPES,
    }
    
    return render(request, 'writer_app/templates.html', context)


@login_required
@require_http_methods(["POST"])
def ai_assist(request):
    """AI assistance endpoint."""
    try:
        data = json.loads(request.body)
        manuscript_id = data.get('manuscript_id')
        assistance_type = data.get('type')
        content = data.get('content')
        
        # Get manuscript and check permissions
        try:
            manuscript = Manuscript.objects.get(id=manuscript_id)
            if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
                return JsonResponse({'error': 'Permission denied'}, status=403)
        except Manuscript.DoesNotExist:
            return JsonResponse({'error': 'Manuscript not found'}, status=404)
        
        # Mock AI response for now
        suggested_text = f"Enhanced version of: {content[:100]}..."
        
        # Log the assistance
        ai_log = AIAssistanceLog.objects.create(
            manuscript=manuscript,
            user=request.user,
            assistance_type=assistance_type,
            original_text=content,
            suggested_text=suggested_text,
            tokens_used=len(content.split()),
            response_time=0.5
        )
        
        # Update manuscript AI tracking
        manuscript.ai_suggestions_count += 1
        manuscript.last_ai_assist = datetime.now()
        manuscript.save()
        
        return JsonResponse({
            'success': True,
            'suggestion': suggested_text,
            'log_id': ai_log.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def export_manuscript(request, slug):
    """Export manuscript in various formats."""
    # Get manuscript and check permissions
    try:
        manuscript = Manuscript.objects.get(slug=slug)
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except Manuscript.DoesNotExist:
        return JsonResponse({'error': 'Manuscript not found'}, status=404)
    
    format_type = request.GET.get('format', 'latex')
    
    if format_type == 'latex':
        # Return LaTeX source
        response = HttpResponse(manuscript.content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{manuscript.slug}.tex"'
        return response
    
    elif format_type == 'bibtex':
        # Return BibTeX entries
        citations = manuscript.citations.all()
        bibtex_content = '\n\n'.join([c.bibtex_entry for c in citations])
        response = HttpResponse(bibtex_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{manuscript.slug}.bib"'
        return response
    
    else:
        return JsonResponse({'error': 'Invalid format'}, status=400)
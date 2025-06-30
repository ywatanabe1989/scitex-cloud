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
    Figure, Table, Citation, CompilationJob, AIAssistanceLog,
    CollaborativeSession, DocumentChange, ManuscriptVersion,
    ManuscriptBranch, DiffResult, MergeRequest
)
from .version_control import VersionControlManager
from apps.project_app.models import Project
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
    """Load actual LaTeX file content directly from SciTeX-Writer structure."""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=405)
    
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        manuscript = Manuscript.objects.get(project=project, owner=request.user)
    except (Project.DoesNotExist, Manuscript.DoesNotExist):
        return JsonResponse({'error': 'Project or manuscript not found'}, status=404)
    
    section = request.GET.get('section')
    doc_type = request.GET.get('doc_type', 'manuscript')
    
    # Map section names to actual SciTeX-Writer file names
    section_mapping = {
        'manuscript': {
            'abstract': 'abstract.tex',
            'highlights': 'highlights.tex', 
            'introduction': 'introduction.tex',
            'methods': 'methods.tex',
            'results': 'results.tex',
            'discussion': 'discussion.tex',
            'title': 'title.tex',
            'authors': 'authors.tex',
            'keywords': 'keywords.tex'
        },
        'revision': {
            'introduction': 'introduction.tex',
            'commands': 'commands.tex', 
            'conclusion': 'conclusion.tex',
            'references': 'references.tex'
        },
        'supplementary': {
            'methods': 'methods.tex',
            'results': 'results.tex',
            'references': 'references.tex'
        }
    }
    
    if section not in section_mapping.get(doc_type, {}):
        return JsonResponse({'error': 'Invalid section for document type'}, status=400)
    
    paper_path = manuscript.get_project_paper_path()
    if not paper_path:
        return JsonResponse({'error': 'Paper directory not found'}, status=404)
    
    # Determine the correct path based on document type
    if doc_type == 'manuscript':
        section_file = paper_path / 'manuscript' / 'src' / section_mapping[doc_type][section]
    elif doc_type == 'revision':
        section_file = paper_path / 'revision' / 'src' / section_mapping[doc_type][section]
    elif doc_type == 'supplementary':
        section_file = paper_path / 'supplementary' / 'src' / section_mapping[doc_type][section]
    else:
        return JsonResponse({'error': 'Invalid document type'}, status=400)
    
    # Load actual LaTeX file content from SciTeX-Writer structure
    if section_file.exists():
        with open(section_file, 'r', encoding='utf-8') as f:
            latex_content = f.read()
    else:
        # Create file with SciTeX-Writer template if it doesn't exist
        latex_content = _get_scitex_writer_template(section, doc_type)
        section_file.parent.mkdir(parents=True, exist_ok=True)
        with open(section_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
    
    return JsonResponse({
        'success': True,
        'latex_content': latex_content,
        'file_path': str(section_file)
    })


def _get_scitex_writer_template(section, doc_type):
    """Get template content from SciTeX-Writer externals."""
    from django.conf import settings
    from pathlib import Path
    
    try:
        template_path = Path(settings.SCITEX_WRITER_TEMPLATE_PATH)
        
        # Try to read template from externals/SciTeX-Writer
        if doc_type == 'manuscript':
            template_file = template_path / 'manuscript' / 'src' / f'{section}.tex'
        elif doc_type == 'revision':
            template_file = template_path / 'revision' / 'src' / f'{section}.tex'  
        elif doc_type == 'supplementary':
            template_file = template_path / 'supplementary' / 'src' / f'{section}.tex'
        
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print(f"Error loading SciTeX-Writer template: {e}")
    
    # Fallback templates
    fallback_templates = {
        'abstract': '% Abstract\n% Write a concise summary of your research\n\n',
        'highlights': '% Highlights\n% List 3-5 key contributions\n\n',
        'introduction': '% Introduction\n% Provide background and motivation\n\n',
        'methods': '% Methods\n% Describe your methodology\n\n',
        'results': '% Results\n% Present your findings\n\n',
        'discussion': '% Discussion\n% Interpret your results\n\n',
        'title': '% Title\n\\title{Your Research Title}\n',
        'authors': '% Authors\n\\author{Your Name}\n',
        'keywords': '% Keywords\nKeyword1, Keyword2, Keyword3\n'
    }
    
    return fallback_templates.get(section, f'% {section.title()}\n\n')


@login_required
def save_latex_section(request, project_id):
    """Save LaTeX content directly to SciTeX-Writer file structure."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        manuscript = Manuscript.objects.get(project=project, owner=request.user)
    except (Project.DoesNotExist, Manuscript.DoesNotExist):
        return JsonResponse({'error': 'Project or manuscript not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        section = data.get('section')
        doc_type = data.get('doc_type', 'manuscript')
        latex_content = data.get('latex_content', '')
        
        # Use same mapping as load function
        section_mapping = {
            'manuscript': {
                'abstract': 'abstract.tex',
                'highlights': 'highlights.tex',
                'introduction': 'introduction.tex',
                'methods': 'methods.tex',
                'results': 'results.tex',
                'discussion': 'discussion.tex',
                'title': 'title.tex',
                'authors': 'authors.tex',
                'keywords': 'keywords.tex'
            },
            'revision': {
                'introduction': 'introduction.tex',
                'commands': 'commands.tex',
                'conclusion': 'conclusion.tex', 
                'references': 'references.tex'
            },
            'supplementary': {
                'methods': 'methods.tex',
                'results': 'results.tex',
                'references': 'references.tex'
            }
        }
        
        if section not in section_mapping.get(doc_type, {}):
            return JsonResponse({'error': 'Invalid section for document type'}, status=400)
        
        paper_path = manuscript.get_project_paper_path()
        if not paper_path:
            return JsonResponse({'error': 'Paper directory not found'}, status=404)
        
        # Determine correct file path
        if doc_type == 'manuscript':
            section_file = paper_path / 'manuscript' / 'src' / section_mapping[doc_type][section]
        elif doc_type == 'revision':
            section_file = paper_path / 'revision' / 'src' / section_mapping[doc_type][section]
        elif doc_type == 'supplementary':
            section_file = paper_path / 'supplementary' / 'src' / section_mapping[doc_type][section]
        
        # Save directly to SciTeX-Writer file structure
        section_file.parent.mkdir(parents=True, exist_ok=True)
        with open(section_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        # Update word counts based on the LaTeX content
        manuscript.update_word_counts()
        
        return JsonResponse({
            'success': True,
            'word_count': getattr(manuscript, f'word_count_{section}', 0),
            'total_words': manuscript.word_count_total,
            'file_path': str(section_file)
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
def cloud_compile_sections(request, project_id):
    """Cloud-based section-separated LaTeX compilation."""
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
        sections = data.get('sections', ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion'])
        
        # Create compilation job for section-separated compilation
        job = CompilationJob.objects.create(
            manuscript=manuscript,
            status='queued',
            compilation_type='sectioned'
        )
        
        # Start cloud compilation asynchronously
        import threading
        
        def run_cloud_compilation():
            compile_latex_cloud_sections(job, sections)
        
        compilation_thread = threading.Thread(target=run_cloud_compilation)
        compilation_thread.daemon = True
        compilation_thread.start()
        
        return JsonResponse({
            'success': True,
            'job_id': str(job.job_id),
            'message': 'Cloud section compilation started',
            'sections': sections
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def compile_latex_cloud_sections(job, sections):
    """Compile LaTeX sections using actual SciTeX-Writer compilation scripts."""
    try:
        job.status = 'running'
        job.save()
        
        manuscript = job.manuscript
        paper_path = manuscript.get_project_paper_path()
        
        if not paper_path:
            job.status = 'failed'
            job.error_message = 'Paper directory not found'
            job.save()
            return
        
        # Use SciTeX-Writer's actual compilation approach
        manuscript_dir = paper_path / 'manuscript'
        
        # Check if SciTeX-Writer compile script exists
        compile_script = manuscript_dir / 'compile.sh'
        if not compile_script.exists():
            # Create compile script using SciTeX-Writer template
            from django.conf import settings
            template_script = Path(settings.SCITEX_WRITER_TEMPLATE_PATH) / 'scripts' / 'compile-manuscript.sh'
            if template_script.exists():
                shutil.copy2(template_script, compile_script)
                compile_script.chmod(0o755)
        
        # Compile using SciTeX-Writer's own system
        result = compile_latex_scitex_writer(manuscript_dir, paper_path)
        
        if result['success']:
            job.status = 'completed'
            job.output_pdf = result['pdf_path']
            job.compilation_time = result.get('compilation_time', 0)
            job.page_count = result.get('page_count', 0)
        else:
            job.status = 'failed'
            job.error_message = result.get('error', 'Unknown compilation error')
            job.error_log = result.get('log', '')
        
    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
    
    job.save()


def generate_sectioned_latex(paper_path, sections):
    """Generate LaTeX document with specified sections."""
    latex_content = """\\documentclass[12pt]{article}
\\usepackage[utf8]{inputenc}
\\usepackage{amsmath}
\\usepackage{graphicx}
\\usepackage[margin=1in]{geometry}
\\usepackage{natbib}

\\title{SciTeX Cloud Document}
\\author{Generated by SciTeX Writer}
\\date{\\today}

\\begin{document}

\\maketitle

"""
    
    # Add each section
    for section in sections:
        section_file = paper_path / 'manuscript' / 'src' / f'{section}.tex'
        if section_file.exists():
            latex_content += f"\\section{{{section.title()}}}\n"
            with open(section_file, 'r') as f:
                latex_content += f.read() + "\n\n"
    
    # Add bibliography if exists
    bib_file = paper_path / 'references' / 'references.bib'
    if bib_file.exists():
        latex_content += """
\\bibliographystyle{plain}
\\bibliography{../references/references}
"""
    
    latex_content += "\\end{document}"
    return latex_content


def compile_latex_cloud(tex_path, paper_path):
    """Compile LaTeX document using cloud resources."""
    import time
    start_time = time.time()
    
    try:
        # Change to manuscript directory for compilation
        manuscript_dir = paper_path / 'manuscript'
        
        # Run pdflatex compilation
        cmd = ['pdflatex', '-interaction=nonstopmode', tex_path.name]
        result = subprocess.run(
            cmd,
            cwd=manuscript_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        compilation_time = time.time() - start_time
        
        # Check if PDF was generated
        pdf_path = manuscript_dir / f"{tex_path.stem}.pdf"
        if pdf_path.exists():
            # Count pages (simplified)
            page_count = 1  # Could use PyPDF2 for accurate count
            
            return {
                'success': True,
                'pdf_path': str(pdf_path),
                'compilation_time': compilation_time,
                'page_count': page_count,
                'log': result.stdout
            }
        else:
            return {
                'success': False,
                'error': 'PDF generation failed',
                'log': result.stdout + result.stderr
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Compilation timeout',
            'log': 'Compilation took too long and was terminated'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'log': f'Exception during compilation: {str(e)}'
        }


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
def download_paper_zip(request, project_id):
    """Download project paper directory as ZIP file."""
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        manuscript = Manuscript.objects.get(project=project, owner=request.user)
    except (Project.DoesNotExist, Manuscript.DoesNotExist):
        return JsonResponse({'error': 'Project or manuscript not found'}, status=404)
    
    paper_path = manuscript.get_project_paper_path()
    if not paper_path or not paper_path.exists():
        return JsonResponse({'error': 'Paper directory not found'}, status=404)
    
    # Create ZIP file
    import zipfile
    import tempfile
    from django.http import FileResponse
    
    # Create temporary ZIP file
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    
    try:
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from paper directory
            for file_path in paper_path.rglob('*'):
                if file_path.is_file():
                    # Use relative path within ZIP
                    arc_name = file_path.relative_to(paper_path)
                    zipf.write(file_path, arc_name)
        
        # Prepare response
        zip_filename = f"{project.name.replace(' ', '_')}_paper.zip"
        response = FileResponse(
            open(temp_zip.name, 'rb'),
            as_attachment=True,
            filename=zip_filename,
            content_type='application/zip'
        )
        
        # Clean up temp file after response (handled by FileResponse)
        import os
        response['X-Temp-File'] = temp_zip.name  # For cleanup reference
        
        return response
        
    except Exception as e:
        # Clean up on error
        import os
        if os.path.exists(temp_zip.name):
            os.unlink(temp_zip.name)
        return JsonResponse({'error': f'Failed to create ZIP: {str(e)}'}, status=500)


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
                'status_url': f'/writer/api/status/{job.job_id}/',
                'message': 'Quick compilation started!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Compilation failed to start'
            }, status=500)
    
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def test_compilation(request):
    """Test endpoint to verify PDF compilation works end-to-end."""
    if request.method == 'POST':
        try:
            from .utils import test_pdf_compilation
            
            # Run direct PDF compilation test
            test_result = test_pdf_compilation()
            
            if test_result['success']:
                # Create a test manuscript and compilation job
                test_content = r"""
\section{Introduction}
This is a test document for SciTeX Writer PDF compilation.

\subsection{Mathematical Expressions}
Here is an equation: $E = mc^2$

\subsection{Lists}
\begin{itemize}
\item First item
\item Second item
\item Third item
\end{itemize}

\section{Conclusion}
PDF compilation is working correctly.
"""
                
                manuscript, created = Manuscript.objects.get_or_create(
                    owner=request.user,
                    title="PDF Compilation Test",
                    defaults={
                        'slug': f"test-{request.user.username}-{uuid.uuid4().hex[:8]}",
                        'content': test_content
                    }
                )
                
                # Create compilation job
                job = CompilationJob.objects.create(
                    manuscript=manuscript,
                    status='queued',
                    compilation_type='test'
                )
                
                # Start compilation
                import threading
                from .utils import compile_latex_document
                
                def run_test_compilation():
                    compile_latex_document(job)
                
                compilation_thread = threading.Thread(target=run_test_compilation)
                compilation_thread.daemon = True
                compilation_thread.start()
                
                return JsonResponse({
                    'success': True,
                    'job_id': str(job.job_id),
                    'status_url': f'/writer/api/status/{job.job_id}/',
                    'test_result': test_result,
                    'message': 'Test compilation started successfully!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'test_result': test_result,
                    'message': 'PDF compilation test failed'
                }, status=500)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'Test compilation failed'
            }, status=500)
    
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


# Collaborative Editing API Views

@login_required
@require_http_methods(["GET"])
def collaborative_sessions(request, manuscript_id):
    """Get active collaborative sessions for a manuscript."""
    try:
        manuscript = Manuscript.objects.get(id=manuscript_id)
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except Manuscript.DoesNotExist:
        return JsonResponse({'error': 'Manuscript not found'}, status=404)
    
    # Get active sessions from last 5 minutes
    from django.utils import timezone
    from datetime import timedelta
    
    active_sessions = CollaborativeSession.objects.filter(
        manuscript=manuscript,
        is_active=True,
        last_activity__gte=timezone.now() - timedelta(minutes=5)
    ).select_related('user')
    
    sessions_data = []
    for session in active_sessions:
        sessions_data.append({
            'user_id': session.user.id,
            'username': session.user.username,
            'session_id': session.session_id,
            'started_at': session.started_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'locked_sections': session.locked_sections or [],
            'characters_typed': session.characters_typed,
            'operations_count': session.operations_count
        })
    
    return JsonResponse({
        'success': True,
        'sessions': sessions_data,
        'total_active': len(sessions_data)
    })


@login_required
@require_http_methods(["POST"])
def join_collaboration(request, manuscript_id):
    """Join a collaborative editing session."""
    try:
        manuscript = Manuscript.objects.get(id=manuscript_id)
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except Manuscript.DoesNotExist:
        return JsonResponse({'error': 'Manuscript not found'}, status=404)
    
    # Create or update collaborative session
    session, created = CollaborativeSession.objects.get_or_create(
        manuscript=manuscript,
        user=request.user,
        defaults={
            'session_id': str(uuid.uuid4()),
            'is_active': True
        }
    )
    
    if not created:
        session.session_id = str(uuid.uuid4())
        session.is_active = True
        session.save()
    
    return JsonResponse({
        'success': True,
        'session_id': session.session_id,
        'created': created
    })


@login_required
@require_http_methods(["POST"])
def leave_collaboration(request, manuscript_id):
    """Leave a collaborative editing session."""
    try:
        manuscript = Manuscript.objects.get(id=manuscript_id)
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except Manuscript.DoesNotExist:
        return JsonResponse({'error': 'Manuscript not found'}, status=404)
    
    # End collaborative session
    sessions = CollaborativeSession.objects.filter(
        manuscript=manuscript,
        user=request.user,
        is_active=True
    )
    
    for session in sessions:
        session.is_active = False
        session.ended_at = timezone.now()
        session.save()
    
    return JsonResponse({
        'success': True,
        'sessions_ended': len(sessions)
    })


@login_required
@require_http_methods(["POST"])
def lock_section(request, section_id):
    """Lock a section for exclusive editing."""
    try:
        section = ManuscriptSection.objects.get(id=section_id)
        manuscript = section.manuscript
        
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except ManuscriptSection.DoesNotExist:
        return JsonResponse({'error': 'Section not found'}, status=404)
    
    # Check if section is already locked by another user
    existing_lock = CollaborativeSession.objects.filter(
        manuscript=manuscript,
        locked_sections__contains=[str(section_id)],
        is_active=True
    ).exclude(user=request.user).first()
    
    if existing_lock:
        return JsonResponse({
            'success': False,
            'error': 'Section is already locked',
            'locked_by': existing_lock.user.username
        }, status=409)
    
    # Lock the section
    session, created = CollaborativeSession.objects.get_or_create(
        manuscript=manuscript,
        user=request.user,
        defaults={
            'session_id': str(uuid.uuid4()),
            'is_active': True,
            'locked_sections': [str(section_id)]
        }
    )
    
    if not created:
        if not session.locked_sections:
            session.locked_sections = []
        if str(section_id) not in session.locked_sections:
            session.locked_sections.append(str(section_id))
            session.save()
    
    return JsonResponse({
        'success': True,
        'section_id': section_id,
        'locked_by': request.user.username
    })


@login_required
@require_http_methods(["POST"])
def unlock_section(request, section_id):
    """Unlock a section."""
    try:
        section = ManuscriptSection.objects.get(id=section_id)
        manuscript = section.manuscript
        
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except ManuscriptSection.DoesNotExist:
        return JsonResponse({'error': 'Section not found'}, status=404)
    
    # Unlock the section
    try:
        session = CollaborativeSession.objects.get(
            manuscript=manuscript,
            user=request.user,
            is_active=True
        )
        
        if session.locked_sections and str(section_id) in session.locked_sections:
            session.locked_sections.remove(str(section_id))
            session.save()
        
        return JsonResponse({
            'success': True,
            'section_id': section_id
        })
        
    except CollaborativeSession.DoesNotExist:
        return JsonResponse({
            'success': True,
            'section_id': section_id,
            'message': 'No active session found'
        })


@login_required
def collaborative_editor(request, manuscript_id):
    """Collaborative manuscript editor with real-time features."""
    try:
        manuscript = Manuscript.objects.get(id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            messages.error(request, 'You do not have permission to edit this manuscript.')
            return redirect('writer:index')
            
    except Manuscript.DoesNotExist:
        messages.error(request, 'Manuscript not found.')
        return redirect('writer:index')
    
    # Get or create sections
    sections = {}
    section_types = ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion']
    
    for section_type in section_types:
        section, created = ManuscriptSection.objects.get_or_create(
            manuscript=manuscript,
            section_type=section_type,
            defaults={
                'title': section_type.title(),
                'content': '',
                'order': section_types.index(section_type)
            }
        )
        sections[section_type] = section
    
    # Get active collaborative sessions
    active_sessions = CollaborativeSession.objects.filter(
        manuscript=manuscript,
        is_active=True,
        last_activity__gte=timezone.now() - timedelta(minutes=5)
    ).select_related('user')
    
    # Get recent document changes for version tracking
    recent_changes = DocumentChange.objects.filter(
        manuscript=manuscript
    ).order_by('-created_at')[:10]
    
    context = {
        'manuscript': manuscript,
        'sections': sections,
        'active_sessions': active_sessions,
        'recent_changes': recent_changes,
        'can_edit': True,
        'is_collaborative': True,
    }
    
    return render(request, 'writer_app/collaborative_editor.html', context)


# Version Control API Views

@login_required
@require_http_methods(["GET"])
def version_history(request, manuscript_id):
    """Get version history for a manuscript."""
    try:
        manuscript = Manuscript.objects.get(id=manuscript_id)
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except Manuscript.DoesNotExist:
        return JsonResponse({'error': 'Manuscript not found'}, status=404)
    
    branch_name = request.GET.get('branch', 'main')
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 20))
    
    # Get versions for the specified branch
    versions = manuscript.versions.filter(branch_name=branch_name)
    
    # Paginate results
    paginator = Paginator(versions, per_page)
    versions_page = paginator.get_page(page)
    
    versions_data = []
    for version in versions_page:
        versions_data.append({
            'id': str(version.id),
            'version_number': version.version_number,
            'version_tag': version.version_tag,
            'branch_name': version.branch_name,
            'created_by': {
                'id': version.created_by.id,
                'username': version.created_by.username,
                'full_name': version.created_by.get_full_name()
            },
            'created_at': version.created_at.isoformat(),
            'commit_message': version.commit_message,
            'is_major_version': version.is_major_version,
            'is_published': version.is_published,
            'stats': {
                'total_changes': version.total_changes,
                'word_count_delta': version.word_count_delta,
                'lines_added': version.lines_added,
                'lines_removed': version.lines_removed
            }
        })
    
    return JsonResponse({
        'success': True,
        'versions': versions_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'total_versions': paginator.count,
            'has_next': versions_page.has_next(),
            'has_previous': versions_page.has_previous()
        }
    })


@login_required
@require_http_methods(["POST"])
def create_version(request, manuscript_id):
    """Create a new version of the manuscript."""
    try:
        manuscript = Manuscript.objects.get(id=manuscript_id)
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except Manuscript.DoesNotExist:
        return JsonResponse({'error': 'Manuscript not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        commit_message = data.get('commit_message', '')
        version_tag = data.get('version_tag', '')
        branch_name = data.get('branch_name', 'main')
        is_major = data.get('is_major', False)
        
        version_manager = VersionControlManager()
        version = version_manager.create_version(
            manuscript=manuscript,
            user=request.user,
            commit_message=commit_message,
            version_tag=version_tag,
            branch_name=branch_name,
            is_major=is_major
        )
        
        return JsonResponse({
            'success': True,
            'version': {
                'id': str(version.id),
                'version_number': version.version_number,
                'version_tag': version.version_tag,
                'branch_name': version.branch_name,
                'commit_message': version.commit_message,
                'created_at': version.created_at.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def view_diff(request, manuscript_id, from_version_id, to_version_id):
    """Generate and view diff between two versions."""
    try:
        manuscript = Manuscript.objects.get(id=manuscript_id)
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except Manuscript.DoesNotExist:
        return JsonResponse({'error': 'Manuscript not found'}, status=404)
    
    try:
        from_version = ManuscriptVersion.objects.get(id=from_version_id, manuscript=manuscript)
        to_version = ManuscriptVersion.objects.get(id=to_version_id, manuscript=manuscript)
    except ManuscriptVersion.DoesNotExist:
        return JsonResponse({'error': 'Version not found'}, status=404)
    
    diff_type = request.GET.get('type', 'unified')
    
    try:
        version_manager = VersionControlManager()
        diff_result = version_manager.generate_diff(from_version, to_version, diff_type)
        
        return JsonResponse({
            'success': True,
            'diff': {
                'id': str(diff_result.id),
                'type': diff_result.diff_type,
                'data': diff_result.diff_data,
                'html': diff_result.diff_html,
                'stats': diff_result.diff_stats,
                'from_version': {
                    'id': str(from_version.id),
                    'version_number': from_version.version_number,
                    'created_at': from_version.created_at.isoformat()
                },
                'to_version': {
                    'id': str(to_version.id),
                    'version_number': to_version.version_number,
                    'created_at': to_version.created_at.isoformat()
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def branch_list(request, manuscript_id):
    """Get list of branches for a manuscript."""
    try:
        manuscript = Manuscript.objects.get(id=manuscript_id)
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except Manuscript.DoesNotExist:
        return JsonResponse({'error': 'Manuscript not found'}, status=404)
    
    branches = manuscript.branches.filter(is_active=True)
    
    branches_data = []
    for branch in branches:
        latest_version = branch.get_latest_version()
        ahead_behind = branch.get_commits_ahead_behind()
        
        branches_data.append({
            'id': str(branch.id),
            'name': branch.name,
            'description': branch.description,
            'created_by': {
                'id': branch.created_by.id,
                'username': branch.created_by.username
            },
            'created_at': branch.created_at.isoformat(),
            'last_updated': branch.last_updated.isoformat(),
            'is_merged': branch.is_merged,
            'total_commits': branch.total_commits,
            'latest_version': {
                'version_number': latest_version.version_number if latest_version else None,
                'created_at': latest_version.created_at.isoformat() if latest_version else None
            } if latest_version else None,
            'commits_ahead': ahead_behind['ahead'],
            'commits_behind': ahead_behind['behind']
        })
    
    return JsonResponse({
        'success': True,
        'branches': branches_data
    })


@login_required
@require_http_methods(["POST"])
def create_branch(request, manuscript_id):
    """Create a new branch for the manuscript."""
    try:
        manuscript = Manuscript.objects.get(id=manuscript_id)
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except Manuscript.DoesNotExist:
        return JsonResponse({'error': 'Manuscript not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        branch_name = data.get('name', '').strip()
        description = data.get('description', '')
        base_version_id = data.get('base_version_id')
        
        if not branch_name:
            return JsonResponse({'error': 'Branch name is required'}, status=400)
        
        # Check if branch name already exists
        if manuscript.branches.filter(name=branch_name).exists():
            return JsonResponse({'error': 'Branch name already exists'}, status=400)
        
        base_version = None
        if base_version_id:
            try:
                base_version = ManuscriptVersion.objects.get(id=base_version_id, manuscript=manuscript)
            except ManuscriptVersion.DoesNotExist:
                return JsonResponse({'error': 'Base version not found'}, status=404)
        
        version_manager = VersionControlManager()
        branch = version_manager.create_branch(
            manuscript=manuscript,
            branch_name=branch_name,
            description=description,
            user=request.user,
            base_version=base_version
        )
        
        return JsonResponse({
            'success': True,
            'branch': {
                'id': str(branch.id),
                'name': branch.name,
                'description': branch.description,
                'created_at': branch.created_at.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def rollback_version(request, manuscript_id, version_id):
    """Rollback manuscript to a specific version."""
    try:
        manuscript = Manuscript.objects.get(id=manuscript_id)
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except Manuscript.DoesNotExist:
        return JsonResponse({'error': 'Manuscript not found'}, status=404)
    
    try:
        target_version = ManuscriptVersion.objects.get(id=version_id, manuscript=manuscript)
    except ManuscriptVersion.DoesNotExist:
        return JsonResponse({'error': 'Version not found'}, status=404)
    
    try:
        version_manager = VersionControlManager()
        rollback_version = version_manager.rollback_to_version(
            manuscript=manuscript,
            target_version=target_version,
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'rollback_version': {
                'id': str(rollback_version.id),
                'version_number': rollback_version.version_number,
                'created_at': rollback_version.created_at.isoformat(),
                'target_version': target_version.version_number
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def create_merge_request(request, manuscript_id):
    """Create a merge request between branches."""
    try:
        manuscript = Manuscript.objects.get(id=manuscript_id)
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except Manuscript.DoesNotExist:
        return JsonResponse({'error': 'Manuscript not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        description = data.get('description', '')
        source_branch_id = data.get('source_branch_id')
        target_branch_id = data.get('target_branch_id')
        
        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)
        
        try:
            source_branch = ManuscriptBranch.objects.get(id=source_branch_id, manuscript=manuscript)
            target_branch = ManuscriptBranch.objects.get(id=target_branch_id, manuscript=manuscript)
        except ManuscriptBranch.DoesNotExist:
            return JsonResponse({'error': 'Branch not found'}, status=404)
        
        version_manager = VersionControlManager()
        merge_request = version_manager.create_merge_request(
            source_branch=source_branch,
            target_branch=target_branch,
            title=title,
            description=description,
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'merge_request': {
                'id': str(merge_request.id),
                'title': merge_request.title,
                'description': merge_request.description,
                'status': merge_request.status,
                'has_conflicts': merge_request.has_conflicts,
                'auto_mergeable': merge_request.auto_mergeable,
                'created_at': merge_request.created_at.isoformat(),
                'source_branch': merge_request.source_branch.name,
                'target_branch': merge_request.target_branch.name
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def version_control_dashboard(request, manuscript_id):
    """Version control dashboard for manuscript management."""
    try:
        manuscript = Manuscript.objects.get(id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            messages.error(request, 'You do not have permission to manage this manuscript.')
            return redirect('writer:index')
            
    except Manuscript.DoesNotExist:
        messages.error(request, 'Manuscript not found.')
        return redirect('writer:index')
    
    # Get recent versions
    recent_versions = manuscript.versions.all()[:10]
    
    # Get active branches
    branches = manuscript.branches.filter(is_active=True)
    
    # Get open merge requests
    merge_requests = manuscript.merge_requests.exclude(status__in=['merged', 'closed'])
    
    context = {
        'manuscript': manuscript,
        'recent_versions': recent_versions,
        'branches': branches,
        'merge_requests': merge_requests,
        'can_edit': True,
    }
    
    return render(request, 'writer_app/version_control_dashboard.html', context)


# Version Control API Views
@login_required
@require_http_methods(["POST"])
def create_version(request, manuscript_id):
    """Create a new version of the manuscript."""
    try:
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        data = json.loads(request.body)
        commit_message = data.get('commit_message', '')
        version_tag = data.get('version_tag', '')
        branch_name = data.get('branch_name', 'main')
        is_major = data.get('is_major', False)
        
        # Use version control manager
        vc_manager = VersionControlManager()
        version = vc_manager.create_version(
            manuscript=manuscript,
            user=request.user,
            commit_message=commit_message,
            version_tag=version_tag,
            branch_name=branch_name,
            is_major=is_major
        )
        
        return JsonResponse({
            'success': True,
            'version': {
                'id': str(version.id),
                'version_number': version.version_number,
                'version_tag': version.version_tag,
                'branch_name': version.branch_name,
                'commit_message': version.commit_message,
                'created_at': version.created_at.isoformat(),
                'created_by': version.created_by.username,
                'total_changes': version.total_changes,
                'word_count_delta': version.word_count_delta
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def version_history(request, manuscript_id):
    """Get version history for a manuscript."""
    try:
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        branch_name = request.GET.get('branch', 'main')
        limit = int(request.GET.get('limit', 20))
        
        versions = manuscript.versions.filter(branch_name=branch_name).order_by('-created_at')[:limit]
        
        version_data = []
        for version in versions:
            version_data.append({
                'id': str(version.id),
                'version_number': version.version_number,
                'version_tag': version.version_tag,
                'branch_name': version.branch_name,
                'commit_message': version.commit_message,
                'created_at': version.created_at.isoformat(),
                'created_by': version.created_by.username,
                'total_changes': version.total_changes,
                'word_count_delta': version.word_count_delta,
                'lines_added': version.lines_added,
                'lines_removed': version.lines_removed,
                'is_major_version': version.is_major_version
            })
        
        return JsonResponse({
            'success': True,
            'versions': version_data,
            'branch': branch_name,
            'total_count': manuscript.versions.filter(branch_name=branch_name).count()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def view_diff(request, manuscript_id, from_version_id, to_version_id):
    """View diff between two versions."""
    try:
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        from_version = get_object_or_404(ManuscriptVersion, id=from_version_id, manuscript=manuscript)
        to_version = get_object_or_404(ManuscriptVersion, id=to_version_id, manuscript=manuscript)
        
        diff_type = request.GET.get('type', 'unified')
        
        # Use version control manager
        vc_manager = VersionControlManager()
        diff_result = vc_manager.generate_diff(from_version, to_version, diff_type)
        
        return JsonResponse({
            'success': True,
            'diff': {
                'type': diff_result.diff_type,
                'html': diff_result.diff_html,
                'data': diff_result.diff_data,
                'stats': diff_result.diff_stats
            },
            'from_version': {
                'id': str(from_version.id),
                'version_number': from_version.version_number,
                'created_at': from_version.created_at.isoformat()
            },
            'to_version': {
                'id': str(to_version.id),
                'version_number': to_version.version_number,
                'created_at': to_version.created_at.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def rollback_version(request, manuscript_id, version_id):
    """Rollback manuscript to a specific version."""
    try:
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        target_version = get_object_or_404(ManuscriptVersion, id=version_id, manuscript=manuscript)
        
        # Use version control manager
        vc_manager = VersionControlManager()
        rollback_version = vc_manager.rollback_to_version(manuscript, target_version, request.user)
        
        return JsonResponse({
            'success': True,
            'rollback_version': {
                'id': str(rollback_version.id),
                'version_number': rollback_version.version_number,
                'created_at': rollback_version.created_at.isoformat()
            },
            'target_version': {
                'id': str(target_version.id),
                'version_number': target_version.version_number
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def branch_list(request, manuscript_id):
    """Get list of branches for a manuscript."""
    try:
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        branches = manuscript.branches.filter(is_active=True).order_by('name')
        
        branch_data = []
        for branch in branches:
            latest_version = branch.get_latest_version()
            branch_data.append({
                'id': str(branch.id),
                'name': branch.name,
                'description': branch.description,
                'created_at': branch.created_at.isoformat(),
                'created_by': branch.created_by.username,
                'is_merged': branch.is_merged,
                'total_commits': branch.get_total_commits(),
                'last_updated': latest_version.created_at.isoformat() if latest_version else None,
                'latest_version': latest_version.version_number if latest_version else None
            })
        
        return JsonResponse({
            'success': True,
            'branches': branch_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def create_branch(request, manuscript_id):
    """Create a new branch for the manuscript."""
    try:
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        data = json.loads(request.body)
        branch_name = data.get('name', '').strip()
        description = data.get('description', '')
        
        if not branch_name:
            return JsonResponse({'error': 'Branch name is required'}, status=400)
        
        # Check if branch name already exists
        if manuscript.branches.filter(name=branch_name).exists():
            return JsonResponse({'error': 'Branch name already exists'}, status=400)
        
        # Use version control manager
        vc_manager = VersionControlManager()
        branch = vc_manager.create_branch(
            manuscript=manuscript,
            branch_name=branch_name,
            description=description,
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'branch': {
                'id': str(branch.id),
                'name': branch.name,
                'description': branch.description,
                'created_at': branch.created_at.isoformat(),
                'created_by': branch.created_by.username
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def create_merge_request(request, manuscript_id):
    """Create a merge request between branches."""
    try:
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        description = data.get('description', '')
        source_branch_id = data.get('source_branch_id')
        target_branch_id = data.get('target_branch_id', 'main')
        
        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)
        
        source_branch = get_object_or_404(ManuscriptBranch, id=source_branch_id, manuscript=manuscript)
        
        # Handle target branch (could be ID or name)
        if target_branch_id == 'main':
            target_branch = manuscript.branches.filter(name='main').first()
        else:
            target_branch = get_object_or_404(ManuscriptBranch, id=target_branch_id, manuscript=manuscript)
        
        if not target_branch:
            return JsonResponse({'error': 'Target branch not found'}, status=404)
        
        # Use version control manager
        vc_manager = VersionControlManager()
        merge_request = vc_manager.create_merge_request(
            source_branch=source_branch,
            target_branch=target_branch,
            title=title,
            description=description,
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'merge_request': {
                'id': str(merge_request.id),
                'title': merge_request.title,
                'description': merge_request.description,
                'status': merge_request.status,
                'source_branch': merge_request.source_branch.name,
                'target_branch': merge_request.target_branch.name,
                'has_conflicts': merge_request.has_conflicts,
                'auto_mergeable': merge_request.auto_mergeable,
                'created_at': merge_request.created_at.isoformat(),
                'created_by': merge_request.created_by.username
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Collaborative Editing Views
@login_required
def collaborative_editor(request, manuscript_id):
    """Collaborative manuscript editor with real-time features."""
    try:
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            messages.error(request, 'You do not have permission to edit this manuscript.')
            return redirect('writer:index')
        
        context = {
            'manuscript': manuscript,
            'can_edit': True,
            'user_can_create_versions': manuscript.owner == request.user
        }
        
        return render(request, 'writer_app/collaborative_editor.html', context)
        
    except Manuscript.DoesNotExist:
        messages.error(request, 'Manuscript not found.')
        return redirect('writer:index')


@login_required
@require_http_methods(["GET"])
def collaborative_sessions(request, manuscript_id):
    """Get active collaborative sessions for a manuscript."""
    try:
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Get active sessions (last 5 minutes)
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(minutes=5)
        active_sessions = manuscript.collaborative_sessions.filter(
            last_activity__gte=cutoff_time,
            is_active=True
        ).select_related('user')
        
        session_data = []
        for session in active_sessions:
            session_data.append({
                'id': str(session.id),
                'user': {
                    'id': session.user.id,
                    'username': session.user.username,
                    'full_name': session.user.get_full_name()
                },
                'started_at': session.started_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'current_section': session.current_section,
                'is_editing': session.is_editing
            })
        
        return JsonResponse({
            'success': True,
            'active_sessions': session_data,
            'total_users': len(session_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def join_collaboration(request, manuscript_id):
    """Join a collaborative editing session."""
    try:
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Check permissions
        if manuscript.owner != request.user and request.user not in manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Create or update collaborative session
        session, created = CollaborativeSession.objects.get_or_create(
            manuscript=manuscript,
            user=request.user,
            defaults={
                'is_active': True,
                'current_section': None,
                'is_editing': False
            }
        )
        
        if not created:
            session.is_active = True
            session.last_activity = timezone.now()
            session.save()
        
        return JsonResponse({
            'success': True,
            'session_id': str(session.id),
            'message': 'Joined collaborative session'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def leave_collaboration(request, manuscript_id):
    """Leave a collaborative editing session."""
    try:
        manuscript = get_object_or_404(Manuscript, id=manuscript_id)
        
        # Find and deactivate session
        try:
            session = CollaborativeSession.objects.get(
                manuscript=manuscript,
                user=request.user,
                is_active=True
            )
            session.is_active = False
            session.ended_at = timezone.now()
            session.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Left collaborative session'
            })
            
        except CollaborativeSession.DoesNotExist:
            return JsonResponse({
                'success': True,
                'message': 'No active session found'
            })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def lock_section(request, section_id):
    """Lock a section for editing."""
    try:
        section = get_object_or_404(ManuscriptSection, id=section_id)
        
        # Check permissions
        if section.manuscript.owner != request.user and request.user not in section.manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Check if section is already locked
        if section.locked_by and section.locked_by != request.user:
            return JsonResponse({
                'error': f'Section is locked by {section.locked_by.username}',
                'locked_by': section.locked_by.username
            }, status=409)
        
        # Lock the section
        section.locked_by = request.user
        section.locked_at = timezone.now()
        section.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Section locked for editing',
            'locked_by': request.user.username
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def unlock_section(request, section_id):
    """Unlock a section."""
    try:
        section = get_object_or_404(ManuscriptSection, id=section_id)
        
        # Check permissions
        if section.manuscript.owner != request.user and request.user not in section.manuscript.collaborators.all():
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Only allow unlocking if user locked it or is the owner
        if section.locked_by and section.locked_by != request.user and section.manuscript.owner != request.user:
            return JsonResponse({'error': 'Cannot unlock section locked by another user'}, status=403)
        
        # Unlock the section
        section.locked_by = None
        section.locked_at = None
        section.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Section unlocked'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
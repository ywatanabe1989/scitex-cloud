from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from ..models import CodeExecutionJob, DataAnalysisJob, Notebook, ResourceUsage
# from apps.api  # Removed - api app not installed.utils import execute_code_safely, generate_analysis_code
import json
import threading
from . import workspace_views as default_workspace_views
from . import project_views

# Expose default workspace views
guest_session_view = default_workspace_views.guest_session_view
user_default_workspace = default_workspace_views.user_default_workspace

# Expose project views
project_code = project_views.project_code


@login_required
def index(request):
    """Code app - redirect to user's projects."""
    messages.info(request, 'Please select or create a project to use Code.')
    return redirect('user_projects:user_projects', username=request.user.username)


def features(request):
    """Code features view."""
    return render(request, 'code_app/features.html')


def pricing(request):
    """Code pricing view."""
    return render(request, 'code_app/pricing.html')


@login_required
def editor(request):
    """SciTeX Code editor interface."""
    # Get user's recent jobs for sidebar
    recent_jobs = CodeExecutionJob.objects.filter(user=request.user)[:5]
    
    context = {
        'recent_jobs': recent_jobs,
        'user_notebooks': Notebook.objects.filter(user=request.user)[:5]
    }
    return render(request, 'code_app/editor.html', context)


@login_required
def jobs(request):
    """List user's code execution jobs."""
    jobs_list = CodeExecutionJob.objects.filter(user=request.user).select_related('user').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        jobs_list = jobs_list.filter(status=status_filter)
    
    # Paginate results
    paginator = Paginator(jobs_list, 20)
    page = request.GET.get('page', 1)
    jobs = paginator.get_page(page)
    
    context = {
        'jobs': jobs,
        'status_filter': status_filter,
        'status_choices': CodeExecutionJob.JOB_STATUS
    }
    return render(request, 'code_app/jobs.html', context)


@login_required
def job_detail(request, job_id):
    """View details of a specific job."""
    job = get_object_or_404(CodeExecutionJob, job_id=job_id, user=request.user)
    
    context = {
        'job': job,
        'output_files': job.output_files,
        'plot_files': job.plot_files
    }
    return render(request, 'code_app/job_detail.html', context)


@login_required
@require_http_methods(["POST"])
def execute_code(request):
    """Execute code via web interface."""
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip()
        execution_type = data.get('type', 'script')
        timeout = min(int(data.get('timeout', 300)), 600)
        max_memory = min(int(data.get('max_memory', 512)), 2048)
        
        if not code:
            return JsonResponse({'error': 'Code is required'}, status=400)
        
        # Create execution job
        job = CodeExecutionJob.objects.create(
            user=request.user,
            execution_type=execution_type,
            source_code=code,
            timeout_seconds=timeout,
            max_memory_mb=max_memory
        )
        
        # Start execution in background
        def run_execution():
            execute_code_safely(job)
        
        execution_thread = threading.Thread(target=run_execution)
        execution_thread.daemon = True
        execution_thread.start()
        
        return JsonResponse({
            'success': True,
            'job_id': str(job.job_id),
            'status': job.status,
            'message': 'Code execution started'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def job_status(request, job_id):
    """Get job status via AJAX."""
    try:
        job = CodeExecutionJob.objects.get(job_id=job_id, user=request.user)
        
        response_data = {
            'job_id': str(job.job_id),
            'status': job.status,
            'progress': get_job_progress(job.status),
            'message': f'Job {job.status}',
            'execution_time': job.execution_time,
            'cpu_time': job.cpu_time,
            'memory_peak': job.memory_peak,
            'created_at': job.created_at.isoformat(),
            'output': job.output,
            'error_output': job.error_output,
            'output_files': job.output_files,
            'plot_files': job.plot_files
        }
        
        return JsonResponse(response_data)
        
    except CodeExecutionJob.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)


@login_required
def notebooks(request):
    """List user's notebooks."""
    notebooks_list = Notebook.objects.filter(user=request.user).prefetch_related('shared_with').order_by('-updated_at')
    
    # Paginate results
    paginator = Paginator(notebooks_list, 20)
    page = request.GET.get('page', 1)
    notebooks = paginator.get_page(page)
    
    context = {
        'notebooks': notebooks
    }
    return render(request, 'code_app/notebooks.html', context)


@login_required
def notebook_detail(request, notebook_id):
    """View/edit a specific notebook."""
    notebook = get_object_or_404(Notebook, notebook_id=notebook_id, user=request.user)
    
    context = {
        'notebook': notebook
    }
    return render(request, 'code_app/notebook_detail.html', context)


@login_required
def analysis(request):
    """Data analysis interface."""
    analysis_jobs = DataAnalysisJob.objects.filter(user=request.user)[:10]
    
    context = {
        'analysis_jobs': analysis_jobs,
        'analysis_types': DataAnalysisJob.ANALYSIS_TYPES
    }
    return render(request, 'code_app/analysis.html', context)


def templates(request):
    """SCITEX framework templates page."""
    return render(request, 'code_app/templates.html')


@login_required
@require_http_methods(["POST"])
def run_analysis(request):
    """Run data analysis via web interface."""
    try:
        analysis_type = request.POST.get('type', 'custom')
        input_data = request.POST.get('data_path', '')
        parameters = json.loads(request.POST.get('parameters', '{}'))
        
        # Create analysis job
        analysis_job = DataAnalysisJob.objects.create(
            user=request.user,
            analysis_type=analysis_type,
            input_data_path=input_data,
            parameters=parameters
        )
        
        # Generate analysis code
        analysis_code = generate_analysis_code(analysis_type, input_data, parameters)
        
        # Create code execution job
        code_job = CodeExecutionJob.objects.create(
            user=request.user,
            execution_type='analysis',
            source_code=analysis_code,
            timeout_seconds=600,
            max_memory_mb=1024
        )
        
        analysis_job.code_job = code_job
        analysis_job.save()
        
        # Start execution
        def run_analysis_execution():
            execute_code_safely(code_job)
        
        analysis_thread = threading.Thread(target=run_analysis_execution)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        messages.success(request, f'Analysis "{analysis_type}" started successfully!')
        return redirect('code:job_detail', job_id=code_job.job_id)
        
    except Exception as e:
        messages.error(request, f'Error starting analysis: {str(e)}')
        return redirect('code:analysis')


def get_job_progress(status):
    """Calculate job progress percentage."""
    progress_map = {
        'queued': 10,
        'running': 50,
        'completed': 100,
        'failed': 0,
        'timeout': 0,
        'cancelled': 0
    }
    return progress_map.get(status, 0)


# Environment Management Views
@login_required
def environments(request):
    """List user's execution environments."""
    from ..services.environment_manager import EnvironmentManager
    
    env_manager = EnvironmentManager(request.user)
    environments = env_manager.list_environments()
    
    context = {
        'environments': environments,
        'total_environments': len(environments)
    }
    return render(request, 'code_app/environments.html', context)


@login_required
@require_http_methods(["POST"])
def create_environment(request):
    """Create a new execution environment."""
    try:
        from ..services.environment_manager import EnvironmentManager
        
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        requirements = data.get('requirements', [])
        
        if not name:
            return JsonResponse({'error': 'Environment name is required'}, status=400)
        
        env_manager = EnvironmentManager(request.user)
        environment = env_manager.create_environment(name, requirements)
        
        return JsonResponse({
            'success': True,
            'environment': {
                'id': environment.env_id,
                'name': environment.name,
                'requirements': [str(req) for req in environment.requirements],
                'created_at': environment.created_at.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def setup_environment(request, env_id):
    """Set up an environment with packages."""
    try:
        from ..services.environment_manager import EnvironmentManager
        
        env_manager = EnvironmentManager(request.user)
        success, message = env_manager.setup_environment(env_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': message
            })
        else:
            return JsonResponse({
                'success': False,
                'error': message
            }, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def environment_detail(request, env_id):
    """View environment details."""
    from ..services.environment_manager import EnvironmentManager
    
    env_manager = EnvironmentManager(request.user)
    env_info = env_manager.get_environment_info(env_id)
    
    if not env_info:
        messages.error(request, 'Environment not found.')
        return redirect('code:environments')
    
    context = {
        'environment': env_info
    }
    return render(request, 'code_app/environment_detail.html', context)


@login_required
@require_http_methods(["POST"])
def execute_in_environment(request, env_id):
    """Execute code in a specific environment."""
    try:
        from ..services.environment_manager import EnvironmentManager
        
        data = json.loads(request.body)
        code = data.get('code', '').strip()
        timeout = min(int(data.get('timeout', 300)), 600)
        
        if not code:
            return JsonResponse({'error': 'Code is required'}, status=400)
        
        env_manager = EnvironmentManager(request.user)
        success, result = env_manager.execute_in_environment(env_id, code, timeout)
        
        if success:
            # Create execution job record
            job = CodeExecutionJob.objects.create(
                user=request.user,
                execution_type='script',
                source_code=code,
                status='completed',
                output=result.get('stdout', ''),
                error_output=result.get('stderr', ''),
                return_code=result.get('return_code', 0),
                execution_time=result.get('execution_time', 0),
                timeout_seconds=timeout
            )
            
            return JsonResponse({
                'success': True,
                'job_id': str(job.job_id),
                'result': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Workflow Management Views
@login_required
def workflows(request):
    """List user's research workflows."""
    from ..services.environment_manager import WorkflowManager
    import os
    from pathlib import Path
    
    workflows_dir = Path(settings.MEDIA_ROOT) / 'workflows' / str(request.user.id)
    
    workflows = []
    if workflows_dir.exists():
        for workflow_file in workflows_dir.glob('*.json'):
            try:
                with open(workflow_file) as f:
                    workflow_data = json.load(f)
                    workflows.append(workflow_data)
            except Exception as e:
                continue
    
    # Sort by creation date
    workflows.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    context = {
        'workflows': workflows
    }
    return render(request, 'code_app/workflows.html', context)


@login_required
@require_http_methods(["POST"])
def create_workflow(request):
    """Create a new research workflow."""
    try:
        from ..services.environment_manager import WorkflowManager
        
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        description = data.get('description', '')
        steps = data.get('steps', [])
        
        if not name:
            return JsonResponse({'error': 'Workflow name is required'}, status=400)
        
        if not steps:
            return JsonResponse({'error': 'At least one step is required'}, status=400)
        
        workflow_manager = WorkflowManager(request.user)
        workflow = workflow_manager.create_workflow(name, description, steps)
        
        return JsonResponse({
            'success': True,
            'workflow': workflow
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def execute_workflow(request, workflow_id):
    """Execute a research workflow."""
    try:
        from ..services.environment_manager import WorkflowManager
        
        workflow_manager = WorkflowManager(request.user)
        success, results = workflow_manager.execute_workflow(workflow_id)
        
        return JsonResponse({
            'success': success,
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def workflow_detail(request, workflow_id):
    """View workflow details."""
    from pathlib import Path
    
    workflows_dir = Path(settings.MEDIA_ROOT) / 'workflows' / str(request.user.id)
    workflow_file = workflows_dir / f"{workflow_id}.json"
    
    if not workflow_file.exists():
        messages.error(request, 'Workflow not found.')
        return redirect('code:workflows')
    
    try:
        with open(workflow_file) as f:
            workflow = json.load(f)
    except Exception as e:
        messages.error(request, f'Error loading workflow: {e}')
        return redirect('code:workflows')
    
    context = {
        'workflow': workflow
    }
    return render(request, 'code_app/workflow_detail.html', context)


# Notebook Enhanced Views with Environment Support
@login_required
@require_http_methods(["POST"])
def create_notebook(request):
    """Create a new notebook."""
    try:
        from ..services.jupyter_service import NotebookManager, NotebookTemplates
        
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        description = data.get('description', '')
        template_type = data.get('template', 'basic')
        
        if not title:
            return JsonResponse({'error': 'Notebook title is required'}, status=400)
        
        notebook_manager = NotebookManager(request.user)
        
        if template_type == 'data_analysis':
            content = NotebookTemplates.get_data_analysis_template()
        elif template_type == 'machine_learning':
            content = NotebookTemplates.get_machine_learning_template()
        elif template_type == 'visualization':
            content = NotebookTemplates.get_visualization_template()
        else:
            # Create basic notebook
            notebook = notebook_manager.create_notebook(title, description)
            return JsonResponse({
                'success': True,
                'notebook_id': str(notebook.notebook_id),
                'redirect_url': f'/code/notebooks/{notebook.notebook_id}/'
            })
        
        # Create notebook with template
        from ..models import Notebook
        notebook = Notebook.objects.create(
            user=request.user,
            title=title,
            description=description,
            content=content,
            status='draft'
        )
        
        return JsonResponse({
            'success': True,
            'notebook_id': str(notebook.notebook_id),
            'redirect_url': f'/code/notebooks/{notebook.notebook_id}/'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def execute_notebook(request, notebook_id):
    """Execute a Jupyter notebook."""
    try:
        from ..services.jupyter_service import NotebookManager, NotebookExecutor
        
        notebook = get_object_or_404(Notebook, notebook_id=notebook_id, user=request.user)
        
        # Create execution job
        job = CodeExecutionJob.objects.create(
            user=request.user,
            execution_type='notebook',
            source_code=json.dumps(notebook.content),
            timeout_seconds=600,
            max_memory_mb=1024
        )
        
        # Execute notebook in background
        def run_notebook_execution():
            executor = NotebookExecutor(timeout=600)
            success, result = executor.execute_notebook(notebook, job)
            
            if success:
                job.status = 'completed'
                job.output = json.dumps(result, indent=2)
            else:
                job.status = 'failed'
                job.error_output = result.get('error', 'Unknown error')
            
            job.completed_at = timezone.now()
            job.save()
        
        execution_thread = threading.Thread(target=run_notebook_execution)
        execution_thread.daemon = True
        execution_thread.start()
        
        return JsonResponse({
            'success': True,
            'job_id': str(job.job_id),
            'message': 'Notebook execution started'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Data Visualization Pipeline Views
@login_required
def visualizations(request):
    """List user's generated visualizations."""
    from pathlib import Path
    
    viz_dir = Path(settings.MEDIA_ROOT) / 'visualizations' / str(request.user.id)
    visualizations = []
    
    if viz_dir.exists():
        for viz_file in viz_dir.glob('*.png'):
            try:
                stat = viz_file.stat()
                visualizations.append({
                    'filename': viz_file.name,
                    'size': stat.st_size,
                    'created': timezone.datetime.fromtimestamp(stat.st_ctime),
                    'path': f'visualizations/{request.user.id}/{viz_file.name}'
                })
            except Exception:
                continue
    
    # Sort by creation time
    visualizations.sort(key=lambda x: x['created'], reverse=True)
    
    context = {
        'visualizations': visualizations
    }
    return render(request, 'code_app/visualizations.html', context)


@login_required
@require_http_methods(["POST"])
def generate_visualization(request):
    """Generate a visualization from data."""
    try:
        from ..services.visualization_pipeline import VisualizationGenerator
        
        data = json.loads(request.body)
        plot_type = data.get('type', 'line')
        plot_data = data.get('data', {})
        options = data.get('options', {})
        
        generator = VisualizationGenerator(request.user)
        success, result = generator.generate_plot(plot_type, plot_data, options)
        
        if success:
            # Create a job record for tracking
            job = CodeExecutionJob.objects.create(
                user=request.user,
                execution_type='visualization',
                source_code=f"# Generated {plot_type} plot\n# Data points: {result.get('data_points', 'N/A')}",
                status='completed',
                output=json.dumps(result, indent=2)
            )
            
            return JsonResponse({
                'success': True,
                'job_id': str(job.job_id),
                'result': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def process_data_visualization(request):
    """Process data file and generate multiple visualizations."""
    try:
        from ..services.visualization_pipeline import VisualizationPipeline
        
        data = json.loads(request.body)
        data_source = data.get('data_source', '')
        visualization_specs = data.get('visualizations', [])
        
        if not data_source:
            return JsonResponse({'error': 'Data source is required'}, status=400)
        
        if not visualization_specs:
            return JsonResponse({'error': 'At least one visualization specification is required'}, status=400)
        
        pipeline = VisualizationPipeline(request.user)
        result = pipeline.process_data_and_visualize(data_source, visualization_specs)
        
        if result.get('success'):
            # Create job record
            job = CodeExecutionJob.objects.create(
                user=request.user,
                execution_type='analysis',
                source_code=f"# Data visualization pipeline\n# Data shape: {result.get('data_shape', 'N/A')}\n# Visualizations: {len(visualization_specs)}",
                status='completed',
                output=json.dumps(result, indent=2)
            )
            
            return JsonResponse({
                'success': True,
                'job_id': str(job.job_id),
                'result': result
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def create_research_report(request):
    """Create a research report with visualizations."""
    try:
        from ..services.visualization_pipeline import VisualizationPipeline
        
        data = json.loads(request.body)
        title = data.get('title', 'Research Report')
        sections = data.get('sections', [])
        
        if not sections:
            return JsonResponse({'error': 'At least one section is required'}, status=400)
        
        pipeline = VisualizationPipeline(request.user)
        report_path = pipeline.create_research_report(title, sections)
        
        return JsonResponse({
            'success': True,
            'report_path': report_path,
            'message': 'Research report created successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
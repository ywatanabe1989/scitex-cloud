from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import CodeExecutionJob, DataAnalysisJob, Notebook, ResourceUsage
from apps.api.utils import execute_code_safely, generate_analysis_code
import json
import threading


def index(request):
    """Code app index view."""
    return render(request, 'code_app/index.html')


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
    jobs_list = CodeExecutionJob.objects.filter(user=request.user).order_by('-created_at')
    
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
    notebooks_list = Notebook.objects.filter(user=request.user).order_by('-updated_at')
    
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
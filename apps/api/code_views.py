from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.paginator import Paginator
from apps.code_app.models import CodeExecutionJob, DataAnalysisJob, Notebook, ResourceUsage
from .utils import execute_code_safely, generate_analysis_code
import threading

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_code(request):
    """Execute Python code using MNGS utilities with security sandbox."""
    code = request.data.get('code', '')
    execution_type = request.data.get('type', 'script')
    timeout = min(int(request.data.get('timeout', 300)), 600)  # Max 10 minutes
    max_memory = min(int(request.data.get('max_memory', 512)), 2048)  # Max 2GB
    
    if not code.strip():
        return Response({
            'error': 'Code is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create execution job
    job = CodeExecutionJob.objects.create(
        user=request.user,
        execution_type=execution_type,
        source_code=code,
        timeout_seconds=timeout,
        max_memory_mb=max_memory
    )
    
    # Start execution in background thread
    def run_execution():
        execute_code_safely(job)
    
    execution_thread = threading.Thread(target=run_execution)
    execution_thread.daemon = True
    execution_thread.start()
    
    return Response({
        'job_id': str(job.job_id),
        'status': job.status,
        'message': 'Code execution started',
        'timeout': timeout,
        'max_memory_mb': max_memory
    }, status=status.HTTP_202_ACCEPTED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_data(request):
    """Analyze data using MNGS tools."""
    analysis_type = request.data.get('type', 'custom')
    input_data = request.data.get('data_path', '')
    parameters = request.data.get('parameters', {})
    
    # Create analysis job
    analysis_job = DataAnalysisJob.objects.create(
        user=request.user,
        analysis_type=analysis_type,
        input_data_path=input_data,
        parameters=parameters
    )
    
    # Create corresponding code execution job
    analysis_code = generate_analysis_code(analysis_type, input_data, parameters)
    
    code_job = CodeExecutionJob.objects.create(
        user=request.user,
        execution_type='analysis',
        source_code=analysis_code,
        timeout_seconds=600,  # 10 minutes for analysis
        max_memory_mb=1024   # 1GB for data analysis
    )
    
    analysis_job.code_job = code_job
    analysis_job.save()
    
    # Start execution
    def run_analysis():
        execute_code_safely(code_job)
        # Update analysis job when completed
        if code_job.status == 'completed':
            analysis_job.completed_at = timezone.now()
            analysis_job.results = {'output': code_job.output}
            analysis_job.save()
    
    analysis_thread = threading.Thread(target=run_analysis)
    analysis_thread.daemon = True
    analysis_thread.start()
    
    return Response({
        'analysis_id': str(analysis_job.analysis_id),
        'job_id': str(code_job.job_id),
        'status': 'processing',
        'message': 'Data analysis started',
        'analysis_type': analysis_type
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_jobs(request):
    """List user's code execution jobs."""
    page = int(request.GET.get('page', 1))
    page_size = min(int(request.GET.get('page_size', 20)), 100)
    status_filter = request.GET.get('status')
    job_type = request.GET.get('type')
    
    # Get user's jobs
    jobs = CodeExecutionJob.objects.filter(user=request.user)
    
    # Apply filters
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    if job_type:
        jobs = jobs.filter(execution_type=job_type)
    
    # Paginate
    paginator = Paginator(jobs, page_size)
    page_obj = paginator.get_page(page)
    
    # Serialize job data
    job_data = []
    for job in page_obj:
        job_data.append({
            'job_id': str(job.job_id),
            'status': job.status,
            'execution_type': job.execution_type,
            'created_at': job.created_at.isoformat(),
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'execution_time': job.execution_time,
            'cpu_time': job.cpu_time,
            'memory_peak': job.memory_peak,
            'has_output': bool(job.output),
            'has_plots': len(job.plot_files) > 0,
            'error': job.error_output[:100] if job.error_output else None
        })
    
    return Response({
        'jobs': job_data,
        'total': paginator.count,
        'page': page,
        'pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def job_detail(request, job_id):
    """Get details of a specific job."""
    try:
        job = CodeExecutionJob.objects.get(job_id=job_id, user=request.user)
    except CodeExecutionJob.DoesNotExist:
        return Response({
            'error': 'Job not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Prepare detailed job information
    job_detail = {
        'job_id': str(job.job_id),
        'status': job.status,
        'execution_type': job.execution_type,
        'source_code': job.source_code,
        'output': job.output,
        'error_output': job.error_output,
        'return_code': job.return_code,
        
        # Resource usage
        'cpu_time': job.cpu_time,
        'memory_peak': job.memory_peak,
        'execution_time': job.execution_time,
        
        # Limits
        'timeout_seconds': job.timeout_seconds,
        'max_memory_mb': job.max_memory_mb,
        
        # Files
        'output_files': job.output_files,
        'plot_files': job.plot_files,
        
        # Timestamps
        'created_at': job.created_at.isoformat(),
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
        
        # Duration
        'duration': job.duration
    }
    
    return Response(job_detail)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notebook_list(request):
    """List user's notebooks."""
    page = int(request.GET.get('page', 1))
    page_size = min(int(request.GET.get('page_size', 20)), 100)
    status_filter = request.GET.get('status')
    
    # Get user's notebooks
    notebooks = Notebook.objects.filter(user=request.user)
    
    # Apply status filter
    if status_filter:
        notebooks = notebooks.filter(status=status_filter)
    
    # Paginate
    paginator = Paginator(notebooks, page_size)
    page_obj = paginator.get_page(page)
    
    # Serialize notebook data
    notebook_data = []
    for notebook in page_obj:
        notebook_data.append({
            'notebook_id': str(notebook.notebook_id),
            'title': notebook.title,
            'description': notebook.description,
            'status': notebook.status,
            'is_public': notebook.is_public,
            'execution_count': notebook.execution_count,
            'last_executed': notebook.last_executed.isoformat() if notebook.last_executed else None,
            'created_at': notebook.created_at.isoformat(),
            'updated_at': notebook.updated_at.isoformat(),
            'shared_count': notebook.shared_with.count()
        })
    
    return Response({
        'notebooks': notebook_data,
        'total': paginator.count,
        'page': page,
        'pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous()
    })
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.engine_app.models import (
    EngineConfiguration, EngineSession, EngineRequest
)
from django.utils import timezone
import uuid
import time

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def orchestrate_workflow(request):
    """Orchestrate research workflow using SciTeX-Engine."""
    # Get or create configuration
    config = EngineConfiguration.objects.filter(user=request.user).first()
    if not config:
        config = EngineConfiguration.objects.create(user=request.user)
    
    # Create session
    session = EngineSession.objects.create(
        user=request.user,
        configuration=config,
        status='active'
    )
    
    # TODO: Implement actual orchestration logic
    return Response({
        'job_id': str(session.session_id),
        'status': 'queued',
        'message': 'Workflow orchestration started'
    }, status=status.HTTP_202_ACCEPTED)

@api_view(['GET'])
def job_status(request, job_id):
    """Get status of orchestration job."""
    # TODO: Implement job status tracking
    return Response({
        'job_id': job_id,
        'status': 'running',
        'progress': 50,
        'current_step': 'literature_search'
    })

@api_view(['GET'])
def list_templates(request):
    """List available workflow templates."""
    return Response({
        'templates': [
            {'id': 'basic', 'name': 'Basic Research Workflow'},
            {'id': 'ml', 'name': 'Machine Learning Research'},
            {'id': 'bioinformatics', 'name': 'Bioinformatics Pipeline'},
        ]
    })

@api_view(['GET'])
def emacs_config(request):
    """Get Emacs configuration for SciTeX-Engine."""
    return Response({
        'config': {
            'claude_vterm_mode': True,
            'auto_response': True,
            'keybindings': {}
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def emacs_request(request):
    """Handle requests from Emacs SciTeX-Engine."""
    try:
        data = request.data
        
        # Get or create configuration
        config = EngineConfiguration.objects.filter(user=request.user).first()
        if not config:
            config = EngineConfiguration.objects.create(user=request.user)
        
        # Get or create active session
        session = EngineSession.objects.filter(
            user=request.user,
            status='active'
        ).order_by('-start_time').first()
        
        if not session:
            session = EngineSession.objects.create(
                user=request.user,
                configuration=config,
                status='active'
            )
        
        # Record request
        start_time = time.time()
        
        # Process request based on type
        request_type = data.get('type', 'custom')
        prompt = data.get('prompt', '')
        context = data.get('context', {})
        
        # Here you would integrate with Claude API
        # For now, return a mock response
        response_text = f"This is a mock response for: {prompt[:50]}..."
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Create request record
        engine_request = EngineRequest.objects.create(
            session=session,
            request_type=request_type,
            prompt=prompt,
            context=str(context),
            response=response_text,
            tokens_used=len(prompt.split()) + len(response_text.split()),  # Mock token count
            response_time=response_time,
            buffer_name=context.get('buffer_name', ''),
            file_path=context.get('file_path', ''),
            language_mode=context.get('mode', '')
        )
        
        # Update session metrics
        session.request_count += 1
        session.tokens_used += engine_request.tokens_used
        session.save()
        
        # Update configuration usage
        config.total_requests += 1
        config.total_tokens_used += engine_request.tokens_used
        config.last_used = timezone.now()
        config.save()
        
        return Response({
            'success': True,
            'response': response_text,
            'request_id': engine_request.id,
            'session_id': str(session.session_id),
            'tokens_used': engine_request.tokens_used,
            'response_time': response_time
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_session(request):
    """End an active Engine session."""
    session_id = request.data.get('session_id')
    
    try:
        session = EngineSession.objects.get(
            session_id=session_id,
            user=request.user,
            status='active'
        )
        session.complete_session()
        
        return Response({
            'success': True,
            'message': 'Session ended successfully'
        })
    except EngineSession.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)
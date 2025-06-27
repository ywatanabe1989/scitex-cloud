from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Q
from apps.cloud_app.models import (
    SubscriptionPlan, Subscription, CloudResource, 
    APIKey, ServiceIntegration
)
from apps.api.serializers import (
    SubscriptionSerializer, ResourceUsageSerializer,
    APIKeySerializer, ServiceIntegrationSerializer
)
import uuid
import hashlib


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_status(request):
    """Get current subscription status for the user."""
    try:
        subscription = Subscription.objects.filter(
            user=request.user
        ).select_related('plan').latest('created_at')
        
        serializer = SubscriptionSerializer(subscription)
        
        # Calculate resource usage
        current_period_usage = CloudResource.objects.filter(
            user=request.user,
            period_start__gte=subscription.current_period_start,
            period_end__lte=subscription.current_period_end
        ).values('resource_type').annotate(
            total=Sum('amount_used')
        )
        
        usage_dict = {item['resource_type']: item['total'] for item in current_period_usage}
        
        return Response({
            'subscription': serializer.data,
            'usage': {
                'cpu_hours': usage_dict.get('cpu', 0),
                'gpu_hours': usage_dict.get('gpu', 0),
                'storage_gb': usage_dict.get('storage', 0),
                'bandwidth_gb': usage_dict.get('bandwidth', 0),
                'api_calls': usage_dict.get('api_calls', 0),
            },
            'limits': {
                'max_projects': subscription.plan.max_projects,
                'storage_gb': subscription.plan.storage_gb,
                'cpu_cores': subscription.plan.cpu_cores,
                'gpu_vram_gb': subscription.plan.gpu_vram_gb,
            }
        })
    except Subscription.DoesNotExist:
        # Return free plan defaults
        free_plan = SubscriptionPlan.objects.filter(plan_type='free').first()
        return Response({
            'subscription': None,
            'message': 'No active subscription. Using free tier.',
            'limits': {
                'max_projects': free_plan.max_projects if free_plan else 1,
                'storage_gb': free_plan.storage_gb if free_plan else 5,
                'cpu_cores': free_plan.cpu_cores if free_plan else 2,
                'gpu_vram_gb': free_plan.gpu_vram_gb if free_plan else 0,
            }
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resource_usage(request):
    """Get detailed resource usage for the user."""
    # Get date range from query params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    resource_type = request.GET.get('type')
    
    # Build query
    query = Q(user=request.user)
    if start_date:
        query &= Q(period_start__gte=start_date)
    if end_date:
        query &= Q(period_end__lte=end_date)
    if resource_type:
        query &= Q(resource_type=resource_type)
    
    # Get usage records
    usage_records = CloudResource.objects.filter(query).order_by('-created_at')[:100]
    serializer = ResourceUsageSerializer(usage_records, many=True)
    
    # Calculate totals
    totals = usage_records.values('resource_type').annotate(
        total=Sum('amount_used')
    )
    
    return Response({
        'usage': serializer.data,
        'totals': {item['resource_type']: item['total'] for item in totals},
        'count': usage_records.count()
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_api_keys(request):
    """Manage API keys for the user."""
    if request.method == 'GET':
        keys = APIKey.objects.filter(user=request.user)
        serializer = APIKeySerializer(keys, many=True)
        return Response({
            'api_keys': serializer.data,
            'total': keys.count()
        })
    
    else:  # POST - Create new API key
        name = request.data.get('name')
        if not name:
            return Response({
                'error': 'API key name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user has too many keys
        if APIKey.objects.filter(user=request.user, is_active=True).count() >= 10:
            return Response({
                'error': 'Maximum number of API keys reached (10)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate secure API key
        key_uuid = uuid.uuid4()
        key_hash = hashlib.sha256(f"{key_uuid}{request.user.id}{timezone.now()}".encode()).hexdigest()
        
        # Create API key
        api_key = APIKey.objects.create(
            user=request.user,
            name=name,
            key=key_hash,
            can_read=request.data.get('can_read', True),
            can_write=request.data.get('can_write', False),
            can_delete=request.data.get('can_delete', False),
            rate_limit_per_hour=request.data.get('rate_limit', 1000)
        )
        
        # Return the key only once
        return Response({
            'api_key': {
                'id': api_key.id,
                'name': api_key.name,
                'key': api_key.key,  # Only returned on creation
                'prefix': api_key.prefix,
                'permissions': {
                    'can_read': api_key.can_read,
                    'can_write': api_key.can_write,
                    'can_delete': api_key.can_delete,
                },
                'rate_limit_per_hour': api_key.rate_limit_per_hour,
                'created_at': api_key.created_at.isoformat()
            },
            'message': 'API key created successfully. Please save the key securely as it will not be shown again.'
        }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_api_key(request, key_id):
    """Delete an API key."""
    api_key = get_object_or_404(APIKey, id=key_id, user=request.user)
    api_key.delete()
    
    return Response({
        'message': 'API key deleted successfully'
    }, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_integrations(request):
    """Manage service integrations."""
    if request.method == 'GET':
        integrations = ServiceIntegration.objects.filter(user=request.user)
        serializer = ServiceIntegrationSerializer(integrations, many=True)
        
        # Get available integrations
        existing_types = integrations.values_list('integration_type', flat=True)
        available = [
            {'type': choice[0], 'name': choice[1]}
            for choice in ServiceIntegration.INTEGRATION_TYPES
            if choice[0] not in existing_types
        ]
        
        return Response({
            'integrations': serializer.data,
            'available': available
        })
    
    else:  # POST - Add new integration
        integration_type = request.data.get('type')
        external_id = request.data.get('external_id')
        
        if not integration_type or not external_id:
            return Response({
                'error': 'Integration type and external ID are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if integration already exists
        if ServiceIntegration.objects.filter(
            user=request.user,
            integration_type=integration_type
        ).exists():
            return Response({
                'error': 'This integration already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create integration
        integration = ServiceIntegration.objects.create(
            user=request.user,
            integration_type=integration_type,
            external_id=external_id,
            access_token=request.data.get('access_token', ''),
            refresh_token=request.data.get('refresh_token', '')
        )
        
        serializer = ServiceIntegrationSerializer(integration)
        return Response({
            'integration': serializer.data,
            'message': f'{integration.get_integration_type_display()} integration added successfully'
        }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_integration(request, integration_id):
    """Delete a service integration."""
    integration = get_object_or_404(ServiceIntegration, id=integration_id, user=request.user)
    integration_type = integration.get_integration_type_display()
    integration.delete()
    
    return Response({
        'message': f'{integration_type} integration removed successfully'
    }, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_usage(request):
    """Track resource usage for billing."""
    resource_type = request.data.get('resource_type')
    amount = request.data.get('amount', 0)
    unit = request.data.get('unit')
    
    if not resource_type or not unit:
        return Response({
            'error': 'Resource type and unit are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get user's subscription
    try:
        subscription = Subscription.objects.filter(
            user=request.user,
            status__in=['trial', 'active']
        ).latest('created_at')
    except Subscription.DoesNotExist:
        subscription = None
    
    # Create usage record
    usage = CloudResource.objects.create(
        user=request.user,
        subscription=subscription,
        resource_type=resource_type,
        amount_used=amount,
        unit=unit,
        period_start=timezone.now(),
        period_end=timezone.now()
    )
    
    return Response({
        'usage_id': usage.id,
        'message': 'Usage tracked successfully'
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def available_plans(request):
    """Get available subscription plans."""
    plans = SubscriptionPlan.objects.filter(is_active=True)
    
    plan_data = []
    for plan in plans:
        plan_data.append({
            'id': plan.id,
            'name': plan.name,
            'type': plan.plan_type,
            'price_monthly': str(plan.price_monthly),
            'price_yearly': str(plan.price_yearly) if plan.price_yearly else None,
            'features': {
                'max_projects': plan.max_projects,
                'storage_gb': plan.storage_gb,
                'cpu_cores': plan.cpu_cores,
                'gpu_vram_gb': plan.gpu_vram_gb,
                'has_watermark': plan.has_watermark,
                'requires_citation': plan.requires_citation,
                'has_priority_support': plan.has_priority_support,
                'has_team_collaboration': plan.has_team_collaboration,
            },
            'is_featured': plan.is_featured
        })
    
    return Response({
        'plans': plan_data,
        'total': len(plan_data)
    })
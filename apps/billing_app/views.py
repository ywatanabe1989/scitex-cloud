#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SciTeX-Cloud Billing Views
Subscription management, billing, and payment processing views
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
from django.db import transaction
from django.conf import settings
import stripe
import json
import logging

from .models import (
    SubscriptionTier, UserSubscription, UsageTracking, QuotaLimit,
    BillingHistory, InstitutionalLicense, PaymentMethod, PromoCode,
    FeatureFlag
)
from .services import (
    SubscriptionService, UsageService, QuotaService, 
    FeatureAccessService, BillingService
)
from .forms import SubscriptionUpgradeForm, PaymentMethodForm

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


@login_required
def subscription_dashboard(request):
    """Main subscription dashboard"""
    try:
        subscription = UserSubscription.objects.filter(user=request.user).first()
        tier_info = FeatureAccessService.get_user_tier_info(request.user)
        
        # Get usage summary for current month
        usage_summary = UsageService.get_usage_summary(request.user)
        
        # Get quota status
        quotas = QuotaLimit.objects.filter(
            user=request.user,
            period_end__gte=timezone.now()
        ).order_by('resource_type')
        
        # Get recent billing history
        billing_history = BillingHistory.objects.filter(
            user=request.user
        ).order_by('-transaction_date')[:10]
        
        # Get available tiers for upgrade
        available_tiers = SubscriptionTier.objects.filter(
            is_active=True
        ).order_by('price_monthly')
        
        context = {
            'subscription': subscription,
            'tier_info': tier_info,
            'usage_summary': usage_summary,
            'quotas': quotas,
            'billing_history': billing_history,
            'available_tiers': available_tiers,
        }
        
        return render(request, 'billing_app/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in subscription dashboard: {str(e)}")
        messages.error(request, "Error loading subscription dashboard")
        return redirect('core_app:dashboard')


@login_required
def pricing_page(request):
    """Pricing page with subscription tiers"""
    tiers = SubscriptionTier.objects.filter(
        is_active=True
    ).order_by('display_order', 'price_monthly')
    
    user_tier_info = FeatureAccessService.get_user_tier_info(request.user)
    
    context = {
        'tiers': tiers,
        'user_tier_info': user_tier_info,
    }
    
    return render(request, 'billing_app/pricing.html', context)


@login_required
@require_POST
def subscribe(request):
    """Handle subscription creation"""
    try:
        tier_id = request.POST.get('tier_id')
        billing_cycle = request.POST.get('billing_cycle', 'monthly')
        payment_method_id = request.POST.get('payment_method_id')
        promo_code = request.POST.get('promo_code')
        
        if not tier_id:
            return JsonResponse({
                'success': False,
                'error': 'Tier ID is required'
            }, status=400)
        
        tier = get_object_or_404(SubscriptionTier, id=tier_id, is_active=True)
        
        # Check if user already has subscription
        existing_sub = UserSubscription.objects.filter(user=request.user).first()
        if existing_sub and existing_sub.is_active():
            return JsonResponse({
                'success': False,
                'error': 'You already have an active subscription'
            }, status=400)
        
        # Create subscription
        subscription = SubscriptionService.create_subscription(
            user=request.user,
            tier=tier,
            billing_cycle=billing_cycle,
            payment_method_id=payment_method_id,
            promo_code=promo_code
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully subscribed to {tier.name}',
            'subscription_id': subscription.id,
            'redirect_url': reverse('billing:dashboard')
        })
        
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def upgrade_subscription(request):
    """Handle subscription upgrade"""
    try:
        subscription = get_object_or_404(UserSubscription, user=request.user)
        
        tier_id = request.POST.get('tier_id')
        billing_cycle = request.POST.get('billing_cycle')
        
        if not tier_id:
            return JsonResponse({
                'success': False,
                'error': 'Tier ID is required'
            }, status=400)
        
        new_tier = get_object_or_404(SubscriptionTier, id=tier_id, is_active=True)
        
        # Upgrade subscription
        updated_subscription = SubscriptionService.upgrade_subscription(
            subscription=subscription,
            new_tier=new_tier,
            billing_cycle=billing_cycle
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully upgraded to {new_tier.name}',
            'subscription_id': updated_subscription.id
        })
        
    except Exception as e:
        logger.error(f"Error upgrading subscription: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def cancel_subscription(request):
    """Handle subscription cancellation"""
    try:
        subscription = get_object_or_404(UserSubscription, user=request.user)
        
        reason = request.POST.get('reason', '')
        immediate = request.POST.get('immediate') == 'true'
        
        SubscriptionService.cancel_subscription(
            subscription=subscription,
            reason=reason,
            immediate=immediate
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Subscription canceled successfully' if immediate 
                      else 'Subscription will cancel at the end of current period'
        })
        
    except Exception as e:
        logger.error(f"Error canceling subscription: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def payment_methods(request):
    """Manage payment methods"""
    methods = PaymentMethod.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-is_default', '-created_at')
    
    context = {
        'payment_methods': methods,
        'stripe_publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''),
    }
    
    return render(request, 'billing_app/payment_methods.html', context)


@login_required
@require_POST
def add_payment_method(request):
    """Add new payment method"""
    try:
        payment_method_id = request.POST.get('payment_method_id')
        if not payment_method_id:
            return JsonResponse({
                'success': False,
                'error': 'Payment method ID is required'
            }, status=400)
        
        # Get payment method from Stripe
        pm = stripe.PaymentMethod.retrieve(payment_method_id)
        
        # Create customer if doesn't exist
        subscription = UserSubscription.objects.filter(user=request.user).first()
        if subscription and subscription.stripe_customer_id:
            customer_id = subscription.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=request.user.email,
                name=request.user.get_full_name() or request.user.username,
                metadata={'user_id': request.user.id}
            )
            customer_id = customer.id
            
            # Update subscription with customer ID
            if subscription:
                subscription.stripe_customer_id = customer_id
                subscription.save()
        
        # Attach payment method to customer
        stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
        
        # Create payment method record
        PaymentMethod.objects.create(
            user=request.user,
            stripe_payment_method_id=payment_method_id,
            card_brand=pm.card.brand,
            card_last4=pm.card.last4,
            card_exp_month=pm.card.exp_month,
            card_exp_year=pm.card.exp_year,
            billing_name=pm.billing_details.name or '',
            billing_address=pm.billing_details.address.line1 or '' if pm.billing_details.address else '',
            billing_city=pm.billing_details.address.city or '' if pm.billing_details.address else '',
            billing_state=pm.billing_details.address.state or '' if pm.billing_details.address else '',
            billing_zip=pm.billing_details.address.postal_code or '' if pm.billing_details.address else '',
            billing_country=pm.billing_details.address.country or '' if pm.billing_details.address else '',
            is_default=not PaymentMethod.objects.filter(user=request.user, is_active=True).exists()
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Payment method added successfully'
        })
        
    except Exception as e:
        logger.error(f"Error adding payment method: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def usage_analytics(request):
    """Usage analytics and quota management page"""
    # Get current period usage
    usage_summary = UsageService.get_usage_summary(request.user)
    
    # Get quota status
    quotas = QuotaLimit.objects.filter(
        user=request.user,
        period_end__gte=timezone.now()
    ).order_by('resource_type')
    
    # Get usage history for charts
    usage_history = UsageTracking.objects.filter(
        user=request.user,
        period_start__gte=timezone.now().replace(day=1) - timezone.timedelta(days=90)
    ).order_by('-recorded_at')[:100]
    
    tier_info = FeatureAccessService.get_user_tier_info(request.user)
    
    context = {
        'usage_summary': usage_summary,
        'quotas': quotas,
        'usage_history': usage_history,
        'tier_info': tier_info,
    }
    
    return render(request, 'billing_app/usage_analytics.html', context)


@login_required
def billing_history(request):
    """Billing history page"""
    history = BillingHistory.objects.filter(
        user=request.user
    ).order_by('-transaction_date')
    
    paginator = Paginator(history, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'billing_history': page_obj.object_list,
    }
    
    return render(request, 'billing_app/billing_history.html', context)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    try:
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        
        if endpoint_secret:
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, endpoint_secret
                )
            except ValueError:
                return JsonResponse({'error': 'Invalid payload'}, status=400)
            except stripe.error.SignatureVerificationError:
                return JsonResponse({'error': 'Invalid signature'}, status=400)
        else:
            event = json.loads(payload)
        
        # Process the webhook
        BillingService.process_webhook(event)
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JsonResponse({'error': 'Webhook processing failed'}, status=500)


@login_required
def api_usage_details(request):
    """API endpoint for usage details"""
    resource_type = request.GET.get('resource_type')
    
    if resource_type:
        usage_records = UsageTracking.objects.filter(
            user=request.user,
            resource_type=resource_type,
            period_start__gte=timezone.now().replace(day=1)
        ).order_by('-recorded_at')[:50]
    else:
        usage_records = UsageTracking.objects.filter(
            user=request.user,
            period_start__gte=timezone.now().replace(day=1)
        ).order_by('-recorded_at')[:100]
    
    data = []
    for record in usage_records:
        data.append({
            'resource_type': record.resource_type,
            'amount_used': float(record.amount_used),
            'unit': record.unit,
            'module': record.module,
            'feature': record.feature,
            'recorded_at': record.recorded_at.isoformat(),
            'metadata': record.metadata
        })
    
    return JsonResponse({'usage_records': data})


@login_required
def quota_status_api(request):
    """API endpoint for quota status"""
    quotas = QuotaLimit.objects.filter(
        user=request.user,
        period_end__gte=timezone.now()
    )
    
    data = {}
    for quota in quotas:
        data[quota.resource_type] = {
            'limit_amount': float(quota.limit_amount),
            'used_amount': float(quota.used_amount),
            'unit': quota.unit,
            'usage_percentage': quota.usage_percentage(),
            'is_near_limit': quota.is_near_limit(),
            'is_exceeded': quota.is_exceeded(),
            'warning_threshold': float(quota.warning_threshold),
            'period_end': quota.period_end.isoformat()
        }
    
    return JsonResponse({'quotas': data})


@staff_member_required
def admin_billing_dashboard(request):
    """Admin billing dashboard"""
    # Get subscription statistics
    total_subscriptions = UserSubscription.objects.count()
    active_subscriptions = UserSubscription.objects.filter(
        status__in=['active', 'trialing']
    ).count()
    
    # Revenue statistics
    monthly_revenue = BillingHistory.objects.filter(
        transaction_type='subscription',
        status='succeeded',
        transaction_date__gte=timezone.now().replace(day=1)
    ).aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    # Recent transactions
    recent_transactions = BillingHistory.objects.filter(
        transaction_date__gte=timezone.now() - timezone.timedelta(days=7)
    ).order_by('-transaction_date')[:20]
    
    # Tier distribution
    tier_distribution = UserSubscription.objects.filter(
        status__in=['active', 'trialing']
    ).values('tier__name').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    context = {
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'monthly_revenue': monthly_revenue,
        'recent_transactions': recent_transactions,
        'tier_distribution': tier_distribution,
    }
    
    return render(request, 'billing_app/admin_dashboard.html', context)


@login_required
def institutional_licenses(request):
    """Institutional licenses page"""
    if not request.user.email:
        messages.warning(request, "Email address required for institutional licensing")
        return redirect('billing:dashboard')
    
    user_domain = request.user.email.split('@')[1].lower()
    
    # Check if user's domain has institutional license
    license = InstitutionalLicense.objects.filter(
        domain__iexact=user_domain,
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).first()
    
    context = {
        'license': license,
        'user_domain': user_domain,
        'is_eligible': license and license.is_user_eligible(request.user),
    }
    
    return render(request, 'billing_app/institutional.html', context)


@login_required
@require_POST
def join_institutional_license(request):
    """Join institutional license"""
    try:
        license_id = request.POST.get('license_id')
        license = get_object_or_404(InstitutionalLicense, id=license_id, is_active=True)
        
        if not license.is_user_eligible(request.user):
            return JsonResponse({
                'success': False,
                'error': 'You are not eligible for this institutional license'
            }, status=400)
        
        if not license.can_add_user():
            return JsonResponse({
                'success': False,
                'error': 'This institutional license has reached its user limit'
            }, status=400)
        
        # Create subscription under institutional license
        from .services import InstitutionalService
        subscription = InstitutionalService.add_user_to_institution(request.user, license)
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully joined {license.institution_name} license',
            'subscription_id': subscription.id
        })
        
    except Exception as e:
        logger.error(f"Error joining institutional license: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def feature_access_check(request):
    """API endpoint to check feature access"""
    feature_name = request.GET.get('feature')
    if not feature_name:
        return JsonResponse({'error': 'Feature name required'}, status=400)
    
    has_access = FeatureAccessService.has_feature_access(request.user, feature_name)
    tier_info = FeatureAccessService.get_user_tier_info(request.user)
    
    return JsonResponse({
        'has_access': has_access,
        'feature': feature_name,
        'current_tier': tier_info['tier'].name if tier_info else 'Free',
        'tier_info': tier_info
    })
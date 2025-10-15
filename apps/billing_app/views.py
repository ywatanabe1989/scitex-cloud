from django.shortcuts import render


def pricing(request):
    """Display pricing plans."""
    return render(request, 'billing_app/pricing.html')


def premium_subscription(request):
    """Premium subscription page."""
    return render(request, 'billing_app/premium_subscription.html')


def donation_success(request):
    """Donation success page."""
    return render(request, 'billing_app/donation_success.html')

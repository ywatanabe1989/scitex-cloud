from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Pricing and subscription pages
    path('pricing/', views.pricing, name='pricing'),
    path('subscribe/', views.premium_subscription, name='subscribe'),
    path('donation/success/', views.donation_success, name='donation_success'),
]

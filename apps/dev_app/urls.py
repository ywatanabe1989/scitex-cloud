from django.urls import path
from .views import DesignSystemView

app_name = 'dev_app'

urlpatterns = [
    path('design.html', DesignSystemView.as_view(), name='design_system'),
    path('design/', DesignSystemView.as_view(), name='design_system_alt'),
]

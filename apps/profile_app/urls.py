from django.urls import path
from . import views

app_name = 'profile_app'

urlpatterns = [
    # Profile views
    path('profile/', views.profile_view, name='profile'),
    path('settings/profile/', views.profile_edit, name='profile_edit'),
    path('settings/appearance/', views.appearance_settings, name='appearance'),
]

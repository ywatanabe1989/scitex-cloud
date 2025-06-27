from django.urls import path
from . import views

app_name = 'engine'

urlpatterns = [
    path('', views.index, name='index'),
    path('features/', views.features, name='features'),
    path('pricing/', views.pricing, name='pricing'),
    
    # Authenticated views
    path('dashboard/', views.dashboard, name='dashboard'),
    path('configuration/', views.configuration, name='configuration'),
    path('configuration/<int:config_id>/', views.configuration, name='configuration-detail'),
    path('sessions/', views.sessions, name='sessions'),
    path('sessions/<uuid:session_id>/', views.session_detail, name='session-detail'),
    path('snippets/', views.snippets, name='snippets'),
    path('snippets/create/', views.create_snippet, name='create-snippet'),
    path('workflows/', views.workflows, name='workflows'),
    path('integrations/', views.integrations, name='integrations'),
]
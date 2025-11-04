from django.urls import path
from ..views.dashboard import main

urlpatterns = [
    path('', main.dashboard_main, name='dashboard'),
    path('writer/', main.dashboard_main, name='dashboard_writer'),
]

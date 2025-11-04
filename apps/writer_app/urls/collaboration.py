from django.urls import path
from ..views.collaboration import session

urlpatterns = [
    path('', session.collaboration_session, name='session'),
]

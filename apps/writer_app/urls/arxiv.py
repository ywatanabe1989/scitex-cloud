from django.urls import path
from ..views.arxiv import submission

urlpatterns = [
    path('submit/', submission.arxiv_submit, name='submit'),
]

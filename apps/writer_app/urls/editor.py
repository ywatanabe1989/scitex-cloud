from django.urls import path
from ..views.editor import editor

urlpatterns = [
    path('', editor.editor, name='editor'),
]

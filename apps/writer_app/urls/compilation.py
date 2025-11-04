from django.urls import path
from ..views.compilation import compilation

urlpatterns = [
    path('', compilation.compilation_view, name='compilation_view'),
]

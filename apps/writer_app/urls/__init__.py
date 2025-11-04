from django.urls import path, include

app_name = 'writer_app'

urlpatterns = [
    path('editor/', include('apps.writer_app.urls.editor')),
    path('compilation/', include('apps.writer_app.urls.compilation')),
    path('version-control/', include('apps.writer_app.urls.version_control')),
    path('arxiv/', include('apps.writer_app.urls.arxiv')),
    path('collaboration/', include('apps.writer_app.urls.collaboration')),
    path('', include('apps.writer_app.urls.dashboard')),
]

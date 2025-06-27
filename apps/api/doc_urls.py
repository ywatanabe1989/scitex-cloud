from django.urls import path
from apps.api import doc_views

urlpatterns = [
    # SciTeX-Doc API endpoints
    path('compile/', doc_views.compile_document, name='doc-compile'),
    path('templates/', doc_views.list_templates, name='doc-templates'),
    path('revisions/<int:manuscript_id>/', doc_views.list_revisions, name='doc-revisions'),
    path('export/', doc_views.export_document, name='doc-export'),
    path('citations/', doc_views.manage_citations, name='doc-citations'),
    path('generate-section/', doc_views.generate_section, name='doc-generate-section'),
]
from django.urls import path
from apps.api import viz_views

urlpatterns = [
    # SciTeX-Viz API endpoints
    path('generate/', viz_views.generate_figure, name='viz-generate'),
    path('templates/', viz_views.list_templates, name='viz-templates'),
    path('sigmaplot/', viz_views.sigmaplot_export, name='viz-sigmaplot'),
    path('gallery/', viz_views.figure_gallery, name='viz-gallery'),
]
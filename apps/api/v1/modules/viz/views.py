from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import base64


class VizViewSet(viewsets.ViewSet):
    """
    API for SciTeX-Viz (SigmaPlot integration)
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def convert(self, request):
        """Convert Python plot to SigmaPlot format"""
        plot_data = request.data.get('plot_data', {})
        plot_type = request.data.get('plot_type', 'scatter')
        
        # Mock conversion - in production would use actual conversion
        result = {
            'sigmaplot_file': 'plot_12345.jnb',
            'preview_url': '/media/previews/plot_12345.png',
            'download_url': '/api/v1/viz/download/plot_12345/',
            'format': 'SigmaPlot 14.0',
            'status': 'success'
        }
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get publication-ready plot templates"""
        templates = [
            {
                'id': 'nature_scatter',
                'name': 'Nature - Scatter Plot',
                'description': 'Nature journal scatter plot specifications',
                'preview': '/static/images/templates/nature_scatter.png'
            },
            {
                'id': 'science_bar',
                'name': 'Science - Bar Chart',
                'description': 'Science journal bar chart template',
                'preview': '/static/images/templates/science_bar.png'
            },
            {
                'id': 'ieee_line',
                'name': 'IEEE - Line Plot',
                'description': 'IEEE transaction line plot format',
                'preview': '/static/images/templates/ieee_line.png'
            }
        ]
        
        return Response({
            'templates': templates,
            'count': len(templates)
        })
    
    @action(detail=False, methods=['post'])
    def preview(self, request):
        """Generate plot preview"""
        # Mock preview generation
        preview_data = {
            'preview_image': 'data:image/png;base64,iVBORw0KGgoAAAANS...',
            'dimensions': {'width': 800, 'height': 600},
            'format': 'PNG',
            'dpi': 300
        }
        
        return Response(preview_data)
    
    @action(detail=False, methods=['get'])
    def gallery(self, request):
        """Get example gallery"""
        gallery = [
            {
                'id': 'neuroscience_1',
                'title': 'Neural Activity Heatmap',
                'category': 'neuroscience',
                'thumbnail': '/static/images/gallery/neural_heatmap_thumb.png',
                'full_image': '/static/images/gallery/neural_heatmap.png'
            },
            {
                'id': 'stats_1',
                'title': 'Multi-panel Statistical Comparison',
                'category': 'statistics',
                'thumbnail': '/static/images/gallery/stats_multi_thumb.png',
                'full_image': '/static/images/gallery/stats_multi.png'
            }
        ]
        
        return Response({
            'gallery': gallery,
            'categories': ['neuroscience', 'statistics', 'biology', 'physics']
        })
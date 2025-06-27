from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def generate_figure(request):
    """Generate a figure using SciTeX-Viz."""
    plot_type = request.data.get('plot_type', 'line')
    data = request.data.get('data', {})
    # TODO: Implement figure generation
    return Response({
        'figure_id': 'fig-123',
        'status': 'generating',
        'message': 'Figure generation started'
    }, status=status.HTTP_202_ACCEPTED)

@api_view(['GET'])
def list_templates(request):
    """List available figure templates."""
    return Response({
        'templates': [
            {'id': 'line', 'name': 'Line Plot'},
            {'id': 'scatter', 'name': 'Scatter Plot'},
            {'id': 'bar', 'name': 'Bar Chart'},
            {'id': 'box', 'name': 'Box Plot'},
            {'id': 'violin', 'name': 'Violin Plot'},
        ]
    })

@api_view(['POST'])
def sigmaplot_export(request):
    """Export figure to SigmaPlot format."""
    figure_id = request.data.get('figure_id')
    # TODO: Implement SigmaPlot export
    return Response({
        'export_id': 'export-123',
        'status': 'processing',
        'message': 'SigmaPlot export started'
    })

@api_view(['GET'])
def figure_gallery(request):
    """Get user's figure gallery."""
    # TODO: Implement figure gallery
    return Response({
        'figures': [],
        'total': 0
    })
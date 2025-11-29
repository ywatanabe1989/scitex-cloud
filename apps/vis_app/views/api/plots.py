"""
Scientific Figure Editor - Plot Rendering API Views
REST API endpoints for backend plot rendering using matplotlib/scitex.plt
"""

import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from apps.vis_app.plot_renderer import render_plot_from_spec


@require_http_methods(["POST"])
@csrf_exempt
def render_plot(request):
    """
    Render a scientific plot from JSON specification.

    POST /api/vis/plot/

    Request body (JSON):
    {
      "figure": {"width_mm": 35, "height_mm": 24.5, "dpi": 300},
      "style": {"tick_length_mm": 0.8, ...},
      "plot": {"kind": "line", "csv_path": "...", ...}
    }

    Response:
    - Success: SVG image (Content-Type: image/svg+xml)
    - Error: JSON with error details
    """
    try:
        spec = json.loads(request.body)

        # Validate required fields
        if 'figure' not in spec:
            return JsonResponse({
                'error': 'Missing required field: figure is required'
            }, status=400)

        if 'plot' not in spec and 'panels' not in spec:
            return JsonResponse({
                'error': 'Missing required field: either plot or panels is required'
            }, status=400)

        # Render plot using matplotlib backend
        svg_buffer = render_plot_from_spec(spec)

        # Return SVG
        return HttpResponse(
            svg_buffer.getvalue(),
            content_type='image/svg+xml'
        )

    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)

    except ValueError as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'error': f'Internal server error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def upload_plot_data(request):
    """
    Upload CSV or Excel file for plot rendering.

    POST /api/vis/upload-plot-data/

    Request: multipart/form-data with 'file' field

    Response:
    - Success: JSON with file_path
    - Error: JSON with error details
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({
                'error': 'No file uploaded'
            }, status=400)

        uploaded_file = request.FILES['file']

        # Validate file extension
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        file_ext = '.' + uploaded_file.name.split('.')[-1].lower()

        if file_ext not in allowed_extensions:
            return JsonResponse({
                'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
            }, status=400)

        # Save to temporary directory
        import tempfile
        import os
        from pathlib import Path

        # Create temp directory for uploaded plot data
        temp_dir = Path(tempfile.gettempdir()) / 'scitex_plot_data'
        temp_dir.mkdir(exist_ok=True)

        # Generate unique filename
        import uuid
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = temp_dir / unique_filename

        # Save file
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        return JsonResponse({
            'success': True,
            'file_path': str(file_path),
            'filename': uploaded_file.name,
            'size': uploaded_file.size
        })

    except Exception as e:
        return JsonResponse({
            'error': f'Upload failed: {str(e)}'
        }, status=500)

"""
Scientific Figure Editor - API Views
REST API endpoints for the Canvas editor
"""

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
import base64

from .models import (
    JournalPreset,
    ScientificFigure,
    FigurePanel,
    Annotation,
    FigureExport,
)


@require_http_methods(["GET"])
def get_journal_presets(request):
    """Get all available journal presets"""
    presets = JournalPreset.objects.filter(is_active=True).values(
        "id",
        "name",
        "column_type",
        "width_mm",
        "height_mm",
        "dpi",
        "font_family",
        "font_size_pt",
        "line_width_pt",
    )

    return JsonResponse({"presets": list(presets)})


@require_http_methods(["GET"])
def get_preset_detail(request, preset_id):
    """Get details of a specific journal preset"""
    preset = get_object_or_404(JournalPreset, id=preset_id, is_active=True)

    # Calculate pixel dimensions
    def mm_to_pixels(mm, dpi):
        inches = mm / 25.4
        return int(inches * dpi)

    width_px = mm_to_pixels(preset.width_mm, preset.dpi)
    height_px = mm_to_pixels(preset.height_mm, preset.dpi) if preset.height_mm else None

    return JsonResponse({
        "id": preset.id,
        "name": preset.name,
        "column_type": preset.column_type,
        "width_mm": preset.width_mm,
        "height_mm": preset.height_mm,
        "width_px": width_px,
        "height_px": height_px,
        "dpi": preset.dpi,
        "font_family": preset.font_family,
        "font_size_pt": preset.font_size_pt,
        "line_width_pt": preset.line_width_pt,
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def save_figure_state(request, figure_id):
    """Save canvas state to database"""
    figure = get_object_or_404(ScientificFigure, id=figure_id, owner=request.user)

    try:
        data = json.loads(request.body)
        canvas_state = data.get("canvas_state", {})

        figure.canvas_state = canvas_state
        figure.status = "editing"
        figure.save()

        return JsonResponse({
            "success": True,
            "message": "Figure saved successfully",
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON data",
        }, status=400)


@login_required
@require_http_methods(["GET"])
def load_figure_state(request, figure_id):
    """Load canvas state from database"""
    figure = get_object_or_404(ScientificFigure, id=figure_id, owner=request.user)

    return JsonResponse({
        "figure_id": str(figure.id),
        "title": figure.title,
        "layout": figure.layout,
        "canvas_state": figure.canvas_state,
        "canvas_width_px": figure.canvas_width_px,
        "canvas_height_px": figure.canvas_height_px,
        "canvas_dpi": figure.canvas_dpi,
        "journal_preset_id": figure.journal_preset_id,
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def upload_panel_image(request, figure_id):
    """Upload image for a figure panel"""
    figure = get_object_or_object(ScientificFigure, id=figure_id, owner=request.user)

    try:
        data = json.loads(request.body)
        panel_position = data.get("position", "A")
        image_data = data.get("image_data")  # base64 encoded

        if not image_data:
            return JsonResponse({
                "success": False,
                "error": "No image data provided",
            }, status=400)

        # Decode base64 image
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_file = ContentFile(base64.b64decode(imgstr), name=f'panel_{panel_position}.{ext}')

        # Create or update panel
        panel, created = FigurePanel.objects.update_or_create(
            figure=figure,
            position=panel_position,
            defaults={
                "source_image": image_file,
                "order": ord(panel_position) - ord('A'),
            }
        )

        return JsonResponse({
            "success": True,
            "panel_id": str(panel.id),
            "image_url": panel.source_image.url if panel.source_image else None,
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e),
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def update_figure_config(request, figure_id):
    """Update figure configuration (layout, preset, canvas size)"""
    figure = get_object_or_404(ScientificFigure, id=figure_id, owner=request.user)

    try:
        data = json.loads(request.body)

        if "layout" in data:
            figure.layout = data["layout"]

        if "journal_preset_id" in data:
            figure.journal_preset_id = data["journal_preset_id"]

        if "canvas_width_px" in data:
            figure.canvas_width_px = data["canvas_width_px"]

        if "canvas_height_px" in data:
            figure.canvas_height_px = data["canvas_height_px"]

        if "canvas_dpi" in data:
            figure.canvas_dpi = data["canvas_dpi"]

        figure.save()

        return JsonResponse({
            "success": True,
            "message": "Figure configuration updated",
        })

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON data",
        }, status=400)

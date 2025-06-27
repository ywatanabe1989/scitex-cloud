from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


def index(request):
    """Writer app - direct LaTeX editor interface."""
    return render(request, 'writer_app/simple_editor.html')


def modular_editor(request):
    """Modular text-based editor with word counts (User Requested Approach)."""
    return render(request, 'writer_app/modular_editor.html')


def simple_editor(request):
    """Simple MVP LaTeX editor interface."""
    return render(request, 'writer_app/simple_editor.html')


def features(request):
    """Writer features view."""
    return render(request, 'writer_app/features.html')


def pricing(request):
    """Writer pricing view."""
    return render(request, 'writer_app/pricing.html')


@require_http_methods(["POST"])
def mock_compile(request):
    """Mock LaTeX compilation endpoint."""
    # Mock successful compilation
    return JsonResponse({
        'status': 'success',
        'pdf_url': '/static/mock/sample.pdf',
        'log': 'LaTeX compilation completed successfully.\nOutput: 2 pages, 45.7 KB',
        'pages': 2,
        'size': '45.7 KB'
    })


@require_http_methods(["POST"])
def mock_save(request):
    """Mock document save endpoint."""
    return JsonResponse({
        'status': 'success',
        'message': 'Document saved successfully',
        'timestamp': '2024-01-01 12:00:00'
    })
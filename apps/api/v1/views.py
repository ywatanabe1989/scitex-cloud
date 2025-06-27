from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class ModuleViewSet(viewsets.ViewSet):
    """
    API endpoint for listing and managing SciTeX modules
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List all available SciTeX modules with their status"""
        modules = [
            {
                'id': 'engine',
                'name': 'SciTeX-Engine',
                'description': 'AI-assisted coding in Emacs',
                'status': 'active',
                'version': '1.0.0',
                'features': ['Code completion', 'AI assistance', 'Research templates']
            },
            {
                'id': 'doc',
                'name': 'SciTeX-Doc',
                'description': 'LaTeX manuscript management',
                'status': 'active',
                'version': '1.0.0',
                'features': ['Version control', 'Template library', 'Citation management']
            },
            {
                'id': 'code',
                'name': 'SciTeX-Code',
                'description': 'MNGS Python utilities',
                'status': 'active',
                'version': '1.3.7',
                'features': ['Data processing', 'Visualization', 'Statistical analysis']
            },
            {
                'id': 'viz',
                'name': 'SciTeX-Viz',
                'description': 'SigmaPlot integration',
                'status': 'active',
                'version': '1.0.0',
                'features': ['Publication-ready plots', 'Python to SigmaPlot bridge', 'Export templates']
            },
            {
                'id': 'search',
                'name': 'SciTeX-Search',
                'description': 'Advanced LaTeX search',
                'status': 'active',
                'version': '1.0.0',
                'features': ['Math formula search', 'Full-text indexing', 'Citation tracking']
            }
        ]
        
        return Response({
            'modules': modules,
            'count': len(modules)
        })
    
    def retrieve(self, request, pk=None):
        """Get details for a specific module"""
        module_details = {
            'engine': {
                'id': 'engine',
                'name': 'SciTeX-Engine',
                'description': 'AI-assisted coding in Emacs for research',
                'long_description': 'Integrates advanced AI capabilities directly into Emacs for scientific coding',
                'status': 'active',
                'version': '1.0.0',
                'documentation_url': '/docs/engine/',
                'api_endpoint': '/api/v1/engine/',
                'requirements': ['Emacs 27+', 'Python 3.8+'],
                'pricing_tiers': ['free', 'premium', 'enterprise']
            },
            'doc': {
                'id': 'doc',
                'name': 'SciTeX-Doc',
                'description': 'Complete LaTeX manuscript lifecycle management',
                'long_description': 'Manage your research papers from draft to publication',
                'status': 'active',
                'version': '1.0.0',
                'documentation_url': '/docs/doc/',
                'api_endpoint': '/api/v1/doc/',
                'requirements': ['LaTeX distribution', 'Git'],
                'pricing_tiers': ['free', 'premium', 'enterprise']
            },
            'code': {
                'id': 'code',
                'name': 'SciTeX-Code (MNGS)',
                'description': 'Comprehensive Python utilities for research',
                'long_description': 'Production-ready Python package with utilities for data processing and analysis',
                'status': 'active',
                'version': '1.3.7',
                'documentation_url': '/docs/code/',
                'api_endpoint': '/api/v1/code/',
                'requirements': ['Python 3.8+'],
                'pricing_tiers': ['free', 'premium', 'enterprise'],
                'pypi_url': 'https://pypi.org/project/mngs/'
            },
            'viz': {
                'id': 'viz',
                'name': 'SciTeX-Viz',
                'description': 'Python to SigmaPlot bridge for publication-ready figures',
                'long_description': 'Create publication-quality figures with SigmaPlot from Python',
                'status': 'active',
                'version': '1.0.0',
                'documentation_url': '/docs/viz/',
                'api_endpoint': '/api/v1/viz/',
                'requirements': ['Python 3.8+', 'SigmaPlot license'],
                'pricing_tiers': ['premium', 'enterprise']
            },
            'search': {
                'id': 'search',
                'name': 'SciTeX-Search',
                'description': 'Advanced search for LaTeX documents and math formulas',
                'long_description': 'Search through LaTeX documents including mathematical expressions',
                'status': 'active',
                'version': '1.0.0',
                'documentation_url': '/docs/search/',
                'api_endpoint': '/api/v1/search/',
                'requirements': ['Python 3.8+'],
                'pricing_tiers': ['free', 'premium', 'enterprise']
            }
        }
        
        if pk in module_details:
            return Response(module_details[pk])
        else:
            return Response(
                {'error': 'Module not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Check the operational status of a module"""
        # In production, this would check actual service health
        return Response({
            'module': pk,
            'operational': True,
            'response_time_ms': 45,
            'last_checked': '2025-01-23T12:00:00Z'
        })
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class CodeViewSet(viewsets.ViewSet):
    """
    API for SciTeX-Code (MNGS Python utilities)
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def modules(self, request):
        """List available MNGS modules"""
        modules = [
            {
                'name': 'mngs.io',
                'description': 'Advanced I/O operations',
                'functions': ['load', 'save', 'read_yaml', 'write_yaml']
            },
            {
                'name': 'mngs.plt',
                'description': 'Enhanced plotting utilities',
                'functions': ['subplots', 'figure', 'savefig', 'add_colorbar']
            },
            {
                'name': 'mngs.dsp',
                'description': 'Digital signal processing',
                'functions': ['fft', 'filter', 'resample', 'hilbert']
            },
            {
                'name': 'mngs.stats',
                'description': 'Statistical analysis tools',
                'functions': ['ttest', 'anova', 'correlation', 'regression']
            }
        ]
        
        return Response({
            'modules': modules,
            'version': '1.3.7',
            'pypi_url': 'https://pypi.org/project/mngs/'
        })
    
    @action(detail=False, methods=['post'])
    def execute(self, request):
        """Execute MNGS code snippet"""
        code = request.data.get('code', '')
        module = request.data.get('module', '')
        
        # Mock execution - in production would run in sandboxed environment
        result = {
            'output': 'Array shape: (100, 50)\nMean: 0.523\nStd: 1.024',
            'execution_time': 0.125,
            'memory_used': '12.5 MB',
            'status': 'success'
        }
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def examples(self, request):
        """Get code examples"""
        examples = [
            {
                'id': 'io_example',
                'title': 'Loading and saving data',
                'code': 'import mngs\n\ndata = mngs.io.load("data.pkl")\nprocessed = data.mean(axis=0)\nmngs.io.save(processed, "result.pkl")',
                'tags': ['io', 'data']
            },
            {
                'id': 'plot_example',
                'title': 'Creating publication figures',
                'code': 'import mngs\n\nfig, ax = mngs.plt.subplots()\nax.plot(x, y)\nmngs.plt.savefig("figure.png", dpi=300)',
                'tags': ['plotting', 'visualization']
            }
        ]
        
        return Response({
            'examples': examples,
            'count': len(examples)
        })
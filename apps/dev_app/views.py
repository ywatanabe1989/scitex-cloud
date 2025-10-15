from django.shortcuts import render
from django.views import View


class DesignSystemView(View):
    """Display the SciTeX design system documentation."""

    template_name = 'dev_app/pages/design.html'

    def get(self, request):
        """Render the design system page."""
        return render(request, self.template_name)

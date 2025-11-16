"""
WebSocket routing for Code Workspace
"""

from django.urls import path
from . import terminal_views

websocket_urlpatterns = [
    path('ws/code/terminal/', terminal_views.TerminalConsumer.as_asgi()),
]

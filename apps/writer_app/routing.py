"""
WebSocket routing for Writer app collaborative editing.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/writer/manuscript/(?P<manuscript_id>\w+)/$', consumers.DocumentCollaborationConsumer.as_asgi()),
]
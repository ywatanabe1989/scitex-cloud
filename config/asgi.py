"""
ASGI config for SciTeX Cloud project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# Import routing after Django setup
from apps.writer_app import routing as writer_routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                writer_routing.websocket_urlpatterns
            )
        )
    ),
})
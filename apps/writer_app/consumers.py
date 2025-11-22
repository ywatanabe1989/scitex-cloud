"""
WebSocket consumers for SciTeX Writer real-time collaboration.
Uses Django 5.2 async ORM for optimal performance.
"""

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from datetime import datetime
from .models import Manuscript
from scitex import logging

logger = logging.getLogger(__name__)


class WriterConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time collaborative editing.

    Handles:
    - User presence (join/leave notifications)
    - Section locking
    - Real-time text changes
    - Cursor position broadcasting
    """

    async def connect(self):
        """Handle new WebSocket connection."""
        self.manuscript_id = self.scope["url_route"]["kwargs"]["manuscript_id"]
        self.room_group_name = f"manuscript_{self.manuscript_id}"
        self.user = self.scope["user"]

        # Reject anonymous users
        if not self.user.is_authenticated:
            await self.close()
            return

        # Django 5.2 async ORM: Check manuscript access
        try:
            self.manuscript = await Manuscript.objects.select_related(
                "owner", "project"
            ).aget(id=self.manuscript_id)
        except Manuscript.DoesNotExist:
            await self.close()
            return

        # Check permissions
        has_access = await self.check_access()
        if not has_access:
            await self.close()
            return

        # Initialize OT coordinator and undo/redo coordinator for this manuscript
        self.ot_coordinator = OTCoordinator(self.manuscript_id)
        self.undo_redo_coordinator = CollaborativeUndoRedoCoordinator(
            self.manuscript_id
        )

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Create or update collaborative session
        self.session = await self.create_session()

        # Broadcast user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_joined",
                "user_id": self.user.id,
                "username": self.user.username,
                "timestamp": datetime.now().isoformat(),
            },
        )

        # Send current collaborators list to new user
        collaborators = await self.get_active_collaborators()
        await self.send(
            text_data=json.dumps(
                {"type": "collaborators_list", "collaborators": collaborators}
            )
        )

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect."""
        # End session
        if hasattr(self, "session"):
            await self.end_session()

        # Broadcast user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_left",
                "user_id": self.user.id,
                "username": self.user.username,
                "timestamp": datetime.now().isoformat(),
            },
        )

        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "text_change":
                await self.handle_text_change(data)
            elif message_type == "cursor_position":
                await self.handle_cursor_position(data)
            elif message_type == "section_lock":
                await self.handle_section_lock(data)
            elif message_type == "section_unlock":
                await self.handle_section_unlock(data)
            elif message_type == "operation_ack":
                await self.handle_operation_ack(data)
            elif message_type == "queue_status":
                await self.handle_queue_status(data)
            elif message_type == "undo":
                await self.handle_undo(data)
            elif message_type == "redo":
                await self.handle_redo(data)
            elif message_type == "undo_status":
                await self.handle_undo_status(data)
            else:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "error",
                            "message": f"Unknown message type: {message_type}",
                        }
                    )
                )

        except json.JSONDecodeError:
            await self.send(
                text_data=json.dumps({"type": "error", "message": "Invalid JSON"})
            )
        except Exception as e:
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))

    # Message type handlers

    async def user_joined(self, event):
        """Broadcast user joined to all clients."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_joined",
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def user_left(self, event):
        """Broadcast user left to all clients."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_left",
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def text_change(self, event):
        """Broadcast text change to all clients except sender."""
        if event.get("sender_channel") != self.channel_name:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "text_change",
                        "section": event["section"],
                        "operation": event["operation"],
                        "user_id": event["user_id"],
                        "username": event["username"],
                        "timestamp": event["timestamp"],
                    }
                )
            )

    async def cursor_update(self, event):
        """Broadcast cursor position to all clients except sender."""
        if event.get("sender_channel") != self.channel_name:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "cursor_update",
                        "section": event["section"],
                        "position": event["position"],
                        "user_id": event["user_id"],
                        "username": event["username"],
                    }
                )
            )

    async def section_locked(self, event):
        """Broadcast section lock to all clients."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "section_locked",
                    "section": event["section"],
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def section_unlocked(self, event):
        """Broadcast section unlock to all clients."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "section_unlocked",
                    "section": event["section"],
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    # Action handlers

    async def handle_text_change(self, data):
        """Handle text change from client using OT coordinator."""
        section_id = data.get("section_id")
        operation = data.get("operation")
        version = data.get("version", 0)

        # Submit operation to OT coordinator
        result = await self.ot_coordinator.submit_operation(
            user_id=self.user.id,
            username=self.user.username,
            session_id=self.session.session_id,
            section_id=section_id,
            operation=operation,
            version=version,
        )

        # Send acknowledgment to sender
        await self.send(
            text_data=json.dumps(
                {
                    "type": "operation_submitted",
                    "operation_id": result.get("operation_id"),
                    "status": result.get("status"),
                    "queue_length": result.get("queue_length", 0),
                    "current_version": result.get("current_version", version),
                }
            )
        )

        # Broadcast processed operations to all users
        if result.get("processed"):
            for processed_op in result["processed"]:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "text_change",
                        "section_id": section_id,
                        "operation": operation,
                        "operation_id": processed_op["operation_id"],
                        "user_id": processed_op["user_id"],
                        "version": processed_op["version"],
                        "timestamp": datetime.now().isoformat(),
                        "sender_channel": self.channel_name,
                    },
                )

        # Handle errors
        if result.get("errors"):
            for error in result["errors"]:
                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "operation_error",
                            "operation_id": error["operation_id"],
                            "error": error["error"],
                        }
                    )
                )

    async def handle_cursor_position(self, data):
        """Handle cursor position update from client."""
        section = data.get("section")
        position = data.get("position")

        # Update session cursor position
        await self.update_cursor_position(section, position)

        # Broadcast to all users in room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "cursor_update",
                "section": section,
                "position": position,
                "user_id": self.user.id,
                "username": self.user.username,
                "sender_channel": self.channel_name,
            },
        )

    async def handle_section_lock(self, data):
        """Handle section lock request from client."""
        section = data.get("section")

        # Check if section is already locked
        is_locked = await self.is_section_locked(section)
        if is_locked:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "lock_failed",
                        "section": section,
                        "message": "Section is already locked by another user",
                    }
                )
            )
            return

        # Lock section
        await self.lock_section(section)

        # Broadcast lock to all users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "section_locked",
                "section": section,
                "user_id": self.user.id,
                "username": self.user.username,
                "timestamp": datetime.now().isoformat(),
            },
        )

    async def handle_section_unlock(self, data):
        """Handle section unlock request from client."""
        section = data.get("section")

        # Unlock section
        await self.unlock_section(section)

        # Broadcast unlock to all users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "section_unlocked",
                "section": section,
                "user_id": self.user.id,
                "username": self.user.username,
                "timestamp": datetime.now().isoformat(),
            },
        )

    async def handle_operation_ack(self, data):
        """Handle operation acknowledgment from client."""
        operation_id = data.get("operation_id")
        section_id = data.get("section_id")

        result = await self.ot_coordinator.acknowledge_operation(
            operation_id=operation_id, section_id=section_id
        )

        await self.send(text_data=json.dumps({"type": "ack_received", **result}))

    async def handle_queue_status(self, data):
        """Handle queue status request from client."""
        section_id = data.get("section_id")

        status = await self.ot_coordinator.get_queue_status(section_id)

        await self.send(text_data=json.dumps({"type": "queue_status", **status}))

    async def handle_undo(self, data):
        """Handle undo request from client."""
        section_id = data.get("section_id")
        current_version = data.get("version", 0)

        # Get undo/redo manager for this user and section
        manager = self.undo_redo_coordinator.get_manager(self.user.id, section_id)

        # Perform undo
        undo_result = await manager.undo(current_version)

        if undo_result:
            # Submit the inverse operation through OT coordinator
            result = await self.ot_coordinator.submit_operation(
                user_id=self.user.id,
                username=self.user.username,
                session_id=self.session.session_id,
                section_id=section_id,
                operation=undo_result["operation"],
                version=current_version,
            )

            await self.send(
                text_data=json.dumps(
                    {
                        "type": "undo_result",
                        "success": True,
                        "operation_id": result.get("operation_id"),
                        **undo_result,
                    }
                )
            )

            # Broadcast undo to other users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_undone",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "section_id": section_id,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        else:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "undo_result",
                        "success": False,
                        "message": "Nothing to undo",
                    }
                )
            )

    async def handle_redo(self, data):
        """Handle redo request from client."""
        section_id = data.get("section_id")
        current_version = data.get("version", 0)

        # Get undo/redo manager for this user and section
        manager = self.undo_redo_coordinator.get_manager(self.user.id, section_id)

        # Perform redo
        redo_result = await manager.redo(current_version)

        if redo_result:
            # Submit the operation through OT coordinator
            result = await self.ot_coordinator.submit_operation(
                user_id=self.user.id,
                username=self.user.username,
                session_id=self.session.session_id,
                section_id=section_id,
                operation=redo_result["operation"],
                version=current_version,
            )

            await self.send(
                text_data=json.dumps(
                    {
                        "type": "redo_result",
                        "success": True,
                        "operation_id": result.get("operation_id"),
                        **redo_result,
                    }
                )
            )

            # Broadcast redo to other users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_redone",
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "section_id": section_id,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        else:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "redo_result",
                        "success": False,
                        "message": "Nothing to redo",
                    }
                )
            )

    async def handle_undo_status(self, data):
        """Handle undo/redo status request from client."""
        section_id = data.get("section_id")

        # Get undo/redo manager for this user and section
        manager = self.undo_redo_coordinator.get_manager(self.user.id, section_id)

        # Get status
        status = await manager.get_status()

        await self.send(
            text_data=json.dumps(
                {"type": "undo_status", "section_id": section_id, **status}
            )
        )

    async def user_undone(self, event):
        """Broadcast user undo action to all clients."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_undone",
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "section_id": event["section_id"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def user_redone(self, event):
        """Broadcast user redo action to all clients."""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_redone",
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "section_id": event["section_id"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    # Database operations (Django 5.2 async ORM)

    async def check_access(self):
        """Check if user has access to manuscript."""
        if self.manuscript.owner_id == self.user.id:
            return True
        is_collaborator = await self.manuscript.collaborators.filter(
            id=self.user.id
        ).aexists()
        return is_collaborator

    async def create_session(self):
        """Create or update collaborative session."""
        session, created = await CollaborativeSession.objects.aupdate_or_create(
            manuscript=self.manuscript,
            user=self.user,
            session_id=self.channel_name,
            defaults={"is_active": True, "locked_sections": []},
        )
        return session

    async def end_session(self):
        """End collaborative session."""
        if hasattr(self, "session"):
            self.session.is_active = False
            await self.session.asave()

    async def get_active_collaborators(self):
        """Get list of currently active collaborators."""
        collaborators = []
        async for session in CollaborativeSession.objects.filter(
            manuscript=self.manuscript, is_active=True
        ).select_related("user"):
            if session.is_session_active():
                collaborators.append(
                    {
                        "user_id": session.user.id,
                        "username": session.user.username,
                        "locked_sections": session.locked_sections,
                    }
                )
        return collaborators

    async def log_change(self, section, operation):
        """Log document change to database."""
        from .models import ManuscriptSection

        try:
            section_obj = await ManuscriptSection.objects.aget(
                manuscript=self.manuscript, section_type=section
            )
            await DocumentChange.objects.acreate(
                manuscript=self.manuscript,
                section=section_obj,
                user=self.user,
                session=self.session,
                change_type=operation.get("type", "insert"),
                operation_data=operation,
            )
        except ManuscriptSection.DoesNotExist:
            pass

    async def update_cursor_position(self, section, position):
        """Update cursor position in session."""
        if hasattr(self, "session"):
            self.session.cursor_position = {"section": section, "position": position}
            await self.session.asave(update_fields=["cursor_position", "last_activity"])

    async def is_section_locked(self, section):
        """Check if section is locked by another user."""
        return (
            await CollaborativeSession.objects.filter(
                manuscript=self.manuscript,
                is_active=True,
                locked_sections__contains=[section],
            )
            .exclude(user=self.user)
            .aexists()
        )

    async def lock_section(self, section):
        """Lock a section for current user."""
        if hasattr(self, "session") and section not in self.session.locked_sections:
            self.session.locked_sections.append(section)
            await self.session.asave(update_fields=["locked_sections"])

    async def unlock_section(self, section):
        """Unlock a section for current user."""
        if hasattr(self, "session") and section in self.session.locked_sections:
            self.session.locked_sections.remove(section)
            await self.session.asave(update_fields=["locked_sections"])

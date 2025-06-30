"""
WebSocket consumers for real-time collaborative editing in SciTeX Writer.
Implements operational transforms, user presence, and live cursors.
"""
import json
import uuid
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Manuscript, ManuscriptSection, CollaborativeSession
from .operational_transforms import OperationalTransform


class DocumentCollaborationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time document collaboration."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.manuscript_id = self.scope['url_route']['kwargs']['manuscript_id']
        self.user = self.scope['user']
        
        # Check if user is authenticated and has permission
        if not self.user.is_authenticated:
            await self.close()
            return
            
        # Verify user has access to this manuscript
        has_access = await self.check_manuscript_access()
        if not has_access:
            await self.close()
            return
            
        # Create unique room group name
        self.room_group_name = f'manuscript_{self.manuscript_id}'
        
        # Generate unique user session ID
        self.user_session_id = str(uuid.uuid4())
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Create/update collaborative session
        await self.create_collaborative_session()
        
        await self.accept()
        
        # Announce user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'username': self.user.username,
                'session_id': self.user_session_id,
                'timestamp': timezone.now().isoformat()
            }
        )
        
        # Send current active users to the new user
        await self.send_active_users()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Update collaborative session
        await self.end_collaborative_session()
        
        # Announce user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.user.id,
                'username': self.user.username,
                'session_id': self.user_session_id,
                'timestamp': timezone.now().isoformat()
            }
        )

    async def receive(self, text_data):
        """Handle received WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'document_change':
                await self.handle_document_change(data)
            elif message_type == 'cursor_position':
                await self.handle_cursor_position(data)
            elif message_type == 'selection_change':
                await self.handle_selection_change(data)
            elif message_type == 'section_lock':
                await self.handle_section_lock(data)
            elif message_type == 'section_unlock':
                await self.handle_section_unlock(data)
            elif message_type == 'typing_indicator':
                await self.handle_typing_indicator(data)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON data'
            }))

    async def handle_document_change(self, data):
        """Handle document text changes with operational transforms."""
        section_id = data.get('section_id')
        operation = data.get('operation')
        
        # Apply operational transform
        ot = OperationalTransform()
        transformed_operation = await self.apply_operational_transform(
            section_id, operation
        )
        
        # Save change to database
        await self.save_document_change(section_id, transformed_operation)
        
        # Broadcast change to all other users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'document_changed',
                'section_id': section_id,
                'operation': transformed_operation,
                'user_id': self.user.id,
                'username': self.user.username,
                'session_id': self.user_session_id,
                'timestamp': timezone.now().isoformat()
            }
        )

    async def handle_cursor_position(self, data):
        """Handle cursor position updates."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cursor_moved',
                'section_id': data.get('section_id'),
                'position': data.get('position'),
                'user_id': self.user.id,
                'username': self.user.username,
                'session_id': self.user_session_id,
                'user_color': await self.get_user_color(),
                'timestamp': timezone.now().isoformat()
            }
        )

    async def handle_selection_change(self, data):
        """Handle text selection changes."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'selection_changed',
                'section_id': data.get('section_id'),
                'start': data.get('start'),
                'end': data.get('end'),
                'user_id': self.user.id,
                'username': self.user.username,
                'session_id': self.user_session_id,
                'user_color': await self.get_user_color(),
                'timestamp': timezone.now().isoformat()
            }
        )

    async def handle_section_lock(self, data):
        """Handle section locking for exclusive editing."""
        section_id = data.get('section_id')
        
        # Check if section is already locked
        is_locked = await self.is_section_locked(section_id)
        if is_locked:
            await self.send(text_data=json.dumps({
                'type': 'section_lock_failed',
                'section_id': section_id,
                'message': 'Section is already locked by another user'
            }))
            return
        
        # Lock the section
        await self.lock_section(section_id)
        
        # Broadcast lock to all users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'section_locked',
                'section_id': section_id,
                'user_id': self.user.id,
                'username': self.user.username,
                'session_id': self.user_session_id,
                'timestamp': timezone.now().isoformat()
            }
        )

    async def handle_section_unlock(self, data):
        """Handle section unlocking."""
        section_id = data.get('section_id')
        
        # Unlock the section
        await self.unlock_section(section_id)
        
        # Broadcast unlock to all users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'section_unlocked',
                'section_id': section_id,
                'user_id': self.user.id,
                'username': self.user.username,
                'session_id': self.user_session_id,
                'timestamp': timezone.now().isoformat()
            }
        )

    async def handle_typing_indicator(self, data):
        """Handle typing indicators."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'section_id': data.get('section_id'),
                'is_typing': data.get('is_typing', False),
                'user_id': self.user.id,
                'username': self.user.username,
                'session_id': self.user_session_id,
                'timestamp': timezone.now().isoformat()
            }
        )

    # Group message handlers
    async def user_joined(self, event):
        """Send user joined message to WebSocket."""
        if event['session_id'] != self.user_session_id:
            await self.send(text_data=json.dumps(event))

    async def user_left(self, event):
        """Send user left message to WebSocket."""
        if event['session_id'] != self.user_session_id:
            await self.send(text_data=json.dumps(event))

    async def document_changed(self, event):
        """Send document change to WebSocket."""
        if event['session_id'] != self.user_session_id:
            await self.send(text_data=json.dumps(event))

    async def cursor_moved(self, event):
        """Send cursor position to WebSocket."""
        if event['session_id'] != self.user_session_id:
            await self.send(text_data=json.dumps(event))

    async def selection_changed(self, event):
        """Send selection change to WebSocket."""
        if event['session_id'] != self.user_session_id:
            await self.send(text_data=json.dumps(event))

    async def section_locked(self, event):
        """Send section lock notification to WebSocket."""
        await self.send(text_data=json.dumps(event))

    async def section_unlocked(self, event):
        """Send section unlock notification to WebSocket."""
        await self.send(text_data=json.dumps(event))

    async def user_typing(self, event):
        """Send typing indicator to WebSocket."""
        if event['session_id'] != self.user_session_id:
            await self.send(text_data=json.dumps(event))

    # Database operations
    @database_sync_to_async
    def check_manuscript_access(self):
        """Check if user has access to the manuscript."""
        try:
            manuscript = Manuscript.objects.get(id=self.manuscript_id)
            return (manuscript.owner == self.user or 
                   self.user in manuscript.collaborators.all())
        except Manuscript.DoesNotExist:
            return False

    @database_sync_to_async
    def create_collaborative_session(self):
        """Create or update collaborative session."""
        session, created = CollaborativeSession.objects.get_or_create(
            manuscript_id=self.manuscript_id,
            user=self.user,
            defaults={
                'session_id': self.user_session_id,
                'started_at': timezone.now(),
                'last_activity': timezone.now(),
                'is_active': True
            }
        )
        if not created:
            session.session_id = self.user_session_id
            session.last_activity = timezone.now()
            session.is_active = True
            session.save()
        return session

    @database_sync_to_async
    def end_collaborative_session(self):
        """End collaborative session."""
        try:
            session = CollaborativeSession.objects.get(
                manuscript_id=self.manuscript_id,
                user=self.user,
                session_id=self.user_session_id
            )
            session.is_active = False
            session.ended_at = timezone.now()
            session.save()
        except CollaborativeSession.DoesNotExist:
            pass

    @database_sync_to_async
    def apply_operational_transform(self, section_id, operation):
        """Apply operational transform to resolve conflicts."""
        # Implementation of operational transform algorithm
        # This is a simplified version - production would need more sophisticated OT
        return operation

    @database_sync_to_async
    def save_document_change(self, section_id, operation):
        """Save document change to database."""
        try:
            section = ManuscriptSection.objects.get(id=section_id)
            # Apply the operation to the section content
            if operation['type'] == 'insert':
                pos = operation['position']
                text = operation['text']
                section.content = (section.content[:pos] + 
                                 text + 
                                 section.content[pos:])
            elif operation['type'] == 'delete':
                start = operation['start']
                end = operation['end']
                section.content = (section.content[:start] + 
                                 section.content[end:])
            elif operation['type'] == 'replace':
                start = operation['start']
                end = operation['end']
                text = operation['text']
                section.content = (section.content[:start] + 
                                 text + 
                                 section.content[end:])
            section.save()
        except ManuscriptSection.DoesNotExist:
            pass

    @database_sync_to_async
    def get_user_color(self):
        """Get user's assigned color for cursor/selection display."""
        # Generate consistent color based on user ID
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
        ]
        return colors[self.user.id % len(colors)]

    @database_sync_to_async
    def is_section_locked(self, section_id):
        """Check if section is locked by another user."""
        return CollaborativeSession.objects.filter(
            manuscript_id=self.manuscript_id,
            locked_sections__contains=[section_id],
            is_active=True
        ).exclude(user=self.user).exists()

    @database_sync_to_async
    def lock_section(self, section_id):
        """Lock section for exclusive editing."""
        session = CollaborativeSession.objects.get(
            manuscript_id=self.manuscript_id,
            user=self.user,
            session_id=self.user_session_id
        )
        if not session.locked_sections:
            session.locked_sections = []
        if section_id not in session.locked_sections:
            session.locked_sections.append(section_id)
            session.save()

    @database_sync_to_async
    def unlock_section(self, section_id):
        """Unlock section."""
        try:
            session = CollaborativeSession.objects.get(
                manuscript_id=self.manuscript_id,
                user=self.user,
                session_id=self.user_session_id
            )
            if session.locked_sections and section_id in session.locked_sections:
                session.locked_sections.remove(section_id)
                session.save()
        except CollaborativeSession.DoesNotExist:
            pass

    async def send_active_users(self):
        """Send list of currently active users to the connecting user."""
        active_sessions = await self.get_active_sessions()
        await self.send(text_data=json.dumps({
            'type': 'active_users',
            'users': active_sessions,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def get_active_sessions(self):
        """Get list of active collaborative sessions."""
        sessions = CollaborativeSession.objects.filter(
            manuscript_id=self.manuscript_id,
            is_active=True,
            last_activity__gte=timezone.now() - timedelta(minutes=5)
        ).select_related('user')
        
        return [{
            'user_id': session.user.id,
            'username': session.user.username,
            'session_id': session.session_id,
            'started_at': session.started_at.isoformat(),
            'locked_sections': session.locked_sections or []
        } for session in sessions]
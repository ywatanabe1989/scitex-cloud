import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class DocumentCollaborationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time collaborative editing of documents
    Handles text synchronization, cursor positions, and user presence
    """
    
    async def connect(self):
        self.document_id = self.scope['url_route']['kwargs']['document_id']
        self.room_group_name = f'document_{self.document_id}'
        self.user = self.scope['user']
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Add user to active users list
        await self.add_user_to_room()
        
        # Send current document state to newly connected user
        await self.send_document_state()
        
        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'username': self.user.username,
                'message': f'{self.user.username} joined the document'
            }
        )
        
        logger.info(f"User {self.user.username} connected to document {self.document_id}")
    
    async def disconnect(self, close_code):
        # Remove user from active users list
        await self.remove_user_from_room()
        
        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.user.id,
                'username': self.user.username,
                'message': f'{self.user.username} left the document'
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"User {self.user.username} disconnected from document {self.document_id}")
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'text_change':
                await self.handle_text_change(data)
            elif message_type == 'cursor_position':
                await self.handle_cursor_position(data)
            elif message_type == 'selection_change':
                await self.handle_selection_change(data)
            elif message_type == 'request_document_state':
                await self.send_document_state()
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from WebSocket")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def handle_text_change(self, data):
        """Handle real-time text changes using operational transformation"""
        operation = data.get('operation', {})
        timestamp = data.get('timestamp')
        
        # Store the operation in cache for conflict resolution
        await self.store_operation(operation, timestamp)
        
        # Broadcast to all other users in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'text_changed',
                'operation': operation,
                'user_id': self.user.id,
                'username': self.user.username,
                'timestamp': timestamp
            }
        )
    
    async def handle_cursor_position(self, data):
        """Handle cursor position updates"""
        position = data.get('position', 0)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cursor_moved',
                'user_id': self.user.id,
                'username': self.user.username,
                'position': position
            }
        )
    
    async def handle_selection_change(self, data):
        """Handle text selection changes"""
        selection = data.get('selection', {})
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'selection_changed',
                'user_id': self.user.id,
                'username': self.user.username,
                'selection': selection
            }
        )
    
    async def text_changed(self, event):
        """Send text change to WebSocket"""
        if event['user_id'] != self.user.id:  # Don't send back to sender
            await self.send(text_data=json.dumps({
                'type': 'text_change',
                'operation': event['operation'],
                'user_id': event['user_id'],
                'username': event['username'],
                'timestamp': event['timestamp']
            }))
    
    async def cursor_moved(self, event):
        """Send cursor position to WebSocket"""
        if event['user_id'] != self.user.id:  # Don't send back to sender
            await self.send(text_data=json.dumps({
                'type': 'cursor_position',
                'user_id': event['user_id'],
                'username': event['username'],
                'position': event['position']
            }))
    
    async def selection_changed(self, event):
        """Send selection change to WebSocket"""
        if event['user_id'] != self.user.id:  # Don't send back to sender
            await self.send(text_data=json.dumps({
                'type': 'selection_change',
                'user_id': event['user_id'],
                'username': event['username'],
                'selection': event['selection']
            }))
    
    async def user_joined(self, event):
        """Send user joined notification"""
        if event['user_id'] != self.user.id:  # Don't send to the user who joined
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'username': event['username'],
                'message': event['message']
            }))
    
    async def user_left(self, event):
        """Send user left notification"""
        if event['user_id'] != self.user.id:  # Don't send to the user who left
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user_id': event['user_id'],
                'username': event['username'],
                'message': event['message']
            }))
    
    @database_sync_to_async
    def add_user_to_room(self):
        """Add user to the active users list for this document"""
        cache_key = f"document_users_{self.document_id}"
        active_users = cache.get(cache_key, {})
        active_users[str(self.user.id)] = {
            'username': self.user.username,
            'channel_name': self.channel_name
        }
        cache.set(cache_key, active_users, timeout=3600)  # 1 hour timeout
    
    @database_sync_to_async
    def remove_user_from_room(self):
        """Remove user from the active users list for this document"""
        cache_key = f"document_users_{self.document_id}"
        active_users = cache.get(cache_key, {})
        active_users.pop(str(self.user.id), None)
        cache.set(cache_key, active_users, timeout=3600)
    
    @database_sync_to_async
    def get_document_content(self):
        """Get current document content from database/cache"""
        cache_key = f"document_content_{self.document_id}"
        content = cache.get(cache_key)
        if content is None:
            # In production, load from database
            content = {
                'text': '',
                'version': 1,
                'last_modified': None
            }
            cache.set(cache_key, content, timeout=3600)
        return content
    
    @database_sync_to_async
    def store_operation(self, operation, timestamp):
        """Store operation for conflict resolution"""
        cache_key = f"document_operations_{self.document_id}"
        operations = cache.get(cache_key, [])
        operations.append({
            'operation': operation,
            'user_id': self.user.id,
            'timestamp': timestamp
        })
        # Keep only last 100 operations
        operations = operations[-100:]
        cache.set(cache_key, operations, timeout=3600)
    
    async def send_document_state(self):
        """Send current document state to the client"""
        content = await self.get_document_content()
        active_users = await self.get_active_users()
        
        await self.send(text_data=json.dumps({
            'type': 'document_state',
            'content': content,
            'active_users': active_users
        }))
    
    @database_sync_to_async
    def get_active_users(self):
        """Get list of currently active users in this document"""
        cache_key = f"document_users_{self.document_id}"
        active_users = cache.get(cache_key, {})
        return [user_info for user_info in active_users.values()]
"""
Socket.io Server for Frontend Integration

This module provides Socket.io compatibility for the frontend
while maintaining the existing WebSocket infrastructure.
"""

import socketio
import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException
from ..dependencies import decode_access_token
from .websocket_manager import websocket_manager
from .analytics_engine import AnalyticsEngine
from ..database import get_db

logger = logging.getLogger(__name__)

# Create Socket.io server with CORS support
sio = socketio.AsyncServer(
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001"
    ],
    logger=True,
    engineio_logger=True,
    async_mode='asgi'
)

# Store user sessions
user_sessions: Dict[str, Dict[str, Any]] = {}

@sio.event
async def connect(sid, environ, auth):
    """Handle Socket.io connection"""
    try:
        # Get query parameters
        query_string = environ.get('QUERY_STRING', '')
        params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
        
        # Extract and verify token
        token = params.get('token')
        mall_id = params.get('mall_id')
        
        if not token:
            logger.error(f"Socket.io connection rejected: No token provided")
            await sio.disconnect(sid)
            return False
        
        try:
            # Decode JWT token
            payload = decode_access_token(token)
            user_id = payload.get('user_id')
            
            if not user_id:
                logger.error(f"Socket.io connection rejected: Invalid token payload")
                await sio.disconnect(sid)
                return False
            
            # Store session info
            user_sessions[sid] = {
                'user_id': user_id,
                'mall_id': int(mall_id) if mall_id else None,
                'connected_at': datetime.utcnow().isoformat(),
                'rooms': set()
            }
            
            logger.info(f"Socket.io connected: sid={sid}, user_id={user_id}, mall_id={mall_id}")
            
            # Auto-join mall room if mall_id provided
            if mall_id:
                room = f"mall_{mall_id}"
                await sio.enter_room(sid, room)
                user_sessions[sid]['rooms'].add(room)
                
                # Send initial analytics data
                try:
                    db = next(get_db())
                    analytics_engine = AnalyticsEngine(db)
                    initial_data = analytics_engine.get_frontend_compatible_analytics(int(mall_id))
                    
                    await sio.emit('analytics_update', {
                        'type': 'analytics_update',
                        'data': initial_data
                    }, room=sid)
                    
                    db.close()
                except Exception as e:
                    logger.error(f"Error sending initial data: {str(e)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            await sio.disconnect(sid)
            return False
            
    except Exception as e:
        logger.error(f"Socket.io connection error: {str(e)}")
        await sio.disconnect(sid)
        return False

@sio.event
async def disconnect(sid):
    """Handle Socket.io disconnection"""
    try:
        if sid in user_sessions:
            session = user_sessions[sid]
            logger.info(f"Socket.io disconnected: sid={sid}, user_id={session.get('user_id')}")
            
            # Leave all rooms
            for room in session.get('rooms', set()):
                await sio.leave_room(sid, room)
            
            # Remove session
            del user_sessions[sid]
        
    except Exception as e:
        logger.error(f"Error handling disconnect: {str(e)}")

@sio.event
async def join_room(sid, data):
    """Handle room join requests"""
    try:
        if sid not in user_sessions:
            return {'success': False, 'error': 'Session not found'}
        
        room = data.get('room')
        if not room:
            return {'success': False, 'error': 'Room not specified'}
        
        await sio.enter_room(sid, room)
        user_sessions[sid]['rooms'].add(room)
        
        logger.info(f"Socket.io joined room: sid={sid}, room={room}")
        
        # Send confirmation
        await sio.emit('room_joined', {
            'room': room,
            'timestamp': datetime.utcnow().isoformat()
        }, room=sid)
        
        return {'success': True, 'room': room}
        
    except Exception as e:
        logger.error(f"Error joining room: {str(e)}")
        return {'success': False, 'error': str(e)}

@sio.event
async def leave_room(sid, data):
    """Handle room leave requests"""
    try:
        if sid not in user_sessions:
            return {'success': False, 'error': 'Session not found'}
        
        room = data.get('room')
        if not room:
            return {'success': False, 'error': 'Room not specified'}
        
        await sio.leave_room(sid, room)
        user_sessions[sid]['rooms'].discard(room)
        
        logger.info(f"Socket.io left room: sid={sid}, room={room}")
        
        return {'success': True, 'room': room}
        
    except Exception as e:
        logger.error(f"Error leaving room: {str(e)}")
        return {'success': False, 'error': str(e)}

@sio.event
async def get_analytics(sid, data):
    """Handle analytics data requests"""
    try:
        if sid not in user_sessions:
            await sio.emit('error', {'message': 'Session not found'}, room=sid)
            return
        
        mall_id = data.get('mall_id') or user_sessions[sid].get('mall_id')
        if not mall_id:
            await sio.emit('error', {'message': 'Mall ID not provided'}, room=sid)
            return
        
        # Get analytics data
        db = next(get_db())
        analytics_engine = AnalyticsEngine(db)
        analytics_data = analytics_engine.get_frontend_compatible_analytics(mall_id)
        
        # Send analytics update
        await sio.emit('analytics_update', {
            'type': 'analytics_update',
            'data': analytics_data
        }, room=sid)
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        await sio.emit('error', {'message': str(e)}, room=sid)

@sio.event
async def get_realtime_status(sid, data):
    """Handle real-time status requests"""
    try:
        if sid not in user_sessions:
            await sio.emit('error', {'message': 'Session not found'}, room=sid)
            return
        
        mall_id = data.get('mall_id') or user_sessions[sid].get('mall_id')
        if not mall_id:
            await sio.emit('error', {'message': 'Mall ID not provided'}, room=sid)
            return
        
        # Get real-time status
        db = next(get_db())
        analytics_engine = AnalyticsEngine(db)
        status_data = analytics_engine.get_realtime_status(mall_id)
        
        # Send status update
        await sio.emit('status_update', {
            'type': 'status_update', 
            'data': status_data
        }, room=sid)
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        await sio.emit('error', {'message': str(e)}, room=sid)

# Broadcasting functions for integration with existing WebSocket manager
async def broadcast_analytics_to_socketio(mall_id: int, analytics_data: Dict[str, Any]):
    """Broadcast analytics data to Socket.io clients"""
    try:
        room = f"mall_{mall_id}"
        await sio.emit('analytics_update', {
            'type': 'analytics_update',
            'data': analytics_data
        }, room=room)
        
        logger.debug(f"Broadcasted analytics to Socket.io room: {room}")
        
    except Exception as e:
        logger.error(f"Error broadcasting to Socket.io: {str(e)}")

async def broadcast_detections_to_socketio(camera_id: int, detection_data: Dict[str, Any]):
    """Broadcast detection data to Socket.io clients"""
    try:
        room = f"camera_{camera_id}"
        await sio.emit('detection_update', {
            'type': 'detection_update',
            'data': detection_data
        }, room=room)
        
        logger.debug(f"Broadcasted detections to Socket.io room: {room}")
        
    except Exception as e:
        logger.error(f"Error broadcasting detections to Socket.io: {str(e)}")

async def broadcast_camera_status_to_socketio(camera_id: int, mall_id: int, status: str):
    """Broadcast camera status to Socket.io clients"""
    try:
        room = f"mall_{mall_id}"
        await sio.emit('camera_status', {
            'type': 'camera_status',
            'data': {
                'cameraId': camera_id,
                'status': status,
                'timestamp': datetime.utcnow().isoformat()
            }
        }, room=room)
        
        logger.debug(f"Broadcasted camera status to Socket.io room: {room}")
        
    except Exception as e:
        logger.error(f"Error broadcasting camera status to Socket.io: {str(e)}")

def get_socketio_stats():
    """Get Socket.io server statistics"""
    return {
        'connected_clients': len(user_sessions),
        'active_rooms': len(set().union(*[session['rooms'] for session in user_sessions.values()])),
        'sessions': {
            sid: {
                'user_id': session['user_id'],
                'mall_id': session['mall_id'],
                'connected_at': session['connected_at'],
                'rooms': list(session['rooms'])
            }
            for sid, session in user_sessions.items()
        }
    }

# Background task to send periodic analytics updates
async def socketio_analytics_broadcaster():
    """Background task to broadcast analytics updates periodically"""
    while True:
        try:
            # Get all active malls from sessions
            active_malls = set()
            for session in user_sessions.values():
                if session.get('mall_id'):
                    active_malls.add(session['mall_id'])
            
            # Broadcast analytics for each active mall
            for mall_id in active_malls:
                try:
                    db = next(get_db())
                    analytics_engine = AnalyticsEngine(db)
                    analytics_data = analytics_engine.get_frontend_compatible_analytics(mall_id)
                    
                    await broadcast_analytics_to_socketio(mall_id, analytics_data)
                    
                    db.close()
                    
                except Exception as e:
                    logger.error(f"Error broadcasting analytics for mall {mall_id}: {str(e)}")
            
            # Wait 5 seconds before next broadcast
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Error in Socket.io broadcaster: {str(e)}")
            await asyncio.sleep(5)

logger.info("Socket.io server configured and ready") 
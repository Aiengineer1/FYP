"""
Simplified Socket.io Server Integration

This provides a cleaner Socket.io implementation that's compatible
with the frontend while avoiding version conflicts.
"""

import socketio
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI
from ..dependencies import decode_access_token
from .analytics_engine import AnalyticsEngine
from ..database import get_db

logger = logging.getLogger(__name__)

# Create a simple Socket.io server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",  # Simplified CORS for development
    logger=False,
    engineio_logger=False
)

# Store user sessions
user_sessions = {}

@sio.event
async def connect(sid, environ, auth=None):
    """Handle Socket.io connection with simplified authentication"""
    try:
        logger.info(f"Socket.io connection attempt: sid={sid}")
        
        # Get query string from environ
        query_string = environ.get('QUERY_STRING', '')
        params = {}
        
        # Parse query parameters manually
        if query_string:
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
        
        token = params.get('token')
        mall_id = params.get('mall_id')
        
        logger.info(f"Socket.io parsed params: mall_id={mall_id}, has_token={bool(token)}")
        
        if not token:
            logger.warning(f"Socket.io connection rejected: No token provided for sid={sid}")
            return False
        
        try:
            # Verify token
            payload = decode_access_token(token)
            user_id = payload.get('user_id')
            
            if not user_id:
                logger.warning(f"Socket.io connection rejected: Invalid token for sid={sid}")
                return False
            
            # Store session
            user_sessions[sid] = {
                'user_id': user_id,
                'mall_id': int(mall_id) if mall_id else None,
                'connected_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Socket.io connected successfully: sid={sid}, user_id={user_id}")
            
            # Join mall room if mall_id provided
            if mall_id:
                room = f"mall_{mall_id}"
                await sio.enter_room(sid, room)
                logger.info(f"Socket.io joined room: sid={sid}, room={room}")
                
                # Send initial analytics data
                try:
                    db = next(get_db())
                    analytics_engine = AnalyticsEngine(db)
                    analytics_data = analytics_engine.get_frontend_compatible_analytics(int(mall_id))
                    
                    await sio.emit('analytics_update', {
                        'type': 'analytics_update',
                        'data': analytics_data
                    }, room=sid)
                    
                    db.close()
                    logger.info(f"Sent initial analytics to sid={sid}")
                    
                except Exception as e:
                    logger.error(f"Error sending initial analytics: {str(e)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Token verification failed for sid={sid}: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Socket.io connection error for sid={sid}: {str(e)}")
        return False

@sio.event
async def disconnect(sid):
    """Handle Socket.io disconnection"""
    try:
        if sid in user_sessions:
            session = user_sessions[sid]
            logger.info(f"Socket.io disconnected: sid={sid}, user_id={session.get('user_id')}")
            del user_sessions[sid]
        else:
            logger.info(f"Socket.io disconnected: sid={sid} (no session found)")
    except Exception as e:
        logger.error(f"Error handling disconnect for sid={sid}: {str(e)}")

@sio.event
async def get_analytics(sid, data):
    """Handle analytics data requests"""
    try:
        if sid not in user_sessions:
            await sio.emit('error', {'message': 'Session not found'}, room=sid)
            return
        
        session = user_sessions[sid]
        mall_id = data.get('mall_id') or session.get('mall_id')
        
        if not mall_id:
            await sio.emit('error', {'message': 'Mall ID required'}, room=sid)
            return
        
        # Get and send analytics data
        db = next(get_db())
        analytics_engine = AnalyticsEngine(db)
        analytics_data = analytics_engine.get_frontend_compatible_analytics(mall_id)
        
        await sio.emit('analytics_update', {
            'type': 'analytics_update',
            'data': analytics_data
        }, room=sid)
        
        db.close()
        logger.info(f"Sent analytics data to sid={sid} for mall={mall_id}")
        
    except Exception as e:
        logger.error(f"Error getting analytics for sid={sid}: {str(e)}")
        await sio.emit('error', {'message': str(e)}, room=sid)

# Background task for periodic updates
async def analytics_broadcaster():
    """Send periodic analytics updates"""
    while True:
        try:
            # Get all active mall IDs from sessions
            active_malls = set()
            for session in user_sessions.values():
                if session.get('mall_id'):
                    active_malls.add(session['mall_id'])
            
            # Send updates for each active mall
            for mall_id in active_malls:
                try:
                    db = next(get_db())
                    analytics_engine = AnalyticsEngine(db)
                    analytics_data = analytics_engine.get_frontend_compatible_analytics(mall_id)
                    
                    room = f"mall_{mall_id}"
                    await sio.emit('analytics_update', {
                        'type': 'analytics_update',
                        'data': analytics_data
                    }, room=room)
                    
                    db.close()
                    logger.debug(f"Broadcasted analytics to mall_{mall_id}")
                    
                except Exception as e:
                    logger.error(f"Error broadcasting analytics for mall {mall_id}: {str(e)}")
            
            # Wait 5 seconds before next update
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Error in analytics broadcaster: {str(e)}")
            await asyncio.sleep(5)

def get_socket_app(fastapi_app: FastAPI):
    """Create and return the Socket.io ASGI app"""
    return socketio.ASGIApp(sio, fastapi_app)

logger.info("Simple Socket.io server configured") 
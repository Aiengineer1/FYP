"""
WebSocket Manager for Real-time Communication

This module handles:
- WebSocket connection management
- Real-time data broadcasting
- Room-based subscriptions (mall, camera)
- Connection cleanup and error handling
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict

logger = logging.getLogger(__name__)

class WebSocketConnection:
    """Represents a WebSocket connection with metadata"""
    
    def __init__(self, websocket: WebSocket, user_id: Optional[int] = None):
        self.websocket = websocket
        self.user_id = user_id
        self.connected_at = datetime.utcnow()
        self.subscriptions: Set[str] = set()
        self.last_ping = datetime.utcnow()
    
    async def send_message(self, message: Dict[str, Any]):
        """Send a message to this connection"""
        try:
            await self.websocket.send_text(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {str(e)}")
            return False
    
    def add_subscription(self, room: str):
        """Add a room subscription"""
        self.subscriptions.add(room)
    
    def remove_subscription(self, room: str):
        """Remove a room subscription"""
        self.subscriptions.discard(room)
    
    def is_subscribed_to(self, room: str) -> bool:
        """Check if subscribed to a room"""
        return room in self.subscriptions

class WebSocketManager:
    """Manager for WebSocket connections and real-time broadcasting"""
    
    def __init__(self):
        # Connection storage
        self.connections: Dict[WebSocket, WebSocketConnection] = {}
        
        # Room-based subscriptions
        self.room_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        
        # Performance tracking
        self.message_count = 0
        self.failed_sends = 0
        
        logger.info("WebSocket manager initialized")
    
    async def connect(self, websocket: WebSocket, user_id: Optional[int] = None) -> WebSocketConnection:
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        connection = WebSocketConnection(websocket, user_id)
        self.connections[websocket] = connection
        
        logger.info(f"WebSocket connected: user_id={user_id}, total_connections={len(self.connections)}")
        
        return connection
    
    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        if websocket not in self.connections:
            return
        
        connection = self.connections[websocket]
        
        # Remove from all room subscriptions
        for room in list(connection.subscriptions):
            await self.leave_room(websocket, room)
        
        # Remove connection
        del self.connections[websocket]
        
        logger.info(f"WebSocket disconnected: user_id={connection.user_id}, remaining_connections={len(self.connections)}")
    
    async def join_room(self, websocket: WebSocket, room: str):
        """Subscribe a connection to a room"""
        if websocket not in self.connections:
            logger.warning("Attempted to join room for non-existent connection")
            return
        
        connection = self.connections[websocket]
        connection.add_subscription(room)
        self.room_connections[room].add(websocket)
        
        logger.debug(f"Connection joined room '{room}': user_id={connection.user_id}")
        
        # Send confirmation
        await connection.send_message({
            "type": "room_joined",
            "room": room,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def leave_room(self, websocket: WebSocket, room: str):
        """Unsubscribe a connection from a room"""
        if websocket not in self.connections:
            return
        
        connection = self.connections[websocket]
        connection.remove_subscription(room)
        self.room_connections[room].discard(websocket)
        
        # Clean up empty rooms
        if not self.room_connections[room]:
            del self.room_connections[room]
        
        logger.debug(f"Connection left room '{room}': user_id={connection.user_id}")
    
    async def broadcast_to_room(self, room: str, message: Dict[str, Any]):
        """Broadcast a message to all connections in a room"""
        if room not in self.room_connections:
            logger.debug(f"No connections in room '{room}'")
            return
        
        connections = list(self.room_connections[room])
        if not connections:
            return
        
        # Add metadata
        message.update({
            "room": room,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Send to all connections in room
        failed_connections = []
        success_count = 0
        
        for websocket in connections:
            if websocket in self.connections:
                connection = self.connections[websocket]
                success = await connection.send_message(message)
                
                if success:
                    success_count += 1
                    self.message_count += 1
                else:
                    failed_connections.append(websocket)
                    self.failed_sends += 1
        
        # Clean up failed connections
        for websocket in failed_connections:
            await self.disconnect(websocket)
        
        logger.debug(f"Broadcasted to room '{room}': {success_count} successful, {len(failed_connections)} failed")
    
    async def broadcast_to_mall(self, mall_id: int, analytics_data: Dict[str, Any]):
        """Broadcast analytics data to all connections subscribed to a mall"""
        room = f"mall_{mall_id}"
        
        # Format data to match frontend expectations exactly
        formatted_data = {
            "mallId": mall_id,
            "activeVisitors": analytics_data.get("active_visitors", 0),
            "totalVisitors": analytics_data.get("total_visitors", 0),
            "averageDwellTime": analytics_data.get("average_dwell_time", 0),
            "peakHours": [
                {"hour": item["hour"], "visitors": item["visitors"]} 
                for item in analytics_data.get("hourly_traffic", [])
            ],
            "popularSections": [
                {"name": item["zone"], "visitors": item["count"], "percentage": item["percentage"]} 
                for item in analytics_data.get("zone_popularity", [])
            ],
            "timestamp": analytics_data.get("timestamp", datetime.utcnow().isoformat())
        }
        
        message = {
            "type": "analytics_update",
            "data": formatted_data
        }
        
        await self.broadcast_to_room(room, message)
    
    async def broadcast_to_camera(self, camera_id: int, detection_data: Dict[str, Any]):
        """Broadcast detection data to all connections subscribed to a camera"""
        room = f"camera_{camera_id}"
        
        # Format detection data to match frontend expectations
        formatted_detections = []
        for detection in detection_data.get("detections", []):
            formatted_detections.append({
                "person_id": detection.get("person_id"),
                "bbox": detection.get("bbox", [0, 0, 0, 0]),  # [x, y, width, height]
                "confidence": detection.get("confidence", 0.0),
                "age": detection.get("age", 0),
                "gender": "Male" if detection.get("gender") == "male" else "Female",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        formatted_data = {
            "cameraId": camera_id,
            "detections": formatted_detections
        }
        
        message = {
            "type": "detection_update",
            "data": formatted_data
        }
        
        await self.broadcast_to_room(room, message)
    
    async def broadcast_camera_status(self, camera_id: int, mall_id: int, status: str):
        """Broadcast camera status changes to mall subscribers"""
        room = f"mall_{mall_id}"
        
        message = {
            "type": "camera_status",
            "data": {
                "cameraId": camera_id,
                "status": status,  # "online" | "offline"
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        await self.broadcast_to_room(room, message)
    
    async def send_to_user(self, user_id: int, message: Dict[str, Any]):
        """Send a message to a specific user's connections"""
        user_connections = [
            conn for conn in self.connections.values()
            if conn.user_id == user_id
        ]
        
        if not user_connections:
            logger.debug(f"No connections found for user {user_id}")
            return
        
        # Add metadata
        message.update({
            "target_user": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        for connection in user_connections:
            await connection.send_message(message)
            self.message_count += 1
        
        logger.debug(f"Sent message to user {user_id}: {len(user_connections)} connections")
    
    async def handle_client_message(self, websocket: WebSocket, message: str):
        """Handle incoming message from client"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "join_room":
                room = data.get("room")
                if room:
                    await self.join_room(websocket, room)
            
            elif message_type == "leave_room":
                room = data.get("room")
                if room:
                    await self.leave_room(websocket, room)
            
            elif message_type == "ping":
                # Update last ping time
                if websocket in self.connections:
                    self.connections[websocket].last_ping = datetime.utcnow()
                
                # Send pong response
                await self.connections[websocket].send_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from WebSocket: {message}")
        except Exception as e:
            logger.error(f"Error handling client message: {str(e)}")
    
    async def cleanup_stale_connections(self):
        """Remove connections that haven't pinged recently"""
        stale_threshold = datetime.utcnow().timestamp() - 300  # 5 minutes
        stale_connections = []
        
        for websocket, connection in self.connections.items():
            if connection.last_ping.timestamp() < stale_threshold:
                stale_connections.append(websocket)
        
        for websocket in stale_connections:
            logger.info(f"Cleaning up stale connection: user_id={self.connections[websocket].user_id}")
            await self.disconnect(websocket)
        
        if stale_connections:
            logger.info(f"Cleaned up {len(stale_connections)} stale connections")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics"""
        room_stats = {
            room: len(connections) 
            for room, connections in self.room_connections.items()
        }
        
        return {
            "total_connections": len(self.connections),
            "total_rooms": len(self.room_connections),
            "room_statistics": room_stats,
            "messages_sent": self.message_count,
            "failed_sends": self.failed_sends,
            "success_rate": (
                (self.message_count / (self.message_count + self.failed_sends)) * 100
                if (self.message_count + self.failed_sends) > 0 else 100
            )
        }
    
    async def broadcast_system_message(self, message: str, level: str = "info"):
        """Broadcast a system message to all connections"""
        system_message = {
            "type": "system_message",
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all connections
        for connection in self.connections.values():
            await connection.send_message(system_message)
            self.message_count += 1

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

# Background task for connection cleanup
async def websocket_cleanup_task():
    """Background task to clean up stale connections"""
    while True:
        try:
            await websocket_manager.cleanup_stale_connections()
            await asyncio.sleep(60)  # Run every minute
        except Exception as e:
            logger.error(f"Error in WebSocket cleanup task: {str(e)}")
            await asyncio.sleep(60) 
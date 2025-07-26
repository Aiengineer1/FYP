"""
Communication module for AI solutions
Contains WebSocket and SocketIO functionality
"""

from app.ai_solutions.communication.websocket_manager import websocket_manager
from app.ai_solutions.communication.socketio_server import socketio_analytics_broadcaster
from app.ai_solutions.communication.simple_socketio import *

__all__ = ['websocket_manager', 'socketio_analytics_broadcaster'] 
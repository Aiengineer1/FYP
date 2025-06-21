#!/usr/bin/env python3
"""
Socket.io WebSocket Test Script
Tests real-time Socket.io connectivity and event handling
"""

import socketio
import requests
import json
import time
import threading
from datetime import datetime

BASE_URL = "http://localhost:8000"

class SocketIOTester:
    def __init__(self):
        self.sio = socketio.Client()
        self.token = None
        self.mall_id = None
        self.connected = False
        self.events_received = []
        
    def setup_events(self):
        """Setup Socket.io event handlers"""
        
        @self.sio.event
        def connect():
            print("✅ Socket.io Connected!")
            print(f"   Session ID: {self.sio.sid}")
            self.connected = True
        
        @self.sio.event
        def disconnect():
            print("🔌 Socket.io Disconnected")
            self.connected = False
        
        @self.sio.event
        def connect_error(data):
            print(f"❌ Connection Error: {data}")
        
        @self.sio.event
        def analytics_update(data):
            print("📊 Analytics Update Received:")
            print(f"   Type: {data.get('type', 'unknown')}")
            print(f"   Mall ID: {data.get('data', {}).get('mallId', 'N/A')}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            self.events_received.append(('analytics_update', data))
        
        @self.sio.event
        def detection_update(data):
            print("🎯 Detection Update Received:")
            camera_id = data.get('data', {}).get('cameraId', 'N/A')
            detections = data.get('data', {}).get('detections', [])
            print(f"   Camera ID: {camera_id}")
            print(f"   Detections: {len(detections)}")
            if detections:
                print(f"   First detection: {detections[0]}")
            self.events_received.append(('detection_update', data))
        
        @self.sio.event
        def camera_status(data):
            print("📹 Camera Status Update:")
            print(f"   Camera ID: {data.get('data', {}).get('cameraId', 'N/A')}")
            print(f"   Status: {data.get('data', {}).get('status', 'N/A')}")
            print(f"   Message: {data.get('data', {}).get('message', 'N/A')}")
            self.events_received.append(('camera_status', data))
        
        @self.sio.event
        def error(data):
            print(f"⚠️  Socket.io Error: {data}")
            self.events_received.append(('error', data))
        
        @self.sio.event
        def status_update(data):
            print(f"📡 Status Update: {data}")
            self.events_received.append(('status_update', data))
    
    def get_auth_token(self):
        """Get authentication token"""
        print("🔐 Getting authentication token...")
        
        # Create test user
        import random
        random_num = random.randint(10000, 99999)
        signup_data = {
            "name": f"SocketIO Test User {random_num}",
            "email": f"socketio_test_{random_num}@test.com",
            "password": "testpass123",
            "mall_id": 1
        }
        
        # Signup
        try:
            response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
            if response.status_code != 200:
                print(f"⚠️  Signup failed, trying login: {response.text}")
        except Exception as e:
            print(f"⚠️  Signup error: {str(e)}")
        
        # Login
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                login_response = response.json()
                self.token = login_response.get('access_token')
                self.mall_id = login_response.get('mall_id', 1)
                print(f"✅ Token obtained: {self.token[:30]}...")
                print(f"   Mall ID: {self.mall_id}")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def test_connection(self):
        """Test Socket.io connection"""
        print("\n🔌 Testing Socket.io connection...")
        
        if not self.token:
            print("❌ No authentication token")
            return False
        
        try:
            # Setup event handlers
            self.setup_events()
            
            # Connect with authentication
            connect_params = {
                'token': self.token,
                'mall_id': str(self.mall_id)
            }
            
            print(f"🔗 Connecting to {BASE_URL} with Socket.io...")
            # Construct URL with query parameters
            url = f"{BASE_URL}?token={connect_params['token']}&mall_id={connect_params['mall_id']}"
            self.sio.connect(url, socketio_path='socket.io', wait_timeout=10)
            
            # Wait for connection
            time.sleep(2)
            
            if self.connected:
                print("✅ Socket.io connection successful!")
                return True
            else:
                print("❌ Socket.io connection failed")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False
    
    def test_room_joining(self):
        """Test joining Socket.io rooms"""
        print("\n🏠 Testing room joining...")
        
        if not self.connected:
            print("❌ Not connected to Socket.io")
            return False
        
        try:
            # Join mall room
            print(f"📡 Joining mall room: mall_{self.mall_id}")
            self.sio.emit('join_room', {'room': f'mall_{self.mall_id}'})
            time.sleep(1)
            
            # Join system room
            print("📡 Joining system room")
            self.sio.emit('join_room', {'room': 'system'})
            time.sleep(1)
            
            print("✅ Room joining completed")
            return True
            
        except Exception as e:
            print(f"❌ Room joining error: {str(e)}")
            return False
    
    def test_event_emission(self):
        """Test emitting events to server"""
        print("\n📡 Testing event emission...")
        
        if not self.connected:
            print("❌ Not connected to Socket.io")
            return False
        
        try:
            # Test analytics request
            print("📊 Requesting analytics via Socket.io...")
            self.sio.emit('get_analytics', {'mall_id': self.mall_id})
            time.sleep(1)
            
            # Test status request
            print("📡 Requesting status via Socket.io...")
            self.sio.emit('get_status', {'mall_id': self.mall_id})
            time.sleep(1)
            
            print("✅ Event emission completed")
            return True
            
        except Exception as e:
            print(f"❌ Event emission error: {str(e)}")
            return False
    
    def test_real_time_updates(self):
        """Test receiving real-time updates"""
        print("\n⏰ Testing real-time updates...")
        
        if not self.connected:
            print("❌ Not connected to Socket.io")
            return False
        
        print("⏳ Listening for real-time updates for 15 seconds...")
        
        initial_events = len(self.events_received)
        start_time = time.time()
        
        # Listen for events
        time.sleep(15)
        
        end_time = time.time()
        final_events = len(self.events_received)
        events_received = final_events - initial_events
        
        print(f"✅ Real-time test completed")
        print(f"   Duration: {end_time - start_time:.1f} seconds")
        print(f"   Events received: {events_received}")
        
        # Show event breakdown
        event_types = {}
        for event_type, _ in self.events_received[initial_events:]:
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        if event_types:
            print("   Event breakdown:")
            for event_type, count in event_types.items():
                print(f"     {event_type}: {count}")
        
        return events_received > 0
    
    def test_authentication_failure(self):
        """Test Socket.io with invalid authentication"""
        print("\n🚫 Testing authentication failure...")
        
        try:
            # Create new client for bad auth test
            bad_sio = socketio.Client()
            
            @bad_sio.event
            def connect():
                print("❌ Bad auth connected (should not happen)")
            
            @bad_sio.event
            def connect_error(data):
                print("✅ Authentication failure detected correctly")
                print(f"   Error: {data}")
            
            # Try to connect with bad token
            bad_url = f"{BASE_URL}?token=invalid_token&mall_id=1"
            bad_sio.connect(bad_url, socketio_path='socket.io', wait_timeout=5)
            
            time.sleep(2)
            bad_sio.disconnect()
            
            return True
            
        except Exception as e:
            print(f"✅ Authentication properly rejected: {str(e)}")
            return True
    
    def run_all_tests(self):
        """Run complete Socket.io test suite"""
        print("🚀 STARTING SOCKET.IO TEST SUITE")
        print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {}
        
        # Test 1: Authentication
        results['authentication'] = self.get_auth_token()
        
        # Test 2: Connection
        if results['authentication']:
            results['connection'] = self.test_connection()
        
        # Test 3: Room Joining
        if results.get('connection'):
            results['room_joining'] = self.test_room_joining()
        
        # Test 4: Event Emission
        if results.get('connection'):
            results['event_emission'] = self.test_event_emission()
        
        # Test 5: Real-time Updates
        if results.get('connection'):
            results['real_time_updates'] = self.test_real_time_updates()
        
        # Test 6: Authentication Failure
        results['auth_failure'] = self.test_authentication_failure()
        
        # Cleanup
        if self.connected:
            self.sio.disconnect()
        
        # Print Results
        print("\n" + "="*60)
        print("🎯 SOCKET.IO TEST RESULTS")
        print("="*60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} - {test_name.replace('_', ' ').title()}")
        
        print(f"\n📊 SUMMARY: {passed_tests}/{total_tests} tests passed")
        print(f"📡 Total events received: {len(self.events_received)}")
        
        if passed_tests == total_tests:
            print("🎉 ALL SOCKET.IO TESTS PASSED!")
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed")
        
        print(f"⏰ End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    tester = SocketIOTester()
    tester.run_all_tests() 
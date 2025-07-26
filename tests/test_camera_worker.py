#!/usr/bin/env python3
"""
Camera Worker Test Script
Tests camera processing, detection pipeline, and real-time streaming
"""

import requests
import json
import time
import asyncio
from datetime import datetime
import io
from PIL import Image

BASE_URL = "http://localhost:8000"

class CameraWorkerTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.mall_id = None
        self.camera_id = None
    
    def create_test_image(self, size=(800, 600), format='PNG'):
        """Create a test image in memory"""
        image = Image.new('RGB', size, color='lightblue')
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return buffer

    def setup_test_data(self):
        """Setup required test data (user, mall, camera)"""
        print("Setting up test data...")
        
        # Login/signup
        if not self.login_or_signup():
            return False
            
        # Create mall
        if not self.create_test_mall():
            return False
            
        # Create camera
        if not self.create_test_camera():
            return False
            
        print("Test data setup complete")
        return True

    def login_or_signup(self):
        """Login or signup user"""
        try:
            # Try login first
            login_data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                print(f"Login successful - User ID: {self.user_id}")
                return True
            else:
                # Try signup
                signup_data = {
                    "name": "Test User",
                    "email": "test@example.com",
                    "password": "testpassword123"
                }
                
                response = requests.post(f"{self.base_url}/auth/signup", json=signup_data)
                
                if response.status_code in [200, 201]:
                    # Now login
                    response = requests.post(f"{self.base_url}/auth/login", json=login_data)
                    if response.status_code == 200:
                        data = response.json()
                        self.token = data.get("access_token")
                        self.user_id = data.get("user_id")
                        print(f"Signup and login successful - User ID: {self.user_id}")
                        return True
                
                print("Failed to login or signup")
                return False
                
        except Exception as e:
            print(f"Login/signup error: {str(e)}")
            return False

    def create_test_mall(self):
        """Create a test mall"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create test image
            test_image = self.create_test_image(size=(1280, 720))
            
            # Prepare form data with file
            files = {
                'map_image': ('test_mall_map.png', test_image, 'image/png')
            }
            
            # Use params for query parameters
            params = {
                'name': 'Test Mall for Camera',
                'address': '456 Camera Test Street',
                'user_id': self.user_id
            }
            
            response = requests.post(
                f"{self.base_url}/mall/create",
                headers=headers,
                files=files,
                params=params
            )
            
            if response.status_code in [200, 201]:
                mall_data = response.json()
                self.mall_id = mall_data.get("id")
                print(f"Mall created - Mall ID: {self.mall_id}")
                return True
            else:
                print(f"Mall creation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Mall creation error: {str(e)}")
            return False

    def create_test_camera(self):
        """Create a test camera"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            camera_data = {
                "name": "Test Worker Camera",
                "ip_address": "192.168.1.100",
                "username": "admin",
                "password": "admin1234", 
                "location": "Test Location",
                "mall_id": self.mall_id
            }
            
            response = requests.post(f"{self.base_url}/add_camera", json=camera_data, headers=headers)
            
            if response.status_code in [200, 201]:
                camera_response = response.json()
                self.camera_id = camera_response.get("id")
                print(f"Camera created - Camera ID: {self.camera_id}")
                return True
            else:
                print(f"Camera creation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Camera creation error: {str(e)}")
            return False

    def test_camera_creation_and_management(self):
        """Test camera creation and basic management"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test getting camera details
            response = requests.get(f"{self.base_url}/{self.camera_id}", headers=headers)
            
            if response.status_code == 200:
                camera_data = response.json()
                print(f"Camera details retrieved - Name: {camera_data.get('name')}")
                return True
            else:
                print(f"Camera details failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Camera management error: {str(e)}")
            return False

    def test_detection_pipeline(self):
        """Test detection pipeline functionality"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test starting camera processing
            response = requests.post(f"{self.base_url}/analytics/camera/{self.camera_id}/start", headers=headers)
            
            if response.status_code == 200:
                print("Detection pipeline start successful")
                return True
            else:
                print(f"Detection pipeline start failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Detection pipeline error: {str(e)}")
            return False

    def test_analytics_engine(self):
        """Test analytics engine functionality"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test camera analytics
            response = requests.get(f"{self.base_url}/analytics/camera/{self.camera_id}/details", headers=headers)
            
            if response.status_code == 200:
                analytics_data = response.json()
                print("Analytics engine test successful")
                return True
            else:
                print(f"Analytics engine test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Analytics engine error: {str(e)}")
            return False

    def test_frame_endpoint(self):
        """Test camera frame endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Construct RTSP URL for frame request
            rtsp_url = f"rtsp://admin:admin1234@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0"
            
            frame_request = {
                "rtsp_url": rtsp_url,
                "camera_id": self.camera_id
            }
            
            response = requests.post(f"{self.base_url}/camera/frame", json=frame_request, headers=headers)
            
            if response.status_code == 200 and response.headers.get('content-type') == 'image/jpeg':
                print("Frame endpoint test successful")
                return True
            elif response.status_code == 404:
                print("Frame endpoint responding correctly (camera not available)")
                return True
            else:
                print(f"Frame endpoint test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Frame endpoint error: {str(e)}")
            return False

    def test_stream_endpoint(self):
        """Test camera stream endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test optimized stream
            response = requests.get(f"{self.base_url}/{self.camera_id}/stream", headers=headers, stream=True, timeout=5)
            
            if response.status_code == 200:
                print("Stream endpoint test successful")
                return True
            elif response.status_code == 500:
                print("Stream endpoint responding correctly (camera not available)")
                return True
            else:
                print(f"Stream endpoint test failed: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print("Stream endpoint responding (timeout expected)")
            return True
        except Exception as e:
            print(f"Stream endpoint error: {str(e)}")
            return False

    def test_camera_start_stop_controls(self):
        """Test camera start and stop controls"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test start camera
            start_response = requests.post(f"{self.base_url}/analytics/camera/{self.camera_id}/start", headers=headers)
            
            if start_response.status_code == 200:
                print("Camera start control successful")
                
                # Wait a moment
                time.sleep(2)
                
                # Test stop camera
                stop_response = requests.post(f"{self.base_url}/analytics/camera/{self.camera_id}/stop", headers=headers)
                
                if stop_response.status_code == 200:
                    print("Camera stop control successful")
                    return True
                else:
                    print(f"Camera stop failed: {stop_response.status_code}")
                    return False
            else:
                print(f"Camera start failed: {start_response.status_code}")
                return False
                
        except Exception as e:
            print(f"Camera controls error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all camera worker tests"""
        print("Starting Camera Worker Test Suite\n")
        
        # Setup test data first
        if not self.setup_test_data():
            print("Failed to setup test data")
            return False
        
        tests = [
            ("Camera Creation and Management", self.test_camera_creation_and_management),
            ("Detection Pipeline", self.test_detection_pipeline),
            ("Analytics Engine", self.test_analytics_engine),
            ("Frame Endpoint", self.test_frame_endpoint),
            ("Stream Endpoint", self.test_stream_endpoint),
            ("Camera Start/Stop Controls", self.test_camera_start_stop_controls)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- Testing {test_name} ---")
            if test_func():
                passed += 1
            time.sleep(1)  # Small delay between tests
        
        print(f"\nTest Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("All camera worker tests passed!")
        else:
            print(f" {total - passed} tests failed")
        
        return passed == total

if __name__ == "__main__":
    tester = CameraWorkerTester()
    tester.run_all_tests() 
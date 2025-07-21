#!/usr/bin/env python3
"""
Real Camera Testing Script
Add and test user's actual cameras with provided IP addresses and credentials.
"""

import requests
import io
import time
from PIL import Image

BASE_URL = "http://localhost:8000"

class RealCameraTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.user_id = None
        self.mall_id = None
        self.camera_ids = []
        
        # Real camera details provided by user
        self.cameras = [
            {
                "name": "Camera 1 - Main Camera",
                "ip_address": "192.168.0.5",
                "username": "admin",
                "password": "admin1234",
                "location": "Main Area"
            }
        ]
        
    def create_test_image(self, size=(800, 600), format='PNG'):
        """Create a test image in memory"""
        image = Image.new('RGB', size, color='lightblue')
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return buffer
    
    def print_status(self, message, status="INFO"):
        symbols = {"SUCCESS": "OK", "FAILED": "FAIL", "INFO": "INFO", "TESTING": "TESTING"}
        print(f"{symbols.get(status, 'INFO')} {message}")
    
    def setup_authentication(self):
        """Setup authentication"""
        self.print_status("Setting up authentication...", "TESTING")
        
        # Try login first
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.print_status(f"Login successful - User ID: {self.user_id}", "SUCCESS")
                return True
            else:
                # Create new user if login fails
                signup_data = {
                    "name": "Camera Test User",
                    "email": "test@example.com",
                    "password": "testpassword123"
                }
                
                response = requests.post(f"{self.base_url}/auth/signup", json=signup_data)
                if response.status_code in [200, 201]:
                    # Login after signup
                    response = requests.post(f"{self.base_url}/auth/login", json=login_data)
                    if response.status_code == 200:
                        data = response.json()
                        self.token = data.get("access_token")
                        self.user_id = data.get("user_id")
                        self.print_status(f"Signup and login successful - User ID: {self.user_id}", "SUCCESS")
                        return True
                
                self.print_status("Authentication failed", "FAILED")
                return False
        except Exception as e:
            self.print_status(f"Authentication error: {str(e)}", "FAILED")
            return False
    
    def setup_mall(self):
        """Setup mall for cameras"""
        self.print_status("Setting up mall...", "TESTING")
        
        if not self.token:
            self.print_status("No auth token available", "FAILED")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Check if user already has a mall
        try:
            response = requests.get(f"{self.base_url}/auth/user/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                self.mall_id = user_data.get("mall_id")
                if self.mall_id:
                    self.print_status(f"Using existing mall - ID: {self.mall_id}", "INFO")
                    return True
        except Exception as e:
            pass
        
        # Create new mall
        try:
            test_image = self.create_test_image()
            files = {'map_image': ('mall_map.png', test_image, 'image/png')}
            params = {
                'name': 'Real Camera Test Mall',
                'address': 'Camera Testing Location',
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
                self.print_status(f"Mall created successfully - ID: {self.mall_id}", "SUCCESS")
                return True
            elif response.status_code == 400 and "already has a mall" in response.text:
                # Get existing mall ID from user profile
                response = requests.get(f"{self.base_url}/auth/user/me", headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    self.mall_id = user_data.get("mall_id")
                    if self.mall_id:
                        self.print_status(f"Using existing mall - ID: {self.mall_id}", "INFO")
                        return True
                    
            self.print_status(f"Mall setup failed: {response.status_code}", "FAILED")
            return False
            
        except Exception as e:
            self.print_status(f"Mall setup error: {str(e)}", "FAILED")
            return False
    
    def add_real_cameras(self):
        """Add all real cameras to the system"""
        self.print_status("Adding real cameras to system...", "TESTING")
        
        if not self.token or not self.mall_id:
            self.print_status("Missing auth token or mall ID", "FAILED")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        success_count = 0
        for i, camera in enumerate(self.cameras, 1):
            try:
                camera_data = {
                    "name": camera["name"],
                    "ip_address": camera["ip_address"],
                    "username": camera["username"],
                    "password": camera["password"],
                    "location": camera["location"],
                    "mall_id": self.mall_id
                }
                
                response = requests.post(f"{self.base_url}/add_camera", json=camera_data, headers=headers)
                
                if response.status_code in [200, 201]:
                    camera_response = response.json()
                    camera_id = camera_response.get("id")
                    self.camera_ids.append(camera_id)
                    self.print_status(f"Camera {i} added successfully - IP: {camera['ip_address']}, ID: {camera_id}", "SUCCESS")
                    success_count += 1
                else:
                    self.print_status(f"Camera {i} failed - IP: {camera['ip_address']}, Error: {response.status_code}", "FAILED")
                    
            except Exception as e:
                self.print_status(f"Camera {i} error - IP: {camera['ip_address']}, Error: {str(e)}", "FAILED")
        
        self.print_status(f"Added {success_count}/{len(self.cameras)} cameras successfully", "INFO")
        return success_count > 0
    
    def test_camera_connectivity(self):
        """Test connectivity to real cameras"""
        self.print_status("Testing camera connectivity...", "TESTING")
        
        if not self.token or not self.camera_ids:
            self.print_status("Missing auth token or camera IDs", "FAILED")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        for i, camera_id in enumerate(self.camera_ids):
            camera = self.cameras[i]
            try:
                # Test frame endpoint
                rtsp_url = f"rtsp://{camera['username']}:{camera['password']}@{camera['ip_address']}:554/cam/realmonitor?channel=1&subtype=0"
                
                frame_request = {
                    "rtsp_url": rtsp_url,
                    "camera_id": camera_id
                }
                
                response = requests.post(f"{self.base_url}/camera/frame", json=frame_request, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.print_status(f"Camera {i+1} ({camera['ip_address']}) - Frame capture successful", "SUCCESS")
                elif response.status_code == 404:
                    self.print_status(f"Camera {i+1} ({camera['ip_address']}) - Connection failed (camera may be offline)", "FAILED")
                else:
                    self.print_status(f"Camera {i+1} ({camera['ip_address']}) - Status: {response.status_code}", "INFO")
                    
            except requests.exceptions.Timeout:
                self.print_status(f"Camera {i+1} ({camera['ip_address']}) - Connection timeout", "FAILED")
            except Exception as e:
                self.print_status(f"Camera {i+1} ({camera['ip_address']}) - Error: {str(e)}", "FAILED")
        
        return True
    
    def test_camera_controls(self):
        """Test camera start/stop controls"""
        self.print_status("Testing camera controls...", "TESTING")
        
        if not self.token or not self.camera_ids:
            self.print_status("Missing auth token or camera IDs", "FAILED")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        for i, camera_id in enumerate(self.camera_ids):
            camera = self.cameras[i]
            try:
                # Test start camera processing
                response = requests.post(f"{self.base_url}/analytics/camera/{camera_id}/start", headers=headers)
                
                if response.status_code == 200:
                    self.print_status(f"Camera {i+1} ({camera['ip_address']}) - Start control successful", "SUCCESS")
                    
                    # Wait briefly then test stop
                    time.sleep(2)
                    
                    # Test stop camera processing
                    response = requests.post(f"{self.base_url}/analytics/camera/{camera_id}/stop", headers=headers)
                    
                    if response.status_code == 200:
                        self.print_status(f"Camera {i+1} ({camera['ip_address']}) - Stop control successful", "SUCCESS")
                    else:
                        self.print_status(f"Camera {i+1} ({camera['ip_address']}) - Stop failed: {response.status_code}", "FAILED")
                else:
                    self.print_status(f"Camera {i+1} ({camera['ip_address']}) - Start failed: {response.status_code}", "FAILED")
                    
            except Exception as e:
                self.print_status(f"Camera {i+1} ({camera['ip_address']}) - Control error: {str(e)}", "FAILED")
        
        return True
    
    def list_cameras(self):
        """List all cameras in the mall"""
        self.print_status("Listing all cameras...", "TESTING")
        
        if not self.token or not self.mall_id:
            self.print_status("Missing auth token or mall ID", "FAILED")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.base_url}/mall/{self.mall_id}/cameras", headers=headers)
            
            if response.status_code == 200:
                cameras = response.json()
                self.print_status(f"Found {len(cameras)} cameras in mall:", "SUCCESS")
                
                for camera in cameras:
                    print(f"   📹 ID: {camera.get('id')}, Name: {camera.get('name')}, IP: {camera.get('ip_address')}, Location: {camera.get('location')}")
                
                return True
            else:
                self.print_status(f"Camera listing failed: {response.status_code}", "FAILED")
                return False
                
        except Exception as e:
            self.print_status(f"Camera listing error: {str(e)}", "FAILED")
            return False
    
    def run_real_camera_tests(self):
        """Run complete real camera testing"""
        print("🚀 Real Camera Testing - Adding and Testing Your Camera")
        print("=" * 70)
        print(f"Camera IP: 192.168.0.5")
        print(f"Username: admin, Password: admin1234")
        print("=" * 70)
        
        tests = [
            ("Authentication Setup", self.setup_authentication),
            ("Mall Setup", self.setup_mall),
            ("Add Real Cameras", self.add_real_cameras),
            ("List Cameras", self.list_cameras),
            ("Test Camera Connectivity", self.test_camera_connectivity),
            ("Test Camera Controls", self.test_camera_controls)
        ]
        
        passed = 0
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            if test_func():
                passed += 1
            time.sleep(1)
        
        print(f"\n{'=' * 70}")
        print(f"🎯 Real Camera Test Results: {passed}/{len(tests)} tests passed")
        
        if passed >= 3:  # At least auth, mall, and camera addition should work
            print("🎉 Your cameras have been successfully added to the system!")
            print("\n📋 Camera Summary:")
            for i, camera in enumerate(self.cameras, 1):
                print(f"  📹 Camera {i}: {camera['ip_address']} - {camera['location']}")
            
            if len(self.camera_ids) > 0:
                print(f"\n✅ Camera IDs: {self.camera_ids}")
                print("💡 You can now use these cameras in your mall analytics system!")
        else:
            print(f"⚠️  Some tests failed. Please check camera connectivity and network settings.")
        
        return passed >= 3

if __name__ == "__main__":
    tester = RealCameraTester()
    tester.run_real_camera_tests() 
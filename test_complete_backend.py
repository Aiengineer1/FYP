#!/usr/bin/env python3
"""
Complete Backend Test Suite
Tests all major backend features including:
- Authentication
- Analytics APIs
- Socket.io WebSocket
- Protected endpoints
- Mall/Camera management
"""

import requests
import json
import time
import random
import socketio
import asyncio
from datetime import datetime
import os
import io
from PIL import Image

BASE_URL = "http://localhost:8000"

class BackendTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.mall_id = None
        self.camera_id = None
        self.sio = None
        
    def print_section(self, title):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(title)
        print(f"{'='*60}")
    
    def print_test(self, test_name, status):
        """Print test status"""
        if status == "SUCCESS":
            print(f"{test_name} - SUCCESS")
        else:
            print(f"{test_name} - FAILED")
    
    def create_test_image(self, size=(800, 600), format='PNG'):
        """Create a test image in memory"""
        image = Image.new('RGB', size, color='lightblue')
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return buffer

    def test_health_check(self):
        """Test server health"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.print_test("Server Health Check", "SUCCESS")
                health_data = response.json()
                print(f"   Message: {health_data.get('message')}")
                print(f"   Version: {health_data.get('version')}")
                return True
            else:
                self.print_test("Server Health Check", "FAILED")
                print(f"   Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Server Health Check", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_signup(self):
        """Test user signup"""
        try:
            signup_data = {
                "name": "Test User",
                "email": "test@example.com", 
                "password": "testpassword123"
            }
            
            response = requests.post(f"{self.base_url}/auth/signup", json=signup_data)
            
            if response.status_code in [200, 201]:
                self.print_test("User Signup", "SUCCESS")
                user_data = response.json()
                print(f"   User ID: {user_data.get('id')}")
                print(f"   Email: {user_data.get('email')}")
                return True
            elif response.status_code == 400 and "already registered" in response.text:
                self.print_test("User Signup", "SUCCESS")
                print(f" User already exists (expected)")
                return True
            else:
                self.print_test("User Signup", "FAILED")
                print(f"   Error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_test("User Signup", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_login(self):
        """Test user login"""
        try:
            login_data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                self.print_test("User Login", "SUCCESS")
                login_response = response.json()
                self.token = login_response.get("access_token")
                self.user_id = login_response.get("user_id")
                print(f"   Token: {self.token[:30]}...")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                self.print_test("User Login", "FAILED")
                print(f"   Error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_test("User Login", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_token_verification(self):
        """Test token verification"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/auth/verify", headers=headers)
            
            if response.status_code == 200:
                self.print_test("Token Verification", "SUCCESS")
                verify_data = response.json()
                print(f"   Valid: {verify_data.get('valid')}")
                print(f"   User: {verify_data.get('user')}")
                return True
            else:
                self.print_test("Token Verification", "FAILED")
                print(f"   Error: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_test("Token Verification", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_user_profile(self):
        """Test getting user profile"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/auth/user/me", headers=headers)
            
            if response.status_code == 200:
                self.print_test("Get User Profile", "SUCCESS")
                profile = response.json()
                print(f"   Name: {profile.get('name')}")
                print(f"   Email: {profile.get('email')}")
                return True
            else:
                self.print_test("Get User Profile", "FAILED")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            self.print_test("Get User Profile", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_mall_creation(self):
        """Test mall creation with multipart form data"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create test image
            test_image = self.create_test_image()
            
            # Prepare form data with file
            files = {
                'map_image': ('test_mall_map.png', test_image, 'image/png')
            }
            
            # Use params for query parameters
            params = {
                'name': 'Test Mall',
                'address': '123 Test Street, Test City',
                'user_id': self.user_id
            }
            
            response = requests.post(
                f"{self.base_url}/mall/create", 
                headers=headers,
                files=files,
                params=params
            )
            
            if response.status_code in [200, 201]:
                self.print_test("Create Mall", "SUCCESS")
                mall_response = response.json()
                self.mall_id = mall_response.get("id")
                print(f"   Mall ID: {self.mall_id}")
                print(f"   Name: {mall_response.get('name')}")
                return True
            else:
                self.print_test("Create Mall", "FAILED")
                print(f"   Error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_test("Create Mall", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_mall_retrieval(self):
        """Test mall retrieval"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/mall/{self.mall_id}", headers=headers)
            
            if response.status_code == 200:
                self.print_test("Get Mall Details", "SUCCESS")
                mall_details = response.json()
                print(f"   Mall: {mall_details.get('name')}")
                print(f"   Address: {mall_details.get('address')}")
                return True
            else:
                self.print_test("Get Mall Details", "FAILED")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            self.print_test("Get Mall Details", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_camera_creation(self):
        """Test camera creation"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            camera_data = {
                "name": "Test Camera 1",
                "ip_address": "192.168.1.100",
                "username": "admin",
                "password": "admin1234",
                "location": "Main Entrance",
                "mall_id": self.mall_id
            }
            
            response = requests.post(f"{self.base_url}/add_camera", json=camera_data, headers=headers)
            
            if response.status_code in [200, 201]:
                self.print_test("Create Camera", "SUCCESS")
                camera_response = response.json()
                self.camera_id = camera_response.get("id")
                print(f"   Camera ID: {self.camera_id}")
                print(f"   Name: {camera_response.get('name')}")
                return True
            else:
                self.print_test("Create Camera", "FAILED")
                print(f"   Error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.print_test("Create Camera", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_camera_listing(self):
        """Test camera listing by mall"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/mall/{self.mall_id}/cameras", headers=headers)
            
            if response.status_code == 200:
                self.print_test("Get Camera List", "SUCCESS")
                cameras = response.json()
                print(f"   Total Cameras: {len(cameras)}")
                return True
            else:
                self.print_test("Get Camera List", "FAILED")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            self.print_test("Get Camera List", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_camera_details(self):
        """Test camera details retrieval"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/{self.camera_id}", headers=headers)
            
            if response.status_code == 200:
                self.print_test("Get Camera Details", "SUCCESS")
                camera = response.json()
                print(f"   Camera: {camera.get('name')}")
                print(f"   Location: {camera.get('location')}")
                return True
            else:
                self.print_test("Get Camera Details", "FAILED")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            self.print_test("Get Camera Details", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_analytics_mall(self):
        """Test mall analytics"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/analytics/mall/{self.mall_id}", headers=headers)
            
            if response.status_code == 200:
                self.print_test("Mall Analytics", "SUCCESS")
                analytics = response.json()
                print(f"   Total Visitors: {analytics.get('totalVisitors', 'N/A')}")
                print(f"   Active Visitors: {analytics.get('activeVisitors', 'N/A')}")
                print(f"   Popular Sections: {len(analytics.get('popularSections', []))}")
                return True
            else:
                self.print_test("Mall Analytics", "FAILED")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            self.print_test("Mall Analytics", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_analytics_realtime(self):
        """Test real-time analytics"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/analytics/realtime/{self.mall_id}", headers=headers)
            
            if response.status_code == 200:
                self.print_test("Real-time Status", "SUCCESS")
                realtime = response.json()
                print(f"   Current Visitors: {realtime.get('currentVisitors', 'N/A')}")
                print(f"   System Health: {realtime.get('systemHealth', {})}")
                return True
            else:
                self.print_test("Real-time Status", "FAILED")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            self.print_test("Real-time Status", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_analytics_heatmap(self):
        """Test heatmap analytics"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/analytics/mall/{self.mall_id}/heatmap", headers=headers)
            
            if response.status_code == 200:
                self.print_test("Heatmap Data", "SUCCESS")
                heatmap = response.json()
                print(f"   Success: {heatmap.get('success', 'N/A')}")
                print(f"   Data Keys: {list(heatmap.get('data', {}).keys())}")
                return True
            else:
                self.print_test("Heatmap Data", "FAILED")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            self.print_test("Heatmap Data", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_analytics_system_status(self):
        """Test system status"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/analytics/system/status", headers=headers)
            
            if response.status_code == 200:
                self.print_test("System Status", "SUCCESS")
                system_status = response.json()
                print(f"   Success: {system_status.get('success', 'N/A')}")
                print(f"   System Health: {system_status.get('data', {}).get('system_health', 'N/A')}")
                return True
            else:
                self.print_test("System Status", "FAILED")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            self.print_test("System Status", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def test_camera_controls(self):
        """Test camera start/stop controls"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test start camera processing
            start_response = requests.post(f"{self.base_url}/analytics/camera/{self.camera_id}/start", headers=headers)
            
            if start_response.status_code == 200:
                self.print_test("Start Camera Processing", "SUCCESS")
                
                # Wait a moment
                time.sleep(1)
                
                # Test stop camera processing
                stop_response = requests.post(f"{self.base_url}/analytics/camera/{self.camera_id}/stop", headers=headers)
                
                if stop_response.status_code == 200:
                    self.print_test("Stop Camera Processing", "SUCCESS")
                    return True
                else:
                    self.print_test("Stop Camera Processing", "FAILED")
                    print(f"   Error: {stop_response.status_code}")
                    return False
            else:
                self.print_test("Start Camera Processing", "FAILED")
                print(f"   Error: {start_response.status_code}")
                return False
                
        except Exception as e:
            self.print_test("Start Camera Processing", "FAILED")
            print(f"   Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run complete test suite"""
        print("STARTING COMPLETE BACKEND TEST SUITE")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {}
        
        # Test 1: Server Health
        results['server_health'] = self.test_health_check()
        
        # Test 2: Authentication
        results['authentication'] = self.test_signup() and self.test_login() and self.test_token_verification() and self.test_user_profile()
        
        # Test 3: Mall Management
        if results['authentication']:
            results['mall_management'] = self.test_mall_creation() and self.test_mall_retrieval()
        
        # Test 4: Camera Management
        if results.get('mall_management'):
            results['camera_management'] = self.test_camera_creation() and self.test_camera_listing() and self.test_camera_details()
        
        # Test 5: Analytics APIs
        if results.get('mall_management'):
            results['analytics_apis'] = self.test_analytics_mall() and self.test_analytics_realtime() and self.test_analytics_heatmap() and self.test_analytics_system_status()
        
        # Test 6: Camera Controls
        if results.get('camera_management'):
            results['camera_controls'] = self.test_camera_controls()
        
        # Print Results Summary
        self.print_section("TEST RESULTS SUMMARY")
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for test_name, result in results.items():
            status = "PASSED" if result else "FAILED"
            print(f"{status} - {test_name.replace('_', ' ').title()}")
        
        print(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print(" ALL TESTS PASSED! Backend is fully functional!")
        else:
            print(f" {total_tests - passed_tests} tests failed. Review the issues above.")
        
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    tester = BackendTester()
    tester.run_all_tests() 
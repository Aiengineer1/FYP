#!/usr/bin/env python3
"""
Test script for deletion endpoints
Tests user account and mall deletion functionality
"""

import requests
import json
import time
from typing import Optional, Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "deletion_test@example.com"
TEST_PASSWORD = "testpass123"
TEST_NAME = "Deletion Test User"

class DeletionEndpointTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.mall_id: Optional[int] = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get('headers', {})
        
        # Add authorization header if token is available
        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"
            
        kwargs['headers'] = headers
        
        try:
            response = requests.request(method, url, **kwargs)
            self.log(f"{method} {endpoint} -> {response.status_code}")
            return response
        except Exception as e:
            self.log(f"Request failed: {str(e)}", "ERROR")
            raise
    
    def signup_test_user(self) -> bool:
        """Create a test user account"""
        self.log("Creating test user account...")
        
        user_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        }
        
        response = self.make_request(
            "POST", 
            "/auth/signup",
            json=user_data
        )
        
        if response.status_code in [200, 201]:  # Accept both 200 and 201
            user = response.json()
            self.user_id = user['id']
            self.log(f"✅ Test user created with ID: {self.user_id}")
            return True
        elif response.status_code == 400:
            error = response.json()
            if "already registered" in error.get('detail', {}).get('message', ''):
                self.log("⚠️  User already exists, proceeding with login...")
                return self.login_test_user()
        
        self.log(f"❌ Failed to create user: {response.text}", "ERROR")
        return False
    
    def login_test_user(self) -> bool:
        """Login with test user credentials"""
        self.log("Logging in test user...")
        
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        response = self.make_request(
            "POST",
            "/auth/login", 
            json=login_data
        )
        
        if response.status_code == 200:
            auth_data = response.json()
            self.token = auth_data['access_token']
            self.user_id = auth_data['user_id']
            self.mall_id = auth_data.get('mall_id')
            self.log(f"✅ Login successful. User ID: {self.user_id}, Mall ID: {self.mall_id}")
            return True
        
        self.log(f"❌ Login failed: {response.text}", "ERROR")
        return False
    
    def create_test_mall(self) -> bool:
        """Create a test mall for the user"""
        if self.mall_id:
            self.log(f"✅ User already has mall ID: {self.mall_id}")
            return True
            
        self.log("Creating test mall...")
        
        # Create a simple test image (1x1 pixel PNG)
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDAT\x08\x1dc\xf8\x0f\x00\x00\x01\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {
            'map_image': ('test_mall.png', test_image_data, 'image/png')
        }
        
        data = {
            'name': 'Test Mall for Deletion',
            'address': 'Test Address 123',
            'user_id': str(self.user_id)
        }
        
        # Use params for query parameters
        params = {
            'name': 'Test Mall for Deletion',
            'address': 'Test Address 123',
            'user_id': str(self.user_id)
        }
        
        response = self.make_request(
            "POST",
            "/mall/create",
            files=files,
            params=params
        )
        
        if response.status_code == 200:
            mall = response.json()
            self.mall_id = mall['id']
            self.log(f"✅ Test mall created with ID: {self.mall_id}")
            return True
        
        self.log(f"❌ Failed to create mall: {response.text}", "ERROR")
        return False
    
    def test_mall_deletion_endpoints(self) -> Dict[str, bool]:
        """Test mall deletion endpoints"""
        results = {}
        
        if not self.mall_id:
            self.log("❌ No mall to test deletion with", "ERROR")
            return {"mall_deletion": False}
        
        self.log("\n=== Testing Mall Deletion Endpoints ===")
        
        # Test 1: Delete my mall (convenience endpoint)
        self.log("1. Testing DELETE /mall/delete-my-mall")
        response = self.make_request("DELETE", "/mall/delete-my-mall")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                self.log(f"✅ Mall deleted successfully: {result.get('message')}")
                results['delete_my_mall'] = True
                self.mall_id = None  # Mall is deleted
            else:
                self.log(f"❌ Unexpected response: {result}", "ERROR")
                results['delete_my_mall'] = False
        else:
            self.log(f"❌ Mall deletion failed: {response.text}", "ERROR")
            results['delete_my_mall'] = False
        
        return results
    
    def test_account_deletion_endpoints(self) -> Dict[str, bool]:
        """Test account deletion endpoints"""
        results = {}
        
        self.log("\n=== Testing Account Deletion Endpoints ===")
        
        # Test 1: Delete my account (convenience endpoint)
        self.log("1. Testing DELETE /auth/account/delete")
        response = self.make_request("DELETE", "/auth/account/delete")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                self.log(f"✅ Account deleted successfully: {result.get('message')}")
                results['delete_my_account'] = True
                self.token = None  # Token is invalid now
                self.user_id = None
            else:
                self.log(f"❌ Unexpected response: {result}", "ERROR")
                results['delete_my_account'] = False
        else:
            self.log(f"❌ Account deletion failed: {response.text}", "ERROR")
            results['delete_my_account'] = False
        
        return results
    
    def test_unauthorized_access(self) -> Dict[str, bool]:
        """Test that deletion endpoints require authentication"""
        results = {}
        
        self.log("\n=== Testing Unauthorized Access ===")
        
        # Remove token temporarily
        original_token = self.token
        self.token = None
        
        # Test 1: Delete account without token
        self.log("1. Testing DELETE /auth/account/delete (no auth)")
        response = self.make_request("DELETE", "/auth/account/delete")
        
        if response.status_code == 401:
            self.log("✅ Properly rejected unauthorized access")
            results['unauthorized_account_delete'] = True
        else:
            self.log(f"❌ Should have rejected unauthorized access: {response.status_code}", "ERROR")
            results['unauthorized_account_delete'] = False
        
        # Test 2: Delete mall without token
        self.log("2. Testing DELETE /mall/delete-my-mall (no auth)")
        response = self.make_request("DELETE", "/mall/delete-my-mall")
        
        if response.status_code == 401:
            self.log("✅ Properly rejected unauthorized access")
            results['unauthorized_mall_delete'] = True
        else:
            self.log(f"❌ Should have rejected unauthorized access: {response.status_code}", "ERROR")
            results['unauthorized_mall_delete'] = False
        
        # Restore token
        self.token = original_token
        return results
    
    def test_nonexistent_resources(self) -> Dict[str, bool]:
        """Test deletion of nonexistent resources"""
        results = {}
        
        self.log("\n=== Testing Nonexistent Resource Deletion ===")
        
        # Test 1: Delete nonexistent user
        self.log("1. Testing DELETE /auth/user/99999")
        response = self.make_request("DELETE", "/auth/user/99999")
        
        if response.status_code in [403, 404]:  # 403 for unauthorized, 404 for not found
            self.log("✅ Properly handled nonexistent user")
            results['nonexistent_user'] = True
        else:
            self.log(f"❌ Should have returned 403/404 for nonexistent user: {response.status_code}", "ERROR")
            results['nonexistent_user'] = False
        
        # Test 2: Delete nonexistent mall
        self.log("2. Testing DELETE /mall/99999")
        response = self.make_request("DELETE", "/mall/99999")
        
        if response.status_code in [404, 403]:  # 404 for not found, 403 for not owned
            self.log("✅ Properly handled nonexistent mall")
            results['nonexistent_mall'] = True
        else:
            self.log(f"❌ Should have returned 404/403 for nonexistent mall: {response.status_code}", "ERROR")
            results['nonexistent_mall'] = False
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive deletion endpoint tests"""
        self.log("🚀 Starting Deletion Endpoints Test Suite")
        self.log("=" * 50)
        
        all_results = {}
        
        # Setup phase
        self.log("\n=== SETUP PHASE ===")
        if not self.signup_test_user():
            if not self.login_test_user():
                self.log("❌ Failed to setup test user", "ERROR")
                return {"error": "Failed to setup test user"}
        
        if not self.create_test_mall():
            self.log("⚠️  Proceeding without mall (will test account deletion only)")
        
        # Test unauthorized access first (before deleting anything)
        unauthorized_results = self.test_unauthorized_access()
        all_results.update(unauthorized_results)
        
        # Test nonexistent resources
        nonexistent_results = self.test_nonexistent_resources()
        all_results.update(nonexistent_results)
        
        # Test mall deletion
        if self.mall_id:
            mall_results = self.test_mall_deletion_endpoints()
            all_results.update(mall_results)
        
        # Test account deletion (this should be last as it deletes the user)
        account_results = self.test_account_deletion_endpoints()
        all_results.update(account_results)
        
        return all_results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print test results summary"""
        self.log("\n" + "=" * 50)
        self.log("🏁 DELETION ENDPOINTS TEST SUMMARY")
        self.log("=" * 50)
        
        if "error" in results:
            self.log(f"❌ Test suite failed: {results['error']}", "ERROR")
            return
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        self.log(f"📊 Tests Run: {total_tests}")
        self.log(f"✅ Tests Passed: {passed_tests}")
        self.log(f"❌ Tests Failed: {total_tests - passed_tests}")
        self.log(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        self.log("\n📋 Detailed Results:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"  {test_name}: {status}")
        
        if passed_tests == total_tests:
            self.log("\n🎉 ALL DELETION ENDPOINTS WORKING PERFECTLY!")
        else:
            self.log(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Check the logs above.")

def main():
    """Run the deletion endpoint tests"""
    tester = DeletionEndpointTester()
    
    try:
        results = tester.run_all_tests()
        tester.print_summary(results)
    except KeyboardInterrupt:
        tester.log("\n🛑 Test interrupted by user", "INFO")
    except Exception as e:
        tester.log(f"💥 Test suite crashed: {str(e)}", "ERROR")
        raise

if __name__ == "__main__":
    main() 
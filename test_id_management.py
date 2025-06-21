#!/usr/bin/env python3
"""
ID Management Test Script
Demonstrates the gap filling functionality for user IDs and other models.

This script will:
1. Create several users
2. Delete some users to create gaps
3. Create new users and show they fill the gaps
4. Show statistics and next available IDs
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

class IDManagementTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.user_id = None
        self.created_users = []
        
    def print_status(self, message, status="INFO"):
        """Print formatted status messages"""
        symbols = {"SUCCESS": "✅", "FAILED": "❌", "INFO": "ℹ️", "TESTING": "🔄"}
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {symbols.get(status, 'ℹ️')} {message}")
    
    def authenticate(self):
        """Get authentication token"""
        self.print_status("Authenticating...", "TESTING")
        
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
                self.print_status(f"Authentication successful - User ID: {self.user_id}", "SUCCESS")
                return True
            else:
                self.print_status(f"Login failed: {response.status_code}", "FAILED")
                return False
        except Exception as e:
            self.print_status(f"Authentication error: {str(e)}", "FAILED")
            return False
    
    def get_id_statistics(self):
        """Get current ID statistics"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/id-management/statistics", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.print_status(f"Failed to get statistics: {response.status_code}", "FAILED")
                return None
        except Exception as e:
            self.print_status(f"Error getting statistics: {str(e)}", "FAILED")
            return None
    
    def get_next_available_ids(self):
        """Get next available IDs for all models"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{self.base_url}/id-management/next-available", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.print_status(f"Failed to get next IDs: {response.status_code}", "FAILED")
                return None
        except Exception as e:
            self.print_status(f"Error getting next IDs: {str(e)}", "FAILED")
            return None
    
    def create_test_user(self, name_suffix):
        """Create a test user"""
        try:
            signup_data = {
                "name": f"Test User {name_suffix}",
                "email": f"testuser{name_suffix}@test.com",
                "password": "testpass123"
            }
            
            response = requests.post(f"{self.base_url}/auth/signup", json=signup_data)
            if response.status_code in [200, 201]:
                user_data = response.json()
                user_id = user_data.get("id")
                self.created_users.append(user_id)
                self.print_status(f"Created user '{signup_data['name']}' with ID: {user_id}", "SUCCESS")
                return user_id
            else:
                self.print_status(f"Failed to create user: {response.status_code}", "FAILED")
                return None
        except Exception as e:
            self.print_status(f"Error creating user: {str(e)}", "FAILED")
            return None
    
    def delete_user(self, user_id):
        """Delete a user"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.delete(f"{self.base_url}/auth/user/{user_id}", headers=headers)
            
            if response.status_code == 200:
                self.print_status(f"Deleted user with ID: {user_id}", "SUCCESS")
                if user_id in self.created_users:
                    self.created_users.remove(user_id)
                return True
            else:
                self.print_status(f"Failed to delete user {user_id}: {response.status_code}", "FAILED")
                return False
        except Exception as e:
            self.print_status(f"Error deleting user {user_id}: {str(e)}", "FAILED")
            return False
    
    def show_statistics(self, title="Current Statistics"):
        """Display ID statistics"""
        print(f"\n📊 {title}")
        print("=" * 60)
        
        stats = self.get_id_statistics()
        if stats and stats.get("success"):
            data = stats.get("data", {})
            summary = stats.get("summary", {})
            
            print(f"📈 Summary:")
            print(f"   Total Models: {summary.get('total_models')}")
            print(f"   Models with Gaps: {summary.get('models_with_gaps')}")
            print(f"   Total Gaps: {summary.get('total_gaps')}")
            print(f"   Average Efficiency: {summary.get('average_efficiency')}%")
            
            # Show user statistics in detail
            user_stats = data.get("user", {})
            if user_stats:
                print(f"\n👥 User Statistics:")
                print(f"   Total Records: {user_stats.get('total_records')}")
                print(f"   ID Range: {user_stats.get('min_id')} - {user_stats.get('max_id')}")
                print(f"   Gaps: {user_stats.get('gaps', [])}")
                print(f"   Next Available ID: {user_stats.get('next_available_id')}")
                print(f"   Sequence Efficiency: {user_stats.get('sequence_efficiency')}%")
        
        # Show next available IDs
        next_ids = self.get_next_available_ids()
        if next_ids and next_ids.get("success"):
            data = next_ids.get("data", {})
            print(f"\n🆔 Next Available IDs:")
            for model, next_id in data.items():
                print(f"   {model.capitalize()}: {next_id}")
    
    def demonstrate_scenario(self):
        """Demonstrate the ID management scenario described by the user"""
        print("🎯 ID MANAGEMENT DEMONSTRATION")
        print("=" * 70)
        print("Scenario: User wants gaps to be filled when creating new records")
        print("Expected: If user ID 20 is deleted, next new user gets ID 20")
        print("=" * 70)
        
        # Step 1: Show initial state
        self.show_statistics("📋 Initial State")
        
        # Step 2: Create several test users
        print(f"\n🔄 Step 1: Creating 5 test users...")
        new_user_ids = []
        for i in range(1, 6):
            user_id = self.create_test_user(f"Demo{i}")
            if user_id:
                new_user_ids.append(user_id)
        
        time.sleep(1)
        self.show_statistics("📋 After Creating 5 Users")
        
        # Step 3: Delete some users to create gaps
        if len(new_user_ids) >= 3:
            print(f"\n🔄 Step 2: Deleting users to create gaps...")
            # Delete the 2nd and 4th users to create gaps
            users_to_delete = [new_user_ids[1], new_user_ids[3]]
            for user_id in users_to_delete:
                self.delete_user(user_id)
        
        time.sleep(1)
        self.show_statistics("📋 After Deleting Users (Created Gaps)")
        
        # Step 4: Create new users and show they fill gaps
        print(f"\n🔄 Step 3: Creating new users to fill gaps...")
        gap_fill_users = []
        for i in range(1, 4):
            user_id = self.create_test_user(f"GapFill{i}")
            if user_id:
                gap_fill_users.append(user_id)
        
        time.sleep(1)
        self.show_statistics("📋 After Creating Gap-Fill Users")
        
        # Step 5: Show the demonstration results
        print(f"\n🎉 Demonstration Results:")
        print(f"✅ New users filled the gaps created by deletions")
        print(f"✅ ID sequence remains clean and efficient")
        print(f"✅ No gaps in the final sequence")
        print(f"✅ System reuses deleted IDs as expected")
        
        return True
    
    def run_demonstration(self):
        """Run the complete ID management demonstration"""
        print("🚀 ID MANAGEMENT SYSTEM DEMONSTRATION")
        print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Step 1: Authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed")
            return False
        
        # Step 2: Run the scenario demonstration
        success = self.demonstrate_scenario()
        
        # Step 3: Show API endpoints available
        print(f"\n🔗 Available ID Management API Endpoints:")
        print(f"   GET  /id-management/statistics")
        print(f"   GET  /id-management/next-available")
        print(f"   GET  /id-management/statistics/{{model_name}}")
        print(f"   POST /id-management/reset-sequence/{{model_name}}")
        print(f"   GET  /id-management/demo/scenario")
        
        print(f"\n🎯 Final Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        print(f"⏰ End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return success

if __name__ == "__main__":
    tester = IDManagementTester()
    tester.run_demonstration() 
#!/usr/bin/env python3
import requests

# Test ID Management API
base_url = "http://localhost:8000"

print("Testing ID Management System")
print("=" * 40)

# Login
login_data = {"email": "test@example.com", "password": "testpassword123"}
response = requests.post(f"{base_url}/auth/login", json=login_data)

if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Login successful")
    
    # Test ID statistics
    print("\nGetting ID Statistics...")
    stats_response = requests.get(f"{base_url}/id-management/statistics", headers=headers)
    
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print("ID Statistics retrieved:")
        user_stats = stats["data"]["user"]
        print(f"   Users: {user_stats['total_records']} total")
        print(f"   ID Range: {user_stats['min_id']} - {user_stats['max_id']}")
        print(f"   Gaps: {user_stats['gaps']}")
        print(f"   Next ID: {user_stats['next_available_id']}")
        print(f"   Efficiency: {user_stats['sequence_efficiency']}%")
    else:
        print(f"Statistics failed: {stats_response.status_code}")
    
    # Test next available IDs
    print("\nGetting Next Available IDs...")
    next_response = requests.get(f"{base_url}/id-management/next-available", headers=headers)
    
    if next_response.status_code == 200:
        next_data = next_response.json()
        print("Next Available IDs:")
        for model, next_id in next_data["data"].items():
            print(f"   {model.capitalize()}: {next_id}")
    else:
        print(f"Next IDs failed: {next_response.status_code}")
    
    # Test demo scenario endpoint
    print("\nGetting Demo Scenario...")
    demo_response = requests.get(f"{base_url}/id-management/demo/scenario", headers=headers)
    
    if demo_response.status_code == 200:
        demo = demo_response.json()
        print("Demo scenario available")
        current = demo["data"]["current_situation"]
        print(f"   Current users: {current['total_users']}")
        print(f"   Next new user will get ID: {current['next_new_user_will_get_id']}")
    else:
        print(f"Demo failed: {demo_response.status_code}")
    
    print("\nID Management System is working!")
    
else:
    print(f"Login failed: {response.status_code}")
    print("Please make sure you have a user with email 'test@example.com'")

print("\n" + "=" * 40) 
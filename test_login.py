import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Test login API"""
    login_data = {
        "email": "f2021376018@umt.edu.pk",
        "password": "Ghulam@1234"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Name: {data.get('name')}")
            print(f"   Email: {data.get('email')}")
            print(f"   Token: {data.get('access_token')[:50]}...")
            return data.get('access_token')
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing login: {str(e)}")
        return None

def test_signup():
    """Test signup API"""
    signup_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        print(f"\nSignup Status Code: {response.status_code}")
        print(f"Signup Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Signup successful!")
        else:
            print(f"❌ Signup failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing signup: {str(e)}")

if __name__ == "__main__":
    print("🔐 Testing Authentication APIs...")
    print("="*50)
    
    # Test login
    token = test_login()
    
    # Test signup
    test_signup()
    
    print("\n" + "="*50)
    print("✅ Authentication API tests completed!") 
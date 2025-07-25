#!/usr/bin/env python3
"""
Comprehensive test script for authentication system
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1/auth"

# Test user data
test_user = {
    "username": "testauth",
    "email": "testauth@example.com",
    "first_name": "Test",
    "last_name": "Auth",
    "phone": "1234567890",
    "role": "TECHNICIAN",
    "password": "testpass123",
    "is_active": True
}

def test_registration():
    """Test user registration"""
    print("🧪 Testing Registration...")
    try:
        response = requests.post(f"{BASE_URL}/register", json=test_user)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Registration successful! User ID: {data['id']}")
            return True
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login():
    """Test user login"""
    print("\n🧪 Testing Login...")
    try:
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            print(f"✅ Login successful! Token: {token[:20]}...")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_me_endpoint(token):
    """Test /me endpoint"""
    print("\n🧪 Testing /me endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ /me successful! User: {data['username']}")
            return True
        else:
            print(f"❌ /me failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_verify_token(token):
    """Test token verification"""
    print("\n🧪 Testing Token Verification...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/verify-token", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token verification successful! {data['message']}")
            return True
        else:
            print(f"❌ Token verification failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_change_password(token):
    """Test password change"""
    print("\n🧪 Testing Password Change...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        password_data = {
            "current_password": test_user["password"],
            "new_password": "newpass123"
        }
        response = requests.post(f"{BASE_URL}/change-password", json=password_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Password change successful! {data['message']}")
            return True
        else:
            print(f"❌ Password change failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_logout(token):
    """Test logout"""
    print("\n🧪 Testing Logout...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/logout", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Logout successful! {data['message']}")
            return True
        else:
            print(f"❌ Logout failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_after_logout(token):
    """Test that token is invalidated after logout"""
    print("\n🧪 Testing Token After Logout...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Token properly invalidated after logout!")
            return True
        else:
            print(f"❌ Token still valid after logout: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Authentication System Tests\n")
    
    # Test registration
    if not test_registration():
        print("\n❌ Registration test failed. Stopping tests.")
        return
    
    # Test login
    token = test_login()
    if not token:
        print("\n❌ Login test failed. Stopping tests.")
        return
    
    # Test authenticated endpoints
    test_me_endpoint(token)
    test_verify_token(token)
    test_change_password(token)
    
    # Test logout
    test_logout(token)
    
    # Test that token is invalidated
    test_after_logout(token)
    
    print("\n🎉 All authentication tests completed!")

if __name__ == "__main__":
    main() 
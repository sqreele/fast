#!/usr/bin/env python3
"""
Test script for user registration
"""
import requests
import json

# Test registration data
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "phone": "1234567890",
    "role": "TECHNICIAN",
    "password": "testpass123",
    "is_active": True,
    "property_ids": [1]
}

def test_registration():
    """Test the registration endpoint"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            return True
        else:
            print("❌ Registration failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing user registration...")
    test_registration() 
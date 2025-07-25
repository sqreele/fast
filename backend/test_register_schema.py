#!/usr/bin/env python3
"""
Test script for registration endpoint using the exact JSON schema provided
"""
import requests
import json

# The exact JSON schema you provided
test_user_data = {
    "username": "string",
    "email": "user@example.com",
    "first_name": "string",
    "last_name": "string",
    "phone": "string",
    "role": "TECHNICIAN",
    "is_active": True,
    "password": "string",
    "property_ids": [0]
}

def test_registration_with_schema():
    """Test registration with the exact schema provided"""
    print("🧪 Testing Registration with Provided Schema...")
    print(f"Endpoint: POST /api/v1/auth/register")
    print(f"Data: {json.dumps(test_user_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json=test_user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Registration successful!")
            print(f"User ID: {data.get('id')}")
            print(f"Username: {data.get('username')}")
            print(f"Email: {data.get('email')}")
            print(f"Role: {data.get('role')}")
            return True
        else:
            print(f"\n❌ Registration failed!")
            if response.status_code == 422:
                print("Validation error - check the schema requirements:")
                error_data = response.json()
                for error in error_data.get('detail', []):
                    print(f"  - {error.get('loc', [])}: {error.get('msg', '')}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_with_real_data():
    """Test with more realistic data"""
    print("\n" + "="*60)
    print("🧪 Testing with Realistic Data...")
    
    realistic_data = {
        "username": "john_doe",
        "email": "john.doe@company.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1-555-123-4567",
        "role": "TECHNICIAN",
        "is_active": True,
        "password": "securepassword123",
        "property_ids": [1, 2]  # Multiple properties
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json=realistic_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Realistic registration successful!")
            print(f"User: {data.get('first_name')} {data.get('last_name')}")
            return True
        else:
            print(f"❌ Realistic registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_validation_errors():
    """Test various validation scenarios"""
    print("\n" + "="*60)
    print("🧪 Testing Validation Errors...")
    
    test_cases = [
        {
            "name": "Missing required fields",
            "data": {"username": "test"},
            "expected_status": 422
        },
        {
            "name": "Invalid email format",
            "data": {
                "username": "testuser",
                "email": "invalid-email",
                "first_name": "Test",
                "last_name": "User",
                "role": "TECHNICIAN",
                "password": "password123",
                "is_active": True
            },
            "expected_status": 422
        },
        {
            "name": "Password too short",
            "data": {
                "username": "testuser",
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User",
                "role": "TECHNICIAN",
                "password": "123",  # Too short
                "is_active": True
            },
            "expected_status": 422
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/auth/register",
                json=test_case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == test_case['expected_status']:
                print(f"✅ Expected validation error: {response.status_code}")
            else:
                print(f"❌ Unexpected status: {response.status_code} (expected {test_case['expected_status']})")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Registration Endpoint with Provided Schema\n")
    
    # Test with the exact schema you provided
    test_registration_with_schema()
    
    # Test with realistic data
    test_with_real_data()
    
    # Test validation errors
    test_validation_errors()
    
    print("\n🎉 Schema testing completed!") 
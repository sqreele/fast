#!/usr/bin/env python3
"""
Test script for registration with property_ids
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/auth"

def test_registration_with_properties():
    """Test registration with property_ids included"""
    print("🧪 Testing Registration with Property IDs...")
    
    # Test data with property_ids
    test_user_data = {
        "username": "propertyuser",
        "email": "propertyuser@example.com",
        "first_name": "Property",
        "last_name": "User",
        "phone": "1234567890",
        "role": "TECHNICIAN",
        "is_active": True,
        "password": "testpass123",
        "property_ids": [1, 2]  # Multiple properties
    }
    
    print(f"Registration data: {json.dumps(test_user_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=test_user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Registration successful!")
            print(f"User ID: {data.get('id')}")
            print(f"Username: {data.get('username')}")
            print(f"Properties assigned: {test_user_data['property_ids']}")
            return True
        else:
            print(f"\n❌ Registration failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_registration_without_properties():
    """Test registration without property_ids"""
    print("\n🧪 Testing Registration without Property IDs...")
    
    test_user_data = {
        "username": "nopropertyuser",
        "email": "nopropertyuser@example.com",
        "first_name": "NoProperty",
        "last_name": "User",
        "phone": "1234567890",
        "role": "TECHNICIAN",
        "is_active": True,
        "password": "testpass123"
        # property_ids omitted
    }
    
    print(f"Registration data: {json.dumps(test_user_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=test_user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Registration successful!")
            print(f"User ID: {data.get('id')}")
            print(f"Username: {data.get('username')}")
            return True
        else:
            print(f"\n❌ Registration failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_properties_endpoint():
    """Test the properties endpoint to see available properties"""
    print("\n🧪 Testing Properties Endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/api/v1/properties/public")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            properties = response.json()
            print(f"✅ Found {len(properties)} properties:")
            for prop in properties:
                print(f"  - ID: {prop.get('id')}, Name: {prop.get('name')}")
            return properties
        else:
            print(f"❌ Failed to get properties: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def main():
    """Run all tests"""
    print("🚀 Testing Registration with Property IDs\n")
    
    # First, check available properties
    properties = test_properties_endpoint()
    
    # Test registration with properties
    test_registration_with_properties()
    
    # Test registration without properties
    test_registration_without_properties()
    
    print("\n🎉 Property registration testing completed!")

if __name__ == "__main__":
    main() 
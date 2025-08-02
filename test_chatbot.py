#!/usr/bin/env python3
"""
Test script for the Ceeva chatbot functionality.
This script tests the chatbot endpoints and verifies they work correctly.
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_chatbot_assist():
    """Test the chatbot assist endpoint"""
    print("Testing chatbot assist endpoint...")
    
    # Test data
    test_request = {
        "user_message": "Can you help me understand healthcare facility planning?",
        "session_context": {
            "last_simulation_result": {
                "regency_name": "Jakarta Selatan",
                "budget_used": 5000000000,
                "facilities_recommended": 3,
                "coverage_percentage": 75.5
            }
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chatbot/assist",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chatbot assist endpoint working!")
            print(f"Bot Response: {result.get('bot_response', 'No response')}")
            print(f"Suggested Actions: {len(result.get('suggested_actions', []))}")
            return True
        else:
            print(f"❌ Chatbot assist endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing chatbot assist: {e}")
        return False

def test_recent_simulations():
    """Test the recent simulations endpoint"""
    print("\nTesting recent simulations endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/chatbot/recent-simulations")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Recent simulations endpoint working!")
            print(f"Found {len(result)} recent simulations")
            return True
        else:
            print(f"❌ Recent simulations endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing recent simulations: {e}")
        return False

def test_store_simulation():
    """Test storing a simulation result"""
    print("\nTesting store simulation endpoint...")
    
    # Test simulation data
    test_simulation = {
        "regency_id": "550e8400-e29b-41d4-a716-446655440002",
        "regency_name": "Jakarta Selatan",
        "total_budget": 5000000000,
        "budget_used": 4500000000,
        "facilities_recommended": 3,
        "total_population_covered": 150000,
        "coverage_percentage": 75.5,
        "optimized_facilities": [
            {
                "latitude": -6.2088,
                "longitude": 106.8456,
                "facility_type": "Puskesmas",
                "estimated_cost": 2000000000,
                "population_covered": 50000
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chatbot/store-simulation",
            json=test_simulation,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Store simulation endpoint working!")
            print(f"Stored simulation ID: {result.get('simulation_id')}")
            return True
        else:
            print(f"❌ Store simulation endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing store simulation: {e}")
        return False

def main():
    """Run all chatbot tests"""
    print("🧪 Testing Ceeva Chatbot Functionality")
    print("=" * 50)
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code != 200:
            print("❌ Server is not running. Please start the server first.")
            return
    except:
        print("❌ Cannot connect to server. Please start the server first.")
        return
    
    print("✅ Server is running")
    
    # Run tests
    tests = [
        test_chatbot_assist,
        test_recent_simulations,
        test_store_simulation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All chatbot tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main() 
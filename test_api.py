#!/usr/bin/env python3
"""
Test the running FastAPI application with Gemini API
"""

import requests
import json
import time

def test_api_endpoints():
    """Test the FastAPI endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Testing FastAPI Application with Gemini...")
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test ready endpoint
    print("\n2. Testing ready endpoint...")
    try:
        response = requests.get(f"{base_url}/ready")
        if response.status_code == 200:
            print("✅ Ready check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Ready check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Ready check error: {e}")
    
    # Test single query (will use fallback due to quota)
    print("\n3. Testing single query...")
    query_data = {
        "query": "What is covered under dental procedures?",
        "context": {}
    }
    
    try:
        response = requests.post(
            f"{base_url}/query",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ Single query test passed")
            result = response.json()
            print(f"   Answer: {result.get('answer', 'No answer')[:100]}...")
            print(f"   Confidence: {result.get('confidence', 0)}")
        else:
            print(f"❌ Single query failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Single query error: {e}")
    
    # Test batch query
    print("\n4. Testing batch query...")
    batch_data = {
        "documents": "sample_document.pdf",  # This should be a real document URL
        "questions": [
            "What is the eligibility criteria?",
            "Are dental procedures covered?",
            "What is the deductible amount?"
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/batch-query",
            json=batch_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ Batch query test passed")
            result = response.json()
            print(f"   Processed {len(result.get('results', []))} queries")
            print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
        else:
            print(f"❌ Batch query failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Batch query error: {e}")

if __name__ == "__main__":
    test_api_endpoints()

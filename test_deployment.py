#!/usr/bin/env python3
"""
Production deployment test script for Render
"""
import asyncio
import json
import httpx
import sys

async def test_deployment(base_url):
    """Test the deployed API endpoints."""
    
    print(f"🧪 Testing Deployment: {base_url}")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        
        # Test 1: Health Check
        print("1. Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("   ✅ Health check passed")
                print(f"   📊 Status: {response.json()}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False
        
        # Test 2: Simple Query (if you have single query endpoint)
        print("\n2. Testing simple query endpoint...")
        try:
            simple_query = {
                "query": "What is the grace period for premium payment?",
                "document_url": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
            }
            response = await client.post(f"{base_url}/query", json=simple_query)
            if response.status_code == 200:
                print("   ✅ Simple query works")
            else:
                print(f"   ⚠️ Simple query returned: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Simple query not available or error: {e}")
        
        # Test 3: Batch Query (main test)
        print("\n3. Testing batch query endpoint...")
        try:
            batch_request = {
                "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
                "questions": [
                    "What is the grace period for premium payment?",
                    "What is the No Claim Discount (NCD) offered?",
                    "What is the waiting period for cataract surgery?"
                ]
            }
            
            print("   📤 Sending batch query request...")
            response = await client.post(f"{base_url}/batch-query", json=batch_request)
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Batch query successful!")
                print(f"   📊 Received {len(result.get('answers', []))} answers")
                
                # Show first answer as sample
                if result.get('answers'):
                    print(f"\n   📝 Sample Answer:")
                    print(f"   Q: {batch_request['questions'][0]}")
                    print(f"   A: {result['answers'][0][:200]}...")
                
                return True
            else:
                print(f"   ❌ Batch query failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Batch query error: {e}")
            return False

async def main():
    """Main test function."""
    
    if len(sys.argv) < 2:
        print("Usage: python test_deployment.py <your-render-url>")
        print("Example: python test_deployment.py https://your-app.onrender.com")
        return
    
    base_url = sys.argv[1].rstrip('/')
    
    print("🚀 Bajaj Hackathon - LLM Query System")
    print("🌐 Production Deployment Test")
    print("=" * 60)
    
    success = await test_deployment(base_url)
    
    if success:
        print("\n🎉 Deployment test successful!")
        print("Your API is working correctly on Render!")
        print(f"\n📋 API Documentation: {base_url}/docs")
        print(f"🔗 Health Check: {base_url}/health")
        print(f"🎯 Batch Query: {base_url}/batch-query")
    else:
        print("\n❌ Deployment test failed!")
        print("Check the Render logs for more details.")

if __name__ == "__main__":
    asyncio.run(main())

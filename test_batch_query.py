#!/usr/bin/env python3
"""
Test script for the new batch query endpoint
"""
import asyncio
import json
import httpx

async def test_batch_query():
    """Test the batch query endpoint with sample data."""
    
    # Sample batch request in the exact format you specified
    batch_request = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?",
            "What is the waiting period for cataract surgery?",
            "Are the medical expenses for an organ donor covered under this policy?",
            "What is the No Claim Discount (NCD) offered in this policy?",
            "Is there a benefit for preventive health check-ups?",
            "How does the policy define a 'Hospital'?",
            "What is the extent of coverage for AYUSH treatments?",
            "Are there any sub-limits on room rent and ICU charges for Plan A?"
        ]
    }
    
    print("Testing batch query endpoint...")
    print(f"Document: {batch_request['documents'][:80]}...")
    print(f"Number of questions: {len(batch_request['questions'])}")
    print("\nQuestions:")
    for i, question in enumerate(batch_request['questions'], 1):
        print(f"{i}. {question}")
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout
            print("\nSending request to http://127.0.0.1:8000/batch-query...")
            
            response = await client.post(
                "http://127.0.0.1:8000/batch-query",
                json=batch_request
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Success! Batch query completed.")
                print("\nAnswers:")
                
                for i, answer in enumerate(result.get("answers", []), 1):
                    print(f"\n{i}. Q: {batch_request['questions'][i-1]}")
                    print(f"   A: {answer}")
                
                # Also save the result to a file
                with open("batch_query_result.json", "w") as f:
                    json.dump({
                        "request": batch_request,
                        "response": result
                    }, f, indent=2)
                
                print(f"\n📁 Full result saved to batch_query_result.json")
                
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing Batch Query Endpoint")
    print("=" * 50)
    asyncio.run(test_batch_query())

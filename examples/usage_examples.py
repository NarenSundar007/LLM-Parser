#!/usr/bin/env python3
"""
Example usage script for the LLM-Powered Query-Retrieval System.
This script demonstrates various use cases across different domains.
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_system_health():
    """Test if the system is running and healthy."""
    print("🔍 Testing system health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ System Status: {health.get('status', 'unknown')}")
            print(f"📊 Vector Store: {health.get('vector_db_status', 'unknown')}")
            print(f"🤖 LLM Status: {health.get('llm_status', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to system: {e}")
        return False

def process_query(query: str, document_url: str = None, domain: str = "general") -> Dict[str, Any]:
    """Process a query with optional document URL."""
    print(f"\n🔍 Processing {domain} query: {query}")
    
    payload = {"query": query}
    if document_url:
        payload["document_url"] = document_url
        print(f"📄 Document URL: {document_url}")
    
    try:
        response = requests.post(f"{BASE_URL}/query", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Answer: {result['answer']}")
            print(f"🎯 Confidence: {result['confidence']:.2f}")
            if result['conditions']:
                print(f"⚠️  Conditions: {', '.join(result['conditions'])}")
            print(f"📖 Clause: {result['clause'][:100]}...")
            print(f"💭 Rationale: {result['rationale'][:150]}...")
            if result['page_references']:
                print(f"📄 Page References: {result['page_references']}")
            return result
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            return {}
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return {}

def test_insurance_use_case():
    """Test insurance domain queries."""
    print("\n" + "="*50)
    print("🏥 INSURANCE USE CASE TESTING")
    print("="*50)
    
    # Example insurance document URL (replace with actual)
    insurance_doc = "https://example.com/insurance_policy.pdf"
    
    queries = [
        "Does this policy cover knee surgery?",
        "What is the annual deductible for family coverage?",
        "Are prescription drugs covered under this plan?",
        "Is mental health therapy covered?",
        "What are the co-payment requirements for specialist visits?"
    ]
    
    for query in queries:
        process_query(query, insurance_doc, "insurance")
        time.sleep(1)  # Be nice to the API

def test_legal_use_case():
    """Test legal domain queries."""
    print("\n" + "="*50)
    print("⚖️  LEGAL USE CASE TESTING")
    print("="*50)
    
    legal_doc = "https://example.com/contract.pdf"
    
    queries = [
        "What are the termination clauses in this contract?",
        "What is the force majeure provision?",
        "What are the payment terms and conditions?",
        "Are there any non-compete clauses?",
        "What is the governing law for this agreement?"
    ]
    
    for query in queries:
        process_query(query, legal_doc, "legal")
        time.sleep(1)

def test_hr_use_case():
    """Test HR domain queries."""
    print("\n" + "="*50)
    print("👥 HR USE CASE TESTING")
    print("="*50)
    
    hr_doc = "https://example.com/employee_handbook.pdf"
    
    queries = [
        "What is the parental leave policy?",
        "How many vacation days do employees get?",
        "What is the remote work policy?",
        "What are the performance review procedures?",
        "What benefits are available to part-time employees?"
    ]
    
    for query in queries:
        process_query(query, hr_doc, "hr")
        time.sleep(1)

def test_compliance_use_case():
    """Test compliance domain queries."""
    print("\n" + "="*50)
    print("📋 COMPLIANCE USE CASE TESTING")
    print("="*50)
    
    compliance_doc = "https://example.com/privacy_policy.pdf"
    
    queries = [
        "Does this policy comply with GDPR requirements?",
        "What data retention policies are in place?",
        "How is user consent obtained for data processing?",
        "What are the data breach notification procedures?",
        "Are there provisions for data subject rights?"
    ]
    
    for query in queries:
        process_query(query, compliance_doc, "compliance")
        time.sleep(1)

def test_semantic_search():
    """Test semantic search functionality."""
    print("\n" + "="*50)
    print("🔍 SEMANTIC SEARCH TESTING")
    print("="*50)
    
    search_queries = [
        "surgical procedures",
        "employee benefits",
        "contract termination",
        "data privacy"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Searching for: {query}")
        try:
            response = requests.post(f"{BASE_URL}/search", params={"query": query, "k": 3})
            if response.status_code == 200:
                results = response.json()
                print(f"Found {results['count']} results:")
                for i, result in enumerate(results['results'][:2], 1):
                    print(f"  {i}. Score: {result['similarity_score']:.3f}")
                    print(f"     Content: {result['content'][:100]}...")
                    print(f"     Page: {result['page_number']}")
            else:
                print(f"❌ Search failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Search request failed: {e}")

def test_document_processing():
    """Test document processing functionality."""
    print("\n" + "="*50)
    print("📄 DOCUMENT PROCESSING TESTING")
    print("="*50)
    
    # Test document processing
    test_doc_url = "https://example.com/test_document.pdf"
    
    print(f"📤 Processing document: {test_doc_url}")
    try:
        response = requests.post(f"{BASE_URL}/documents/process", 
                               params={"blob_url": test_doc_url})
        if response.status_code == 200:
            result = response.json()
            doc_id = result.get("document_id")
            print(f"✅ Document processed: {doc_id}")
            
            # Check document status
            if doc_id:
                status_response = requests.get(f"{BASE_URL}/documents/{doc_id}/status")
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(f"📊 Status: {status}")
                
        else:
            print(f"❌ Document processing failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Document processing request failed: {e}")

def show_system_stats():
    """Show system statistics."""
    print("\n" + "="*50)
    print("📊 SYSTEM STATISTICS")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print("System Health:")
            for key, value in stats.get('system_health', {}).items():
                print(f"  {key}: {value}")
            
            print("\nDocument Statistics:")
            doc_stats = stats.get('documents_stats', {})
            for key, value in doc_stats.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats request failed: {e}")

def main():
    """Main testing function."""
    print("🚀 LLM-Powered Query-Retrieval System - Example Usage")
    print("="*60)
    
    # Test system health first
    if not test_system_health():
        print("❌ System is not healthy. Please check the server.")
        return
    
    print("\n⚠️  Note: This demo uses example URLs.")
    print("Replace with actual PDF blob URLs for real testing.\n")
    
    # Run all test cases
    try:
        # Test different domain use cases
        test_insurance_use_case()
        test_legal_use_case()
        test_hr_use_case()
        test_compliance_use_case()
        
        # Test search functionality
        test_semantic_search()
        
        # Test document processing
        test_document_processing()
        
        # Show system statistics
        show_system_stats()
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("🔗 API Documentation: http://localhost:8000/docs")
        print("🏥 Health Check: http://localhost:8000/health")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user.")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test script for Gemini API integration
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.config import settings
from src.llm_parser import LLMParser
from loguru import logger

async def test_gemini_integration():
    """Test the Gemini API integration"""
    
    print("🔍 Testing Gemini API Integration...")
    print(f"LLM Provider: {settings.llm_provider}")
    print(f"LLM Model: {settings.llm_model}")
    print(f"Gemini API Key: {'✅ Set' if settings.gemini_api_key else '❌ Not Set'}")
    
    # Initialize the LLM parser
    llm_parser = LLMParser()
    
    # Test query
    test_query = "What is the coverage for dental procedures?"
    
    print(f"\n📝 Testing query: '{test_query}'")
    
    try:
        # Parse the query
        parsed_result = await llm_parser.parse_query(test_query)
        
        print("✅ Query parsing successful!")
        print(f"Intent: {parsed_result.intent}")
        print(f"Target Subject: {parsed_result.target_subject}")
        print(f"Keywords: {parsed_result.keywords}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during query parsing: {e}")
        logger.error(f"Gemini test failed: {e}")
        return False

async def test_direct_gemini_call():
    """Test direct Gemini API call"""
    
    print("\n🧪 Testing direct Gemini API call...")
    
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        
        # Initialize model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test prompt
        prompt = "Explain what a health insurance policy is in one sentence."
        
        # Generate response
        response = model.generate_content(prompt)
        
        print("✅ Direct Gemini API call successful!")
        print(f"Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct Gemini API call failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Gemini Integration Tests...")
    
    # Test direct API call first
    asyncio.run(test_direct_gemini_call())
    
    # Test integrated parser
    success = asyncio.run(test_gemini_integration())
    
    if success:
        print("\n🎉 All tests passed! Gemini integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the configuration and try again.")

#!/usr/bin/env python3
"""
Test script to verify Groq API connectivity
"""
import os
import sys

# Set the API key from environment variable
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")

# Clear any proxy settings that might interfere
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
for var in proxy_vars:
    if var in os.environ:
        del os.environ[var]

try:
    from groq import Groq
    import httpx
    
    # Create custom HTTP client without proxy settings
    custom_client = httpx.Client()
    
    # Initialize client with custom HTTP client
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
        http_client=custom_client
    )
    
    print("✅ Groq client initialized successfully!")
    print(f"Client type: {type(client)}")
    
    # Test a simple API call with an available model
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Use available model
            messages=[
                {"role": "user", "content": "Say hello in JSON format with a 'message' field."}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        print("✅ API call successful!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as api_error:
        print(f"❌ API call failed: {api_error}")
        
except Exception as e:
    print(f"❌ Failed to initialize Groq client: {e}")
    print("This might be due to proxy settings or network configuration.")

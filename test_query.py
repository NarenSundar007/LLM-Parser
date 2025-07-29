#!/usr/bin/env python3
"""
Test script to verify the query processing works
"""
import asyncio
import json
from src.llm_parser import LLMParser

async def test_llm_parsing():
    print("Testing LLM parsing...")
    
    llm = LLMParser()
    print(f"LLM Provider: {llm.provider}")
    print(f"LLM Model: {llm.model}")
    
    if llm.provider == "groq":
        print("✅ Groq client initialized successfully!")
        
        # Test a simple response generation
        query = "What is the grace period for premium payment?"
        best_clause = "A grace period of thirty days is provided for premium payment after the due date to renew or continue the first policy."
        logic_eval = {
            "answer": "Yes, 30 days",
            "meets_criteria": True,
            "applicable_conditions": ["Policy must be active"],
            "rationale": "Policy clearly states grace period",
            "confidence_score": 0.9,
            "supporting_evidence": ["grace period of thirty days"]
        }
        page_refs = [1, 6]
        
        try:
            result = await llm.generate_final_response(query, best_clause, logic_eval, page_refs)
            print("✅ Final response generation successful!")
            print(f"Result: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"❌ Final response generation failed: {e}")
    
    else:
        print(f"ℹ️  Using fallback mode: {llm.provider}")

if __name__ == "__main__":
    asyncio.run(test_llm_parsing())

#!/usr/bin/env python3
"""
Simple test script for Ollama integration
"""

import asyncio
import json
from langchain_community.llms import Ollama

async def test_ollama():
    """Test Ollama with a simple prompt"""
    try:
        # Initialize Ollama
        llm = Ollama(
            model="llama4:16x17b",
            base_url="http://localhost:11434"
        )
        
        # Simple prompt
        prompt = "You are a helpful assistant. Describe a cat in one sentence. Return as JSON: {\"description\": \"your description\"}"
        
        print("Testing Ollama...")
        result = await llm.ainvoke(prompt)
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ollama()) 
#!/usr/bin/env python3
"""
Direct test script for Ollama integration using HTTP calls
"""

import asyncio
import httpx
import json

async def test_ollama_direct():
    """Test Ollama directly with HTTP calls"""
    try:
        client = httpx.AsyncClient()
        
        payload = {
            "model": "llama4:16x17b",
            "prompt": "You are a helpful assistant. Describe a cat in one sentence.",
            "stream": False
        }
        
        print("Testing Ollama directly...")
        response = await client.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=60.0
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Response: {result.get('response', '')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ollama_direct()) 
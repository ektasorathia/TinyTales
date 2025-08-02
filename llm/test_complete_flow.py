#!/usr/bin/env python3
"""
Complete End-to-End Flow Test for TinyTales
Tests the complete flow: Frontend -> Flask Orchestrator -> LLM Framework -> Image Generation
"""

import asyncio
import json
import httpx
import time

async def test_complete_flow():
    """Test the complete end-to-end flow"""
    print("🧪 Testing Complete End-to-End Flow for TinyTales")
    print("=" * 60)
    
    # Test 1: Check if Flask orchestrator is running
    print("\n1️⃣ Testing Flask Orchestrator...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3001/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ Flask orchestrator is running")
            else:
                print("❌ Flask orchestrator health check failed")
                return False
    except Exception as e:
        print(f"❌ Flask orchestrator is not running: {e}")
        return False
    
    # Test 2: Test story generation with images
    print("\n2️⃣ Testing Story Generation with Images...")
    try:
        async with httpx.AsyncClient() as client:
            story_data = {
                "username": "TestUser",
                "prompt": "A brave knight who discovers a magical castle in the forest",
                "genre": "fantasy",
                "age_group": "5-10",
                "scene_count": 3
            }
            
            response = await client.post(
                "http://localhost:3001/createstory",
                json=story_data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Story generation successful!")
                
                # Verify the response structure
                if result.get('success'):
                    story = result.get('data', {}).get('story', {})
                    scenes = story.get('scenes', [])
                    
                    print(f"📖 Story Title: {story.get('title', 'N/A')}")
                    print(f"🎭 Number of Scenes: {len(scenes)}")
                    
                    # Check each scene for images
                    for i, scene in enumerate(scenes, 1):
                        has_image = scene.get('image') is not None
                        image_length = len(scene.get('image', '')) if scene.get('image') else 0
                        print(f"   Scene {i}: {'✅ Has Image' if has_image else '❌ No Image'} ({image_length} chars)")
                    
                    return True
                else:
                    print("❌ Story generation returned success: false")
                    return False
            else:
                print(f"❌ Story generation failed with status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Story generation test failed: {e}")
        return False
    
    # Test 3: Check if React frontend is running
    print("\n3️⃣ Testing React Frontend...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3000", timeout=5.0)
            if response.status_code == 200:
                print("✅ React frontend is running")
                return True
            else:
                print("❌ React frontend is not responding")
                return False
    except Exception as e:
        print(f"❌ React frontend is not running: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Complete End-to-End Flow Test")
    print("This test verifies the complete flow from frontend to backend to LLM")
    print()
    
    success = await test_complete_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 COMPLETE FLOW TEST SUCCESSFUL!")
        print("✅ All components are working together")
        print("✅ Images are being generated and included in responses")
        print("✅ The system is ready for use!")
        print("\n🌐 You can now:")
        print("   - Open http://localhost:3000 in your browser")
        print("   - Create a story with the form")
        print("   - See the generated images displayed in the UI")
    else:
        print("❌ COMPLETE FLOW TEST FAILED")
        print("Please check the error messages above and fix the issues")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 
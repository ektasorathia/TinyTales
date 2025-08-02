#!/usr/bin/env python3
"""
Test script for the execute method in GenerateStoryTool
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_execute_method():
    """Test the execute method of GenerateStoryTool"""
    try:
        from tools.generate_story.tool import GenerateStoryTool
        from tools.generate_story.schemas import GenerateStoryRequest
        
        print("Testing GenerateStoryTool execute method...")
        
        # Create tool instance
        tool = GenerateStoryTool()
        
        # Create test request
        request = GenerateStoryRequest(
            username="TestUser",
            prompt="A brave little mouse who discovers a magical garden",
            age_group="3",
            scene_count=5,
            genre="kids"
        )
        
        print(f"Request: {request}")
        
        # Execute the tool
        response = await tool.execute(request)
        
        print(f"Response success: {response.success}")
        if response.success:
            print(f"Story title: {response.data.title}")
            print(f"Number of scenes: {len(response.data.scenes)}")
            for i, scene in enumerate(response.data.scenes):
                print(f"Scene {i+1}: {scene.description[:50]}...")
        else:
            print(f"Error: {response.error}")
        
        print("✅ Execute method test completed!")
        
    except Exception as e:
        print(f"❌ Error testing execute method: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_execute_method())

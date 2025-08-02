#!/usr/bin/env python3
"""
Test script for complete story generation with images
"""

import asyncio
import json
from tools.generate_story.tool import GenerateStoryTool
from tools.generate_story.schemas import GenerateStoryRequest

async def test_complete_story():
    """Test the complete story generation with images"""
    try:
        print("Testing complete story generation with images...")
        
        # Initialize the model manager
        from app.llm.manager import ModelManager
        ModelManager.initialize()
        print("✅ ModelManager initialized")
        
        # Create tool instance
        tool = GenerateStoryTool()
        
        # Create request
        request = GenerateStoryRequest(
            username="TestUser",
            prompt="A brave knight who discovers a magical castle",
            age_group="children",
            genre="fantasy",
            scene_count=3  # Test with 3 scenes for faster testing
        )
        
        print(f"Generating story for: {request.prompt}")
        print(f"User: {request.username}")
        print(f"Genre: {request.genre}")
        print(f"Scenes: {request.scene_count}")
        
        # Execute the tool
        result = await tool.execute(request)
        
        if result and hasattr(result, 'result'):
            print("✅ Story generation successful!")
            
            # Parse the result
            try:
                story_data = json.loads(result.result)
                print(f"Story title: {story_data.get('title', 'Unknown')}")
                print(f"Story theme: {story_data.get('theme', 'Unknown')}")
                
                scenes = story_data.get('scenes', [])
                print(f"Number of scenes: {len(scenes)}")
                
                for i, scene in enumerate(scenes, 1):
                    scene_num = scene.get('scene_number', i)
                    story_text = scene.get('story_text', 'No description')
                    has_image = 'image' in scene and scene['image']
                    
                    print(f"  Scene {scene_num}:")
                    print(f"    Text: {story_text[:50]}...")
                    print(f"    Has image: {'✅' if has_image else '❌'}")
                    
                    if has_image:
                        image_data = scene['image']
                        if image_data.startswith('data:image/png;base64,'):
                            print(f"    Image format: ✅ Valid base64")
                            print(f"    Image size: {len(image_data)} characters")
                        else:
                            print(f"    Image format: ❌ Invalid format")
                
                print("\n🎉 Complete story generation test successful!")
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse story JSON: {e}")
                print(f"Raw result: {result.result[:200]}...")
        else:
            print("❌ Story generation failed - no result returned")
            
    except Exception as e:
        print(f"❌ Error during story generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_story()) 
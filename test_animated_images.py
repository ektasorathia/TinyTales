#!/usr/bin/env python3
"""
Test script for animated image generation improvements
"""

import asyncio
import sys
import os

# Add the llm directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'llm'))

from tools.generate_story.image_generator import image_generator

async def test_animated_image_generation():
    """Test the improved animated image generation"""
    print("🎨 Testing Animated Image Generation")
    print("=" * 50)
    
    # Test prompts for different scenes
    test_prompts = [
        {
            "prompt": "A little rabbit sitting in a cozy nest made of soft grasses and flowers with the big, silver moon shining brightly outside its window",
            "style": "kids",
            "description": "Rabbit in cozy nest with moon"
        },
        {
            "prompt": "A brave knight standing in front of a majestic castle with a shining sword",
            "style": "fantasy",
            "description": "Knight in front of castle"
        }
    ]
    
    print("Generating animated images for different scenes...")
    print()
    
    for i, test_case in enumerate(test_prompts, 1):
        print(f"{i}. {test_case['description']}")
        print(f"   Prompt: {test_case['prompt']}")
        print(f"   Style: {test_case['style']}")
        
        try:
            # Generate the animated image
            image_data = await image_generator.generate_image(
                prompt=test_case['prompt'],
                style=test_case['style']
            )
            
            if image_data:
                print(f"   ✅ Generated animated image successfully!")
                print(f"   📏 Image size: {len(image_data)} characters")
            else:
                print(f"   ❌ Failed to generate image")
                
        except Exception as e:
            print(f"   ❌ Error generating image: {str(e)}")
        
        print()
    
    print("🎉 Animated Image Generation Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_animated_image_generation()) 
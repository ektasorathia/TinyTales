#!/usr/bin/env python3
"""
Test script for image generation functionality
"""

import asyncio
import json
from tools.generate_story.image_generator import image_generator

async def test_image_generation():
    """Test the image generation functionality"""
    try:
        print("Testing image generation...")
        
        # Test with a simple prompt
        prompt = "A brave knight standing on a mountain peak at sunset"
        style = "fantasy digital art"
        
        print(f"Generating image for: {prompt}")
        print(f"Style: {style}")
        
        # Generate image
        image_data = await image_generator.generate_image(prompt, style)
        
        if image_data:
            print("✅ Image generation successful!")
            print(f"Image data length: {len(image_data)} characters")
            print(f"Image starts with: {image_data[:50]}...")
            
            # Test if it's valid base64
            if image_data.startswith("data:image/png;base64,"):
                print("✅ Valid base64 image format")
            else:
                print("❌ Invalid image format")
        else:
            print("❌ Image generation failed")
            
    except Exception as e:
        print(f"❌ Error during image generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_image_generation()) 
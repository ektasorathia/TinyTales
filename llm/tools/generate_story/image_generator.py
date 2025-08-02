"""
Image Generator Module

This module handles image generation for story scenes using various AI image generation services.
"""

import base64
import io
import httpx
import json
from typing import Optional, Dict, Any
from loguru import logger
from PIL import Image, ImageDraw, ImageFont
import os


class ImageGenerator:
    """Base class for image generation"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.stability_api_key = os.getenv('STABILITY_API_KEY')
    
    async def generate_image(self, prompt: str, style: str = "digital art") -> Optional[str]:
        """
        Generate an image from a prompt and return as base64 string
        
        Args:
            prompt: Text description of the image to generate
            style: Artistic style for the image
            
        Returns:
            Base64 encoded image string or None if generation fails
        """
        try:
            # Try OpenAI DALL-E first
            if self.api_key:
                return await self._generate_with_dalle(prompt, style)
            
            # Try Stability AI if available
            elif self.stability_api_key:
                return await self._generate_with_stability(prompt, style)
            
            # Fallback to mock image generation
            else:
                return await self._generate_mock_image(prompt, style)
                
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return await self._generate_mock_image(prompt, style)
    
    async def _generate_with_dalle(self, prompt: str, style: str) -> Optional[str]:
        """Generate image using OpenAI DALL-E"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "dall-e-3",
                        "prompt": f"{prompt}, {style} style, high quality, detailed",
                        "n": 1,
                        "size": "1024x1024",
                        "response_format": "b64_json"
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data") and len(data["data"]) > 0:
                        return f"data:image/png;base64,{data['data'][0]['b64_json']}"
                
                logger.warning(f"DALL-E API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"DALL-E generation failed: {str(e)}")
            return None
    
    async def _generate_with_stability(self, prompt: str, style: str) -> Optional[str]:
        """Generate image using Stability AI"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                    headers={
                        "Authorization": f"Bearer {self.stability_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "text_prompts": [
                            {
                                "text": f"{prompt}, {style} style, high quality, detailed",
                                "weight": 1
                            }
                        ],
                        "cfg_scale": 7,
                        "height": 1024,
                        "width": 1024,
                        "samples": 1,
                        "steps": 30
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("artifacts") and len(data["artifacts"]) > 0:
                        image_data = base64.b64decode(data["artifacts"][0]["base64"])
                        return f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
                
                logger.warning(f"Stability API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Stability generation failed: {str(e)}")
            return None
    
    async def _generate_mock_image(self, prompt: str, style: str) -> str:
        """Generate a mock image with text overlay"""
        try:
            # Create a simple image with the prompt text
            width, height = 512, 512
            
            # Create image with gradient background
            image = Image.new('RGB', (width, height), color='#87CEEB')  # Sky blue
            draw = ImageDraw.Draw(image)
            
            # Add gradient effect
            for y in range(height):
                r = int(135 + (y / height) * 40)  # Blue gradient
                g = int(206 + (y / height) * 20)
                b = int(235 + (y / height) * 20)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            # Add text
            try:
                # Try to use a default font
                font = ImageFont.load_default()
            except:
                font = None
            
            # Split prompt into lines
            words = prompt.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if len(test_line) > 30:  # Approximate character limit
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            
            if current_line:
                lines.append(current_line)
            
            # Draw text lines
            y_position = height // 2 - (len(lines) * 20) // 2
            for line in lines:
                # Get text size
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center the text
                x = (width - text_width) // 2
                y = y_position
                
                # Draw text with outline
                draw.text((x-1, y-1), line, fill='black', font=font)
                draw.text((x+1, y-1), line, fill='black', font=font)
                draw.text((x-1, y+1), line, fill='black', font=font)
                draw.text((x+1, y+1), line, fill='black', font=font)
                draw.text((x, y), line, fill='white', font=font)
                
                y_position += text_height + 10
            
            # Add style indicator
            style_text = f"Style: {style}"
            draw.text((10, height - 30), style_text, fill='white', font=font)
            
            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Mock image generation failed: {str(e)}")
            # Return a simple colored rectangle as fallback
            image = Image.new('RGB', (512, 512), color='#FF6B6B')
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"


# Global instance
image_generator = ImageGenerator() 
"""
Story generation prompts for the Generate Story Tool
"""

STORY_GENERATION_PROMPT = """
You are a creative storyteller who creates engaging picture stories for {age_group}.

Create a {genre} story based on the following prompt: "{prompt}"

Requirements:
- Create exactly {scene_count} scenes
- Each scene should be engaging and visually descriptive
- The story should have a clear beginning, middle, and end
- Make it appropriate for {age_group}
- Include elements that would make great images

Please structure your response as a JSON object with the following format:
{{
    "title": "Story title",
    "scenes": [
        {{
            "id": 1,
            "description": "Detailed scene description",
            "imagePrompt": "Visual prompt for image generation"
        }},
        // ... more scenes
    ]
}}

The imagePrompt should be descriptive and include visual elements like:
- Setting and environment
- Characters and their appearance
- Actions and emotions
- Colors and lighting
- Style suggestions (e.g., "colorful", "whimsical", "dramatic")

Make sure the story flows naturally from scene to scene and creates an engaging narrative.
"""

IMAGE_GENERATION_PROMPT = """
Create a detailed image prompt for the following scene:

Scene Description: {scene_description}

Requirements:
- Include visual style (e.g., "watercolor", "digital art", "photorealistic")
- Specify mood and atmosphere
- Include color palette suggestions
- Mention any specific artistic influences
- Make it suitable for {age_group}

The image prompt should be detailed enough for an AI image generator to create a compelling visual.
"""

STORY_VALIDATION_PROMPT = """
Please validate this story structure and ensure it meets the requirements:

Story: {story_json}

Requirements to check:
1. Has exactly {scene_count} scenes
2. Each scene has a description and imagePrompt
3. Story flows logically from beginning to end
4. Appropriate for {age_group}
5. Fits the {genre} genre
6. Image prompts are detailed and visual

If there are any issues, please provide specific feedback for improvement.
"""

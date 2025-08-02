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
- Include elements that would make great animated images

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
- Setting and environment with vibrant colors
- Characters with expressive faces and animated poses
- Actions and emotions that convey movement
- Bright, cheerful lighting and atmosphere
- Animated/cartoon style with rounded shapes and bold colors
- Whimsical and playful elements suitable for children

Make sure the story flows naturally from scene to scene and creates an engaging narrative that will look great as animated illustrations.
"""

IMAGE_GENERATION_PROMPT = """
Create a detailed animated image prompt for the following scene:

Scene Description: {scene_description}

Requirements:
- Use animated/cartoon style with vibrant colors
- Include expressive characters with big eyes and friendly faces
- Add whimsical and playful elements
- Use bright, cheerful lighting
- Include rounded shapes and bold outlines
- Make it suitable for {age_group} with a storybook feel
- Add magical or fantastical elements when appropriate

The image prompt should be detailed enough for an AI image generator to create a compelling animated visual that looks like it belongs in a children's storybook.
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
6. Image prompts are detailed and include animated/cartoon style elements
7. Visual descriptions are vibrant and engaging

If there are any issues, please provide specific feedback for improvement.
"""

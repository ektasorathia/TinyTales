#!/usr/bin/env python3
"""
Test script to verify the execute method structure without requiring API keys
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_execute_structure():
    """Test the execute method structure of GenerateStoryTool"""
    try:
        from tools.generate_story.tool import GenerateStoryTool
        from tools.generate_story.schemas import GenerateStoryRequest
        
        print("Testing GenerateStoryTool execute method structure...")
        
        # Create tool instance
        tool = GenerateStoryTool()
        
        # Test that the tool implements ToolInterface
        print(f"✅ Tool name: {tool.name}")
        print(f"✅ Tool description: {tool.description}")
        print(f"✅ Input schema: {tool.get_input_schema()}")
        print(f"✅ Output schema: {tool.get_output_schema()}")
        
        # Create test request
        request = GenerateStoryRequest(
            username="TestUser",
            prompt="A brave little mouse who discovers a magical garden",
            age_group="3",
            scene_count=5,
            genre="kids"
        )
        
        print(f"✅ Request created: {request.username} - {request.prompt}")
        
        # Test that the execute method exists and has correct signature
        if hasattr(tool, 'execute'):
            print("✅ Execute method exists")
            
            # Test that it's callable
            if callable(tool.execute):
                print("✅ Execute method is callable")
            else:
                print("❌ Execute method is not callable")
        else:
            print("❌ Execute method does not exist")
        
        # Test that the tool has the required LLM integration methods
        if hasattr(tool, '_generate_story_with_llm'):
            print("✅ _generate_story_with_llm method exists")
        else:
            print("❌ _generate_story_with_llm method does not exist")
            
        if hasattr(tool, '_parse_llm_response'):
            print("✅ _parse_llm_response method exists")
        else:
            print("❌ _parse_llm_response method does not exist")
        
        print("\n🎉 Execute method structure test completed successfully!")
        print("\nTo test with actual LLM calls, you need to:")
        print("1. Set your OPENAI_API_KEY in the .env file")
        print("2. Run: python test_execute_method.py")
        
    except Exception as e:
        print(f"❌ Error testing execute method structure: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_execute_structure())

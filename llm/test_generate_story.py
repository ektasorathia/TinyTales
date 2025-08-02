#!/usr/bin/env python3
"""
Test script for the generate-story endpoint
"""
import requests
import json

BASE_URL = 'http://localhost:8000'

def test_generate_story():
    """Test the generate-story endpoint"""
    try:
        data = {
            'username': 'TestUser',
            'prompt': 'A brave little mouse who discovers a magical garden'
        }
        
        print(f'Testing generate-story endpoint...')
        print(f'Request data: {json.dumps(data, indent=2)}')
        
        response = requests.post(f'{BASE_URL}/generate-story', json=data)
        
        print(f'Response status: {response.status_code}')
        print(f'Response data: {json.dumps(response.json(), indent=2)}')
        
        if response.status_code == 200:
            print('✅ Generate story endpoint test passed!')
        else:
            print('❌ Generate story endpoint test failed!')
            
    except requests.exceptions.ConnectionError:
        print('❌ Could not connect to the API. Make sure it\'s running on port 8000.')
    except Exception as e:
        print(f'❌ Error testing endpoint: {str(e)}')

if __name__ == '__main__':
    test_generate_story()

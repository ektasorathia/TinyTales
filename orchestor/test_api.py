#!/usr/bin/env python3
"""
Simple test script for the TinyTales API
"""
import requests
import json

BASE_URL = 'http://localhost:3001'

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/health')
        print(f'Health Check: {response.status_code}')
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print('❌ Could not connect to the API. Make sure it\'s running on port 3001.')
        return False

def test_create_story():
    """Test the create story endpoint"""
    try:
        data = {
            'username': 'TestUser',
            'prompt': 'A brave little mouse who discovers a magical garden'
        }
        
        response = requests.post(f'{BASE_URL}/createstory', json=data)
        print(f'\nCreate Story: {response.status_code}')
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print('❌ Could not connect to the API. Make sure it\'s running on port 3001.')
        return False

if __name__ == '__main__':
    print('🧪 Testing TinyTales API...\n')
    
    health_ok = test_health()
    story_ok = test_create_story()
    
    if health_ok and story_ok:
        print('\n✅ All tests passed!')
    else:
        print('\n❌ Some tests failed.')

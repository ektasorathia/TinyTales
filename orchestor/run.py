#!/usr/bin/env python3
"""
TinyTales Orchestor API Runner
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3001))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f'🚀 Starting TinyTales Orchestor API on port {port}')
    print(f'📊 Health check: http://localhost:{port}/health')
    print(f'📝 Create story: POST http://localhost:{port}/createstory')
    
    app.run(host='0.0.0.0', port=port, debug=debug)

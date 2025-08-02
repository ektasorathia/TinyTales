# TinyTales - AI Picture Story Generator

A full-stack application that generates beautiful picture stories using AI. Users can input a prompt and receive a story with at least 5 scenes, each with generated images.

## Project Structure

```
TinyTales/
├── orchestor/          # Backend API and LLM orchestration (Python Flask)
│   ├── app.py          # Flask application with API endpoints
│   ├── run.py          # Runner script
│   ├── requirements.txt # Python dependencies
│   ├── test_api.py     # API test script
│   └── README.md       # Backend setup instructions
├── web/               # React TypeScript frontend
│   ├── src/           # Source code
│   ├── public/        # Public assets
│   ├── package.json   # Frontend dependencies
│   └── README.md      # Frontend setup instructions
└── README.md          # This file
```

## Quick Start

### Prerequisites

1. **Install Python 3.8+**:
   - Download from: https://python.org/
   - Or use Homebrew: `brew install python`

2. **Install Node.js and npm**:
   - Download from: https://nodejs.org/
   - Or use Homebrew: `brew install node`

### Backend Setup (Python Flask)

1. Navigate to the orchestor directory:
   ```bash
   cd orchestor
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the API server:
   ```bash
   python app.py
   ```
   
   The API will run on http://localhost:3001

### Frontend Setup (React TypeScript)

1. Open a new terminal and navigate to the web directory:
   ```bash
   cd web
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```
   
   The web app will open at http://localhost:3000

## API Endpoints

### POST /createstory
Creates a new story based on user input.

**Request Body:**
```json
{
  "username": "string",
  "prompt": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "username": "string",
    "prompt": "string",
    "story": {
      "title": "string",
      "scenes": [
        {
          "id": 1,
          "description": "string",
          "imagePrompt": "string",
          "image": "string|null"
        }
      ]
    },
    "createdAt": "string",
    "status": "string"
  }
}
```

### GET /health
Health check endpoint.

## Testing the API

You can test the API using the provided test script:

```bash
cd orchestor
python test_api.py
```

## Features

- 🎨 Beautiful, modern UI with gradient backgrounds
- 📝 User-friendly story creation form
- 🖼️ Display of story scenes with image placeholders
- 📱 Responsive design for all devices
- ⚡ Real-time API integration
- 🔄 RESTful API with proper error handling
- 🐍 Python Flask backend for easy LLM integration

## Next Steps

1. **LLM Integration**: Connect to OpenAI, Anthropic, or other LLM services for story generation
2. **Image Generation**: Integrate with DALL-E, Stable Diffusion, or similar services
3. **Database**: Add persistent storage for stories and user data
4. **Authentication**: Implement user authentication and story management
5. **Advanced Features**: Add story editing, sharing, and collaboration features

## Technology Stack

### Backend
- Python 3.8+ with Flask
- Flask-CORS for cross-origin requests
- python-dotenv for environment variable management
- Gunicorn for production deployment

### Frontend
- React 18 with TypeScript
- Modern CSS with gradients and animations
- Axios for API communication
- Responsive design

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the ISC License.

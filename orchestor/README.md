# TinyTales Orchestor API (Python)

This is the backend API for the TinyTales story generation application, built with Python Flask.

## Setup Instructions

1. **Install Python 3.8+** (if not already installed):
   - Download from: https://python.org/
   - Or use Homebrew: `brew install python`

2. **Create a virtual environment** (recommended):
   ```bash
   cd orchestor
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your configuration.

5. **Start the server**:
   ```bash
   python app.py
   ```
   
   Or use the runner script:
   ```bash
   ./run.py
   ```

## API Endpoints

### POST /createstory
Creates a new story based on user prompt.

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

## Environment Variables

Create a `.env` file with the following variables:
- `PORT`: Server port (default: 3001)
- `FLASK_ENV`: Set to 'development' for debug mode
- Add other environment variables as needed for LLM integration

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python app.py
```

### Running with Gunicorn (Production)
```bash
gunicorn -w 4 -b 0.0.0.0:3001 app:app
```

## Project Structure

```
orchestor/
├── app.py              # Main Flask application
├── run.py              # Runner script
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # This file
```

## Next Steps

1. Integrate with LLM service for story generation
2. Add image generation service integration
3. Implement database for story storage
4. Add authentication and user management
5. Add logging and monitoring

## Dependencies

- Flask: Web framework
- Flask-CORS: Cross-origin resource sharing
- python-dotenv: Environment variable management
- requests: HTTP library for external API calls
- gunicorn: WSGI server for production deployment

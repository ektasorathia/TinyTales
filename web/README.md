# TinyTales Web Application

A beautiful React TypeScript application for generating AI-powered picture stories.

## Features

- 🎨 Beautiful, modern UI with gradient backgrounds
- 📝 User-friendly story creation form
- 🖼️ Display of story scenes with image placeholders
- 📱 Responsive design for all devices
- ⚡ Real-time API integration

## Setup Instructions

1. **Install Node.js and npm** (if not already installed):
   - Download from: https://nodejs.org/
   - Or use Homebrew: `brew install node`

2. **Install dependencies**:
   ```bash
   cd web
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```
   
   The app will open at http://localhost:3000

4. **Build for production**:
   ```bash
   npm run build
   ```

## Project Structure

```
src/
├── components/          # React components
│   ├── StoryForm.tsx   # Story creation form
│   └── StoryDisplay.tsx # Story display component
├── services/           # API services
│   └── api.ts         # API client
├── types/             # TypeScript type definitions
│   └── index.ts       # Type definitions
├── App.tsx            # Main application component
├── App.css            # Application styles
├── index.tsx          # Application entry point
└── index.css          # Global styles
```

## API Integration

The application connects to the TinyTales Orchestor API running on port 3001. Make sure the API server is running before using the web application.

## Environment Variables

Create a `.env` file in the web directory if you need to customize the API URL:
```
REACT_APP_API_URL=http://localhost:3001
```

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## Dependencies

- React 18
- TypeScript
- Axios for API calls
- Modern CSS with gradients and animations

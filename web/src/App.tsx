import React, { useState } from 'react';
import './App.css';
import StoryForm from './components/StoryForm';
import StoryDisplay from './components/StoryDisplay';
import { CreateStoryRequest, Story } from './types';
import { storyService } from './services/api';

function App() {
  const [story, setStory] = useState<Story | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateStory = async (request: CreateStoryRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await storyService.createStory(request);
      if (response.success && response.data) {
        setStory(response.data);
      } else {
        setError(response.error || 'Failed to create story');
      }
    } catch (err) {
      setError('Failed to connect to the server. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎭 TinyTales</h1>
        <p>Create beautiful picture stories with AI</p>
      </header>
      
      <main className="App-main">
        {error && (
          <div className="error-message">
            <p>{error}</p>
            <button onClick={() => setError(null)}>Dismiss</button>
          </div>
        )}
        
        {!story ? (
          <StoryForm onSubmit={handleCreateStory} isLoading={isLoading} />
        ) : (
          <div className="story-container">
            <StoryDisplay story={story} />
            <button 
              className="new-story-btn"
              onClick={() => setStory(null)}
            >
              Create Another Story
            </button>
          </div>
        )}
      </main>
      
      <footer className="App-footer">
        <p>Powered by AI • Made with ❤️</p>
      </footer>
    </div>
  );
}

export default App;

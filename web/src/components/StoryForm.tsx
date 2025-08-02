import React, { useState } from 'react';
import { CreateStoryRequest } from '../types';

interface StoryFormProps {
  onSubmit: (request: CreateStoryRequest) => void;
  isLoading: boolean;
}

const StoryForm: React.FC<StoryFormProps> = ({ onSubmit, isLoading }) => {
  const [username, setUsername] = useState('');
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (username.trim() && prompt.trim()) {
      onSubmit({ username: username.trim(), prompt: prompt.trim() });
    }
  };

  return (
    <div className="story-form">
      <h2>Create Your TinyTale</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Your Name:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your name"
            required
            disabled={isLoading}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="prompt">Story Prompt:</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the story you want to create... (e.g., 'A brave little mouse who discovers a magical garden')"
            rows={4}
            required
            disabled={isLoading}
          />
        </div>
        
        <button type="submit" disabled={isLoading || !username.trim() || !prompt.trim()}>
          {isLoading ? 'Creating Story...' : 'Generate Story'}
        </button>
      </form>
    </div>
  );
};

export default StoryForm;

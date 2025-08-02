import React from 'react';
import { Story } from '../types';

interface StoryDisplayProps {
  story: Story | null;
}

const StoryDisplay: React.FC<StoryDisplayProps> = ({ story }) => {
  if (!story) return null;

  return (
    <div className="story-display">
      <h2>{story.story.title}</h2>
      <div className="story-meta">
        <p><strong>Created by:</strong> {story.username}</p>
        <p><strong>Prompt:</strong> {story.prompt}</p>
        <p><strong>Created:</strong> {new Date(story.createdAt).toLocaleString()}</p>
      </div>
      
      <div className="scenes-container">
        {story.story.scenes.map((scene) => (
          <div key={scene.id} className="scene-card">
            <div className="scene-image">
              {scene.image ? (
                <img src={scene.image} alt={scene.description} />
              ) : (
                <div className="image-placeholder">
                  <p>Image will be generated for:</p>
                  <p className="image-prompt">{scene.imagePrompt}</p>
                </div>
              )}
            </div>
            <div className="scene-content">
              <h3>Scene {scene.id}</h3>
              <p>{scene.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StoryDisplay;

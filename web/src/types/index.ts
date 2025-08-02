export interface StoryScene {
  id: number;
  description: string;
  imagePrompt: string;
  image: string | null;
}

export interface Story {
  id: string;
  username: string;
  prompt: string;
  story: {
    title: string;
    scenes: StoryScene[];
  };
  createdAt: string;
  status: string;
}

export interface CreateStoryRequest {
  username: string;
  prompt: string;
}

export interface CreateStoryResponse {
  success: boolean;
  data?: Story;
  error?: string;
}

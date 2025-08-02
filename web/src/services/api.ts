import axios from 'axios';
import { CreateStoryRequest, CreateStoryResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const storyService = {
  createStory: async (request: CreateStoryRequest): Promise<CreateStoryResponse> => {
    try {
      const response = await api.post('/createstory', request);
      return response.data;
    } catch (error) {
      console.error('Error creating story:', error);
      throw error;
    }
  },
};

export default api;

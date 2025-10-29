import axios from 'axios';

// Types for API responses
export interface Opportunity {
  id: string;
  name: string;
  value: number | null;
  stage: string;
  next_action_at: string;
  next_action_details: string | null;
}

export interface CompleteActionRequest {
  new_next_action_at: string;
  new_next_action_details: string;
}

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add tenant ID to all requests
api.interceptors.request.use((config) => {
  // For demo purposes, using a hardcoded tenant ID
  // In production, this would come from authentication context
  config.headers['X-Tenant-ID'] = 'demo-tenant-123';
  return config;
});

// API functions
export const opportunitiesApi = {
  // Get all due opportunities
  getDueOpportunities: async (): Promise<Opportunity[]> => {
    const response = await api.get('/opportunities/due');
    return response.data;
  },

  // Complete an action and set the next one
  completeAction: async (
    opportunityId: string,
    data: CompleteActionRequest
  ): Promise<void> => {
    await api.post(`/opportunities/${opportunityId}/complete_action`, data);
  },
};

export default api;
import axios, { AxiosError } from 'axios';

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

export interface ApiError {
  message: string;
  status: number;
  details?: any;
}

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second base delay

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Global tenant ID - in production this would come from context
let globalTenantId = process.env.REACT_APP_TENANT_ID || '550e8400-e29b-41d4-a716-446655440000';

export const setTenantId = (tenantId: string) => {
  globalTenantId = tenantId;
};

// Request interceptor to add tenant ID
api.interceptors.request.use(
  (config) => {
    config.headers['X-Tenant-ID'] = globalTenantId;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const apiError: ApiError = {
      message: 'An unexpected error occurred',
      status: error.response?.status || 500,
      details: error.response?.data,
    };

    // Handle specific error cases
    if (error.response?.status === 400) {
      apiError.message = 'Invalid request data';
    } else if (error.response?.status === 404) {
      apiError.message = 'Resource not found';
    } else if (error.response?.status === 422) {
      apiError.message = 'Validation error';
    } else if (error.response?.status === 500) {
      apiError.message = 'Server error - please try again later';
    } else if (error.code === 'ECONNABORTED') {
      apiError.message = 'Request timeout - please check your connection';
    } else if (!error.response) {
      apiError.message = 'Network error - please check your connection';
    }

    return Promise.reject(apiError);
  }
);

// Retry function with exponential backoff
const retryRequest = async <T>(
  requestFn: () => Promise<T>,
  retries = MAX_RETRIES
): Promise<T> => {
  try {
    return await requestFn();
  } catch (error) {
    if (retries > 0 && shouldRetry(error as ApiError)) {
      const delay = RETRY_DELAY * (MAX_RETRIES - retries + 1);
      await new Promise(resolve => setTimeout(resolve, delay));
      return retryRequest(requestFn, retries - 1);
    }
    throw error;
  }
};

// Determine if error should be retried
const shouldRetry = (error: ApiError): boolean => {
  // Retry on network errors, timeouts, and 5xx server errors
  return (
    error.status >= 500 ||
    error.message.includes('Network error') ||
    error.message.includes('timeout')
  );
};

// API functions with retry logic
export const opportunitiesApi = {
  // Get all due opportunities
  getDueOpportunities: async (): Promise<Opportunity[]> => {
    return retryRequest(async () => {
      const response = await api.get('/opportunities/due');
      return response.data;
    });
  },

  // Complete an action and set the next one
  completeAction: async (
    opportunityId: string,
    data: CompleteActionRequest
  ): Promise<void> => {
    return retryRequest(async () => {
      await api.post(`/opportunities/${opportunityId}/complete_action`, data);
    });
  },
};

export default api;
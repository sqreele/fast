import axios, { AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { getSession } from 'next-auth/react';

// Enhanced error interface
interface ApiError extends Error {
  status?: number;
  data?: unknown;
}

interface ErrorResponse {
  message?: string;
  [key: string]: unknown;
}

// Create axios instance
const api = axios.create({
  baseURL: '/api/v1', // Use relative URL to go through nginx
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    try {
      const session = await getSession();
      if (session?.accessToken) {
        config.headers.Authorization = `Bearer ${session.accessToken}`;
      }
    } catch (error) {
      console.error('Error getting session:', error);
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError<ErrorResponse>) => {
    const apiError: ApiError = new Error();
    
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      apiError.status = status;
      apiError.data = data;
      apiError.message = data?.message || `Server error: ${status}`;
      
      switch (status) {
        case 401:
          console.error('Unauthorized access - redirecting to login');
          if (typeof window !== 'undefined') {
            window.location.href = '/api/auth/signin'; // Fixed typo in signin
          }
          break;
        case 403:
          console.error('Forbidden access');
          break;
        case 404:
          console.error('Resource not found');
          break;
        case 422:
          console.error('Validation error:', data);
          break;
        case 429:
          console.error('Too many requests');
          break;
        default:
          if (status >= 500) {
            console.error('Server error:', status);
          }
      }
    } else if (error.request) {
      // Network error
      apiError.message = 'Network error - please check your connection';
      console.error('Network error:', error.message);
    } else {
      // Something else happened
      apiError.message = error.message || 'An unexpected error occurred';
      console.error('Request setup error:', error.message);
    }
    
    return Promise.reject(apiError);
  }
);

// Helper function to handle API errors
export const handleApiError = (error: unknown): string => {
  if (error && typeof error === 'object' && 'status' in error) {
    const apiError = error as ApiError;
    switch (apiError.status) {
      case 400:
        return 'Bad request. Please check your input.';
      case 401:
        return 'You are not authorized. Please sign in.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 422:
        return (apiError.data as ErrorResponse)?.message || 'Validation error occurred.';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return apiError.message || 'An unexpected error occurred.';
    }
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'Network error. Please check your connection.';
};

export default api;
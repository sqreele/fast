// lib/axios.ts
import axios, { AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';

// Enhanced error interface
interface ApiError extends Error {
  status?: number;
  data?: unknown;
}

interface ErrorResponse {
  message?: string;
  [key: string]: unknown;
}

// Get API base URL
const getApiBaseUrl = () => {
  // For production, use environment variable or empty string to avoid double /api prefix
  if (process.env.NODE_ENV === 'production') {
    return process.env.NEXT_PUBLIC_API_BASE_URL || '';
  }
  // Development
  return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
};

// Create axios instance
const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token from your custom auth
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    try {
      // Get token from your auth store instead of NextAuth
      if (typeof window !== 'undefined') {
        const authStorage = localStorage.getItem('auth-storage');
        if (authStorage) {
          const parsed = JSON.parse(authStorage);
          const token = parsed.state?.token;
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        }
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
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
      const { status, data } = error.response;
      apiError.status = status;
      apiError.data = data;
      apiError.message = data?.message || `Server error: ${status}`;
      
      // Handle 401 errors by clearing auth and redirecting
      if (status === 401) {
        console.error('Unauthorized access - clearing auth');
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth-storage');
          window.location.href = '/login';
        }
      }
    } else if (error.request) {
      apiError.message = 'Network error - unable to connect to the server. Please check if the backend service is running.';
      console.error('Network error:', error.message);
    } else {
      apiError.message = error.message || 'An unexpected error occurred';
      console.error('Request setup error:', error.message);
    }
    
    return Promise.reject(apiError);
  }
);

// Error handler function for use in stores and components
export const handleApiError = (error: unknown): string => {
  if (error instanceof Error) {
    const apiError = error as ApiError;
    return apiError.message || 'An unexpected error occurred';
  }
  return 'An unexpected error occurred';
};

export default api;

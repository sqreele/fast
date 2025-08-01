/**
 * Utility functions for handling authentication URLs across different environments
 */

/**
 * Get the correct base URL for the current environment
 * This prevents issues with invalid URLs like 0.0.0.0 in production
 */
export const getAuthBaseUrl = (): string => {
  // In browser environment
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  
  // Server-side environment
  if (process.env.NEXTAUTH_URL) {
    return process.env.NEXTAUTH_URL;
  }
  
  // Fallbacks based on environment
  if (process.env.NODE_ENV === 'production') {
    return 'http://localhost';
  }
  
  return 'http://localhost:3000';
};

/**
 * Validate and sanitize a URL to prevent invalid addresses
 */
export const sanitizeUrl = (url: string): string => {
  try {
    // Check for invalid patterns
    if (url.includes('0.0.0.0') || url.includes('127.0.0.1:3000')) {
      console.warn('Invalid URL detected, using fallback:', url);
      return getAuthBaseUrl();
    }
    
    // Validate URL format
    new URL(url);
    return url;
  } catch (error) {
    console.warn('Invalid URL format, using fallback:', url, error);
    return getAuthBaseUrl();
  }
};

/**
 * Get the correct callback URL for signout
 */
export const getSignoutCallbackUrl = (): string => {
  const baseUrl = getAuthBaseUrl();
  return `${baseUrl}/signin`;
};
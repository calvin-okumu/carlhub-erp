import { getAccessToken, refreshAccessToken, isTokenExpired } from "@/utils/auth";

interface ApiOptions extends RequestInit {
  skipAuth?: boolean;
}

export async function apiRequest(url: string, options: ApiOptions = {}): Promise<Response> {
  const { skipAuth = false, ...fetchOptions } = options;
  
  let token = getAccessToken();
  
  // Check if token is expired and refresh if needed
  if (!skipAuth && token && isTokenExpired(token)) {
    token = await refreshAccessToken();
  }
  
  const headers = {
    "Content-Type": "application/json",
    ...(token && !skipAuth && { Authorization: `Bearer ${token}` }),
    ...fetchOptions.headers,
  };

  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  });

  // If we get a 401, try to refresh token and retry once
  if (response.status === 401 && !skipAuth) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      const retryHeaders = {
        ...headers,
        Authorization: `Bearer ${newToken}`,
      };
      
      return fetch(url, {
        ...fetchOptions,
        headers: retryHeaders,
      });
    }
  }
  
  return response;
}

// Helper function for API calls with automatic JSON parsing
export async function apiCall<T = any>(
  url: string, 
  options: ApiOptions = {}
): Promise<T> {
  const response = await apiRequest(url, options);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.detail || `HTTP ${response.status}`);
  }
  
  return response.json();
}
/**
 * Centralized HTTP API Client for SIFT Frontend.
 * Communicates with FastAPI backend using standardized JSON requests,
 * URL query serialization, and normalized error contracts.
 */

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/+$/, '');

class ApiError extends Error {
  constructor(status, code, message, details = null) {
    super(message || 'An unexpected API error occurred.');
    this.name = 'ApiError';
    this.status = status;
    this.code = code || 'UNKNOWN_ERROR';
    this.details = details;
  }
}

/**
 * Builds safe URLSearchParams object, omitting null, undefined, empty string, and 'ALL'.
 */
function buildQueryString(params = {}) {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '' || value === 'ALL') {
      continue;
    }
    searchParams.append(key, String(value));
  }
  const str = searchParams.toString();
  return str ? `?${str}` : '';
}

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  const headers = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...(options.headers || {}),
  };

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);

    // Handle 204 No Content
    if (response.status === 204) {
      return null;
    }

    const contentType = response.headers.get('content-type');
    const isJson = contentType && contentType.includes('application/json');
    const data = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const errorObj = data && typeof data === 'object' ? data.error || data : {};
      const errorCode = errorObj.code || `HTTP_${response.status}`;
      const errorMessage = errorObj.message || response.statusText || 'Request failed';
      const errorDetails = errorObj.details || null;

      throw new ApiError(response.status, errorCode, errorMessage, errorDetails);
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    // Network failure or abort
    console.error(`[API Network Error] on ${config.method || 'GET'} ${url}:`, error);
    throw new ApiError(
      0,
      'NETWORK_ERROR',
      'Unable to connect to SIFT Safety Intelligence backend. Please ensure the server is running.',
      error.message
    );
  }
}

export const apiClient = {
  /**
   * HTTP GET Request
   */
  async get(endpoint, params = {}, options = {}) {
    const queryString = buildQueryString(params);
    return request(`${endpoint}${queryString}`, {
      method: 'GET',
      ...options,
    });
  },

  /**
   * HTTP POST Request
   */
  async post(endpoint, body = {}, options = {}) {
    return request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body),
      ...options,
    });
  },

  /**
   * HTTP PATCH Request
   */
  async patch(endpoint, body = {}, options = {}) {
    return request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(body),
      ...options,
    });
  },

  /**
   * HTTP DELETE Request
   */
  async delete(endpoint, options = {}) {
    return request(endpoint, {
      method: 'DELETE',
      ...options,
    });
  },

  /**
   * Check backend root health
   */
  async checkHealth() {
    try {
      const rootUrl = BASE_URL.replace(/\/api\/v1$/, '');
      const res = await fetch(`${rootUrl}/health`);
      return res.ok;
    } catch {
      return false;
    }
  },
};

export { ApiError };

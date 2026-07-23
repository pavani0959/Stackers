const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();

export const API_BASE_URL = configuredBaseUrl
  ? configuredBaseUrl.replace(/\/+$/, '')
  : '';

export class ApiError extends Error {
  constructor(message, { status = 0, code = 'API_ERROR', details = null } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

function buildUrl(path) {
  if (!API_BASE_URL) {
    throw new ApiError(
      'VITE_API_BASE_URL is not configured. Copy .env.example to .env and restart Vite.',
      { code: 'API_BASE_URL_MISSING' },
    );
  }

  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}

async function parseResponse(response) {
  if (response.status === 204) return null;

  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json().catch(() => null);
  }

  const text = await response.text();
  return text || null;
}

export async function apiRequest(path, options = {}) {
  const isFormData =
    typeof FormData !== 'undefined' && options.body instanceof FormData;
  const headers = new Headers(options.headers || {});

  headers.set('Accept', 'application/json');
  if (options.body !== undefined && !isFormData && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  // Attach JWT token if available
  const token = localStorage.getItem('myntra_auth_token');
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  let response;
  try {
    response = await fetch(buildUrl(path), {
      ...options,
      headers,
    });
  } catch (error) {
    if (error instanceof ApiError) throw error;

    throw new ApiError('Unable to reach the server. Check that the backend is running.', {
      code: 'NETWORK_ERROR',
      details: error,
    });
  }

  const payload = await parseResponse(response);

  if (!response.ok) {
    // On 401, clear stale token and redirect to login
    if (response.status === 401) {
      const isAuthRoute = path.startsWith('/api/auth/');
      if (!isAuthRoute) {
        localStorage.removeItem('myntra_auth_token');
        window.location.href = '/login';
        return;
      }
    }

    throw new ApiError(
      payload?.error?.message ||
        payload?.detail ||
        `Request failed with status ${response.status}`,
      {
        status: response.status,
        code: payload?.error?.code || 'HTTP_ERROR',
        details: payload,
      },
    );
  }

  return payload;
}

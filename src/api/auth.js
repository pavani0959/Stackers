import { apiRequest } from './client';

const TOKEN_KEY = 'myntra_auth_token';

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearStoredToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export async function signup({ name, email, password }) {
  const data = await apiRequest('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ name, email, password }),
  });

  setStoredToken(data.token);
  return data;
}

export async function login({ email, password }) {
  const data = await apiRequest('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

  setStoredToken(data.token);
  return data;
}

export async function getMe() {
  return apiRequest('/api/auth/me');
}

export function logout() {
  clearStoredToken();
}

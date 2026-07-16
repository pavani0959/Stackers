import { apiRequest } from './client';

export function createUserEvent(payload) {
  return apiRequest('/api/events', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getUserEvents(limit = 50) {
  const parsedLimit = Number(limit);

  const safeLimit = Number.isFinite(parsedLimit)
    ? Math.min(Math.max(Math.trunc(parsedLimit), 1), 200)
    : 50;

  return apiRequest(
    `/api/events?limit=${safeLimit}`,
  );
}
export function getMemoryTimeline() {
  return apiRequest('/api/memory/timeline');
}

export function checkRegret(productId) {
  return apiRequest(`/api/memory/regret-check/${productId}`);
}

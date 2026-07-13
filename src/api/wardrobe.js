import { apiRequest } from './client';

export function getWardrobe() {
  return apiRequest('/api/wardrobe');
}

export function createWardrobeItem(item) {
  return apiRequest('/api/wardrobe', {
    method: 'POST',
    body: JSON.stringify(item),
  });
}
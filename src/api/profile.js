import { apiRequest } from './client';

export function getCurrentProfile() {
  return apiRequest('/api/profile');
}

export function savePreferences(preferences) {
  return apiRequest('/api/profile/preferences', {
    method: 'PUT',
    body: JSON.stringify(preferences),
  });
}

export function saveFashionDNA(styleProfile) {
  return apiRequest('/api/profile/dna', {
    method: 'POST',
    body: JSON.stringify(styleProfile),
  });
}

export function saveIdentity(identity) {
  return apiRequest('/api/profile/identity', {
    method: 'PUT',
    body: JSON.stringify(identity),
  });
}

export function calculateFashionDNA(answers) {
  return apiRequest('/api/profile/dna/calculate', {
    method: 'POST',
    body: JSON.stringify({
      answers,
    }),
  });
}
import { apiRequest } from './client';

export function createProductDecision(productId, context = {}) {
  return apiRequest(`/api/decisions/products/${productId}`, {
    method: 'POST',
    body: JSON.stringify({
      context: {
        source: 'product_detail',
        ...context,
      },
    }),
  });
}

export function getDecision(snapshotId) {
  return apiRequest(`/api/decisions/${snapshotId}`);
}

export function getDecisionFeed({
  limit = 20,
  antiTrend = false,
  context = {},
} = {}) {
  return apiRequest('/api/decisions/feed', {
    method: 'POST',
    body: JSON.stringify({
      limit,
      anti_trend: antiTrend,
      context: {
        source: 'feed',
        ...context,
      },
    }),
  });
}

export function getDecisionMemory() {
  return apiRequest('/api/decisions/memory');
}

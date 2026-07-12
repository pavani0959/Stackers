// The static products array has been removed as we fetch from the real backend now.

// Get product by ID
export const getProduct = (products, id) => products.find(p => p.id === Number(id));

// Budget tier order (for comparison)
export const budgetTiers = ['budget-explorer', 'smart-spender', 'campus-casual', 'style-investor', 'luxury-seeker'];

// Calculate confidence score between a product and user profile
export const calcConfidence = (product, userProfile) => {
  const dna = userProfile.dna || {};
  const userTags = Object.keys(dna).filter(k => dna[k] > 20);
  const userOccasions = userProfile.occasions || [];
  const userBudget = userProfile.budget || 'campus-casual';

  // Style Match: how many product tags align with user DNA
  const tagOverlap = product.tags.filter(t => userTags.includes(t)).length;
  const styleMatch = Math.min(100, Math.round((tagOverlap / Math.max(product.tags.length, 1)) * 100 + 10));

  // Occasion Match
  const occOverlap = product.occasions.filter(o => userOccasions.includes(o)).length;
  const occasionMatch = Math.min(100, occOverlap > 0 ? Math.round((occOverlap / Math.max(product.occasions.length, 1)) * 100 + 15) : 40);

  // Budget Match
  const userBudgetIdx = budgetTiers.indexOf(userBudget);
  const prodBudgetIdx = budgetTiers.indexOf(product.budgetTier);
  const budgetDiff = Math.abs(userBudgetIdx - prodBudgetIdx);
  const budgetMatch = budgetDiff === 0 ? 95 : budgetDiff === 1 ? 80 : 60;

  // Weather Match (based on current month)
  const month = new Date().getMonth();
  const isSummer = month >= 3 && month <= 8;
  const weatherMatch = product.season === 'all' ? 90 : (product.season === 'summer' && isSummer) || (product.season === 'winter' && !isSummer) ? 92 : 72;

  // Wardrobe Fit: check against purchase memory tags
  const memory = userProfile.purchaseMemory || [];
  const memoryTags = memory.flatMap(m => m.tags || []);
  const wardrobeOverlap = product.tags.filter(t => memoryTags.includes(t)).length;
  const wardrobeMatch = memory.length > 0 ? Math.min(100, Math.round((wardrobeOverlap / Math.max(product.tags.length, 1)) * 100 + 20)) : 75;

  const overall = Math.round((styleMatch + occasionMatch + budgetMatch + weatherMatch + wardrobeMatch) / 5);

  return { overall, styleMatch, occasionMatch, budgetMatch, weatherMatch, wardrobeMatch };
};

// Get products sorted by DNA match for the user
export const getProductsForUser = (products, userProfile) => {
  if (!products || products.length === 0) return [];
  return [...products]
    .map(p => ({ ...p, confidence: calcConfidence(p, userProfile) }))
    .sort((a, b) => b.confidence.overall - a.confidence.overall);
};

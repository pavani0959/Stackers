const STYLE_LABELS = {
  minimalist: 'Minimalist',
  streetwear: 'Streetwear',
  quietLuxury: 'Quiet Luxury',
  romantic: 'Soft Romantic',
  sporty: 'Sporty',
  y2k: 'Y2K',
  bohemian: 'Bohemian',
  campusCasual: 'Campus Casual',
};

export function buildDnaBars(dna = {}) {
  return Object.entries(dna)
    .sort((left, right) => {
      if (right[1] !== left[1]) {
        return right[1] - left[1];
      }

      return left[0].localeCompare(right[0]);
    })
    .map(([key, percentage]) => ({
      key,
      label: STYLE_LABELS[key] ?? key,
      percentage,
    }));
}
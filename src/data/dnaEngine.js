// DNA Engine — converts quiz answers into DNA percentages and identity name

const aestheticLabels = {
  minimalist:   'Minimalist',
  streetwear:   'Streetwear',
  campusCasual: 'Campus Casual',
  quietLuxury:  'Quiet Luxury',
  y2k:          'Y2K',
  darkAcademia: 'Dark Academia',
  bold:         'Bold & Expressive',
  neutral:      'Neutral Palette',
  feminine:     'Soft & Feminine',
  vintage:      'Vintage',
};

// Identity name based on top two aesthetics
const identityMap = {
  'minimalist+campusCasual': { name: 'Campus Minimalist', desc: 'You keep it clean, you keep it real. Neutral tones, comfortable silhouettes, and just enough edge to stand out without trying too hard.' },
  'minimalist+neutral':      { name: 'Clean Aesthetic', desc: 'Your wardrobe is your sanctuary. Everything is intentional, nothing is excessive. You are the definition of effortless cool.' },
  'minimalist+quietLuxury':  { name: 'Quiet Luxury Minimalist', desc: 'You dress like you know things others don\'t. Subtle signals, refined taste, zero noise.' },
  'streetwear+bold':         { name: 'Bold Street Player', desc: 'You make a statement before you say a word. Fashion is your language and you speak it loudly.' },
  'streetwear+y2k':          { name: 'Y2K Street Rebel', desc: 'Nostalgia with attitude. You\'re always 5 minutes ahead of the trend cycle.' },
  'campusCasual+neutral':    { name: 'Effortless Campus', desc: 'You roll out of bed looking put-together. Comfort is your superpower and neutrals are your armour.' },
  'y2k+bold':                { name: 'Y2K Maximalist', desc: 'More is more. Always. You see fashion as a playground and every outfit is a performance.' },
  'darkAcademia+vintage':    { name: 'Dark Scholar', desc: 'Structured, literary, moody. Your wardrobe tells stories that most people haven\'t read yet.' },
  'quietLuxury+neutral':     { name: 'Old Money Aesthetic', desc: 'Understatement is your luxury. You dress like you\'ve already arrived.' },
  'feminine+colorful':       { name: 'Soft Maximalist', desc: 'Playful, expressive, joyful. Your style is a mood board in motion.' },
};

export const calculateDNA = (answers) => {
  // answers = array of choice objects, each with .tags array
  const tagCounts = {};

  answers.forEach(choice => {
    if (!choice || !choice.tags) return;
    choice.tags.forEach(tag => {
      tagCounts[tag] = (tagCounts[tag] || 0) + 1;
    });
  });

  // Convert to percentages (out of max possible = 10 * 3 tags = 30)
  const total = Object.values(tagCounts).reduce((a, b) => a + b, 0);
  const dna = {};

  Object.entries(tagCounts).forEach(([tag, count]) => {
    dna[tag] = Math.round((count / total) * 100);
  });

  // Get top aesthetics
  const sorted = Object.entries(dna).sort((a, b) => b[1] - a[1]);
  const top1 = sorted[0]?.[0] || 'minimalist';
  const top2 = sorted[1]?.[0] || 'neutral';

  // Look up identity name
  const key1 = `${top1}+${top2}`;
  const key2 = `${top2}+${top1}`;
  const identity = identityMap[key1] || identityMap[key2] || {
    name: `${aestheticLabels[top1] || top1} Explorer`,
    desc: `Your style is a unique blend of ${aestheticLabels[top1] || top1} and ${aestheticLabels[top2] || top2}. There\'s no label for what you are — and that\'s exactly the point.`,
  };

  // Build top 4 DNA bars to display
  const topBars = sorted.slice(0, 4).map(([tag, pct]) => ({
    tag,
    label: aestheticLabels[tag] || tag,
    percentage: pct,
  }));

  return { dna, identity, topBars };
};

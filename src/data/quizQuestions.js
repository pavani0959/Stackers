// DNA Quiz — 5 visual questions (reduced for better UX)
// Each choice has aesthetic tags that feed into DNA calculation

export const quizQuestions = [
  {
    id: 1,
    question: 'Which outfit would you reach for on a regular college day?',
    choices: [
      { label: 'Minimal White Tee + Beige Cargo', bg: 'linear-gradient(160deg,#F5F0E8,#D4C4B0)', tags: ['minimalist', 'neutral', 'campusCasual'] },
      { label: 'Bold Graphic Hoodie + Baggy Jeans', bg: 'linear-gradient(160deg,#1A1A2E,#2D2D4E)', tags: ['streetwear', 'bold', 'y2k'] },
      { label: 'Floral Dress + White Sneakers', bg: 'linear-gradient(160deg,#FFE4E1,#FFC0CB)', tags: ['feminine', 'colorful', 'casual'] },
      { label: 'Oversized Denim Jacket + Vintage Tee', bg: 'linear-gradient(160deg,#4A4A6A,#6A6A9A)', tags: ['streetwear', 'vintage', 'casual'] },
    ],
  },
  {
    id: 2,
    question: 'Pick the aesthetic that feels most like home',
    choices: [
      { label: 'Quiet Luxury — subtle, refined', bg: 'linear-gradient(160deg,#C8B8A2,#A89080)', tags: ['quietLuxury', 'neutral', 'minimalist'] },
      { label: 'Y2K Energy — bold, nostalgic', bg: 'linear-gradient(160deg,#FF69B4,#00CED1)', tags: ['y2k', 'bold', 'colorful'] },
      { label: 'Dark Academia — moody, intellectual', bg: 'linear-gradient(160deg,#2F1B0E,#5C3317)', tags: ['darkAcademia', 'vintage', 'classic'] },
      { label: 'Clean Girl — effortless, natural', bg: 'linear-gradient(160deg,#FFF8F0,#F0E8D8)', tags: ['minimalist', 'campusCasual', 'neutral'] },
    ],
  },
  {
    id: 3,
    question: 'Your colour story is mostly…',
    choices: [
      { label: 'Neutrals — white, beige, grey, brown', bg: 'linear-gradient(160deg,#F5F0E8,#D4C4B0)', tags: ['neutral', 'minimalist', 'quietLuxury'] },
      { label: 'Darks — black, navy, forest green', bg: 'linear-gradient(160deg,#1A1A1A,#1B2838)', tags: ['darkAcademia', 'classic', 'formal'] },
      { label: 'Brights — red, yellow, electric blue', bg: 'linear-gradient(160deg,#FF4500,#FFD700)', tags: ['bold', 'colorful', 'y2k'] },
      { label: 'Pastels — lilac, mint, blush', bg: 'linear-gradient(160deg,#D8BFD8,#98FB98)', tags: ['feminine', 'soft', 'casual'] },
    ],
  },
  {
    id: 4,
    question: 'What matters most when you buy clothes?',
    choices: [
      { label: 'Versatility — pairs with everything', bg: 'linear-gradient(160deg,#F5F0E8,#E8E0D0)', tags: ['minimalist', 'neutral', 'classic'] },
      { label: 'Uniqueness — nobody else has it', bg: 'linear-gradient(160deg,#4A0E8F,#7B1FA2)', tags: ['bold', 'streetwear', 'y2k'] },
      { label: 'Price — best deal wins', bg: 'linear-gradient(160deg,#1B5E20,#388E3C)', tags: ['campusCasual', 'casual', 'smart'] },
      { label: 'Vibe — how it makes me feel', bg: 'linear-gradient(160deg,#FF3CAC,#784BA0)', tags: ['feminine', 'colorful', 'bold'] },
    ],
  },
  {
    id: 5,
    question: "Last one — what's your fashion goal?",
    choices: [
      { label: 'Build a timeless wardrobe', bg: 'linear-gradient(160deg,#C8B8A2,#A89080)', tags: ['minimalist', 'quietLuxury', 'classic'] },
      { label: 'Always look fresh and on trend', bg: 'linear-gradient(160deg,#FF3CAC,#784BA0)', tags: ['y2k', 'bold', 'colorful'] },
      { label: 'Express who I am right now', bg: 'linear-gradient(160deg,#2B86C5,#06B6D4)', tags: ['streetwear', 'casual', 'campusCasual'] },
      { label: 'Spend less, look more', bg: 'linear-gradient(160deg,#1B5E20,#2E7D32)', tags: ['campusCasual', 'smart', 'neutral'] },
    ],
  },
];

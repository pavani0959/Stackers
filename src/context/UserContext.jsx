import { useEffect, useState } from 'react';
import { UserContext } from './UserContextBase';
import { apiRequest } from '../api/client';

const DEFAULT_STATE = {
  // Onboarding
  name: '',
  gender: '',
  age: 21,
  budget: 'campus-casual',
  colours: [],
  occasions: [],
  // DNA
  dna: {},
  dnaTopBars: [],
  identityName: '',
  identityDesc: '',
  confidenceScore: 0,
  // App state
  moodState: 'quiet',
  wishlist: [],
  purchaseMemory: [],
  cartItems: [],
  products: [],
  // Flags
  hasCompletedOnboarding: false,
  hasCompletedQuiz: false,
};

export function UserProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('myntra_identity_user');
      return saved
        ? { ...DEFAULT_STATE, ...JSON.parse(saved), products: [] }
        : DEFAULT_STATE;
    } catch {
      return DEFAULT_STATE;
    }
  });

  // Fetch real products from backend
  useEffect(() => {
    apiRequest('/api/products')
      .then((data) => {
        setUser((prev) => ({ ...prev, products: data }));
      })
      .catch((err) =>
        console.error('Failed to fetch products from backend:', err)
      );
  }, []);

  // Auto-save to localStorage whenever user changes
  useEffect(() => {
    try {
      localStorage.setItem('myntra_identity_user', JSON.stringify(user));
    } catch {
      // localStorage full — ignore
    }
  }, [user]);

  const updateUser = (updates) => {
    setUser((prev) => ({ ...prev, ...updates }));
  };

  const buyItem = (product, confidenceOverall = 85) => {
    const memoryItem = {
      id: product.id,
      name: product.name,
      price: product.price,
      image: product.image,
      date: new Date().toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'short',
      }),
      occasion: product.occasions?.[0] || 'Casual',
      dnaMatch: confidenceOverall,
      reason: `Bought because it matched your ${
        user.identityName || 'vibe'
      }.`,
      tags: product.tags || [],
    };

    setUser((prev) => ({
      ...prev,
      purchaseMemory: [memoryItem, ...(prev.purchaseMemory || [])],
    }));
  };

  const addToWishlist = (productId) => {
    setUser((prev) => ({
      ...prev,
      wishlist: prev.wishlist.includes(productId)
        ? prev.wishlist.filter((id) => id !== productId)
        : [...prev.wishlist, productId],
    }));
  };

  const addToCart = (product) => {
    buyItem(product, product.confidence?.overall);
  };

  const resetAll = () => {
    setUser(DEFAULT_STATE);
    localStorage.removeItem('myntra_identity_user');
  };

  return (
    <UserContext.Provider
      value={{
        user,
        updateUser,
        addToWishlist,
        addToCart,
        buyItem,
        resetAll,
      }}
    >
      {children}
    </UserContext.Provider>
  );
}

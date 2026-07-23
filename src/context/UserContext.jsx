import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react';

import { apiRequest } from '../api/client';

import {
  createUserEvent as createUserEventRequest,
} from '../api/events';

import {
  calculateFashionDNA,
  getCurrentProfile,
  saveFashionDNA,
  saveIdentity,
  savePreferences,
} from '../api/profile';

import { UserContext } from './UserContextBase';

const UI_STORAGE_KEY = 'myntra_identity_ui';
const LEGACY_STORAGE_KEY = 'myntra_identity_user';

const DEFAULT_UI_STATE = {
  moodState: 'quiet',
  wishlist: [],
  cartItems: [],
};

const DEFAULT_STATE = {
  // Server-controlled user information
  id: null,
  name: '',
  email: '',
  gender: '',
  age: null,
  avatarUrl: null,
  onboardingCompleted: false,

  // Server-controlled preferences
  budgetMin: null,
  budgetMax: null,
  budget: null,
  colours: [],
  brands: [],
  occasions: [],
  aesthetics: [],
  fitPreferences: [],
  comfortPriority: 0.5,
  trendOpenness: 0.5,

  // Server-controlled Fashion DNA
  dna: {},
  identityName: '',
  secondaryIdentity: null,
  profileConfidence: 0,
  dnaVersion: null,

  // Temporary compatibility fields
  dnaTopBars: [],
  identityDesc: '',
  confidenceScore: 0,
  hasCompletedOnboarding: false,
  hasCompletedQuiz: false,

  // UI-only state
  ...DEFAULT_UI_STATE,

  // Products come from the backend
  products: [],
  createdAt: null,
  occasionPriorities: {},
  fashionGoal: '',
  comfortExpressionBalance: 0.5,
  profileId: null,
  identityDescription: '',
  confidenceBreakdown: {},
  evidence: {},
};

function loadUIState() {
  try {
    const saved = localStorage.getItem(
      UI_STORAGE_KEY,
    );

    if (!saved) {
      return DEFAULT_UI_STATE;
    }

    const parsed = JSON.parse(saved);

    return {
      moodState:
        typeof parsed.moodState === 'string'
          ? parsed.moodState
          : DEFAULT_UI_STATE.moodState,

      wishlist: Array.isArray(parsed.wishlist)
        ? parsed.wishlist
        : [],

      cartItems: Array.isArray(parsed.cartItems)
        ? parsed.cartItems
        : [],
    };
  } catch {
    return DEFAULT_UI_STATE;
  }
}

function mapServerProfile(payload) {
  const preferences = payload.preferences;
  const styleProfile = payload.style_profile;
  const dna = styleProfile?.dna_vector ?? {};

  return {
    id: payload.user.id,
    name: payload.user.name,
    email: payload.user.email,
    gender: payload.user.gender,
    age: payload.user.age,
    avatarUrl: payload.user.avatar_url,
    createdAt:
      payload.user.created_at ?? null,

    onboardingCompleted:
      payload.user.onboarding_completed,

    budgetMin:
      preferences?.budget_min ?? null,

    budgetMax:
      preferences?.budget_max ?? null,

    budget:
      preferences?.budget_tier ?? null,

    colours:
      preferences?.preferred_colours ?? [],

    brands:
      preferences?.preferred_brands ?? [],

    occasions:
      preferences?.preferred_occasions ?? [],

    aesthetics:
      preferences?.preferred_aesthetics ?? [],

    fitPreferences:
      preferences?.fit_preferences ?? [],

    comfortPriority:
      preferences?.comfort_priority ?? 0.5,

    trendOpenness:
      preferences?.trend_openness ?? 0.5,

    dna,

    identityName:
      styleProfile?.identity?.name ??
      styleProfile?.primary_identity ??
      '',

    identityDescription:
      styleProfile?.identity?.description ?? '',

    secondaryIdentity:
      styleProfile?.identity?.secondary ??
      styleProfile?.secondary_identity ??
      null,

    profileConfidence:
      styleProfile?.profile_confidence ?? 0,

    dnaVersion:
      styleProfile?.version ?? null,

    /*
     * Temporary aliases for existing screens.
     * Remove these after all components use the new names.
     */
    confidenceScore:
      styleProfile?.profile_confidence ?? 0,

    hasCompletedOnboarding:
      payload.user.onboarding_completed,

    hasCompletedQuiz: Boolean(styleProfile),

    occasionPriorities:
      preferences?.occasion_priorities ?? {},

    fashionGoal:
      preferences?.fashion_goal ?? '',

    comfortExpressionBalance:
      preferences?.comfort_expression_balance ??
      0.5,
  };
}

export function UserProvider({ children }) {
  const [user, setUser] = useState(() => ({
    ...DEFAULT_STATE,
    ...loadUIState(),
  }));

  const [profileLoading, setProfileLoading] =
    useState(true);

  const [profileError, setProfileError] =
    useState(null);

  /*
   * Remove the legacy entry because profile data
   * must now come from the backend.
   */
  useEffect(() => {
    localStorage.removeItem(LEGACY_STORAGE_KEY);
  }, []);

  const refreshProfile = useCallback(async () => {
    setProfileLoading(true);
    setProfileError(null);

    try {
      const payload =
        await getCurrentProfile();

      const serverProfile =
        mapServerProfile(payload);

      /*
       * Keep UI-only state while refreshing
       * server-controlled profile fields.
       */
      setUser((previousUser) => ({
        ...previousUser,
        ...serverProfile,
      }));
    } catch (error) {
      console.error(
        'Failed to fetch current profile:',
        error,
      );

      setProfileError(error);
    } finally {
      setProfileLoading(false);
    }
  }, []);

  const updateIdentity = useCallback(
    async (identity) => {
      await saveIdentity(identity);
      await refreshProfile();
    },
    [refreshProfile],
  );

  useEffect(() => {
    refreshProfile();
  }, [refreshProfile]);

  /*
   * Products are fetched separately from
   * the profile request.
   */
  useEffect(() => {
    let cancelled = false;

    async function fetchProducts() {
      try {
        const products = await apiRequest(
          '/api/products',
        );

        if (!cancelled) {
          setUser((previousUser) => ({
            ...previousUser,
            products,
          }));
        }
      } catch (error) {
        console.error(
          'Failed to fetch products from backend:',
          error,
        );
      }
    }

    fetchProducts();

    return () => {
      cancelled = true;
    };
  }, []);

  /*
   * Only temporary UI data is persisted locally.
   *
   * Identity, preferences and Fashion DNA
   * deliberately remain backend-controlled.
   */
  useEffect(() => {
    try {
      const uiState = {
        moodState: user.moodState,
        wishlist: user.wishlist,
        cartItems: user.cartItems,
      };

      localStorage.setItem(
        UI_STORAGE_KEY,
        JSON.stringify(uiState),
      );
    } catch {
      // Ignore unavailable or full localStorage.
    }
  }, [
    user.moodState,
    user.wishlist,
    user.cartItems,
  ]);

  const updatePreferences = useCallback(
    async (preferences) => {
      await savePreferences(preferences);
      await refreshProfile();
    },
    [refreshProfile],
  );

  const calculateDNA = useCallback(
    async (answers) => {
      const result = await calculateFashionDNA(
        answers,
      );

      await refreshProfile();

      return result;
    },
    [refreshProfile],
  );

  const updateDNA = useCallback(
    async (styleProfile) => {
      await saveFashionDNA(styleProfile);
      await refreshProfile();
    },
    [refreshProfile],
  );



  /*
   * Record one backend user activity event.
   *
   * Components may decide whether failures should
   * be displayed or ignored.
   */
  const createUserEvent = useCallback(
    (eventPayload) => {
      return createUserEventRequest(
        eventPayload,
      );
    },
    [],
  );

  /*
   * Temporary compatibility method.
   *
   * This updates React state only. It must not be
   * used for permanent preferences or Fashion DNA.
   */
  const updateUser = useCallback((updates) => {
    setUser((previousUser) => ({
      ...previousUser,
      ...updates,
    }));
  }, []);



  const addToWishlist = useCallback(
    (productId) => {
      setUser((previousUser) => {
        const wishlist =
          previousUser.wishlist ?? [];

        return {
          ...previousUser,

          wishlist: wishlist.includes(productId)
            ? wishlist.filter(
              (id) => id !== productId,
            )
            : [...wishlist, productId],
        };
      });
    },
    [],
  );

  /*
   * Adding to cart must not add the item to
   * purchase memory.
   */
  const addToCart = useCallback((product) => {
    setUser((previousUser) => {
      const cartItems =
        previousUser.cartItems ?? [];

      const existingIndex =
        cartItems.findIndex(
          (item) =>
            item.id === product.id &&
            item.selectedSize ===
            product.selectedSize,
        );

      if (existingIndex === -1) {
        return {
          ...previousUser,

          cartItems: [
            ...cartItems,
            {
              ...product,
              quantity: 1,
            },
          ],
        };
      }

      const updatedCartItems = [...cartItems];

      const existingItem =
        updatedCartItems[existingIndex];

      updatedCartItems[existingIndex] = {
        ...existingItem,

        quantity:
          (existingItem.quantity ?? 1) + 1,
      };

      return {
        ...previousUser,
        cartItems: updatedCartItems,
      };
    });
    
    /*
     * Cart addition is only an intent event.
     * It must not create a purchase or wardrobe item.
     */
    void createUserEventRequest({
      event_type: 'cart_add',

      product_id: product.id,

      recommendation_item_id:
        product.recommendationItemId
        ?? null,

      metadata: {
        source:
          product.source
          ?? 'cart',

        size:
          product.selectedSize
          ?? 'M',

        decision_snapshot_id:
          product.decisionSnapshotId
          ?? null,
      },
    }).catch((error) => {
      console.warn(
        'Failed to log cart_add event',
        error,
      );
    });
  }, []);

  const removeFromCart = useCallback((productId, selectedSize) => {
    setUser((previousUser) => {
      const cartItems = previousUser.cartItems ?? [];
      return {
        ...previousUser,
        cartItems: cartItems.filter(
          item => !(item.id === productId && item.selectedSize === selectedSize)
        )
      };
    });
  }, []);

  const updateCartItemQuantity = useCallback((productId, selectedSize, newQuantity) => {
    setUser((previousUser) => {
      if (newQuantity <= 0) {
        return previousUser; // Or handle as remove, but UI should prevent this
      }
      const cartItems = previousUser.cartItems ?? [];
      const updatedCartItems = cartItems.map(item => {
        if (item.id === productId && item.selectedSize === selectedSize) {
          return { ...item, quantity: newQuantity };
        }
        return item;
      });

      return {
        ...previousUser,
        cartItems: updatedCartItems
      };
    });
  }, []);

  const clearCart = useCallback(() => {
    setUser((previousUser) => ({
      ...previousUser,
      cartItems: [],
    }));
  }, []);

  /*
   * Clear only local UI state.
   * The server profile remains untouched.
   */
  const resetAll = useCallback(() => {
    localStorage.removeItem(UI_STORAGE_KEY);

    setUser((previousUser) => ({
      ...previousUser,
      ...DEFAULT_UI_STATE,
    }));
  }, []);

  const value = useMemo(
    () => ({
      user,
      profileLoading,
      profileError,
      refreshProfile,

      updateIdentity,
      updatePreferences,
      calculateDNA,
      updateDNA,
      createUserEvent,

      // Temporary compatibility/UI methods
      updateUser,
      addToWishlist,
      addToCart,
      removeFromCart,
      updateCartItemQuantity,
      clearCart,
      resetAll,
    }),
    [
      user,
      profileLoading,
      profileError,
      refreshProfile,
      updateIdentity,
      updatePreferences,
      calculateDNA,
      updateDNA,
      createUserEvent,
      updateUser,
      addToWishlist,
      addToCart,
      removeFromCart,
      updateCartItemQuantity,
      clearCart,
      resetAll,
    ],
  );

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
}
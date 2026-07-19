import {
  useEffect,
  useState,
} from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Dna,
  Heart,
  ShoppingBag,
  Trash2,
} from 'lucide-react';

import { apiRequest } from '../../api/client';
import BottomNav from '../../components/BottomNav/BottomNav';
import '../../styles/Wishlist.css';

function WishlistItem({ item, moveToCart, removeItem, navigate }) {
  const [imgError, setImgError] = useState(false);

  return (
    <article className="wl-card">
      <button
        type="button"
        className="wl-img-wrap"
        aria-label={`View ${item.name}`}
        onClick={() => navigate(`/product/${item.id}`)}
      >
        {!imgError ? (
          <img
            src={item.image}
            alt=""
            className="wl-img"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="img-fallback">
            <span className="img-fallback-icon">👕</span>
            <span className="img-fallback-text">{item.name}</span>
          </div>
        )}

        <span className="wl-dna-badge">
          <Dna aria-hidden="true" size={14} />
          <span>{item.dnaMatch || 75}%</span>
        </span>
      </button>

      <div className="wl-info">
        <div className="wl-brand">{item.brand}</div>

        <button
          type="button"
          className="wl-name"
          onClick={() => navigate(`/product/${item.id}`)}
        >
          {item.name}
        </button>

        <div className="wl-price">
          ₹{Number(item.price || 0).toLocaleString('en-IN')}
        </div>

        <div className="wl-actions">
          <button
            type="button"
            className="wl-cart-btn"
            onClick={() => moveToCart(item)}
          >
            <ShoppingBag aria-hidden="true" size={17} />
            <span>Add to Cart</span>
          </button>

          <button
            type="button"
            className="wl-remove-btn"
            aria-label={`Remove ${item.name} from wishlist`}
            onClick={() => removeItem(item.id)}
          >
            <Trash2 aria-hidden="true" size={18} />
          </button>
        </div>
      </div>
    </article>
  );
}

export default function Wishlist() {
  const navigate = useNavigate();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState('');


  const showToast = (message) => {
    setToast(message);

    window.setTimeout(() => {
      setToast('');
    }, 2500);
  };


  useEffect(() => {
    try {
      const savedItems = JSON.parse(
        localStorage.getItem(
          'myntra_wishlist',
        ) || '[]',
      );

      setItems(
        Array.isArray(savedItems)
          ? savedItems
          : [],
      );
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);


  const trackWishlistRemoval = (productId) => {
    apiRequest('/api/events', {
      method: 'POST',
      body: JSON.stringify({
        product_id: productId,
        event_type: 'wishlist_remove',
        source: 'wishlist_screen',
      }),
    }).catch(() => {
      // The local wishlist action should still succeed
      // when event tracking is unavailable.
    });
  };


  const removeItem = (productId) => {
    setItems((currentItems) => {
      const updatedItems = currentItems.filter(
        (item) => item.id !== productId,
      );

      localStorage.setItem(
        'myntra_wishlist',
        JSON.stringify(updatedItems),
      );

      return updatedItems;
    });

    trackWishlistRemoval(productId);
    showToast('Removed from wishlist');
  };


  const moveToCart = (item) => {
    let cart = [];

    try {
      const storedCart = JSON.parse(
        localStorage.getItem(
          'myntra_cart',
        ) || '[]',
      );

      cart = Array.isArray(storedCart)
        ? storedCart
        : [];
    } catch {
      cart = [];
    }

    const alreadyInCart = cart.some(
      (cartItem) => cartItem.id === item.id,
    );

    if (!alreadyInCart) {
      cart.push(item);

      localStorage.setItem(
        'myntra_cart',
        JSON.stringify(cart),
      );
    }

    setItems((currentItems) => {
      const updatedItems = currentItems.filter(
        (wishlistItem) =>
          wishlistItem.id !== item.id,
      );

      localStorage.setItem(
        'myntra_wishlist',
        JSON.stringify(updatedItems),
      );

      return updatedItems;
    });

    trackWishlistRemoval(item.id);

    showToast(
      `${item.name} moved to cart!`,
    );
  };


  const moveAllToCart = () => {
    let cart = [];

    try {
      const storedCart = JSON.parse(
        localStorage.getItem(
          'myntra_cart',
        ) || '[]',
      );

      cart = Array.isArray(storedCart)
        ? storedCart
        : [];
    } catch {
      cart = [];
    }

    const existingProductIds = new Set(
      cart.map((item) => item.id),
    );

    const newCartItems = items.filter(
      (item) =>
        !existingProductIds.has(item.id),
    );

    const updatedCart = [
      ...cart,
      ...newCartItems,
    ];

    localStorage.setItem(
      'myntra_cart',
      JSON.stringify(updatedCart),
    );

    localStorage.setItem(
      'myntra_wishlist',
      JSON.stringify([]),
    );

    items.forEach((item) => {
      trackWishlistRemoval(item.id);
    });

    setItems([]);
    showToast('All items moved to cart!');
  };


  const totalValue = items.reduce(
    (sum, item) =>
      sum + Number(item.price || 0),
    0,
  );

  const averageMatch = items.length
    ? Math.round(
      items.reduce(
        (sum, item) =>
          sum
          + Number(
            item.dnaMatch || 75,
          ),
        0,
      ) / items.length,
    )
    : 0;


  return (
    <div className="screen wishlist-screen">
      <header className="wl-hdr">
        <div className="wl-back-row">
          <button
            type="button"
            className="back-btn"
            aria-label="Go back"
            onClick={() => {
              navigate(-1);
            }}
          >
            <ArrowLeft
              aria-hidden="true"
              size={21}
            />
          </button>

          <div>
            <div className="wl-title">
              <Heart
                aria-hidden="true"
                size={20}
                fill="currentColor"
              />

              <span>
                My Wishlist
              </span>
            </div>

            <div className="wl-sub">
              {items.length} items · Avg DNA Match{' '}
              {averageMatch}%
            </div>
          </div>
        </div>
      </header>

      <main className="wl-body">
        {loading ? (
          <div className="wl-empty">
            Loading…
          </div>
        ) : items.length === 0 ? (
          <div className="wl-empty-state">
            <div
              className="wl-empty-icon"
              aria-hidden="true"
            >
              <Heart
                size={28}
                fill="currentColor"
              />
            </div>

            <div className="wl-empty-title">
              Your wishlist is empty
            </div>

            <div className="wl-empty-sub">
              Tap the heart on any product to
              save it here.
            </div>

            <button
              type="button"
              className="wl-browse-btn"
              onClick={() => {
                navigate('/home');
              }}
            >
              Browse Products
            </button>
          </div>
        ) : (
          <>
            <div className="wl-summary">
              <div className="wl-sum-item">
                <div className="wl-sum-val">
                  {items.length}
                </div>

                <div className="wl-sum-lbl">
                  Items
                </div>
              </div>

              <div className="wl-sum-item">
                <div className="wl-sum-val">
                  ₹{totalValue.toLocaleString(
                    'en-IN',
                  )}
                </div>

                <div className="wl-sum-lbl">
                  Total Value
                </div>
              </div>

              <div className="wl-sum-item">
                <div className="wl-sum-val">
                  {averageMatch}%
                </div>

                <div className="wl-sum-lbl">
                  Avg DNA Match
                </div>
              </div>
            </div>

            <div className="wl-list">
              {items.map((item) => (
                <WishlistItem
                  key={item.id}
                  item={item}
                  moveToCart={moveToCart}
                  removeItem={removeItem}
                  navigate={navigate}
                />
              ))}
            </div>

            <button
              type="button"
              className="wl-cart-all-btn"
              onClick={moveAllToCart}
            >
              <ShoppingBag
                aria-hidden="true"
                size={18}
              />

              <span>
                Move All to Cart
              </span>
            </button>
          </>
        )}
      </main>

      {toast && (
        <div
          className="toast"
          role="status"
          aria-live="polite"
        >
          {toast}
        </div>
      )}

      <BottomNav />
    </div>
  );
}

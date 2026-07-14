import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { apiRequest } from '../../api/client';
import BottomNav from '../../components/BottomNav/BottomNav';
import '../../styles/Wishlist.css';

export default function Wishlist() {
  const navigate = useNavigate();
  const { user } = useUser();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState('');

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 2500); };

  // Wishlist stored in localStorage (keyed by user wishlist UI state)
  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem('myntra_wishlist') || '[]');
    setItems(saved);
    setLoading(false);
  }, []);

  const removeItem = (id) => {
    const updated = items.filter(item => item.id !== id);
    setItems(updated);
    localStorage.setItem('myntra_wishlist', JSON.stringify(updated));
    showToast('Removed from wishlist');

    // Track event on backend
    apiRequest('/api/events', {
      method: 'POST',
      body: JSON.stringify({
        product_id: id,
        event_type: 'wishlist_remove',
        source: 'wishlist_screen',
      }),
    }).catch(() => {});
  };

  const moveToCart = (item) => {
    const cart = JSON.parse(localStorage.getItem('myntra_cart') || '[]');
    const exists = cart.find(c => c.id === item.id);
    if (!exists) {
      cart.push(item);
      localStorage.setItem('myntra_cart', JSON.stringify(cart));
    }
    removeItem(item.id);
    showToast(`${item.name} moved to cart! 🛒`);
  };

  const totalValue = items.reduce((sum, i) => sum + (i.price || 0), 0);
  const avgMatch = items.length
    ? Math.round(items.reduce((s, i) => s + (i.dnaMatch || 75), 0) / items.length)
    : 0;

  return (
    <div className="screen wishlist-screen">
      <div className="wl-hdr">
        <div className="wl-back-row">
          <div className="back-btn" onClick={() => navigate(-1)}>←</div>
          <div>
            <div className="wl-title">♡ My Wishlist</div>
            <div className="wl-sub">{items.length} items · Avg DNA Match {avgMatch}%</div>
          </div>
        </div>
      </div>

      <div className="wl-body">
        {loading ? (
          <div className="wl-empty">Loading…</div>
        ) : items.length === 0 ? (
          <div className="wl-empty-state">
            <div className="wl-empty-icon">♡</div>
            <div className="wl-empty-title">Your wishlist is empty</div>
            <div className="wl-empty-sub">Tap the heart on any product to save it here</div>
            <button className="wl-browse-btn" onClick={() => navigate('/home')}>
              Browse Products
            </button>
          </div>
        ) : (
          <>
            {/* Summary card */}
            <div className="wl-summary">
              <div className="wl-sum-item">
                <div className="wl-sum-val">{items.length}</div>
                <div className="wl-sum-lbl">Items</div>
              </div>
              <div className="wl-sum-item">
                <div className="wl-sum-val">₹{totalValue.toLocaleString('en-IN')}</div>
                <div className="wl-sum-lbl">Total Value</div>
              </div>
              <div className="wl-sum-item">
                <div className="wl-sum-val">{avgMatch}%</div>
                <div className="wl-sum-lbl">Avg DNA Match</div>
              </div>
            </div>

            {/* Wishlist items */}
            <div className="wl-list">
              {items.map(item => (
                <div key={item.id} className="wl-card">
                  <div
                    className="wl-img-wrap"
                    onClick={() => navigate(`/product/${item.id}`)}
                  >
                    <img src={item.image} alt={item.name} className="wl-img" />
                    <div className="wl-dna-badge">🧬 {item.dnaMatch || 75}%</div>
                  </div>
                  <div className="wl-info">
                    <div className="wl-brand">{item.brand}</div>
                    <div
                      className="wl-name"
                      onClick={() => navigate(`/product/${item.id}`)}
                    >
                      {item.name}
                    </div>
                    <div className="wl-price">₹{(item.price || 0).toLocaleString('en-IN')}</div>

                    <div className="wl-actions">
                      <button className="wl-cart-btn" onClick={() => moveToCart(item)}>
                        Add to Cart
                      </button>
                      <button
                        className="wl-remove-btn"
                        onClick={() => removeItem(item.id)}
                        aria-label="Remove"
                      >
                        🗑
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {items.length > 0 && (
              <button
                className="wl-cart-all-btn"
                onClick={() => {
                  items.forEach(i => moveToCart(i));
                }}
              >
                Move All to Cart
              </button>
            )}
          </>
        )}
      </div>

      {toast && <div className="toast">{toast}</div>}
      <BottomNav />
    </div>
  );
}

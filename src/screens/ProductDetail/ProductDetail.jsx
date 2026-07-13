import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { apiRequest } from '../../api/client';
import BottomNav from '../../components/BottomNav/BottomNav';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';
import '../../styles/ProductDetail.css';

const SIZES = ['XS', 'S', 'M', 'L', 'XL'];

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, addToCart, addToWishlist } = useUser();

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);
  const [size, setSize] = useState('S');
  const [toast, setToast] = useState('');
  const [showAR, setShowAR] = useState(false);



  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 2500); };

  useEffect(() => {
    let cancelled = false;

    async function loadProduct() {
      setLoading(true);
      setError(null);

      try {
        const [productData, confidenceData] = await Promise.all([
          apiRequest(`/api/products/${id}`),
          apiRequest(`/api/recommend/confidence/${id}`, {
            method: 'POST',
            body: JSON.stringify({
              user_profile: user,
            }),
          }),
        ]);

        if (!cancelled) {
          setProduct({
            ...productData,
            confidence: confidenceData,
          });
        }
      } catch (requestError) {
        if (!cancelled) {
          setError(requestError);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadProduct();

    return () => {
      cancelled = true;
    };
  }, [id, user, retryKey]);

  const conf = product.confidence;
  const isWished = user.wishlist.includes(product.id);

  // Feature 7: DNA Dynamic Pricing (15% off if confidence >= 90)
  const isDnaDiscount = conf.overall >= 90;
  const finalPrice = isDnaDiscount ? Math.round(product.price * 0.85) : product.price;
  const discount = Math.round((1 - finalPrice / product.originalPrice) * 100);

  const handleAddToCart = () => {
    // Pass the final discounted price to the cart/memory
    const productToBuy = { ...product, price: finalPrice };
    addToCart(productToBuy, 'Added from product detail');
    showToast('Added to cart! Fashion Memory will track this 📖');
  };

  if (loading) {
    return (
      <div className="screen">
        <div className="page-loading">Loading product…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="screen">
        <ApiErrorState
          error={error}
          title="Product unavailable"
          onRetry={() => setRetryKey((value) => value + 1)}
        />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="screen">
        <ApiErrorState title="Product not found" />
      </div>
    );
  }

  return (
    <div className="screen det-screen">
      {/* Image */}
      <div className="det-img-wrap">
        <img src={product.image} alt={product.name} />
        <div className="det-hdr-btns">
          <div className="back-btn" onClick={() => navigate(-1)}>←</div>
          <button className="wish-top-btn" onClick={() => { addToWishlist(product.id); showToast(isWished ? 'Removed from wishlist' : 'Added to wishlist ❤️'); }}>
            {isWished ? '❤️' : '🤍'}
          </button>
        </div>
        <div className="det-conf-pill">
          <span className="det-score">{conf.overall}</span>
          <span className="det-score-lbl">Confidence Score</span>
        </div>
        <button
          className="ar-btn"
          onClick={() => setShowAR(true)}
          style={{ position: 'absolute', bottom: 15, left: 15, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(10px)', color: 'white', border: '1px solid rgba(255,255,255,0.2)', padding: '6px 12px', borderRadius: 20, fontSize: 12, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
        >
          📸 Try It On (AR)
        </button>
      </div>

      {/* Scrollable body */}
      <div className="det-body">
        <div>
          <div className="det-brand">{product.brand}</div>
          <div className="det-name">{product.name}</div>
          <div className="det-pr-row">
            <span className="det-price">₹{finalPrice.toLocaleString('en-IN')}</span>
            <span className="det-og">₹{product.originalPrice.toLocaleString('en-IN')}</span>
            <span className="det-disc">{discount}% off</span>
          </div>
          {isDnaDiscount && (
            <div style={{ marginTop: 8, padding: '6px 12px', background: 'rgba(57, 255, 20, 0.1)', color: 'var(--green)', borderRadius: 6, fontSize: 12, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6 }}>
              <span>💰</span> Because this is a 90%+ match, you unlocked a 15% DNA Discount!
            </div>
          )}
        </div>

        {/* Confidence Score Card */}
        <div className="conf-card">
          <div className="conf-card-hdr">
            <div><h3>🎯 Confidence Score</h3><p>Why this is perfect for you</p></div>
            <div className="conf-big grad-text">{conf.overall}</div>
          </div>
          {[
            { icon: '🧬', label: 'Style Match', val: conf.styleMatch },
            { icon: '📅', label: 'Occasion Match', val: conf.occasionMatch },
            { icon: '💰', label: 'Budget Match', val: conf.budgetMatch },
            { icon: '☁️', label: 'Weather Match', val: conf.weatherMatch },
            { icon: '👗', label: 'Wardrobe Fit', val: conf.wardrobeMatch },
          ].map(row => (
            <div key={row.label} className="conf-row">
              <span className="conf-icon">{row.icon}</span>
              <span className="conf-lbl">{row.label}</span>
              <div className="conf-bar-wrap">
                <div className="conf-bar-fill" style={{ '--target-w': `${row.val}%` }} />
              </div>
              <span className="conf-pct">{row.val}%</span>
            </div>
          ))}
        </div>

        {/* Why button */}
        <button className="btn-accent-outline" onClick={() => navigate(`/decision/${product.id}`)}>
          🤔 Why is this recommended for me? →
        </button>

        {/* Size */}
        <div>
          <div className="size-label">Select Size</div>
          <div className="size-row">
            {SIZES.map(s => (
              <div key={s} className={`size-chip ${size === s ? 'active' : ''}`} onClick={() => setSize(s)}>{s}</div>
            ))}
          </div>
        </div>

        <button className="btn-primary" onClick={handleAddToCart}>
          Add to Cart — ₹{finalPrice.toLocaleString('en-IN')}
        </button>
      </div>

      {/* AR Modal Overlay */}
      {showAR && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 1000, background: '#000', display: 'flex', flexDirection: 'column' }}>
          {/* Header */}
          <div style={{ padding: '48px 18px 14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontWeight: 800, color: '#fff', fontSize: 16 }}>📸 Virtual Try-On</div>
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', marginTop: 2 }}>See how it looks on you</div>
            </div>
            <div onClick={() => setShowAR(false)} style={{ fontSize: 28, cursor: 'pointer', color: '#fff', lineHeight: 1 }}>×</div>
          </div>

          {/* Camera Frame */}
          <div style={{ flex: 1, position: 'relative', background: '#111', margin: '0 18px', borderRadius: 16, overflow: 'hidden' }}>
            {/* Camera background simulation */}
            <div style={{
              position: 'absolute', inset: 0,
              background: 'linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              {/* Body outline guide */}
              <div style={{
                width: 140, height: 260, border: '2px dashed rgba(255,63,108,0.4)',
                borderRadius: 80, display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexDirection: 'column', gap: 8
              }}>
                <span style={{ fontSize: 32 }}>🧍</span>
                <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', textAlign: 'center' }}>Stand here</span>
              </div>
            </div>

            {/* Product overlay */}
            <img
              src={product.image}
              alt="Try On"
              style={{
                position: 'absolute', top: '30%', left: '50%',
                transform: 'translate(-50%, -30%)',
                width: '65%', opacity: 0.88,
                filter: 'drop-shadow(0 8px 24px rgba(255,63,108,0.3))'
              }}
            />

            {/* Corner guides */}
            {['0 auto auto 0', '0 0 auto auto', 'auto auto 0 0', 'auto 0 0 auto'].map((pos, i) => (
              <div key={i} style={{
                position: 'absolute', width: 20, height: 20,
                top: i < 2 ? 20 : 'auto', bottom: i >= 2 ? 20 : 'auto',
                left: i % 2 === 0 ? 20 : 'auto', right: i % 2 === 1 ? 20 : 'auto',
                borderTop: i < 2 ? '2px solid var(--accent)' : 'none',
                borderBottom: i >= 2 ? '2px solid var(--accent)' : 'none',
                borderLeft: i % 2 === 0 ? '2px solid var(--accent)' : 'none',
                borderRight: i % 2 === 1 ? '2px solid var(--accent)' : 'none',
              }} />
            ))}

            {/* Scanning line */}
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: 'var(--accent)', boxShadow: '0 0 12px var(--accent)', animation: 'scan 2.5s infinite linear' }} />
          </div>

          <style dangerouslySetInnerHTML={{
            __html: `
            @keyframes scan { 0% { top: 0%; opacity: 0; } 10% { opacity: 1; } 90% { opacity: 1; } 100% { top: 100%; opacity: 0; } }
          `}} />

          {/* Bottom info */}
          <div style={{ padding: '14px 18px 40px', textAlign: 'center' }}>
            <div style={{ color: '#fff', fontSize: 14, fontWeight: 700, marginBottom: 4 }}>{product.name}</div>
            <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12, lineHeight: 1.5 }}>
              This shows how the item would look on you.<br />
              In the full app, your camera would be used for a live preview.
            </div>
          </div>
        </div>
      )}

      {toast && <div className="toast">{toast}</div>}
      <BottomNav />
    </div>
  );
}

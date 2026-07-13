import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { apiRequest } from '../../api/client';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';
import '../../styles/DecisionIntelligence.css';

export default function DecisionIntelligence() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, addToCart } = useUser();

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadDecisionData() {
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

    loadDecisionData();

    return () => {
      cancelled = true;
    };
  }, [id, user, retryKey]);


  const conf = product.confidence;

  if (loading) {
    return (
      <div className="screen">
        <div className="page-loading">
          Loading decision intelligence…
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="screen">
        <ApiErrorState
          error={error}
          title="Decision intelligence unavailable"
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
    <div className="screen di-screen">
      <div className="di-hdr">
        <div className="back-btn" onClick={() => navigate(-1)}>←</div>
        <div className="di-hdr-text">
          <h3>Decision Intelligence</h3>
          <h2>Why this recommendation?</h2>
        </div>
      </div>

      <div className="di-body">
        <div className="di-hero">
          <img src={product.image} alt={product.name} />
          <div className="di-hero-info">
            <div className="di-hero-brand">{product.brand}</div>
            <div className="di-hero-name">{product.name}</div>
            <div className="di-hero-score">🎯 Confidence: {conf.overall}</div>
          </div>
        </div>

        <div className="di-sec-label">Why Myntra recommends this</div>

        <div className="di-reason">
          <div className="di-reason-icon" style={{ background: 'rgba(255,60,172,.1)', color: 'var(--accent)' }}>🧬</div>
          <div>
            <h4>Matches your DNA ({conf.styleMatch}%)</h4>
            <p>Your {user.identityName || 'Minimalist'} profile loves these aesthetics. This item is {conf.styleMatch}% aligned with your core style identity.</p>
          </div>
        </div>

        <div className="di-reason" style={{ animationDelay: '0.1s' }}>
          <div className="di-reason-icon" style={{ background: 'rgba(34,197,94,.1)', color: 'var(--green)' }}>💰</div>
          <div>
            <h4>Within your budget</h4>
            <p>At ₹{product.price.toLocaleString('en-IN')}, it falls perfectly within your {user.budget?.replace(/-/g, ' ') || 'budget'}. Value ratio is excellent at {Math.round((1 - product.price / product.originalPrice) * 100)}% discount.</p>
          </div>
        </div>

        <div className="di-reason" style={{ animationDelay: '0.2s' }}>
          <div className="di-reason-icon" style={{ background: 'rgba(120,75,160,.1)', color: '#A78BFA' }}>🎓</div>
          <div>
            <h4>Perfect for your occasions</h4>
            <p>You marked {user.occasions?.slice(0, 2).join(' and ') || 'casual'}. This works seamlessly for these events — no second outfit needed.</p>
          </div>
        </div>

        <div className="di-reason" style={{ animationDelay: '0.3s' }}>
          <div className="di-reason-icon" style={{ background: 'rgba(43,134,197,.1)', color: '#60A5FA' }}>👥</div>
          <div>
            <h4>Similar DNA users loved this <span className="new-badge">NEW</span></h4>
            <p>Users with 90%+ DNA match bought this in the last 7 days. This is a Real Eyes recommendation.</p>
          </div>
        </div>

        {conf.styleMatch < 70 && (
          <div className="di-warn">
            <div className="di-warn-icon">⚠️</div>
            <div className="di-warn-text">
              <strong>AI Regret Warning:</strong> This item has a low DNA match ({conf.styleMatch}%). Based on your history, items under 75% match are returned 60% of the time.
            </div>
          </div>
        )}

        <button className="btn-primary" onClick={() => { addToCart(product, 'Added after viewing Decision Intelligence'); navigate(-1); }}>
          Got it — Add to Cart
        </button>
      </div>
    </div>
  );
}

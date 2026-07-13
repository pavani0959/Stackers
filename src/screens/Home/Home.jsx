import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { apiRequest } from '../../api/client';
import ProductCard from '../../components/ProductCard/ProductCard';
import BottomNav from '../../components/BottomNav/BottomNav';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';
import '../../styles/Home.css';

const MOODS = [
  { id: 'quiet', icon: '😌', label: 'Quiet' },
  { id: 'bold', icon: '⚡', label: 'Bold' },
  { id: 'grind', icon: '💼', label: 'Grind' },
  { id: 'night', icon: '🌙', label: 'Night' },
];

export default function Home() {
  const navigate = useNavigate();
  const { user, updateUser } = useUser();
  const [mood, setMood] = useState(user.moodState || 'quiet');
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);
  const [antiTrend, setAntiTrend] = useState(false);
  const [showAllProducts, setShowAllProducts] = useState(false);
  const [showAllRealEyes, setShowAllRealEyes] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadFeed() {
      setLoading(true);
      setError(null);

      try {
        const data = await apiRequest('/api/recommend/feed', {
          method: 'POST',
          body: JSON.stringify({
            user_profile: user,
            anti_trend: antiTrend,
          }),
        });

        if (!cancelled) {
          setFeed(data);
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

    loadFeed();

    return () => {
      cancelled = true;
    };
  }, [user, antiTrend, retryKey]);

  const setMoodState = (m) => { setMood(m); updateUser({ moodState: m }); };
  const firstName = user.name?.trim().split(' ')[0] || 'Style Explorer';

  // Products to show - all 20 if "See all" clicked, else 4
  const gridProducts = showAllProducts ? feed : feed.slice(0, 4);
  const realEyesProducts = showAllRealEyes ? feed.slice(4) : feed.slice(6, 10);

  if (loading) {
    return (
      <div className="screen">
        <div className="page-loading">
          Loading your recommendations…
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="screen">
        <ApiErrorState
          error={error}
          title="Recommendations unavailable"
          onRetry={() => setRetryKey((value) => value + 1)}
        />
      </div>
    );
  }

  return (
    <div className="screen home-screen">
      {/* Header */}
      <div className="home-hdr">
        <div className="home-top">
          <div className="home-greet">Hey, <span className="grad-text">{firstName}</span> 👋</div>
          <div className="home-avatar" onClick={() => navigate('/identity-card')}>🧬</div>
        </div>
        <div className="home-search">
          🔍 Search by vibe, occasion, or item…
        </div>
        <div className="home-tabs">
          <div className="h-tab active">For You</div>
          <div className="h-tab" onClick={() => navigate('/reverse')}>🔮 Reverse Shop</div>
          <div className="h-tab" onClick={() => navigate('/community')}>🌐 Tribe</div>
        </div>
      </div>

      {/* Scrollable body */}
      <div className="home-body">
        {/* Anti-Trend Toggle */}
        <div className="anti-trend-bar">
          <div>
            <div style={{ fontWeight: 800, fontSize: 14 }}>🔀 Anti-Trend Mode</div>
            <div style={{ fontSize: 11, color: 'var(--text-2)' }}>Break out of your algorithm.</div>
          </div>
          <div className={`at-toggle ${antiTrend ? 'active' : ''}`} onClick={() => setAntiTrend(!antiTrend)}>
            <div className="at-knob"></div>
          </div>
        </div>

        {/* Mood Card */}
        <div className="mood-card">
          <div className="mood-title">🌡️ What's your vibe today? <span className="new-badge">NEW</span></div>
          <div className="mood-opts">
            {MOODS.map(m => (
              <button key={m.id} className={`mood-btn ${mood === m.id ? 'active' : ''}`} onClick={() => setMoodState(m.id)}>
                <span className="mood-icon">{m.icon}</span>
                {m.label}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-2)' }}>
            <div style={{ fontSize: 28, marginBottom: 10 }}>🧬</div>
            Loading ML Recommendations...
          </div>
        ) : (
          <>
            {/* DNA Banner */}
            <div className="dna-banner" style={{ background: antiTrend ? '#1f1a24' : '' }}>
              <div className="dna-banner-icon" style={{ background: antiTrend ? '#333' : '' }}>
                {antiTrend ? '🔀' : '🧬'}
              </div>
              <div>
                <h3 style={{ color: antiTrend ? '#fff' : '' }}>
                  {antiTrend ? 'Opposite of your DNA' : 'Filtered by your DNA'}
                </h3>
                <p style={{ color: antiTrend ? 'rgba(255,255,255,0.6)' : '' }}>
                  Every product is a <strong>mathematical {antiTrend ? 'mismatch' : 'match'}</strong> for {user.identityName || 'Minimalist'}.
                </p>
              </div>
            </div>

            {/* Products Grid - ALL products visible after See all */}
            <div>
              <div className="section-header">
                <span className="section-title">Built For Your DNA</span>
                <span className="section-action" onClick={() => setShowAllProducts(!showAllProducts)}>
                  {showAllProducts ? 'Show less' : `See all (${feed.length})`}
                </span>
              </div>
              <div className="prod-grid">
                {gridProducts.map(p => <ProductCard key={p.id} product={p} />)}
              </div>
              {showAllProducts && (
                <div style={{ textAlign: 'center', marginTop: 12 }}>
                  <button
                    onClick={() => setShowAllProducts(false)}
                    style={{ background: 'none', border: '1px solid var(--border)', borderRadius: 4, padding: '8px 20px', color: 'var(--text-2)', fontSize: 13, cursor: 'pointer' }}
                  >
                    Show Less
                  </button>
                </div>
              )}
            </div>

            {/* Real Eyes - horizontal scroll or full grid */}
            <div>
              <div className="section-header">
                <div className="re-title-row">
                  <span className="section-title">👁 Real Eyes</span>
                  <span className="new-badge">NEW</span>
                </div>
                <span className="section-action" onClick={() => setShowAllRealEyes(!showAllRealEyes)}>
                  {showAllRealEyes ? 'Show less' : 'View all'}
                </span>
              </div>
              <p className="re-subtitle">People with your DNA preferred these — not the algorithm.</p>

              {showAllRealEyes ? (
                <div className="prod-grid">
                  {realEyesProducts.map(p => <ProductCard key={p.id} product={p} />)}
                </div>
              ) : (
                <div className="h-scroll">
                  {realEyesProducts.map(p => (
                    <div key={p.id} className="h-card" onClick={() => navigate(`/product/${p.id}`)}>
                      <div className="h-card-img">
                        <img src={p.image} alt={p.name} loading="lazy" />
                        <div className="h-float">🧬 {p.confidence?.overall || 88}%</div>
                      </div>
                      <div className="h-card-info">
                        <div className="h-card-name">{p.name}</div>
                        <div className="h-card-price">₹{p.price.toLocaleString('en-IN')}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {/* Reverse CTA */}
        <div className="rs-cta" onClick={() => navigate('/reverse')}>
          <div className="rsc-icon">🔮</div>
          <div className="rsc-title">Reverse Shopping</div>
          <div className="rsc-sub">Tell us your occasion — we'll build the perfect outfit for your DNA</div>
          <button className="rs-cta-btn">Try It Now</button>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}

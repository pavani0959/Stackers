import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { apiRequest } from '../../api/client';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';
import BottomNav from '../../components/BottomNav/BottomNav';
import ProductCard from '../../components/ProductCard/ProductCard';
import { useUser } from '../../context/useUser';
import '../../styles/Home.css';

const MOODS = [
  {
    id: 'quiet',
    icon: '😌',
    label: 'Quiet',
  },
  {
    id: 'bold',
    icon: '⚡',
    label: 'Bold',
  },
  {
    id: 'grind',
    icon: '💼',
    label: 'Grind',
  },
  {
    id: 'night',
    icon: '🌙',
    label: 'Night',
  },
];

export default function Home() {
  const navigate = useNavigate();

  const {
    user,
    profileLoading,
    updateUser,
  } = useUser();

  const [mood, setMood] = useState(
    user.moodState || 'quiet',
  );

  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);
  const [antiTrend, setAntiTrend] = useState(false);

  const [showAllProducts, setShowAllProducts] =
    useState(false);

  const [showAllRealEyes, setShowAllRealEyes] =
    useState(false);

  useEffect(() => {
    /*
     * Do not request recommendations until the
     * server-backed user profile has finished loading.
     */
    if (profileLoading || !user?.id) {
      return undefined;
    }

    let cancelled = false;

    async function loadFeed() {
      setLoading(true);
      setError(null);

      try {
        const data = await apiRequest(
          '/api/recommend/feed',
          {
            method: 'POST',
            body: JSON.stringify({
              user_profile: user,
              anti_trend: antiTrend,
            }),
          },
        );

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
  }, [
    user,
    profileLoading,
    antiTrend,
    retryKey,
  ]);

  const setMoodState = (newMood) => {
    setMood(newMood);

    /*
     * Mood is temporary UI state, so updateUser
     * is still correct here.
     */
    updateUser({
      moodState: newMood,
    });
  };

  const firstName =
    user.name?.trim().split(' ')[0] ||
    'Style Explorer';

  const gridProducts = showAllProducts
    ? feed
    : feed.slice(0, 4);

  const realEyesProducts = showAllRealEyes
    ? feed.slice(4)
    : feed.slice(6, 10);

  /*
   * Show loading while either:
   * 1. the profile is loading from the server, or
   * 2. recommendations are loading.
   */
  if (profileLoading || loading) {
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
          onRetry={() =>
            setRetryKey(
              (currentValue) => currentValue + 1,
            )
          }
        />
      </div>
    );
  }

  return (
    <div className="screen home-screen">
      {/* Header */}
      <div className="home-hdr">
        <div className="home-top">
          <div className="home-greet">
            Hey,{' '}
            <span className="grad-text">
              {firstName}
            </span>{' '}
            👋
          </div>

          <div
            className="home-avatar"
            onClick={() =>
              navigate('/identity-card')
            }
          >
            🧬
          </div>
        </div>

        <div className="home-search" onClick={() => navigate('/search')}>
          🔍 Search by vibe, occasion, or item…
        </div>


        <div className="home-tabs">
          <div className="h-tab active">
            For You
          </div>

          <div
            className="h-tab"
            onClick={() => navigate('/reverse')}
          >
            🔮 Reverse Shop
          </div>

          <div
            className="h-tab"
            onClick={() =>
              navigate('/community')
            }
          >
            🌐 Tribe
          </div>
        </div>
      </div>

      {/* Scrollable body */}
      <div className="home-body">
        {/* Anti-Trend Toggle */}
        <div className="anti-trend-bar">
          <div>
            <div
              style={{
                fontWeight: 800,
                fontSize: 14,
              }}
            >
              🔀 Anti-Trend Mode
            </div>

            <div
              style={{
                fontSize: 11,
                color: 'var(--text-2)',
              }}
            >
              Break out of your algorithm.
            </div>
          </div>

          <div
            className={`at-toggle ${
              antiTrend ? 'active' : ''
            }`}
            onClick={() =>
              setAntiTrend(
                (currentValue) => !currentValue,
              )
            }
          >
            <div className="at-knob" />
          </div>
        </div>

        {/* Mood Card */}
        <div className="mood-card">
          <div className="mood-title">
            🌡️ What&apos;s your vibe today?{' '}
            <span className="new-badge">
              NEW
            </span>
          </div>

          <div className="mood-opts">
            {MOODS.map((moodOption) => (
              <button
                key={moodOption.id}
                type="button"
                className={`mood-btn ${
                  mood === moodOption.id
                    ? 'active'
                    : ''
                }`}
                onClick={() =>
                  setMoodState(moodOption.id)
                }
              >
                <span className="mood-icon">
                  {moodOption.icon}
                </span>

                {moodOption.label}
              </button>
            ))}
          </div>
        </div>

        {/* DNA Banner */}
        <div
          className="dna-banner"
          style={{
            background: antiTrend
              ? '#1f1a24'
              : '',
          }}
        >
          <div
            className="dna-banner-icon"
            style={{
              background: antiTrend
                ? '#333'
                : '',
            }}
          >
            {antiTrend ? '🔀' : '🧬'}
          </div>

          <div>
            <h3
              style={{
                color: antiTrend ? '#fff' : '',
              }}
            >
              {antiTrend
                ? 'Opposite of your DNA'
                : 'Filtered by your DNA'}
            </h3>

            <p
              style={{
                color: antiTrend
                  ? 'rgba(255,255,255,0.6)'
                  : '',
              }}
            >
              Every product is a{' '}
              <strong>
                mathematical{' '}
                {antiTrend
                  ? 'mismatch'
                  : 'match'}
              </strong>{' '}
              for{' '}
              {user.identityName ||
                'Minimalist'}
              .
            </p>
          </div>
        </div>

        {/* Products Grid */}
        <div>
          <div className="section-header">
            <span className="section-title">
              Built For Your DNA
            </span>

            <span
              className="section-action"
              onClick={() =>
                setShowAllProducts(
                  (currentValue) =>
                    !currentValue,
                )
              }
            >
              {showAllProducts
                ? 'Show less'
                : `See all (${feed.length})`}
            </span>
          </div>

          <div className="prod-grid">
            {gridProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
              />
            ))}
          </div>

          {showAllProducts && (
            <div
              style={{
                textAlign: 'center',
                marginTop: 12,
              }}
            >
              <button
                type="button"
                onClick={() =>
                  setShowAllProducts(false)
                }
                style={{
                  background: 'none',
                  border:
                    '1px solid var(--border)',
                  borderRadius: 4,
                  padding: '8px 20px',
                  color: 'var(--text-2)',
                  fontSize: 13,
                  cursor: 'pointer',
                }}
              >
                Show Less
              </button>
            </div>
          )}
        </div>

        {/* Real Eyes */}
        <div>
          <div className="section-header">
            <div className="re-title-row">
              <span className="section-title">
                👁 Real Eyes
              </span>

              <span className="new-badge">
                NEW
              </span>
            </div>

            <span
              className="section-action"
              onClick={() =>
                setShowAllRealEyes(
                  (currentValue) =>
                    !currentValue,
                )
              }
            >
              {showAllRealEyes
                ? 'Show less'
                : 'View all'}
            </span>
          </div>

          <p className="re-subtitle">
            People with your DNA preferred these
            — not the algorithm.
          </p>

          {showAllRealEyes ? (
            <div className="prod-grid">
              {realEyesProducts.map(
                (product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                  />
                ),
              )}
            </div>
          ) : (
            <div className="h-scroll">
              {realEyesProducts.map(
                (product) => (
                  <div
                    key={product.id}
                    className="h-card"
                    onClick={() =>
                      navigate(
                        `/product/${product.id}`,
                      )
                    }
                  >
                    <div className="h-card-img">
                      <img
                        src={product.image}
                        alt={product.name}
                        loading="lazy"
                      />

                      <div className="h-float">
                        🧬{' '}
                        {product.confidence
                          ?.overall || 88}
                        %
                      </div>
                    </div>

                    <div className="h-card-info">
                      <div className="h-card-name">
                        {product.name}
                      </div>

                      <div className="h-card-price">
                        ₹
                        {product.price.toLocaleString(
                          'en-IN',
                        )}
                      </div>
                    </div>
                  </div>
                ),
              )}
            </div>
          )}
        </div>

        {/* Reverse CTA */}
        <div
          className="rs-cta"
          onClick={() => navigate('/reverse')}
        >
          <div className="rsc-icon">🔮</div>

          <div className="rsc-title">
            Reverse Shopping
          </div>

          <div className="rsc-sub">
            Tell us your occasion — we&apos;ll
            build the perfect outfit for your DNA
          </div>

          <button
            type="button"
            className="rs-cta-btn"
          >
            Try It Now
          </button>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
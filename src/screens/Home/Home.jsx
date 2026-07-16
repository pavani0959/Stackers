import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDecisionFeed } from '../../api/decisions';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';
import BottomNav from '../../components/BottomNav/BottomNav';
import ProductCard from '../../components/ProductCard/ProductCard';
import { useUser } from '../../context/useUser';
import '../../styles/Home.css';

const MOODS = [
  { id: 'quiet', icon: '', label: 'Quiet' },
  { id: 'bold', icon: '⚡', label: 'Bold' },
  { id: 'grind', icon: '', label: 'Grind' },
  { id: 'night', icon: '', label: 'Night' },
];

export default function Home() {
  const navigate = useNavigate();
  const { user, profileLoading, updateUser } = useUser();
  const [mood, setMood] = useState(user.moodState || 'quiet');
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);
  const [antiTrend, setAntiTrend] = useState(false);
  const [showAllProducts, setShowAllProducts] = useState(false);
  const [showAllMatches, setShowAllMatches] = useState(false);
  const primaryOccasion = user.occasions?.[0] ?? null;

  useEffect(() => {
    if (profileLoading || !user?.id) {
      return undefined;
    }

    let cancelled = false;

    async function loadFeed() {
      setLoading(true);
      setError(null);
      try {
        const data = await getDecisionFeed({
          limit: 20,
          antiTrend,
          context: {
            occasion: primaryOccasion,
          },
        });
        if (!cancelled) {
          setFeed(data.items);
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
    user?.id,
    primaryOccasion,
    profileLoading,
    antiTrend,
    retryKey,
  ]);

  const firstName = user.name?.trim().split(' ')[0] || 'Style Explorer';
  const gridProducts = showAllProducts ? feed : feed.slice(0, 4);
  const additionalMatches = showAllMatches
    ? feed.slice(4)
    : feed.slice(4, 8);

  function setMoodState(newMood) {
    setMood(newMood);
    updateUser({ moodState: newMood });
  }

  if (profileLoading || loading) {
    return <div className="screen-center">Loading your recommendations…</div>;
  }

  if (error) {
    return (
      <ApiErrorState
        error={error}
        title="Recommendations could not be loaded"
        onRetry={() => setRetryKey((value) => value + 1)}
      />
    );
  }

  return (
    <div className="screen home-screen">
      <header className="home-hdr">
        <div className="home-top">
          <h1 className="home-greet">Hey, {firstName}</h1>
          <button
            type="button"
            className="home-avatar"
            onClick={() => navigate('/identity-card')}
            aria-label="Open identity card"
          >
            {firstName[0]?.toUpperCase() || 'S'}
          </button>
        </div>

        <button
          type="button"
          className="home-search"
          onClick={() => navigate('/search')}
        >
          Search by vibe, occasion, or item…
        </button>

        <nav className="home-tabs" aria-label="Home sections">
          <span className="h-tab active">For You</span>
          <button
            type="button"
            className="h-tab"
            onClick={() => navigate('/reverse')}
          >
            Reverse Shop
          </button>
          <button
            type="button"
            className="h-tab"
            onClick={() => navigate('/community')}
          >
            Tribe
          </button>
        </nav>
      </header>

      <main className="home-body">
        <section className="anti-trend-bar">
          <div>
            <strong>Anti-Trend Mode</strong>
            <p>Show the lowest-scoring profile matches first.</p>
          </div>
          <button
            type="button"
            className={`at-toggle ${antiTrend ? 'active' : ''}`}
            onClick={() => setAntiTrend((value) => !value)}
            aria-pressed={antiTrend}
            aria-label="Toggle anti-trend mode"
          >
            <span className="at-knob" />
          </button>
        </section>

        <section className="mood-card">
          <p className="mood-title">What's your vibe today? NEW</p>
          <div className="mood-opts">
            {MOODS.map((option) => (
              <button
                type="button"
                key={option.id}
                className={`mood-btn ${mood === option.id ? 'active' : ''}`}
                onClick={() => setMoodState(option.id)}
              >
                <span className="mood-icon">{option.icon}</span>
                {option.label}
              </button>
            ))}
          </div>
        </section>

        <section className="dna-banner">
          <span className="dna-banner-icon">{antiTrend ? '' : ''}</span>
          <div>
            <h3>{antiTrend ? 'Opposite profile ranking' : 'Ranked by your saved DNA'}</h3>
            <p>
              Every score is calculated from the server-owned profile and
              stored as an immutable decision snapshot.
            </p>
          </div>
        </section>

        <section>
          <div className="section-title-row">
            <h2>Built For Your DNA</h2>
            <button
              type="button"
              onClick={() => setShowAllProducts((value) => !value)}
            >
              {showAllProducts ? 'Show less' : `See all (${feed.length})`}
            </button>
          </div>
          <div className="prod-grid">
            {gridProducts.map((decision) => (
              <ProductCard
                key={decision.snapshot_id}
                decision={decision}
              />
            ))}
          </div>
        </section>

        <section>
          <div className="section-title-row">
            <h2>More matches for your current profile</h2>
            <button
              type="button"
              onClick={() => setShowAllMatches((value) => !value)}
            >
              {showAllMatches ? 'Show less' : 'View all'}
            </button>
          </div>
          <p className="re-subtitle">
            Additional products ranked using your saved Fashion DNA and
            preferences.
          </p>
          <div className="prod-grid">
            {additionalMatches.map((decision) => (
              <ProductCard
                key={decision.snapshot_id}
                decision={decision}
              />
            ))}
          </div>
        </section>

        <button
          type="button"
          className="rs-cta"
          onClick={() => navigate('/reverse')}
        >
          <div className="rsc-icon"></div>
          <div className="rsc-title">Reverse Shopping</div>
          <div className="rsc-sub">
            Tell us your occasion and budget to build an outfit.
          </div>
          <span className="rs-cta-btn">Try It Now</span>
        </button>
      </main>

      <BottomNav />
    </div>
  );
}

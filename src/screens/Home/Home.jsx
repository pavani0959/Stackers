import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDecisionFeed } from '../../api/decisions';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';
import BottomNav from '../../components/BottomNav/BottomNav';
import CartIconButton from '../../components/CartIconButton/CartIconButton';
import ProductCard from '../../components/ProductCard/ProductCard';
import { useUser } from '../../context/useUser';
import '../../styles/Home.css';

const Icons = {
  Search: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>,
  Bell: () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>,
  ForYou: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>,
  Camera: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>,
  Tribe: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>,
  Crown: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5zm14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/></svg>,
  ArrowLeft: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>,
  ArrowRight: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>,
  SparkleBadge: () => <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="12" fill="#FF3F6C"/><path d="M12 4.5l1.5 5.5 5.5 1.5-5.5 1.5L12 18.5l-1.5-5.5L5 11.5l5.5-1.5L12 4.5z" fill="white"/></svg>
};

import { Moon, Zap, Flame, Building2 } from 'lucide-react';

const MOODS = [
  { id: 'quiet', icon: <Moon size={16} />, label: 'Quiet' },
  { id: 'bold', icon: <Zap size={16} />, label: 'Bold' },
  { id: 'grind', icon: <Flame size={16} />, label: 'Grind' },
  { id: 'night', icon: <Building2 size={16} />, label: 'Night' },
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
    if (profileLoading || !user?.id) return undefined;
    let cancelled = false;
    async function loadFeed() {
      setLoading(true);
      setError(null);
      try {
        const data = await getDecisionFeed({ limit: 20, antiTrend, context: { occasion: primaryOccasion, vibe: mood } });
        if (!cancelled) setFeed(data.items);
      } catch (requestError) {
        if (!cancelled) setError(requestError);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadFeed();
    return () => { cancelled = true; };
  }, [user?.id, primaryOccasion, profileLoading, antiTrend, mood, retryKey]);

  const firstName = user.name?.trim().split(' ')[0] || 'Style Explorer';
  const gridProducts = showAllProducts ? feed : feed.slice(0, 4);
  const additionalMatches = showAllMatches ? feed.slice(4) : feed.slice(4, 8);

  function setMoodState(newMood) {
    setMood(newMood);
    updateUser({ moodState: newMood });
  }

  if (profileLoading || loading) return <div className="screen-center">Loading your recommendations…</div>;
  if (error) return <ApiErrorState error={error} title="Recommendations could not be loaded" onRetry={() => setRetryKey((value) => value + 1)} />;

  return (
    <div className="screen home-screen">
      <header className="home-hdr">
        <div className="home-hdr-bg">
          <svg width="100%" height="100%" preserveAspectRatio="none" viewBox="0 0 400 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0 60 Q 150 150 400 30" stroke="rgba(255, 215, 0, 0.3)" strokeWidth="1.5" fill="none" />
            <path d="M0 80 Q 200 180 400 50" stroke="rgba(255, 215, 0, 0.2)" strokeWidth="1" fill="none" />
            <path d="M-50 100 Q 180 220 450 70" stroke="rgba(255, 215, 0, 0.15)" strokeWidth="1" fill="none" />
          </svg>
        </div>
        
        <div className="home-hdr-content">
          <div className="home-top">
            <h1 className="home-greet">Hey, {firstName} 👋</h1>
            <div className="home-top-actions">
              <button type="button" className="home-bell-btn">
                <Icons.Bell />
                <span className="home-bell-dot"></span>
              </button>
              <CartIconButton className="home-avatar" style={{ background: 'transparent', width: '36px', height: '36px' }} />
              <button type="button" className="home-avatar" onClick={() => navigate('/profile')} aria-label="Open profile">
                {firstName[0]?.toUpperCase() || 'S'}
              </button>
            </div>
          </div>

          <button type="button" className="home-search-bar" onClick={() => navigate('/search')}>
            <Icons.Search />
            <span className="home-search-placeholder">Search by vibe, occasion or item...</span>
          </button>

          <nav className="home-tabs" aria-label="Home sections">
            <button type="button" className="h-tab active"><Icons.ForYou /> For You</button>
            <button type="button" className="h-tab" onClick={() => navigate('/reverse')}><Icons.Camera /> Reverse Shop</button>
            <button type="button" className="h-tab" onClick={() => navigate('/community')}><Icons.Tribe /> Tribe</button>
          </nav>
        </div>
      </header>

      <main className="home-body">
        <section className="anti-trend-bar">
          <div className="at-bar-left">
            <Icons.SparkleBadge />
            <div className="at-bar-text">
              <div className="at-bar-title">
                Anti-Trend Mode <span className="at-badge">NEW</span>
              </div>
              <p>Show the lowest-scoring profile matches first.</p>
            </div>
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
          <p className="mood-title">What's your vibe today? ✨</p>
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
          <div className="dna-banner-icon"><Icons.Crown /></div>
          <div className="dna-banner-text">
            <h3>Ranked by your saved DNA</h3>
            <p>Every score is calculated from the server-owned profile and stored as an immutable decision snapshot.</p>
          </div>
          <div className="dna-banner-illus">
             <img src="/catalog/myi-top-0009.png" alt="" aria-hidden="true" style={{width: 40, height: 40, objectFit: 'cover', borderRadius: '50%'}} 
                 onError={(e) => { e.currentTarget.style.display = 'none'; }} />
          </div>
        </section>

        <section className="h-product-section">
          <div className="sh-header">
            <div className="sh-left">
              <h2>Built For Your DNA</h2>
              <button type="button" className="sh-link" onClick={() => setShowAllProducts((value) => !value)}>
                See all ({feed.length}) &gt;
              </button>
            </div>
            <div className="sh-right">
              <button type="button" className="sh-nav-btn"><Icons.ArrowLeft /></button>
              <button type="button" className="sh-nav-btn"><Icons.ArrowRight /></button>
            </div>
          </div>
          
          <div className="prod-scroll-row">
            {gridProducts.map((decision) => (
              <div className="prod-scroll-item" key={decision.snapshot_id}>
                <ProductCard decision={decision} />
              </div>
            ))}
          </div>
        </section>

        <section className="h-grid-section">
          <div className="sh-header-col">
            <h2>More matches for your current profile</h2>
            <button type="button" className="sh-link" onClick={() => setShowAllMatches((value) => !value)}>
              View all &gt;
            </button>
            <p className="sh-subtitle">Additional products ranked using your saved Fashion DNA and preferences.</p>
          </div>
          
          <div className="prod-grid">
            {additionalMatches.map((decision, index) => (
              <ProductCard decision={decision} key={decision.snapshot_id} index={index} variant="gradient" />
            ))}
          </div>
        </section>

        <button type="button" className="rs-cta" onClick={() => navigate('/reverse')}>
          <div className="rsc-illus-img">
            <img src="/catalog/myi-top-0009.png" alt="" aria-hidden="true" style={{width: 60, height: 60, objectFit: 'cover', borderRadius: '8px'}} onError={(e) => { e.currentTarget.style.display = 'none'; }} />
          </div>
          <div className="rsc-content">
            <div className="rsc-title">Reverse Shopping</div>
            <div className="rsc-sub">Tell us your occasion and budget to build an outfit.</div>
            <span className="rs-cta-btn">Try It Now &gt;</span>
          </div>
        </button>
      </main>

      <BottomNav />
    </div>
  );
}

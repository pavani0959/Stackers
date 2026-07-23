import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { apiRequest } from '../../api/client';
import { useReducedMotion } from '../../hooks/useReducedMotion';
import { gsap } from '../../motion/gsap';
import BottomNav from '../../components/BottomNav/BottomNav';
import ProductCard from '../../components/ProductCard/ProductCard';
import '../../styles/ReverseShopping.css';
import {
  ArrowLeft,
  Mic,
  Sparkles,
  ArrowRight,
  Heart,
  Briefcase,
  PartyPopper,
  Moon,
  GraduationCap,
  ShoppingBag,
  Flower2,
  Music,
  Sun,
  Calendar,
  IndianRupee,
  Dna,
  User,
  Zap,
} from 'lucide-react';

const QUICK_PROMPTS = [
  { label: 'Interview', icon: <Briefcase size={16} />, text: 'College interview tomorrow, smart casual, ₹6000' },
  { label: 'College Fest', icon: <PartyPopper size={16} />, text: 'College fest Saturday, retro theme, ₹4500' },
  { label: 'First Date', icon: <Heart size={16} />, text: 'First date at a cafe, casual but cute, ₹4500' },
  { label: 'Night Out', icon: <Moon size={16} />, text: 'Night out with friends, sleek elegant look, ₹4500' },
  { label: 'Campus', icon: <GraduationCap size={16} />, text: 'Casual campus day, comfortable and clean, ₹3000' },
];

const INSPIRATION_PROMPTS = [
  { icon: <ShoppingBag size={18} />, label: 'Old money aesthetic for college', text: 'Old money aesthetic outfit for college, classic elegant, ₹5000' },
  { icon: <Flower2 size={18} />, label: 'Pinterest Korean outfit', text: 'Pinterest-style Korean minimal outfit, soft pastels, ₹4000' },
  { icon: <Music size={18} />, label: 'Concert look under ₹3000', text: 'Concert outfit, trendy and bold, budget ₹3000' },
  { icon: <Briefcase size={18} />, label: 'Internship interview', text: 'Internship interview, formal minimal look, ₹5000' },
  { icon: <Sun size={18} />, label: 'Beach vacation in Goa', text: 'Goa beach vacation outfits, breezy colorful, ₹4000' },
];

const AI_FEATURES = [
  { icon: <Calendar size={20} />, bg: '#fff1f2', label: 'Occasion', desc: 'Where & when' },
  { icon: <IndianRupee size={20} />, bg: '#fef2f2', label: 'Budget', desc: 'What fits you' },
  { icon: <Sun size={20} />, bg: '#ecfdf5', label: 'Weather', desc: 'Adapts to weather' },
  { icon: <Dna size={20} />, bg: '#eef2ff', label: 'Fashion DNA', desc: 'Your unique style' },
  { icon: <Heart size={20} />, bg: '#fdf2f8', label: 'Preferences', desc: 'Colours, brands & more' },
  { icon: <User size={20} />, bg: '#f0f9ff', label: 'Body Fit', desc: 'Perfect fit for you' },
];

function OutfitItem({ item, onClick }) {
  const [imgError, setImgError] = useState(false);

  return (
    <button
      type="button"
      className="outfit-item"
      aria-label={`View ${item.name}`}
      onClick={onClick}
    >
      <div className="outfit-item-img-wrap">
        {!imgError ? (
          <img
            src={item.image}
            alt={item.name}
            loading="lazy"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="img-fallback">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg>
            <span>Image unavailable</span>
          </div>
        )}
      </div>

      <span className="outfit-item-lbl">
        <span className="outfit-item-cat">
          {item.category.toUpperCase()}
        </span>

        <span>
          ₹{item.price.toLocaleString('en-IN')}
        </span>
      </span>
    </button>
  );
}

export default function ReverseShopping() {
  const navigate = useNavigate();
  const {
    user,
    addToCart,
  } = useUser();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [toast, setToast] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [micError, setMicError] = useState('');
  const resultsRef = useRef(null);
  const reducedMotion = useReducedMotion();

  // Animate outfit cards whenever new results arrive
  useEffect(() => {
    if (!results || reducedMotion || !resultsRef.current) return;
    const cards = resultsRef.current.querySelectorAll('.outfit-card');
    if (!cards.length) return;
    gsap.fromTo(
      cards,
      { y: 32, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.45, stagger: 0.12, ease: 'power3.out' },
    );
  }, [results, reducedMotion]);

  const showToast = (message) => {
    setToast(message);
    setTimeout(() => setToast(''), 3000);
  };

  const handleMicClick = () => {
    setMicError('');
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setMicError('Voice not supported in this browser. Please use Chrome.');
      showToast('❌ Use Chrome for voice search');
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
      setMicError('');
    };

    recognition.onend = () => setIsListening(false);

    recognition.onerror = (event) => {
      setIsListening(false);
      if (event.error === 'not-allowed') {
        setMicError('Microphone blocked. Click the 🔒 icon in your browser address bar and allow microphone.');
        showToast('❌ Mic blocked — allow access in browser');
      } else if (event.error === 'no-speech') {
        setMicError('No speech detected. Tap the mic and speak clearly.');
        showToast('🎤 No speech detected, try again');
      } else {
        setMicError(`Error: ${event.error}. Try again.`);
      }
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      showToast(`✅ Heard: "${transcript}"`);
    };

    try {
      recognition.start();
    } catch {
      setMicError('Could not start microphone. Try refreshing the page.');
    }
  };

  const handleGenerate = async () => {
    if (!input.trim()) {
      showToast('Please describe your occasion first');
      return;
    }

    setLoading(true);
    setResults(null);

    try {
      const data = await apiRequest('/api/recommend/reverse', {
        method: 'POST',
        body: JSON.stringify({ prompt: input, user_profile: user }),
      });
      setResults(data);
    } catch (error) {
      console.error(error);
      showToast('❌ Could not connect to backend');
    } finally {
      setLoading(false);
    }
  };

  const handleAddOutfitToCart = (group) => {
    group.items.forEach((item) => {
      addToCart({
        ...item,

        /*
         * Reverse Shopping does not currently provide
         * a size-selection UI. Use the first supplied
         * size when available, otherwise default to M.
         */
        selectedSize:
          item.sizes?.[0] ?? 'M',

        source: 'reverse_shopping',
      });
    });

    showToast(
      `Outfit ${group.index} added to cart`,
    );
  };

  const hasResults = Boolean(results || loading);
  const outfitGroups = results?.outfits || [];

  return (
    <div className="screen rs-screen">
      {/* ── Header ── */}
      <div className="rs-hdr">
        <div className="rs-back-row">
          <button
            type="button"
            className="rs-back-btn"
            onClick={() => navigate(-1)}
            aria-label="Go back"
          >
            <ArrowLeft aria-hidden="true" size={20} />
          </button>
          <span className="rs-crystal">🔮</span>
          <div className="rs-hdr-text">
            <h1 className="rs-title">Reverse Shopping</h1>
            <p className="rs-sub-pink">Create your perfect outfit with AI ✨</p>
            <p className="rs-sub">Tell us your occasion. We build your outfit.</p>
          </div>
        </div>
      </div>

      {/* ── Body ── */}
      <div className="rs-body">
        <div className={`rs-layout ${hasResults ? 'results-mode' : ''}`}>
          {/* ── Main column ── */}
          <div className="rs-main">
            {/* Input card */}
            <div className={`rs-input-card ${hasResults ? 'compact' : ''}`}>
              <div className="rs-input-lbl">Describe your occasion, vibe, or event ✨</div>
              <div className="rs-input-wrapper">
                <textarea
                  className="rs-textarea"
                  rows={hasResults ? 1 : 5}
                  placeholder={
                    hasResults
                      ? 'Describe your event…'
                      : 'Describe your event…\n\nExamples:\n• College fest Saturday, retro theme, budget ₹1500\n• Internship interview, formal, minimal look\n• First date, cute and classy\n• Night out with friends, rooftop party\n• Goa trip, beach vacation outfits'
                  }
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                />
                <button
                  type="button"
                  className={`rs-mic-btn ${isListening ? 'listening' : ''}`}
                  onClick={handleMicClick}
                  aria-label={isListening ? 'Stop voice input' : 'Use voice input'}
                  aria-pressed={isListening}
                >
                  <Mic aria-hidden="true" size={18} />
                </button>
              </div>
              {isListening && (
                <div className="rs-mic-status">
                  <span className="rs-mic-dot" /> Listening… speak your occasion clearly
                </div>
              )}
              {micError && <div className="rs-mic-error">⚠️ {micError}</div>}

              {/* Popular Ideas — integrated into card in results mode */}
              {hasResults && (
                <div className="rs-pills-row inline">
                  {QUICK_PROMPTS.map((prompt) => (
                    <button
                      type="button"
                      key={prompt.label}
                      className={`rs-pill ${input === prompt.text ? 'active' : ''}`}
                      onClick={() => setInput(prompt.text)}
                    >
                      <span className="rs-pill-icon">{prompt.icon}</span>
                      {prompt.label}
                    </button>
                  ))}
                  <button type="button" className="rs-pill rs-pill-more">•••</button>
                </div>
              )}
            </div>

            {/* Empty State Only Sections */}
            {!hasResults && (
              <>
                <div className="rs-pills-section">
                  <div className="rs-pills-label">✨ Popular Ideas</div>
                  <div className="rs-pills-row">
                    {QUICK_PROMPTS.map((prompt) => (
                      <button
                        type="button"
                        key={prompt.label}
                        className={`rs-pill ${input === prompt.text ? 'active' : ''}`}
                        onClick={() => setInput(prompt.text)}
                      >
                        <span className="rs-pill-icon">{prompt.icon}</span>
                        {prompt.label}
                      </button>
                    ))}
                    <button type="button" className="rs-pill rs-pill-more">•••</button>
                  </div>
                </div>

                <div className="rs-pills-section">
                  <div className="rs-pills-label">✨ Need inspiration? Try these</div>
                  <div className="rs-inspiration-row">
                    {INSPIRATION_PROMPTS.map((prompt) => (
                      <button
                        type="button"
                        key={prompt.label}
                        className={`rs-insp-pill ${input === prompt.text ? 'active' : ''}`}
                        onClick={() => setInput(prompt.text)}
                      >
                        <span className="rs-insp-icon">{prompt.icon}</span>
                        <span className="rs-insp-text">{prompt.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}

            {/* Generate button */}
            <button
              type="button"
              className={`rs-gen-btn ${hasResults ? 'rs-gen-again' : ''}`}
              onClick={handleGenerate}
              disabled={loading}
            >
              <Sparkles aria-hidden="true" size={18} />
              <span>
                {loading
                  ? 'Building Your Outfits…'
                  : hasResults
                    ? 'GENERATE AGAIN'
                    : 'GENERATE MY OUTFITS'}
              </span>
              {!hasResults && <ArrowRight aria-hidden="true" size={18} />}
            </button>

            {/* Trust signal - empty state only */}
            {!hasResults && (
              <div className="rs-trust-row">
                <span>🛡 100% Personalised</span>
                <span className="rs-trust-dot">•</span>
                <span>🤖 AI-Powered</span>
                <span className="rs-trust-dot">•</span>
                <span>❤️ Styled for You</span>
              </div>
            )}
          </div>

          {/* ── Sidebar (Empty State Only) ── */}
          {!hasResults && (
            <aside className="rs-sidebar">
              <div className="rs-sidebar-card">
                <h3 className="rs-sidebar-title">✨ AI understands</h3>
                <div className="rs-ai-list">
                  {AI_FEATURES.map((feature) => (
                    <div className="rs-ai-row" key={feature.label}>
                      <div className="rs-ai-icon" style={{ background: feature.bg }}>
                        {feature.icon}
                      </div>
                      <div>
                        <div className="rs-ai-label">{feature.label}</div>
                        <div className="rs-ai-desc">{feature.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </aside>
          )}
        </div>

        {/* ── Loading state ── */}
        {loading && (
          <div className="rs-loading-wrap">
            <div className="rs-spinner">🧬</div>
            <div className="rs-loading-title">Building your outfits…</div>
            <div className="rs-loading-sub">
              NLP matching · DNA filtering · Full-outfit budget check · {user.identityName || 'Your Style'}
            </div>
          </div>
        )}

        {/* ── Results state ── */}
        {results && (
          <div className="rs-results-view" ref={resultsRef}>
            {/* Budget Banner */}
            <div className={`rs-budget-banner ${results.within_budget ? 'success' : 'warning'}`}>
              <div className="rs-budget-banner-icon">
                {results.within_budget ? '✅' : '⚠️'}
              </div>
              <div className="rs-budget-banner-content">
                <div className="rs-budget-banner-title">Budget validated</div>
                <div className="rs-budget-banner-desc">Built {outfitGroups.length} complete outfit(s) within ₹{results.budget_limit.toLocaleString('en-IN')}.</div>
                <div className="rs-budget-banner-meta">
                  Budget score: <span className="score-good">you're great!</span> • Left: ₹{Math.max(0, results.budget_limit - (outfitGroups[0]?.total || 0)).toLocaleString('en-IN')}
                </div>
              </div>
              <div className="rs-budget-banner-img">
                🛍️
              </div>
            </div>

            {/* Stepper Row */}
            <div className="rs-stepper">
              <span className="rs-step active"><Briefcase size={16} /></span>
              <span className="rs-step-line active" />
              <span className="rs-step active"><Zap size={16} /></span>
              <span className="rs-step-line" />
              <span className="rs-step"><Sparkles size={16} /></span>
            </div>

            {/* Results Header */}
            {outfitGroups.length > 0 && (
              <div className="rs-outfits-section">
                <div className="rs-outfits-hdr">
                  <h3>{outfitGroups.length} Completed Outfits ✨</h3>
                  <p>Budget matched • DNA matched • All unique products</p>
                </div>

                <div className="rs-outfits-grid">
                  {outfitGroups.map((group) => {
                    const isStretch = group.index === 3 || group.label?.toUpperCase() === 'STYLE STRETCH';
                    const badgeLabel = group.label || (group.index === 1 ? 'BEST MATCH' : group.index === 2 ? 'BUDGET SMART' : 'STYLE STRETCH');
                    const badgeClass = isStretch ? 'stretch' : (group.index === 1 ? 'best' : 'smart');

                    return (
                      <div key={group.index} className={`rs-outfit-card ${isStretch ? 'is-stretch' : ''}`}>
                        <div className="rs-outfit-hdr">
                          <div className="rs-outfit-hdr-left">
                            <span className={`rs-outfit-badge ${badgeClass}`}>
                              {badgeLabel}
                            </span>
                            <span className="rs-outfit-title">Outfit {group.index}</span>
                          </div>
                          <div className="rs-outfit-match">
                            <Heart size={14} fill="#ff3f6c" color="#ff3f6c" /> {group.score || (isStretch ? 78 : 76)}%
                          </div>
                        </div>

                        <div className="rs-outfit-body">
                          {/* Score Bars */}
                          <div className="rs-score-bars">
                            {['style', 'occasion', 'budget', 'weather', 'wardrobe'].map((metric) => {
                              const val = group.breakdown?.[metric] || 85;
                              return (
                                <div key={metric} className="rs-score-row">
                                  <span className="rs-score-label">{metric.charAt(0).toUpperCase() + metric.slice(1)}</span>
                                  <div className="rs-score-bar-bg">
                                    <div className="rs-score-bar-fill" style={{ width: `${val}%` }} />
                                  </div>
                                  <span className="rs-score-val">{val}</span>
                                </div>
                              );
                            })}
                          </div>

                          {/* Product Thumbnails */}
                          <div className={`rs-outfit-thumbs ${isStretch ? 'stretch-grid' : 'compact-grid'}`}>
                            {group.items.slice(0, isStretch ? 4 : 3).map((item, i) => (
                              <div key={item.id} className={`rs-thumb-wrapper ${isStretch && i === 0 ? 'large-thumb' : ''}`}>
                                <ProductCard product={item} variant="thumbnail" />
                                <div className="rs-thumb-tag">MYNTRA IDENTITY CATALOGUE</div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Footer: Checklist + Cart */}
                        <div className="rs-outfit-footer-new">
                          <div className="rs-outfit-reasons">
                            {group.why && group.why.length > 0 ? (
                              group.why.map((line, i) => (
                                <div key={i} className="rs-reason-line"><span className="rs-check">✓</span> {line}</div>
                              ))
                            ) : (
                              <>
                                <div className="rs-reason-line"><span className="rs-check">✓</span> Built for a {results.parsed_intent?.occasion?.replace('_', ' ') || 'special event'} occasion.</div>
                                <div className="rs-reason-line"><span className="rs-check">✓</span> ₹{group.total?.toLocaleString('en-IN')} — within your ₹{results.budget_limit?.toLocaleString('en-IN')} budget.</div>
                                <div className="rs-reason-line"><span className="rs-check">✓</span> Strong aesthetic coherence across all pieces.</div>
                                {isStretch && (
                                  <div className="rs-reason-line"><span className="rs-check">✓</span> Pushes the style boundary while respecting your budget.</div>
                                )}
                              </>
                            )}
                          </div>
                          
                          <div className="rs-outfit-checkout-row sticky-action-bar">
                            <div className="rs-outfit-total">
                              ₹{group.total?.toLocaleString('en-IN')} <span className="rs-total-sub">• within budget</span>
                            </div>
                            <button className="rs-outfit-cart-btn" onClick={() => handleAddOutfitToCart(group)}>
                              <span className="rs-cart-icon">🛍</span> Add All to Cart
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {toast && <div className="toast">{toast}</div>}
      <BottomNav />
    </div>
  );
}

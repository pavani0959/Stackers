import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { apiRequest } from '../../api/client';
import { useReducedMotion } from '../../hooks/useReducedMotion';
import { gsap } from '../../motion/gsap';
import BottomNav from '../../components/BottomNav/BottomNav';
import '../../styles/ReverseShopping.css';
import {
  ArrowLeft,
  Mic,
  Sparkles,
} from 'lucide-react';

const QUICK_PROMPTS = [
  { label: '💼 Interview', text: 'College interview tomorrow, smart casual, ₹6000' },
  { label: '🎉 College Fest', text: 'College fest Saturday, retro theme, ₹4500' },
  { label: '💕 First Date', text: 'First date at a cafe, casual but cute, ₹4500' },
  { label: '🌙 Night Out', text: 'Night out with friends, sleek elegant look, ₹4500' },
  { label: '🎓 Campus', text: 'Casual campus day, comfortable and clean, ₹3000' },
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
            <span className="img-fallback-icon">👕</span>
            <span className="img-fallback-text">{item.name}</span>
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

  const outfitGroups = results?.outfits || [];

  return (
    <div className="screen rs-screen">
      <div className="rs-hdr">
        <div className="rs-back-row">
          <button
            type="button"
            className="back-btn"
            onClick={() => navigate(-1)}
            aria-label="Go back"
          >
            <ArrowLeft
              aria-hidden="true"
              size={21}
            />
          </button>
          <div>
            <div className="rs-title">🔮 Reverse Shopping</div>
            <div className="rs-sub">Tell us your occasion. We build your outfit.</div>
          </div>
        </div>
      </div>

      <div className="rs-body">
        <div className="rs-input-card">
          <div className="rs-input-lbl">Describe your occasion, vibe, or event</div>
          <div className="rs-input-wrapper">
            <textarea
              className="rs-textarea"
              rows={3}
              placeholder="e.g. College fest Saturday, retro theme, budget ₹1500…"
              value={input}
              onChange={(event) => setInput(event.target.value)}
            />
            <button
              type="button"
              className={`rs-mic-btn-new ${isListening ? 'listening' : ''}`}
              onClick={handleMicClick}
              aria-label={
                isListening
                  ? 'Stop voice input'
                  : 'Use voice input'
              }
              aria-pressed={isListening}
              title={
                isListening
                  ? 'Stop listening'
                  : 'Tap to speak your occasion'
              }
            >
              <Mic
                aria-hidden="true"
                size={20}
              />
            </button>
          </div>

          {isListening && (
            <div className="rs-mic-status">
              <span className="rs-mic-dot" />
              Listening… speak your occasion clearly
            </div>
          )}

          {micError && <div className="rs-mic-error">⚠️ {micError}</div>}

          <div className="rs-chips">
            {QUICK_PROMPTS.map((prompt) => (
              <button
                type="button"
                key={prompt.label}
                className={`rs-chip ${input === prompt.text ? 'active' : ''}`}
                aria-pressed={input === prompt.text}
                onClick={() => setInput(prompt.text)}
              >
                {prompt.label}
              </button>
            ))}
          </div>
        </div>

        <button
          type="button"
          id="rs-gen-btn"
          className="rs-gen-btn"
          onClick={handleGenerate}
          disabled={loading}

          aria-label="Generate outfits"
        >
          {!loading && (
            <Sparkles
              aria-hidden="true"
              size={20}
            />
          )}

          <span>
            {loading
              ? 'Building Your Outfits…'
              : results
                ? 'Generate Again'
                : 'Generate My Outfits'}
          </span>
        </button>

        {loading && (
          <div className="rs-loading-wrap">
            <div className="rs-spinner">🧬</div>
            <div className="rs-loading-title">Building your outfits…</div>
            <div className="rs-loading-sub">
              NLP matching · DNA filtering · Full-outfit budget check · {user.identityName || 'Your Style'}
            </div>
          </div>
        )}

        {results && (
          <div className="rs-results" ref={resultsRef}>
            <div className={`rs-budget-message ${results.within_budget ? 'success' : 'warning'}`}>
              <div className="rs-budget-title">
                {results.within_budget ? '✅ Budget validated' : '⚠️ No complete outfit in budget'}
              </div>
              <div>{results.message}</div>
              <div className="rs-budget-meta">
                Budget source: {results.budget_source === 'prompt' ? 'your prompt' : 'your profile'} ·
                Limit ₹{results.budget_limit.toLocaleString('en-IN')}
              </div>
            </div>

            {results.parsed_intent && (
              <div className="rs-intent-chips">
                {results.parsed_intent.occasion && (
                  <span className="rs-intent-chip">🎭 {results.parsed_intent.occasion.replace('_', ' ')}</span>
                )}
                {results.parsed_intent.budget_total && (
                  <span className="rs-intent-chip">💰 ₹{results.parsed_intent.budget_total}</span>
                )}
                {results.parsed_intent.theme?.map((t) => (
                  <span key={t} className="rs-intent-chip">✨ {t}</span>
                ))}
              </div>
            )}


            {outfitGroups.length > 0 && (
              <>
                <div className="rs-results-hdr">
                  <h3>{outfitGroups.length} Complete Outfits</h3>
                  <p>Budget enforced · DNA matched · {results.reused_items ? 'Minimal item reuse' : 'All unique products'}</p>
                </div>

                {outfitGroups.map((group) => (
                  <div key={group.index} className="outfit-card">
                    {/* Header: label badge + overall score */}
                    <div className="outfit-hdr">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className="outfit-label-badge">{group.label || group.title}</span>
                        <span className="outfit-title-sm">Outfit {group.index}</span>
                      </div>
                      <div className="outfit-score">🎯 {group.score}%</div>
                    </div>

                    {/* Score breakdown */}
                    {group.breakdown && Object.keys(group.breakdown).length > 0 && (
                      <div className="outfit-breakdown">
                        {Object.entries(group.breakdown).map(([key, val]) => (
                          <div key={key} className="breakdown-row">
                            <span className="breakdown-label">{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                            <div className="breakdown-bar-wrap">
                              <div className="breakdown-bar" style={{ width: `${val}%` }} />
                            </div>
                            <span className="breakdown-val">{val}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Product items */}
                    <div className="outfit-items">
                      {group.items.map((item) => (
                        <OutfitItem 
                          key={item.id} 
                          item={item} 
                          onClick={() => navigate(`/product/${item.id}`)} 
                        />
                      ))}
                    </div>

                    {/* Why lines */}
                    {group.why && group.why.length > 0 && (
                      <div className="outfit-why">
                        {group.why.map((line, i) => (
                          <div key={i} className="outfit-why-line">✓ {line}</div>
                        ))}
                      </div>
                    )}

                    {/* Footer: total + cart button */}
                    <div className="outfit-footer">
                      <div className="outfit-total">
                        ₹{group.total.toLocaleString('en-IN')} <span>· within budget</span>
                      </div>
                      <button
                        type="button"
                        className="outfit-buy"
                        onClick={() => handleAddOutfitToCart(group)}
                      >
                        Add All to Cart
                      </button>
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>
        )}
      </div>

      {toast && <div className="toast">{toast}</div>}
      <BottomNav />
    </div>
  );
}

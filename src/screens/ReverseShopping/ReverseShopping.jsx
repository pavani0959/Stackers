import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import BottomNav from '../../components/BottomNav/BottomNav';
import '../../styles/ReverseShopping.css';

const QUICK_PROMPTS = [
  { label: '💼 Interview', text: 'College interview tomorrow, smart casual, ₹6000' },
  { label: '🎉 College Fest', text: 'College fest Saturday, retro theme, ₹4500' },
  { label: '💕 First Date', text: 'First date at a cafe, casual but cute, ₹4500' },
  { label: '🌙 Night Out', text: 'Night out with friends, sleek elegant look, ₹4500' },
  { label: '🎓 Campus', text: 'Casual campus day, comfortable and clean, ₹3000' },
];

export default function ReverseShopping() {
  const navigate = useNavigate();
  const { user, buyItem } = useUser();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [toast, setToast] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [micError, setMicError] = useState('');

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
      const response = await fetch('http://localhost:8000/api/recommend/reverse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: input, user_profile: user }),
      });

      if (!response.ok) {
        throw new Error(`Reverse Shopping failed with HTTP ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error(error);
      showToast('❌ Could not connect to backend');
    } finally {
      setLoading(false);
    }
  };

  const outfitGroups = results?.outfits || [];

  return (
    <div className="screen rs-screen">
      <div className="rs-hdr">
        <div className="rs-back-row">
          <div className="back-btn" onClick={() => navigate(-1)}>←</div>
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
              className={`rs-mic-btn-new ${isListening ? 'listening' : ''}`}
              onClick={handleMicClick}
              title="Tap to speak your occasion"
              type="button"
            >
              {isListening ? '🔴' : '🎤'}
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
              <div
                key={prompt.label}
                className={`rs-chip ${input === prompt.text ? 'active' : ''}`}
                onClick={() => setInput(prompt.text)}
              >
                {prompt.label}
              </div>
            ))}
          </div>
        </div>

        <button
          id="rs-gen-btn"
          className="rs-gen-btn"
          onClick={handleGenerate}
          disabled={loading}
        >
          {loading ? '⏳ Building Your Outfits…' : results ? '✨ Generate Again' : '✨ Generate My Outfits'}
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
          <div className="rs-results">
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

            {outfitGroups.length > 0 && (
              <>
                <div className="rs-results-hdr">
                  <h3>{outfitGroups.length} Outfits Built For You</h3>
                  <p>
                    Prompt matched · Filtered by your DNA · {results.reused_items ? 'Minimal item reuse' : 'No repeated items'}
                  </p>
                </div>

                {outfitGroups.map((group) => (
                  <div key={group.index} className="outfit-card">
                    <div className="outfit-hdr">
                      <div className="outfit-title">Outfit {group.index} — {group.title}</div>
                      <div className="outfit-score">🎯 {group.score}%</div>
                    </div>

                    <div className="outfit-items">
                      {group.items.map((item) => (
                        <div
                          key={item.id}
                          className="outfit-item"
                          onClick={() => navigate(`/product/${item.id}`)}
                        >
                          <img src={item.image} alt={item.name} loading="lazy" />
                          <div className="outfit-item-lbl">
                            {item.category.toUpperCase()}<br />
                            ₹{item.price.toLocaleString('en-IN')}
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="outfit-footer">
                      <div className="outfit-total">
                        ₹{group.total.toLocaleString('en-IN')} <span>· within budget</span>
                      </div>
                      <button
                        className="outfit-buy"
                        onClick={() => {
                          group.items.forEach((item) => buyItem(item, item.confidence?.overall || 85));
                          showToast(`Outfit ${group.index} added to Fashion Memory! 🛍️`);
                        }}
                      >
                        Buy All
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

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import BottomNav from '../../components/BottomNav/BottomNav';
import '../../styles/ReverseShopping.css';

const QUICK_PROMPTS = [
  { label: '💼 Interview', text: 'College interview tomorrow, smart casual, ₹2000' },
  { label: '🎉 College Fest', text: 'College fest Saturday, retro theme, ₹1500' },
  { label: '💕 First Date', text: 'First date at a cafe, casual but cute, ₹1800' },
  { label: '🌙 Night Out', text: 'Night out with friends, bold look, ₹2500' },
  { label: '🎓 Campus', text: 'Casual campus day, comfortable and clean' },
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

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000); };

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

    recognition.onerror = (e) => {
      setIsListening(false);
      if (e.error === 'not-allowed') {
        setMicError('Microphone blocked. Click the 🔒 icon in your browser address bar and allow microphone.');
        showToast('❌ Mic blocked — allow access in browser');
      } else if (e.error === 'no-speech') {
        setMicError('No speech detected. Tap the mic and speak clearly.');
        showToast('🎤 No speech detected, try again');
      } else {
        setMicError(`Error: ${e.error}. Try again.`);
      }
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      showToast(`✅ Heard: "${transcript}"`);
      setTimeout(() => document.getElementById('rs-gen-btn')?.click(), 600);
    };

    try {
      recognition.start();
    } catch (err) {
      setMicError('Could not start microphone. Try refreshing the page.');
    }
  };

  const handleGenerate = () => {
    if (!input.trim()) { showToast('Please describe your occasion first'); return; }
    setLoading(true);
    setResults(null);

    fetch('http://localhost:8000/api/recommend/reverse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: input, user_profile: user })
    })
    .then(res => res.json())
    .then(data => {
      setResults(data);
      setLoading(false);
    })
    .catch(err => {
      console.error(err);
      showToast('❌ Could not connect to backend');
      setLoading(false);
    });
  };

  // Group results by outfit_index (1, 2, 3)
  const getOutfitGroups = () => {
    if (!results) return [];
    const groups = {};
    results.forEach(item => {
      const idx = item.outfit_index || 1;
      if (!groups[idx]) groups[idx] = [];
      groups[idx].push(item);
    });
    return Object.entries(groups).map(([idx, items]) => ({
      index: Number(idx),
      items,
      score: items[0]?.outfit_score || Math.round(items.reduce((a, b) => a + (b.confidence?.overall || 0), 0) / items.length),
      total: items.reduce((a, b) => a + b.price, 0),
    }));
  };

  const outfitGroups = getOutfitGroups();
  const outfitNames = ['Optimal Match', 'Alternative Fit', 'Bold Choice'];

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
              onChange={e => setInput(e.target.value)}
            />
            <button
              className={`rs-mic-btn-new ${isListening ? 'listening' : ''}`}
              onClick={handleMicClick}
              title="Tap to speak your occasion"
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

          {micError && (
            <div className="rs-mic-error">⚠️ {micError}</div>
          )}

          <div className="rs-chips">
            {QUICK_PROMPTS.map(p => (
              <div
                key={p.label}
                className={`rs-chip ${input === p.text ? 'active' : ''}`}
                onClick={() => setInput(p.text)}
              >
                {p.label}
              </div>
            ))}
          </div>
        </div>

        <button id="rs-gen-btn" className="rs-gen-btn" onClick={handleGenerate} disabled={loading}>
          {loading ? '⏳ Building Your Outfits…' : results ? '✨ Generate Again' : '✨ Generate My Outfits'}
        </button>

        {loading && (
          <div className="rs-loading-wrap">
            <div className="rs-spinner">🧬</div>
            <div className="rs-loading-title">Building your outfits…</div>
            <div className="rs-loading-sub">NLP matching · DNA filtering · Budget check · {user.identityName || 'Your Style'}</div>
          </div>
        )}

        {results && outfitGroups.length > 0 && (
          <div className="rs-results">
            <div className="rs-results-hdr">
              <h3>{outfitGroups.length} Outfits Built For You</h3>
              <p>NLP matched · Filtered by your DNA · {user.identityName || 'Minimalist'}</p>
            </div>

            {outfitGroups.map((group) => (
              <div key={group.index} className="outfit-card">
                <div className="outfit-hdr">
                  <div className="outfit-title">Outfit {group.index} — {outfitNames[group.index - 1] || 'Match'}</div>
                  <div className="outfit-score">🎯 {group.score}%</div>
                </div>

                <div className="outfit-items">
                  {group.items.map((item) => (
                    <div key={item.id} className="outfit-item" onClick={() => navigate(`/product/${item.id}`)}>
                      <img src={item.image} alt={item.name} loading="lazy" />
                      <div className="outfit-item-lbl">
                        {item.category?.toUpperCase() || 'ITEM'}<br />
                        ₹{item.price.toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="outfit-footer">
                  <div className="outfit-total">
                    ₹{group.total.toLocaleString()} <span>· NLP matched</span>
                  </div>
                  <button className="outfit-buy" onClick={() => {
                    group.items.forEach(item => buyItem(item, item.confidence?.overall || 85));
                    showToast(`Outfit ${group.index} added to Fashion Memory! 🛍️`);
                  }}>
                    Buy All
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {toast && <div className="toast">{toast}</div>}
      <BottomNav />
    </div>
  );
}

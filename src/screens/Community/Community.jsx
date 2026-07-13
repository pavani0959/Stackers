import { useState, useEffect } from 'react';
import { useUser } from '../../context/useUser';
import BottomNav from '../../components/BottomNav/BottomNav';
import { apiRequest } from '../../api/client';
import '../../styles/Community.css';

export default function Community() {
  const { user, updateUser } = useUser();
  const [twins, setTwins] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [blendingCreator, setBlendingCreator] = useState(null);
  const [blendValue, setBlendValue] = useState(20);
  const [toast, setToast] = useState('');

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 2500); };

  useEffect(() => {
    apiRequest('/api/community/twins', {
      method: 'POST',
      body: JSON.stringify({ user_profile: user })
    })
    .then(data => {
      setTwins(data);
      setLoading(false);
    })
    .catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, [user]);

  const handleBlend = () => {
    if (!blendingCreator) return;
    
    apiRequest('/api/dna/blend', {
      method: 'POST',
      body: JSON.stringify({ 
        user_profile: user,
        creator_dna: blendingCreator.dna,
        blend_percentage: blendValue
      })
    })
    .then(data => {
      updateUser({ dna: data.merged_dna });
      showToast(`Merged ${blendValue}% of ${blendingCreator.name}'s vibe into your DNA! 🧬`);
      setBlendingCreator(null);
    })
    .catch(err => console.error(err));
  };

  const creators = twins.filter(t => t.role === 'creator');
  const pureTwins = twins.filter(t => t.role === 'user');

  return (
    <div className="screen com-screen">
      <div className="com-hdr">
        <div className="com-title">🌐 The Tribe</div>
        <div className="com-sub">Find your twins, steal their vibe.</div>
      </div>

      <div className="com-body">
        {loading ? (
          <div style={{padding: 40, textAlign: 'center'}}>Syncing with community...</div>
        ) : (
          <>
            {/* Creators Section */}
            <div className="com-section">
              <div className="com-sec-title">Steal Their Vibe <span className="new-badge">NEW</span></div>
              <p className="com-sec-sub">Merge a creator's Fashion DNA with yours.</p>
              
              <div className="creator-list">
                {creators.map(c => (
                  <div key={c.id} className="creator-card">
                    <img src={c.avatar} alt={c.name} className="creator-img" />
                    <div className="creator-info">
                      <div className="creator-name">{c.name} {c.match_percentage > 80 && '🔥'}</div>
                      <div className="creator-handle">{c.handle}</div>
                      <div className="creator-dna">{c.dna_label}</div>
                    </div>
                    <button className="blend-btn" onClick={() => setBlendingCreator(c)}>Blend DNA</button>
                  </div>
                ))}
              </div>
            </div>

            {/* Twins Section */}
            <div className="com-section">
              <div className="com-sec-title">Wardrobe Twins</div>
              <p className="com-sec-sub">Users with a &gt;90% match to your exact aesthetic.</p>
              
              <div className="twin-list">
                {pureTwins.length > 0 ? pureTwins.map(t => (
                  <div key={t.id} className="twin-card">
                    <div className="twin-top">
                      <img src={t.avatar} alt={t.name} className="twin-img" />
                      <div>
                        <div className="twin-name">{t.name}</div>
                        <div className="twin-match">🧬 {t.match_percentage}% DNA Match</div>
                      </div>
                    </div>
                    <div className="twin-msg">"Recently bought {t.recent_purchases.length} items you might like."</div>
                  </div>
                )) : (
                  <div className="no-twins">No 90%+ twins found yet. Keep shopping to refine your DNA!</div>
                )}
              </div>
            </div>
          </>
        )}
      </div>

      {/* Blend Modal */}
      {blendingCreator && (
        <div className="blend-modal-overlay">
          <div className="blend-modal">
            <div className="bm-close" onClick={() => setBlendingCreator(null)}>×</div>
            <img src={blendingCreator.avatar} className="bm-avatar" alt=""/>
            <h3 className="bm-title">Steal {blendingCreator.name}'s Vibe</h3>
            <p className="bm-sub">How much of their <strong>{blendingCreator.dna_label}</strong> DNA do you want to merge into yours?</p>
            
            <div className="bm-slider-wrap">
              <input 
                type="range" 
                min="10" max="100" step="10" 
                value={blendValue} 
                onChange={(e) => setBlendValue(Number(e.target.value))}
                className="bm-slider" 
              />
              <div className="bm-val">{blendValue}%</div>
            </div>
            
            <button className="bm-confirm" onClick={handleBlend}>Confirm Identity Shift</button>
          </div>
        </div>
      )}

      {toast && <div className="toast">{toast}</div>}
      <BottomNav />
    </div>
  );
}

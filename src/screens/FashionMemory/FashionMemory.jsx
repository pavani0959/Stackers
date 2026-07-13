import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import BottomNav from '../../components/BottomNav/BottomNav';
import '../../styles/FashionMemory.css';

export default function FashionMemory() {
  const navigate = useNavigate();
  const { user } = useUser();
  const memory = user.purchaseMemory || [];

  return (
    <div className="screen fm-screen">
      <div className="fm-hdr">
        <div className="fm-back-row">
          <div className="back-btn" onClick={() => navigate('/home')}>←</div>
          <div>
            <div className="fm-title">📖 Fashion Memory</div>
            <div className="fm-sub">Everything you've bought — and why.</div>
          </div>
        </div>
      </div>

      <div className="fm-body">
        {/* DNA Evolution */}
        <div className="dna-shift">
          <div className="dna-shift-title">📊 Your DNA Is Evolving</div>
          <div className="shift-row">
            <div className="shift-name">{user.identityName?.split(' ')[1] || 'Minimalist'}</div>
            <div className="shift-delta">+4% this month ↑</div>
          </div>
          <div className="shift-row">
            <div className="shift-name">Streetwear</div>
            <div className="shift-delta shift-down">−2% this month ↓</div>
          </div>
          <div className="shift-note">Your purchases are making your style more consistent. Confidence: 87% → {user.profileConfidence ?? 0}%</div>
        </div>

        {/* AI Regret Prevention */}
        <div className="regret-card">
          <div className="regret-title">🛡️ AI Regret Prevention <span className="new-badge">NEW</span></div>
          <div className="regret-body">Before you bought those bold cargo pants last week, our AI flagged a 58% DNA match warning. You bought it anyway — and returned it 3 days later.</div>
          <div className="regret-stat">Potential regret saved this month: ₹2,490</div>
        </div>

        <div className="month-label">Your Purchases</div>

        {memory.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-2)', fontSize: 13 }}>
            You haven't bought anything yet.<br/><br/>
            Go to the Home feed or Reverse Shopping to find items that match your DNA.
          </div>
        ) : (
          memory.map((item, idx) => (
            <div key={idx} className="mem-item" onClick={() => navigate(`/product/${item.id}`)}>
              <div className="mem-top">
                <img src={item.image} className="mem-img" alt={item.name} />
                <div className="mem-info">
                  <div className="mem-date">{item.date}</div>
                  <div className="mem-name">{item.name}</div>
                  <div className="mem-price">₹{item.price?.toLocaleString('en-IN')}</div>
                  <div className="mem-occ">📅 {item.occasion}</div>
                </div>
              </div>
              <div className="mem-bottom">
                <div className="mem-reason">"{item.reason || 'Added because it matched your vibe perfectly.'}"</div>
                <div className={`mem-dna ${item.dnaMatch >= 80 ? 'good' : 'warn'}`}>
                  {item.dnaMatch >= 80 ? '🧬' : '⚠️'} {item.dnaMatch}% DNA Match · {item.dnaMatch >= 80 ? 'Great purchase' : 'Low fit'}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <BottomNav />
    </div>
  );
}

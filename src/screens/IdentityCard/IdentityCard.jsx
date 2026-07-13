import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import '../../styles/IdentityCard.css';

export default function IdentityCard() {
  const navigate = useNavigate();
  const { user } = useUser();
  const bars = user.dnaTopBars || [];
  const name = user.name?.trim() || 'Style Explorer';

  const share = () => {
    const text = `My Myntra Identity: ${user.identityName}\n${bars.map(b => `${b.label}: ${b.percentage}%`).join(' | ')}\nStyle Confidence: ${user.confidenceScore}%`;
    if (navigator.share) { navigator.share({ title: 'My Fashion DNA', text }); }
    else { navigator.clipboard.writeText(text); }
  };

  return (
    <div className="screen id-card-screen">
      <p className="id-card-lbl">✦ Your Aesthetic Passport <span className="new-badge">NEW</span></p>

      <div className="id-card">
        <div className="card-glow1" />
        <div className="card-glow2" />
        <div className="card-top">
          <span className="card-brand">MYNTRA IDENTITY</span>
          <div className="card-logo-icon">🧬</div>
        </div>
        <div className="card-name">{name}</div>
        <div className="card-sub">Style Member · Since July 2025</div>
        <div className="card-tags">
          {bars.slice(0,3).map((b,i) => (
            <span key={b.tag} className={`card-tag ct-${['pink','purple','blue'][i]}`}>{b.label} {b.percentage}%</span>
          ))}
          <span className="card-tag ct-pink">{user.budget?.replace(/-/g,' ') || 'Campus Casual'}</span>
          {user.occasions?.slice(0,2).map(o => (
            <span key={o} className="card-tag ct-purple">{o}</span>
          ))}
        </div>
        <div className="card-conf">
          <div>
            <div className="cc-label">Style Confidence</div>
            <div className="card-conf-bar"><div className="card-conf-fill" style={{ width: `${user.confidenceScore || 87}%` }} /></div>
          </div>
          <div className="card-conf-val grad-text">{user.confidenceScore || 87}%</div>
        </div>
      </div>

      <button className="id-share-btn" onClick={share}>📤 Share My Aesthetic Passport</button>
      <button className="id-enter-btn" onClick={() => navigate('/home')}>Enter My Myntra →</button>
    </div>
  );
}

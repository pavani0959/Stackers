import { useNavigate } from 'react-router-dom';
import '../../styles/Splash.css';

export default function Splash() {
  const navigate = useNavigate();
  return (
    <div className="screen splash-screen">
      <div className="splash-orb1" />
      <div className="splash-orb2" />
      <div className="splash-content">
        <div className="splash-icon">🧬</div>
        <h1 className="splash-logo">Myntra <span className="grad-text">Identity</span></h1>
        <p className="splash-tag">Fashion that knows who you are.</p>
        <button className="splash-btn" onClick={() => navigate('/onboard/gender')}>
          Begin Your Journey →
        </button>
      </div>
    </div>
  );
}

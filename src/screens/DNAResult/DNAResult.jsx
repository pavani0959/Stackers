import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import '../../styles/DNAResult.css';

const BAR_COLORS = [
  'linear-gradient(90deg,#FF3CAC,#784BA0)',
  'linear-gradient(90deg,#784BA0,#2B86C5)',
  'linear-gradient(90deg,#2B86C5,#06B6D4)',
  'linear-gradient(90deg,#555,#9090B0)',
];

function formatDnaLabel(value) {
  return value
    .replace(/[_-]/g, ' ')
    .replace(/\b\w/g, (character) =>
      character.toUpperCase(),
    );
}

function buildDnaBars(user) {
  if (user.dnaTopBars?.length) {
    return user.dnaTopBars;
  }

  return Object.entries(user.dna ?? {})
    .sort(
      ([, firstValue], [, secondValue]) =>
        secondValue - firstValue,
    )
    .slice(0, 4)
    .map(([tag, percentage]) => ({
      tag,
      label: formatDnaLabel(tag),
      percentage: Math.round(percentage),
    }));
}

export default function DNAResult() {
  const navigate = useNavigate();
  const { user } = useUser();
  const bars = buildDnaBars(user);
  const identity = {
    name: user.identityName,
    desc:
      user.identityDesc ||
      'A style identity shaped by your preferences and Fashion DNA.',
  };

  return (
    <div className="screen dna-result-screen">
      <div className="dna-res-hdr">
        <p>YOUR FASHION DNA</p>
        <h1>We figured you out. 🧬</h1>
      </div>

      <div className="dna-bars">
        {bars.map((bar, i) => (
          <div key={bar.tag} className="bar-row" style={{ animationDelay: `${i * 0.15}s` }}>
            <div className="bar-info">
              <span className="bar-name">{bar.label}</span>
              <span className="bar-pct" style={{ color: i === 0 ? '#FF3CAC' : i === 1 ? '#784BA0' : '#2B86C5' }}>
                {bar.percentage}%
              </span>
            </div>
            <div className="bar-track">
              <div
                className="bar-fill"
                style={{ '--target-w': `${bar.percentage}%`, background: BAR_COLORS[i] || BAR_COLORS[0] }}
              />
            </div>
          </div>
        ))}
      </div>

      {identity.name && (
        <div className="identity-box">
          <p className="ib-label">Your Style Identity</p>
          <h2 className="ib-title grad-text">{identity.name}</h2>
          <p className="ib-desc">{identity.desc}</p>
        </div>
      )}

      <button className="btn-primary" onClick={() => navigate('/identity-card')}>
        See My Identity Card →
      </button>
    </div>
  );
}

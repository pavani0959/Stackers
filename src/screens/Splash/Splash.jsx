import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import '../../styles/Splash.css';

/* ── tiny 4-point sparkle SVG ────────────────────────── */
function Sparkle({ size = 16, color = 'var(--gradient-hero-start)', className = '' }) {
  return (
    <svg
      className={`splash-sparkle ${className}`}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={color}
      aria-hidden="true"
    >
      <path d="M12 0 L14 10 L24 12 L14 14 L12 24 L10 14 L0 12 L10 10 Z" />
    </svg>
  );
}

export default function Splash() {
  const navigate = useNavigate();

  return (
    <div className="screen splash-screen">
      {/* ── decorative curved lines (top-right corner) ──── */}
      <svg className="splash-deco-lines splash-deco-tr" viewBox="0 0 200 200" fill="none" aria-hidden="true">
        <path d="M40,0 Q200,30 200,180" stroke="var(--color-primary-soft)" strokeWidth="1" opacity="0.35" />
        <path d="M80,0 Q210,60 195,200" stroke="var(--color-lavender)" strokeWidth="1" opacity="0.3" />
      </svg>

      {/* ── decorative curved lines (bottom-left corner) ── */}
      <svg className="splash-deco-lines splash-deco-bl" viewBox="0 0 200 200" fill="none" aria-hidden="true">
        <path d="M0,40 Q30,200 180,200" stroke="var(--color-primary-soft)" strokeWidth="1" opacity="0.35" />
        <path d="M0,80 Q60,210 200,195" stroke="var(--color-lavender)" strokeWidth="1" opacity="0.3" />
      </svg>

      {/* ── sparkle clusters ──────────────────────────────── */}
      <Sparkle size={14} color="var(--gradient-hero-start)" className="sparkle-1" />
      <Sparkle size={10} color="var(--color-lavender)"       className="sparkle-2" />
      <Sparkle size={18} color="var(--gradient-hero-end)"    className="sparkle-3" />
      <Sparkle size={12} color="var(--gradient-hero-start)"  className="sparkle-4" />
      <Sparkle size={16} color="var(--color-lavender)"       className="sparkle-5" />
      <Sparkle size={10} color="var(--gradient-hero-end)"    className="sparkle-6" />
      <Sparkle size={14} color="var(--gradient-hero-start)"  className="sparkle-7" />

      {/* ── soft lavender blob bottom-left ─────────────── */}
      <div className="splash-blob" aria-hidden="true" />

      {/* ── main centred content ──────────────────────── */}
      <div className="splash-content">
        {/* App icon */}
        <div className="splash-icon" aria-hidden="true">
          {/* DNA double-helix glyph */}
          <svg width="54" height="54" viewBox="0 0 64 64" fill="none" aria-hidden="true">
            <g stroke="white" strokeWidth="3" strokeLinecap="round">
              {/* Left strand */}
              <path d="M16,10 C16,22 28,28 28,40 C28,52 16,58 16,58" />
              {/* Right strand */}
              <path d="M48,10 C48,22 36,28 36,40 C36,52 48,58 48,58" />
              {/* Rungs */}
              <line x1="20" y1="18" x2="44" y2="18" opacity="0.7" />
              <line x1="24" y1="28" x2="40" y2="28" opacity="0.7" />
              <line x1="24" y1="38" x2="40" y2="38" opacity="0.7" />
              <line x1="20" y1="48" x2="44" y2="48" opacity="0.7" />
            </g>
          </svg>
        </div>

        {/* Wordmark */}
        <h1 className="splash-logo">
          Myntra <span className="splash-logo-accent">Identity</span>
        </h1>

        {/* Tagline */}
        <p className="splash-tag">Fashion that knows who you are.</p>

        {/* CTA */}
        <button
          className="splash-btn"
          onClick={() => navigate('/onboard/gender')}
        >
          <span>Begin Your Journey</span>
          <ArrowRight size={20} aria-hidden="true" />
        </button>
      </div>
    </div>
  );
}

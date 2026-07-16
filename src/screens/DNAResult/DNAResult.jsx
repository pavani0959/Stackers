import { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { useReducedMotion } from '../../hooks/useReducedMotion';
import { gsap, useGSAP } from '../../motion/gsap';
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
  const reducedMotion = useReducedMotion();
  const root = useRef(null);
  const bars = buildDnaBars(user);
  const identity = {
    name: user.identityName,
    desc:
      user.identityDesc ||
      'A style identity shaped by your preferences and Fashion DNA.',
  };

  useGSAP(
    () => {
      if (reducedMotion) return;

      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

      // Header fades up
      tl.from('[data-dna-hdr]', { y: 28, opacity: 0, duration: 0.55 });

      // Each bar row staggers in from below
      tl.from(
        '[data-bar-row]',
        { y: 20, opacity: 0, duration: 0.4, stagger: 0.12 },
        '-=0.2',
      );

      // Bar fills animate from scaleX:0 to target width
      tl.from(
        '[data-bar-fill]',
        {
          scaleX: 0,
          transformOrigin: 'left center',
          duration: 0.9,
          stagger: 0.12,
          ease: 'power2.out',
        },
        '-=0.6',
      );

      // Percentage counters count up
      bars.forEach((bar, i) => {
        const el = document.querySelector(`[data-bar-pct="${bar.tag}"]`);
        if (!el) return;
        const obj = { val: 0 };
        gsap.to(obj, {
          val: bar.percentage,
          duration: 1.0,
          delay: 0.3 + i * 0.12,
          ease: 'power2.out',
          onUpdate: () => {
            el.textContent = `${Math.round(obj.val)}%`;
          },
        });
      });

      // Identity card entrance
      tl.from(
        '[data-identity-box]',
        { y: 24, opacity: 0, duration: 0.5 },
        '-=0.4',
      );

      // CTA button
      tl.from(
        '[data-dna-cta]',
        { y: 16, opacity: 0, duration: 0.4 },
        '-=0.2',
      );
    },
    { scope: root, dependencies: [reducedMotion] },
  );

  return (
    <div className="screen dna-result-screen" ref={root}>
      <div className="dna-res-hdr" data-dna-hdr>
        <p>YOUR FASHION DNA</p>
        <h1>We figured you out. 🧬</h1>
      </div>

      <div className="dna-bars">
        {bars.map((bar, i) => (
          <div key={bar.tag} className="bar-row" data-bar-row>
            <div className="bar-info">
              <span className="bar-name">{bar.label}</span>
              <span
                className="bar-pct"
                data-bar-pct={bar.tag}
                style={{ color: i === 0 ? '#FF3CAC' : i === 1 ? '#784BA0' : '#2B86C5' }}
              >
                {bar.percentage}%
              </span>
            </div>
            <div className="bar-track">
              <div
                className="bar-fill"
                data-bar-fill
                style={{ '--target-w': `${bar.percentage}%`, background: BAR_COLORS[i] || BAR_COLORS[0] }}
              />
            </div>
          </div>
        ))}
      </div>

      {identity.name && (
        <div className="identity-box" data-identity-box>
          <p className="ib-label">Your Style Identity</p>
          <h2 className="ib-title grad-text">{identity.name}</h2>
          <p className="ib-desc">{identity.desc}</p>
        </div>
      )}

      <button
        className="btn-primary"
        data-dna-cta
        onClick={() => navigate('/identity-card')}
      >
        See My Identity Card →
      </button>
    </div>
  );
}

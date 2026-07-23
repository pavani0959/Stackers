import { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { useReducedMotion } from '../../hooks/useReducedMotion';
import { gsap, useGSAP } from '../../motion/gsap';
import '../../styles/DNAResult.css';

import { Sparkles, Footprints, Headphones, Shirt, Gem, Briefcase, Palette } from 'lucide-react';

const TRAIT_META = {
  'minimalist':    { name: 'Minimalist',   icon: <Sparkles size={18} />, color: '#ec4899' },
  'streetwear':    { name: 'Streetwear',   icon: <Footprints size={18} />, color: '#8b5cf6' },
  'y2k':           { name: 'Y2k',          icon: <Headphones size={18} />, color: '#3b82f6' },
  'campus-casual': { name: 'CampusCasual', icon: <Shirt size={18} />, color: '#14b8a6' },
  'campuscasual':  { name: 'CampusCasual', icon: <Shirt size={18} />, color: '#14b8a6' },
  'quiet-luxury':  { name: 'QuietLuxury',  icon: <Gem size={18} />, color: '#64748b' },
  'quietluxury':   { name: 'QuietLuxury',  icon: <Gem size={18} />, color: '#64748b' },
  'classic':       { name: 'Classic',      icon: <Briefcase size={18} />, color: '#f59e0b' },
  'default':       { name: 'Style',        icon: <Palette size={18} />, color: '#6b7280' }
};

function formatDnaLabel(value) {
  return value
    .replace(/[_-]/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function getTraitMeta(tag) {
  return TRAIT_META[tag.toLowerCase()] || { 
    ...TRAIT_META.default, 
    name: formatDnaLabel(tag) 
  };
}

function buildDnaBars(user) {
  if (user.dnaTopBars?.length) {
    return user.dnaTopBars.map(bar => ({
      ...bar,
      meta: getTraitMeta(bar.tag)
    }));
  }

  // Provide fallback data for preview if user.dna is empty
  const defaultDna = {
    'minimalist': 28,
    'streetwear': 23,
    'y2k': 21,
    'campus-casual': 15
  };
  
  const dnaData = (user.dna && Object.keys(user.dna).length > 0) ? user.dna : defaultDna;

  return Object.entries(dnaData)
    .sort(([, firstValue], [, secondValue]) => secondValue - firstValue)
    .slice(0, 4)
    .map(([tag, percentage]) => {
      const meta = getTraitMeta(tag);
      return {
        tag,
        label: meta.name,
        percentage: Math.round(percentage),
        meta
      };
    });
}

export default function DNAResult() {
  const navigate = useNavigate();
  const { user } = useUser();
  const reducedMotion = useReducedMotion();
  const root = useRef(null);
  
  const bars = buildDnaBars(user);
  
  const identityName = user.identityName || 'Minimalist Streetwear';
  const identityDesc = user.identityDesc || 'A style identity shaped by your preferences and Fashion DNA.';

  useGSAP(
    () => {
      if (reducedMotion) return;

      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

      tl.from('.dna-res-card', { y: 20, opacity: 0, duration: 0.6 });
      tl.from('[data-dna-hdr]', { y: 15, opacity: 0, duration: 0.5 }, '-=0.4');

      tl.from(
        '[data-bar-row]',
        { x: -15, opacity: 0, duration: 0.4, stagger: 0.1 },
        '-=0.2',
      );

      tl.from(
        '[data-bar-fill]',
        {
          scaleX: 0,
          transformOrigin: 'left center',
          duration: 0.9,
          stagger: 0.1,
          ease: 'power2.out',
        },
        '-=0.4',
      );

      bars.forEach((bar, i) => {
        const el = document.querySelector(`[data-bar-pct="${bar.tag}"]`);
        if (!el) return;
        const obj = { val: 0 };
        gsap.to(obj, {
          val: bar.percentage,
          duration: 1.0,
          delay: 0.4 + i * 0.1,
          ease: 'power2.out',
          onUpdate: () => {
            el.textContent = `${Math.round(obj.val)}%`;
          },
        });
      });

      tl.from(
        '[data-identity-box]',
        { y: 20, opacity: 0, duration: 0.5 },
        '-=0.4',
      );

      tl.from(
        '[data-dna-cta]',
        { y: 15, opacity: 0, duration: 0.4 },
        '-=0.3',
      );
    },
    { scope: root, dependencies: [reducedMotion] },
  );

  return (
    <div className="dna-res-shell" ref={root}>
      {/* Decorative background elements */}
      <div className="dna-res-bg-blob"></div>
      
      {/* Top Left Sparkles */}
      <div className="dna-res-sparkle top-left">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 0C12 6.62742 6.62742 12 0 12C6.62742 12 12 17.3726 12 24C12 17.3726 17.3726 12 24 12C17.3726 12 12 6.62742 12 0Z" fill="#ffb7ce"/>
        </svg>
      </div>
      <div className="dna-res-sparkle top-left-small">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 0C12 6.62742 6.62742 12 0 12C6.62742 12 12 17.3726 12 24C12 17.3726 17.3726 12 24 12C17.3726 12 12 6.62742 12 0Z" fill="#c4b5fd"/>
        </svg>
      </div>
      
      {/* Bottom Right Sparkles */}
      <div className="dna-res-sparkle bottom-right">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 0C12 6.62742 6.62742 12 0 12C6.62742 12 12 17.3726 12 24C12 17.3726 17.3726 12 24 12C17.3726 12 12 6.62742 12 0Z" fill="#c4b5fd"/>
        </svg>
      </div>
      <div className="dna-res-sparkle bottom-right-small">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 0C12 6.62742 6.62742 12 0 12C6.62742 12 12 17.3726 12 24C12 17.3726 17.3726 12 24 12C17.3726 12 12 6.62742 12 0Z" fill="#ffb7ce"/>
        </svg>
      </div>

      <div className="dna-res-wavy">
        <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
          <path d="M-20 40 C 20 40, 40 80, 80 80 C 120 80, 140 40, 180 40" stroke="#fecdd3" strokeWidth="1.5" strokeLinecap="round" fill="none" opacity="0.6"/>
          <path d="M-20 55 C 20 55, 40 95, 80 95 C 120 95, 140 55, 180 55" stroke="#fecdd3" strokeWidth="1.5" strokeLinecap="round" fill="none" opacity="0.6"/>
          <path d="M-20 70 C 20 70, 40 110, 80 110 C 120 110, 140 70, 180 70" stroke="#fecdd3" strokeWidth="1.5" strokeLinecap="round" fill="none" opacity="0.6"/>
        </svg>
      </div>

      <div className="dna-res-card">
        <div className="dna-res-hdr" data-dna-hdr>
          <p>YOUR FASHION DNA</p>
          <h1>We figured you out. 🧬<span className="hdr-sparkle">✨</span></h1>
        </div>

        <div className="dna-bars">
          {bars.map((bar) => (
            <div key={bar.tag} className="bar-row" data-bar-row style={{ '--trait-color': bar.meta.color }}>
              <div className="bar-icon-wrap" aria-hidden="true">
                {bar.meta.icon}
              </div>
              <div className="bar-content">
                <div className="bar-info">
                  <span className="bar-name">{bar.label}</span>
                  <span
                    className="bar-pct"
                    data-bar-pct={bar.tag}
                  >
                    {bar.percentage}%
                  </span>
                </div>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    data-bar-fill
                    style={{ width: `${bar.percentage}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="identity-box" data-identity-box>
          <div className="ib-content">
            <p className="ib-label">
              <span className="ib-star">✦</span> Your Style Identity
            </p>
            <h2 className="ib-title">{identityName}</h2>
            <div className="ib-divider" />
            <p className="ib-desc">{identityDesc}</p>
          </div>
          <div className="ib-illus" aria-hidden="true">
            <svg width="100" height="100" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ transform: 'rotate(5deg)' }}>
              <path d="M28 35 Q40 10 72 35 L85 65 L70 70 L65 55 L65 85 L35 85 L35 55 L30 70 L15 65 Z" fill="var(--color-bg-blush)" stroke="var(--color-primary-soft)" strokeWidth="3" strokeLinejoin="round"/>
              <path d="M38 35 C38 15 62 15 62 35" fill="none" stroke="var(--color-primary-soft)" strokeWidth="3" strokeLinecap="round"/>
              <path d="M40 85 V70 H60 V85" fill="none" stroke="var(--color-primary-soft)" strokeWidth="3" strokeLinejoin="round"/>
              <path d="M48 35 V45 M52 35 V45" fill="none" stroke="var(--color-primary-soft)" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
        </div>

        <button
          className="btn-dna-cta"
          data-dna-cta
          onClick={() => navigate('/identity-card')}
        >
          <span>SEE MY IDENTITY CARD</span>
          <span className="cta-arrow">→</span>
        </button>
      </div>
    </div>
  );
}

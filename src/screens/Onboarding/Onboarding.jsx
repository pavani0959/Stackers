import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { ArrowRight, User, CheckCircle } from 'lucide-react';
import '../../styles/Onboarding.css';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';

/* ── tiny 4-point sparkle SVG (shared across onboarding) ── */
function Sparkle({ size = 16, color = 'var(--gradient-hero-start)', className = '' }) {
  return (
    <svg
      className={`ob-sparkle ${className}`}
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

/* ── Shared onboarding shell: gradient bg + decorations ── */
function OnboardShell({ children }) {
  return (
    <div className="screen ob-shell">
      {/* Decorative wavy lines top-right */}
      <svg className="ob-deco-lines ob-deco-tr" viewBox="0 0 200 200" fill="none" aria-hidden="true">
        <path d="M40,0 Q200,30 200,180" stroke="var(--color-primary-soft)" strokeWidth="1" opacity="0.35" />
        <path d="M80,0 Q210,60 195,200" stroke="var(--color-lavender)" strokeWidth="1" opacity="0.3" />
      </svg>

      {/* Decorative wavy lines bottom-left */}
      <svg className="ob-deco-lines ob-deco-bl" viewBox="0 0 200 200" fill="none" aria-hidden="true">
        <path d="M0,40 Q30,200 180,200" stroke="var(--color-primary-soft)" strokeWidth="1" opacity="0.35" />
        <path d="M0,80 Q60,210 200,195" stroke="var(--color-lavender)" strokeWidth="1" opacity="0.3" />
      </svg>

      {/* Sparkle clusters */}
      <Sparkle size={14} color="var(--gradient-hero-start)" className="ob-sp-1" />
      <Sparkle size={10} color="var(--color-lavender)"       className="ob-sp-2" />
      <Sparkle size={18} color="var(--gradient-hero-end)"    className="ob-sp-3" />
      <Sparkle size={12} color="var(--gradient-hero-start)"  className="ob-sp-4" />
      <Sparkle size={16} color="var(--color-lavender)"       className="ob-sp-5" />
      <Sparkle size={10} color="var(--gradient-hero-end)"    className="ob-sp-6" />

      {/* Lavender blob bottom-left */}
      <div className="ob-blob" aria-hidden="true" />

      {children}
    </div>
  );
}

const BUDGET_OPTIONS = [
  {
    id: 'budget-explorer',
    label: 'Budget Explorer',
    range: 'Under ₹500',
    min: 0,
    max: 500,
  },
  {
    id: 'smart-spender',
    label: 'Smart Spender',
    range: '₹500 – ₹1,500',
    min: 500,
    max: 1500,
  },
  {
    id: 'campus-casual',
    label: 'Campus Casual',
    range: '₹1,500 – ₹3,000',
    min: 1500,
    max: 3000,
  },
  {
    id: 'style-investor',
    label: 'Style Investor',
    range: '₹3,000 – ₹7,000',
    min: 3000,
    max: 7000,
  },
  {
    id: 'luxury-seeker',
    label: 'Luxury Seeker',
    range: 'Above ₹7,000',
    min: 7000,
    max: null,
  },
];

// Step 1: Gender + Age
export function OnboardGender() {
  const navigate = useNavigate();
  const {
    user,
    updateIdentity,
  } = useUser();
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [name, setName] = useState(user.name || '');
  const [gender, setGender] = useState(user.gender || 'female');
  const [age, setAge] = useState(user.age || 21);
  const [nameError, setNameError] = useState('');

  const next = async () => {

    if (saving) {
      return;
    }

    const cleanName = name
      .trim()
      .replace(/\s+/g, ' ');

    if (cleanName.length < 2) {
      setNameError(
        'Please enter the name you want Myntra Identity to use.',
      );
      return;
    }

    setSaving(true);
    setSaveError(null);

    try {
      await updateIdentity({
        name: cleanName,
        gender,
        age,
      });

      navigate('/onboard/budget');
    } catch (error) {
      setSaveError(error);
    } finally {
      setSaving(false);
    }
  };

  /* Slider fill percentage for the CSS gradient trick */
  const sliderPercent = ((age - 13) / (35 - 13)) * 100;

  return (
    <OnboardShell>
      <div className="ob-card">
        {/* 3-segment step progress bar */}
        <div className="ob-prog-wrap">
          {[0, 1, 2].map(i => (
            <div key={i} className={`ob-bar ${i === 0 ? 'active' : ''}`} />
          ))}
        </div>

        <h1 className="ob-title">
          Before we begin,<br />let&rsquo;s understand you <span aria-hidden="true">👋</span>
        </h1>
        <p className="ob-sub">No boring jargon. Just a quick conversation.</p>

        {/* Name input */}
        <label className="ob-label" htmlFor="profile-name">What should we call you?</label>
        <div className={`ob-input-wrap ${nameError ? 'error' : ''}`}>
          <User size={18} className="ob-input-icon" aria-hidden="true" />
          <input
            id="profile-name"
            className="ob-name-input"
            type="text"
            value={name}
            maxLength={50}
            autoComplete="name"
            placeholder="Enter your name"
            onChange={(event) => {
              setName(event.target.value);
              if (nameError) setNameError('');
            }}
            onKeyDown={(event) => event.key === 'Enter' && next()}
          />
        </div>
        {nameError && <div className="ob-field-error">{nameError}</div>}

        {/* Gender cards */}
        <label className="ob-label">How do you identify?</label>
        <div className="gender-grid">
          {[
            { id: 'male',      icon: '🧑', label: 'Male' },
            { id: 'female',    icon: '👩', label: 'Female' },
            { id: 'nonbinary', icon: '🌈', label: 'Non-Binary / Prefer not to say' },
          ].map((genderOption) => {
            const isSelected = gender === genderOption.id;
            return (
              <button
                type="button"
                key={genderOption.id}
                className={`gender-card ${isSelected ? 'sel' : ''}`}
                aria-pressed={isSelected}
                onClick={() => setGender(genderOption.id)}
              >
                {isSelected && (
                  <span className="gender-check" aria-hidden="true">
                    <CheckCircle size={20} />
                  </span>
                )}
                <span className="g-icon" aria-hidden="true">{genderOption.icon}</span>
                <span className="g-label">{genderOption.label}</span>
              </button>
            );
          })}
        </div>

        {/* Age */}
        <label className="ob-label">Your age</label>
        <div className="age-num">{age}</div>
        <input
          type="range"
          className="age-slider"
          min="13"
          max="35"
          value={age}
          style={{ '--slider-fill': `${sliderPercent}%` }}
          onChange={e => setAge(Number(e.target.value))}
        />

        {saveError && (
          <ApiErrorState
            error={saveError}
            title="Could not save your identity"
            onRetry={next}
          />
        )}

        {/* CTA */}
        <button
          type="button"
          className="ob-cta"
          disabled={saving}
          onClick={next}
        >
          <span>{saving ? 'Saving…' : 'Continue'}</span>
          <ArrowRight size={20} aria-hidden="true" />
        </button>
      </div>
    </OnboardShell>
  );
}

// Step 2: Budget
export function OnboardBudget() {
  const navigate = useNavigate();
  const { user, updateUser } = useUser();

  const [budget, setBudget] = useState(
    user.budget || 'campus-casual',
  );

  /* Budget tiers with icon/color for each badge */
  const BUDGET_TIERS = [
    { ...BUDGET_OPTIONS[0], icon: '💼', badgeColor: '#dbeafe' },
    { ...BUDGET_OPTIONS[1], icon: '🐷', badgeColor: '#fce7f3' },
    { ...BUDGET_OPTIONS[2], icon: '🎓', badgeColor: '#e0e7ff' },
    { ...BUDGET_OPTIONS[3], icon: '📈', badgeColor: '#d1fae5' },
    { ...BUDGET_OPTIONS[4], icon: '💎', badgeColor: '#ede9fe' },
  ];

  const next = () => {
    const selectedBudget =
      BUDGET_OPTIONS.find(
        (option) => option.id === budget,
      ) ??
      BUDGET_OPTIONS.find(
        (option) =>
          option.id === 'campus-casual',
      );

    updateUser({
      budget: selectedBudget.id,
      budgetMin: selectedBudget.min,
      budgetMax: selectedBudget.max,
    });

    navigate('/onboard/colours');
  };

  return (
    <OnboardShell>
      <div className="ob-content">
        {/* 3-segment step progress bar — first 2 filled */}
        <div className="ob-prog-wrap">
          {[0, 1, 2].map(i => (
            <div key={i} className={`ob-bar ${i < 2 ? 'active' : ''}`} />
          ))}
        </div>

        <h1 className="ob-title">
          What&rsquo;s your outfit budget? <span aria-hidden="true">💸</span>
        </h1>

        <p className="ob-sub">
          Par outfit. Be honest — no judgment here.
        </p>

        <div className="budget-list">
          {BUDGET_TIERS.map((option) => {
            const isSelected = budget === option.id;
            return (
              <button
                key={option.id}
                type="button"
                className={`budget-row ${isSelected ? 'sel' : ''}`}
                aria-pressed={isSelected}
                onClick={() => setBudget(option.id)}
              >
                <span
                  className="budget-icon-badge"
                  style={{ background: option.badgeColor }}
                  aria-hidden="true"
                >
                  {option.icon}
                </span>
                <div className="budget-info">
                  <div className="budget-name">{option.label}</div>
                  <div className="budget-range">{option.range}</div>
                </div>
                <span className="budget-radio" aria-hidden="true">
                  {isSelected && <span className="budget-radio-dot" />}
                </span>
              </button>
            );
          })}
        </div>

        {/* CTA */}
        <button type="button" className="ob-cta" onClick={next}>
          <span>CONTINUE</span>
          <ArrowRight size={20} aria-hidden="true" />
        </button>
      </div>
    </OnboardShell>
  );
}

// Step 3: Colours
export function OnboardColours() {
  const navigate = useNavigate();
  const { user, updateUser } = useUser();
  const [selected, setSelected] = useState(user.colours || ['#F5F0E8', '#8BA7BF', '#B0B0B0']);

  const colours = ['#F5F0E8', '#1A1A1A', '#8B7355', '#C4A882', '#4A6741', '#8BA7BF', '#D4B8C0', '#E86D6D', '#5B4FCF', '#F5C842', '#2C7865', '#B0B0B0', '#FFFFFF', '#FF7043'];

  const toggle = (c) => setSelected(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]);
  const next = () => { updateUser({ colours: selected }); navigate('/onboard/occasions'); };

  return (
    <div className="screen ob-screen">
      <div className="ob-prog-wrap">
        {[0, 1, 2, 3].map(i => <div key={i} className={`ob-dot ${i < 2 ? 'done' : ''} ${i === 2 ? 'active' : ''}`} />)}
      </div>
      <h1 className="ob-title">Your colour palette 🎨</h1>
      <p className="ob-sub">Pick the colours that feel like you.</p>

      <div className="colour-grid">
        {colours.map((colour) => {
          const isSelected =
            selected.includes(colour);

          return (
            <button
              type="button"
              key={colour}
              className={`col-chip ${isSelected
                ? 'sel'
                : ''
                }`}
              style={{
                background: colour,
                borderColor:
                  colour === '#FFFFFF'
                    ? 'rgba(0, 0, 0, 0.18)'
                    : 'transparent',
              }}
              aria-label={
                `Select colour ${colour}`
              }
              aria-pressed={isSelected}
              onClick={() => {
                toggle(colour);
              }}
            ></button>
          );
        })}
      </div>

      <div className="ob-footer">
        <button type="button" className="btn-primary" onClick={next}>Continue →</button>
      </div>
    </div>
  );
}

// Step 4: Occasions
export function OnboardOccasions() {
  const navigate = useNavigate();

  const {
    user,
    updatePreferences,
  } = useUser();

  const [selected, setSelected] = useState(
    user.occasions?.length
      ? user.occasions
      : ['campus', 'fest', 'dates', 'gym'],
  );

  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] =
    useState(null);

  const all = [
    { id: 'campus',    emoji: '🎓', label: 'College / Campus' },
    { id: 'work',      emoji: '💼', label: 'Internship / Work' },
    { id: 'fest',      emoji: '🎉', label: 'Fests & Events' },
    { id: 'night-out', emoji: '🌙', label: 'Night Outs' },
    { id: 'dates',     emoji: '📅', label: 'Dates' },
    { id: 'puja',      emoji: '🙏', label: 'Puja / Festivals' },
    { id: 'travel',    emoji: '✈️', label: 'Travel' },
    { id: 'gym',       emoji: '💪', label: 'Gym / Sports' },
    { id: 'cafe',      emoji: '☕', label: 'Cafe Hangouts' },
    { id: 'concerts',  emoji: '🎤', label: 'Concerts' },
    { id: 'photos',    emoji: '📸', label: 'Photoshoots' },
    { id: 'home',      emoji: '🏡', label: 'Home / Casual' },
  ];

  const toggle = (id) => {
    setSelected((previous) =>
      previous.includes(id)
        ? previous.filter(
          (occasion) => occasion !== id,
        )
        : [...previous, id],
    );
  };

  const next = async () => {
    if (saving) {
      return;
    }

    const selectedBudget =
      BUDGET_OPTIONS.find(
        (option) =>
          option.id === user.budget,
      ) ??
      BUDGET_OPTIONS.find(
        (option) =>
          option.id === 'campus-casual',
      );

    setSaving(true);
    setSaveError(null);

    try {
      await updatePreferences({
        budget_min:
          user.budgetMin ??
          selectedBudget.min,

        budget_max:
          user.budgetMax ??
          selectedBudget.max,

        budget_tier:
          user.budget ??
          selectedBudget.id,

        preferred_colours:
          user.colours ?? [],

        preferred_brands:
          user.brands ?? [],

        preferred_occasions: selected,

        preferred_aesthetics:
          user.aesthetics ?? [],

        fit_preferences:
          user.fitPreferences ?? [],

        comfort_priority:
          user.comfortPriority ?? 0.5,

        trend_openness:
          user.trendOpenness ?? 0.5,
      });



      navigate('/quiz');
    } catch (error) {
      setSaveError(error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <OnboardShell>
      <div className="ob-card">
        {/* 3-segment progress bar — all 3 filled (last step) */}
        <div className="ob-prog-wrap">
          {[0, 1, 2].map(i => (
            <div key={i} className={`ob-bar ${i < 2 ? 'active' : ''} ${i === 2 ? 'active' : ''}`} />
          ))}
        </div>

        <h1 className="ob-title">
          When do you dress up? <span aria-hidden="true">📅</span>
        </h1>

        <p className="ob-sub">
          Pick all the occasions that matter to you.
        </p>

        <div className="occasion-grid">
          {all.map((occasion) => {
            const isSelected = selected.includes(occasion.id);
            return (
              <button
                type="button"
                key={occasion.id}
                className={`occasion-chip ${isSelected ? 'sel' : ''}`}
                aria-pressed={isSelected}
                onClick={() => toggle(occasion.id)}
              >
                <span className="occasion-emoji" aria-hidden="true">{occasion.emoji}</span>
                <span className="occasion-label">{occasion.label}</span>
                {isSelected && (
                  <CheckCircle size={16} className="occasion-check" aria-hidden="true" />
                )}
              </button>
            );
          })}
        </div>

        {saveError && (
          <ApiErrorState
            error={saveError}
            title="Could not save preferences"
            onRetry={next}
          />
        )}

        {/* CTA */}
        <button
          type="button"
          className="ob-cta"
          disabled={saving}
          onClick={next}
        >
          <span>{saving ? 'Saving…' : 'CONTINUE'}</span>
          <ArrowRight size={20} aria-hidden="true" />
        </button>
      </div>
    </OnboardShell>
  );
}

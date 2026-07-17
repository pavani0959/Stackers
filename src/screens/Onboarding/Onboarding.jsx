import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import '../../styles/Onboarding.css';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';

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

  return (
    <div className="screen ob-screen">
      <div className="ob-prog-wrap">
        {[0, 1, 2, 3].map(i => <div key={i} className={`ob-dot ${i === 0 ? 'active' : ''}`} />)}
      </div>
      <h1 className="ob-title">Before we begin,<br />let's understand you 👋</h1>
      <p className="ob-sub">No boring signup. Just a quick conversation.</p>

      <label className="ob-label" htmlFor="profile-name">What should we call you?</label>
      <input
        id="profile-name"
        className={`ob-name-input ${nameError ? 'error' : ''}`}
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
      {nameError && <div className="ob-field-error">{nameError}</div>}

      <label className="ob-label">How do you identify?</label>
      <div className="gender-grid">
        {[
          {
            id: 'male',
            icon: '🙋‍♂️',
            label: 'Male',
          },
          {
            id: 'female',
            icon: '🙋‍♀️',
            label: 'Female',
          },
          {
            id: 'nonbinary',
            icon: '🌈',
            label: 'Non-Binary / Prefer not to say',
            wide: true,
          },
        ].map((genderOption) => {
          const isSelected =
            gender === genderOption.id;

          return (
            <button
              type="button"
              key={genderOption.id}
              className={`gender-card ${genderOption.wide
                ? 'wide'
                : ''
                } ${isSelected
                  ? 'sel'
                  : ''
                }`}
              aria-pressed={isSelected}
              onClick={() => {
                setGender(
                  genderOption.id,
                );
              }}
            >
              <span
                className="g-icon"
                aria-hidden="true"
              >
                {genderOption.icon}
              </span>

              <span className="g-label">
                {genderOption.label}
              </span>
            </button>
          );
        })}
      </div>

      <label className="ob-label">Your age</label>
      <div className="age-num grad-text">{age}</div>
      <input type="range" className="age-slider" min="13" max="35" value={age} onChange={e => setAge(Number(e.target.value))} />

      {saveError && (
        <ApiErrorState
          error={saveError}
          title="Could not save your identity"
          onRetry={next}
        />
      )}

      <div className="ob-footer">
        <button type="button" className="btn-primary" onClick={next}>Continue →</button>
      </div>
    </div>
  );
}

// Step 2: Budget
export function OnboardBudget() {
  const navigate = useNavigate();
  const { user, updateUser } = useUser();

  const [budget, setBudget] = useState(
    user.budget || 'campus-casual',
  );

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
    <div className="screen ob-screen">
      <div className="ob-prog-wrap">
        {[0, 1, 2, 3].map((index) => (
          <div
            key={index}
            className={`ob-dot ${index === 0 ? 'done' : ''
              } ${index === 1 ? 'active' : ''
              }`}
          />
        ))}
      </div>

      <h1 className="ob-title">
        What's your outfit budget? 💸
      </h1>

      <p className="ob-sub">
        Per outfit. Be honest — no judgment here.
      </p>

      <div className="budget-list">
        {BUDGET_OPTIONS.map((option) => (
          <button
            key={option.id}
            type="button"
            className={`budget-opt ${budget === option.id
              ? 'sel'
              : ''
              }`}

            aria-pressed={budget === option.id}

            onClick={() =>
              setBudget(option.id)
            }
          >
            <div>
              <div className="budget-name">
                {option.label}
              </div>

              <div className="budget-range">
                {option.range}
              </div>
            </div>

            <div className="budget-chk">
              {budget === option.id
                ? '✓'
                : ''}
            </div>
          </button>
        ))}
      </div>

      <div className="ob-footer">
        <button
          type="button"
          className="btn-primary"
          onClick={next}
        >
          Continue →
        </button>
      </div>
    </div>
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
    {
      id: 'campus',
      label: '🎓 College / Campus',
    },
    {
      id: 'work',
      label: '💼 Internship / Work',
    },
    {
      id: 'fest',
      label: '🎉 Fests & Events',
    },
    {
      id: 'night-out',
      label: '🌙 Night Outs',
    },
    {
      id: 'dates',
      label: '📅 Dates',
    },
    {
      id: 'puja',
      label: '🙏 Puja / Festivals',
    },
    {
      id: 'travel',
      label: '✈️ Travel',
    },
    {
      id: 'gym',
      label: '🏃 Gym / Sports',
    },
    {
      id: 'cafe',
      label: '☕ Cafe Hangouts',
    },
    {
      id: 'concerts',
      label: '🎤 Concerts',
    },
    {
      id: 'photos',
      label: '📸 Photoshoots',
    },
    {
      id: 'home',
      label: '🏡 Home / Casual',
    },
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
    <div className="screen ob-screen">
      <div className="ob-prog-wrap">
        {[0, 1, 2, 3].map((index) => (
          <div
            key={index}
            className={`ob-dot ${index < 3 ? 'done' : ''
              } ${index === 3 ? 'active' : ''
              }`}
          />
        ))}
      </div>

      <h1 className="ob-title">
        When do you dress up? 📅
      </h1>

      <p className="ob-sub">
        Pick all the occasions that matter to you.
      </p>

      <div className="chip-grid">
        {all.map((occasion) => {
          const isSelected =
            selected.includes(
              occasion.id,
            );

          return (
            <button
              type="button"
              key={occasion.id}
              className={`chip ${isSelected
                  ? 'selected'
                  : ''
                }`}
              aria-pressed={isSelected}
              onClick={() => {
                toggle(occasion.id);
              }}
            >
              {occasion.label}
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

      <div className="ob-footer">
        <button
          type="button"
          className="btn-primary"
          disabled={saving}
          onClick={next}
        >
          {saving
            ? 'Saving…'
            : 'Continue →'}
        </button>
      </div>
    </div>
  );
}

import {
  useEffect,
  useState,
} from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import BottomNav from '../../components/BottomNav/BottomNav';
import '../../styles/Profile.css';
import {
  ArrowLeft,
  Dna,
  Heart,
} from 'lucide-react';

const BUDGET_OPTIONS = [
  {
    label: '₹500–₹1,500',
    value: 'campus-casual',
    description: 'Budget Friendly',
    min: 500,
    max: 1500,
  },
  {
    label: '₹1,500–₹3,000',
    value: 'mid-range',
    description: 'Mid Range',
    min: 1500,
    max: 3000,
  },
  {
    label: '₹3,000–₹6,000',
    value: 'premium',
    description: 'Premium',
    min: 3000,
    max: 6000,
  },
  {
    label: '₹6,000+',
    value: 'luxury',
    description: 'Luxury',
    min: 6000,
    max: null,
  },
];

const OCCASION_OPTIONS = [
  'casual',
  'campus',
  'formal',
  'interview',
  'party',
  'date',
  'festive',
  'outdoor',
  'gym',
];

const COLOUR_OPTIONS = [
  'black',
  'white',
  'beige',
  'grey',
  'brown',
  'olive',
  'rust',
  'pink',
  'lavender',
  'sky blue',
  'red',
  'cobalt',
];

const AESTHETIC_OPTIONS = [
  'minimalist',
  'campusCasual',
  'quietLuxury',
  'streetwear',
  'romantic',
  'sporty',
  'y2k',
  'bohemian',
];

const BRAND_OPTIONS = [
  'Mango',
  'ONLY',
  'Roadster',
  'HIGHLANDER',
  'Puma',
  'HRX',
  'Sassafras',
  'Tokyo Talkies',
];

const FIT_OPTIONS = [
  'relaxed',
  'oversized',
  'regular',
  'slim',
  'fitted',
];

const FASHION_GOALS = [
  'Refine my signature style',
  'Experiment with new styles',
  'Build a versatile wardrobe',
  'Make smarter purchase decisions',
];

const GENDER_EMOJI = {
  male: '♂',
  female: '♀',
  'non-binary': '⚧',
};

function formatLabel(value) {
  if (!value) {
    return '';
  }

  return value
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/[-_]/g, ' ')
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase(),
    );
}

function getBudgetTier(user) {
  if (user.budgetTier) {
    return user.budgetTier;
  }

  if (user.budget) {
    return user.budget;
  }

  const budgetMaximum = Number(
    user.budgetMax,
  );

  if (
    Number.isFinite(budgetMaximum) &&
    budgetMaximum <= 1500
  ) {
    return 'campus-casual';
  }

  if (
    Number.isFinite(budgetMaximum) &&
    budgetMaximum <= 3000
  ) {
    return 'mid-range';
  }

  if (
    Number.isFinite(budgetMaximum) &&
    budgetMaximum <= 6000
  ) {
    return 'premium';
  }

  if (
    user.budgetMin !== null &&
    user.budgetMin !== undefined &&
    Number(user.budgetMin) >= 6000
  ) {
    return 'luxury';
  }

  return 'campus-casual';
}

function getPrimaryOccasion(user) {
  const priorities =
    user.occasionPriorities ?? {};

  const highestPriority = Object.entries(
    priorities,
  ).sort(
    ([, leftPriority], [, rightPriority]) =>
      rightPriority - leftPriority,
  )[0];

  return (
    highestPriority?.[0] ??
    user.occasions?.[0] ??
    ''
  );
}

function getErrorMessage(error) {
  return (
    error?.message ??
    error?.detail ??
    'Could not save your profile.'
  );
}

export default function Profile() {
  const navigate = useNavigate();

  const {
    user,
    updateIdentity,
    updatePreferences,
  } = useUser();

  const [editing, setEditing] =
    useState(false);

  const [name, setName] = useState(
    user.name ?? '',
  );

  const [budgetTier, setBudgetTier] =
    useState(() => getBudgetTier(user));

  const [occasions, setOccasions] =
    useState(user.occasions ?? []);

  const [
    primaryOccasion,
    setPrimaryOccasion,
  ] = useState(() =>
    getPrimaryOccasion(user),
  );

  const [colours, setColours] = useState(
    user.colours ??
      user.preferredColours ??
      [],
  );

  const [brands, setBrands] = useState(
    user.brands ??
      user.preferredBrands ??
      [],
  );

  const [aesthetics, setAesthetics] =
    useState(
      user.aesthetics ??
        user.preferredAesthetics ??
        [],
    );

  const [
    fitPreferences,
    setFitPreferences,
  ] = useState(
    user.fitPreferences ?? [],
  );

  const [
    comfortExpressionBalance,
    setComfortExpressionBalance,
  ] = useState(
    user.comfortExpressionBalance ??
      0.5,
  );

  const [fashionGoal, setFashionGoal] =
    useState(user.fashionGoal ?? '');

  const [saving, setSaving] =
    useState(false);

  const [saveError, setSaveError] =
    useState(null);

  const [toast, setToast] = useState('');

  const [expandedSection, setExpandedSection] = useState(null);

  useEffect(() => {
    if (editing) {
      return;
    }

    setName(user.name ?? '');
    setBudgetTier(getBudgetTier(user));
    setOccasions(user.occasions ?? []);
    setPrimaryOccasion(
      getPrimaryOccasion(user),
    );

    setColours(
      user.colours ??
        user.preferredColours ??
        [],
    );

    setBrands(
      user.brands ??
        user.preferredBrands ??
        [],
    );

    setAesthetics(
      user.aesthetics ??
        user.preferredAesthetics ??
        [],
    );

    setFitPreferences(
      user.fitPreferences ?? [],
    );

    setComfortExpressionBalance(
      user.comfortExpressionBalance ??
        0.5,
    );

    setFashionGoal(
      user.fashionGoal ?? '',
    );
  }, [editing, user]);

  function showToast(message) {
    setToast(message);

    window.setTimeout(() => {
      setToast('');
    }, 2500);
  }

  function toggleArrayValue(
    value,
    values,
    setValues,
  ) {
    setValues((currentValues) =>
      currentValues.includes(value)
        ? currentValues.filter(
            (item) => item !== value,
          )
        : [...currentValues, value],
    );
  }

  function toggleOccasion(occasion) {
    setOccasions(
      (currentOccasions) => {
        if (
          currentOccasions.includes(
            occasion,
          )
        ) {
          const updatedOccasions =
            currentOccasions.filter(
              (item) =>
                item !== occasion,
            );

          if (
            primaryOccasion === occasion
          ) {
            setPrimaryOccasion(
              updatedOccasions[0] ?? '',
            );
          }

          return updatedOccasions;
        }

        const updatedOccasions = [
          ...currentOccasions,
          occasion,
        ];

        if (!primaryOccasion) {
          setPrimaryOccasion(occasion);
        }

        return updatedOccasions;
      },
    );
  }

  function buildOccasionPriorities() {
    return occasions.reduce(
      (priorities, occasion) => {
        priorities[occasion] =
          occasion === primaryOccasion
            ? 1
            : 0.7;

        return priorities;
      },
      {},
    );
  }

  function resetForm() {
    setName(user.name ?? '');
    setBudgetTier(getBudgetTier(user));
    setOccasions(user.occasions ?? []);
    setPrimaryOccasion(
      getPrimaryOccasion(user),
    );

    setColours(
      user.colours ??
        user.preferredColours ??
        [],
    );

    setBrands(
      user.brands ??
        user.preferredBrands ??
        [],
    );

    setAesthetics(
      user.aesthetics ??
        user.preferredAesthetics ??
        [],
    );

    setFitPreferences(
      user.fitPreferences ?? [],
    );

    setComfortExpressionBalance(
      user.comfortExpressionBalance ??
        0.5,
    );

    setFashionGoal(
      user.fashionGoal ?? '',
    );

    setSaveError(null);
  }

  async function handleSave() {
    const trimmedName = name.trim();

    if (!trimmedName) {
      setSaveError(
        new Error(
          'Please enter your name.',
        ),
      );

      return;
    }

    const selectedBudget =
      BUDGET_OPTIONS.find(
        (option) =>
          option.value === budgetTier,
      );

    if (!selectedBudget) {
      setSaveError(
        new Error(
          'Please select a budget range.',
        ),
      );

      return;
    }

    setSaving(true);
    setSaveError(null);

    try {
      await updateIdentity({
        name: trimmedName,
      });

      await updatePreferences({
        budget_min:
          selectedBudget.min,

        budget_max:
          selectedBudget.max,

        budget_tier:
          selectedBudget.value,

        preferred_occasions:
          occasions,

        preferred_colours:
          colours,

        preferred_brands:
          brands,

        preferred_aesthetics:
          aesthetics,

        fit_preferences:
          fitPreferences,

        comfort_priority: Number(
          (
            1 -
            comfortExpressionBalance
          ).toFixed(2),
        ),

        trend_openness: Number(
          comfortExpressionBalance.toFixed(
            2,
          ),
        ),

        comfort_expression_balance:
          Number(
            comfortExpressionBalance.toFixed(
              2,
            ),
          ),

        occasion_priorities:
          buildOccasionPriorities(),

        fashion_goal:
          fashionGoal || null,
      });

      setEditing(false);

      showToast(
        'Profile saved successfully! ✅',
      );
    } catch (requestError) {
      setSaveError(requestError);

      showToast(
        'Could not save. Try again.',
      );
    } finally {
      setSaving(false);
    }
  }

  const dnaEntries = Object.entries(
    user.dna ?? {},
  ).sort(
    ([, leftPercentage], [
      ,
      rightPercentage,
    ]) =>
      rightPercentage -
      leftPercentage,
  );

  const primaryDna = dnaEntries[0];

  const genderEmoji =
    GENDER_EMOJI[user.gender] ?? '🧑';

  const selectedBudget =
    BUDGET_OPTIONS.find(
      (option) =>
        option.value === budgetTier,
    );

  return (
    <div className="screen profile-screen">
      <div className="prf-hdr">
        <div className="prf-back-row">
          <button
            type="button"
            className="back-btn"
            onClick={() => navigate(-1)}
            aria-label="Go back"
          >
            <ArrowLeft aria-hidden="true" size={21} />
          </button>

          <div className="prf-hdr-title">
            My Profile
          </div>

          {!editing && (
            <button
              type="button"
              className="prf-edit-btn-new"
              onClick={() => {
                setSaveError(null);
                setEditing(true);
              }}
            >
              <span className="prf-edit-icon">✎</span> Edit
            </button>
          )}
        </div>
      </div>

      <div className="prf-body">
        <div className="prf-hero">
          <div className="prf-avatar">
            <span className="prf-avatar-emoji">
              {genderEmoji}
            </span>
          </div>

          {editing ? (
            <input
              className="prf-name-input"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Your name"
              maxLength={120}
            />
          ) : (
            <div className="prf-name">
              {user.name || 'Style Explorer'}
            </div>
          )}

          <div className="prf-sub-info">
            {user.gender && (
              <span className="prf-badge-sm">
                👤 {formatLabel(user.gender)}
              </span>
            )}
            {user.age && (
              <span className="prf-badge-sm">
                📅 Age {user.age}
              </span>
            )}
          </div>
        </div>

        {dnaEntries.length > 0 && (
          <div className="prf-card dna-card">
            <div className="prf-card-title-row">
              <div className="prf-card-title">
                🧬 Fashion DNA
              </div>
            </div>

            <div className="prf-dna-traits">
              {dnaEntries.slice(0, 4).map(([style, percentage]) => (
                <div key={style} className="prf-dna-row">
                  <div className="prf-dna-name">{formatLabel(style)}</div>
                  <div className="prf-dna-bar-wrap">
                    <div className="prf-dna-bar" style={{ width: `${percentage}%` }} />
                  </div>
                  <div className="prf-dna-pct">{percentage}%</div>
                </div>
              ))}
            </div>

            <div className="prf-dna-summary-pills">
              <div className="prf-identity-pill">
                ⭐ Identity: <strong>{user.identityName || formatLabel(primaryDna?.[0]) || 'Calculating…'}</strong>
              </div>
              {user.profileConfidence != null && (
                <div className="prf-identity-pill">
                  📊 Confidence: <strong>{user.profileConfidence}%</strong>
                </div>
              )}
            </div>
          </div>
        )}

        <div className={`prf-card ${!editing ? 'clickable' : ''}`} role={!editing ? "button" : undefined} tabIndex={!editing ? 0 : undefined} onKeyDown={(e) => { if(!editing && (e.key==='Enter'||e.key===' ')) { e.preventDefault(); setEditing(true); } }} onClick={() => !editing && setEditing(true)}>
          <div className="prf-card-title-row">
            <div className="prf-card-title">💰 Budget Range</div>
            {!editing && <div className="prf-chevron">›</div>}
          </div>

          {editing ? (
            <div className="prf-budget-opts">
              {BUDGET_OPTIONS.map((option) => (
                <button
                  type="button"
                  key={option.value}
                  className={`prf-budget-btn ${budgetTier === option.value ? 'active' : ''}`}
                  onClick={() => setBudgetTier(option.value)}
                >
                  <div className="prf-budget-lbl">{option.label}</div>
                  <div className="prf-budget-desc">{option.description}</div>
                </button>
              ))}
            </div>
          ) : (
            <div className="prf-value-pills">
              {selectedBudget?.label ? (
                <span className="prf-occ-chip active">{selectedBudget.label}</span>
              ) : (
                <span className="prf-not-selected">Not selected</span>
              )}
            </div>
          )}
        </div>

        <div className={`prf-card ${!editing ? 'clickable' : ''}`} role={!editing ? "button" : undefined} tabIndex={!editing ? 0 : undefined} onKeyDown={(e) => { if(!editing && (e.key==='Enter'||e.key===' ')) { e.preventDefault(); setEditing(true); } }} onClick={() => !editing && setEditing(true)}>
          <div className="prf-card-title-row">
            <div className="prf-card-title">📅 Your Occasions</div>
            {!editing && <div className="prf-chevron">›</div>}
          </div>

          {editing ? (
            <>
              <div className="prf-occ-chips">
                {OCCASION_OPTIONS.map((occasion) => (
                  <button
                    type="button"
                    key={occasion}
                    className={`prf-occ-chip ${occasions.includes(occasion) ? 'active' : ''}`}
                    onClick={() => toggleOccasion(occasion)}
                  >
                    {formatLabel(occasion)}
                  </button>
                ))}
              </div>

              {occasions.length > 0 && (
                <label className="prf-field">
                  <span>Primary occasion</span>
                  <select value={primaryOccasion} onChange={(event) => setPrimaryOccasion(event.target.value)}>
                    {occasions.map((occasion) => (
                      <option key={occasion} value={occasion}>{formatLabel(occasion)}</option>
                    ))}
                  </select>
                </label>
              )}
            </>
          ) : (
            <div className="prf-value-pills">
              {occasions.length > 0 ? (
                occasions.map((occasion) => (
                  <span key={occasion} className="prf-occ-chip active prf-color-party">
                    {formatLabel(occasion)}
                  </span>
                ))
              ) : (
                <span className="prf-not-selected">Not selected</span>
              )}
            </div>
          )}
        </div>

        <div className={`prf-card ${!editing ? 'clickable' : ''}`} role={!editing ? "button" : undefined} tabIndex={!editing ? 0 : undefined} onKeyDown={(e) => { if(!editing && (e.key==='Enter'||e.key===' ')) { e.preventDefault(); setEditing(true); } }} onClick={() => !editing && setEditing(true)}>
          <div className="prf-card-title-row">
            <div className="prf-card-title">🎨 Preferred Colours</div>
            {!editing && <div className="prf-chevron">›</div>}
          </div>

          {editing ? (
            <div className="prf-occ-chips">
              {COLOUR_OPTIONS.map((colour) => (
                <button
                  type="button"
                  key={colour}
                  className={`prf-occ-chip ${colours.includes(colour) ? 'active' : ''}`}
                  onClick={() => toggleArrayValue(colour, colours, setColours)}
                >
                  {formatLabel(colour)}
                </button>
              ))}
            </div>
          ) : (
            <div className="prf-value-pills">
              {colours.length > 0 ? (
                colours.map((colour) => (
                  <span key={colour} className={`prf-occ-chip active prf-color-${colour.replace(' ', '')}`}>
                    {formatLabel(colour)}
                  </span>
                ))
              ) : (
                <span className="prf-not-selected">Not selected</span>
              )}
            </div>
          )}
        </div>

        <div className={`prf-card ${!editing ? 'clickable' : ''}`} role={!editing ? "button" : undefined} tabIndex={!editing ? 0 : undefined} onKeyDown={(e) => { if(!editing && (e.key==='Enter'||e.key===' ')) { e.preventDefault(); setEditing(true); } }} onClick={() => !editing && setEditing(true)}>
          <div className="prf-card-title-row">
            <div className="prf-card-title">✨ Preferred Aesthetics</div>
            {!editing && <div className="prf-chevron">›</div>}
          </div>

          {editing ? (
            <div className="prf-occ-chips">
              {AESTHETIC_OPTIONS.map((aesthetic) => (
                <button
                  type="button"
                  key={aesthetic}
                  className={`prf-occ-chip ${aesthetics.includes(aesthetic) ? 'active' : ''}`}
                  onClick={() => toggleArrayValue(aesthetic, aesthetics, setAesthetics)}
                >
                  {formatLabel(aesthetic)}
                </button>
              ))}
            </div>
          ) : (
            <div className="prf-value-pills">
              {aesthetics.length > 0 ? (
                aesthetics.map((aesthetic) => (
                  <span key={aesthetic} className="prf-occ-chip active prf-color-aesthetic">
                    {formatLabel(aesthetic)}
                  </span>
                ))
              ) : (
                <span className="prf-not-selected">Not selected</span>
              )}
            </div>
          )}
        </div>

        <div className={`prf-card ${!editing ? 'clickable' : ''}`} role={!editing ? "button" : undefined} tabIndex={!editing ? 0 : undefined} onKeyDown={(e) => { if(!editing && (e.key==='Enter'||e.key===' ')) { e.preventDefault(); setEditing(true); } }} onClick={() => !editing && setEditing(true)}>
          <div className="prf-card-title-row">
            <div className="prf-card-title">👕 Fit Preferences</div>
            {!editing && <div className="prf-chevron">›</div>}
          </div>

          {editing ? (
            <div className="prf-occ-chips">
              {FIT_OPTIONS.map((fit) => (
                <button
                  type="button"
                  key={fit}
                  className={`prf-occ-chip ${fitPreferences.includes(fit) ? 'active' : ''}`}
                  onClick={() => toggleArrayValue(fit, fitPreferences, setFitPreferences)}
                >
                  {formatLabel(fit)}
                </button>
              ))}
            </div>
          ) : (
            <div className="prf-value-pills">
              {fitPreferences.length > 0 ? (
                fitPreferences.map((fit) => (
                  <span key={fit} className="prf-occ-chip active prf-color-fit">
                    {formatLabel(fit)}
                  </span>
                ))
              ) : (
                <span className="prf-not-selected">Not selected</span>
              )}
            </div>
          )}
        </div>

        <div className={`prf-card ${!editing ? 'clickable' : ''}`} role={!editing ? "button" : undefined} tabIndex={!editing ? 0 : undefined} onKeyDown={(e) => { if(!editing && (e.key==='Enter'||e.key===' ')) { e.preventDefault(); setEditing(true); } }} onClick={() => !editing && setEditing(true)}>
          <div className="prf-card-title-row">
            <div className="prf-card-title">🏷️ Preferred Brands</div>
            {!editing && <div className="prf-chevron">›</div>}
          </div>

          {editing ? (
            <div className="prf-occ-chips">
              {BRAND_OPTIONS.map((brand) => (
                <button
                  type="button"
                  key={brand}
                  className={`prf-occ-chip ${brands.includes(brand) ? 'active' : ''}`}
                  onClick={() => toggleArrayValue(brand, brands, setBrands)}
                >
                  {formatLabel(brand)}
                </button>
              ))}
            </div>
          ) : (
            <div className="prf-value-pills">
              {brands.length > 0 ? (
                brands.map((brand) => (
                  <span key={brand} className="prf-occ-chip active prf-color-brand">
                    {formatLabel(brand)}
                  </span>
                ))
              ) : (
                <span className="prf-not-selected">Not selected</span>
              )}
            </div>
          )}
        </div>

        <div className={`prf-card ${!editing ? 'clickable' : ''}`} role={!editing ? "button" : undefined} tabIndex={!editing ? 0 : undefined} onKeyDown={(e) => { if(!editing && (e.key==='Enter'||e.key===' ')) { e.preventDefault(); setEditing(true); } }} onClick={() => !editing && setEditing(true)}>
          <div className="prf-card-title-row">
            <div className="prf-card-title">🎯 Fashion Goal</div>
            {!editing && <div className="prf-chevron">›</div>}
          </div>

          {editing ? (
            <div className="prf-occ-chips">
              <select
                className="prf-select"
                value={fashionGoal}
                onChange={(event) => setFashionGoal(event.target.value)}
              >
                <option value="">Select your fashion goal</option>
                {FASHION_GOALS.map((goal) => (
                  <option key={goal} value={goal}>{formatLabel(goal)}</option>
                ))}
              </select>
            </div>
          ) : (
            <div className="prf-value-pills">
              {fashionGoal ? (
                <span className="prf-occ-chip active prf-color-goal">{formatLabel(fashionGoal)}</span>
              ) : (
                <span className="prf-not-selected">Not selected</span>
              )}
            </div>
          )}
        </div>

        <div className={`prf-card ${!editing ? 'clickable' : ''}`} role={!editing ? "button" : undefined} tabIndex={!editing ? 0 : undefined} onKeyDown={(e) => { if(!editing && (e.key==='Enter'||e.key===' ')) { e.preventDefault(); setEditing(true); } }} onClick={() => !editing && setEditing(true)}>
          <div className="prf-card-title-row">
            <div className="prf-card-title">⚖️ Comfort vs Expression</div>
            {!editing && <div className="prf-chevron">›</div>}
          </div>

          {editing ? (
            <div className="prf-range-wrap">
              <div className="prf-range-labels">
                <span>Comfort</span>
                <span>Self-expression</span>
              </div>

              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={comfortExpressionBalance}
                onChange={(event) => setComfortExpressionBalance(Number(event.target.value))}
              />

              <div className="prf-value-sub">
                {Math.round(comfortExpressionBalance * 100)}% expression
              </div>
            </div>
          ) : (
            <div className="prf-value-pills">
              <span className="prf-occ-chip active prf-color-comfort">
                {Math.round(comfortExpressionBalance * 100)}% Expression
              </span>
            </div>
          )}
        </div>



        {saveError ? (
          <div
            className="prf-save-error"
            role="alert"
          >
            {getErrorMessage(saveError)}
          </div>
        ) : null}

        {editing ? (
          <div className="prf-actions">
            <button
              type="button"
              className="prf-save-btn"
              onClick={handleSave}
              disabled={saving}
            >
              {saving
                ? 'Saving…'
                : 'Save Changes'}
            </button>

            <button
              type="button"
              className="prf-cancel-btn"
              disabled={saving}
              onClick={() => {
                resetForm();
                setEditing(false);
              }}
            >
              Cancel
            </button>
          </div>
        ) : null}

        <div className="prf-accordions">
          {/* Fashion Memory */}
          <div className={`prf-accordion ${expandedSection === 'memory' ? 'expanded' : ''}`}>
            <div
              className="prf-acc-hdr"
              onClick={() => setExpandedSection(expandedSection === 'memory' ? null : 'memory')}
            >
              <div className="prf-acc-title">
                <span className="prf-acc-icon-svg">📈</span> Fashion Memory
              </div>
              <div className="prf-acc-chevron">{expandedSection === 'memory' ? '⌃' : '⌄'}</div>
            </div>
            {expandedSection === 'memory' && (
              <div className="prf-acc-body">
                <p>Track how your style evolves over time and past occasions.</p>
                <button type="button" className="prf-acc-link-btn" onClick={() => navigate('/memory')}>
                  Open Fashion Memory ›
                </button>
              </div>
            )}
          </div>

          {/* My Wishlist */}
          <div className={`prf-accordion ${expandedSection === 'wishlist' ? 'expanded' : ''}`}>
            <div
              className="prf-acc-hdr"
              onClick={() => setExpandedSection(expandedSection === 'wishlist' ? null : 'wishlist')}
            >
              <div className="prf-acc-title">
                <span className="prf-acc-icon-svg"><Heart size={16} /></span> My Wishlist
              </div>
              <div className="prf-acc-chevron">{expandedSection === 'wishlist' ? '⌃' : '⌄'}</div>
            </div>
            {expandedSection === 'wishlist' && (
              <div className="prf-acc-body">
                <p>You have {(user.wishlist || []).length} item(s) in your wishlist.</p>
                <button type="button" className="prf-acc-link-btn" onClick={() => navigate('/wishlist')}>
                  Open My Wishlist ›
                </button>
              </div>
            )}
          </div>

          {/* DNA Identity Card */}
          <div className={`prf-accordion ${expandedSection === 'dna' ? 'expanded' : ''}`}>
            <div
              className="prf-acc-hdr"
              onClick={() => setExpandedSection(expandedSection === 'dna' ? null : 'dna')}
            >
              <div className="prf-acc-title">
                <span className="prf-acc-icon-svg"><Dna size={16} /></span> DNA Identity Card
              </div>
              <div className="prf-acc-chevron">{expandedSection === 'dna' ? '⌃' : '⌄'}</div>
            </div>
            {expandedSection === 'dna' && (
              <div className="prf-acc-body">
                <p>View and share your personalized Aesthetic Passport.</p>
                <button type="button" className="prf-acc-link-btn" onClick={() => navigate('/identity-card')}>
                  Open Identity Card ›
                </button>
              </div>
            )}
          </div>
        </div>
        
        {/* Floating Action Button */}
        <button className="prf-fab" aria-label="Quick action">
          ✨
        </button>
      </div>

      {toast ? (
        <div className="toast">
          {toast}
        </div>
      ) : null}

      <BottomNav />
    </div>
  );
}
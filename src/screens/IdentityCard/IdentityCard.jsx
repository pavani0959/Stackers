import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import {
  buildDnaBars,
} from '../../features/dna/formatDNA';
import '../../styles/IdentityCard.css';

function formatBudget(user) {
  const hasMinimum =
    user.budgetMin !== null &&
    user.budgetMin !== undefined;

  const hasMaximum =
    user.budgetMax !== null &&
    user.budgetMax !== undefined;

  if (hasMinimum && hasMaximum) {
    return `₹${user.budgetMin.toLocaleString(
      'en-IN',
    )} – ₹${user.budgetMax.toLocaleString(
      'en-IN',
    )}`;
  }

  if (hasMaximum) {
    return `Up to ₹${user.budgetMax.toLocaleString(
      'en-IN',
    )}`;
  }

  if (hasMinimum) {
    return `From ₹${user.budgetMin.toLocaleString(
      'en-IN',
    )}`;
  }

  if (user.budget) {
    return user.budget.replace(/-/g, ' ');
  }

  return null;
}

function formatMemberSince(createdAt) {
  if (!createdAt) {
    return 'Recently joined';
  }

  const createdDate = new Date(createdAt);

  if (Number.isNaN(createdDate.getTime())) {
    return 'Recently joined';
  }

  return createdDate.toLocaleDateString(
    'en-IN',
    {
      month: 'long',
      year: 'numeric',
    },
  );
}

function buildOccasionList(user) {
  const priorities =
    user.occasionPriorities ?? {};

  const prioritizedOccasions = Object.entries(
    priorities,
  )
    .sort(
      ([, leftPriority], [, rightPriority]) =>
        rightPriority - leftPriority,
    )
    .map(([occasion]) => occasion);

  if (prioritizedOccasions.length > 0) {
    return prioritizedOccasions;
  }

  return user.occasions ?? [];
}

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

export default function IdentityCard() {
  const navigate = useNavigate();
  const { user } = useUser();

  const bars = buildDnaBars(user.dna);
  const name =
    user.name?.trim() || 'Style Explorer';

  const identityName =
    user.identityName ||
    bars[0]?.label ||
    'Your Fashion Identity';

  const identityDescription =
    user.identityDescription ||
    'Your Fashion DNA will become more precise as you interact with styles, products, and recommendations.';

  const memberSince = formatMemberSince(
    user.createdAt,
  );

  const budget = formatBudget(user);

  const occasions = buildOccasionList(
    user,
  );

  const colours = user.colours ?? [];
  const fitPreferences =
    user.fitPreferences ?? [];

  const confidence =
    user.profileConfidence ?? 0;

  const confidenceBreakdown =
    user.confidenceBreakdown ?? {};

  const evidence = user.evidence ?? {};

  async function share() {
    const dnaText = bars
      .slice(0, 4)
      .map(
        (bar) =>
          `${bar.label}: ${bar.percentage}%`,
      )
      .join(' | ');

    const text = [
      `My Myntra Identity: ${identityName}`,
      dnaText,
      `Style Confidence: ${confidence}%`,
    ]
      .filter(Boolean)
      .join('\n');

    try {
      if (navigator.share) {
        await navigator.share({
          title: 'My Fashion DNA',
          text,
        });

        return;
      }

      if (navigator.clipboard) {
        await navigator.clipboard.writeText(
          text,
        );

        window.alert(
          'Your Fashion DNA has been copied.',
        );

        return;
      }

      window.prompt(
        'Copy your Fashion DNA:',
        text,
      );
    } catch (shareError) {
      if (shareError?.name !== 'AbortError') {
        window.prompt(
          'Copy your Fashion DNA:',
          text,
        );
      }
    }
  }

  return (
    <div className="screen id-card-screen">
      <p className="id-card-lbl">
        ✦ Your Aesthetic Passport{' '}
        <span className="new-badge">
          NEW
        </span>
      </p>

      <div className="id-card">
        <div className="card-glow1" />
        <div className="card-glow2" />

        <div className="card-top">
          <span className="card-brand">
            MYNTRA IDENTITY
          </span>

          <div
            className="card-logo-icon"
            aria-hidden="true"
          >
            🧬
          </div>
        </div>

        <div className="card-name">
          {name}
        </div>

        <div className="card-sub">
          <p>
            Style Member · Since{' '}
            {memberSince}
          </p>

          {user.dnaVersion ? (
            <p>
              Fashion DNA Version{' '}
              {user.dnaVersion}
            </p>
          ) : null}
        </div>

        <div className="identity-summary">
          <h1 className="identity-name">
            {identityName}
          </h1>

          <p className="identity-description">
            {identityDescription}
          </p>
        </div>

        <div className="card-tags">
          {bars.slice(0, 3).map(
            (bar, index) => (
              <span
                key={bar.key}
                className={`card-tag ct-${
                  [
                    'pink',
                    'purple',
                    'blue',
                  ][index]
                }`}
              >
                {bar.label}{' '}
                {bar.percentage}%
              </span>
            ),
          )}

          {budget ? (
            <span className="card-tag ct-pink">
              {budget}
            </span>
          ) : null}

          {occasions
            .slice(0, 2)
            .map((occasion) => (
              <span
                key={occasion}
                className="card-tag ct-purple"
              >
                {formatLabel(occasion)}
              </span>
            ))}
        </div>

        <div className="identity-details">
          {colours.length > 0 ? (
            <div className="identity-detail">
              <span className="detail-label">
                Colour palette
              </span>

              <span className="detail-value">
                {colours
                  .slice(0, 4)
                  .map(formatLabel)
                  .join(', ')}
              </span>
            </div>
          ) : null}

          {fitPreferences.length > 0 ? (
            <div className="identity-detail">
              <span className="detail-label">
                Preferred fit
              </span>

              <span className="detail-value">
                {fitPreferences
                  .map(formatLabel)
                  .join(', ')}
              </span>
            </div>
          ) : null}

          {user.fashionGoal ? (
            <div className="identity-detail">
              <span className="detail-label">
                Fashion goal
              </span>

              <span className="detail-value">
                {user.fashionGoal}
              </span>
            </div>
          ) : null}
        </div>

        <div className="card-conf">
          <div>
            <div className="cc-label">
              Style Confidence
            </div>

            <div className="card-conf-val grad-text">
              {confidence}%
            </div>
          </div>
        </div>

        <div className="confidence-breakdown">
          <p>
            Quiz completeness:{' '}
            <strong>
              {confidenceBreakdown
                .quiz_completeness ?? 0}
              /40
            </strong>
          </p>

          <p>
            Answer consistency:{' '}
            <strong>
              {confidenceBreakdown
                .answer_consistency ?? 0}
              /25
            </strong>
          </p>

          <p>
            Preference coverage:{' '}
            <strong>
              {confidenceBreakdown
                .preference_coverage ?? 0}
              /20
            </strong>
          </p>

          <p>
            Behaviour evidence:{' '}
            <strong>
              {confidenceBreakdown
                .behavior_evidence ?? 0}
              /15
            </strong>
          </p>
        </div>

        <div className="identity-evidence">
          <span>
            Quiz answers:{' '}
            {evidence.quiz_answers ?? 0}
          </span>

          <span>
            Behaviour events:{' '}
            {evidence.behavior_events ?? 0}
          </span>
        </div>
      </div>

      <div className="identity-card-actions">
        <button
          type="button"
          className="id-edit-btn"
          onClick={() =>
            navigate('/profile')
          }
        >
          Edit Identity
        </button>

        <button
          type="button"
          className="id-share-btn"
          onClick={share}
        >
          📤 Share My Aesthetic Passport
        </button>

        <button
          type="button"
          className="id-enter-btn"
          onClick={() =>
            navigate('/home')
          }
        >
          Enter My Myntra →
        </button>
      </div>
    </div>
  );
}
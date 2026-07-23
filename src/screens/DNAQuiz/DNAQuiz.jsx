import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { quizQuestions } from '../../data/quizQuestions';
import { useReducedMotion } from '../../hooks/useReducedMotion';
import { gsap, useGSAP } from '../../motion/gsap';
import { ArrowRight, CheckCircle } from 'lucide-react';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';
import OnboardingCard from '../../components/OnboardingCard/OnboardingCard';
import '../../styles/DNAQuiz.css';

/* ── tiny 4-point sparkle SVG ── */
function Sparkle({ size = 16, color = 'var(--gradient-hero-start)', className = '' }) {
  return (
    <svg
      className={`quiz-sparkle ${className}`}
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

/* ── Per-choice card metadata (title, description, accent) ──
   Keys = choice.id. For choices without an explicit entry the
   component gracefully falls back to the raw label text.        */
const CHOICE_META = {
  /* Q1 — everyday look */
  'minimal-campus': { title: 'Minimal Campus', desc: 'Clean everyday college looks', accent: '#6b7280' },
  'street-ready': { title: 'Street Ready', desc: 'Laidback and confident street style', accent: '#7c3aed' },
  'soft-romantic': { title: 'Soft Romantic', desc: 'Gentle colors and flowing trends', accent: '#ec4899' },
  'quiet-luxury': { title: 'Quiet Luxury', desc: 'Subtle earthy and modern polish', accent: '#b45309' },
  /* Q2 — silhouette */
  'relaxed-fit': { title: 'Relaxed Fit', desc: 'Easy movement and natural grace', accent: '#10b981' },
  'oversized-fit': { title: 'Oversized', desc: 'Loose, expressive and on-trend', accent: '#7c3aed' },
  'regular-fit': { title: 'Regular Fit', desc: 'Clean, proportional for everyday wear', accent: '#0ea5e9' },
  'fitted-fit': { title: 'Fitted', desc: 'Defined and close to the body', accent: '#ec4899' },
  /* Q3 — brand */
  'clean-premium': { title: 'Clean & Premium', desc: 'Refined minimal aesthetic with premium polish', accent: '#1e293b' },
  'youth-street': { title: 'Youth Street', desc: 'Culture-forward streetwear energy', accent: '#7c3aed' },
  'sporty-active': { title: 'Sporty Active', desc: 'Functional, energetic and performance-led', accent: '#10b981' },
  'expressive-trend': { title: 'Expressive Trends', desc: 'Trend-led, experimental and bold', accent: '#f97316' },
  /* Q4 — colour */
  'neutral-palette': { title: 'Neutral Palette', desc: 'Black, white, beige & grey', accent: '#ec4899', swatches: ['#1a1a1a', '#6b7280', '#d1d5db', '#d4c9a8', '#f5f5f4'] },
  'earthy-palette': { title: 'Earthy Palette', desc: 'Brown, olive, rust & cream', accent: '#92400e', swatches: ['#5c3d2e', '#6b7c3e', '#b45309', '#c4a882', '#f5f0e8'] },
  'pastel-palette': { title: 'Pastel Palette', desc: 'Lavender, pink, blue & mint', accent: '#a78bfa', swatches: ['#c4b5fd', '#f9a8d4', '#93c5fd', '#86efac', '#fcd5ce'] },
  'bold-palette': { title: 'Bold Palette', desc: 'Red, cobalt, orange & magenta', accent: '#dc2626', swatches: ['#dc2626', '#2563eb', '#f97316', '#d946ef', '#eab308'] },
  /* Q5 — comfort vs expression */
  'comfort-first': { title: 'Comfort First', desc: 'Function above everything', accent: '#6b7280' },
  'comfort-balanced': { title: 'Mostly Comfort', desc: 'Comfortable but polished', accent: '#0ea5e9' },
  'expression-balanced': { title: 'Mostly Expression', desc: 'Expressive yet wearable', accent: '#ec4899' },
  'expression-first': { title: 'Expression First', desc: 'Bold and fully expressive', accent: '#7c3aed' },
  /* Q6 — occasion */
  'campus-priority': { title: 'Campus', desc: 'Practical daily campus looks', accent: '#0ea5e9' },
  'work-priority': { title: 'Work', desc: 'Polished work and interview', accent: '#1e293b' },
  'party-priority': { title: 'Parties', desc: 'Night-outs and party style', accent: '#ec4899' },
  'everyday-priority': { title: 'Everyday', desc: 'Versatile everyday outfits', accent: '#10b981' },
  /* Q7 — motivation */
  'versatility-first': { title: 'Versatility', desc: 'Works with many outfits', accent: '#6b7280' },
  'trend-discovery': { title: 'Trend Discovery', desc: 'Helps me try a trend', accent: '#f97316' },
  'statement-pieces': { title: 'Statement', desc: 'Makes a bold statement', accent: '#7c3aed' },
  'quality-first': { title: 'Quality', desc: 'Feels high quality', accent: '#1e293b' },
  /* Q8 — goal */
  'refine-signature': { title: 'Refine', desc: 'Sharpen my signature style', accent: '#1e293b' },
  'experiment-more': { title: 'Experiment', desc: 'Try brand new styles', accent: '#f97316' },
  'build-wardrobe': { title: 'Build', desc: 'Create a versatile wardrobe', accent: '#0ea5e9' },
  'shop-smarter': { title: 'Shop Smart', desc: 'Make smarter purchases', accent: '#10b981' },
};

function getChoiceMeta(choice) {
  const meta = CHOICE_META[choice.id];
  if (meta) return meta;
  /* Graceful fallback — derive from raw label */
  return { title: choice.label, desc: choice.alt || '', accent: '#6b7280' };
}

export default function DNAQuiz() {
  const navigate = useNavigate();
  const { calculateDNA } = useUser();

  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState({});
  const [selected, setSelected] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [retryAnswers, setRetryAnswers] = useState(null);

  const root = useRef(null);
  const reducedMotion = useReducedMotion();

  useGSAP(
    () => {
      if (reducedMotion) return;
      const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });

      tl.from('[data-quiz-text]', { opacity: 0, x: 20, duration: 0.4 });
      tl.from(
        '[data-quiz-choice]',
        { opacity: 0, scale: 0.95, y: 15, duration: 0.35, stagger: 0.08 },
        '-=0.2',
      );
    },
    { scope: root, dependencies: [currentQ, reducedMotion] },
  );

  const question = quizQuestions[currentQ];
  const totalQs = quizQuestions.length;

  async function calculateAndSaveDNA(finalAnswers) {
    setSubmitting(true);
    setSubmitError(null);
    setRetryAnswers(finalAnswers);

    try {
      const payload = quizQuestions.map(
        (quizQuestion) => ({
          question_id: quizQuestion.id,
          choice_id: finalAnswers[quizQuestion.id],
        }),
      );

      await calculateDNA(payload);

      navigate('/dna-result');
    } catch (requestError) {
      setSubmitError(requestError);
    } finally {
      setSubmitting(false);
    }
  }

  function pickChoice(choiceId) {
    setSelected(choiceId);
  }

  async function next() {
    if (selected === null || submitting) {
      return;
    }

    const updatedAnswers = {
      ...answers,
      [question.id]: selected,
    };

    setAnswers(updatedAnswers);

    const isLastQuestion =
      currentQ === quizQuestions.length - 1;

    if (isLastQuestion) {
      await calculateAndSaveDNA(updatedAnswers);
      return;
    }

    setCurrentQ(
      (currentQuestion) => currentQuestion + 1,
    );

    setSelected(null);
  }

  if (submitting) {
    return (
      <div className="screen">
        <div className="page-loading">
          Calculating your Fashion DNA…
        </div>
      </div>
    );
  }

  if (submitError) {
    return (
      <div className="screen">
        <ApiErrorState
          error={submitError}
          title="Fashion DNA calculation failed"
          onRetry={
            retryAnswers
              ? () =>
                calculateAndSaveDNA(
                  retryAnswers,
                )
              : undefined
          }
        />

        <div className="quiz-nav">
          <button
            type="button"
            className="btn-primary"
            onClick={() => setSubmitError(null)}
          >
            Return to quiz
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="screen quiz-shell" ref={root}>
      {/* Decorative wavy lines */}
      <svg className="quiz-deco-lines quiz-deco-tr" viewBox="0 0 200 200" fill="none" aria-hidden="true">
        <path d="M40,0 Q200,30 200,180" stroke="var(--color-primary-soft)" strokeWidth="1" opacity="0.35" />
        <path d="M80,0 Q210,60 195,200" stroke="var(--color-lavender)" strokeWidth="1" opacity="0.3" />
      </svg>
      <svg className="quiz-deco-lines quiz-deco-bl" viewBox="0 0 200 200" fill="none" aria-hidden="true">
        <path d="M0,40 Q30,200 180,200" stroke="var(--color-primary-soft)" strokeWidth="1" opacity="0.35" />
        <path d="M0,80 Q60,210 200,195" stroke="var(--color-lavender)" strokeWidth="1" opacity="0.3" />
      </svg>

      {/* Sparkle clusters */}
      <Sparkle size={14} color="var(--gradient-hero-start)" className="qsp-1" />
      <Sparkle size={10} color="var(--color-lavender)" className="qsp-2" />
      <Sparkle size={18} color="var(--gradient-hero-end)" className="qsp-3" />
      <Sparkle size={12} color="var(--gradient-hero-start)" className="qsp-4" />
      <Sparkle size={16} color="var(--color-lavender)" className="qsp-5" />
      <Sparkle size={10} color="var(--gradient-hero-end)" className="qsp-6" />

      {/* Lavender blob */}
      <div className="quiz-blob" aria-hidden="true" />

      <OnboardingCard
        className="quiz-card-wrapper"
        footer={
          <button
            type="button"
            className="quiz-cta"
            disabled={selected === null || submitting}
            onClick={next}
          >
            <span>{currentQ === totalQs - 1 ? 'SEE MY DNA' : 'NEXT'}</span>
            <ArrowRight size={20} aria-hidden="true" />
          </button>
        }
      >
        {/* 8-segment progress bar */}
        <div className="quiz-prog-bar">
          {Array.from({ length: totalQs }, (_, i) => (
            <div
              key={i}
              className={`quiz-seg ${i <= currentQ ? 'filled' : ''}`}
            />
          ))}
        </div>

        <div className="quiz-q-num" data-quiz-text>
          Question {currentQ + 1} of {totalQs}
        </div>

        <h1 className="quiz-question" data-quiz-text>
          {question.question}
        </h1>

        {/* Answer cards */}
        <div className="quiz-cards-grid">
          {question.choices.map((choice) => {
            const meta = getChoiceMeta(choice);
            const isSel = selected === choice.id;

            return (
              <button
                type="button"
                key={choice.id}
                data-quiz-choice
                className={`quiz-option-card ${isSel ? 'sel' : ''}`}
                style={{ '--card-accent': meta.accent }}
                aria-pressed={isSel}
                onClick={() => pickChoice(choice.id)}
              >
                {/* Selection indicator */}
                <span className="quiz-card-check" aria-hidden="true">
                  {isSel
                    ? <CheckCircle size={22} />
                    : <span className="quiz-card-ring" />}
                </span>

                {/* Illustration */}
                <div className="quiz-card-img-wrap">
                  <img
                    className="quiz-card-img"
                    src={choice.image}
                    alt={choice.alt}
                    draggable="false"
                    onError={(e) => {
                      e.currentTarget.onerror = null;
                      e.currentTarget.src = '/quiz/fallback.webp';
                    }}
                  />
                </div>

                {/* Optional swatch row */}
                {meta.swatches && (
                  <div className="quiz-card-swatches">
                    {meta.swatches.map((hex) => (
                      <span
                        key={hex}
                        className="quiz-swatch"
                        style={{ background: hex }}
                        aria-hidden="true"
                      />
                    ))}
                  </div>
                )}

                {/* Text content */}
                <div className="quiz-card-body">
                  <div className="quiz-card-title">{meta.title}</div>
                  <div className="quiz-card-desc">{meta.desc}</div>
                  <div className="quiz-card-pill">
                    {choice.label}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </OnboardingCard>
    </div>
  );
}
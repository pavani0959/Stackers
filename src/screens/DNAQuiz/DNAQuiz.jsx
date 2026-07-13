import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { quizQuestions } from '../../data/quizQuestions';
import { apiRequest } from '../../api/client';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';
import '../../styles/DNAQuiz.css';

export default function DNAQuiz() {
  const navigate = useNavigate();
  const { updateDNA, updateUser } = useUser();
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState(Array(quizQuestions.length).fill(null));
  const [selected, setSelected] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [retryTags, setRetryTags] = useState(null);

  const question = quizQuestions[currentQ];
  const progress = Math.round(((currentQ + 1) / quizQuestions.length) * 100);

  async function calculateAndSaveDNA(tags) {
    setSubmitting(true);
    setSubmitError(null);
    setRetryTags(tags);

    try {
      const calculatedDNA = await apiRequest(
        '/api/dna/calculate',
        {
          method: 'POST',
          body: JSON.stringify({
            tags,
          }),
        },
      );

      if (
        !calculatedDNA?.dna ||
        typeof calculatedDNA.dna !== 'object'
      ) {
        throw new Error(
          'The server returned an invalid Fashion DNA result.',
        );
      }

      const orderedDNA = Object.entries(
        calculatedDNA.dna,
      ).sort(
        (left, right) =>
          right[1] - left[1],
      );

      /*
       * These are temporary presentation fields only.
       * They are not saved in localStorage.
       */
      updateUser({
        dnaTopBars:
          calculatedDNA.topBars ?? [],

        identityDesc:
          calculatedDNA.identity?.desc ??
          '',
      });

      /*
       * updateDNA creates a new backend version.
       */
      await updateDNA({
        dna_vector:
          calculatedDNA.dna,

        primary_identity:
          orderedDNA[0]?.[0] ??
          'personal_style',

        secondary_identity:
          orderedDNA[1]?.[0] ??
          null,

        profile_confidence:
          calculatedDNA.confidence ??
          65,

        source: 'quiz',

        model_version:
          'dna-v1',
      });

      navigate('/dna-result');
    } catch (error) {
      setSubmitError(error);
    } finally {
      setSubmitting(false);
    }
  }

  const pickChoice = (choice, idx) => {
    setSelected(idx);
    const newAnswers = [...answers];
    newAnswers[currentQ] = choice;
    setAnswers(newAnswers);
  };

  const next = async () => {
    if (selected === null || submitting) {
      return;
    }

    if (currentQ < quizQuestions.length - 1) {
      setCurrentQ((currentQuestion) => currentQuestion + 1);
      setSelected(null);
      return;
    }

    const allTags = [];

    answers.forEach((answer) => {
      if (answer?.tags) {
        allTags.push(...answer.tags);
      }
    });

    await calculateAndSaveDNA(allTags);
  };

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
            retryTags
              ? () => calculateAndSaveDNA(retryTags)
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

    <div className="screen quiz-screen">
      <div className="quiz-hdr">
        <div className="quiz-prog-wrap">
          <div className="quiz-prog-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="quiz-q-num">Question {currentQ + 1} of {quizQuestions.length}</div>
        <div className="quiz-question">{question.question}</div>
      </div>

      <div className="choices-grid">
        {question.choices.map((choice, idx) => (
          <div
            key={idx}
            className={`choice-card ${selected === idx ? 'sel' : ''}`}
            onClick={() => pickChoice(choice, idx)}
          >
            <div className="choice-bg" style={{ background: choice.bg }}>
              <div className="choice-label">{choice.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="quiz-nav">
        <button
          type="button"
          className="btn-primary"
          disabled={selected === null || submitting}
          style={{
            opacity: selected === null || submitting ? 0.45 : 1,
            pointerEvents: selected === null || submitting ? 'none' : 'auto',
          }}
          onClick={next}
        >
          {submitting
            ? 'Calculating…'
            : currentQ === quizQuestions.length - 1
              ? 'See My DNA →'
              : 'Next →'}
        </button>
      </div>
    </div>
  );
}

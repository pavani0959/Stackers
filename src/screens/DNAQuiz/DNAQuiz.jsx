import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { quizQuestions } from '../../data/quizQuestions';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';
import '../../styles/DNAQuiz.css';

export default function DNAQuiz() {
  const navigate = useNavigate();
  const { calculateDNA } = useUser();

  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState({});
  const [selected, setSelected] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [retryAnswers, setRetryAnswers] = useState(null);

  const question = quizQuestions[currentQ];

  const progress = Math.round(
    ((currentQ + 1) / quizQuestions.length) * 100,
  );

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
    <div className="screen quiz-screen">
      <div className="quiz-hdr">
        <div className="quiz-prog-wrap">
          <div
            className="quiz-prog-fill"
            style={{
              width: `${progress}%`,
            }}
          />
        </div>

        <div className="quiz-q-num">
          Question {currentQ + 1} of{' '}
          {quizQuestions.length}
        </div>

        <div className="quiz-question">
          {question.question}
        </div>
      </div>

      <div className="choices-grid">
        {question.choices.map((choice) => (
          <button
            type="button"
            key={choice.id}
            className={`choice-card ${
              selected === choice.id
                ? 'sel'
                : ''
            }`}
            aria-pressed={
              selected === choice.id
            }
            onClick={() =>
              pickChoice(choice.id)
            }
          >
            <div className="choice-bg">
              <img
                className="dna-choice-image"
                src={choice.image}
                alt={choice.alt}
                draggable="false"
              />

              <div className="choice-label">
                {choice.label}
              </div>
            </div>
          </button>
        ))}
      </div>

      <div className="quiz-nav">
        <button
          type="button"
          className="btn-primary"
          disabled={
            selected === null || submitting
          }
          onClick={next}
        >
          {currentQ ===
          quizQuestions.length - 1
            ? 'See My DNA →'
            : 'Next →'}
        </button>
      </div>
    </div>
  );
}
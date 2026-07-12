import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { quizQuestions } from '../../data/quizQuestions';
import '../../styles/DNAQuiz.css';

export default function DNAQuiz() {
  const navigate = useNavigate();
  const { updateUser } = useUser();
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState(Array(quizQuestions.length).fill(null));
  const [selected, setSelected] = useState(null);

  const question = quizQuestions[currentQ];
  const progress = Math.round(((currentQ + 1) / quizQuestions.length) * 100);

  const pickChoice = (choice, idx) => {
    setSelected(idx);
    const newAnswers = [...answers];
    newAnswers[currentQ] = choice;
    setAnswers(newAnswers);
  };

  const next = () => {
    if (selected === null) return;
    if (currentQ < quizQuestions.length - 1) {
      setCurrentQ(c => c + 1);
      setSelected(null);
    } else {
      // Gather all tags from selected answers
      const allTags = [];
      answers.forEach(ans => {
        if (ans && ans.tags) {
          allTags.push(...ans.tags);
        }
      });

      // Call the real ML Backend
      fetch('http://localhost:8000/api/dna/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tags: allTags })
      })
      .then(res => res.json())
      .then(data => {
        const { dna, identity, topBars } = data;
        const confidence = Math.round(Object.values(dna).reduce((a, b) => a + b, 0) / Math.max(Object.keys(dna).length, 1) + 20);
        updateUser({
          dna,
          dnaTopBars: topBars,
          identityName: identity.name,
          identityDesc: identity.desc,
          confidenceScore: Math.min(confidence, 94),
          hasCompletedQuiz: true,
        });
        navigate('/dna-result');
      })
      .catch(err => {
        console.error("Failed to run ML model:", err);
        // Fallback or error state could be handled here
      });
    }
  };

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
          className="btn-primary"
          style={{ opacity: selected === null ? 0.45 : 1, pointerEvents: selected === null ? 'none' : 'auto' }}
          onClick={next}
        >
          {currentQ === quizQuestions.length - 1 ? 'See My DNA →' : 'Next →'}
        </button>
      </div>
    </div>
  );
}

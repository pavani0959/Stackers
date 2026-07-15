import {
  fireEvent,
  render,
  screen,
  waitFor,
} from '@testing-library/react';
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';
import DNAQuiz from './DNAQuiz';
import {
  quizQuestions,
} from '../../data/quizQuestions';

const mocks = vi.hoisted(() => ({
  calculateDNA: vi.fn(),
  navigate: vi.fn(),
}));

vi.mock(
  '../../context/useUser',
  () => ({
    useUser: () => ({
      calculateDNA:
        mocks.calculateDNA,
    }),
  }),
);

vi.mock(
  'react-router-dom',
  async () => {
    const actual = await vi.importActual(
      'react-router-dom',
    );

    return {
      ...actual,
      useNavigate: () =>
        mocks.navigate,
    };
  },
);

describe('DNAQuiz', () => {
  beforeEach(() => {
    mocks.calculateDNA.mockReset();
    mocks.navigate.mockReset();

    mocks.calculateDNA.mockResolvedValue({
      profile_id:
        '0a984b56-eccc-4f12-8af9-5806a4912988',
      version: 1,
    });
  });

  it('contains exactly eight visual questions', () => {
    expect(quizQuestions).toHaveLength(8);

    for (
      const question
      of quizQuestions
    ) {
      expect(question.id).toBeTruthy();
      expect(question.choices.length)
        .toBeGreaterThanOrEqual(4);

      for (
        const choice
        of question.choices
      ) {
        expect(choice.id).toBeTruthy();
        expect(choice.label).toBeTruthy();
        expect(choice.image).toMatch(
          /^\/quiz\//,
        );
        expect(choice.alt).toBeTruthy();
      }
    }
  });

  it('submits one question ID and choice ID for every question', async () => {
    render(<DNAQuiz />);

    const expectedAnswers = [];

    for (
      let index = 0;
      index < quizQuestions.length;
      index += 1
    ) {
      const question =
        quizQuestions[index];

      const selectedChoice =
        question.choices[0];

      expect(
        screen.getByText(
          question.question,
        ),
      ).toBeInTheDocument();

      const choiceLabel =
        screen.getByText(
          selectedChoice.label,
        );

      const choiceButton =
        choiceLabel.closest('button');

      expect(choiceButton).not.toBeNull();

      fireEvent.click(choiceButton);

      expectedAnswers.push({
        question_id:
          question.id,
        choice_id:
          selectedChoice.id,
      });

      const isLastQuestion =
        index ===
        quizQuestions.length - 1;

      fireEvent.click(
        screen.getByRole(
          'button',
          {
            name: isLastQuestion
              ? /see my dna/i
              : /next/i,
          },
        ),
      );
    }

    await waitFor(() => {
      expect(
        mocks.calculateDNA,
      ).toHaveBeenCalledTimes(1);
    });

    expect(
      mocks.calculateDNA,
    ).toHaveBeenCalledWith(
      expectedAnswers,
    );

    expect(
      mocks.navigate,
    ).toHaveBeenCalledWith(
      '/dna-result',
    );
  });

  it('does not submit before all eight questions are completed', () => {
    render(<DNAQuiz />);

    expect(
      screen.getByRole(
        'button',
        {
          name: /next/i,
        },
      ),
    ).toBeDisabled();

    expect(
      mocks.calculateDNA,
    ).not.toHaveBeenCalled();
  });
});
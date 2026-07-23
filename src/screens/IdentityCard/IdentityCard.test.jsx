import {
  fireEvent,
  render,
  screen,
} from '@testing-library/react';
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest';
import IdentityCard from './IdentityCard';

const mocks = vi.hoisted(() => ({
  navigate: vi.fn(),
}));

const mockUser = {
  name: 'Test Style Explorer',
  createdAt:
    '2026-07-15T10:00:00',
  identityName:
    'Minimalist Campus Casual',
  identityDescription:
    'Clean, versatile and campus-ready.',
  dna: {
    minimalist: 55,
    campusCasual: 30,
    quietLuxury: 15,
  },
  profileConfidence: 73,
  confidenceBreakdown: {
    quiz_completeness: 40,
    answer_consistency: 13,
    preference_coverage: 20,
    behavior_evidence: 0,
  },
  evidence: {
    quiz_answers: 8,
    behavior_events: 0,
  },
  dnaVersion: 2,
  budgetMin: 500,
  budgetMax: 1500,
  occasionPriorities: {
    campus: 1,
    casual: 0.7,
  },
  occasions: [
    'campus',
    'casual',
  ],
  colours: [
    'black',
    'white',
    'beige',
  ],
  fitPreferences: [
    'relaxed',
  ],
  fashionGoal:
    'Make smarter purchase decisions',
};

vi.mock(
  '../../context/useUser',
  () => ({
    useUser: () => ({
      user: mockUser,
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

describe('IdentityCard', () => {
  beforeEach(() => {
    mocks.navigate.mockReset();
  });

  it('renders the persisted identity without a buildDnaBars error', () => {
    expect(() => {
      render(<IdentityCard />);
    }).not.toThrow();

    expect(
      screen.getByText(
        'Test Style Explorer',
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        'Minimalist Campus Casual',
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        'Clean, versatile and campus-ready.',
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText('73%'),
    ).toBeInTheDocument();
  });

  it('shows the confidence explanation and evidence', () => {
    render(<IdentityCard />);

    expect(
      screen.getByText(
        /quiz completeness:/i,
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        /answer consistency:/i,
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        /preference coverage:/i,
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        /behaviour evidence:/i,
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        /quiz answers:/i,
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        /behaviour events:/i,
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        /fashion dna version/i,
      ),
    ).toBeInTheDocument();
  });

  it('opens the Profile editor when Edit Identity is clicked', () => {
    render(<IdentityCard />);

    fireEvent.click(
      screen.getByRole(
        'button',
        {
          name: /edit identity/i,
        },
      ),
    );

    expect(
      mocks.navigate,
    ).toHaveBeenCalledWith(
      '/profile',
    );
  });
});
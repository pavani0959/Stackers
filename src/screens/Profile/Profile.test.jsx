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
import {
  MemoryRouter,
} from 'react-router-dom';
import Profile from './Profile';

const mocks = vi.hoisted(() => ({
  updateIdentity: vi.fn(),
  updatePreferences: vi.fn(),
}));

const mockUser = {
  name: 'Original Name',
  gender: 'female',
  age: 21,

  budget: 'campus-casual',
  budgetTier: 'campus-casual',
  budgetMin: 500,
  budgetMax: 1500,

  occasions: [
    'campus',
    'casual',
  ],

  occasionPriorities: {
    campus: 1,
    casual: 0.7,
  },

  colours: [
    'black',
    'white',
  ],

  brands: [
    'Mango',
  ],

  aesthetics: [
    'minimalist',
  ],

  fitPreferences: [
    'relaxed',
  ],

  comfortExpressionBalance: 0.35,

  fashionGoal:
    'Build a versatile wardrobe',

  dna: {
    minimalist: 60,
    campusCasual: 40,
  },

  identityName:
    'Minimalist Campus Casual',

  profileConfidence: 72,
};

vi.mock(
  '../../context/useUser',
  () => ({
    useUser: () => ({
      user: mockUser,
      updateIdentity:
        mocks.updateIdentity,
      updatePreferences:
        mocks.updatePreferences,
    }),
  }),
);

vi.mock(
  '../../components/BottomNav/BottomNav',
  () => ({
    default: () => (
      <div data-testid="bottom-nav" />
    ),
  }),
);

describe('Profile', () => {
  beforeEach(() => {
    mocks.updateIdentity.mockReset();
    mocks.updatePreferences.mockReset();

    mocks.updateIdentity.mockResolvedValue(
      {
        name: 'Updated Name',
      },
    );

    mocks.updatePreferences.mockResolvedValue(
      {},
    );
  });

  function renderProfile() {
    return render(
      <MemoryRouter>
        <Profile />
      </MemoryRouter>,
    );
  }

  it('renders the existing persisted profile', () => {
    renderProfile();

    expect(
      screen.getByText(
        'Original Name',
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        'Minimalist Campus Casual',
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText('72%'),
    ).toBeInTheDocument();
  });

  it('persists identity and canonical snake_case preference fields', async () => {
    renderProfile();

    fireEvent.click(
      screen.getByRole(
        'button',
        {
          name: /^edit$/i,
        },
      ),
    );

    const nameInput =
      screen.getByPlaceholderText(
        /your name/i,
      );

    fireEvent.change(
      nameInput,
      {
        target: {
          value: 'Updated Name',
        },
      },
    );

    fireEvent.click(
      screen.getByRole(
        'button',
        {
          name:
            /₹1,500–₹3,000/i,
        },
      ),
    );

    fireEvent.click(
      screen.getByRole(
        'button',
        {
          name: /^party$/i,
        },
      ),
    );

    const goalSelects =
      screen.getAllByRole(
        'combobox',
      );

    const fashionGoalSelect =
      goalSelects[
        goalSelects.length - 1
      ];

    fireEvent.change(
      fashionGoalSelect,
      {
        target: {
          value:
            'Make smarter purchase decisions',
        },
      },
    );

    fireEvent.click(
      screen.getByRole(
        'button',
        {
          name: /save changes/i,
        },
      ),
    );

    await waitFor(() => {
      expect(
        mocks.updateIdentity,
      ).toHaveBeenCalledWith({
        name: 'Updated Name',
      });
    });

    await waitFor(() => {
      expect(
        mocks.updatePreferences,
      ).toHaveBeenCalledTimes(1);
    });

    expect(
      mocks.updatePreferences,
    ).toHaveBeenCalledWith(
      expect.objectContaining({
        budget_min: 1500,
        budget_max: 3000,
        budget_tier: 'mid-range',

        preferred_occasions:
          expect.arrayContaining([
            'campus',
            'casual',
            'party',
          ]),

        preferred_colours:
          expect.arrayContaining([
            'black',
            'white',
          ]),

        preferred_brands:
          expect.arrayContaining([
            'Mango',
          ]),

        preferred_aesthetics:
          expect.arrayContaining([
            'minimalist',
          ]),

        fit_preferences:
          expect.arrayContaining([
            'relaxed',
          ]),

        comfort_priority: 0.65,
        trend_openness: 0.35,

        comfort_expression_balance:
          0.35,

        occasion_priorities: {
          campus: 1,
          casual: 0.7,
          party: 0.7,
        },

        fashion_goal:
          'Make smarter purchase decisions',
      }),
    );
  });

  it('does not call the API when the name is empty', async () => {
    renderProfile();

    fireEvent.click(
      screen.getByRole(
        'button',
        {
          name: /^edit$/i,
        },
      ),
    );

    fireEvent.change(
      screen.getByPlaceholderText(
        /your name/i,
      ),
      {
        target: {
          value: '   ',
        },
      },
    );

    fireEvent.click(
      screen.getByRole(
        'button',
        {
          name: /save changes/i,
        },
      ),
    );

    expect(
      await screen.findByText(
        /please enter your name/i,
      ),
    ).toBeInTheDocument();

    expect(
      mocks.updateIdentity,
    ).not.toHaveBeenCalled();

    expect(
      mocks.updatePreferences,
    ).not.toHaveBeenCalled();
  });
});
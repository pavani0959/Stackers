import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { decisionFixture } from '../../testDecisionFixture';
import Home from './Home';

const mocks = vi.hoisted(() => ({
  getDecisionFeed: vi.fn(),
  updateUser: vi.fn(),
  addToWishlist: vi.fn(),
}));

vi.mock('../../api/decisions', () => ({
  getDecisionFeed: mocks.getDecisionFeed,
}));

vi.mock('../../context/useUser', () => ({
  useUser: () => ({
    user: {
      id: 1,
      name: 'Test User',
      moodState: 'quiet',
      occasions: ['campus'],
      wishlist: [],
    },
    profileLoading: false,
    updateUser: mocks.updateUser,
    addToWishlist: mocks.addToWishlist,
  }),
}));

vi.mock('../../components/BottomNav/BottomNav', () => ({
  default: () => null,
}));

describe('Home decision feed', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.getDecisionFeed.mockResolvedValue({
      session_id: 9,
      model_version: 'decision-v1.0.0',
      profile_version: 3,
      items: [decisionFixture],
    });
  });

  it('requests a server-owned feed without sending user_profile', async () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>,
    );

    expect(
      await screen.findByText('Minimal Campus Shirt'),
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(mocks.getDecisionFeed).toHaveBeenCalledTimes(1);
    });
    const request = mocks.getDecisionFeed.mock.calls[0][0];
    expect(request).toEqual({
      limit: 20,
      antiTrend: false,
      context: { occasion: 'campus', vibe: 'quiet' },
    });
    expect(JSON.stringify(request)).not.toContain('user_profile');
  });

  it('re-fetches feed when a vibe is clicked', async () => {
    const { fireEvent } = await import('@testing-library/react');
    
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Minimal Campus Shirt')).toBeInTheDocument();
    
    // Initial fetch
    expect(mocks.getDecisionFeed).toHaveBeenCalledTimes(1);
    
    const boldButton = screen.getByRole('button', { name: /bold/i });
    fireEvent.click(boldButton);
    
    await waitFor(() => {
      expect(mocks.getDecisionFeed).toHaveBeenCalledTimes(2);
    });
    
    const secondRequest = mocks.getDecisionFeed.mock.calls[1][0];
    expect(secondRequest.context.vibe).toBe('bold');
  });
});

import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { decisionFixture } from '../../testDecisionFixture';
import FashionMemory from './FashionMemory';

const mocks = vi.hoisted(() => ({
  getDecisionMemory: vi.fn(),
}));

vi.mock('../../api/decisions', () => ({
  getDecisionMemory: mocks.getDecisionMemory,
}));

vi.mock('../../components/BottomNav/BottomNav', () => ({
  default: () => null,
}));

describe('FashionMemory', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.getDecisionMemory.mockResolvedValue({
      items: [
        {
          event: {
            id: 100,
            event_type: 'purchase',
            occurred_at: '2026-07-16T12:00:00Z',
            metadata: {},
          },
          decision: decisionFixture,
        },
      ],
    });
  });

  it('renders the stored recommendation-time score', async () => {
    render(
      <MemoryRouter>
        <FashionMemory />
      </MemoryRouter>,
    );

    expect(
      await screen.findByText('88% recommendation-time match'),
    ).toBeInTheDocument();
    expect(screen.getByText('purchase')).toBeInTheDocument();
    expect(mocks.getDecisionMemory).toHaveBeenCalledTimes(1);
  });
});

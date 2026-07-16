import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import FashionMemory from './FashionMemory';

// ------------------------------------------------------------------
// Phase 6: FashionMemory now fetches /api/memory/timeline
// Mock the new API (getMemoryTimeline from ../../api/events)
// ------------------------------------------------------------------

const mocks = vi.hoisted(() => ({
  getMemoryTimeline: vi.fn(),
}));

vi.mock('../../api/events', () => ({
  getMemoryTimeline: mocks.getMemoryTimeline,
  createUserEvent: vi.fn(),
  getUserEvents: vi.fn(),
  checkRegret: vi.fn(),
}));

vi.mock('../../components/BottomNav/BottomNav', () => ({
  default: () => null,
}));

describe('FashionMemory', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows empty state when no timeline events exist', async () => {
    mocks.getMemoryTimeline.mockResolvedValue({ timeline: [] });

    render(
      <MemoryRouter>
        <FashionMemory />
      </MemoryRouter>,
    );

    expect(
      await screen.findByText('No events recorded yet.'),
    ).toBeInTheDocument();
    expect(mocks.getMemoryTimeline).toHaveBeenCalledTimes(1);
  });

  it('renders a timeline event with product info', async () => {
    mocks.getMemoryTimeline.mockResolvedValue({
      timeline: [
        {
          id: 1,
          type: 'cart_add',
          date: '2026-07-16T12:00:00Z',
          metadata: { size: 'M', match_score: 88 },
          product: {
            id: 42,
            name: 'Minimal White Tee',
            image: 'https://example.com/tee.jpg',
            price: 1299,
          },
        },
      ],
    });

    render(
      <MemoryRouter>
        <FashionMemory />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Minimal White Tee')).toBeInTheDocument();
    // event label is now rendered as '🛒 Added to Cart'
    expect(screen.getByText('🛒 Added to Cart')).toBeInTheDocument();
    expect(mocks.getMemoryTimeline).toHaveBeenCalledTimes(1);
  });

  it('renders the match score from event metadata when present', async () => {
    mocks.getMemoryTimeline.mockResolvedValue({
      timeline: [
        {
          id: 2,
          type: 'keep',
          date: '2026-07-16T13:00:00Z',
          metadata: { match_score: 92 },
          product: {
            id: 10,
            name: 'Streetwear Hoodie',
            image: 'https://example.com/hoodie.jpg',
            price: 2499,
          },
        },
      ],
    });

    render(
      <MemoryRouter>
        <FashionMemory />
      </MemoryRouter>,
    );

    expect(await screen.findByText('Streetwear Hoodie')).toBeInTheDocument();
    expect(screen.getByText('92% match')).toBeInTheDocument();
  });
});

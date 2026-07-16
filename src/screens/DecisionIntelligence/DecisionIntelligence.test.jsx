import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { decisionFixture } from '../../testDecisionFixture';
import DecisionIntelligence from './DecisionIntelligence';

const mocks = vi.hoisted(() => ({
  getDecision: vi.fn(),
  addToCart: vi.fn(),
  createUserEvent: vi.fn(() => Promise.resolve()),
}));

vi.mock('../../api/decisions', () => ({
  getDecision: mocks.getDecision,
}));

vi.mock('../../context/useUser', () => ({
  useUser: () => ({
    addToCart: mocks.addToCart,
    createUserEvent: mocks.createUserEvent,
  }),
}));

function renderDecision() {
  return render(
    <MemoryRouter
      initialEntries={[`/decision/${decisionFixture.snapshot_id}`]}
    >
      <Routes>
        <Route
          path="/decision/:id"
          element={<DecisionIntelligence />}
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe('DecisionIntelligence', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.getDecision.mockResolvedValue(decisionFixture);
  });

  it('loads only the stored snapshot and renders stored evidence', async () => {
    renderDecision();

    expect(await screen.findByText('88')).toBeInTheDocument();
    expect(
      screen.getByText(/Alignment with your Minimalist DNA/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText('Similar item already in your wardrobe'),
    ).toBeInTheDocument();
    expect(mocks.getDecision).toHaveBeenCalledWith(
      decisionFixture.snapshot_id,
    );
  });

  it('contains no fabricated community or return-rate claim', async () => {
    renderDecision();
    await screen.findByText('88');

    expect(screen.queryByText(/users loved/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/returned 60%/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/real eyes/i)).not.toBeInTheDocument();
  });
});

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { decisionFixture } from '../../testDecisionFixture';
import ProductDetail from './ProductDetail';

const mocks = vi.hoisted(() => ({
  createProductDecision: vi.fn(),
  getDecision: vi.fn(),
  addToCart: vi.fn(),
  addToWishlist: vi.fn(),
  createUserEvent: vi.fn(() => Promise.resolve()),
}));

vi.mock('../../api/decisions', () => ({
  createProductDecision: mocks.createProductDecision,
  getDecision: mocks.getDecision,
}));

vi.mock('../../context/useUser', () => ({
  useUser: () => ({
    user: {
      id: 1,
      occasions: ['campus'],
      wishlist: [],
    },
    profileLoading: false,
    addToCart: mocks.addToCart,
    addToWishlist: mocks.addToWishlist,
    createUserEvent: mocks.createUserEvent,
  }),
}));

vi.mock('../../components/BottomNav/BottomNav', () => ({
  default: () => null,
}));

function renderProductDetail(initialEntry) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/product/:id" element={<ProductDetail />} />
        <Route path="/decision/:id" element={<div>Decision route</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('ProductDetail decision snapshots', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocks.getDecision.mockResolvedValue(decisionFixture);
    mocks.createProductDecision.mockResolvedValue(decisionFixture);
  });

  it('uses an existing snapshot from the URL', async () => {
    renderProductDetail(
      `/product/1?decision=${decisionFixture.snapshot_id}`,
    );

    expect((await screen.findAllByText(/88/i)).length).toBeGreaterThan(0);
    expect(mocks.getDecision).toHaveBeenCalledWith(
      decisionFixture.snapshot_id,
    );
    expect(mocks.createProductDecision).not.toHaveBeenCalled();
  });

  it('creates one snapshot when opened directly', async () => {
    renderProductDetail('/product/1');

    await waitFor(() => {
      expect(mocks.createProductDecision).toHaveBeenCalledTimes(1);
    });
    expect(mocks.createProductDecision).toHaveBeenCalledWith(1, {
      occasion: 'campus',
    });
  });

  it('navigates to Decision Intelligence using the snapshot UUID', async () => {
    renderProductDetail(
      `/product/1?decision=${decisionFixture.snapshot_id}`,
    );

    fireEvent.click(
      await screen.findByRole('button', {
        name: /detailed match analysis/i,
      }),
    );

    expect(screen.getByText('Decision route')).toBeInTheDocument();
  });
});

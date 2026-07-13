import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { AppProviders } from './providers';

function BrokenComponent() {
  throw new Error('Intentional render failure');
}

it('shows the shared render error page', () => {
  const consoleSpy = vi
    .spyOn(console, 'error')
    .mockImplementation(() => {});

  render(
    <AppProviders>
      <BrokenComponent />
    </AppProviders>,
  );

  expect(
    screen.getByRole('alert'),
  ).toHaveTextContent('Something went wrong');

  consoleSpy.mockRestore();
});

describe('AppProviders', () => {
  it('renders application children', () => {
    render(
      <AppProviders>
        <p>Provider smoke test</p>
      </AppProviders>,
    );

    expect(screen.getByText('Provider smoke test')).toBeInTheDocument();
  });
});

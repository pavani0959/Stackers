import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { AppProviders } from './providers';

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

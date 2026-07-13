import { Component } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './queryClient';

class AppErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('[render-error]', error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <main
          role="alert"
          style={{
            maxWidth: 560,
            margin: '80px auto',
            padding: 24,
            fontFamily: 'var(--font-family)',
          }}
        >
          <h1>Something went wrong</h1>
          <p>Please reload the app. Your saved Fashion DNA is still stored locally.</p>
          <button type="button" onClick={() => window.location.reload()}>
            Reload app
          </button>
        </main>
      );
    }

    return this.props.children;
  }
}

export function AppProviders({ children }) {
  return (
    <AppErrorBoundary>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </AppErrorBoundary>
  );
}

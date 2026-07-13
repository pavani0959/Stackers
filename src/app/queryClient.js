import {
  MutationCache,
  QueryCache,
  QueryClient,
} from '@tanstack/react-query';

function reportServerError(error) {
  console.error('[server-error]', error);
}

function shouldRetry(failureCount, error) {
  if (failureCount >= 2) return false;
  return !error?.status || error.status >= 500;
}

export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: reportServerError,
  }),
  mutationCache: new MutationCache({
    onError: reportServerError,
  }),
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: shouldRetry,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: false,
    },
  },
});

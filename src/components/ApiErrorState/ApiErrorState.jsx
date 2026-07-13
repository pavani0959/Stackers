import './ApiErrorState.css';

export default function ApiErrorState({
  error,
  title = 'Something went wrong',
  onRetry,
}) {
  const message =
    error?.message ||
    'The requested information could not be loaded. Please try again.';

  return (
    <div className="api-error-state" role="alert">
      <div className="api-error-state__icon" aria-hidden="true">
        !
      </div>

      <h2 className="api-error-state__title">{title}</h2>

      <p className="api-error-state__message">{message}</p>

      {onRetry && (
        <button
          type="button"
          className="api-error-state__retry"
          onClick={onRetry}
        >
          Try again
        </button>
      )}
    </div>
  );
}
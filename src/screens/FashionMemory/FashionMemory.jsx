import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDecisionMemory } from '../../api/decisions';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';
import BottomNav from '../../components/BottomNav/BottomNav';
import '../../styles/FashionMemory.css';

export default function FashionMemory() {
  const navigate = useNavigate();
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadMemory() {
      setLoading(true);
      setError(null);
      try {
        const data = await getDecisionMemory();
        if (!cancelled) {
          setEntries(data.items);
        }
      } catch (requestError) {
        if (!cancelled) {
          setError(requestError);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadMemory();
    return () => {
      cancelled = true;
    };
  }, [retryKey]);

  if (loading) {
    return <div className="screen-center">Loading Fashion Memory…</div>;
  }

  if (error) {
    return (
      <ApiErrorState
        error={error}
        title="Fashion Memory could not be loaded"
        onRetry={() => setRetryKey((value) => value + 1)}
      />
    );
  }

  return (
    <div className="screen fm-screen">
      <header className="fm-hdr">
        <div className="fm-back-row">
          <button type="button" className="back-btn" onClick={() => navigate('/home')}>
            ←
          </button>
          <div>
            <h1 className="fm-title">Fashion Memory</h1>
            <p className="fm-sub">
              Stored recommendation-time evidence for purchases, keeps and
              returns.
            </p>
          </div>
        </div>
      </header>

      <main className="fm-body">
        <p className="month-label">Your recorded decisions</p>

        {entries.length === 0 ? (
          <div className="fm-empty">
            <p>No purchase, keep or return event is linked to a decision yet.</p>
            <p>
              A memory entry appears after checkout records a purchase with
              the recommendation item ID stored in the cart.
            </p>
          </div>
        ) : (
          entries.map(({ event, decision }) => {
            const product = decision.product;
            const firstSignal = decision.regret_signals[0];
            return (
              <article
                className="mem-item"
                key={`${event.id}-${decision.snapshot_id}`}
                onClick={() => navigate(
                  `/product/${product.id}?decision=${decision.snapshot_id}`,
                )}
              >
                <div className="mem-top">
                  <img
                    className="mem-img"
                    src={product.image}
                    alt={product.name}
                  />
                  <div className="mem-info">
                    <span className="mem-date">
                      {new Date(event.occurred_at).toLocaleDateString('en-IN')}
                    </span>
                    <strong className="mem-name">{product.name}</strong>
                    <span className="mem-price">
                      ₹{product.price.toLocaleString('en-IN')}
                    </span>
                    <span className="mem-occ">{event.event_type}</span>
                  </div>
                </div>

                <div className="mem-bottom">
                  <p className="mem-reason">
                    “{decision.explanation.summary}”
                  </p>
                  <p className={`mem-dna ${decision.overall_score >= 80 ? 'good' : 'warn'}`}>
                    {decision.overall_score}% recommendation-time match
                  </p>
                  {firstSignal && (
                    <p className="mem-signal">
                      {firstSignal.title}: {firstSignal.detail}
                    </p>
                  )}
                  <small>
                    Model {decision.model_version} · Profile v{decision.profile_version}
                  </small>
                </div>
              </article>
            );
          })
        )}
      </main>

      <BottomNav />
    </div>
  );
}

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMemoryTimeline } from '../../api/events';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';
import BottomNav from '../../components/BottomNav/BottomNav';
import '../../styles/FashionMemory.css';

export default function FashionMemory() {
  const navigate = useNavigate();
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadMemory() {
      setLoading(true);
      setError(null);
      try {
        const data = await getMemoryTimeline();
        if (!cancelled) {
          setTimeline(data.timeline);
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
              Your style evolution across saves, carts, returns, and keeps.
            </p>
          </div>
        </div>
      </header>

      <main className="fm-body">
        <p className="month-label">Your timeline</p>

        {timeline.length === 0 ? (
          <div className="fm-empty">
            <p>No events recorded yet.</p>
            <p>
              Events appear as you interact with the app (save, cart, return, etc.).
            </p>
          </div>
        ) : (
          timeline.map((item) => {
            const product = item.product;
            return (
              <article
                className="mem-item"
                key={item.id}
                onClick={() => product ? navigate(`/product/${product.id}`) : null}
              >
                {product && (
                  <div className="mem-top">
                    <img
                      className="mem-img"
                      src={product.image}
                      alt={product.name}
                    />
                    <div className="mem-info">
                      <span className="mem-date">
                        {new Date(item.date).toLocaleDateString('en-IN')}
                      </span>
                      <strong className="mem-name">{product.name}</strong>
                      <span className="mem-price">
                        ₹{product.price.toLocaleString('en-IN')}
                      </span>
                      <span className={`mem-occ event-${item.type}`}>{item.type.toUpperCase()}</span>
                    </div>
                  </div>
                )}
                
                {item.metadata && Object.keys(item.metadata).length > 0 && (
                  <div className="mem-bottom">
                    <pre style={{ fontSize: '0.7rem', margin: 0, color: 'var(--ink-500)'}}>
                      {JSON.stringify(item.metadata, null, 2)}
                    </pre>
                  </div>
                )}
              </article>
            );
          })
        )}
      </main>

      <BottomNav />
    </div>
  );
}

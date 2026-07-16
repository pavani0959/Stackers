import { useEffect, useRef, useState } from 'react';
import {
  useNavigate,
  useParams,
  useSearchParams,
} from 'react-router-dom';
import {
  createProductDecision,
  getDecision,
} from '../../api/decisions';
import { checkRegret } from '../../api/events';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';
import BottomNav from '../../components/BottomNav/BottomNav';
import { useUser } from '../../context/useUser';
import '../../styles/ProductDetail.css';

const SIZES = ['XS', 'S', 'M', 'L', 'XL'];
const COMPONENT_LABELS = {
  style: 'Style DNA',
  occasion: 'Occasion',
  budget: 'Budget',
  wardrobe: 'Wardrobe compatibility',
  season: 'Season compatibility',
};

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const requestedSnapshotId = searchParams.get('decision');
  const productId = Number(id);
  const {
    user,
    profileLoading,
    addToCart,
    addToWishlist,
    createUserEvent,
  } = useUser();

  const [decision, setDecision] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);
  const [size, setSize] = useState('S');
  const [toast, setToast] = useState('');
  const [showAR, setShowAR] = useState(false);
  const [regretWarning, setRegretWarning] = useState(null);
  const [checkingRegret, setCheckingRegret] = useState(false);
  const viewedSnapshotRef = useRef(null);
  const primaryOccasion = user.occasions?.[0] ?? null;

  function showToast(message) {
    setToast(message);
    window.setTimeout(() => setToast(''), 2500);
  }

  useEffect(() => {
    if (profileLoading || !user?.id) {
      return undefined;
    }

    let cancelled = false;

    async function loadDecision() {
      setLoading(true);
      setError(null);
      try {
        const loadedDecision = requestedSnapshotId
          ? await getDecision(requestedSnapshotId)
          : await createProductDecision(productId, {
              occasion: primaryOccasion,
            });

        if (String(loadedDecision.product.id) !== String(id)) {
          throw new Error(
            'This decision snapshot belongs to a different product.',
          );
        }

        if (cancelled) {
          return;
        }

        setDecision(loadedDecision);

        if (!requestedSnapshotId) {
          navigate(
            `/product/${id}?decision=${loadedDecision.snapshot_id}`,
            { replace: true },
          );
        }

        if (viewedSnapshotRef.current !== loadedDecision.snapshot_id) {
          viewedSnapshotRef.current = loadedDecision.snapshot_id;
          createUserEvent({
            event_type: 'view',
            product_id: loadedDecision.product.id,
            recommendation_item_id:
              loadedDecision.recommendation_item_id,
            metadata: {
              source: 'product_detail',
              decision_snapshot_id: loadedDecision.snapshot_id,
              match_score: loadedDecision.overall_score,
              model_version: loadedDecision.model_version,
              profile_version: loadedDecision.profile_version,
            },
          }).catch(() => {});
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

    loadDecision();
    return () => {
      cancelled = true;
    };
  }, [
    id,
    productId,
    requestedSnapshotId,
    user?.id,
    primaryOccasion,
    profileLoading,
    retryKey,
    navigate,
    createUserEvent,
  ]);

  if (profileLoading || loading) {
    return <div className="screen-center">Loading product decision…</div>;
  }

  if (error) {
    return (
      <ApiErrorState
        error={error}
        title="Product decision could not be loaded"
        onRetry={() => setRetryKey((value) => value + 1)}
      />
    );
  }

  if (!decision) {
    return <div className="screen-center">Decision not found.</div>;
  }

  const product = decision.product;
  const isWished = (user.wishlist ?? []).includes(product.id);
  const isPerfectMatch = decision.overall_score >= 85;
  const originalPrice = product.originalPrice ?? product.price;
  const discount = originalPrice > 0
    ? Math.round((1 - product.price / originalPrice) * 100)
    : 0;
  const components = Object.entries(decision.score_breakdown);

  function handleWishlist() {
    const wasAlreadyWished = isWished;
    addToWishlist(product.id);

    const storageKey = 'myntra_wishlist';
    const current = JSON.parse(localStorage.getItem(storageKey) || '[]');
    if (wasAlreadyWished) {
      localStorage.setItem(
        storageKey,
        JSON.stringify(current.filter((item) => item.id !== product.id)),
      );
    } else if (!current.some((item) => item.id === product.id)) {
      current.push({
        id: product.id,
        name: product.name,
        brand: product.brand,
        price: finalPrice,
        image: product.image,
        dnaMatch: decision.overall_score,
        decisionSnapshotId: decision.snapshot_id,
        recommendationItemId: decision.recommendation_item_id,
      });
      localStorage.setItem(storageKey, JSON.stringify(current));
    }

    if (!wasAlreadyWished) {
      createUserEvent({
        event_type: 'wishlist',
        product_id: product.id,
        recommendation_item_id: decision.recommendation_item_id,
        metadata: {
          decision_snapshot_id: decision.snapshot_id,
          match_score: decision.overall_score,
        },
      }).catch(() => {});
    }

    showToast(
      wasAlreadyWished ? 'Removed from wishlist' : 'Added to wishlist ❤️',
    );
  }

  async function handleAddToCart() {
    setCheckingRegret(true);
    try {
      const regretData = await checkRegret(product.id);
      if (!regretData.safe_to_buy) {
        setRegretWarning(regretData);
        return; // Pause add to cart to show modal
      }
    } catch (e) {
      console.error('Failed to check regret', e);
    } finally {
      setCheckingRegret(false);
    }
    proceedWithCartAdd();
  }

  function proceedWithCartAdd() {
    setRegretWarning(null);
    addToCart({
      ...product,
      price: finalPrice,
      selectedSize: size,
      decisionSnapshotId: decision.snapshot_id,
      recommendationItemId: decision.recommendation_item_id,
    });

    createUserEvent({
      event_type: 'cart_add',
      product_id: product.id,
      recommendation_item_id: decision.recommendation_item_id,
      metadata: {
        size,
        match_score: decision.overall_score,
        model_version: decision.model_version,
        profile_version: decision.profile_version,
        decision_snapshot_id: decision.snapshot_id,
      },
    }).catch(() => {});

    showToast('Added to cart');
  }

  return (
    <div className="screen det-screen">
      <div className="det-img-wrap">
        <img 
          src={product.image} 
          alt={product.name} 
          onError={(e) => { e.target.onerror = null; e.target.src = 'https://via.placeholder.com/600x800?text=Myntra+App'; }}
        />
        <div className="det-hdr-btns">
          <button type="button" className="back-btn" onClick={() => navigate(-1)}>
            ←
          </button>
          <button
            type="button"
            className="wish-top-btn"
            onClick={handleWishlist}
            aria-label={isWished ? 'Remove from wishlist' : 'Add to wishlist'}
          >
            {isWished ? '❤️' : '♡'}
          </button>
        </div>

        <div className="det-conf-pill">
          <span className="det-score">{decision.overall_score}</span>
          <span className="det-score-lbl">Confidence Score</span>
        </div>
        <div className="det-action-bar" style={{ padding: '0 16px 16px', display: 'flex', gap: '10px' }}>
          <button
            type="button"
            className="ar-btn"
            onClick={() => setShowAR(true)}
          >
            Try it on AR
          </button>
        </div>
      </div>

      <main className="det-body">
        <section>
          <p className="det-brand">{product.brand}</p>
          <p className="det-name">{product.name}</p>
          <div className="det-pr-row">
            <span className="det-price">
              ₹{product.price.toLocaleString('en-IN')}
            </span>
            <span className="det-og">
              ₹{originalPrice.toLocaleString('en-IN')}
            </span>
            <span className="det-disc">{discount}% off</span>
          </div>
        </section>

        {isPerfectMatch && (
          <p className="decision-note match">
            ★ Perfect Match — this product scores above 85% on your Fashion DNA.
          </p>
        )}

        <section className="conf-card">
          <div className="conf-card-hdr">
            <div>
              <h3>Confidence Score</h3>
              <p>{decision.explanation.summary}</p>
            </div>
            <span className="conf-big">{decision.overall_score}</span>
          </div>

          {components.map(([name, component]) => (
            <div className="conf-row" key={name}>
              <span className="conf-lbl">
                {COMPONENT_LABELS[name] ?? name}
              </span>
              <div className="conf-bar-wrap">
                <div
                  className="conf-bar-fill"
                  style={{ '--target-w': `${component.score}%` }}
                />
              </div>
              <span className="conf-pct">{component.score}%</span>
            </div>
          ))}

          <button
            type="button"
            className="secondary-btn decision-link"
            onClick={() => navigate(`/decision/${decision.snapshot_id}`)}
          >
            Why is this recommended for me? →
          </button>
        </section>

        <section>
          <p className="size-label">Select Size</p>
          <div className="size-row">
            {SIZES.map((availableSize) => (
              <button
                type="button"
                key={availableSize}
                className={`size-chip ${size === availableSize ? 'active' : ''}`}
                onClick={() => setSize(availableSize)}
              >
                {availableSize}
              </button>
            ))}
          </div>
        </section>

        <button type="button" className="primary-btn" onClick={handleAddToCart} disabled={checkingRegret}>
          {checkingRegret ? 'Checking...' : `Add to Cart — ₹${product.price.toLocaleString('en-IN')}`}
        </button>
      </main>

      {regretWarning && (
        <div className="modal-overlay">
          <div className="modal-content regret-modal">
            <h2>⚠️ Potential Regret Detected</h2>
            
            <div className="regret-signals">
              {regretWarning.signals.map((sig, idx) => (
                <div key={idx} className="regret-signal-item">
                  <strong>{sig.title}</strong>
                  <p>{sig.detail}</p>
                </div>
              ))}
            </div>

            {regretWarning.alternatives && regretWarning.alternatives.length > 0 && (
              <div className="regret-alternatives">
                <h4>Suggested Alternatives</h4>
                <div className="alt-scroll" style={{ display: 'flex', overflowX: 'auto', gap: '10px' }}>
                  {regretWarning.alternatives.map((alt) => (
                    <div key={alt.id} className="alt-item" onClick={() => {
                        setRegretWarning(null);
                        navigate(`/product/${alt.id}`);
                    }} style={{ minWidth: '120px', cursor: 'pointer' }}>
                      <img src={alt.image} alt={alt.name} style={{ width: '100%', borderRadius: '8px' }} />
                      <div style={{ fontSize: '0.8rem', marginTop: '4px' }}>
                        <strong>{alt.name}</strong>
                        <p style={{ margin: 0, color: 'var(--ink-500)', fontSize: '0.7rem' }}>{alt.reason}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="regret-actions" style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
              <button className="secondary-btn" onClick={() => setRegretWarning(null)} style={{ flex: 1 }}>
                Cancel
              </button>
              <button className="primary-btn warning-btn" onClick={proceedWithCartAdd} style={{ flex: 1, backgroundColor: '#e74c3c' }}>
                I still want it
              </button>
            </div>
          </div>
        </div>
      )}

      {showAR && (
        <div className="ar-overlay" role="dialog" aria-modal="true">
          <div className="ar-modal">
            <button type="button" onClick={() => setShowAR(false)}>
              ×
            </button>
            <h2>Virtual Try-On</h2>
            <p>See how it looks on you</p>
            <div className="ar-camera">Stand here</div>
          </div>
        </div>
      )}

      {toast && <div className="toast">{toast}</div>}
      <BottomNav />
    </div>
  );
}

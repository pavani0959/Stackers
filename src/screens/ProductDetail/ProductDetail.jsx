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
  const isDnaDiscount = decision.overall_score >= 90;
  const finalPrice = isDnaDiscount
    ? Math.round(product.price * 0.85)
    : product.price;
  const originalPrice = product.originalPrice ?? product.price;
  const discount = originalPrice > 0
    ? Math.round((1 - finalPrice / originalPrice) * 100)
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

  function handleAddToCart() {
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
        <img src={product.image} alt={product.name} />
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

        <button
          type="button"
          className="det-ar-button"
          onClick={() => setShowAR(true)}
        >
          Try It On (AR)
        </button>
      </div>

      <main className="det-body">
        <section>
          <p className="det-brand">{product.brand}</p>
          <p className="det-name">{product.name}</p>
          <div className="det-pr-row">
            <span className="det-price">
              ₹{finalPrice.toLocaleString('en-IN')}
            </span>
            <span className="det-og">
              ₹{originalPrice.toLocaleString('en-IN')}
            </span>
            <span className="det-disc">{discount}% off</span>
          </div>
        </section>

        {isDnaDiscount && (
          <p className="decision-note">
            This stored decision qualifies for the app's 15% DNA discount rule.
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

        <button type="button" className="primary-btn" onClick={handleAddToCart}>
          Add to Cart — ₹{finalPrice.toLocaleString('en-IN')}
        </button>
      </main>

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

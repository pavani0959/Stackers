import {
  useEffect,
  useRef,
  useState,
} from 'react';

import {
  useNavigate,
  useParams,
} from 'react-router-dom';

import { useUser } from '../../context/useUser';
import { apiRequest } from '../../api/client';

import BottomNav from '../../components/BottomNav/BottomNav';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';

import '../../styles/ProductDetail.css';

const SIZES = ['XS', 'S', 'M', 'L', 'XL'];

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const {
    user,
    profileLoading,
    addToCart,
    addToWishlist,
    createUserEvent,
  } = useUser();

  const [product, setProduct] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState(null);

  const [retryKey, setRetryKey] =
    useState(0);

  const [size, setSize] =
    useState('S');

  const [toast, setToast] =
    useState('');

  const [showAR, setShowAR] =
    useState(false);

  /*
   * Prevent duplicate view events caused by
   * effect reruns or React Strict Mode.
   */
  const viewedProductIdRef =
    useRef(null);

  function showToast(message) {
    setToast(message);

    window.setTimeout(() => {
      setToast('');
    }, 2500);
  }

  useEffect(() => {
    if (profileLoading || !user?.id) {
      return undefined;
    }

    let cancelled = false;

    async function loadProduct() {
      setLoading(true);
      setError(null);

      try {
        const [
          productData,
          confidenceData,
        ] = await Promise.all([
          apiRequest(
            `/api/products/${id}`,
          ),

          apiRequest(
            `/api/recommend/confidence/${id}`,
            {
              method: 'POST',

              body: JSON.stringify({
                user_profile: user,
              }),
            },
          ),
        ]);

        if (cancelled) {
          return;
        }

        const loadedProduct = {
          ...productData,
          confidence: confidenceData,
        };

        setProduct(loadedProduct);

        /*
         * Event creation is non-blocking.
         * Product rendering still succeeds even if
         * analytics recording fails.
         */
        if (
          viewedProductIdRef.current !==
          loadedProduct.id
        ) {
          viewedProductIdRef.current =
            loadedProduct.id;

          createUserEvent({
            event_type: 'view',
            product_id: loadedProduct.id,

            metadata: {
              source: 'product_detail',
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

    loadProduct();

    return () => {
      cancelled = true;
    };
  }, [
    id,
    user,
    retryKey,
    profileLoading,
    createUserEvent,
  ]);

  if (loading) {
    return (
      <div className="screen">
        <div className="page-loading">
          Loading product…
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="screen">
        <ApiErrorState
          error={error}
          title="Product unavailable"
          onRetry={() =>
            setRetryKey(
              (value) => value + 1,
            )
          }
        />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="screen">
        <ApiErrorState
          title="Product not found"
        />
      </div>
    );
  }

  const conf = product.confidence ?? {
    overall: 0,
    styleMatch: 0,
    occasionMatch: 0,
    budgetMatch: 0,
    weatherMatch: 0,
    wardrobeMatch: 0,
  };

  const isWished = (
    user.wishlist ?? []
  ).includes(product.id);

  const isDnaDiscount =
    conf.overall >= 90;

  const finalPrice = isDnaDiscount
    ? Math.round(product.price * 0.85)
    : product.price;

  const originalPrice =
    product.originalPrice ??
    product.price;

  const discount =
    originalPrice > 0
      ? Math.round(
          (
            1 -
            finalPrice / originalPrice
          ) * 100,
        )
      : 0;

  function handleWishlist() {
    const wasAlreadyWished = isWished;

    addToWishlist(product.id);

    // Sync to localStorage so the Wishlist screen can read it
    const storageKey = 'myntra_wishlist';
    const current = JSON.parse(localStorage.getItem(storageKey) || '[]');
    if (wasAlreadyWished) {
      const updated = current.filter(item => item.id !== product.id);
      localStorage.setItem(storageKey, JSON.stringify(updated));
    } else {
      const alreadyExists = current.find(i => i.id === product.id);
      if (!alreadyExists) {
        current.push({
          id: product.id,
          name: product.name,
          brand: product.brand,
          price: finalPrice,
          image: product.image,
          dnaMatch: conf.overall ?? 75,
        });
        localStorage.setItem(storageKey, JSON.stringify(current));
      }
    }

    // Record backend event only on add
    if (!wasAlreadyWished) {
      createUserEvent({
        event_type: 'wishlist',
        product_id: product.id,
        metadata: { match_score: conf.overall ?? null },
      }).catch(() => {});
    }

    showToast(
      wasAlreadyWished ? 'Removed from wishlist' : 'Added to wishlist ❤️',
    );
  }

  function handleAddToCart() {
    const productToAdd = {
      ...product,
      price: finalPrice,
      selectedSize: size,
    };

    addToCart(productToAdd);

    /*
     * Adding to cart creates only cart_add.
     * It must never create a purchase event.
     */
    createUserEvent({
      event_type: 'cart_add',
      product_id: product.id,

      metadata: {
        size,

        match_score:
          conf.overall ?? null,
      },
    }).catch(() => {});

    showToast('Added to cart 🛒');
  }

  return (
    <div className="screen det-screen">
      {/* Product image */}
      <div className="det-img-wrap">
        <img
          src={product.image}
          alt={product.name}
        />

        <div className="det-hdr-btns">
          <button
            type="button"
            className="back-btn"
            onClick={() => navigate(-1)}
          >
            ←
          </button>

          <button
            type="button"
            className="wish-top-btn"
            onClick={handleWishlist}
          >
            {isWished ? '❤️' : '🤍'}
          </button>
        </div>

        <div className="det-conf-pill">
          <span className="det-score">
            {conf.overall}
          </span>

          <span className="det-score-lbl">
            Confidence Score
          </span>
        </div>

        <button
          type="button"
          className="ar-btn"
          onClick={() => setShowAR(true)}
          style={{
            position: 'absolute',
            bottom: 15,
            left: 15,
            background: 'rgba(0,0,0,0.6)',
            backdropFilter: 'blur(10px)',
            color: 'white',
            border:
              '1px solid rgba(255,255,255,0.2)',
            padding: '6px 12px',
            borderRadius: 20,
            fontSize: 12,
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          📸 Try It On (AR)
        </button>
      </div>

      {/* Scrollable body */}
      <div className="det-body">
        <div>
          <div className="det-brand">
            {product.brand}
          </div>

          <div className="det-name">
            {product.name}
          </div>

          <div className="det-pr-row">
            <span className="det-price">
              ₹
              {finalPrice.toLocaleString(
                'en-IN',
              )}
            </span>

            <span className="det-og">
              ₹
              {originalPrice.toLocaleString(
                'en-IN',
              )}
            </span>

            <span className="det-disc">
              {discount}% off
            </span>
          </div>

          {isDnaDiscount && (
            <div
              style={{
                marginTop: 8,
                padding: '6px 12px',
                background:
                  'rgba(57, 255, 20, 0.1)',
                color: 'var(--green)',
                borderRadius: 6,
                fontSize: 12,
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <span>💰</span>

              Because this is a 90%+ match,
              you unlocked a 15% DNA
              Discount!
            </div>
          )}
        </div>

        {/* Confidence Score Card */}
        <div className="conf-card">
          <div className="conf-card-hdr">
            <div>
              <h3>
                🎯 Confidence Score
              </h3>

              <p>
                Why this is perfect for you
              </p>
            </div>

            <div className="conf-big grad-text">
              {conf.overall}
            </div>
          </div>

          {[
            {
              icon: '🧬',
              label: 'Style Match',
              val: conf.styleMatch,
            },
            {
              icon: '📅',
              label: 'Occasion Match',
              val: conf.occasionMatch,
            },
            {
              icon: '💰',
              label: 'Budget Match',
              val: conf.budgetMatch,
            },
            {
              icon: '☁️',
              label: 'Weather Match',
              val: conf.weatherMatch,
            },
            {
              icon: '👗',
              label: 'Wardrobe Fit',
              val: conf.wardrobeMatch,
            },
          ].map((row) => (
            <div
              key={row.label}
              className="conf-row"
            >
              <span className="conf-icon">
                {row.icon}
              </span>

              <span className="conf-lbl">
                {row.label}
              </span>

              <div className="conf-bar-wrap">
                <div
                  className="conf-bar-fill"
                  style={{
                    '--target-w':
                      `${row.val}%`,
                  }}
                />
              </div>

              <span className="conf-pct">
                {row.val}%
              </span>
            </div>
          ))}
        </div>

        <button
          type="button"
          className="btn-accent-outline"
          onClick={() =>
            navigate(
              `/decision/${product.id}`,
            )
          }
        >
          🤔 Why is this recommended for me? →
        </button>

        {/* Size */}
        <div>
          <div className="size-label">
            Select Size
          </div>

          <div className="size-row">
            {SIZES.map((availableSize) => (
              <button
                key={availableSize}
                type="button"
                className={`size-chip ${
                  size === availableSize
                    ? 'active'
                    : ''
                }`}
                onClick={() =>
                  setSize(availableSize)
                }
              >
                {availableSize}
              </button>
            ))}
          </div>
        </div>

        <button
          type="button"
          className="btn-primary"
          onClick={handleAddToCart}
        >
          Add to Cart — ₹
          {finalPrice.toLocaleString(
            'en-IN',
          )}
        </button>
      </div>

      {/* AR Modal Overlay */}
      {showAR && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 1000,
            background: '#000',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <div
            style={{
              padding: '48px 18px 14px',
              display: 'flex',
              justifyContent:
                'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <div
                style={{
                  fontWeight: 800,
                  color: '#fff',
                  fontSize: 16,
                }}
              >
                📸 Virtual Try-On
              </div>

              <div
                style={{
                  fontSize: 11,
                  color:
                    'rgba(255,255,255,0.5)',
                  marginTop: 2,
                }}
              >
                See how it looks on you
              </div>
            </div>

            <button
              type="button"
              aria-label="Close virtual try-on"
              onClick={() =>
                setShowAR(false)
              }
              style={{
                border: 0,
                background: 'transparent',
                fontSize: 28,
                cursor: 'pointer',
                color: '#fff',
                lineHeight: 1,
              }}
            >
              ×
            </button>
          </div>

          {/* Camera frame */}
          <div
            style={{
              flex: 1,
              position: 'relative',
              background: '#111',
              margin: '0 18px',
              borderRadius: 16,
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                position: 'absolute',
                inset: 0,
                background:
                  'linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <div
                style={{
                  width: 140,
                  height: 260,
                  border:
                    '2px dashed rgba(255,63,108,0.4)',
                  borderRadius: 80,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexDirection: 'column',
                  gap: 8,
                }}
              >
                <span
                  style={{
                    fontSize: 32,
                  }}
                >
                  🧍
                </span>

                <span
                  style={{
                    fontSize: 11,
                    color:
                      'rgba(255,255,255,0.3)',
                    textAlign: 'center',
                  }}
                >
                  Stand here
                </span>
              </div>
            </div>

            <img
              src={product.image}
              alt={`Virtual preview of ${product.name}`}
              style={{
                position: 'absolute',
                top: '30%',
                left: '50%',
                transform:
                  'translate(-50%, -30%)',
                width: '65%',
                opacity: 0.88,
                filter:
                  'drop-shadow(0 8px 24px rgba(255,63,108,0.3))',
              }}
            />

            {[
              'top-left',
              'top-right',
              'bottom-left',
              'bottom-right',
            ].map((corner, index) => (
              <div
                key={corner}
                style={{
                  position: 'absolute',
                  width: 20,
                  height: 20,

                  top:
                    index < 2
                      ? 20
                      : 'auto',

                  bottom:
                    index >= 2
                      ? 20
                      : 'auto',

                  left:
                    index % 2 === 0
                      ? 20
                      : 'auto',

                  right:
                    index % 2 === 1
                      ? 20
                      : 'auto',

                  borderTop:
                    index < 2
                      ? '2px solid var(--accent)'
                      : 'none',

                  borderBottom:
                    index >= 2
                      ? '2px solid var(--accent)'
                      : 'none',

                  borderLeft:
                    index % 2 === 0
                      ? '2px solid var(--accent)'
                      : 'none',

                  borderRight:
                    index % 2 === 1
                      ? '2px solid var(--accent)'
                      : 'none',
                }}
              />
            ))}

            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: 2,
                background: 'var(--accent)',
                boxShadow:
                  '0 0 12px var(--accent)',
                animation:
                  'scan 2.5s infinite linear',
              }}
            />
          </div>

          <style
            dangerouslySetInnerHTML={{
              __html: `
                @keyframes scan {
                  0% {
                    top: 0%;
                    opacity: 0;
                  }

                  10% {
                    opacity: 1;
                  }

                  90% {
                    opacity: 1;
                  }

                  100% {
                    top: 100%;
                    opacity: 0;
                  }
                }
              `,
            }}
          />

          <div
            style={{
              padding: '14px 18px 40px',
              textAlign: 'center',
            }}
          >
            <div
              style={{
                color: '#fff',
                fontSize: 14,
                fontWeight: 700,
                marginBottom: 4,
              }}
            >
              {product.name}
            </div>

            <div
              style={{
                color:
                  'rgba(255,255,255,0.5)',
                fontSize: 12,
                lineHeight: 1.5,
              }}
            >
              This shows how the item would
              look on you.
              <br />
              In the full app, your camera
              would be used for a live preview.
            </div>
          </div>
        </div>
      )}

      {toast && (
        <div className="toast">
          {toast}
        </div>
      )}

      <BottomNav />
    </div>
  );
}
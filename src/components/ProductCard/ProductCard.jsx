import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import '../../styles/ProductCard.css';
import { Heart } from 'lucide-react';

// "Perfect Match" badge threshold — achievable through normal quiz flow
const PERFECT_MATCH_THRESHOLD = 85;

const COLOUR_MAP = {
  black: '#1a1a1a', white: '#f5f5f5', grey: '#9ca3af', gray: '#9ca3af',
  red: '#ef4444', blue: '#3b82f6', green: '#22c55e', yellow: '#eab308',
  pink: '#ec4899', purple: '#a855f7', orange: '#f97316', brown: '#92400e',
  beige: '#d4b896', navy: '#1e3a5f', teal: '#14b8a6', cream: '#fffdd0',
  maroon: '#800000', olive: '#808000', coral: '#ff7f50', lavender: '#e6e6fa',
  multicolour: 'conic-gradient(red,yellow,lime,aqua,blue,magenta,red)',
};

function getColourStyle(colourName) {
  if (!colourName) return null;
  const key = colourName.toLowerCase().trim();
  const colour = COLOUR_MAP[key];
  if (!colour) return { backgroundColor: '#d1d5db' };
  if (colour.startsWith('conic')) return { background: colour };
  return { backgroundColor: colour };
}

export default function ProductCard({ decision: decisionProp, product: productProp, variant }) {
  const navigate = useNavigate();
  const { user, addToWishlist } = useUser();

  // Support both {decision} (Home feed) and {product} (Search results) props
  const decision = decisionProp || {
    product: productProp,
    overall_score: productProp?.confidence?.overall ?? 70,
    snapshot_id: productProp?.id ?? '',
  };
  const product = decision.product;
  const isWished = (user.wishlist ?? []).includes(product.id);
  const isPerfectMatch = decision.overall_score >= PERFECT_MATCH_THRESHOLD;
  const [imgError, setImgError] = useState(false);

  const colour = product.primary_colour || null;
  const isGradient = variant === 'gradient';

  function openProduct() {
    navigate(`/product/${product.id}?decision=${decision.snapshot_id}`);
  }

  // Deterministic gradient class for the gradient variant
  const gradientClass = isGradient ? `prod-grad-${(product.id % 4) + 1}` : '';

  // ── Image block (shared between both variants) ──
  const imageBlock = (
    <div className="prod-img-wrap">
      {!imgError ? (
        <img
          src={product.image}
          alt={product.name}
          onError={() => setImgError(true)}
        />
      ) : (
        <div className="img-fallback">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg>
          <span>Image unavailable</span>
        </div>
      )}
    </div>
  );

  // ── Info block below image (inside card body for gradient, or directly) ──
  const infoBlock = (
    <div className="prod-info">
      <span className="prod-label">Myntra Edit</span>
      <p className="prod-name">{product.name}</p>
      {colour && (
        <div className="prod-colour-row">
          <span className="prod-colour-dot" style={getColourStyle(colour)} />
          <span className="prod-colour-text">Colour: {colour}</span>
        </div>
      )}
      <div className="prod-catalogue-link">
        MYNTRA IDENTITY CATALOGUE <span className="prod-catalogue-arrow">›</span>
      </div>
    </div>
  );

  if (variant === 'thumbnail') {
    return (
      <button
        type="button"
        className="prod-thumb-card"
        aria-label={`View ${product.name}`}
        onClick={openProduct}
      >
        <div className="prod-thumb-img-wrap">
          {!imgError ? (
            <img src={product.image} alt={product.name} onError={() => setImgError(true)} />
          ) : (
            <div className="img-fallback">
              <span>Image unavailable</span>
            </div>
          )}
        </div>
        <div className="prod-thumb-name">{product.name}</div>
        <div className="prod-thumb-price">₹{product.price.toLocaleString('en-IN')}</div>
      </button>
    );
  }

  return (
    <article className={`prod-card ${isGradient ? 'is-gradient' : ''}`}>
      <button
        type="button"
        className="prod-card-open"
        aria-label={`View ${product.name}`}
        onClick={openProduct}
      ></button>

      {isGradient ? (
        /* Gradient frame wraps badge + white inner card */
        <div className={`prod-gradient-frame ${gradientClass}`}>
          <span className={`dna-badge ${isPerfectMatch ? 'perfect' : ''}`}>
            {isPerfectMatch ? '★ ' : ''}{decision.overall_score}% Match
          </span>
          <div className="prod-inner-card">
            {imageBlock}
            {infoBlock}
          </div>
        </div>
      ) : (
        /* Standard card: badge + heart overlay the image directly */
        <>
          <div className="prod-img-container">
            {imageBlock}
            <span className={`dna-badge ${isPerfectMatch ? 'perfect' : ''}`}>
              {isPerfectMatch ? '★ ' : ''}{decision.overall_score}% Match
            </span>
            <button
              type="button"
              className="wish-btn"
              aria-label={isWished ? 'Remove from wishlist' : 'Add to wishlist'}
              onClick={(event) => {
                event.stopPropagation();
                addToWishlist(product.id);
              }}
            >
              <Heart aria-hidden="true" size={18} fill={isWished ? 'currentColor' : 'none'} />
            </button>
          </div>
          {infoBlock}
        </>
      )}

      {/* Bottom strip: heart + brand + price (shown once, outside the card body) */}
      <div className="prod-bottom">
        <div className="prod-bottom-left">
          <button
            type="button"
            className="wish-btn-inline"
            aria-label={isWished ? 'Remove from wishlist' : 'Add to wishlist'}
            onClick={(event) => {
              event.stopPropagation();
              addToWishlist(product.id);
            }}
          >
            <Heart size={14} className="prod-bottom-heart" fill={isWished ? 'currentColor' : 'none'} />
          </button>
          <span className="prod-brand">{product.brand}</span>
        </div>
        <div className="prod-pr-row">
          <span className="prod-price">₹{product.price.toLocaleString('en-IN')}</span>
          <span className="prod-og">₹{product.originalPrice.toLocaleString('en-IN')}</span>
        </div>
      </div>
    </article>
  );
}

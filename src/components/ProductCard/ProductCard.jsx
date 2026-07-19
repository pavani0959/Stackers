import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import '../../styles/ProductCard.css';
import {
  Heart,
} from 'lucide-react';

// "Perfect Match" badge threshold — achievable through normal quiz flow
const PERFECT_MATCH_THRESHOLD = 85;

export default function ProductCard({ decision }) {
  const navigate = useNavigate();
  const { user, addToWishlist } = useUser();
  const product = decision.product;
  const isWished = (user.wishlist ?? []).includes(product.id);
  const isPerfectMatch = decision.overall_score >= PERFECT_MATCH_THRESHOLD;
  const [imgError, setImgError] = useState(false);

  function openProduct() {
    navigate(
      `/product/${product.id}?decision=${decision.snapshot_id}`,
    );
  }

  return (
          <article className="prod-card">
        <button
          type="button"
          className="prod-card-open"
          aria-label={`View ${product.name}`}
          onClick={openProduct}
        ></button>

      <div className="prod-img">
        {!imgError ? (
          <img
            src={product.image}
            alt={product.name}
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="img-fallback">
            <span className="img-fallback-icon">👕</span>
            <span className="img-fallback-text">{product.name}</span>
          </div>
        )}
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
          <Heart
            aria-hidden="true"
            size={20}
            fill={
              isWished
                ? 'currentColor'
                : 'none'
            }
          />
        </button>
      </div>

      <div className="prod-info">
        <p className="prod-brand">{product.brand}</p>
        <p className="prod-name">{product.name}</p>
        <div className="prod-pr-row">
          <span className="prod-price">
            ₹{product.price.toLocaleString('en-IN')}
          </span>
          <span className="prod-og">
            ₹{product.originalPrice.toLocaleString('en-IN')}
          </span>
          {isPerfectMatch && (
            <span className="prod-match-badge">Perfect Match</span>
          )}
        </div>
      </div>
    </article>
  );
}

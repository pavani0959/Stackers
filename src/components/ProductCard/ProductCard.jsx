import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import '../../styles/ProductCard.css';

// "Perfect Match" badge threshold — achievable through normal quiz flow
const PERFECT_MATCH_THRESHOLD = 85;

export default function ProductCard({ decision }) {
  const navigate = useNavigate();
  const { user, addToWishlist } = useUser();
  const product = decision.product;
  const isWished = (user.wishlist ?? []).includes(product.id);
  const isPerfectMatch = decision.overall_score >= PERFECT_MATCH_THRESHOLD;

  function openProduct() {
    navigate(
      `/product/${product.id}?decision=${decision.snapshot_id}`,
    );
  }

  return (
    <article
      className="prod-card"
      onClick={openProduct}
      onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          openProduct();
        }
      }}
      role="button"
      tabIndex={0}
    >
      <div className="prod-img">
        <img
          src={product.image}
          alt={product.name}
          onError={(e) => { e.target.onerror = null; e.target.src = '/catalog/fallback-product.webp'; }}
        />
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
          {isWished ? '❤️' : '♡'}
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

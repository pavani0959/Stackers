import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import '../../styles/ProductCard.css';

export default function ProductCard({ decision }) {
  const navigate = useNavigate();
  const { user, addToWishlist } = useUser();
  const product = decision.product;
  const isWished = (user.wishlist ?? []).includes(product.id);
  const isDnaDiscount = decision.overall_score >= 90;
  const finalPrice = isDnaDiscount
    ? Math.round(product.price * 0.85)
    : product.price;

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
          onError={(e) => { e.target.onerror = null; e.target.src = 'https://via.placeholder.com/300x400?text=Myntra+App'; }} 
        />
        <span className="dna-badge">
          {decision.overall_score}% Match
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
            ₹{finalPrice.toLocaleString('en-IN')}
          </span>
          {!isDnaDiscount && (
            <span className="prod-og">
              ₹{product.originalPrice.toLocaleString('en-IN')}
            </span>
          )}
          {isDnaDiscount && (
            <span className="prod-disc">-15% DNA</span>
          )}
        </div>
      </div>
    </article>
  );
}

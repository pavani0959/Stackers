import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import '../../styles/ProductCard.css';

export default function ProductCard({ product }) {
  const navigate = useNavigate();
  const { user, addToWishlist, buyItem } = useUser();
  const isWished = user.wishlist.includes(product.id);
  
  // Feature 7: DNA Dynamic Pricing (15% off if confidence >= 90)
  const isDnaDiscount = product.confidence?.overall >= 90;
  const finalPrice = isDnaDiscount ? Math.round(product.price * 0.85) : product.price;

  return (
    <div className="prod-card" onClick={() => navigate(`/product/${product.id}`)}>
      <div className="prod-img">
        <img src={product.image} alt={product.name} loading="lazy" />
        <div className="dna-badge">🧬 {product.confidence?.overall || 80}% Match</div>
        <button className="wish-btn" onClick={(e) => { e.stopPropagation(); addToWishlist(product.id); }}>
          {isWished ? '❤️' : '🤍'}
        </button>
      </div>
      <div className="prod-info">
        <div className="prod-brand">{product.brand}</div>
        <div className="prod-name">{product.name}</div>
        <div className="prod-pr-row">
          <span className="prod-price">₹{finalPrice.toLocaleString('en-IN')}</span>
          {isDnaDiscount && <span style={{fontSize: 10, color: 'var(--green)', fontWeight: 800}}>✨ -15% DNA</span>}
          {!isDnaDiscount && <span className="prod-og">₹{product.originalPrice.toLocaleString('en-IN')}</span>}
        </div>
      </div>
    </div>
  );
}

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShoppingBag } from 'lucide-react';
import { useUser } from '../../context/useUser';
import './CartIconButton.css';

export default function CartIconButton({ className = '', style = {} }) {
  const navigate = useNavigate();
  const { user } = useUser();
  const cartItems = user?.cartItems || [];
  const count = cartItems.reduce((acc, item) => acc + (item.quantity || 1), 0);

  return (
    <button 
      type="button" 
      className={`cart-icon-btn ${className}`}
      style={style}
      onClick={() => navigate('/cart')}
      aria-label="View Cart"
    >
      <ShoppingBag size={20} aria-hidden="true" />
      {count > 0 && <span className="cart-badge">{count}</span>}
    </button>
  );
}

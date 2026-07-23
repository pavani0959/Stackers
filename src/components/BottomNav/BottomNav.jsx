import { useNavigate, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Home, Search, Sparkles, Globe, User } from 'lucide-react';
import '../../styles/BottomNav.css';

const navItems = [
  { icon: <Home size={22} />, label: 'Home',    path: '/home' },
  { icon: <Search size={22} />, label: 'Search',  path: '/search' },
  { icon: <Sparkles size={22} />, label: 'Reverse', path: '/reverse' },
  { icon: <Globe size={22} />, label: 'Tribe',   path: '/community' },
  { icon: <User size={22} />, label: 'Profile', path: '/profile' },
];

export default function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();
  const [wishlistCount, setWishlistCount] = useState(0);

  useEffect(() => {
    const update = () => {
      const saved = JSON.parse(localStorage.getItem('myntra_wishlist') || '[]');
      setWishlistCount(saved.length);
    };
    update();
    window.addEventListener('storage', update);
    // Also check on focus since same-page changes don't fire storage event
    window.addEventListener('focus', update);
    return () => { window.removeEventListener('storage', update); window.removeEventListener('focus', update); };
  }, []);

  return (
    <nav className="bottom-nav">
      {navItems.map(item => (
        <button
          key={item.label}
          className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          onClick={() => navigate(item.path)}
        >
          <span className="nav-icon-wrap">
            <span className="nav-icon">{item.icon}</span>
            {item.path === '/profile' && wishlistCount > 0 && (
              <span className="nav-badge">{wishlistCount}</span>
            )}
          </span>
          <span>{item.label}</span>
        </button>
      ))}
    </nav>
  );
}

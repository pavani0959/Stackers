import { useNavigate, useLocation } from 'react-router-dom';
import '../../styles/BottomNav.css';

const navItems = [
  { icon: '🏠', label: 'Home',    path: '/home' },
  { icon: '🔮', label: 'Reverse', path: '/reverse' },
  { icon: '🌐', label: 'Tribe',   path: '/community' },
  { icon: '📖', label: 'Memory',  path: '/memory' },
  { icon: '🧬', label: 'DNA',     path: '/identity-card' },
];

export default function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <nav className="bottom-nav">
      {navItems.map(item => (
        <button
          key={item.label}
          className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          onClick={() => navigate(item.path)}
        >
          <span className="nav-icon">{item.icon}</span>
          <span>{item.label}</span>
        </button>
      ))}
    </nav>
  );
}

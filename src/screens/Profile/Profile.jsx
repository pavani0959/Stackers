import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { savePreferences } from '../../api/profile';
import BottomNav from '../../components/BottomNav/BottomNav';
import '../../styles/Profile.css';

const BUDGET_OPTIONS = [
  { label: '₹500–₹1,500', value: 'campus-casual', desc: 'Budget Friendly' },
  { label: '₹1,500–₹3,000', value: 'mid-range', desc: 'Mid Range' },
  { label: '₹3,000–₹6,000', value: 'premium', desc: 'Premium' },
  { label: '₹6,000+', value: 'luxury', desc: 'Luxury' },
];

const OCCASION_OPTIONS = ['casual', 'campus', 'formal', 'party', 'date', 'festive', 'outdoor', 'gym'];

export default function Profile() {
  const navigate = useNavigate();
  const { user, updateUser } = useUser();
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(user.name || '');
  const [budget, setBudget] = useState(user.budget || 'campus-casual');
  const [occasions, setOccasions] = useState(user.occasions || []);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState('');

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 2500); };

  const toggleOccasion = (occ) => {
    setOccasions(prev =>
      prev.includes(occ) ? prev.filter(o => o !== occ) : [...prev, occ]
    );
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await savePreferences({ budget, occasions });
      updateUser({ name, budget, occasions });
      setEditing(false);
      showToast('Profile saved! ✅');
    } catch {
      showToast('Could not save. Try again.');
    } finally {
      setSaving(false);
    }
  };

  // DNA breakdown as sorted array
  const dnaEntries = Object.entries(user.dna || {}).sort(([, a], [, b]) => b - a);
  const primaryDna = dnaEntries[0];

  const GENDER_EMOJI = { male: '♂', female: '♀', 'non-binary': '⚧' };
  const genderEmoji = GENDER_EMOJI[user.gender] || '🧑';

  return (
    <div className="screen profile-screen">
      <div className="prf-hdr">
        <div className="prf-back-row">
          <div className="back-btn" onClick={() => navigate(-1)}>←</div>
          <div className="prf-hdr-title">My Profile</div>
          {!editing && (
            <button className="prf-edit-btn" onClick={() => setEditing(true)}>Edit</button>
          )}
        </div>
      </div>

      <div className="prf-body">
        {/* Avatar + Name */}
        <div className="prf-hero">
          <div className="prf-avatar">
            <span className="prf-avatar-emoji">{genderEmoji}</span>
          </div>
          {editing ? (
            <input
              className="prf-name-input"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Your name"
            />
          ) : (
            <div className="prf-name">{user.name || 'Your Name'}</div>
          )}
          <div className="prf-sub-info">
            {user.gender && <span className="prf-badge">{user.gender}</span>}
            {user.age && <span className="prf-badge">Age {user.age}</span>}
          </div>
        </div>

        {/* Fashion DNA summary */}
        {dnaEntries.length > 0 && (
          <div className="prf-card">
            <div className="prf-card-title">🧬 Fashion DNA</div>
            {dnaEntries.slice(0, 4).map(([style, pct]) => (
              <div key={style} className="prf-dna-row">
                <div className="prf-dna-name">{style}</div>
                <div className="prf-dna-bar-wrap">
                  <div
                    className="prf-dna-bar"
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <div className="prf-dna-pct">{pct}%</div>
              </div>
            ))}
            <div className="prf-identity-chip">
              Identity: <strong>{user.identityName || primaryDna?.[0] || 'Calculating…'}</strong>
            </div>
          </div>
        )}

        {/* Budget */}
        <div className="prf-card">
          <div className="prf-card-title">💰 Budget Range</div>
          {editing ? (
            <div className="prf-budget-opts">
              {BUDGET_OPTIONS.map(b => (
                <button
                  key={b.value}
                  className={`prf-budget-btn ${budget === b.value ? 'active' : ''}`}
                  onClick={() => setBudget(b.value)}
                >
                  <div className="prf-budget-lbl">{b.label}</div>
                  <div className="prf-budget-desc">{b.desc}</div>
                </button>
              ))}
            </div>
          ) : (
            <div className="prf-value">
              {BUDGET_OPTIONS.find(b => b.value === budget)?.label || '₹500–₹1,500'}
            </div>
          )}
        </div>

        {/* Occasions */}
        <div className="prf-card">
          <div className="prf-card-title">📅 Your Occasions</div>
          {editing ? (
            <div className="prf-occ-chips">
              {OCCASION_OPTIONS.map(occ => (
                <button
                  key={occ}
                  className={`prf-occ-chip ${occasions.includes(occ) ? 'active' : ''}`}
                  onClick={() => toggleOccasion(occ)}
                >
                  {occ}
                </button>
              ))}
            </div>
          ) : (
            <div className="prf-occ-chips">
              {(occasions.length ? occasions : ['casual']).map(occ => (
                <span key={occ} className="prf-occ-chip active">{occ}</span>
              ))}
            </div>
          )}
        </div>

        {/* Action buttons */}
        {editing && (
          <div className="prf-actions">
            <button
              className="prf-save-btn"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? 'Saving…' : 'Save Changes'}
            </button>
            <button
              className="prf-cancel-btn"
              onClick={() => {
                setEditing(false);
                setName(user.name || '');
                setBudget(user.budget || 'campus-casual');
                setOccasions(user.occasions || []);
              }}
            >
              Cancel
            </button>
          </div>
        )}

        {/* Nav links */}
        <div className="prf-links">
          <div className="prf-link-row" onClick={() => navigate('/memory')}>
            <span>📖 Fashion Memory</span>
            <span>→</span>
          </div>
          <div className="prf-link-row" onClick={() => navigate('/wishlist')}>
            <span>♡ My Wishlist</span>
            <span>→</span>
          </div>
          <div className="prf-link-row" onClick={() => navigate('/identity-card')}>
            <span>🧬 DNA Identity Card</span>
            <span>→</span>
          </div>
        </div>
      </div>

      {toast && <div className="toast">{toast}</div>}
      <BottomNav />
    </div>
  );
}

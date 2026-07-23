import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { buildDnaBars } from '../../features/dna/formatDNA';
import '../../styles/IdentityCard.css';

// SVG Icons
const Icons = {
  Color: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/></svg>,
  Fit: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20.38 3.46L16 2a8.5 8.5 0 0 1-8 0L3.62 3.46a2 2 0 0 0-1.34 2.23l.58 3.47a1 1 0 0 0 .99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V10h2.15a1 1 0 0 0 .99-.84l.58-3.47a2 2 0 0 0-1.34-2.23z"/></svg>,
  Goal: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>,
  Check: () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>,
  List: () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>,
  Shield: () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
  User: () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>,
  Edit: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>,
  Share: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>,
  Trend: () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
};

function formatBudget(user) {
  const hasMinimum = user.budgetMin !== null && user.budgetMin !== undefined;
  const hasMaximum = user.budgetMax !== null && user.budgetMax !== undefined;
  if (hasMinimum && hasMaximum) return `₹${user.budgetMin.toLocaleString('en-IN')} – ₹${user.budgetMax.toLocaleString('en-IN')}`;
  if (hasMaximum) return `Up to ₹${user.budgetMax.toLocaleString('en-IN')}`;
  if (hasMinimum) return `From ₹${user.budgetMin.toLocaleString('en-IN')}`;
  if (user.budget) return user.budget.replace(/-/g, ' ');
  return null;
}

function formatMemberSince(createdAt) {
  if (!createdAt) return 'Recently joined';
  const createdDate = new Date(createdAt);
  if (Number.isNaN(createdDate.getTime())) return 'Recently joined';
  return createdDate.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });
}

function buildOccasionList(user) {
  const priorities = user.occasionPriorities ?? {};
  const prioritizedOccasions = Object.entries(priorities)
    .sort(([, leftPriority], [, rightPriority]) => rightPriority - leftPriority)
    .map(([occasion]) => occasion);
  if (prioritizedOccasions.length > 0) return prioritizedOccasions;
  return user.occasions ?? [];
}

function formatLabel(value) {
  if (!value) return '';
  return value.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/[-_]/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default function IdentityCard() {
  const navigate = useNavigate();
  const { user } = useUser();

  const bars = buildDnaBars(user.dna);
  const name = user.name?.trim() || 'Style Explorer';
  const identityName = user.identityName || bars[0]?.label || 'Your Fashion Identity';
  const identityDescription = user.identityDescription || 'Clean, versatile pieces and intentional styling form the centre of your wardrobe.';
  const memberSince = formatMemberSince(user.createdAt);
  const budget = formatBudget(user);
  const occasions = buildOccasionList(user);
  const colours = user.colours ?? [];
  const fitPreferences = user.fitPreferences ?? [];
  
  const confidence = user.profileConfidence ?? 67;
  const confBreakdown = user.confidenceBreakdown ?? {};
  const evidence = user.evidence ?? {};

  async function share() {
    const text = `My Myntra Identity: ${identityName}\nStyle Confidence: ${confidence}%`;
    try {
      if (navigator.share) await navigator.share({ title: 'My Aesthetic Passport', text });
      else if (navigator.clipboard) {
        await navigator.clipboard.writeText(text);
        window.alert('Passport copied to clipboard!');
      } else window.prompt('Copy:', text);
    } catch (e) {
      if (e?.name !== 'AbortError') window.prompt('Copy:', text);
    }
  }

  // Circular progress math
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const dashoffset = circumference - (confidence / 100) * circumference;

  return (
    <div className="id-res-shell">
      <p className="id-card-lbl">
        ✦ Your Aesthetic Passport
        <span className="id-new-badge">NEW</span>
      </p>

      <div className="id-card-main">
        <div className="idc-header">
          <span className="idc-brand">MYNTRA IDENTITY</span>
          <div className="idc-dna-icon" aria-hidden="true">🧬</div>
        </div>

        <h1 className="idc-name">{name}</h1>
        
        <div className="idc-meta">
          <p>Style Member &nbsp;&bull;&nbsp; Since {memberSince}</p>
          <p>Fashion DNA Version {user.dnaVersion || 7}</p>
        </div>

        <div className="idc-divider" />

        <div className="idc-identity-section">
          <h2 className="idc-identity-title">{identityName}</h2>
          <p className="idc-identity-desc">{identityDescription}</p>
          
          <div className="idc-tags-row">
            {bars.slice(0, 3).map((bar, index) => (
              <span key={bar.key || bar.tag} className={`idc-tag idc-tag-${['pink', 'purple', 'blue'][index]}`}>
                {bar.label} {bar.percentage.toFixed(1)}%
              </span>
            ))}
          </div>
          
          <div className="idc-tags-row idc-tags-secondary">
            {budget && <span className="idc-tag idc-tag-pink-light">{budget}</span>}
            {occasions.slice(0, 2).map((occ) => (
              <span key={occ} className="idc-tag idc-tag-purple-light">{formatLabel(occ)}</span>
            ))}
          </div>
        </div>

        <div className="idc-divider" />

        <div className="idc-details">
          {colours.length > 0 && (
            <div className="idc-detail-row">
              <div className="idc-detail-left">
                <div className="idc-detail-icon"><Icons.Color /></div>
                <span className="idc-detail-label">Colour Palette</span>
              </div>
              <div className="idc-detail-dots"></div>
              <span className="idc-detail-value">{colours.slice(0, 4).map(formatLabel).join(', ')}</span>
            </div>
          )}
          
          {fitPreferences.length > 0 && (
            <div className="idc-detail-row">
              <div className="idc-detail-left">
                <div className="idc-detail-icon"><Icons.Fit /></div>
                <span className="idc-detail-label">Preferred Fit</span>
              </div>
              <div className="idc-detail-dots"></div>
              <span className="idc-detail-value">{fitPreferences.map(formatLabel).join(', ')}</span>
            </div>
          )}

          {user.fashionGoal && (
            <div className="idc-detail-row">
              <div className="idc-detail-left">
                <div className="idc-detail-icon"><Icons.Goal /></div>
                <span className="idc-detail-label">Fashion Goal</span>
              </div>
              <div className="idc-detail-dots"></div>
              <span className="idc-detail-value">{user.fashionGoal}</span>
            </div>
          )}
        </div>

        <div className="idc-confidence-panel">
          <div className="idc-conf-left">
            <div className="idc-conf-lbl">
              <Icons.Trend /> Style Confidence
            </div>
            <div className="idc-conf-val">{confidence}%</div>
          </div>
          
          <div className="idc-conf-ring">
            <svg width="72" height="72" viewBox="0 0 72 72">
              <circle cx="36" cy="36" r={radius} fill="none" stroke="var(--color-primary-soft)" opacity="0.3" strokeWidth="6" />
              <circle cx="36" cy="36" r={radius} fill="none" stroke="var(--color-primary)" strokeWidth="6" strokeLinecap="round"
                style={{
                  strokeDasharray: circumference,
                  strokeDashoffset: dashoffset,
                  transform: 'rotate(-90deg)',
                  transformOrigin: '50% 50%'
                }}
              />
            </svg>
            <div className="idc-conf-sparkle" style={{ transform: `rotate(${(confidence / 100) * 360}deg)` }}>
              <span style={{ transform: 'translateY(-28px) rotate(-45deg)' }}>✨</span>
            </div>
          </div>
        </div>

        <div className="idc-conf-grid">
          <div className="idc-cg-item">
            <div className="idc-cg-icon pink"><Icons.List /></div>
            <span className="idc-cg-lbl">Quiz completeness:</span>
            <strong className="idc-cg-val">{confBreakdown.quiz_completeness ?? 0}/40</strong>
          </div>
          <div className="idc-cg-item">
            <div className="idc-cg-icon blue"><Icons.Shield /></div>
            <span className="idc-cg-lbl">Answer consistency:</span>
            <strong className="idc-cg-val">{confBreakdown.answer_consistency ?? 0}/25</strong>
          </div>
          <div className="idc-cg-item">
            <div className="idc-cg-icon purple"><Icons.Check /></div>
            <span className="idc-cg-lbl">Preference coverage:</span>
            <strong className="idc-cg-val">{confBreakdown.preference_coverage ?? 0}/20</strong>
          </div>
          <div className="idc-cg-item">
            <div className="idc-cg-icon yellow"><Icons.User /></div>
            <span className="idc-cg-lbl">Behaviour evidence:</span>
            <strong className="idc-cg-val">{confBreakdown.behavior_evidence ?? 0}/15</strong>
          </div>
        </div>

        <div className="idc-footer">
          <span>Quiz answers: <strong>{evidence.quiz_answers ?? 0}</strong></span>
          <div className="idc-footer-div" />
          <span>Behaviour events: <strong>{evidence.behavior_events ?? 0}</strong></span>
        </div>
      </div>

      <div className="id-actions">
        <button className="id-btn id-btn-outline" onClick={() => navigate('/profile')}>
          <Icons.Edit /> Edit Identity
        </button>
        <button className="id-btn id-btn-solid" onClick={share}>
          <Icons.Share /> Share My Aesthetic Passport
        </button>
        <button className="id-btn id-btn-outline" onClick={() => navigate('/home')}>
          Enter My Myntra &rarr;
        </button>
      </div>
    </div>
  );
}
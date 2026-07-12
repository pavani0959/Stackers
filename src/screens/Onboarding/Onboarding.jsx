import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import '../../styles/Onboarding.css';

// Step 1: Gender + Age
export function OnboardGender() {
  const navigate = useNavigate();
  const { user, updateUser } = useUser();
  const [gender, setGender] = useState(user.gender || 'female');
  const [age, setAge] = useState(user.age || 21);

  const next = () => {
    updateUser({ gender, age });
    navigate('/onboard/budget');
  };

  return (
    <div className="screen ob-screen">
      <div className="ob-prog-wrap">
        {[0,1,2,3].map(i => <div key={i} className={`ob-dot ${i===0?'active':''}`} />)}
      </div>
      <h1 className="ob-title">Before we begin,<br />let's understand you 👋</h1>
      <p className="ob-sub">No boring signup. Just a quick conversation.</p>

      <label className="ob-label">How do you identify?</label>
      <div className="gender-grid">
        {[{id:'male',icon:'🙋‍♂️',label:'Male'},{id:'female',icon:'🙋‍♀️',label:'Female'},{id:'nonbinary',icon:'🌈',label:'Non-Binary / Prefer not to say',wide:true}].map(g => (
          <div key={g.id} className={`gender-card ${g.wide?'wide':''} ${gender===g.id?'sel':''}`} onClick={() => setGender(g.id)}>
            <span className="g-icon">{g.icon}</span>
            <span className="g-label">{g.label}</span>
          </div>
        ))}
      </div>

      <label className="ob-label">Your age</label>
      <div className="age-num grad-text">{age}</div>
      <input type="range" className="age-slider" min="13" max="35" value={age} onChange={e => setAge(Number(e.target.value))} />

      <div className="ob-footer">
        <button className="btn-primary" onClick={next}>Continue →</button>
      </div>
    </div>
  );
}

// Step 2: Budget
export function OnboardBudget() {
  const navigate = useNavigate();
  const { user, updateUser } = useUser();
  const [budget, setBudget] = useState(user.budget || 'campus-casual');

  const budgets = [
    { id: 'budget-explorer', label: 'Budget Explorer', range: 'Under ₹500' },
    { id: 'smart-spender',   label: 'Smart Spender',   range: '₹500 – ₹1,500' },
    { id: 'campus-casual',   label: 'Campus Casual',   range: '₹1,500 – ₹3,000' },
    { id: 'style-investor',  label: 'Style Investor',  range: '₹3,000 – ₹7,000' },
    { id: 'luxury-seeker',   label: 'Luxury Seeker',   range: '₹7,000+' },
  ];

  const next = () => { updateUser({ budget }); navigate('/onboard/colours'); };

  return (
    <div className="screen ob-screen">
      <div className="ob-prog-wrap">
        {[0,1,2,3].map(i => <div key={i} className={`ob-dot ${i===0?'done':''} ${i===1?'active':''}`} />)}
      </div>
      <h1 className="ob-title">What's your outfit budget? 💸</h1>
      <p className="ob-sub">Per outfit. Be honest — no judgment here.</p>

      <div className="budget-list">
        {budgets.map(b => (
          <div key={b.id} className={`budget-opt ${budget===b.id?'sel':''}`} onClick={() => setBudget(b.id)}>
            <div><div className="budget-name">{b.label}</div><div className="budget-range">{b.range}</div></div>
            <div className="budget-chk">{budget===b.id?'✓':''}</div>
          </div>
        ))}
      </div>

      <div className="ob-footer">
        <button className="btn-primary" onClick={next}>Continue →</button>
      </div>
    </div>
  );
}

// Step 3: Colours
export function OnboardColours() {
  const navigate = useNavigate();
  const { user, updateUser } = useUser();
  const [selected, setSelected] = useState(user.colours || ['#F5F0E8', '#8BA7BF', '#B0B0B0']);

  const colours = ['#F5F0E8','#1A1A1A','#8B7355','#C4A882','#4A6741','#8BA7BF','#D4B8C0','#E86D6D','#5B4FCF','#F5C842','#2C7865','#B0B0B0','#FFFFFF','#FF7043'];

  const toggle = (c) => setSelected(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]);
  const next = () => { updateUser({ colours: selected }); navigate('/onboard/occasions'); };

  return (
    <div className="screen ob-screen">
      <div className="ob-prog-wrap">
        {[0,1,2,3].map(i => <div key={i} className={`ob-dot ${i<2?'done':''} ${i===2?'active':''}`} />)}
      </div>
      <h1 className="ob-title">Your colour palette 🎨</h1>
      <p className="ob-sub">Pick the colours that feel like you.</p>

      <div className="colour-grid">
        {colours.map(c => (
          <div key={c} className={`col-chip ${selected.includes(c)?'sel':''}`}
            style={{ background: c, borderColor: c === '#FFFFFF' ? 'rgba(255,255,255,0.25)' : 'transparent' }}
            onClick={() => toggle(c)}
          />
        ))}
      </div>

      <div className="ob-footer">
        <button className="btn-primary" onClick={next}>Continue →</button>
      </div>
    </div>
  );
}

// Step 4: Occasions
export function OnboardOccasions() {
  const navigate = useNavigate();
  const { user, updateUser } = useUser();
  const [selected, setSelected] = useState(user.occasions || ['campus', 'fest', 'dates', 'gym']);

  const all = [
    { id:'campus',    label:'🎓 College / Campus' },
    { id:'work',      label:'💼 Internship / Work' },
    { id:'fest',      label:'🎉 Fests & Events' },
    { id:'night-out', label:'🌙 Night Outs' },
    { id:'dates',     label:'📅 Dates' },
    { id:'puja',      label:'🙏 Puja / Festivals' },
    { id:'travel',    label:'✈️ Travel' },
    { id:'gym',       label:'🏃 Gym / Sports' },
    { id:'cafe',      label:'☕ Cafe Hangouts' },
    { id:'concerts',  label:'🎤 Concerts' },
    { id:'photos',    label:'📸 Photoshoots' },
    { id:'home',      label:'🏡 Home / Casual' },
  ];

  const toggle = (id) => setSelected(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  const next = () => { updateUser({ occasions: selected, hasCompletedOnboarding: true }); navigate('/quiz'); };

  return (
    <div className="screen ob-screen">
      <div className="ob-prog-wrap">
        {[0,1,2,3].map(i => <div key={i} className={`ob-dot ${i<3?'done':''} ${i===3?'active':''}`} />)}
      </div>
      <h1 className="ob-title">When do you dress up? 📅</h1>
      <p className="ob-sub">Pick all the occasions that matter to you.</p>

      <div className="chip-grid">
        {all.map(o => (
          <div key={o.id} className={`chip ${selected.includes(o.id)?'selected':''}`} onClick={() => toggle(o.id)}>
            {o.label}
          </div>
        ))}
      </div>

      <div className="ob-footer">
        <button className="btn-primary" onClick={next}>Start DNA Quiz ✨</button>
      </div>
    </div>
  );
}

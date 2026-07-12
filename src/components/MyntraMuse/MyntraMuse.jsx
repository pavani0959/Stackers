import { useState, useRef, useEffect } from 'react';
import { useUser } from '../../context/UserContext';
import './MyntraMuse.css';

export default function MyntraMuse() {
  const { user } = useUser();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'ai', text: `Hi! I'm Myntra Muse, your personal AI Stylist. I see your vibe is ${user.identityName || 'Minimalist'}. How can I help you today?` }
  ]);
  const [input, setInput] = useState('');
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    
    // Add user message
    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInput('');

    // Call backend API instead of hardcoded responses
    fetch('http://localhost:8000/api/muse/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMsg, user_profile: user })
    })
    .then(res => res.json())
    .then(data => {
      setMessages(prev => [...prev, { role: 'ai', text: data.reply }]);
    })
    .catch(err => {
      console.error(err);
      setMessages(prev => [...prev, { role: 'ai', text: 'Oops, I am having trouble connecting to my brain right now!' }]);
    });
  };

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <div className="muse-fab" onClick={() => setIsOpen(true)}>
          <span className="muse-icon">✨</span>
        </div>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="muse-window">
          <div className="muse-hdr">
            <div className="muse-hdr-title">
              <span className="muse-icon-small">✨</span> Myntra Muse
            </div>
            <div className="muse-close" onClick={() => setIsOpen(false)}>×</div>
          </div>
          
          <div className="muse-body">
            {messages.map((m, idx) => (
              <div key={idx} className={`muse-msg ${m.role}`}>
                <div className="muse-bubble">{m.text}</div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          
          <div className="muse-footer">
            <input 
              className="muse-input"
              type="text" 
              placeholder="Ask for style advice..." 
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
            />
            <button className="muse-send" onClick={handleSend}>↑</button>
          </div>
        </div>
      )}
    </>
  );
}

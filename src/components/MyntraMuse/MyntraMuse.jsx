import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../context/useUser';
import { apiRequest } from '../../api/client';
import './MyntraMuse.css';
import {
  X,
} from 'lucide-react';

export default function MyntraMuse() {
  const navigate = useNavigate();
  const { user } = useUser();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  useEffect(() => {
    if (!isOpen || messages.length > 0) return;

    const firstName = user.name?.trim().split(' ')[0] || 'Style Explorer';
    const identity = user.identityName || 'your evolving Fashion DNA';
    setMessages([
      {
        role: 'ai',
        text: `Hi ${firstName}! I'm Myntra Muse. I can use ${identity} and the live catalogue to help you shop.`,
        recommendations: [],
      },
    ]);
  }, [isOpen, messages.length, user.identityName, user.name]);

  const handleSend = async () => {
    const userMessage = input.trim();
    if (!userMessage || sending) return;

    setMessages((previous) => [
      ...previous,
      { role: 'user', text: userMessage, recommendations: [] },
    ]);
    setInput('');
    setSending(true);

    try {
      const data = await apiRequest('/api/muse/chat', {
        method: 'POST',
        body: JSON.stringify({ message: userMessage, user_profile: user }),
      });
      setMessages((previous) => [
        ...previous,
        {
          role: 'ai',
          text: data.reply,
          intent: data.intent,
          recommendations: data.recommendations || [],
        },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((previous) => [
        ...previous,
        {
          role: 'ai',
          text: 'I could not reach the Myntra Identity catalogue right now. Please try again.',
          recommendations: [],
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <>
      {!isOpen && (
        <button
          className="muse-fab"
          onClick={() => setIsOpen(true)}
          aria-label="Open Myntra Muse"
          type="button"
        >
          <span className="muse-icon">✨</span>
        </button>
      )}

      {isOpen && (
        <div className="muse-window">
          <div className="muse-hdr">
            <div className="muse-hdr-title">
              <span className="muse-icon-small">✨</span> Myntra Muse
            </div>
            <button
              className="muse-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close Myntra Muse"
              type="button"
            >
              <X
                aria-hidden="true"
                size={20}
              />
            </button>
          </div>

          <div className="muse-body">
            {messages.map((message, index) => (
              <div key={`${message.role}-${index}`} className={`muse-msg ${message.role}`}>
                <div className="muse-message-stack">
                  <div className="muse-bubble">{message.text}</div>

                  {message.recommendations?.length > 0 && (
                    <div className="muse-recommendations">
                      {message.recommendations.map((product) => (
                        <button
                          key={product.id}
                          className="muse-product"
                          onClick={() => {
                            setIsOpen(false);
                            navigate(`/product/${product.id}`);
                          }}
                          type="button"
                        >
                          <img src={product.image} alt="" />
                          <span>
                            <strong>{product.name}</strong>
                            <small>₹{product.price.toLocaleString('en-IN')}</small>
                          </span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {sending && (
              <div className="muse-msg ai">
                <div className="muse-bubble muse-typing">Checking your DNA and live catalogue…</div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="muse-footer">
            <input
              className="muse-input"
              type="text"
              placeholder="Ask for style advice..."
              value={input}
              disabled={sending}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => event.key === 'Enter' && handleSend()}
            />
            <button
              className="muse-send"
              onClick={handleSend}
              disabled={sending || !input.trim()}
              type="button"
            >
              ↑
            </button>
          </div>
        </div>
      )}
    </>
  );
}

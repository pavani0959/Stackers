import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Camera, Upload, Share2, Download, CheckCircle, XCircle, Flame, Trophy } from 'lucide-react';
import { getAuthToken } from '../../api/auth';
import '../../styles/Streak.css';

export default function Streak() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const exportRef = useRef(null);

  const [loading, setLoading] = useState(true);
  const [taskData, setTaskData] = useState(null);
  const [streakData, setStreakData] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  
  const [cameraActive, setCameraActive] = useState(false);
  const [stream, setStream] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  
  const [submitting, setSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState(null); 
  
  const [timeUntilTomorrow, setTimeUntilTomorrow] = useState('');

  useEffect(() => {
    fetchData();
    const interval = setInterval(updateCountdown, 1000);
    updateCountdown();
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const token = getAuthToken();
      if (!token) return navigate('/splash');
      
      const headers = { 'Authorization': `Bearer ${token}` };
      
      const [taskRes, streakRes, lbRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/streaks/today', { headers }),
        fetch('http://127.0.0.1:8000/api/streaks/me', { headers }),
        fetch('http://127.0.0.1:8000/api/streaks/leaderboard', { headers })
      ]);
      
      setTaskData(await taskRes.json());
      setStreakData(await streakRes.json());
      setLeaderboard(await lbRes.json());
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  const updateCountdown = () => {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setUTCHours(24, 0, 0, 0); 
    const diff = tomorrow - now;
    
    if (diff <= 0) {
      setTimeUntilTomorrow('00:00:00');
      return;
    }
    
    const h = Math.floor(diff / (1000 * 60 * 60));
    const m = Math.floor((diff / 1000 / 60) % 60);
    const s = Math.floor((diff / 1000) % 60);
    setTimeUntilTomorrow(`${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`);
  };

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } 
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setCameraActive(true);
    } catch (err) {
      console.error('Camera access denied:', err);
      alert('Could not access camera. Please upload a photo instead.');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setCameraActive(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
    setCapturedImage(dataUrl);
    stopCamera();
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => setCapturedImage(e.target.result);
    reader.readAsDataURL(file);
  };

  const submitPhoto = async () => {
    if (!capturedImage) return;
    setSubmitting(true);
    
    try {
      const res = await fetch('http://127.0.0.1:8000/api/streaks/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({ image_b64: capturedImage })
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Submission failed');
      
      setSubmitResult(data);
      if (data.passed) {
        fetchData();
      }
    } catch (err) {
      console.error(err);
      alert(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleShare = async () => {
    const text = `I'm on a ${streakData?.current_streak}-day style streak on MyStyle! Can you beat me? 🔥`;
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'MyStyle Streak',
          text,
          url: window.location.origin
        });
      } catch (err) {
        console.error(err);
      }
    } else {
      navigator.clipboard.writeText(text);
      alert('Copied to clipboard!');
    }
  };

  const handleExport = () => {
    const canvas = document.createElement('canvas');
    canvas.width = 600;
    canvas.height = 800;
    const ctx = canvas.getContext('2d');
    
    const gradient = ctx.createLinearGradient(0, 0, 600, 800);
    gradient.addColorStop(0, '#fdfbfb');
    gradient.addColorStop(1, '#ebedee');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 600, 800);
    
    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 48px -apple-system, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('MyStyle Streak', 300, 120);
    
    const dnaGradient = ctx.createLinearGradient(100, 200, 500, 400);
    dnaGradient.addColorStop(0, '#ec4899');
    dnaGradient.addColorStop(1, '#8b5cf6');
    
    ctx.fillStyle = dnaGradient;
    ctx.font = 'bold 180px -apple-system, sans-serif';
    ctx.fillText(streakData?.current_streak || 0, 300, 360);
    
    ctx.fillStyle = '#64748b';
    ctx.font = '32px -apple-system, sans-serif';
    ctx.fillText('DAYS', 300, 420);
    
    ctx.fillStyle = '#0f172a';
    ctx.font = '24px -apple-system, sans-serif';
    ctx.fillText(new Date().toLocaleDateString(), 300, 700);
    
    const link = document.createElement('a');
    link.download = 'mystyle-streak.png';
    link.href = canvas.toDataURL();
    link.click();
  };

  if (loading) {
    return <div className="streak-screen"><div className="loading">Loading...</div></div>;
  }

  const isSubmitted = taskData?.is_submitted || submitResult?.passed;

  return (
    <div className="streak-screen">
      <div className="streak-hdr">
        <button className="back-btn" onClick={() => navigate('/profile')}>
          <ArrowLeft size={21} />
        </button>
        <div className="streak-hdr-title">Daily Streak</div>
        <div style={{ width: 21 }}></div>
      </div>

      <div className="streak-body">
        <div className="streak-hero">
          <div className="streak-circle" ref={exportRef}>
            <div className="streak-number">{streakData?.current_streak || 0}</div>
            <div className="streak-label">DAYS</div>
          </div>
          <div className="streak-stats">
            <span><Flame size={16} /> Current: {streakData?.current_streak || 0}</span>
            <span><Trophy size={16} /> Best: {streakData?.longest_streak || 0}</span>
          </div>
          
          <div className="streak-actions">
            <button className="streak-action-btn" onClick={handleShare}>
              <Share2 size={16} /> Share
            </button>
            <button className="streak-action-btn" onClick={handleExport}>
              <Download size={16} /> Export
            </button>
          </div>
        </div>

        <div className="streak-card">
          <div className="streak-card-header">
            <h3>Today's Challenge</h3>
            <span className="countdown">New in {timeUntilTomorrow}</span>
          </div>
          <div className="task-prompt">
            "{taskData?.prompt_text}"
          </div>

          {isSubmitted ? (
            <div className="submission-success">
              <CheckCircle size={48} className="success-icon" />
              <h4>Challenge Completed!</h4>
              <p>Come back tomorrow for your next task.</p>
            </div>
          ) : (
            <div className="submission-area">
              {submitResult && !submitResult.passed && (
                <div className="submission-error">
                  <XCircle size={20} />
                  <div>
                    <strong>Verification Failed</strong>
                    <p>{submitResult.reasoning}</p>
                  </div>
                </div>
              )}

              {!cameraActive && !capturedImage && (
                <div className="capture-options">
                  <button className="capture-btn primary" onClick={startCamera}>
                    <Camera size={20} /> Take Photo
                  </button>
                  <label className="capture-btn secondary">
                    <Upload size={20} /> Upload Photo
                    <input type="file" accept="image/*" onChange={handleFileUpload} hidden />
                  </label>
                </div>
              )}

              {cameraActive && (
                <div className="camera-view">
                  <video ref={videoRef} autoPlay playsInline muted className="camera-video" />
                  <div className="camera-controls">
                    <button className="btn-capture-round" onClick={capturePhoto}></button>
                    <button className="btn-cancel" onClick={stopCamera}>Cancel</button>
                  </div>
                </div>
              )}

              {capturedImage && (
                <div className="preview-view">
                  <img src={capturedImage} alt="Captured" className="image-preview" />
                  <div className="preview-controls">
                    <button className="btn-cancel" onClick={() => setCapturedImage(null)} disabled={submitting}>
                      Retake
                    </button>
                    <button className="btn-submit" onClick={submitPhoto} disabled={submitting}>
                      {submitting ? 'Verifying...' : 'Submit'}
                    </button>
                  </div>
                </div>
              )}
              
              <canvas ref={canvasRef} style={{ display: 'none' }} />
            </div>
          )}
        </div>

        <div className="streak-card">
          <div className="streak-card-header">
            <h3>Leaderboard</h3>
          </div>
          <div className="leaderboard-list">
            {leaderboard.map((user, idx) => (
              <div key={user.user_id} className={`lb-item ${idx < 3 ? 'top-3' : ''}`}>
                <div className="lb-rank">{idx + 1}</div>
                <img src={user.avatar_url || '/catalog/fallback-product.webp'} alt={user.name} className="lb-avatar" />
                <div className="lb-name">{user.name}</div>
                <div className="lb-score">
                  <Flame size={14} /> {user.current_streak}
                </div>
              </div>
            ))}
            {leaderboard.length === 0 && (
              <div className="empty-state">No one has started a streak yet!</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

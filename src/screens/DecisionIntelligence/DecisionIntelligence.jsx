import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getDecision } from '../../api/decisions';
import ApiErrorState from '../../components/ApiErrorState/ApiErrorState';
import { useUser } from '../../context/useUser';
import { useReducedMotion } from '../../hooks/useReducedMotion';
import { gsap, useGSAP } from '../../motion/gsap';
import '../../styles/DecisionIntelligence.css';

export default function DecisionIntelligence() {
  const { id: snapshotId } = useParams();
  const navigate = useNavigate();
  const { addToCart, createUserEvent } = useUser();
  const reducedMotion = useReducedMotion();
  const root = useRef(null);
  const [decision, setDecision] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadDecision() {
      setLoading(true);
      setError(null);
      try {
        const data = await getDecision(snapshotId);
        if (!cancelled) {
          setDecision(data);
        }
      } catch (requestError) {
        if (!cancelled) {
          setError(requestError);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadDecision();
    return () => {
      cancelled = true;
    };
  }, [snapshotId, retryKey]);

  // Run GSAP only after decision data is loaded
  useGSAP(
    () => {
      if (!decision || reducedMotion) return;

      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

      // Hero section slides in
      tl.from('[data-di-hero]', { y: 24, opacity: 0, duration: 0.45 });

      // Overall score counts up
      const scoreEl = document.querySelector('[data-di-score]');
      if (scoreEl) {
        const obj = { val: 0 };
        tl.to(
          obj,
          {
            val: decision.overall_score,
            duration: 0.9,
            ease: 'power2.out',
            onUpdate: () => {
              scoreEl.textContent = Math.round(obj.val);
            },
          },
          '-=0.2',
        );
      }

      // Summary fades in
      tl.from('[data-di-summary]', { opacity: 0, y: 12, duration: 0.35 }, '-=0.3');

      // Reason cards stagger in
      tl.from('[data-di-reason]', { y: 18, opacity: 0, stagger: 0.1, duration: 0.4 }, '-=0.1');

      // Warning cards after reasons
      tl.from('[data-di-warn]', { y: 14, opacity: 0, stagger: 0.08, duration: 0.35 }, '-=0.05');

      // Limitations + meta fade in together
      tl.from('[data-di-limitations], [data-di-meta]', { opacity: 0, duration: 0.3 }, '-=0.1');
    },
    { scope: root, dependencies: [decision, reducedMotion] },
  );

  if (loading) {
    return <div className="screen-center">Loading decision intelligence…</div>;
  }

  if (error) {
    return (
      <ApiErrorState
        error={error}
        title="Decision snapshot could not be loaded"
        onRetry={() => setRetryKey((value) => value + 1)}
      />
    );
  }

  if (!decision) {
    return <div className="screen-center">Decision snapshot not found.</div>;
  }

  const product = decision.product;

  function handleAddToCart() {
    addToCart({
      ...product,
      selectedSize: 'S',
      decisionSnapshotId: decision.snapshot_id,
      recommendationItemId: decision.recommendation_item_id,
    });
    createUserEvent({
      event_type: 'cart_add',
      product_id: product.id,
      recommendation_item_id: decision.recommendation_item_id,
      metadata: {
        size: 'S',
        match_score: decision.overall_score,
        model_version: decision.model_version,
        profile_version: decision.profile_version,
        decision_snapshot_id: decision.snapshot_id,
        source: 'decision_intelligence',
      },
    }).catch(() => {});
    navigate(-1);
  }

  return (
    <div className="screen di-screen" ref={root}>
      <header className="di-hdr">
        <button type="button" className="back-btn" onClick={() => navigate(-1)}>
          ←
        </button>
        <div className="di-hdr-text">
          <h3>Decision Intelligence</h3>
          <h2>Why this recommendation?</h2>
        </div>
      </header>

      <main className="di-body">
        <section className="di-hero" data-di-hero>
          <img src={product.image} alt={product.name} />
          <div className="di-hero-info">
            <span className="di-hero-brand">{product.brand}</span>
            <strong className="di-hero-name">{product.name}</strong>
            <span className="di-hero-score">
              Confidence: <span data-di-score>{decision.overall_score}</span>
            </span>
          </div>
        </section>

        <p className="di-summary" data-di-summary>{decision.explanation.summary}</p>
        <p className="di-sec-label">Evidence-backed reasons</p>

        {decision.explanation.reasons.map((reason) => (
          <article className="di-reason" key={reason.code} data-di-reason>
            <div>
              <h4>
                {reason.title} ({reason.score}%)
              </h4>
              <p>{reason.detail}</p>
              <small>Source: {reason.evidence_source}</small>
            </div>
          </article>
        ))}

        {decision.regret_signals.length > 0 && (
          <p className="di-sec-label">Regret signals</p>
        )}
        {decision.regret_signals.map((signal) => (
          <article
            className={`di-warn ${signal.severity}`}
            key={signal.code}
            data-di-warn
          >
            <div>
              <strong>{signal.title}</strong>
              <p>{signal.detail}</p>
            </div>
          </article>
        ))}

        <p className="di-sec-label">Limitations</p>
        <ul className="di-limitations" data-di-limitations>
          {decision.explanation.limitations.map((limitation) => (
            <li key={limitation}>{limitation}</li>
          ))}
        </ul>

        <div className="di-meta" data-di-meta>
          <span>Model: {decision.model_version}</span>
          <span>Profile version: {decision.profile_version}</span>
          <span>Snapshot: {decision.snapshot_id}</span>
        </div>

        <button type="button" className="primary-btn" onClick={handleAddToCart}>
          Got it — Add to Cart
        </button>
      </main>
    </div>
  );
}

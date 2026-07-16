import { useEffect, useState } from 'react';

/**
 * Returns true when the user has requested reduced motion via OS/browser settings.
 * Use this to skip or simplify GSAP animations.
 */
export function useReducedMotion() {
  const [reduced, setReduced] = useState(
    () =>
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  );

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');

    function handleChange(event) {
      setReduced(event.matches);
    }

    mq.addEventListener('change', handleChange);
    return () => mq.removeEventListener('change', handleChange);
  }, []);

  return reduced;
}

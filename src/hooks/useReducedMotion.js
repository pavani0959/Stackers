import {
  useEffect,
  useState,
} from 'react';


const REDUCED_MOTION_QUERY =
  '(prefers-reduced-motion: reduce)';


function getInitialPreference() {
  if (
    typeof window === 'undefined'
    || typeof window.matchMedia
      !== 'function'
  ) {
    return false;
  }

  return window
    .matchMedia(
      REDUCED_MOTION_QUERY,
    )
    .matches;
}


export function useReducedMotion() {
  const [
    prefersReducedMotion,
    setPrefersReducedMotion,
  ] = useState(
    getInitialPreference,
  );

  useEffect(() => {
    if (
      typeof window === 'undefined'
      || typeof window.matchMedia
        !== 'function'
    ) {
      return undefined;
    }

    const mediaQuery =
      window.matchMedia(
        REDUCED_MOTION_QUERY,
      );

    function handleChange(event) {
      setPrefersReducedMotion(
        event.matches,
      );
    }

    setPrefersReducedMotion(
      mediaQuery.matches,
    );

    if (
      typeof mediaQuery.addEventListener
      === 'function'
    ) {
      mediaQuery.addEventListener(
        'change',
        handleChange,
      );

      return () => {
        mediaQuery.removeEventListener(
          'change',
          handleChange,
        );
      };
    }

    mediaQuery.addListener(
      handleChange,
    );

    return () => {
      mediaQuery.removeListener(
        handleChange,
      );
    };
  }, []);

  return prefersReducedMotion;
}


export default useReducedMotion;

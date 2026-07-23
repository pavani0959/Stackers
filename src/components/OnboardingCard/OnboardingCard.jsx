import React from 'react';
import './OnboardingCard.css';

export default function OnboardingCard({ children, footer, className = '' }) {
  return (
    <div className={`ob-shared-card ${className}`}>
      <div className="ob-shared-card-scroll">
        {children}
      </div>
      {footer && (
        <div className="ob-shared-card-footer">
          {footer}
        </div>
      )}
    </div>
  );
}

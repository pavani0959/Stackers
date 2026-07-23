import React from 'react';

// Single source of truth for onboarding step count and progress rendering.
// Change totalSteps here or via prop if a 5th step is ever added.
export default function OnboardingProgress({ currentStep, totalSteps = 4 }) {
  return (
    <div className="ob-prog-wrap">
      {Array.from({ length: totalSteps }).map((_, i) => {
        const stepIndex = i + 1; // 1-indexed
        let statusClass = '';
        
        if (stepIndex < currentStep) {
          statusClass = 'done';
        } else if (stepIndex === currentStep) {
          statusClass = 'active';
        }
        
        return (
          <div 
            key={i} 
            className={`ob-bar ${statusClass}`} 
          />
        );
      })}
    </div>
  );
}

import React, { useState, useEffect, useRef } from 'react';
import { Button } from 'react-bootstrap';
import { FaTimes, FaChevronRight, FaChevronLeft } from 'react-icons/fa';

const FeatureTour = ({ steps, onComplete, isActive }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const [arrowPosition, setArrowPosition] = useState('bottom');
  const tooltipRef = useRef(null);
  
  useEffect(() => {
    if (!isActive || !steps.length) return;
    
    const targetElement = document.querySelector(steps[currentStep].selector);
    
    if (targetElement) {
      // Add spotlight to the target element
      targetElement.classList.add('tour-spotlight');
      
      // Calculate position for tooltip
      positionTooltip(targetElement);
      
      // Scroll to make sure the element is visible
      targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    return () => {
      // Clean up spotlight when component unmounts
      if (targetElement) {
        targetElement.classList.remove('tour-spotlight');
      }
    };
  }, [currentStep, isActive, steps]);
  
  const positionTooltip = (targetElement) => {
    if (!targetElement || !tooltipRef.current) return;
    
    const targetRect = targetElement.getBoundingClientRect();
    const tooltipRect = tooltipRef.current.getBoundingClientRect();
    
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    
    // Default position is below the element
    let top = targetRect.bottom + 15;
    let left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);
    let arrowPos = 'top';
    
    // Check if tooltip would go off the bottom of the screen
    if (top + tooltipRect.height > windowHeight) {
      // Position above the element
      top = targetRect.top - tooltipRect.height - 15;
      arrowPos = 'bottom';
    }
    
    // Check if tooltip would go off the left of the screen
    if (left < 10) {
      left = 10;
    }
    
    // Check if tooltip would go off the right of the screen
    if (left + tooltipRect.width > windowWidth - 10) {
      left = windowWidth - tooltipRect.width - 10;
    }
    
    setTooltipPosition({ top, left });
    setArrowPosition(arrowPos);
  };
  
  const handleNext = () => {
    // Remove spotlight from current element
    const currentElement = document.querySelector(steps[currentStep].selector);
    if (currentElement) {
      currentElement.classList.remove('tour-spotlight');
    }
    
    // Move to next step or complete
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };
  
  const handlePrevious = () => {
    // Remove spotlight from current element
    const currentElement = document.querySelector(steps[currentStep].selector);
    if (currentElement) {
      currentElement.classList.remove('tour-spotlight');
    }
    
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };
  
  const handleComplete = () => {
    // Remove spotlight from current element
    const currentElement = document.querySelector(steps[currentStep]?.selector);
    if (currentElement) {
      currentElement.classList.remove('tour-spotlight');
    }
    
    onComplete();
  };
  
  if (!isActive || !steps.length) return null;
  
  const currentTourStep = steps[currentStep];
  
  return (
    <div 
      className="tour-tooltip" 
      style={tooltipPosition}
      ref={tooltipRef}
    >
      <div className={`tour-tooltip-arrow ${arrowPosition}`}></div>
      
      <div className="d-flex justify-content-between mb-2">
        <span className="text-muted small">Step {currentStep + 1} of {steps.length}</span>
        <Button 
          variant="link" 
          className="p-0 text-muted" 
          onClick={handleComplete}
          aria-label="Close tour"
        >
          <FaTimes />
        </Button>
      </div>
      
      <h5>{currentTourStep.title}</h5>
      <p className="text-muted mb-3">{currentTourStep.content}</p>
      
      <div className="d-flex justify-content-between">
        <Button
          variant="outline-secondary"
          size="sm"
          onClick={handlePrevious}
          disabled={currentStep === 0}
        >
          <FaChevronLeft /> Back
        </Button>
        
        <Button
          variant="primary"
          size="sm"
          onClick={handleNext}
        >
          {currentStep === steps.length - 1 ? 'Finish' : 'Next'} {currentStep !== steps.length - 1 && <FaChevronRight />}
        </Button>
      </div>
    </div>
  );
};

export default FeatureTour; 
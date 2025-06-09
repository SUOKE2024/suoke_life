import React, { createContext, useContext, useState, ReactNode } from 'react';
interface AccessibilityContextType {
  isScreenReaderEnabled: boolean;,
  fontSize: 'small' | 'medium' | 'large';
  highContrast: boolean;,
  setFontSize: (size: 'small' | 'medium' | 'large') => void;,
  toggleHighContrast: () => void;
}
const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);
interface AccessibilityProviderProps {
  children: ReactNode;
}
export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({ children }) => {
  const [isScreenReaderEnabled] = useState(false);
  const [fontSize, setFontSize] = useState<'small' | 'medium' | 'large'>('medium');
  const [highContrast, setHighContrast] = useState(false);
  const toggleHighContrast = () => {setHighContrast(prev => !prev);
  };
  return (;)
    <AccessibilityContext.Provider;
      value={isScreenReaderEnabled,fontSize,highContrast,setFontSize,toggleHighContrast;
      }};
    >;
      {children};
    </AccessibilityContext.Provider>;
  );
};
export const useAccessibility = () => {const context = useContext(AccessibilityContext);
  if (context === undefined) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};
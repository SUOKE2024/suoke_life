import React, { createContext, useContext, useState } from 'react';

interface LoadingState {
  [key: string]: boolean;
}

interface LoadingContextType {
  loadingStates: LoadingState;
  setLoading: (key: string, loading: boolean) => void;
  isLoading: (key: string) => boolean;
  isAnyLoading: () => boolean;
}

const LoadingContext = createContext<LoadingContextType | null>(null);

/**
 * 加载状态Provider
 */
export const LoadingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [loadingStates, setLoadingStates] = useState<LoadingState>({});
  
  const setLoading = (key: string, loading: boolean) => {
    setLoadingStates(prev => ({
      ...prev,
      [key]: loading,
    }));
  };
  
  const isLoading = (key: string) => {
    return loadingStates[key] || false;
  };
  
  const isAnyLoading = () => {
    return Object.values(loadingStates).some(loading => loading);
  };
  
  return (
    <LoadingContext.Provider value={{
      loadingStates,
      setLoading,
      isLoading,
      isAnyLoading,
    }}>
      {children}
    </LoadingContext.Provider>
  );
};

/**
 * 使用加载状态Hook
 */
export const useLoading = () => {
  const context = useContext(LoadingContext);
  if (!context) {
    throw new Error('useLoading must be used within LoadingProvider');
  }
  return context;
};

/**
 * 自动管理加载状态的Hook
 */
export const useAsyncOperation = <T extends any[], R>(
  operation: (...args: T) => Promise<R>,
  key: string
) => {
  const { setLoading } = useLoading();
  
  return async (...args: T): Promise<R> => {
    setLoading(key, true);
    try {
      const result = await operation(...args);
      return result;
    } finally {
      setLoading(key, false);
    }
  };
};
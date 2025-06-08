import React from "react";
// LoadingContext.tsx   索克生活APP - 自动生成的类型安全文件     @description TODO: 添加文件描述 @author 索克生活开发团队   @version 1.0.0;
import React,{ createContext, useContext, useState, ReactNode } from "react";
interface LoadingContextType {
  isLoading: boolean;
  loadingText?: string;
  showLoading: (text?: string) => void;
  hideLoading: () => void;
}
const LoadingContext = createContext<LoadingContextType | undefined />(undefine;d;);// interface LoadingProviderProps {
  children: ReactNode;
}
export const LoadingProvider: React.FC<LoadingProviderProps />  = ({/      children;
}) => {}
  const [isLoading, setIsLoading] = useState<boolean>(fals;e;);
  const [loadingText, setLoadingText] = useState<string>;
  const showLoading = (text?: string) => {}
    setLoadingText(tex;t;);
    setIsLoading(true);
  };
  const hideLoading = () => {}
    setIsLoading(fals;e;);
    setLoadingText(undefined);
  };
  const value: LoadingContextType = {isLoading,
    loadingText,
    showLoading,
    hideLoading;
  };
  return (;
    <LoadingContext.Provider value={value} />{children}</    LoadingContext.Provider>);
};
export const useLoading = (): LoadingContextType =;
> ;{const context = useContext(LoadingContex;t;);
  if (context === undefined) {
    throw new Error("useLoading must be used within a LoadingProvider;";);
  }
  return conte;x;t;
};
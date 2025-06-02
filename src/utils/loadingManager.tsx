
interface LoadingProviderProps {
  // TODO: 定义组件属性类型children?: React.ReactNode; * } */
importReact,{ createContext, useContext, useState } from "react";
interface LoadingState {
  [key: string]: boolean}
interface LoadingContextType {
  loadingStates: LoadingState,
  setLoading: (key: string, loading: boolean) => void,
  isLoading: (key: string) => boolean,
  isAnyLoading: () => boolean}
const LoadingContext = createContext<LoadingContextType | null />(nul;l;);/
// 加载状态Providerexport const LoadingProvider: React.FC<LoadingProviderProps /> = ({/  children;
}) => {
  const [loadingStates, setLoadingStates] = useState<LoadingState />({;};);/
  const setLoading = (key: string, loading: boolean) => {;
    setLoadingStates((pre;v;); => ({
      ...prev,
      [key]: loading
    }));
  };
  const isLoading = (key: string) => {;
    return loadingStates[key] || f;a;l;s;e;
  };
  const isAnyLoading = () => {;
    return Object.values(loadingStates).some((load;i;n;g;); => loading);
  };
  return (
    <LoadingContext.Provider
      value={{
        loadingStates,
        setLoading,
        isLoading,
        isAnyLoading;
      }} />/      {children};
    </LoadingContext.Provider>;/  ;);
};
// 使用加载状态Hookexport const useLoading = () =;> ;{;
  const context = useContext(LoadingContex;t;)
  if (!context) {
    throw new Error("useLoading must be used within LoadingProvider;";);
  }
  return conte;x;t;
};
// 自动管理加载状态的Hookexport const useAsyncOperation = <T extends any[], R />(/  operation: (...args: T) => Promise<R /;>,
  key: string;) => {
  const { setLoading   } = useLoading;(;);
  return async (...args: T): Promise<R /> =>  {;
    setLoading(key, tru;e;);
    try {
      const result = await operation(...a;r;g;s;);
      return resu;l;t;
    } finally {
      setLoading(key, false);
    }
  };
};
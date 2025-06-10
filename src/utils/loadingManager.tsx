import React from "react";";
interface LoadingProviderProps {}}
}
  // TODO: 定义组件属性类型children?: React.ReactNode *;}"/;"/g"/;
}";,"";
import React,{ createContext, useContext, useState } from "react";";
interface LoadingState {}}
}
  [key: string]: boolean;}
}
interface LoadingContextType {loadingStates: LoadingState}setLoading: (key: string, loading: boolean) => void,;
isLoading: (key: string) => boolean,;
}
}
  isAnyLoading: () => boolean;}
}
const LoadingContext = createContext<LoadingContextType | null  />(nul;l;); 加载状态Providerexport const LoadingProvider: React.FC<LoadingProviderProps  />  = ({/      children;)}/;/g/;
}) => {}
  const [loadingStates, setLoadingStates] = useState<LoadingState  />({};);// setLoading: useCallback((key: string, loading: boolean) => {;}/;,/g/;
setLoadingStates(pre;v;); => ({));}      ...prev,);
}
      [key]: loading;)}
    }));
  };
const isLoading = useCallback((key: string) => {;}
    return loadingStates[key] || f;a;l;s;e;
  };
const  isAnyLoading = useCallback(() => {}
    return Object.values(loadingStates).some(load;i;n;g;); => loading);
  };
return (;);
    <LoadingContext.Provider;  />/;,/g/;
value={loadingStates}setLoading,;
isLoading,;
}
        isAnyLoading;}
      }} />/          {children};/;/g/;
    </    LoadingContext.Provider>);/;/g/;
};
// 使用加载状态Hookexport const useLoading = () =;/;/g/;
> ;{const context = useContext(LoadingContex;t;);";,}if (!context) {";}}"";
    const throw = new Error("useLoading must be used within LoadingProvider;";);"}"";"";
  }
  return conte;x;t;
};
/  ///  >;/;/g/;
>,key: string;) => {}
  const { setLoading   } = useLoading;
return async (...args: T): Promise<R /    > => {;}/;,/g/;
setLoading(key, tru;e;);
try {const result = await operation(...a;r;g;s;);}}
      return result;}
    } finally {}}
      setLoading(key, false);}
    }
  };";"";
};""";
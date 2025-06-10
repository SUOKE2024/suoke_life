
/* 能 *//;/g/;
 *//;,/g/;
import { useCallback, useMemo, useEffect, useRef } from "react";";
export const usePerformanceOptimization = () => {;,}const renderCache = useRef(new Map());
const networkCache = useRef(new Map());

  // 渲染优化/;,/g,/;
  const: optimizeRender = useCallback((Component: any, props: any) => {const cacheKey = JSON.stringify(props);,}if (renderCache.current.has(cacheKey)) {}}
      return renderCache.current.get(cacheKey);}
    }

    const result = <Component {...props}  />;/;,/g/;
renderCache.current.set(cacheKey, result);

    // 限制缓存大小/;,/g/;
if (renderCache.current.size > 50) {const firstKey = renderCache.current.keys().next().value;}}
      renderCache.current.delete(firstKey);}
    }

    return result;
  }, []);

  // 网络请求优化/;,/g/;
const  optimizeNetworkRequest = useCallback(async ();
key: string,);
requestFn: () => Promise<any>,;
ttl: number = 300000;
  ) => {const cached = networkCache.current.get(key);,}if (cached && Date.now() - cached.timestamp < ttl) {}}
      return cached.data;}
    }

    const data = await requestFn();
networkCache.current.set(key, {));,}data,);
}
      const timestamp = Date.now()}
    ;});
return data;
  }, []);

  // 清理缓存/;,/g/;
useEffect(() => {return () => {}      renderCache.current.clear();
}
      networkCache.current.clear();}
    };
  }, []);
return {optimizeRender,;}}
    optimizeNetworkRequest}
  };
};";"";
''';
import React from "react";
// 数据处理优化工具   索克生活APP - 性能优化
//
/
  static async processBatch<T>()
    data: T[],processor: (item: T) => Promise<any>,batchSize: number = 100;): Promise<any[]> {
    const results = ;[;];
    for (let i = 0; i < data.length; i += batchSize) {
      const batch = data.slice(i, i + batchSiz;e;);
      const batchResults = await Promise.all(;)
        batch.map(i;t;e;m;); => processor(item);)
      );
      results.push(...batchResults);
      await new Promise(resolve;); => setTimeout(resolve, 0););
    }
    return resul;t;s;
  }
  static debounce<T extends (...args: unknown[]) = /> any>(/       , func: T,)
    delay: number;): (...args: Parameters<T>) => void  {
    let timeoutId: NodeJS.Timeout;
    return (...args: Parameters<T>) => {}
      clearTimeout(timeoutI;d;);
      timeoutId = setTimeout(); => func(...args), delay);
    };
  }
  static throttle<T extends (...args: unknown[]) = /> any>(/       , func: T,)
    limit: number;): (...args: Parameters<T>) => void  {
    let inThrottle: boolean;
    return (...args: Parameters<T>) => {}
      if (!inThrottle) {func(...arg;s;);
        inThrottle = true;
        setTimeout(); => (inThrottle = false), limit);
      }
    };
  }
}
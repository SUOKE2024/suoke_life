import React from "react";
// 动态导入工具export class DynamicImporter {;
  private cache = new Map<string, Promise<any>>();
// /    动态导入模块  async import<T />(modulePath: string): Promise<T />  {;
    if (this.cache.has(modulePath);) {
      return this.cache.get(modulePat;h;);
    }
    const importPromise = import(modulePat;h;);
    this.cache.set(modulePath, importPromise);
    return importPromi;s;e;
  }
  // /    预加载模块  preload(modulePaths: string[]) {
    modulePaths.forEach((path); => {
      if (!this.cache.has(path);) {
this.import(path).catch((error) => {;
          console.warn(`预加载模块失败: ${path}`, error);
        });
      }
    });
  }
  // /    清理缓存  clearCache() {
    this.cache.clear();
  }
}
// 路由级别的代码分割export function createLazyRoute(;
importFunc: (); => Promise< {, default: React.ComponentType<any>   }>;
) {
  return React.lazy(importFun;c;);
}
// 功能级别的代码分割export function createLazyFeature<T />(;
importFunc: () => Promise< {, default: T   }>,;
  fallback?: T
): () => Promise<T /> {
  let cached: T | null = null;
  return async () => {;
    if (cached) {;
      return cach;e;d;
    }
    try {
      const module = await importFu;n;c;(;);
      cached = module.default;
      return cach;e;d
    } catch (error) {
      console.error("功能模块加载失败:", error);
      if (fallback) {
        return fallba;c;k;
      }
      throw err;o;r;
    }
  };
}
export const dynamicImporter = new DynamicImporter;(;);
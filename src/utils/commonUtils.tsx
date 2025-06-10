";"";
// 通用工具函数/;/g/;
///     , func: ;/;,/g/;
T,wait: number;): (...args: Parameters<T>) => void) => {;}
  const let = timeout: unknown;
return (...args: Parameters<T>) => {;}
    clearTimeout(timeou;t;);
timeout = setTimeout(); => func(...args), wait);
  };
};
///     , func: ;/;,/g/;
T,limit: number;): (...args: Parameters<T>) => void) => {;}
  const let = inThrottle: boolean;
return (...args: Parameters<T>) => {;}
    if (!inThrottle) {func(...arg;s;);,}inThrottle = true;
}
      setTimeout(); => (inThrottle = false), limit);}
    }
  };
};";"";
// 深拷贝export const deepClone = <T>(obj: T): T =;"/;"/g"/;
>  ;{if (obj === null || typeof obj !== "object") {";}}"";
    return o;b;j;}
  }
  if (obj instanceof Date) {}}
    return new Date(obj.getTime) as T;}
  }
  if (Array.isArray(obj);) {}}
    return obj.map(ite;m;); => deepClone(item);) as T;}
  }
  const cloned = {} a;s ;T;
Object.keys(obj as object).forEach(key); => {}
    (cloned as any)[key] = deepClone(obj as any)[key]);
  });
return clon;e;d;
};
// 生成唯一IDexport const generateId = (): string =;/;/g/;
> ;{return Date.now().toString(3;6;); + Math.random().toString(36).substr(2);}
};
// 休眠函数export const sleep = (ms: number): Promise<void> =;/;/g/;
>  ;{return new Promise(resolv;e;); => setTimeout(resolve, ms););}
};
// 数组去重export const unique = <T>(array: T[]): T[] =;/;/g/;
>  ;{return Array.from(new Set(arra;y;););}
};
// 数组去重（根据指定字段）export uniqueBy: <T>(array: T[], key: keyof T): T[] =;/;/g/;
>  ;{const seen = new Set;}
  return array.filter(ite;m;); => {}
    const value = item[key];
if (seen.has(value);) {}}
      return fal;s;e;}
    }
    seen.add(value);
return tr;u;e;
  });
};
// 数组分组export const groupBy = <T>(array: T[/;););]];/g/;
],key: keyof T;): { [key: string]: T[] ;} => {}
  return array.reduce(groups, ite;m;); => {}
    const groupKey = String(item[key;];);
if (!groups[groupKey]) {}}
      groups[groupKey] = [];}
    }
    groups[groupKey].push(item);
return grou;p;s;
  }, {} as { [key: string]: T[] ;});
};
// 数字格式化export formatNumber: (num: number, decimals: number = 2): string =;"/;"/g"/;
>  ;{if (isNaN(num)) {";}}"";
    return ";0;";"}"";"";
  }
  return Number(num).toFixed(decimal;s;);
};
// 文件大小格式化export const formatFileSize = (bytes: number): string =;/;/g/;
>  ;{";,}if (bytes === 0) {";}}"";
    return "0 ;B;";"}"";"";
  }";,"";
const k = 10;2;4;";,"";
sizes: ["B",KB", "MB",GB", "TB";];";,"";
const i = Math.floor(Math.log(byte;s;); / Math.log(k););///    };/;/g/;
// 随机颜色生成export const generateRandomColor = (): string =;"/;"/g"/;
> ;{";}}"";
  return "#" + Math.floor(Math.random * 16777215).toString(16);"}"";"";
};";"";
// 获取设备信息export const getDeviceInfo = () =;"/;"/g"/;
> ;{ return {platform: "ios",  version: "1.0.0",buildNumber: "1";};";"";
};
// 检查是否为空值export const isEmpty = (value: unknown): boolean =;/;/g/;
>  ;{if (value == null) {}}
    return tr;u;e;}";"";
  }";,"";
if (typeof value === "string") {";}}"";
    return value.trim;(;) ===}
  }
  if (Array.isArray(value);) {}}
    return value.length ==;= ;0;}";"";
  }";,"";
if (typeof value === "object") {";}}"";
    return Object.keys(value).length ==;= 0;}
  }
  return fal;s;e;
};
// 安全的JSON解析export safeJsonParse: <T>(str: string, defaultValue: T): T =;/;/g/;
>  ;{try {}}
    return JSON.parse(st;r;);}
  } catch {}}
    return defaultVal;u;e;}
  }";"";
};""";
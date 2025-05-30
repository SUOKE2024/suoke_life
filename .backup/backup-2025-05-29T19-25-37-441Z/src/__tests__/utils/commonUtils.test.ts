/**
 * 通用工具函数测试
 * 测试常用的工具函数
 */

describe('通用工具函数测试', () => {
  describe('数组操作', () => {
    it('应该能够去重数组', () => {
      const removeDuplicates = (arr: any[]) => {
        return [...new Set(arr)];
      };

      const arrayWithDuplicates = [1, 2, 2, 3, 3, 4, 5];
      const uniqueArray = removeDuplicates(arrayWithDuplicates);
      
      expect(uniqueArray).toEqual([1, 2, 3, 4, 5]);
      expect(uniqueArray.length).toBe(5);
    });

    it('应该能够分块数组', () => {
      const chunkArray = (arr: any[], size: number) => {
        const chunks = [];
        for (let i = 0; i < arr.length; i += size) {
          chunks.push(arr.slice(i, i + size));
        }
        return chunks;
      };

      const array = [1, 2, 3, 4, 5, 6, 7, 8, 9];
      const chunks = chunkArray(array, 3);
      
      expect(chunks).toEqual([[1, 2, 3], [4, 5, 6], [7, 8, 9]]);
      expect(chunks.length).toBe(3);
    });

    it('应该能够打乱数组', () => {
      const shuffleArray = (arr: any[]) => {
        const shuffled = [...arr];
        for (let i = shuffled.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
      };

      const originalArray = [1, 2, 3, 4, 5];
      const shuffledArray = shuffleArray(originalArray);
      
      expect(shuffledArray).toHaveLength(originalArray.length);
      expect(shuffledArray.sort()).toEqual(originalArray.sort());
    });

    it('应该能够查找数组中的最大值和最小值', () => {
      const findMinMax = (arr: number[]) => {
        return {
          min: Math.min(...arr),
          max: Math.max(...arr),
        };
      };

      const numbers = [3, 1, 4, 1, 5, 9, 2, 6];
      const result = findMinMax(numbers);
      
      expect(result.min).toBe(1);
      expect(result.max).toBe(9);
    });
  });

  describe('对象操作', () => {
    it('应该能够深拷贝对象', () => {
      const deepClone = (obj: any) => {
        return JSON.parse(JSON.stringify(obj));
      };

      const originalObject = {
        name: '测试',
        nested: {
          value: 123,
          array: [1, 2, 3],
        },
      };

      const clonedObject = deepClone(originalObject);
      clonedObject.nested.value = 456;
      
      expect(originalObject.nested.value).toBe(123);
      expect(clonedObject.nested.value).toBe(456);
    });

    it('应该能够合并对象', () => {
      const mergeObjects = (...objects: any[]) => {
        return Object.assign({}, ...objects);
      };

      const obj1 = { a: 1, b: 2 };
      const obj2 = { b: 3, c: 4 };
      const obj3 = { c: 5, d: 6 };

      const merged = mergeObjects(obj1, obj2, obj3);
      
      expect(merged).toEqual({ a: 1, b: 3, c: 5, d: 6 });
    });

    it('应该能够获取对象的键值对', () => {
      const getObjectEntries = (obj: any) => {
        return Object.entries(obj);
      };

      const testObject = { name: '张三', age: 30, city: '北京' };
      const entries = getObjectEntries(testObject);
      
      expect(entries).toEqual([
        ['name', '张三'],
        ['age', 30],
        ['city', '北京'],
      ]);
    });

    it('应该能够检查对象是否为空', () => {
      const isEmpty = (obj: any) => {
        return Object.keys(obj).length === 0;
      };

      expect(isEmpty({})).toBe(true);
      expect(isEmpty({ a: 1 })).toBe(false);
      expect(isEmpty([])).toBe(true);
    });
  });

  describe('字符串操作', () => {
    it('应该能够首字母大写', () => {
      const capitalize = (str: string) => {
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
      };

      expect(capitalize('hello')).toBe('Hello');
      expect(capitalize('WORLD')).toBe('World');
      expect(capitalize('tEST')).toBe('Test');
    });

    it('应该能够转换为驼峰命名', () => {
      const toCamelCase = (str: string) => {
        return str
          .replace(/[-_\s]+(.)?/g, (_, char) => char ? char.toUpperCase() : '')
          .replace(/^[A-Z]/, char => char.toLowerCase());
      };

      expect(toCamelCase('hello-world')).toBe('helloWorld');
      expect(toCamelCase('test_case')).toBe('testCase');
      expect(toCamelCase('some string')).toBe('someString');
    });

    it('应该能够截断字符串', () => {
      const truncate = (str: string, length: number, suffix = '...') => {
        if (str.length <= length) {return str;}
        return str.slice(0, length) + suffix;
      };

      expect(truncate('这是一个很长的字符串', 5)).toBe('这是一个很...');
      expect(truncate('短字符串', 10)).toBe('短字符串');
      expect(truncate('测试', 5, '***')).toBe('测试');
    });

    it('应该能够移除字符串中的HTML标签', () => {
      const stripHtml = (str: string) => {
        return str.replace(/<[^>]*>/g, '');
      };

      const htmlString = '<p>这是一个<strong>测试</strong>字符串</p>';
      const plainText = stripHtml(htmlString);
      
      expect(plainText).toBe('这是一个测试字符串');
    });
  });

  describe('数字操作', () => {
    it('应该能够格式化数字', () => {
      const formatNumber = (num: number, decimals = 2) => {
        return num.toFixed(decimals);
      };

      expect(formatNumber(123.456)).toBe('123.46');
      expect(formatNumber(123.456, 1)).toBe('123.5');
      expect(formatNumber(123, 0)).toBe('123');
    });

    it('应该能够生成随机数', () => {
      const randomBetween = (min: number, max: number) => {
        return Math.floor(Math.random() * (max - min + 1)) + min;
      };

      const random = randomBetween(1, 10);
      expect(random).toBeGreaterThanOrEqual(1);
      expect(random).toBeLessThanOrEqual(10);
    });

    it('应该能够计算百分比', () => {
      const calculatePercentage = (value: number, total: number) => {
        return Math.round((value / total) * 100);
      };

      expect(calculatePercentage(25, 100)).toBe(25);
      expect(calculatePercentage(1, 3)).toBe(33);
      expect(calculatePercentage(2, 3)).toBe(67);
    });

    it('应该能够限制数字范围', () => {
      const clamp = (value: number, min: number, max: number) => {
        return Math.min(Math.max(value, min), max);
      };

      expect(clamp(5, 1, 10)).toBe(5);
      expect(clamp(-5, 1, 10)).toBe(1);
      expect(clamp(15, 1, 10)).toBe(10);
    });
  });

  describe('类型检查', () => {
    it('应该能够检查数据类型', () => {
      const getType = (value: any) => {
        return Object.prototype.toString.call(value).slice(8, -1).toLowerCase();
      };

      expect(getType(123)).toBe('number');
      expect(getType('hello')).toBe('string');
      expect(getType([])).toBe('array');
      expect(getType({})).toBe('object');
      expect(getType(null)).toBe('null');
      expect(getType(undefined)).toBe('undefined');
      expect(getType(true)).toBe('boolean');
    });

    it('应该能够检查是否为函数', () => {
      const isFunction = (value: any) => {
        return typeof value === 'function';
      };

      expect(isFunction(() => {})).toBe(true);
      expect(isFunction(function() {})).toBe(true);
      expect(isFunction('not a function')).toBe(false);
      expect(isFunction(123)).toBe(false);
    });

    it('应该能够检查是否为数组', () => {
      const isArray = (value: any) => {
        return Array.isArray(value);
      };

      expect(isArray([])).toBe(true);
      expect(isArray([1, 2, 3])).toBe(true);
      expect(isArray('not an array')).toBe(false);
      expect(isArray({})).toBe(false);
    });
  });

  describe('防抖和节流', () => {
    it('应该能够实现防抖功能', (done) => {
      const debounce = (func: Function, delay: number) => {
        let timeoutId: any;
        return (...args: any[]) => {
          clearTimeout(timeoutId);
          timeoutId = setTimeout(() => func.apply(null, args), delay);
        };
      };

      let callCount = 0;
      const debouncedFunction = debounce(() => {
        callCount++;
      }, 100);

      // 快速调用多次
      debouncedFunction();
      debouncedFunction();
      debouncedFunction();

      // 应该只执行一次
      setTimeout(() => {
        expect(callCount).toBe(1);
        done();
      }, 150);
    });

    it('应该能够实现节流功能', (done) => {
      const throttle = (func: Function, delay: number) => {
        let lastCall = 0;
        return (...args: any[]) => {
          const now = Date.now();
          if (now - lastCall >= delay) {
            lastCall = now;
            func.apply(null, args);
          }
        };
      };

      let callCount = 0;
      const throttledFunction = throttle(() => {
        callCount++;
      }, 100);

      // 快速调用多次
      throttledFunction(); // 第1次调用
      setTimeout(() => throttledFunction(), 50); // 被节流
      setTimeout(() => throttledFunction(), 120); // 第2次调用

      setTimeout(() => {
        expect(callCount).toBe(2);
        done();
      }, 200);
    });
  });

  describe('URL操作', () => {
    it('应该能够解析URL参数', () => {
      const parseUrlParams = (url: string) => {
        const params: Record<string, string> = {};
        const urlObj = new URL(url);
        urlObj.searchParams.forEach((value, key) => {
          params[key] = value;
        });
        return params;
      };

      const url = 'https://example.com/page?name=张三&age=30&city=北京';
      const params = parseUrlParams(url);
      
      expect(params).toEqual({
        name: '张三',
        age: '30',
        city: '北京',
      });
    });

    it('应该能够构建URL参数', () => {
      const buildUrlParams = (params: Record<string, any>) => {
        const searchParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
          searchParams.append(key, String(value));
        });
        return searchParams.toString();
      };

      const params = { name: '张三', age: 30, active: true };
      const queryString = buildUrlParams(params);
      
      expect(queryString).toBe('name=%E5%BC%A0%E4%B8%89&age=30&active=true');
    });
  });

  describe('存储操作', () => {
    it('应该能够安全地解析JSON', () => {
      const safeJsonParse = (jsonString: string, defaultValue: any = null) => {
        try {
          return JSON.parse(jsonString);
        } catch {
          return defaultValue;
        }
      };

      const validJson = '{"name": "张三", "age": 30}';
      const invalidJson = '{invalid json}';

      expect(safeJsonParse(validJson)).toEqual({ name: '张三', age: 30 });
      expect(safeJsonParse(invalidJson)).toBe(null);
      expect(safeJsonParse(invalidJson, {})).toEqual({});
    });

    it('应该能够安全地字符串化对象', () => {
      const safeJsonStringify = (obj: any, defaultValue = '{}') => {
        try {
          return JSON.stringify(obj);
        } catch {
          return defaultValue;
        }
      };

      const validObject = { name: '张三', age: 30 };
      const circularObject: any = {};
      circularObject.self = circularObject;

      expect(safeJsonStringify(validObject)).toBe('{"name":"张三","age":30}');
      expect(safeJsonStringify(circularObject)).toBe('{}');
    });
  });
}); 
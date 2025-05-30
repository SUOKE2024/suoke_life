/**
 * 数据处理工具函数测试
 * 测试各种数据处理和转换功能
 */

describe('数据处理工具函数测试', () => {
  describe('数组处理', () => {
    it('应该能够去重数组', () => {
      const removeDuplicates = <T>(array: T[]): T[] => {
        return [...new Set(array)];
      };

      expect(removeDuplicates([1, 2, 2, 3, 3, 4])).toEqual([1, 2, 3, 4]);
      expect(removeDuplicates(['a', 'b', 'b', 'c'])).toEqual(['a', 'b', 'c']);
      expect(removeDuplicates([])).toEqual([]);
    });

    it('应该能够分组数组', () => {
      const groupBy = <T, K extends keyof any>(
        array: T[],
        key: (item: T) => K
      ): Record<K, T[]> => {
        return array.reduce((groups, item) => {
          const groupKey = key(item);
          if (!groups[groupKey]) {
            groups[groupKey] = [];
          }
          groups[groupKey].push(item);
          return groups;
        }, {} as Record<K, T[]>);
      };

      const data = [
        { name: 'Alice', age: 25, department: 'IT' },
        { name: 'Bob', age: 30, department: 'HR' },
        { name: 'Charlie', age: 25, department: 'IT' },
      ];

      const groupedByAge = groupBy(data, item => item.age);
      expect(groupedByAge[25]).toHaveLength(2);
      expect(groupedByAge[30]).toHaveLength(1);

      const groupedByDept = groupBy(data, item => item.department);
      expect(groupedByDept.IT).toHaveLength(2);
      expect(groupedByDept.HR).toHaveLength(1);
    });

    it('应该能够分页数组', () => {
      const paginate = <T>(array: T[], page: number, pageSize: number) => {
        const startIndex = (page - 1) * pageSize;
        const endIndex = startIndex + pageSize;
        return {
          data: array.slice(startIndex, endIndex),
          totalPages: Math.ceil(array.length / pageSize),
          currentPage: page,
          totalItems: array.length,
        };
      };

      const data = Array.from({ length: 25 }, (_, i) => i + 1);
      const page1 = paginate(data, 1, 10);
      const page3 = paginate(data, 3, 10);

      expect(page1.data).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
      expect(page1.totalPages).toBe(3);
      expect(page3.data).toEqual([21, 22, 23, 24, 25]);
    });

    it('应该能够排序数组', () => {
      const sortBy = <T>(
        array: T[],
        key: keyof T,
        direction: 'asc' | 'desc' = 'asc'
      ): T[] => {
        return [...array].sort((a, b) => {
          const aVal = a[key];
          const bVal = b[key];
          
          if (aVal < bVal) {return direction === 'asc' ? -1 : 1;}
          if (aVal > bVal) {return direction === 'asc' ? 1 : -1;}
          return 0;
        });
      };

      const data = [
        { name: 'Charlie', age: 25 },
        { name: 'Alice', age: 30 },
        { name: 'Bob', age: 20 },
      ];

      const sortedByAge = sortBy(data, 'age');
      expect(sortedByAge[0].age).toBe(20);
      expect(sortedByAge[2].age).toBe(30);

      const sortedByName = sortBy(data, 'name');
      expect(sortedByName[0].name).toBe('Alice');
      expect(sortedByName[2].name).toBe('Charlie');
    });
  });

  describe('对象处理', () => {
    it('应该能够深度合并对象', () => {
      const deepMerge = (target: any, source: any): any => {
        const result = { ...target };
        
        for (const key in source) {
          if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
            result[key] = deepMerge(result[key] || {}, source[key]);
          } else {
            result[key] = source[key];
          }
        }
        
        return result;
      };

      const obj1 = {
        a: 1,
        b: { c: 2, d: 3 },
        e: [1, 2],
      };

      const obj2 = {
        b: { d: 4, f: 5 },
        e: [3, 4],
        g: 6,
      };

      const merged = deepMerge(obj1, obj2);
      expect(merged.a).toBe(1);
      expect(merged.b.c).toBe(2);
      expect(merged.b.d).toBe(4);
      expect(merged.b.f).toBe(5);
      expect(merged.g).toBe(6);
    });

    it('应该能够获取嵌套属性', () => {
      const getNestedProperty = (obj: any, path: string, defaultValue?: any) => {
        const keys = path.split('.');
        let result = obj;
        
        for (const key of keys) {
          if (result && typeof result === 'object' && key in result) {
            result = result[key];
          } else {
            return defaultValue;
          }
        }
        
        return result;
      };

      const data = {
        user: {
          profile: {
            name: 'Alice',
            settings: {
              theme: 'dark',
            },
          },
        },
      };

      expect(getNestedProperty(data, 'user.profile.name')).toBe('Alice');
      expect(getNestedProperty(data, 'user.profile.settings.theme')).toBe('dark');
      expect(getNestedProperty(data, 'user.profile.age', 25)).toBe(25);
      expect(getNestedProperty(data, 'invalid.path')).toBeUndefined();
    });

    it('应该能够扁平化对象', () => {
      const flattenObject = (obj: any, prefix = ''): Record<string, any> => {
        const result: Record<string, any> = {};
        
        for (const key in obj) {
          const newKey = prefix ? `${prefix}.${key}` : key;
          
          if (obj[key] && typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
            Object.assign(result, flattenObject(obj[key], newKey));
          } else {
            result[newKey] = obj[key];
          }
        }
        
        return result;
      };

      const nested = {
        a: 1,
        b: {
          c: 2,
          d: {
            e: 3,
          },
        },
        f: [1, 2, 3],
      };

      const flattened = flattenObject(nested);
      expect(flattened.a).toBe(1);
      expect(flattened['b.c']).toBe(2);
      expect(flattened['b.d.e']).toBe(3);
      expect(flattened.f).toEqual([1, 2, 3]);
    });
  });

  describe('数据转换', () => {
    it('应该能够转换CSV数据', () => {
      const parseCSV = (csvText: string): string[][] => {
        return csvText
          .trim()
          .split('\n')
          .map(row => row.split(',').map(cell => cell.trim()));
      };

      const csvData = `name,age,city
Alice,25,Beijing
Bob,30,Shanghai`;

      const parsed = parseCSV(csvData);
      expect(parsed).toEqual([
        ['name', 'age', 'city'],
        ['Alice', '25', 'Beijing'],
        ['Bob', '30', 'Shanghai'],
      ]);
    });

    it('应该能够转换为JSON', () => {
      const arrayToJSON = (headers: string[], rows: string[][]) => {
        return rows.map(row => {
          const obj: Record<string, string> = {};
          headers.forEach((header, index) => {
            obj[header] = row[index] || '';
          });
          return obj;
        });
      };

      const headers = ['name', 'age', 'city'];
      const rows = [
        ['Alice', '25', 'Beijing'],
        ['Bob', '30', 'Shanghai'],
      ];

      const json = arrayToJSON(headers, rows);
      expect(json).toEqual([
        { name: 'Alice', age: '25', city: 'Beijing' },
        { name: 'Bob', age: '30', city: 'Shanghai' },
      ]);
    });
  });

  describe('数据验证', () => {
    it('应该能够验证数据结构', () => {
      const validateSchema = (data: any, schema: Record<string, string>) => {
        const errors: string[] = [];
        
        for (const [key, type] of Object.entries(schema)) {
          if (!(key in data)) {
            errors.push(`Missing required field: ${key}`);
          } else if (typeof data[key] !== type) {
            errors.push(`Field ${key} should be ${type}, got ${typeof data[key]}`);
          }
        }
        
        return {
          isValid: errors.length === 0,
          errors,
        };
      };

      const schema = {
        name: 'string',
        age: 'number',
        active: 'boolean',
      };

      const validData = { name: 'Alice', age: 25, active: true };
      const invalidData = { name: 'Bob', age: '30', active: 'yes' };

      const validResult = validateSchema(validData, schema);
      const invalidResult = validateSchema(invalidData, schema);

      expect(validResult.isValid).toBe(true);
      expect(invalidResult.isValid).toBe(false);
      expect(invalidResult.errors).toHaveLength(2);
    });

    it('应该能够清理数据', () => {
      const sanitizeData = (data: Record<string, any>) => {
        const sanitized: Record<string, any> = {};
        
        for (const [key, value] of Object.entries(data)) {
          if (value !== null && value !== undefined && value !== '') {
            if (typeof value === 'string') {
              sanitized[key] = value.trim();
            } else {
              sanitized[key] = value;
            }
          }
        }
        
        return sanitized;
      };

      const dirtyData = {
        name: '  Alice  ',
        age: 25,
        email: '',
        phone: null,
        city: 'Beijing',
        country: undefined,
      };

      const cleaned = sanitizeData(dirtyData);
      expect(cleaned).toEqual({
        name: 'Alice',
        age: 25,
        city: 'Beijing',
      });
    });
  });

  describe('统计分析', () => {
    it('应该能够计算基本统计', () => {
      const calculateStats = (numbers: number[]) => {
        if (numbers.length === 0) {return null;}
        
        const sorted = [...numbers].sort((a, b) => a - b);
        const sum = numbers.reduce((acc, num) => acc + num, 0);
        const mean = sum / numbers.length;
        
        const median = sorted.length % 2 === 0
          ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
          : sorted[Math.floor(sorted.length / 2)];
        
        const variance = numbers.reduce((acc, num) => acc + Math.pow(num - mean, 2), 0) / numbers.length;
        const stdDev = Math.sqrt(variance);
        
        return {
          count: numbers.length,
          sum,
          mean,
          median,
          min: sorted[0],
          max: sorted[sorted.length - 1],
          variance,
          stdDev,
        };
      };

      const data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
      const stats = calculateStats(data);

      expect(stats?.count).toBe(10);
      expect(stats?.sum).toBe(55);
      expect(stats?.mean).toBe(5.5);
      expect(stats?.median).toBe(5.5);
      expect(stats?.min).toBe(1);
      expect(stats?.max).toBe(10);
    });

    it('应该能够计算频率分布', () => {
      const calculateFrequency = <T>(array: T[]) => {
        const frequency: Record<string, number> = {};
        
        array.forEach(item => {
          const key = String(item);
          frequency[key] = (frequency[key] || 0) + 1;
        });
        
        return frequency;
      };

      const data = ['apple', 'banana', 'apple', 'orange', 'banana', 'apple'];
      const frequency = calculateFrequency(data);

      expect(frequency.apple).toBe(3);
      expect(frequency.banana).toBe(2);
      expect(frequency.orange).toBe(1);
    });
  });

  describe('缓存处理', () => {
    it('应该能够实现简单缓存', () => {
      const createCache = <K, V>(maxSize = 100) => {
        const cache = new Map<K, V>();
        
        return {
          get: (key: K): V | undefined => cache.get(key),
          set: (key: K, value: V): void => {
            if (cache.size >= maxSize) {
              const firstKey = cache.keys().next().value;
              if (firstKey !== undefined) {
                cache.delete(firstKey);
              }
            }
            cache.set(key, value);
          },
          has: (key: K): boolean => cache.has(key),
          clear: (): void => cache.clear(),
          size: (): number => cache.size,
        };
      };

      const cache = createCache<string, number>(3);
      
      cache.set('a', 1);
      cache.set('b', 2);
      cache.set('c', 3);
      
      expect(cache.get('a')).toBe(1);
      expect(cache.size()).toBe(3);
      
      cache.set('d', 4); // 应该移除最旧的项
      expect(cache.has('a')).toBe(false);
      expect(cache.has('d')).toBe(true);
    });
  });
}); 
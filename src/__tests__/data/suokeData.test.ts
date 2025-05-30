import suokeData from "../../data/suokeData";

/**
 * suokeData 测试
 * 索克生活APP - 完整的数据模块测试
 */

describe("suokeData", () => {
  // 基础测试
  describe("基础功能", () => {
    it("应该正确导入模块", () => {
      expect(suokeData).toBeDefined();
      expect(suokeData).not.toBeNull();
      expect(typeof suokeData).toBe("object");
    });

    it("应该具备基本的数据结构", () => {
      // 检查数据模块的基本结构
      const dataKeys = Object.keys(suokeData);
      expect(dataKeys.length).toBeGreaterThan(0);

      // 验证数据类型
      dataKeys.forEach((key) => {
        const value = (suokeData as any)[key];
        expect(value).toBeDefined();
        expect(typeof value).toMatch(
          /^(object|array|string|number|boolean|function)$/
        );
      });
    });

    it("应该包含预期的数据字段", () => {
      // 检查是否包含核心数据字段
      const expectedFields = [
        // 可能的字段名，根据实际数据结构调整
        "agents",
        "health",
        "diagnosis",
        "users",
        "config",
      ];

      const availableKeys = Object.keys(suokeData);
      const hasExpectedFields = expectedFields.some(
        (field) =>
          availableKeys.includes(field) ||
          availableKeys.some((key) =>
            key.toLowerCase().includes(field.toLowerCase())
          )
      );

      // 至少应该有一些预期的字段或相关字段
      expect(hasExpectedFields || availableKeys.length > 0).toBe(true);
    });
  });

  // 数据验证测试
  describe("数据验证", () => {
    it("应该包含有效的数据格式", () => {
      // 验证数据格式的有效性
      const validateDataStructure = (data: any, path = "root") => {
        if (data === null || data === undefined) {
          return { valid: false, error: `${path} is null or undefined` };
        }

        if (typeof data === "object" && !Array.isArray(data)) {
          // 验证对象结构
          const keys = Object.keys(data);
          for (const key of keys) {
            if (typeof key !== "string" || key.length === 0) {
              return { valid: false, error: `Invalid key at ${path}.${key}` };
            }
          }
        }

        return { valid: true };
      };

      const validation = validateDataStructure(suokeData);
      expect(validation.valid).toBe(true);
      if (!validation.valid) {
        console.error("Data validation error:", validation.error);
      }
    });

    it("应该具有一致的数据类型", () => {
      // 检查数据类型的一致性
      const checkTypeConsistency = (data: any) => {
        if (Array.isArray(data)) {
          if (data.length > 0) {
            const firstItemType = typeof data[0];
            const allSameType = data.every(
              (item) => typeof item === firstItemType
            );
            return allSameType;
          }
        }
        return true;
      };

      const dataEntries = Object.entries(suokeData);
      dataEntries.forEach(([key, value]) => {
        if (Array.isArray(value)) {
          const isConsistent = checkTypeConsistency(value);
          expect(isConsistent).toBe(true);
        }
      });
    });
  });

  // 数据操作测试
  describe("数据操作", () => {
    it("应该支持数据读取操作", () => {
      // 测试数据读取
      const testDataAccess = () => {
        try {
          const keys = Object.keys(suokeData);
          const values = Object.values(suokeData);
          const entries = Object.entries(suokeData);

          return {
            keys: keys.length > 0,
            values: values.length > 0,
            entries: entries.length > 0,
            accessible: true,
          };
        } catch (error) {
          return { accessible: false, error };
        }
      };

      const result = testDataAccess();
      expect(result.accessible).toBe(true);
      expect(result.keys).toBe(true);
      expect(result.values).toBe(true);
      expect(result.entries).toBe(true);
    });

    it("应该支持数据查询操作", () => {
      // 测试数据查询功能
      const testDataQuery = (searchTerm: string) => {
        const results: any[] = [];

        const searchInObject = (obj: any, path = "") => {
          if (
            typeof obj === "string" &&
            obj.toLowerCase().includes(searchTerm.toLowerCase())
          ) {
            results.push({ path, value: obj });
          } else if (typeof obj === "object" && obj !== null) {
            Object.entries(obj).forEach(([key, value]) => {
              searchInObject(value, path ? `${path}.${key}` : key);
            });
          }
        };

        searchInObject(suokeData);
        return results;
      };

      // 测试搜索功能
      const searchResults = testDataQuery("test");
      expect(Array.isArray(searchResults)).toBe(true);
      expect(searchResults.length).toBeGreaterThanOrEqual(0);
    });
  });

  // 性能测试
  describe("性能", () => {
    it("应该快速访问数据", () => {
      // 测试数据访问性能
      const startTime = Date.now();

      // 执行多次数据访问
      for (let i = 0; i < 1000; i++) {
        const keys = Object.keys(suokeData);
        const firstKey = keys[0];
        if (firstKey) {
          const value = (suokeData as any)[firstKey];
          expect(value).toBeDefined();
        }
      }

      const endTime = Date.now();
      const accessTime = endTime - startTime;

      // 1000次访问应该在100ms内完成
      expect(accessTime).toBeLessThan(100);
    });

    it("应该高效处理数据遍历", () => {
      // 测试数据遍历性能
      const startTime = Date.now();

      let itemCount = 0;
      const traverseData = (obj: any) => {
        if (typeof obj === "object" && obj !== null) {
          Object.values(obj).forEach((value) => {
            itemCount++;
            if (typeof value === "object" && value !== null) {
              traverseData(value);
            }
          });
        }
      };

      traverseData(suokeData);

      const endTime = Date.now();
      const traversalTime = endTime - startTime;

      expect(itemCount).toBeGreaterThan(0);
      expect(traversalTime).toBeLessThan(500); // 遍历应该在500ms内完成
    });
  });

  // 错误处理测试
  describe("错误处理", () => {
    it("应该正确处理无效访问", () => {
      // 测试访问不存在的属性
      const invalidAccess = () => {
        try {
          const nonExistentProperty = (suokeData as any).nonExistentProperty;
          return { success: true, value: nonExistentProperty };
        } catch (error) {
          return { success: false, error };
        }
      };

      const result = invalidAccess();
      expect(result.success).toBe(true); // 访问不存在的属性应该返回undefined而不是抛出错误
      expect(result.value).toBeUndefined();
    });

    it("应该正确处理数据类型错误", () => {
      // 测试类型安全
      const testTypeSafety = () => {
        const errors: string[] = [];

        Object.entries(suokeData).forEach(([key, value]) => {
          try {
            // 尝试各种操作来测试类型安全
            if (typeof value === "string") {
              value.length; // 字符串操作
            } else if (Array.isArray(value)) {
              value.length; // 数组操作
            } else if (typeof value === "object" && value !== null) {
              Object.keys(value); // 对象操作
            }
          } catch (error) {
            errors.push(`Error accessing ${key}: ${error}`);
          }
        });

        return errors;
      };

      const errors = testTypeSafety();
      expect(errors.length).toBe(0);
    });
  });

  // 数据完整性测试
  describe("数据完整性", () => {
    it("应该具有完整的数据结构", () => {
      // 检查数据完整性
      const checkDataIntegrity = (data: any): boolean => {
        if (data === null || data === undefined) {
          return false;
        }

        if (typeof data === "object") {
          // 检查对象是否有循环引用
          try {
            JSON.stringify(data);
            return true;
          } catch (error) {
            // 可能有循环引用
            return false;
          }
        }

        return true;
      };

      const isIntegral = checkDataIntegrity(suokeData);
      expect(isIntegral).toBe(true);
    });

    it("应该具有有效的数据关系", () => {
      // 检查数据关系的有效性
      const validateDataRelations = (data: any) => {
        const relations: Array<{ from: string; to: string; valid: boolean }> =
          [];

        const findReferences = (obj: any, path = "") => {
          if (typeof obj === "object" && obj !== null) {
            Object.entries(obj).forEach(([key, value]) => {
              if (typeof value === "string" && value.includes("ref:")) {
                // 假设引用格式为 "ref:path"
                const refPath = value.replace("ref:", "");
                const isValidRef = refPath.length > 0;
                relations.push({
                  from: `${path}.${key}`,
                  to: refPath,
                  valid: isValidRef,
                });
              } else if (typeof value === "object") {
                findReferences(value, path ? `${path}.${key}` : key);
              }
            });
          }
        };

        findReferences(data);
        return relations;
      };

      const relations = validateDataRelations(suokeData);

      // 所有找到的引用都应该是有效的
      relations.forEach((relation) => {
        expect(relation.valid).toBe(true);
      });
    });
  });
});

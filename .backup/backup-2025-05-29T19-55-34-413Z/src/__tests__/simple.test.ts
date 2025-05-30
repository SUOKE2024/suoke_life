/**
 * 简单测试 - 验证测试体系是否正常工作
 */

describe("测试体系验证", () => {
  it("应该能够运行基本的JavaScript测试", () => {
    expect(1 + 1).toBe(2);
  });

  it("应该能够测试字符串操作", () => {
    const str = "Hello World";
    expect(str.toLowerCase()).toBe("hello world");
    expect(str.includes("World")).toBe(true);
  });

  it("应该能够测试数组操作", () => {
    const arr = [1, 2, 3, 4, 5];
    expect(arr.length).toBe(5);
    expect(arr.includes(3)).toBe(true);
    expect(arr.filter((x) => x > 3)).toEqual([4, 5]);
  });

  it("应该能够测试对象操作", () => {
    const obj = { name: "索克生活", version: "1.0.0" };
    expect(obj.name).toBe("索克生活");
    expect(obj).toHaveProperty("version");
    expect(Object.keys(obj)).toEqual(["name", "version"]);
  });

  it("应该能够测试异步操作", async () => {
    const promise = Promise.resolve("success");
    const result = await promise;
    expect(result).toBe("success");
  });

  it("应该能够测试错误处理", () => {
    const throwError = () => {
      throw new Error("测试错误");
    };

    expect(throwError).toThrow("测试错误");
  });

  it("应该能够使用Jest的匹配器", () => {
    expect("索克生活").toMatch(/索克/);
    expect(42).toBeGreaterThan(40);
    expect([1, 2, 3]).toContain(2);
    expect({ a: 1, b: 2 }).toEqual({ a: 1, b: 2 });
  });
});

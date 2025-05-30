import { renderHook, act } from "@testing-library/react-native";
import { ThemeProvider, useTheme } from "../../contexts/ThemeContext";
import React from "react";


/**
 * 主题上下文测试
 */

// 创建包装器
const createWrapper = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider>{children}</ThemeProvider>
);

describe("ThemeContext", () => {
  it("应该提供默认的浅色主题", () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper,
    });

    expect(result.current.isDark).toBe(false);
    expect(result.current.theme.colors.primary).toBe("#35bb78");
  });

  it("应该能够切换主题", () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper,
    });

    // 初始状态应该是浅色主题
    expect(result.current.isDark).toBe(false);
    expect(result.current.theme.colors.primary).toBe("#35bb78");

    // 切换到暗黑主题
    act(() => {
      result.current.toggleTheme();
    });

    expect(result.current.isDark).toBe(true);
    expect(result.current.theme.colors.primary).toBe("#66d19e");

    // 再次切换回浅色主题
    act(() => {
      result.current.toggleTheme();
    });

    expect(result.current.isDark).toBe(false);
    expect(result.current.theme.colors.primary).toBe("#35bb78");
  });

  it("应该提供正确的索克品牌色彩", () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper,
    });

    const { theme } = result.current;

    // 验证主色调
    expect(theme.colors.primary).toBe("#35bb78");
    expect(theme.colors.secondary).toBe("#ff6800");

    // 验证中医特色色彩
    expect(theme.colors.tcm.wood).toBe("#35bb78");
    expect(theme.colors.tcm.earth).toBe("#ff6800");
    expect(theme.colors.tcm.fire).toBe("#F44336");
    expect(theme.colors.tcm.metal).toBe("#9E9E9E");
    expect(theme.colors.tcm.water).toBe("#2196F3");

    // 验证状态色
    expect(theme.colors.success).toBe("#35bb78");
    expect(theme.colors.warning).toBe("#ff6800");
  });

  it("应该在暗黑模式下提供正确的色彩", () => {
    const { result } = renderHook(() => useTheme(), {
      wrapper: createWrapper,
    });

    // 切换到暗黑模式
    act(() => {
      result.current.setTheme(true);
    });

    const { theme } = result.current;

    // 验证暗黑模式下的主色调
    expect(theme.colors.primary).toBe("#66d19e");
    expect(theme.colors.secondary).toBe("#ff8533");

    // 验证暗黑模式下的中医特色色彩
    expect(theme.colors.tcm.wood).toBe("#66d19e");
    expect(theme.colors.tcm.earth).toBe("#ff8533");

    // 验证暗黑模式下的状态色
    expect(theme.colors.success).toBe("#66d19e");
    expect(theme.colors.warning).toBe("#ff8533");
  });
});

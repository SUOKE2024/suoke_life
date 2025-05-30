import { Appearance, ColorSchemeName } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import React, {


  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

// 颜色定义
const colors = {
  light: {
    // 主色调 - 索克绿
    primary: "#35bb78", // 索克绿 - 代表生命力和健康
    primaryLight: "#66d19e", // 浅索克绿
    primaryDark: "#2a9960", // 深索克绿

    // 辅助色 - 索克橙
    secondary: "#ff6800", // 索克橙 - 代表活力和温暖
    secondaryLight: "#ff8533",
    secondaryDark: "#cc5200",

    // 中性色
    background: "#FFFFFF",
    surface: "#F8F9FA",
    surfaceVariant: "#F1F3F4",

    // 文本色
    onPrimary: "#FFFFFF",
    onSecondary: "#FFFFFF",
    onBackground: "#1A1A1A",
    onSurface: "#1A1A1A",
    onSurfaceVariant: "#5F6368",

    // 状态色
    success: "#35bb78", // 使用索克绿作为成功色
    warning: "#ff6800", // 使用索克橙作为警告色
    error: "#F44336",
    info: "#2196F3",

    // 边框和分割线
    outline: "#E0E0E0",
    outlineVariant: "#F5F5F5",

    // 阴影
    shadow: "rgba(0, 0, 0, 0.1)",
    elevation: "rgba(0, 0, 0, 0.12)",

    // 中医特色色彩
    tcm: {
      wood: "#35bb78", // 木 - 索克绿
      fire: "#F44336", // 火 - 红色
      earth: "#ff6800", // 土 - 索克橙
      metal: "#9E9E9E", // 金 - 灰色
      water: "#2196F3", // 水 - 蓝色
    },
  },
  dark: {
    // 主色调 - 索克绿（暗黑模式下稍微调亮）
    primary: "#66d19e",
    primaryLight: "#99e6c1",
    primaryDark: "#35bb78",

    // 辅助色 - 索克橙（暗黑模式下稍微调亮）
    secondary: "#ff8533",
    secondaryLight: "#ffab66",
    secondaryDark: "#ff6800",

    // 中性色
    background: "#121212",
    surface: "#1E1E1E",
    surfaceVariant: "#2C2C2C",

    // 文本色
    onPrimary: "#000000",
    onSecondary: "#000000",
    onBackground: "#FFFFFF",
    onSurface: "#FFFFFF",
    onSurfaceVariant: "#B3B3B3",

    // 状态色
    success: "#66d19e", // 暗黑模式下的索克绿
    warning: "#ff8533", // 暗黑模式下的索克橙
    error: "#EF5350",
    info: "#42A5F5",

    // 边框和分割线
    outline: "#3C3C3C",
    outlineVariant: "#2C2C2C",

    // 阴影
    shadow: "rgba(0, 0, 0, 0.3)",
    elevation: "rgba(0, 0, 0, 0.24)",

    // 中医特色色彩
    tcm: {
      wood: "#66d19e", // 木 - 亮索克绿
      fire: "#EF5350", // 火 - 红色
      earth: "#ff8533", // 土 - 亮索克橙
      metal: "#BDBDBD", // 金 - 灰色
      water: "#42A5F5", // 水 - 蓝色
    },
  },
};

// 字体定义
const typography = {
  fontFamily: {
    regular: "System",
    medium: "System",
    bold: "System",
    light: "System",
  },
  fontSize: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    "2xl": 24,
    "3xl": 30,
    "4xl": 36,
    "5xl": 48,
  },
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
  fontWeight: {
    light: "300",
    normal: "400",
    medium: "500",
    semibold: "600",
    bold: "700",
  },
};

// 间距定义
const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  "2xl": 48,
  "3xl": 64,
};

// 圆角定义
const borderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  "2xl": 24,
  full: 9999,
};

// 阴影定义
const shadows = {
  sm: {
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.18,
    shadowRadius: 1.0,
    elevation: 1,
  },
  md: {
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.23,
    shadowRadius: 2.62,
    elevation: 4,
  },
  lg: {
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
    elevation: 8,
  },
  xl: {
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.37,
    shadowRadius: 7.49,
    elevation: 12,
  },
};

// 动画配置
const animations = {
  duration: {
    fast: 150,
    normal: 300,
    slow: 500,
  },
  easing: {
    linear: "linear",
    ease: "ease",
    easeIn: "ease-in",
    easeOut: "ease-out",
    easeInOut: "ease-in-out",
  },
};

// 主题类型定义
export interface Theme {
  colors: typeof colors.light;
  typography: typeof typography;
  spacing: typeof spacing;
  borderRadius: typeof borderRadius;
  shadows: typeof shadows;
  animations: typeof animations;
  isDark: boolean;
}

// 主题上下文类型
interface ThemeContextType {
  theme: Theme;
  isDark: boolean;
  toggleTheme: () => void;
  setTheme: (isDark: boolean) => void;
}

// 创建上下文
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// 主题提供者组件
interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [isDark, setIsDark] = useState<boolean>(false);

  // 初始化主题
  useEffect(() => {
    const initializeTheme = async () => {
      try {
        // 从存储中获取用户偏好
        const savedTheme = await AsyncStorage.getItem("theme");
        if (savedTheme !== null) {
          setIsDark(savedTheme === "dark");
        } else {
          // 如果没有保存的偏好，使用系统主题
          const systemTheme = Appearance.getColorScheme();
          setIsDark(systemTheme === "dark");
        }
      } catch (error) {
        console.warn("Failed to load theme preference:", error);
        // 默认使用浅色主题
        setIsDark(false);
      }
    };

    initializeTheme();

    // 监听系统主题变化
    const subscription = Appearance.addChangeListener(({ colorScheme }) => {
      // 只有在用户没有手动设置主题时才跟随系统
      AsyncStorage.getItem("theme").then((savedTheme) => {
        if (savedTheme === null) {
          setIsDark(colorScheme === "dark");
        }
      });
    });

    return () => subscription?.remove();
  }, []);

  // 切换主题
  const toggleTheme = async () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    try {
      await AsyncStorage.setItem("theme", newTheme ? "dark" : "light");
    } catch (error) {
      console.warn("Failed to save theme preference:", error);
    }
  };

  // 设置主题
  const setTheme = async (dark: boolean) => {
    setIsDark(dark);
    try {
      await AsyncStorage.setItem("theme", dark ? "dark" : "light");
    } catch (error) {
      console.warn("Failed to save theme preference:", error);
    }
  };

  // 构建主题对象
  const theme: Theme = {
    colors: isDark ? colors.dark : colors.light,
    typography,
    spacing,
    borderRadius,
    shadows,
    animations,
    isDark,
  };

  return (
    <ThemeContext.Provider value={{ theme, isDark, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// 主题钩子
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};

// 导出主题相关类型和常量
export { colors, typography, spacing, borderRadius, shadows, animations };
export type { ThemeContextType };

import React, { createContext, ReactNode, useContext, useState } from 'react';

// 颜色定义
const colors = {
  light: {,
  primary: '#66bb6a',
    primaryLight: '#98ee99',
    primaryDark: '#338a3e',
    secondary: '#ff9800',
    secondaryLight: '#ffcc02',
    secondaryDark: '#cc5200',
    surface: '#F8F9FA',
    surfaceVariant: '#F1F3F4',
    background: '#FFFFFF',
    onPrimary: '#FFFFFF',
    onSecondary: '#FFFFFF',
    onBackground: '#1A1A1A',
    onSurface: '#1A1A1A',
    onSurfaceVariant: '#5F6368',
    outline: '#E0E0E0',
    outlineVariant: '#F5F5F5',
    error: '#F44336',
    warning: '#FF9800',
    info: '#2196F3',
    success: '#4CAF50',
    elevation: 'rgba(0, 0, 0, 0.12)',
    shadow: 'rgba(0, 0, 0, 0.12)',
  },
  dark: {,
  primary: '#66bb6a',
    primaryLight: '#99e6c1',
    primaryDark: '#35bb78',
    secondary: '#ff9800',
    secondaryLight: '#ffab66',
    secondaryDark: '#ff6800',
    surface: '#1E1E1E',
    surfaceVariant: '#2C2C2C',
    background: '#121212',
    onPrimary: '#000000',
    onSecondary: '#000000',
    onBackground: '#FFFFFF',
    onSurface: '#FFFFFF',
    onSurfaceVariant: '#B3B3B3',
    outline: '#424242',
    outlineVariant: '#2C2C2C',
    error: '#EF5350',
    warning: '#FFB74D',
    info: '#42A5F5',
    success: '#66BB6A',
    elevation: 'rgba(0, 0, 0, 0.24)',
    shadow: 'rgba(0, 0, 0, 0.24)',
  },
};
// 字体定义
const typography = {
  fontFamily: {,
  regular: 'System',
    medium: 'System',
    bold: 'System',
    light: 'System',
  },
  fontSize: {,
  xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36,
    '5xl': 48,
  },
  lineHeight: {,
  tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
  fontWeight: {,
  light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
};
// 间距定义
const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
  '3xl': 64,
};

// 圆角定义
const borderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  '2xl': 24,
  full: 9999,
};

// 阴影定义
const shadows = {
  sm: {,
  shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.18,
    shadowRadius: 1.0,
    elevation: 1,
  },
  md: {,
  shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.23,
    shadowRadius: 2.62,
    elevation: 4,
  },
  lg: {,
  shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
    elevation: 8,
  },
  xl: {,
  shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.37,
    shadowRadius: 7.49,
    elevation: 12,
  },
};

// 动画配置
const animations = {
  duration: {,
  fast: 150,
    normal: 300,
    slow: 500,
  },
  easing: {,
  linear: 'linear',
    ease: 'ease',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
  },
};
// 主题类型定义
export interface Theme {
  colors: typeof colors.light;,
  typography: typeof typography;,
  spacing: typeof spacing;,
  borderRadius: typeof borderRadius;,
  shadows: typeof shadows;,
  animations: typeof animations;,
  isDark: boolean;
}
// 主题上下文类型
interface ThemeContextType {
  theme: 'light' | 'dark';,
  toggleTheme: () => void;,
  currentTheme: Theme;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// 主题提供者组件
interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme(prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const currentTheme: Theme = {,
  colors: colors[theme],
    typography,
    spacing,
    borderRadius,
    shadows,
    animations,
    isDark: theme === 'dark',
  };

  return (
    <ThemeContext.Provider value={ theme, toggleTheme, currentTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// 主题钩子
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
// 导出主题相关类型和常量
export type { ThemeContextType };

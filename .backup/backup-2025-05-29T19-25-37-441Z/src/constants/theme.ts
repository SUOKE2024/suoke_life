/**
 * 索克生活 - 设计系统主题配置
 * 统一的UI设计规范，包含颜色、字体、间距、阴影等
 */

import { DefaultTheme } from 'react-native-paper';
import { Dimensions } from 'react-native';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

// 颜色系统
export const colors = {
  // 主色调 - 索克绿
  primary: '#35bb78',
  primaryLight: '#5dd39e',
  primaryDark: '#2a9960',
  
  // 辅助色 - 索克橙
  secondary: '#ff6800',
  secondaryLight: '#ff8533',
  secondaryDark: '#cc5200',
  
  // 功能色
  success: '#34C759',
  warning: '#FF9500',
  error: '#FF3B30',
  info: '#35bb78', // 使用索克绿作为信息色
  
  // 中性色
  white: '#FFFFFF',
  black: '#000000',
  gray50: '#F9FAFB',
  gray100: '#F3F4F6',
  gray200: '#E5E7EB',
  gray300: '#D1D5DB',
  gray400: '#9CA3AF',
  gray500: '#6B7280',
  gray600: '#4B5563',
  gray700: '#374151',
  gray800: '#1F2937',
  gray900: '#111827',
  
  // 语义化颜色
  background: '#FFFFFF',
  surface: '#FFFFFF',
  surfaceSecondary: '#F9FAFB',
  border: '#E5E7EB',
  borderLight: '#F3F4F6',
  
  // 文本颜色
  textPrimary: '#111827',
  textSecondary: '#6B7280',
  textTertiary: '#9CA3AF',
  textInverse: '#FFFFFF',
  
  // 中医特色色彩
  tcm: {
    gold: '#FFD700',
    jade: '#35bb78',
    cinnabar: '#E34234',
    indigo: '#4B0082',
    earth: '#8B4513',
  },
  
  // 健康状态色彩
  health: {
    excellent: '#35bb78',
    good: '#32D74B',
    fair: '#FF9500',
    poor: '#FF6B35',
    critical: '#FF3B30',
  },
};

// 字体系统
export const typography = {
  // 字体族
  fontFamily: {
    regular: 'System',
    medium: 'System',
    bold: 'System',
    light: 'System',
  },
  
  // 字体大小
  fontSize: {
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
  
  // 行高
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
  
  // 字重
  fontWeight: {
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
};

// 间距系统
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
  '3xl': 64,
  '4xl': 96,
};

// 圆角系统
export const borderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  '2xl': 24,
  full: 9999,
};

// 阴影系统
export const shadows = {
  none: {
    shadowColor: 'transparent',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0,
    shadowRadius: 0,
    elevation: 0,
  },
  sm: {
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  md: {
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 4,
  },
  lg: {
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 15,
    elevation: 8,
  },
  xl: {
    shadowColor: colors.black,
    shadowOffset: { width: 0, height: 20 },
    shadowOpacity: 0.25,
    shadowRadius: 25,
    elevation: 12,
  },
};

// 动画配置
export const animations = {
  duration: {
    fast: 150,
    normal: 300,
    slow: 500,
  },
  easing: {
    linear: 'linear',
    ease: 'ease',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
  },
};

// 布局配置
export const layout = {
  // 容器最大宽度
  maxWidth: {
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280,
  },
  
  // 断点
  breakpoints: {
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280,
  },
  
  // 安全区域
  safeArea: {
    top: 44,
    bottom: 34,
  },
};

// 组件默认样式
export const components = {
  button: {
    height: 48,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.lg,
  },
  
  input: {
    height: 48,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.md,
    borderWidth: 1,
  },
  
  card: {
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    backgroundColor: colors.surface,
    ...shadows.sm,
  },
  
  modal: {
    borderRadius: borderRadius.xl,
    backgroundColor: colors.surface,
    ...shadows.xl,
  },
};

// 主题类型定义
export interface Theme {
  colors: typeof colors;
  typography: typeof typography;
  spacing: typeof spacing;
  borderRadius: typeof borderRadius;
  shadows: typeof shadows;
  animations: typeof animations;
  layout: typeof layout;
  components: typeof components;
}

// 默认主题
export const theme: Theme = {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  animations,
  layout,
  components,
};

// 暗色主题
export const darkTheme: Theme = {
  ...theme,
  colors: {
    ...colors,
    background: colors.gray900,
    surface: colors.gray800,
    surfaceSecondary: colors.gray700,
    border: colors.gray600,
    borderLight: colors.gray700,
    textPrimary: colors.white,
    textSecondary: colors.gray300,
    textTertiary: colors.gray400,
  },
};

// 屏幕尺寸
export const screen = {
  width: screenWidth,
  height: screenHeight,
  isSmall: screenWidth < 375,
  isMedium: screenWidth >= 375 && screenWidth < 414,
  isLarge: screenWidth >= 414,
};

// React Native Paper 主题配置
export const themePaper = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: colors.primary,
    accent: colors.secondary,
    background: colors.background,
    surface: colors.surface,
    text: colors.textPrimary,
    disabled: colors.gray500,
    placeholder: colors.gray400,
    backdrop: 'rgba(0, 0, 0, 0.5)',
    onSurface: colors.textPrimary,
    notification: colors.primary,
  },
  fonts: {
    ...DefaultTheme.fonts,
    regular: {
      fontFamily: typography.fontFamily.regular,
      fontWeight: 'normal' as const,
    },
    medium: {
      fontFamily: typography.fontFamily.medium,
      fontWeight: '500' as const,
    },
    light: {
      fontFamily: typography.fontFamily.light,
      fontWeight: '300' as const,
    },
    thin: {
      fontFamily: typography.fontFamily.regular,
      fontWeight: '100' as const,
    },
  },
  roundness: borderRadius.md,
};

// 导出所有主题相关配置
export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  animations,
  layout,
  components,
  screen,
  themePaper,
};

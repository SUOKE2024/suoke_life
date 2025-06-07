import React from 'react';
import { DefaultTheme } from 'react-native-paper';
import { Dimensions } from 'react-native';
// 索克生活 - 设计系统主题配置
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
  info: '#35bb78',
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
  text: '#111827',
  textPrimary: '#111827',
  textSecondary: '#6B7280',
  textTertiary: '#9CA3AF',
  textInverse: '#FFFFFF',
  // 中医特色色彩
  tcm: {
      gold: "#FFD700",
      jade: '#35bb78',cinnabar: '#E34234',indigo: '#4B0082',earth: '#8B4513';
  };
  // 健康状态色彩;
  health: {
      excellent: "#35bb78",
      good: '#32D74B',fair: '#FF9500',poor: '#FF6B35',critical: '#FF3B30';
  };
};
// 字体系统
export const typography = {
  fontFamily: {,
  regular: 'System',
    medium: 'System',
    bold: 'System',
    light: 'System'
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
    '5xl': 48;
  };
  lineHeight: {tight: 1.25,normal: 1.5,relaxed: 1.75;
  };
  fontWeight: {
      light: "300",
      normal: '400',medium: '500',semibold: '600',bold: '700';
  };
};
// 间距系统
export const spacing = {xs: 4,sm: 8,md: 16,lg: 24,xl: 32,'2xl': 48,'3xl': 64,'4xl': 96;
};
// 圆角系统
export const borderRadius = {none: 0,sm: 4,md: 8,lg: 12,xl: 16,'2xl': 24,full: 9999;
};
// 阴影系统
export const shadows = {
  none: {,
  shadowColor: 'transparent',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0,
    shadowRadius: 0,
    elevation: 0;
  },
  sm: {,
  shadowColor: colors.black,
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2;
  },
  md: {,
  shadowColor: colors.black,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 4;
  },lg: {shadowColor: colors.black,shadowOffset: { width: 0, height: 10 },shadowOpacity: 0.15,shadowRadius: 15,elevation: 8;
  },xl: {shadowColor: colors.black,shadowOffset: { width: 0, height: 20 },shadowOpacity: 0.25,shadowRadius: 25,elevation: 12;
  };
};
// 动画配置
export const animations = {duration: {fast: 150,normal: 300,slow: 500;
  },easing: {
      linear: "linear",
      ease: 'ease',easeIn: 'ease-in',easeOut: 'ease-out',easeInOut: 'ease-in-out';
  };
};
// 布局配置
export const layout = {
  maxWidth: {,
  sm: 640,
    md: 768,lg: 1024,xl: 1280;
  };
  breakpoints: {sm: 640,md: 768,lg: 1024,xl: 1280;
  };
  safeArea: {top: 44,bottom: 34;
  };
};
// 组件默认样式
export const components = {
  button: {,
  height: 48,borderRadius: borderRadius.md,paddingHorizontal: spacing.lg;
  },input: {height: 48,borderRadius: borderRadius.md,paddingHorizontal: spacing.md,borderWidth: 1,borderColor: colors.border;
  },card: {borderRadius: borderRadius.lg,backgroundColor: colors.surface,...shadows.sm;
  };
};
// React Native Paper 主题配置
export const paperTheme = {...DefaultTheme,colors: {...DefaultTheme.colors,primary: colors.primary,accent: colors.secondary,background: colors.background,surface: colors.surface,text: colors.textPrimary,placeholder: colors.textSecondary,backdrop: colors.black + '50',onSurface: colors.textPrimary,notification: colors.error;
  };
};
// 导出屏幕尺寸
export const screen = {width: screenWidth,height: screenHeight;
};
// 默认导出
export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  animations,
  layout,
  components,
  paperTheme,
  screen;
};

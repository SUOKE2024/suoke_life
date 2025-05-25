import { DefaultTheme } from 'react-native-paper';
import { Dimensions } from 'react-native';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

// 颜色定义
export const colors = {
  primary: '#35bb78', // 索克绿
  primaryDark: '#0F5D35', // 深绿色
  primaryLight: '#4CAF50', // 浅绿色
  secondary: '#FF6800', // 辅助色 - 索克橙
  secondaryDark: '#F57C00', // 深橙色
  secondaryLight: '#FFB74D', // 浅橙色

  // 功能性颜色
  success: '#4CAF50',
  warning: '#FF9800',
  error: '#F44336',
  info: '#2196F3',

  // 中性颜色
  background: '#FAFAFA',
  surface: '#FFFFFF',
  onSurface: '#212121',
  onBackground: '#424242',
  disabled: '#BDBDBD',
  placeholder: '#9E9E9E',

  // 文本颜色
  text: '#212121',
  textPrimary: '#212121',
  textSecondary: '#757575',
  textLight: '#FFFFFF',

  // 基础颜色
  white: '#FFFFFF',
  black: '#000000',

  // 边框和分割线
  border: '#E0E0E0',
  divider: '#EEEEEE',

  // 智能体特色颜色
  agents: {
    xiaoai: '#E8F5E8', // 小艾 - 浅绿色（中医诊断）
    xiaoke: '#E3F2FD', // 小克 - 浅蓝色（服务管理）
    laoke: '#FFF3E0', // 老克 - 浅橙色（教育传播）
    soer: '#F3E5F5', // 索儿 - 浅紫色（生活营养）
  },

  // 四诊颜色
  diagnosis: {
    inspection: '#4CAF50', // 望诊 - 绿色
    auscultation: '#2196F3', // 闻诊 - 蓝色
    inquiry: '#FF9800', // 问诊 - 橙色
    palpation: '#9C27B0', // 切诊 - 紫色
  },

  // 体质颜色映射
  constitution: {
    balanced: '#4CAF50', // 平和质 - 绿色
    qi_deficiency: '#FFC107', // 气虚质 - 黄色
    yang_deficiency: '#FF5722', // 阳虚质 - 深橙色
    yin_deficiency: '#E91E63', // 阴虚质 - 粉红色
    phlegm_dampness: '#795548', // 痰湿质 - 棕色
    damp_heat: '#FF9800', // 湿热质 - 橙色
    blood_stasis: '#9C27B0', // 血瘀质 - 紫色
    qi_stagnation: '#607D8B', // 气郁质 - 蓝灰色
    special_diathesis: '#9E9E9E', // 特禀质 - 灰色
  },
};

// 字体配置
export const fonts = {
  // 字体族
  family: {
    regular: 'System',
    medium: 'System',
    bold: 'System',
  },

  // 字体大小
  size: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    xxl: 24,
    title: 28,
    header: 32,
  },

  // 行高
  lineHeight: {
    xs: 16,
    sm: 20,
    md: 24,
    lg: 28,
    xl: 32,
    xxl: 36,
    title: 40,
    header: 44,
  },
};

// 间距系统
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

// 圆角配置
export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 16,
  xl: 24,
  circle: 50,
};

// 阴影配置
export const shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.18,
    shadowRadius: 1.0,
    elevation: 1,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
    elevation: 8,
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
export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: colors.primary,
    accent: colors.secondary,
    background: colors.background,
    surface: colors.surface,
    text: colors.text,
    disabled: colors.disabled,
    placeholder: colors.placeholder,
    backdrop: 'rgba(0, 0, 0, 0.5)',
    onSurface: colors.onSurface,
    notification: colors.primary,
  },
  fonts: {
    ...DefaultTheme.fonts,
    regular: {
      fontFamily: fonts.family.regular,
      fontWeight: 'normal' as const,
    },
    medium: {
      fontFamily: fonts.family.medium,
      fontWeight: '500' as const,
    },
    light: {
      fontFamily: fonts.family.regular,
      fontWeight: '300' as const,
    },
    thin: {
      fontFamily: fonts.family.regular,
      fontWeight: '100' as const,
    },
  },
  roundness: borderRadius.md,
};

// 动画配置
export const animations = {
  timing: {
    short: 200,
    medium: 300,
    long: 500,
  },
  easing: {
    easeInOut: 'ease-in-out',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    linear: 'linear',
  },
};

// 导出所有主题相关配置
export default {
  colors,
  fonts,
  spacing,
  borderRadius,
  shadows,
  screen,
  theme,
  animations,
};

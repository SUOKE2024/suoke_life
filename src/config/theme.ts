import { MD3LightTheme, MD3DarkTheme, MD3Theme } from 'react-native-paper';

// 索克品牌颜色
export const BRAND_COLORS = {
  // 索克绿，主色调
  primary: '#35BB78',
  // 索克橙，辅色调
  secondary: '#FF6800',
  // 中医特色色彩，五行对应颜色
  wuxing: {
    wood: '#50A060', // 木，青色系
    fire: '#F25B53',  // 火，红色系
    earth: '#DBAE40', // 土，黄色系
    metal: '#E3E1DE', // 金，白色系
    water: '#324D61'  // 水，黑色系
  },
  // 状态颜色
  success: '#25A55F',
  warning: '#FFA726',
  error: '#E53935',
  info: '#4EA9FF',
};

// 应用级别的间距标准
export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

// 圆角半径
export const BORDER_RADIUS = {
  sm: 4,
  md: 8,
  lg: 16,
  xl: 24,
  circle: 999,
};

// 字体大小
export const FONT_SIZE = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 18,
  xl: 20,
  xxl: 24,
  xxxl: 32,
};

// 自定义浅色主题
export const lightTheme: Partial<MD3Theme> = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: BRAND_COLORS.primary,
    primaryContainer: '#E0F7EA',
    secondary: BRAND_COLORS.secondary,
    secondaryContainer: '#FFEADB',
    error: BRAND_COLORS.error,
    success: BRAND_COLORS.success,
    warning: BRAND_COLORS.warning,
    info: BRAND_COLORS.info,
    background: '#FAFAFA',
    surface: '#FFFFFF',
    // 文字颜色
    onBackground: '#1A1A1A',
    onSurface: '#1A1A1A',
    onPrimary: '#FFFFFF',
    onSecondary: '#FFFFFF',
    // 卡片背景
    elevation: {
      level0: '#FFFFFF',
      level1: '#F5F5F5',
      level2: '#EEEEEE',
      level3: '#E0E0E0',
      level4: '#D6D6D6',
      level5: '#C2C2C2',
    },
  },
  // 自定义主题变量
  spacing: SPACING,
  borderRadius: BORDER_RADIUS,
  fontSize: FONT_SIZE,
};

// 自定义深色主题
export const darkTheme: Partial<MD3Theme> = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    primary: BRAND_COLORS.primary,
    primaryContainer: '#0B3826',
    secondary: BRAND_COLORS.secondary,
    secondaryContainer: '#662B00',
    error: BRAND_COLORS.error,
    success: BRAND_COLORS.success,
    warning: BRAND_COLORS.warning,
    info: BRAND_COLORS.info,
    background: '#121212',
    surface: '#1E1E1E',
    // 文字颜色
    onBackground: '#E5E5E5',
    onSurface: '#E5E5E5',
    onPrimary: '#FFFFFF',
    onSecondary: '#FFFFFF',
    // 卡片背景
    elevation: {
      level0: '#1E1E1E',
      level1: '#232323',
      level2: '#272727',
      level3: '#2C2C2C',
      level4: '#323232',
      level5: '#383838',
    },
  },
  // 自定义主题变量
  spacing: SPACING,
  borderRadius: BORDER_RADIUS,
  fontSize: FONT_SIZE,
};

// 使用自定义属性扩展MD3Theme类型
declare global {
  namespace ReactNativePaper {
    interface Theme {
      spacing: typeof SPACING;
      borderRadius: typeof BORDER_RADIUS;
      fontSize: typeof FONT_SIZE;
    }
  }
}

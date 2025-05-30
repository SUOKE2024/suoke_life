import { Dimensions, PixelRatio, Platform, StatusBar } from "react-native";
import DeviceInfo from "react-native-device-info";


// 获取屏幕尺寸
const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get("window");

// 设计稿基准尺寸 (iPhone 12 Pro)
const DESIGN_WIDTH = 390;
const DESIGN_HEIGHT = 844;

// 设备类型枚举
export enum DeviceType {
  PHONE = "phone",
  TABLET = "tablet",
  DESKTOP = "desktop",
}

// 屏幕方向枚举
export enum Orientation {
  PORTRAIT = "portrait",
  LANDSCAPE = "landscape",
}

// 屏幕尺寸分类
export enum ScreenSize {
  SMALL = "small", // < 375px
  MEDIUM = "medium", // 375px - 414px
  LARGE = "large", // 414px - 768px
  XLARGE = "xlarge", // > 768px
}

// 响应式断点
export const BREAKPOINTS = {
  xs: 0,
  sm: 375,
  md: 414,
  lg: 768,
  xl: 1024,
  xxl: 1440,
} as const;

// 设备信息接口
export interface DeviceInfo {
  width: number;
  height: number;
  pixelRatio: number;
  fontScale: number;
  type: DeviceType;
  orientation: Orientation;
  screenSize: ScreenSize;
  isTablet: boolean;
  isPhone: boolean;
  hasNotch: boolean;
  statusBarHeight: number;
  safeAreaInsets: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
}

// 获取设备信息
export const getDeviceInfo = async (): Promise<DeviceInfo> => {
  const { width, height } = Dimensions.get("window");
  const pixelRatio = PixelRatio.get();
  const fontScale = PixelRatio.getFontScale();
  const isTablet = await DeviceInfo.isTablet();
  const hasNotch = await DeviceInfo.hasNotch();

  // 判断设备类型
  const type = isTablet ? DeviceType.TABLET : DeviceType.PHONE;

  // 判断屏幕方向
  const orientation =
    width > height ? Orientation.LANDSCAPE : Orientation.PORTRAIT;

  // 判断屏幕尺寸
  let screenSize: ScreenSize;
  if (width < BREAKPOINTS.sm) {
    screenSize = ScreenSize.SMALL;
  } else if (width < BREAKPOINTS.md) {
    screenSize = ScreenSize.MEDIUM;
  } else if (width < BREAKPOINTS.lg) {
    screenSize = ScreenSize.LARGE;
  } else {
    screenSize = ScreenSize.XLARGE;
  }

  // 状态栏高度
  const statusBarHeight =
    Platform.OS === "ios" ? (hasNotch ? 44 : 20) : StatusBar.currentHeight || 0;

  // 安全区域（简化版，实际应用中可以使用react-native-safe-area-context）
  const safeAreaInsets = {
    top: statusBarHeight,
    bottom: hasNotch ? 34 : 0,
    left: 0,
    right: 0,
  };

  return {
    width,
    height,
    pixelRatio,
    fontScale,
    type,
    orientation,
    screenSize,
    isTablet,
    isPhone: !isTablet,
    hasNotch,
    statusBarHeight,
    safeAreaInsets,
  };
};

// 尺寸适配函数
export const responsive = {
  // 宽度适配
  width: (size: number): number => {
    return (SCREEN_WIDTH / DESIGN_WIDTH) * size;
  },

  // 高度适配
  height: (size: number): number => {
    return (SCREEN_HEIGHT / DESIGN_HEIGHT) * size;
  },

  // 字体大小适配
  fontSize: (size: number): number => {
    const scale = Math.min(
      SCREEN_WIDTH / DESIGN_WIDTH,
      SCREEN_HEIGHT / DESIGN_HEIGHT
    );
    const newSize = size * scale;

    // 考虑用户字体缩放设置
    const fontScale = PixelRatio.getFontScale();
    return Math.round(PixelRatio.roundToNearestPixel(newSize / fontScale));
  },

  // 最小尺寸适配（取宽高比例的最小值）
  min: (size: number): number => {
    const scaleWidth = SCREEN_WIDTH / DESIGN_WIDTH;
    const scaleHeight = SCREEN_HEIGHT / DESIGN_HEIGHT;
    const scale = Math.min(scaleWidth, scaleHeight);
    return size * scale;
  },

  // 最大尺寸适配（取宽高比例的最大值）
  max: (size: number): number => {
    const scaleWidth = SCREEN_WIDTH / DESIGN_WIDTH;
    const scaleHeight = SCREEN_HEIGHT / DESIGN_HEIGHT;
    const scale = Math.max(scaleWidth, scaleHeight);
    return size * scale;
  },

  // 像素适配（确保在不同密度屏幕上显示一致）
  pixel: (size: number): number => {
    return PixelRatio.roundToNearestPixel(size);
  },

  // 百分比宽度
  widthPercent: (percent: number): number => {
    return (SCREEN_WIDTH * percent) / 100;
  },

  // 百分比高度
  heightPercent: (percent: number): number => {
    return (SCREEN_HEIGHT * percent) / 100;
  },
};

// 断点检查函数
export const breakpoints = {
  // 检查是否为小屏幕
  isSmall: (): boolean => SCREEN_WIDTH < BREAKPOINTS.sm,

  // 检查是否为中等屏幕
  isMedium: (): boolean =>
    SCREEN_WIDTH >= BREAKPOINTS.sm && SCREEN_WIDTH < BREAKPOINTS.md,

  // 检查是否为大屏幕
  isLarge: (): boolean =>
    SCREEN_WIDTH >= BREAKPOINTS.md && SCREEN_WIDTH < BREAKPOINTS.lg,

  // 检查是否为超大屏幕
  isXLarge: (): boolean => SCREEN_WIDTH >= BREAKPOINTS.lg,

  // 检查是否为平板
  isTablet: (): boolean => SCREEN_WIDTH >= BREAKPOINTS.lg,

  // 检查是否为手机
  isPhone: (): boolean => SCREEN_WIDTH < BREAKPOINTS.lg,

  // 检查是否为横屏
  isLandscape: (): boolean => SCREEN_WIDTH > SCREEN_HEIGHT,

  // 检查是否为竖屏
  isPortrait: (): boolean => SCREEN_WIDTH <= SCREEN_HEIGHT,
};

// 响应式样式生成器
export const createResponsiveStyles = <T extends Record<string, any>>(styles: {
  default: T;
  small?: Partial<T>;
  medium?: Partial<T>;
  large?: Partial<T>;
  xlarge?: Partial<T>;
  tablet?: Partial<T>;
  landscape?: Partial<T>;
}): T => {
  let finalStyles = { ...styles.default };

  // 根据屏幕尺寸应用样式
  if (breakpoints.isSmall() && styles.small) {
    finalStyles = { ...finalStyles, ...styles.small };
  } else if (breakpoints.isMedium() && styles.medium) {
    finalStyles = { ...finalStyles, ...styles.medium };
  } else if (breakpoints.isLarge() && styles.large) {
    finalStyles = { ...finalStyles, ...styles.large };
  } else if (breakpoints.isXLarge() && styles.xlarge) {
    finalStyles = { ...finalStyles, ...styles.xlarge };
  }

  // 平板特殊样式
  if (breakpoints.isTablet() && styles.tablet) {
    finalStyles = { ...finalStyles, ...styles.tablet };
  }

  // 横屏特殊样式
  if (breakpoints.isLandscape() && styles.landscape) {
    finalStyles = { ...finalStyles, ...styles.landscape };
  }

  return finalStyles;
};

// 响应式值选择器
export const selectResponsiveValue = <T>(values: {
  default: T;
  small?: T;
  medium?: T;
  large?: T;
  xlarge?: T;
  tablet?: T;
  landscape?: T;
}): T => {
  if (breakpoints.isLandscape() && values.landscape !== undefined) {
    return values.landscape;
  }

  if (breakpoints.isTablet() && values.tablet !== undefined) {
    return values.tablet;
  }

  if (breakpoints.isSmall() && values.small !== undefined) {
    return values.small;
  } else if (breakpoints.isMedium() && values.medium !== undefined) {
    return values.medium;
  } else if (breakpoints.isLarge() && values.large !== undefined) {
    return values.large;
  } else if (breakpoints.isXLarge() && values.xlarge !== undefined) {
    return values.xlarge;
  }

  return values.default;
};

// 网格系统
export const grid = {
  // 计算列宽
  getColumnWidth: (columns: number, gutter: number = 16): number => {
    const totalGutter = gutter * (columns - 1);
    return (SCREEN_WIDTH - totalGutter) / columns;
  },

  // 计算容器宽度
  getContainerWidth: (maxWidth?: number): number => {
    if (maxWidth && SCREEN_WIDTH > maxWidth) {
      return maxWidth;
    }
    return SCREEN_WIDTH;
  },

  // 计算边距
  getMargin: (columns: number = 12): number => {
    const margin = selectResponsiveValue({
      default: 16,
      small: 12,
      medium: 16,
      large: 24,
      xlarge: 32,
    });
    return margin;
  },

  // 计算间距
  getGutter: (): number => {
    return selectResponsiveValue({
      default: 16,
      small: 12,
      medium: 16,
      large: 20,
      xlarge: 24,
    });
  },
};

// 字体缩放工具
export const typography = {
  // 获取缩放后的字体大小
  getScaledFontSize: (baseFontSize: number): number => {
    const fontScale = PixelRatio.getFontScale();
    const scaledSize = baseFontSize * fontScale;

    // 限制最大和最小字体大小
    const minSize = baseFontSize * 0.8;
    const maxSize = baseFontSize * 1.5;

    return Math.max(minSize, Math.min(maxSize, scaledSize));
  },

  // 获取行高
  getLineHeight: (fontSize: number, ratio: number = 1.4): number => {
    return Math.round(fontSize * ratio);
  },

  // 响应式字体大小
  responsiveFontSize: (sizes: {
    default: number;
    small?: number;
    medium?: number;
    large?: number;
    xlarge?: number;
  }): number => {
    const baseSize = selectResponsiveValue(sizes);
    return typography.getScaledFontSize(baseSize);
  },
};

// 安全区域工具
export const safeArea = {
  // 获取安全区域内边距
  getSafeAreaInsets: async () => {
    const deviceInfo = await getDeviceInfo();
    return deviceInfo.safeAreaInsets;
  },

  // 获取状态栏高度
  getStatusBarHeight: async (): Promise<number> => {
    const deviceInfo = await getDeviceInfo();
    return deviceInfo.statusBarHeight;
  },

  // 获取底部安全区域高度
  getBottomSafeAreaHeight: async (): Promise<number> => {
    const deviceInfo = await getDeviceInfo();
    return deviceInfo.safeAreaInsets.bottom;
  },
};

// 触摸目标工具
export const touchTarget = {
  // 最小触摸目标尺寸
  MIN_SIZE: 44,

  // 确保触摸目标尺寸符合无障碍标准
  ensureMinimumSize: (size: number): number => {
    return Math.max(size, touchTarget.MIN_SIZE);
  },

  // 计算触摸区域内边距
  calculatePadding: (contentSize: number): number => {
    const minSize = touchTarget.MIN_SIZE;
    if (contentSize >= minSize) {
      return 0;
    }
    return (minSize - contentSize) / 2;
  },
};

// 性能优化工具
export const performance = {
  // 检查是否应该使用高性能模式
  shouldUseHighPerformance: (): boolean => {
    const pixelRatio = PixelRatio.get();
    const screenArea = SCREEN_WIDTH * SCREEN_HEIGHT;

    // 高分辨率大屏设备使用高性能模式
    return pixelRatio >= 3 || screenArea > 1000000;
  },

  // 获取推荐的图片质量
  getRecommendedImageQuality: (): number => {
    const pixelRatio = PixelRatio.get();

    if (pixelRatio >= 3) {
      return 0.8; // 高密度屏幕使用较高质量
    } else if (pixelRatio >= 2) {
      return 0.7; // 中等密度屏幕
    } else {
      return 0.6; // 低密度屏幕
    }
  },

  // 获取推荐的动画帧率
  getRecommendedFrameRate: (): number => {
    if (performance.shouldUseHighPerformance()) {
      return 60; // 高性能设备使用60fps
    } else {
      return 30; // 低性能设备使用30fps
    }
  },
};

// 方向变化监听器
export const orientationListener = {
  // 添加方向变化监听
  addListener: (callback: (orientation: Orientation) => void) => {
    const subscription = Dimensions.addEventListener("change", ({ window }) => {
      const orientation =
        window.width > window.height
          ? Orientation.LANDSCAPE
          : Orientation.PORTRAIT;
      callback(orientation);
    });

    return subscription;
  },

  // 获取当前方向
  getCurrentOrientation: (): Orientation => {
    return breakpoints.isLandscape()
      ? Orientation.LANDSCAPE
      : Orientation.PORTRAIT;
  },
};

// 导出屏幕尺寸常量
export { SCREEN_WIDTH, SCREEN_HEIGHT, DESIGN_WIDTH, DESIGN_HEIGHT };

// 默认导出响应式工具集合
export default {
  responsive,
  breakpoints,
  createResponsiveStyles,
  selectResponsiveValue,
  grid,
  typography,
  safeArea,
  touchTarget,
  performance,
  orientationListener,
  getDeviceInfo,
};

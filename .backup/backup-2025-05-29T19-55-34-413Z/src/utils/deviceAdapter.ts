import { Dimensions, Platform, PixelRatio } from "react-native";
import DeviceInfo from "react-native-device-info";

interface DeviceSpecs {
  screenWidth: number;
  screenHeight: number;
  pixelRatio: number;
  platform: string;
  version: string;
  isTablet: boolean;
  hasNotch: boolean;
}

class DeviceAdapter {
  private specs: DeviceSpecs;

  constructor() {
    const { width, height } = Dimensions.get("window");

    this.specs = {
      screenWidth: width,
      screenHeight: height,
      pixelRatio: PixelRatio.get(),
      platform: Platform.OS,
      version: Platform.Version.toString(),
      isTablet: DeviceInfo.isTablet(),
      hasNotch: DeviceInfo.hasNotch(),
    };
  }

  /**
   * 获取设备规格
   */
  getSpecs(): DeviceSpecs {
    return this.specs;
  }

  /**
   * 响应式尺寸计算
   */
  responsive(size: number): number {
    const baseWidth = 375; // iPhone X 基准宽度
    const scale = this.specs.screenWidth / baseWidth;
    return Math.round(size * scale);
  }

  /**
   * 字体大小适配
   */
  fontSize(size: number): number {
    const scale = Math.min(
      this.specs.screenWidth / 375,
      this.specs.screenHeight / 812
    );
    return Math.round(size * scale);
  }

  /**
   * 安全区域适配
   */
  getSafeAreaInsets() {
    return {
      top: this.specs.hasNotch ? 44 : 20,
      bottom: this.specs.hasNotch ? 34 : 0,
      left: 0,
      right: 0,
    };
  }

  /**
   * 检查是否为小屏设备
   */
  isSmallScreen(): boolean {
    return this.specs.screenWidth < 375 || this.specs.screenHeight < 667;
  }

  /**
   * 检查是否为大屏设备
   */
  isLargeScreen(): boolean {
    return this.specs.screenWidth > 414 || this.specs.isTablet;
  }

  /**
   * 获取适配的布局配置
   */
  getLayoutConfig() {
    return {
      columns: this.specs.isTablet ? 3 : this.isLargeScreen() ? 2 : 1,
      padding: this.responsive(16),
      margin: this.responsive(8),
      borderRadius: this.responsive(8),
    };
  }

  /**
   * 性能级别检测
   */
  getPerformanceLevel(): "low" | "medium" | "high" {
    const totalPixels = this.specs.screenWidth * this.specs.screenHeight;
    const pixelDensity = totalPixels * this.specs.pixelRatio;

    if (pixelDensity > 2000000) {
      return "high";
    }
    if (pixelDensity > 1000000) {
      return "medium";
    }
    return "low";
  }
}

export const deviceAdapter = new DeviceAdapter();
export default deviceAdapter;

/**
 * 高对比度界面生成服务
 * 根据用户需求动态生成适合视力障碍用户的高对比度界面配置
 */
import { ColorConfig } from '../types/accessibility';
import { logger } from '../utils/logger';

/**
 * 高对比度模式类型
 */
export enum HighContrastMode {
  DARK_ON_LIGHT = 'darkOnLight',
  LIGHT_ON_DARK = 'lightOnDark',
  YELLOW_ON_BLACK = 'yellowOnBlack',
  YELLOW_ON_BLUE = 'yellowOnBlue',
  CUSTOM = 'custom'
}

/**
 * 高对比度主题配置
 */
const HIGH_CONTRAST_THEMES: Record<HighContrastMode, ColorConfig> = {
  [HighContrastMode.DARK_ON_LIGHT]: {
    backgroundColor: '#FFFFFF',
    textColor: '#000000',
    primaryColor: '#000000',
    secondaryColor: '#333333',
    accentColor: '#0000FF',
    errorColor: '#FF0000',
    successColor: '#008000',
    borderColor: '#000000',
    disabledBackgroundColor: '#F0F0F0',
    disabledTextColor: '#707070'
  },
  [HighContrastMode.LIGHT_ON_DARK]: {
    backgroundColor: '#000000',
    textColor: '#FFFFFF',
    primaryColor: '#FFFFFF',
    secondaryColor: '#CCCCCC',
    accentColor: '#FFFF00',
    errorColor: '#FF6666',
    successColor: '#66FF66',
    borderColor: '#FFFFFF',
    disabledBackgroundColor: '#333333',
    disabledTextColor: '#999999'
  },
  [HighContrastMode.YELLOW_ON_BLACK]: {
    backgroundColor: '#000000',
    textColor: '#FFFF00',
    primaryColor: '#FFFF00',
    secondaryColor: '#FFDD00',
    accentColor: '#FFFFFF',
    errorColor: '#FF6666',
    successColor: '#00FF00',
    borderColor: '#FFFF00',
    disabledBackgroundColor: '#333333',
    disabledTextColor: '#999900'
  },
  [HighContrastMode.YELLOW_ON_BLUE]: {
    backgroundColor: '#00007F',
    textColor: '#FFFF00',
    primaryColor: '#FFFF00',
    secondaryColor: '#FFFFFF',
    accentColor: '#00FFFF',
    errorColor: '#FF6666',
    successColor: '#00FF00',
    borderColor: '#FFFF00',
    disabledBackgroundColor: '#000033',
    disabledTextColor: '#888800'
  },
  [HighContrastMode.CUSTOM]: {
    backgroundColor: '#FFFFFF',
    textColor: '#000000',
    primaryColor: '#000000',
    secondaryColor: '#333333',
    accentColor: '#0000FF',
    errorColor: '#FF0000',
    successColor: '#008000',
    borderColor: '#000000',
    disabledBackgroundColor: '#F0F0F0',
    disabledTextColor: '#707070'
  }
};

/**
 * 针对不同视力障碍类型的推荐对比度模式
 */
const VISION_DISABILITY_RECOMMENDATIONS: Record<string, HighContrastMode> = {
  'colorBlindness': HighContrastMode.DARK_ON_LIGHT,
  'lowVision': HighContrastMode.YELLOW_ON_BLACK,
  'lightSensitivity': HighContrastMode.LIGHT_ON_DARK,
  'contrast': HighContrastMode.YELLOW_ON_BLACK,
  'elderly': HighContrastMode.YELLOW_ON_BLUE
};

/**
 * 高对比度界面生成服务
 */
export class HighContrastService {
  /**
   * 根据用户偏好获取高对比度配置
   * @param mode 高对比度模式
   * @param customConfig 自定义配置（当mode为CUSTOM时使用）
   * @returns 高对比度颜色配置
   */
  public getHighContrastConfig(mode: HighContrastMode, customConfig?: Partial<ColorConfig>): ColorConfig {
    const baseConfig = { ...HIGH_CONTRAST_THEMES[mode] };
    
    if (mode === HighContrastMode.CUSTOM && customConfig) {
      return { ...baseConfig, ...customConfig };
    }
    
    return baseConfig;
  }
  
  /**
   * 根据视力障碍类型推荐高对比度模式
   * @param disabilityType 视力障碍类型
   * @returns 推荐的高对比度模式
   */
  public recommendModeForDisability(disabilityType: string): HighContrastMode {
    return VISION_DISABILITY_RECOMMENDATIONS[disabilityType] || HighContrastMode.DARK_ON_LIGHT;
  }
  
  /**
   * 验证自定义颜色配置的对比度是否足够
   * @param config 自定义颜色配置
   * @returns 是否通过验证
   */
  public validateContrastRatio(config: ColorConfig): boolean {
    // 检查文本颜色和背景色对比度
    const textContrastRatio = this.calculateContrastRatio(
      this.hexToRgb(config.textColor),
      this.hexToRgb(config.backgroundColor)
    );
    
    // WCAG AA标准要求文本对比度至少为4.5:1
    const passesTextContrast = textContrastRatio >= 4.5;
    
    // 检查主要操作按钮的对比度
    const primaryContrastRatio = this.calculateContrastRatio(
      this.hexToRgb(config.primaryColor),
      this.hexToRgb(config.backgroundColor)
    );
    
    // 大按钮可以接受3:1的对比度
    const passesPrimaryContrast = primaryContrastRatio >= 3.0;
    
    return passesTextContrast && passesPrimaryContrast;
  }
  
  /**
   * 为不同UI元素生成高对比度样式
   * @param mode 高对比度模式
   * @returns UI元素样式对象
   */
  public generateUIStyles(mode: HighContrastMode): Record<string, any> {
    const colors = this.getHighContrastConfig(mode);
    
    return {
      body: {
        backgroundColor: colors.backgroundColor,
        color: colors.textColor
      },
      button: {
        backgroundColor: colors.primaryColor,
        color: colors.backgroundColor,
        border: `2px solid ${colors.borderColor}`,
        padding: '12px 20px',
        fontSize: '18px',
        fontWeight: 'bold'
      },
      link: {
        color: colors.accentColor,
        textDecoration: 'underline',
        fontWeight: 'bold'
      },
      input: {
        backgroundColor: colors.backgroundColor,
        color: colors.textColor,
        border: `2px solid ${colors.borderColor}`,
        padding: '10px'
      },
      header: {
        backgroundColor: colors.primaryColor,
        color: colors.backgroundColor,
        padding: '15px'
      },
      card: {
        backgroundColor: colors.backgroundColor,
        color: colors.textColor,
        border: `3px solid ${colors.borderColor}`,
        padding: '20px'
      },
      icon: {
        color: colors.primaryColor,
        fontSize: '24px'
      },
      alert: {
        error: {
          backgroundColor: colors.errorColor,
          color: colors.backgroundColor,
          padding: '15px',
          border: `2px solid ${colors.borderColor}`
        },
        success: {
          backgroundColor: colors.successColor,
          color: '#FFFFFF',
          padding: '15px',
          border: `2px solid ${colors.borderColor}`
        }
      },
      focus: {
        outline: `4px solid ${colors.accentColor}`
      }
    };
  }
  
  /**
   * 将十六进制颜色转换为RGB对象
   * @param hex 十六进制颜色代码
   * @returns RGB颜色对象
   */
  private hexToRgb(hex: string): { r: number; g: number; b: number } {
    // 去除可能存在的#前缀
    hex = hex.replace(/^#/, '');
    
    // 解析RGB值
    const bigint = parseInt(hex, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    
    return { r, g, b };
  }
  
  /**
   * 计算两个颜色的对比度比率
   * 使用WCAG标准计算公式: https://www.w3.org/TR/WCAG20-TECHS/G17.html
   * @param rgb1 第一个RGB颜色对象
   * @param rgb2 第二个RGB颜色对象
   * @returns 对比度比率
   */
  private calculateContrastRatio(
    rgb1: { r: number; g: number; b: number },
    rgb2: { r: number; g: number; b: number }
  ): number {
    // 计算相对亮度
    const l1 = this.calculateRelativeLuminance(rgb1);
    const l2 = this.calculateRelativeLuminance(rgb2);
    
    // 计算对比度比率
    const lighter = Math.max(l1, l2);
    const darker = Math.min(l1, l2);
    
    return (lighter + 0.05) / (darker + 0.05);
  }
  
  /**
   * 计算颜色的相对亮度
   * 使用WCAG标准计算公式: https://www.w3.org/TR/WCAG20-TECHS/G17.html
   * @param rgb RGB颜色对象
   * @returns 相对亮度值
   */
  private calculateRelativeLuminance(rgb: { r: number; g: number; b: number }): number {
    // 归一化RGB值到0-1范围
    const sR = rgb.r / 255;
    const sG = rgb.g / 255;
    const sB = rgb.b / 255;
    
    // 应用gamma校正
    const R = sR <= 0.03928 ? sR / 12.92 : Math.pow((sR + 0.055) / 1.055, 2.4);
    const G = sG <= 0.03928 ? sG / 12.92 : Math.pow((sG + 0.055) / 1.055, 2.4);
    const B = sB <= 0.03928 ? sB / 12.92 : Math.pow((sB + 0.055) / 1.055, 2.4);
    
    // 计算相对亮度
    return 0.2126 * R + 0.7152 * G + 0.0722 * B;
  }
  
  /**
   * 根据用户偏好自动生成高对比度配置
   * @param userPreferences 用户偏好设置
   * @returns 高对比度颜色配置
   */
  public generateUserAdaptiveConfig(userPreferences: {
    disabilityType?: string;
    prefersDarkMode?: boolean;
    preferredColors?: string[];
    contrastLevel?: number;
  }): ColorConfig {
    try {
      let baseMode: HighContrastMode;
      
      // 根据视力障碍类型选择基础模式
      if (userPreferences.disabilityType) {
        baseMode = this.recommendModeForDisability(userPreferences.disabilityType);
      } else if (userPreferences.prefersDarkMode) {
        baseMode = HighContrastMode.LIGHT_ON_DARK;
      } else {
        baseMode = HighContrastMode.DARK_ON_LIGHT;
      }
      
      const baseConfig = this.getHighContrastConfig(baseMode);
      
      // 应用用户偏好的颜色
      if (userPreferences.preferredColors && userPreferences.preferredColors.length > 0) {
        const customConfig: Partial<ColorConfig> = { ...baseConfig };
        
        // 使用用户首选颜色作为强调色
        if (userPreferences.preferredColors[0]) {
          customConfig.accentColor = userPreferences.preferredColors[0];
        }
        
        // 验证自定义配置的对比度
        const finalConfig = { ...baseConfig, ...customConfig };
        if (this.validateContrastRatio(finalConfig)) {
          return finalConfig;
        }
      }
      
      // 如果自定义配置不满足对比度要求，返回基础配置
      return baseConfig;
    } catch (error) {
      logger.error('生成自适应高对比度配置失败', { error, userPreferences });
      // 默认返回暗底白字模式作为最安全的选择
      return this.getHighContrastConfig(HighContrastMode.LIGHT_ON_DARK);
    }
  }
}

export default new HighContrastService();
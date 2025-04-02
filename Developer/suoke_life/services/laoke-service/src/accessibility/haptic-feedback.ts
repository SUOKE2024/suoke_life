/**
 * 触感反馈服务
 * 提供触感反馈支持
 */
import { HapticFeedbackConfig } from '../types/accessibility';
import { logger } from '../utils/logger';

class HapticFeedback {
  private config: HapticFeedbackConfig = {
    enabled: true,
    intensity: 5,
    mode: 'standard',
    notificationPattern: [100, 50, 100],
    errorPattern: [100, 50, 100, 50, 100],
    confirmationPattern: [200]
  };
  
  // 支持的预设模式
  private presetPatterns: Record<string, number[]> = {
    'tap': [50],
    'double_tap': [50, 30, 50],
    'long_press': [150],
    'success': [50, 30, 100],
    'warning': [100, 30, 100, 30, 100],
    'error': [150, 30, 150, 30, 150],
    'notification': [50, 30, 50, 30, 50],
    'heartbeat': [60, 60, 60, 200, 60],
    'countdown': [30, 100, 30, 100, 30, 100],
    'progress': [20, 20, 20, 20, 20]
  };
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('触感反馈服务初始化');
  }
  
  /**
   * 配置触感反馈
   * @param config 触感反馈配置
   */
  public configure(config: Partial<HapticFeedbackConfig>): void {
    this.config = {
      ...this.config,
      ...config
    };
    logger.info('触感反馈配置已更新', this.config);
  }
  
  /**
   * 触发自定义触感反馈
   * @param pattern 振动模式数组(开启时间，关闭时间，...)
   * @param intensity 强度系数(0.0-2.0)
   * @returns 是否成功触发
   */
  public trigger(
    pattern: number[],
    intensity: number = 1.0
  ): boolean {
    if (!this.config.enabled) {
      logger.info('触感反馈未启用，忽略触发请求');
      return false;
    }
    
    // 限制强度系数在合理范围内
    const safeIntensity = Math.max(0.0, Math.min(2.0, intensity));
    
    // 根据配置的强度和强度系数调整振动模式
    const adjustedPattern = this.adjustPatternIntensity(pattern, safeIntensity);
    
    logger.info('触发触感反馈', { pattern: adjustedPattern, intensity: safeIntensity });
    
    // 实际触发逻辑将在客户端实现
    return true;
  }
  
  /**
   * 触发预设触感反馈
   * @param presetName 预设名称
   * @param intensity 强度系数(0.0-2.0)
   * @returns 是否成功触发
   */
  public triggerPreset(
    presetName: keyof typeof this.presetPatterns,
    intensity: number = 1.0
  ): boolean {
    if (!this.config.enabled) {
      logger.info('触感反馈未启用，忽略触发请求');
      return false;
    }
    
    const pattern = this.presetPatterns[presetName];
    if (!pattern) {
      logger.warn(`未找到预设模式: ${presetName}`);
      return false;
    }
    
    return this.trigger(pattern, intensity);
  }
  
  /**
   * 触发通知触感反馈
   * @param intensity 强度系数(0.0-2.0)
   * @returns 是否成功触发
   */
  public triggerNotification(intensity: number = 1.0): boolean {
    if (!this.config.enabled || !this.config.notificationPattern) {
      return false;
    }
    
    return this.trigger(this.config.notificationPattern, intensity);
  }
  
  /**
   * 触发错误触感反馈
   * @param intensity 强度系数(0.0-2.0)
   * @returns 是否成功触发
   */
  public triggerError(intensity: number = 1.0): boolean {
    if (!this.config.enabled || !this.config.errorPattern) {
      return false;
    }
    
    return this.trigger(this.config.errorPattern, intensity);
  }
  
  /**
   * 触发确认触感反馈
   * @param intensity 强度系数(0.0-2.0)
   * @returns 是否成功触发
   */
  public triggerConfirmation(intensity: number = 1.0): boolean {
    if (!this.config.enabled || !this.config.confirmationPattern) {
      return false;
    }
    
    return this.trigger(this.config.confirmationPattern, intensity);
  }
  
  /**
   * 根据强度调整振动模式
   * @param pattern 原始振动模式
   * @param intensityFactor 强度系数
   * @returns 调整后的振动模式
   */
  private adjustPatternIntensity(pattern: number[], intensityFactor: number): number[] {
    // 根据配置的基础强度和强度系数调整振动模式
    const baseIntensity = this.config.intensity / 5; // 将1-10范围转换为0.2-2.0范围
    const effectiveIntensity = baseIntensity * intensityFactor;
    
    // 根据模式进一步调整
    let modeMultiplier = 1.0;
    switch (this.config.mode) {
      case 'strong':
        modeMultiplier = 1.5;
        break;
      case 'light':
        modeMultiplier = 0.7;
        break;
      default:
        modeMultiplier = 1.0;
    }
    
    // 结合所有因素调整振动模式
    // 振动时间受强度影响，间隔时间保持不变
    return pattern.map((value, index) => {
      // 间隔时间(偶数索引)保持不变，振动时间(奇数索引)根据强度调整
      if (index % 2 === 0) {
        return Math.round(value * effectiveIntensity * modeMultiplier);
      }
      return value;
    });
  }
  
  /**
   * 触发进度反馈
   * @param progress 进度(0.0-1.0)
   * @param duration 持续时间(毫秒)
   * @returns 是否成功触发
   */
  public triggerProgress(progress: number, duration: number = 2000): boolean {
    if (!this.config.enabled) {
      return false;
    }
    
    // 限制进度在合理范围内
    const safeProgress = Math.max(0.0, Math.min(1.0, progress));
    
    // 根据进度生成脉冲序列
    // 进度越高，脉冲越密集
    const pulseCount = Math.max(1, Math.floor(safeProgress * 10));
    const pulseInterval = Math.floor(duration / (pulseCount * 2));
    const pulseLength = Math.floor(pulseInterval * 0.7);
    
    const pattern: number[] = [];
    for (let i = 0; i < pulseCount; i++) {
      pattern.push(pulseLength);
      pattern.push(pulseInterval);
    }
    
    logger.info('触发进度反馈', { progress: safeProgress, pattern });
    
    return this.trigger(pattern);
  }
  
  /**
   * 添加自定义预设模式
   * @param name 预设名称
   * @param pattern 振动模式
   * @returns 是否成功添加
   */
  public addPresetPattern(name: string, pattern: number[]): boolean {
    if (name in this.presetPatterns) {
      logger.warn(`预设模式已存在: ${name}`);
      return false;
    }
    
    this.presetPatterns[name] = pattern;
    logger.info(`添加预设模式: ${name}`, { pattern });
    
    return true;
  }
}

export default new HapticFeedback();
/**
 * 听力障碍反馈服务
 * 为听障用户提供替代反馈方式
 */
import { AccessibilityLevel, AccessibilityUserType, VisualPromptConfig } from '../types/accessibility';
import { logger } from '../utils/logger';

class HearingImpairedFeedback {
  private visualPromptConfig: VisualPromptConfig = {
    enabled: true,
    duration: 3000,
    position: 'center',
    color: '#FF6800', // 索克橙
    sizeLevel: 3
  };
  
  private captionsEnabled: boolean = true;
  private flashNotificationsEnabled: boolean = true;
  private vibrationAlertsEnabled: boolean = true;
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('听力障碍反馈服务初始化');
  }
  
  /**
   * 配置视觉提示
   * @param config 视觉提示配置
   */
  public configureVisualPrompts(config: Partial<VisualPromptConfig>): void {
    this.visualPromptConfig = {
      ...this.visualPromptConfig,
      ...config
    };
    logger.info('视觉提示配置已更新', this.visualPromptConfig);
  }
  
  /**
   * 设置字幕状态
   * @param enabled 是否启用
   */
  public setCaptionsEnabled(enabled: boolean): void {
    this.captionsEnabled = enabled;
    logger.info(`字幕${enabled ? '已启用' : '已禁用'}`);
  }
  
  /**
   * 设置闪光通知状态
   * @param enabled 是否启用
   */
  public setFlashNotificationsEnabled(enabled: boolean): void {
    this.flashNotificationsEnabled = enabled;
    logger.info(`闪光通知${enabled ? '已启用' : '已禁用'}`);
  }
  
  /**
   * 设置振动提醒状态
   * @param enabled 是否启用
   */
  public setVibrationAlertsEnabled(enabled: boolean): void {
    this.vibrationAlertsEnabled = enabled;
    logger.info(`振动提醒${enabled ? '已启用' : '已禁用'}`);
  }
  
  /**
   * 显示视觉提示
   * @param message 提示消息
   * @param options 可选配置
   * @returns 提示ID
   */
  public showVisualPrompt(
    message: string, 
    options?: Partial<VisualPromptConfig>
  ): string {
    if (!this.visualPromptConfig.enabled) {
      logger.info('视觉提示未启用，忽略显示请求');
      return '';
    }
    
    const config = {
      ...this.visualPromptConfig,
      ...options
    };
    
    const promptId = `vp-${Date.now()}`;
    logger.info(`显示视觉提示: ${message}`, { config, promptId });
    
    // 实际显示逻辑将在客户端实现
    // 这里仅返回提示ID用于后续操作
    
    return promptId;
  }
  
  /**
   * 添加动态字幕
   * @param content 字幕内容
   * @param durationMs 持续时间(毫秒)
   */
  public addCaption(content: string, durationMs?: number): void {
    if (!this.captionsEnabled) {
      logger.info('字幕未启用，忽略添加请求');
      return;
    }
    
    const duration = durationMs || content.length * 100;
    logger.info(`添加字幕: ${content}`, { duration });
    
    // 实际字幕添加逻辑将在客户端实现
  }
  
  /**
   * 触发闪光通知
   * @param intensity 强度(1-5)
   * @param color 颜色(HEX)
   * @param durationMs 持续时间(毫秒)
   */
  public triggerFlashNotification(
    intensity: number = 3,
    color: string = '#FF6800',
    durationMs: number = 1000
  ): void {
    if (!this.flashNotificationsEnabled) {
      logger.info('闪光通知未启用，忽略触发请求');
      return;
    }
    
    // 限制强度在1-5范围内
    const safeIntensity = Math.max(1, Math.min(5, intensity));
    
    logger.info('触发闪光通知', { intensity: safeIntensity, color, duration: durationMs });
    
    // 实际闪光通知逻辑将在客户端实现
  }
  
  /**
   * 触发振动提醒
   * @param pattern 振动模式数组(开启时间，关闭时间，...)
   */
  public triggerVibration(pattern: number[] = [200, 100, 200]): void {
    if (!this.vibrationAlertsEnabled) {
      logger.info('振动提醒未启用，忽略触发请求');
      return;
    }
    
    logger.info('触发振动提醒', { pattern });
    
    // 实际振动提醒逻辑将在客户端实现
  }
  
  /**
   * 根据提示类型展示听障用户反馈
   * @param type 提示类型
   * @param message 提示消息
   */
  public showAlert(
    type: 'info' | 'warning' | 'error' | 'success',
    message: string
  ): void {
    // 根据提示类型选择不同颜色
    const colorMap = {
      info: '#35BB78', // 索克绿
      warning: '#FFA500',
      error: '#FF0000',
      success: '#35BB78' // 索克绿
    };
    
    // 显示视觉提示
    this.showVisualPrompt(message, { 
      color: colorMap[type],
      position: type === 'error' ? 'center' : 'top'
    });
    
    // 添加字幕
    this.addCaption(message);
    
    // 错误和警告使用振动提醒
    if (type === 'error' || type === 'warning') {
      const pattern = type === 'error' ? [200, 100, 200, 100, 200] : [200, 100, 200];
      this.triggerVibration(pattern);
      
      // 错误和警告使用闪光通知
      this.triggerFlashNotification(
        type === 'error' ? 5 : 3,
        colorMap[type],
        type === 'error' ? 1500 : 1000
      );
    }
  }
}

export default new HearingImpairedFeedback();
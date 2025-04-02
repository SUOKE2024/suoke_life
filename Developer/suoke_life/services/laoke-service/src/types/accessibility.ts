/**
 * 无障碍相关类型定义
 */

/**
 * 无障碍级别枚举
 */
export enum AccessibilityLevel {
  // 基础级别
  BASIC = 'basic',
  // 中等级别
  MEDIUM = 'medium',
  // 高级别
  ADVANCED = 'advanced',
  // 完全无障碍级别
  FULL = 'full'
}

/**
 * 无障碍用户类型枚举
 */
export enum AccessibilityUserType {
  // 视觉障碍用户
  VISUAL_IMPAIRED = 'visual_impaired',
  // 听觉障碍用户
  HEARING_IMPAIRED = 'hearing_impaired',
  // 运动障碍用户
  MOTOR_IMPAIRED = 'motor_impaired',
  // 认知障碍用户
  COGNITIVE_IMPAIRED = 'cognitive_impaired',
  // 老年用户
  ELDERLY = 'elderly',
  // 普通用户
  REGULAR = 'regular'
}

/**
 * 无障碍配置类型
 */
export interface AccessibilityConfig {
  // 用户类型
  userType: AccessibilityUserType;
  // 无障碍级别
  level: AccessibilityLevel;
  // 是否启用高对比度
  highContrast?: boolean;
  // 是否启用大字体
  largeText?: boolean;
  // 是否启用屏幕阅读
  screenReader?: boolean;
  // 是否启用字幕
  captions?: boolean;
  // 是否启用手语
  signLanguage?: boolean;
  // 是否启用简化界面
  simplifiedInterface?: boolean;
  // 是否启用触觉反馈
  hapticFeedback?: boolean;
  // 是否启用慢速动画
  slowAnimations?: boolean;
  // 文本朗读速度 (0-100)
  speechRate?: number;
  // 自定义设置
  customSettings?: Record<string, any>;
}

/**
 * 音频描述配置
 */
export interface AudioDescriptionConfig {
  // 是否启用
  enabled: boolean;
  // 音量 (0-100)
  volume: number;
  // 语速 (0-100)
  speed: number;
  // 音调 (0-100)
  pitch: number;
  // 语音性别 ('male' | 'female')
  voiceGender: 'male' | 'female';
}

/**
 * 视觉提示配置
 */
export interface VisualPromptConfig {
  // 是否启用
  enabled: boolean;
  // 持续时间(毫秒)
  duration: number;
  // 位置 ('top' | 'bottom' | 'center')
  position: 'top' | 'bottom' | 'center';
  // 颜色
  color: string;
  // 大小级别 (1-5)
  sizeLevel: number;
}

/**
 * 手语翻译配置
 */
export interface SignLanguageConfig {
  // 是否启用
  enabled: boolean;
  // 手语类型 ('csl' 中国手语 | 'asl' 美国手语)
  type: 'csl' | 'asl';
  // 大小比例 (0.5-2.0)
  scale: number;
  // 位置 ('top-right' | 'bottom-right' | 'full')
  position: 'top-right' | 'bottom-right' | 'full';
  // 速度调整 (0.5-2.0)
  speed: number;
}

/**
 * 触觉反馈配置
 */
export interface HapticFeedbackConfig {
  // 是否启用
  enabled: boolean;
  // 强度 (1-10)
  intensity: number;
  // 模式 ('standard' | 'strong' | 'light')
  mode: 'standard' | 'strong' | 'light';
  // 用于通知的震动模式
  notificationPattern?: number[];
  // 用于错误的震动模式
  errorPattern?: number[];
  // 用于确认的震动模式
  confirmationPattern?: number[];
}

/**
 * 认知辅助配置
 */
export interface CognitiveAssistanceConfig {
  // 是否启用
  enabled: boolean;
  // 界面简化级别 (1-5)
  simplificationLevel: number;
  // 是否显示任务分解
  taskBreakdown: boolean;
  // 是否使用图形指示
  useGraphicalCues: boolean;
  // 是否显示重复提醒
  repeatInstructions: boolean;
  // 文本简化级别 (1-5)
  textSimplificationLevel: number;
}

/**
 * 导航辅助配置
 */
export interface NavigationAssistanceConfig {
  // 是否启用
  enabled: boolean;
  // 导航提示模式 ('voice' | 'visual' | 'both')
  promptMode: 'voice' | 'visual' | 'both';
  // 自动聚焦元素
  autoFocus: boolean;
  // 是否提供页面概览
  pageOverview: boolean;
  // 提供快捷导航
  quickNavigation: boolean;
  // 导航设计模式 ('linear' | 'grouped')
  navigationPattern: 'linear' | 'grouped';
}
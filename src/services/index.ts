/**
 * services 统一导出文件
 * 索克生活APP - 架构优化
 */

// 基础服务导出
export { default as agentService } from './agentService';
export { default as authService } from './authService';
export { default as enhancedApiClient } from './enhancedApiClient';
export { default as realTimeSync } from './realTimeSync';

// UI/UX优化服务完整导出
export {
  UIUXOptimizationService,
  AnimationManager,
  PerformanceOptimizer,
  InteractionEnhancer,
  VisualEffectManager,
  ResponsiveManager,
  createUIUXOptimizationService,
  defaultPerformanceConfig,
  defaultVisualEffectConfig,
  defaultResponsiveConfig,
  defaultThemeConfig,
} from './uiUxOptimizationService';

// UI/UX优化服务类型导出
export type {
  AnimationConfig,
  AdvancedAnimationType,
  PerformanceConfig,
  PerformanceMetrics,
  PerformanceWarningLevel,
  InteractionFeedback,
  VisualEffectConfig,
  ResponsiveConfig,
  ThemeConfig,
} from './uiUxOptimizationService';

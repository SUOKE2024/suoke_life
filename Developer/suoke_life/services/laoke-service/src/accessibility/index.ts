/**
 * 老克服务 - 无障碍支持模块
 * 提供全面的无障碍功能支持，包括视觉、听觉、运动和认知障碍辅助
 */
import { AccessibilityLevel, AccessibilityUserType } from '../types/accessibility';
import hearingImpairedFeedback from './hearing-impaired-feedback';
import visualImpairedService from './visual-impaired-service';
import navigationAssistance from './navigation-assistance';
import hapticFeedback from './haptic-feedback';
import signLanguageService from './sign-language-service';
import cognitiveAssistance from './cognitive-assistance';

/**
 * 无障碍服务管理
 * 统一管理和暴露所有无障碍服务
 */
export default {
  // 听力障碍支持
  hearingImpaired: hearingImpairedFeedback,
  
  // 视觉障碍支持
  visualImpaired: visualImpairedService,
  
  // 导航辅助
  navigation: navigationAssistance,
  
  // 触感反馈
  haptic: hapticFeedback,
  
  // 手语支持
  signLanguage: signLanguageService,
  
  // 认知辅助
  cognitive: cognitiveAssistance,
  
  // 类型导出
  types: {
    AccessibilityLevel,
    AccessibilityUserType
  }
};

// 导出类型和枚举
export * from '../types/accessibility';

// 导出各模块
export { default as HearingImpairedFeedback } from './hearing-impaired-feedback';
export { default as VisualImpairedService } from './visual-impaired-service';
export { default as NavigationAssistance } from './navigation-assistance';
export { default as HapticFeedback } from './haptic-feedback';
export { default as SignLanguageService } from './sign-language-service';
export { default as CognitiveAssistance } from './cognitive-assistance';
import { logger } from '../../utils/logger';
import * as screenReader from './screen-reader';
import * as voiceNavigation from './voice-navigation';

// 用户无障碍配置文件
export interface UserAccessibilityProfile {
  userId: string;
  screenReaderSettings: screenReader.ScreenReaderSettings;
  navigationSettings: voiceNavigation.VoiceNavigationSettings;
  lastUpdated: string;
  preferences: {
    highContrast: boolean;
    largeText: boolean;
    reduceMotion: boolean;
    reduceTransparency: boolean;
    invertColors: boolean;
    monoAudio: boolean;
    fontStyle?: string;
    gestureMode: 'standard' | 'assistive' | 'simplified';
    touchAccommodations: boolean;
    automatedActions: boolean;
  };
  medicalInfo?: {
    visualImpairment?: 'none' | 'low' | 'blind';
    hearingImpairment?: 'none' | 'low' | 'deaf';
    mobilityImpairment?: 'none' | 'low' | 'high';
    cognitiveImpairment?: 'none' | 'low' | 'high';
  };
  assistiveTech?: {
    screenReader?: boolean;
    switchControl?: boolean;
    hearingAid?: boolean;
    brailleDisplay?: boolean;
    eyeTracking?: boolean;
    voiceControl?: boolean;
  };
}

// 无障碍界面组件状态
export interface AccessibilityComponentState {
  highContrastMode: boolean;
  largeTextMode: boolean;
  reducedMotionMode: boolean;
  reducedTransparencyMode: boolean;
  gestureMode: 'standard' | 'assistive' | 'simplified';
  fontStyle: string;
}

// 用户无障碍配置存储
const userProfileStore: Record<string, UserAccessibilityProfile> = {};

// 当前应用的无障碍状态
let globalAccessibilityState: AccessibilityComponentState = {
  highContrastMode: false,
  largeTextMode: false,
  reducedMotionMode: false,
  reducedTransparencyMode: false,
  gestureMode: 'standard',
  fontStyle: 'default'
};

// 界面组件注册表
const registeredComponents: Record<string, {
  elementType: string;
  status: 'active' | 'inactive';
  lastUpdated: string;
}> = {};

/**
 * 获取用户无障碍配置
 */
export const getUserProfile = (userId: string): UserAccessibilityProfile | null => {
  return userProfileStore[userId] || null;
};

/**
 * 创建或更新用户无障碍配置
 */
export const createOrUpdateUserProfile = (userId: string, profile: Partial<UserAccessibilityProfile>): UserAccessibilityProfile => {
  const currentProfile = getUserProfile(userId);
  
  const updatedProfile: UserAccessibilityProfile = {
    userId,
    screenReaderSettings: profile.screenReaderSettings || (currentProfile?.screenReaderSettings || screenReader.getUserSettings(userId)),
    navigationSettings: profile.navigationSettings || (currentProfile?.navigationSettings || voiceNavigation.getUserNavigationSettings(userId)),
    lastUpdated: new Date().toISOString(),
    preferences: {
      ...((currentProfile?.preferences || {
        highContrast: false,
        largeText: false,
        reduceMotion: false,
        reduceTransparency: false,
        invertColors: false,
        monoAudio: false,
        gestureMode: 'standard',
        touchAccommodations: false,
        automatedActions: false
      })),
      ...(profile.preferences || {})
    },
    medicalInfo: {
      ...(currentProfile?.medicalInfo || {}),
      ...(profile.medicalInfo || {})
    },
    assistiveTech: {
      ...(currentProfile?.assistiveTech || {}),
      ...(profile.assistiveTech || {})
    }
  };
  
  userProfileStore[userId] = updatedProfile;
  
  // 同步更新屏幕阅读器和导航设置
  screenReader.updateUserSettings(userId, updatedProfile.screenReaderSettings);
  voiceNavigation.updateUserNavigationSettings(userId, updatedProfile.navigationSettings);
  
  logger.info(`用户无障碍配置已更新: ${userId}`);
  return updatedProfile;
};

/**
 * 删除用户无障碍配置
 */
export const deleteUserProfile = (userId: string): boolean => {
  if (!userProfileStore[userId]) {
    return false;
  }
  
  delete userProfileStore[userId];
  logger.info(`用户无障碍配置已删除: ${userId}`);
  return true;
};

/**
 * 设置全局无障碍状态
 */
export const setGlobalAccessibilityState = (state: Partial<AccessibilityComponentState>): AccessibilityComponentState => {
  globalAccessibilityState = {
    ...globalAccessibilityState,
    ...state
  };
  
  logger.info('全局无障碍状态已更新', { state: globalAccessibilityState });
  return globalAccessibilityState;
};

/**
 * 获取全局无障碍状态
 */
export const getGlobalAccessibilityState = (): AccessibilityComponentState => {
  return { ...globalAccessibilityState };
};

/**
 * 注册无障碍组件
 */
export const registerAccessibilityComponent = (componentId: string, elementType: string): void => {
  registeredComponents[componentId] = {
    elementType,
    status: 'active',
    lastUpdated: new Date().toISOString()
  };
  
  logger.debug(`已注册无障碍组件: ${componentId}, 类型: ${elementType}`);
};

/**
 * 更新无障碍组件状态
 */
export const updateComponentStatus = (componentId: string, status: 'active' | 'inactive'): boolean => {
  if (!registeredComponents[componentId]) {
    logger.warn(`尝试更新不存在的组件: ${componentId}`);
    return false;
  }
  
  registeredComponents[componentId].status = status;
  registeredComponents[componentId].lastUpdated = new Date().toISOString();
  
  logger.debug(`更新无障碍组件状态: ${componentId}, 状态: ${status}`);
  return true;
};

/**
 * 应用用户偏好到全局状态
 */
export const applyUserPreferences = (userId: string): boolean => {
  const profile = getUserProfile(userId);
  if (!profile) {
    logger.warn(`尝试应用不存在的用户偏好: ${userId}`);
    return false;
  }
  
  setGlobalAccessibilityState({
    highContrastMode: profile.preferences.highContrast,
    largeTextMode: profile.preferences.largeText,
    reducedMotionMode: profile.preferences.reduceMotion,
    reducedTransparencyMode: profile.preferences.reduceTransparency,
    gestureMode: profile.preferences.gestureMode,
    fontStyle: profile.preferences.fontStyle || 'default'
  });
  
  // 更新屏幕阅读器设置
  screenReader.updateUserSettings(userId, profile.screenReaderSettings);
  
  // 更新导航设置
  voiceNavigation.updateUserNavigationSettings(userId, profile.navigationSettings);
  
  logger.info(`已应用用户偏好到全局状态: ${userId}`);
  return true;
};

/**
 * 创建辅助语音提示
 */
export const createAccessibilityAnnouncement = async (userId: string, message: string, priority: number = 3): Promise<boolean> => {
  try {
    const profile = getUserProfile(userId);
    if (!profile || !profile.screenReaderSettings.enabled) {
      logger.debug(`用户${userId}的屏幕阅读功能未启用，跳过语音提示`);
      return false;
    }
    
    await screenReader.readText(message, userId, priority);
    logger.debug(`已创建辅助语音提示: "${message}", 用户: ${userId}`);
    return true;
  } catch (error) {
    logger.error('创建辅助语音提示失败:', error);
    return false;
  }
};

/**
 * 初始化示例用户配置
 */
export const initSampleUserProfiles = (): void => {
  // 视障用户配置
  const visuallyImpairedProfile: UserAccessibilityProfile = {
    userId: 'vi_user_001',
    screenReaderSettings: {
      enabled: true,
      readingSpeed: 1.2,
      readingVolume: 1.0,
      verbosityLevel: 'high',
      autoReadOnFocus: true,
      autoReadOnHover: true,
      dialect: 1, // MANDARIN
      interruptOnAction: true,
      useCustomDescriptions: true
    },
    navigationSettings: {
      enabled: true,
      navigationVolume: 1.0,
      navigationSpeed: 1.1,
      dialect: 1, // MANDARIN
      distanceUnit: 'meters',
      verbosityLevel: 'high',
      autoAnnouncePoints: true,
      autoAnnounceObstacles: true,
      vibrateOnInstructions: true,
      useBinauralAudio: true,
      repeatInstructionsInterval: 30
    },
    lastUpdated: new Date().toISOString(),
    preferences: {
      highContrast: true,
      largeText: true,
      reduceMotion: true,
      reduceTransparency: true,
      invertColors: false,
      monoAudio: false,
      gestureMode: 'assistive',
      touchAccommodations: true,
      automatedActions: true
    },
    medicalInfo: {
      visualImpairment: 'high',
      hearingImpairment: 'none',
      mobilityImpairment: 'low',
      cognitiveImpairment: 'none'
    },
    assistiveTech: {
      screenReader: true,
      brailleDisplay: true,
      voiceControl: true
    }
  };
  
  // 听障用户配置
  const hearingImpairedProfile: UserAccessibilityProfile = {
    userId: 'hi_user_001',
    screenReaderSettings: {
      enabled: false,
      readingSpeed: 1.0,
      readingVolume: 1.0,
      verbosityLevel: 'medium',
      autoReadOnFocus: false,
      autoReadOnHover: false,
      dialect: 1, // MANDARIN
      interruptOnAction: true,
      useCustomDescriptions: false
    },
    navigationSettings: {
      enabled: false,
      navigationVolume: 1.0,
      navigationSpeed: 1.0,
      dialect: 1, // MANDARIN
      distanceUnit: 'meters',
      verbosityLevel: 'medium',
      autoAnnouncePoints: false,
      autoAnnounceObstacles: false,
      vibrateOnInstructions: true,
      useBinauralAudio: false,
      repeatInstructionsInterval: 0
    },
    lastUpdated: new Date().toISOString(),
    preferences: {
      highContrast: false,
      largeText: false,
      reduceMotion: false,
      reduceTransparency: false,
      invertColors: false,
      monoAudio: true,
      gestureMode: 'standard',
      touchAccommodations: false,
      automatedActions: false
    },
    medicalInfo: {
      visualImpairment: 'none',
      hearingImpairment: 'high',
      mobilityImpairment: 'none',
      cognitiveImpairment: 'none'
    },
    assistiveTech: {
      hearingAid: true
    }
  };
  
  // 行动不便用户配置
  const mobilityImpairedProfile: UserAccessibilityProfile = {
    userId: 'mi_user_001',
    screenReaderSettings: {
      enabled: false,
      readingSpeed: 1.0,
      readingVolume: 1.0,
      verbosityLevel: 'medium',
      autoReadOnFocus: false,
      autoReadOnHover: false,
      dialect: 1, // MANDARIN
      interruptOnAction: true,
      useCustomDescriptions: false
    },
    navigationSettings: {
      enabled: true,
      navigationVolume: 1.0,
      navigationSpeed: 1.0,
      dialect: 1, // MANDARIN
      distanceUnit: 'meters',
      verbosityLevel: 'high',
      autoAnnouncePoints: true,
      autoAnnounceObstacles: true,
      vibrateOnInstructions: false,
      useBinauralAudio: false,
      repeatInstructionsInterval: 0
    },
    lastUpdated: new Date().toISOString(),
    preferences: {
      highContrast: false,
      largeText: false,
      reduceMotion: true,
      reduceTransparency: false,
      invertColors: false,
      monoAudio: false,
      gestureMode: 'simplified',
      touchAccommodations: true,
      automatedActions: true
    },
    medicalInfo: {
      visualImpairment: 'none',
      hearingImpairment: 'none',
      mobilityImpairment: 'high',
      cognitiveImpairment: 'none'
    },
    assistiveTech: {
      switchControl: true,
      voiceControl: true
    }
  };
  
  // 认知障碍用户配置
  const cognitiveImpairedProfile: UserAccessibilityProfile = {
    userId: 'ci_user_001',
    screenReaderSettings: {
      enabled: true,
      readingSpeed: 0.8,
      readingVolume: 1.0,
      verbosityLevel: 'low',
      autoReadOnFocus: true,
      autoReadOnHover: false,
      dialect: 1, // MANDARIN
      interruptOnAction: false,
      useCustomDescriptions: true
    },
    navigationSettings: {
      enabled: true,
      navigationVolume: 1.0,
      navigationSpeed: 0.8,
      dialect: 1, // MANDARIN
      distanceUnit: 'meters',
      verbosityLevel: 'low',
      autoAnnouncePoints: true,
      autoAnnounceObstacles: true,
      vibrateOnInstructions: true,
      useBinauralAudio: false,
      repeatInstructionsInterval: 60
    },
    lastUpdated: new Date().toISOString(),
    preferences: {
      highContrast: true,
      largeText: true,
      reduceMotion: true,
      reduceTransparency: true,
      invertColors: false,
      monoAudio: false,
      gestureMode: 'simplified',
      touchAccommodations: true,
      automatedActions: true
    },
    medicalInfo: {
      visualImpairment: 'none',
      hearingImpairment: 'none',
      mobilityImpairment: 'low',
      cognitiveImpairment: 'high'
    },
    assistiveTech: {
      screenReader: true,
      voiceControl: true
    }
  };
  
  // 老年用户配置
  const elderlyProfile: UserAccessibilityProfile = {
    userId: 'elderly_user_001',
    screenReaderSettings: {
      enabled: false,
      readingSpeed: 0.9,
      readingVolume: 1.0,
      verbosityLevel: 'medium',
      autoReadOnFocus: false,
      autoReadOnHover: false,
      dialect: 1, // MANDARIN
      interruptOnAction: true,
      useCustomDescriptions: false
    },
    navigationSettings: {
      enabled: true,
      navigationVolume: 1.0,
      navigationSpeed: 0.9,
      dialect: 1, // MANDARIN
      distanceUnit: 'meters',
      verbosityLevel: 'high',
      autoAnnouncePoints: true,
      autoAnnounceObstacles: true,
      vibrateOnInstructions: true,
      useBinauralAudio: false,
      repeatInstructionsInterval: 45
    },
    lastUpdated: new Date().toISOString(),
    preferences: {
      highContrast: true,
      largeText: true,
      reduceMotion: true,
      reduceTransparency: true,
      invertColors: false,
      monoAudio: false,
      gestureMode: 'simplified',
      touchAccommodations: true,
      automatedActions: false
    },
    medicalInfo: {
      visualImpairment: 'low',
      hearingImpairment: 'low',
      mobilityImpairment: 'low',
      cognitiveImpairment: 'low'
    },
    assistiveTech: {}
  };
  
  // 将示例配置存入存储
  userProfileStore['vi_user_001'] = visuallyImpairedProfile;
  userProfileStore['hi_user_001'] = hearingImpairedProfile;
  userProfileStore['mi_user_001'] = mobilityImpairedProfile;
  userProfileStore['ci_user_001'] = cognitiveImpairedProfile;
  userProfileStore['elderly_user_001'] = elderlyProfile;
  
  logger.info('已初始化5个示例用户无障碍配置');
};
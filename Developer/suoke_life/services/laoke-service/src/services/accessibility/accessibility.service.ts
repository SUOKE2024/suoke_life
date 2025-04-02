import logger from '../../core/utils/logger';
import { AccessibilityProfileModel } from '../../models/accessibility-profile.model';
import { ApiError } from '../../core/utils/errors';

/**
 * 获取用户无障碍配置
 */
export const getUserAccessibilityProfile = async (userId: string) => {
  try {
    // 查找用户配置
    let profile = await AccessibilityProfileModel.findOne({ userId }).lean();
    
    // 如果不存在，返回默认配置
    if (!profile) {
      const defaultProfile = new AccessibilityProfileModel({
        userId,
        visualSettings: {
          textSize: 'medium',
          highContrast: false,
          reduceMotion: false,
          colorBlindMode: 'none',
          screenReader: false,
          invertColors: false,
          fontType: 'default'
        },
        audioSettings: {
          voiceFeedback: false,
          soundEffects: true,
          hapticFeedback: true,
          voiceRecognition: false,
          voiceSpeed: 1.0,
          voicePitch: 1.0
        },
        interactionSettings: {
          autoCompleteEnabled: true,
          extendedTouch: false,
          singleTapMode: false,
          keyboardNavigation: false,
          gestureControl: false,
          mouseDwell: false,
          mouseSpeed: 1.0
        },
        navigationSettings: {
          simplifiedNavigation: false,
          shortcutsEnabled: true,
          breadcrumbsEnabled: true,
          pageStructure: 'standard'
        },
        dialectPreference: 'standard',
        createdAt: new Date(),
        updatedAt: new Date()
      });
      
      await defaultProfile.save();
      profile = defaultProfile.toObject();
    }
    
    return profile;
  } catch (error) {
    logger.error(`获取用户无障碍配置错误 [用户ID: ${userId}]:`, error);
    throw new ApiError(500, '获取用户无障碍配置失败');
  }
};

/**
 * 更新用户无障碍配置
 */
export const updateUserAccessibilityProfile = async (userId: string, data: any) => {
  try {
    // 查找用户配置
    let profile = await AccessibilityProfileModel.findOne({ userId });
    
    // 如果不存在，创建新配置
    if (!profile) {
      profile = new AccessibilityProfileModel({
        userId,
        ...data,
        createdAt: new Date(),
        updatedAt: new Date()
      });
    } else {
      // 合并更新数据
      
      // 视觉设置
      if (data.visualSettings) {
        profile.visualSettings = {
          ...profile.visualSettings,
          ...data.visualSettings
        };
      }
      
      // 音频设置
      if (data.audioSettings) {
        profile.audioSettings = {
          ...profile.audioSettings,
          ...data.audioSettings
        };
      }
      
      // 交互设置
      if (data.interactionSettings) {
        profile.interactionSettings = {
          ...profile.interactionSettings,
          ...data.interactionSettings
        };
      }
      
      // 导航设置
      if (data.navigationSettings) {
        profile.navigationSettings = {
          ...profile.navigationSettings,
          ...data.navigationSettings
        };
      }
      
      // 方言偏好
      if (data.dialectPreference) {
        profile.dialectPreference = data.dialectPreference;
      }
      
      profile.updatedAt = new Date();
    }
    
    await profile.save();
    
    return profile.toObject();
  } catch (error) {
    logger.error(`更新用户无障碍配置错误 [用户ID: ${userId}]:`, error);
    throw new ApiError(500, '更新用户无障碍配置失败');
  }
};

/**
 * 获取无障碍资源
 */
export const getAccessibilityResources = async () => {
  try {
    // 这里可以从数据库或配置文件获取无障碍资源
    // 暂时返回静态资源
    return {
      guideDocs: [
        {
          id: 'screen-reader-guide',
          title: '屏幕阅读器使用指南',
          description: '了解如何使用屏幕阅读器浏览索克生活应用',
          url: '/docs/accessibility/screen-reader-guide'
        },
        {
          id: 'voice-control-guide',
          title: '语音控制使用指南',
          description: '了解如何使用语音命令控制索克生活应用',
          url: '/docs/accessibility/voice-control-guide'
        },
        {
          id: 'keyboard-navigation-guide',
          title: '键盘导航使用指南',
          description: '了解如何使用键盘快捷键导航索克生活应用',
          url: '/docs/accessibility/keyboard-navigation-guide'
        }
      ],
      accessibilityFeatures: [
        {
          id: 'screen-reader',
          title: '屏幕阅读器',
          description: '将屏幕内容转换为语音输出',
          category: 'visual'
        },
        {
          id: 'voice-control',
          title: '语音控制',
          description: '使用语音命令控制应用',
          category: 'interaction'
        },
        {
          id: 'high-contrast',
          title: '高对比度模式',
          description: '增强文本和背景的对比度，提高可读性',
          category: 'visual'
        },
        {
          id: 'text-size',
          title: '文本大小调整',
          description: '根据需要调整应用中的文本大小',
          category: 'visual'
        },
        {
          id: 'dialect-support',
          title: '方言支持',
          description: '支持多种中国方言的识别和合成',
          category: 'audio'
        }
      ],
      supportContacts: {
        email: 'accessibility@suoke.life',
        phone: '400-123-4567',
        hours: '9:00-18:00 (周一至周五)'
      }
    };
  } catch (error) {
    logger.error('获取无障碍资源错误:', error);
    throw new ApiError(500, '获取无障碍资源失败');
  }
}; 
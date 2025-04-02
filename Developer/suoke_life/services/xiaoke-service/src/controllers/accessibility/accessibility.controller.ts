import { Request, Response } from 'express';
import { logger } from '../../utils/logger';
import * as screenReader from '../../services/accessibility/screen-reader';
import * as voiceNavigation from '../../services/accessibility/voice-navigation';
import * as accessibilityFramework from '../../services/accessibility/accessibility-framework';
import { v4 as uuidv4 } from 'uuid';

/**
 * 获取用户无障碍配置
 */
export const getUserProfile = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      res.status(400).json({ error: '缺少用户ID参数' });
      return;
    }
    
    const profile = accessibilityFramework.getUserProfile(userId);
    
    if (!profile) {
      res.status(404).json({ error: '未找到用户无障碍配置' });
      return;
    }
    
    res.status(200).json({ profile });
  } catch (error) {
    logger.error('获取用户无障碍配置失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 创建或更新用户无障碍配置
 */
export const createOrUpdateUserProfile = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const profileData = req.body;
    
    if (!userId) {
      res.status(400).json({ error: '缺少用户ID参数' });
      return;
    }
    
    if (!profileData) {
      res.status(400).json({ error: '缺少配置数据' });
      return;
    }
    
    const updatedProfile = accessibilityFramework.createOrUpdateUserProfile(userId, profileData);
    
    res.status(200).json({ profile: updatedProfile });
  } catch (error) {
    logger.error('创建或更新用户无障碍配置失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 删除用户无障碍配置
 */
export const deleteUserProfile = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      res.status(400).json({ error: '缺少用户ID参数' });
      return;
    }
    
    const success = accessibilityFramework.deleteUserProfile(userId);
    
    if (!success) {
      res.status(404).json({ error: '未找到用户无障碍配置' });
      return;
    }
    
    res.status(200).json({ success: true });
  } catch (error) {
    logger.error('删除用户无障碍配置失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 获取屏幕阅读器设置
 */
export const getScreenReaderSettings = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      res.status(400).json({ error: '缺少用户ID参数' });
      return;
    }
    
    const settings = screenReader.getUserSettings(userId);
    
    res.status(200).json({ settings });
  } catch (error) {
    logger.error('获取屏幕阅读器设置失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 更新屏幕阅读器设置
 */
export const updateScreenReaderSettings = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const settings = req.body;
    
    if (!userId) {
      res.status(400).json({ error: '缺少用户ID参数' });
      return;
    }
    
    if (!settings) {
      res.status(400).json({ error: '缺少设置数据' });
      return;
    }
    
    const updatedSettings = screenReader.updateUserSettings(userId, settings);
    
    // 同步更新用户无障碍配置
    if (accessibilityFramework.getUserProfile(userId)) {
      accessibilityFramework.createOrUpdateUserProfile(userId, {
        screenReaderSettings: updatedSettings
      });
    }
    
    res.status(200).json({ settings: updatedSettings });
  } catch (error) {
    logger.error('更新屏幕阅读器设置失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 朗读文本
 */
export const readText = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const { text, priority } = req.body;
    
    if (!userId) {
      res.status(400).json({ error: '缺少用户ID参数' });
      return;
    }
    
    if (!text) {
      res.status(400).json({ error: '缺少文本内容' });
      return;
    }
    
    const request = await screenReader.readText(text, userId, priority || 5);
    
    if (!request) {
      res.status(400).json({ error: '屏幕阅读器未启用或朗读失败' });
      return;
    }
    
    res.status(200).json({ request });
  } catch (error) {
    logger.error('朗读文本失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 停止朗读
 */
export const stopReading = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      res.status(400).json({ error: '缺少用户ID参数' });
      return;
    }
    
    screenReader.stopReading(userId);
    
    res.status(200).json({ success: true });
  } catch (error) {
    logger.error('停止朗读失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 获取导航设置
 */
export const getNavigationSettings = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      res.status(400).json({ error: '缺少用户ID参数' });
      return;
    }
    
    const settings = voiceNavigation.getUserNavigationSettings(userId);
    
    res.status(200).json({ settings });
  } catch (error) {
    logger.error('获取导航设置失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 更新导航设置
 */
export const updateNavigationSettings = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const settings = req.body;
    
    if (!userId) {
      res.status(400).json({ error: '缺少用户ID参数' });
      return;
    }
    
    if (!settings) {
      res.status(400).json({ error: '缺少设置数据' });
      return;
    }
    
    const updatedSettings = voiceNavigation.updateUserNavigationSettings(userId, settings);
    
    // 同步更新用户无障碍配置
    if (accessibilityFramework.getUserProfile(userId)) {
      accessibilityFramework.createOrUpdateUserProfile(userId, {
        navigationSettings: updatedSettings
      });
    }
    
    res.status(200).json({ settings: updatedSettings });
  } catch (error) {
    logger.error('更新导航设置失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 开始导航
 */
export const startNavigation = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const { destination, startLocation } = req.body;
    
    if (!userId) {
      res.status(400).json({ error: '缺少用户ID参数' });
      return;
    }
    
    if (!destination || !destination.latitude || !destination.longitude) {
      res.status(400).json({ error: '目的地坐标不完整' });
      return;
    }
    
    const session = voiceNavigation.startNavigation(userId, destination, startLocation);
    
    res.status(200).json({ session });
  } catch (error) {
    logger.error('开始导航失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 结束导航
 */
export const endNavigation = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const { reason } = req.body;
    
    if (!userId) {
      res.status(400).json({ error: '缺少用户ID参数' });
      return;
    }
    
    const session = voiceNavigation.endNavigation(userId, reason);
    
    if (!session) {
      res.status(404).json({ error: '未找到活动的导航会话' });
      return;
    }
    
    res.status(200).json({ session });
  } catch (error) {
    logger.error('结束导航失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 更新用户位置
 */
export const updateUserLocation = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const { location } = req.body;
    
    if (!userId) {
      res.status(400).json({ error: '缺少用户ID参数' });
      return;
    }
    
    if (!location || !location.latitude || !location.longitude) {
      res.status(400).json({ error: '位置坐标不完整' });
      return;
    }
    
    const session = voiceNavigation.updateUserLocation(userId, location);
    
    if (!session) {
      res.status(404).json({ error: '未找到活动的导航会话或导航未启用' });
      return;
    }
    
    res.status(200).json({ session });
  } catch (error) {
    logger.error('更新用户位置失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 获取兴趣点
 */
export const getPointsOfInterest = async (req: Request, res: Response): Promise<void> => {
  try {
    const query = req.query;
    const searchParams: any = {};
    
    if (query.name) searchParams.name = query.name;
    if (query.category) searchParams.category = query.category;
    
    if (query.tags) {
      searchParams.tags = Array.isArray(query.tags) 
        ? query.tags 
        : [query.tags];
    }
    
    if (query.accessibilityFeatures) {
      searchParams.accessibilityFeatures = Array.isArray(query.accessibilityFeatures) 
        ? query.accessibilityFeatures 
        : [query.accessibilityFeatures];
    }
    
    if (query.latitude && query.longitude && query.radius) {
      searchParams.nearLocation = {
        latitude: parseFloat(query.latitude as string),
        longitude: parseFloat(query.longitude as string),
        radiusMeters: parseFloat(query.radius as string)
      };
    }
    
    const results = voiceNavigation.searchPointsOfInterest(searchParams);
    
    res.status(200).json({ results });
  } catch (error) {
    logger.error('获取兴趣点失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 注册UI元素
 */
export const registerUIElement = async (req: Request, res: Response): Promise<void> => {
  try {
    const element = req.body;
    
    if (!element || !element.elementId || !element.elementType) {
      res.status(400).json({ error: '元素数据不完整' });
      return;
    }
    
    // 确保元素有ID
    element.elementId = element.elementId || uuidv4();
    
    screenReader.registerUIElement(element);
    
    res.status(200).json({ elementId: element.elementId });
  } catch (error) {
    logger.error('注册UI元素失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 批量注册UI元素
 */
export const registerUIElements = async (req: Request, res: Response): Promise<void> => {
  try {
    const { elements } = req.body;
    
    if (!elements || !Array.isArray(elements) || elements.length === 0) {
      res.status(400).json({ error: '元素数据不完整或格式错误' });
      return;
    }
    
    // 确保所有元素都有ID
    const processedElements = elements.map(element => ({
      ...element,
      elementId: element.elementId || uuidv4()
    }));
    
    screenReader.registerUIElements(processedElements);
    
    res.status(200).json({ 
      count: processedElements.length,
      elementIds: processedElements.map(el => el.elementId)
    });
  } catch (error) {
    logger.error('批量注册UI元素失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 创建辅助语音提示
 */
export const createAccessibilityAnnouncement = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const { message, priority } = req.body;
    
    if (!userId) {
      res.status(400).json({ error: '缺少用户ID参数' });
      return;
    }
    
    if (!message) {
      res.status(400).json({ error: '缺少提示消息' });
      return;
    }
    
    const success = await accessibilityFramework.createAccessibilityAnnouncement(
      userId, 
      message, 
      priority || 3
    );
    
    if (!success) {
      res.status(400).json({ error: '创建提示失败或用户屏幕阅读功能未启用' });
      return;
    }
    
    res.status(200).json({ success: true });
  } catch (error) {
    logger.error('创建辅助语音提示失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};

/**
 * 初始化示例数据
 */
export const initSampleData = async (req: Request, res: Response): Promise<void> => {
  try {
    // 初始化示例用户配置
    accessibilityFramework.initSampleUserProfiles();
    
    // 初始化示例兴趣点
    voiceNavigation.initSamplePointsOfInterest();
    
    res.status(200).json({ 
      success: true,
      message: '已初始化无障碍功能示例数据'
    });
  } catch (error) {
    logger.error('初始化示例数据失败:', error);
    res.status(500).json({ error: '服务器内部错误' });
  }
};
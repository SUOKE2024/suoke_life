import { v4 as uuidv4 } from 'uuid';
import { logger } from '../../utils/logger';

// 视频数据类型
export interface VideoData {
  id: string;
  userId: string;
  timestamp: string;
  duration: number;
  format: string;
  resolution: string;
  frameRate: number;
  fileSize: number;
  videoUrl?: string;
  thumbnailUrl?: string;
  hasAudio: boolean;
  context?: {
    sessionId?: string;
    location?: string;
    deviceInfo?: string;
    feature?: string;
  };
  metadata?: Record<string, any>;
  analysis?: {
    objects?: string[];
    actions?: string[];
    facesDetected?: number;
    blurScore?: number;
  };
}

// 隐私设置类型
export interface PrivacySettings {
  allowVideoCapture: boolean;
  allowFaceDetection: boolean;
  allowObjectDetection: boolean;
  allowAnalytics: boolean;
  retentionPeriod: number; // 天数
  allowPII: boolean; // 是否允许保留个人身份信息
  blurFaces: boolean; // 是否模糊面部
}

// 视频存储
const videoStore: VideoData[] = [];
const privacySettingsStore: Record<string, PrivacySettings> = {};

// 默认隐私设置
const defaultPrivacySettings: PrivacySettings = {
  allowVideoCapture: false,
  allowFaceDetection: false,
  allowObjectDetection: false,
  allowAnalytics: false,
  retentionPeriod: 7, // 默认存储7天
  allowPII: false,
  blurFaces: true,
};

/**
 * 获取用户隐私设置
 */
export const getUserPrivacySettings = (userId: string): PrivacySettings => {
  return privacySettingsStore[userId] || defaultPrivacySettings;
};

/**
 * 更新用户隐私设置
 */
export const updateUserPrivacySettings = (userId: string, settings: Partial<PrivacySettings>): PrivacySettings => {
  const currentSettings = getUserPrivacySettings(userId);
  const updatedSettings = { ...currentSettings, ...settings };
  privacySettingsStore[userId] = updatedSettings;
  
  logger.info(`用户视频隐私设置已更新: ${userId}`);
  return updatedSettings;
};

/**
 * 捕获视频数据
 */
export const captureVideo = async (data: Omit<VideoData, 'id' | 'timestamp'>): Promise<VideoData | null> => {
  try {
    const { userId } = data;
    const settings = getUserPrivacySettings(userId);
    
    // 检查隐私设置
    if (!settings.allowVideoCapture) {
      logger.info(`视频捕获已被用户设置禁止: ${userId}`);
      return null;
    }
    
    const videoData: VideoData = {
      ...data,
      id: uuidv4(),
      timestamp: new Date().toISOString(),
    };
    
    // 处理PII（个人身份信息）
    if (!settings.allowPII) {
      // 移除可能包含PII的内容
      delete videoData.context?.location;
      if (videoData.metadata) {
        delete videoData.metadata.personalInfo;
        delete videoData.metadata.contactInfo;
      }
    }
    
    // 处理面部检测选项
    if (videoData.analysis && !settings.allowFaceDetection) {
      delete videoData.analysis.facesDetected;
    }
    
    // 处理物体检测选项
    if (videoData.analysis && !settings.allowObjectDetection) {
      delete videoData.analysis.objects;
      delete videoData.analysis.actions;
    }
    
    // 存储视频数据
    videoStore.push(videoData);
    
    // 设置自动删除（基于保留期限）
    scheduleDataDeletion(videoData.id, settings.retentionPeriod);
    
    logger.info(`视频数据已捕获: ${videoData.id}`);
    return videoData;
  } catch (error) {
    logger.error('视频捕获失败:', error);
    throw new Error(`视频捕获失败: ${(error as Error).message}`);
  }
};

/**
 * 获取用户的视频数据历史
 */
export const getUserVideoHistory = (userId: string, limit: number = 20): VideoData[] => {
  const settings = getUserPrivacySettings(userId);
  
  if (!settings.allowVideoCapture) {
    return [];
  }
  
  const userVideos = videoStore
    .filter(video => video.userId === userId)
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, limit);
  
  // 如果不允许分析，则过滤掉一些属性
  if (!settings.allowAnalytics) {
    return userVideos.map(video => {
      const { analysis, context, metadata, ...safeData } = video;
      return safeData;
    });
  }
  
  return userVideos;
};

/**
 * 按ID获取单个视频数据
 */
export const getVideoById = (videoId: string, userId: string): VideoData | null => {
  const video = videoStore.find(v => v.id === videoId);
  
  if (!video || video.userId !== userId) {
    return null;
  }
  
  const settings = getUserPrivacySettings(userId);
  
  // 检查隐私设置
  if (!settings.allowVideoCapture) {
    return null;
  }
  
  // 如果不允许分析，则过滤掉一些属性
  if (!settings.allowAnalytics) {
    const { analysis, context, metadata, ...safeData } = video;
    return safeData;
  }
  
  return video;
};

/**
 * 删除视频数据
 */
export const deleteVideo = (videoId: string, userId: string): boolean => {
  const index = videoStore.findIndex(v => v.id === videoId && v.userId === userId);
  
  if (index === -1) {
    return false;
  }
  
  videoStore.splice(index, 1);
  logger.info(`视频数据已删除: ${videoId}`);
  return true;
};

/**
 * 计划数据自动删除
 */
const scheduleDataDeletion = (videoId: string, retentionPeriod: number): void => {
  const msPerDay = 24 * 60 * 60 * 1000;
  const deleteTime = retentionPeriod * msPerDay;
  
  setTimeout(() => {
    const index = videoStore.findIndex(v => v.id === videoId);
    if (index !== -1) {
      videoStore.splice(index, 1);
      logger.info(`视频数据已自动删除(保留期到期): ${videoId}`);
    }
  }, deleteTime);
};

/**
 * 添加视频分析结果
 */
export const addVideoAnalysis = async (videoId: string, analysis: VideoData['analysis']): Promise<VideoData | null> => {
  const index = videoStore.findIndex(v => v.id === videoId);
  
  if (index === -1) {
    return null;
  }
  
  const video = videoStore[index];
  const settings = getUserPrivacySettings(video.userId);
  
  // 处理面部检测选项
  if (analysis && !settings.allowFaceDetection) {
    delete analysis.facesDetected;
  }
  
  // 处理物体检测选项
  if (analysis && !settings.allowObjectDetection) {
    delete analysis.objects;
    delete analysis.actions;
  }
  
  // 更新分析结果
  videoStore[index] = {
    ...video,
    analysis: {
      ...video.analysis,
      ...analysis
    }
  };
  
  logger.info(`视频分析已添加: ${videoId}`);
  return videoStore[index];
};
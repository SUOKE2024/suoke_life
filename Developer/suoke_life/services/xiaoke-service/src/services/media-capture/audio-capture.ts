import { v4 as uuidv4 } from 'uuid';
import { logger } from '../../utils/logger';

// 音频数据类型
export interface AudioData {
  id: string;
  userId: string;
  timestamp: string;
  duration: number;
  format: string;
  sampleRate: number;
  channels: number;
  fileSize: number;
  audioUrl?: string;
  transcription?: string;
  context?: {
    sessionId?: string;
    location?: string;
    deviceInfo?: string;
    feature?: string;
  };
  metadata?: Record<string, any>;
}

// 隐私设置类型
export interface PrivacySettings {
  allowAudioCapture: boolean;
  allowTranscription: boolean;
  allowAnalytics: boolean;
  retentionPeriod: number; // 天数
  allowPII: boolean; // 是否允许保留个人身份信息
}

// 音频存储
const audioStore: AudioData[] = [];
const privacySettingsStore: Record<string, PrivacySettings> = {};

// 默认隐私设置
const defaultPrivacySettings: PrivacySettings = {
  allowAudioCapture: false,
  allowTranscription: false,
  allowAnalytics: false,
  retentionPeriod: 30,
  allowPII: false,
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
  
  logger.info(`用户隐私设置已更新: ${userId}`);
  return updatedSettings;
};

/**
 * 捕获音频数据
 */
export const captureAudio = async (data: Omit<AudioData, 'id' | 'timestamp'>): Promise<AudioData | null> => {
  try {
    const { userId } = data;
    const settings = getUserPrivacySettings(userId);
    
    // 检查隐私设置
    if (!settings.allowAudioCapture) {
      logger.info(`音频捕获已被用户设置禁止: ${userId}`);
      return null;
    }
    
    const audioData: AudioData = {
      ...data,
      id: uuidv4(),
      timestamp: new Date().toISOString(),
    };
    
    // 处理PII（个人身份信息）
    if (!settings.allowPII) {
      // 移除可能包含PII的内容
      delete audioData.context?.location;
      if (audioData.metadata) {
        delete audioData.metadata.personalInfo;
        delete audioData.metadata.contactInfo;
      }
    }
    
    // 存储音频数据
    audioStore.push(audioData);
    
    // 设置自动删除（基于保留期限）
    scheduleDataDeletion(audioData.id, settings.retentionPeriod);
    
    logger.info(`音频数据已捕获: ${audioData.id}`);
    return audioData;
  } catch (error) {
    logger.error('音频捕获失败:', error);
    throw new Error(`音频捕获失败: ${(error as Error).message}`);
  }
};

/**
 * 获取用户的音频数据历史
 */
export const getUserAudioHistory = (userId: string, limit: number = 20): AudioData[] => {
  const settings = getUserPrivacySettings(userId);
  
  if (!settings.allowAudioCapture) {
    return [];
  }
  
  const userAudio = audioStore
    .filter(audio => audio.userId === userId)
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, limit);
  
  // 如果不允许分析，则过滤掉一些属性
  if (!settings.allowAnalytics) {
    return userAudio.map(audio => {
      const { transcription, context, metadata, ...safeData } = audio;
      return safeData;
    });
  }
  
  return userAudio;
};

/**
 * 按ID获取单个音频数据
 */
export const getAudioById = (audioId: string, userId: string): AudioData | null => {
  const audio = audioStore.find(a => a.id === audioId);
  
  if (!audio || audio.userId !== userId) {
    return null;
  }
  
  const settings = getUserPrivacySettings(userId);
  
  // 检查隐私设置
  if (!settings.allowAudioCapture) {
    return null;
  }
  
  // 如果不允许分析，则过滤掉一些属性
  if (!settings.allowAnalytics) {
    const { transcription, context, metadata, ...safeData } = audio;
    return safeData;
  }
  
  return audio;
};

/**
 * 删除音频数据
 */
export const deleteAudio = (audioId: string, userId: string): boolean => {
  const index = audioStore.findIndex(a => a.id === audioId && a.userId === userId);
  
  if (index === -1) {
    return false;
  }
  
  audioStore.splice(index, 1);
  logger.info(`音频数据已删除: ${audioId}`);
  return true;
};

/**
 * 计划数据自动删除
 */
const scheduleDataDeletion = (audioId: string, retentionPeriod: number): void => {
  const msPerDay = 24 * 60 * 60 * 1000;
  const deleteTime = retentionPeriod * msPerDay;
  
  setTimeout(() => {
    const index = audioStore.findIndex(a => a.id === audioId);
    if (index !== -1) {
      audioStore.splice(index, 1);
      logger.info(`音频数据已自动删除(保留期到期): ${audioId}`);
    }
  }, deleteTime);
};

/**
 * 添加音频转录
 */
export const addTranscription = async (audioId: string, transcription: string): Promise<AudioData | null> => {
  const index = audioStore.findIndex(a => a.id === audioId);
  
  if (index === -1) {
    return null;
  }
  
  const audio = audioStore[index];
  const settings = getUserPrivacySettings(audio.userId);
  
  // 检查隐私设置
  if (!settings.allowTranscription) {
    logger.info(`音频转录被用户设置禁止: ${audio.userId}`);
    return null;
  }
  
  // 更新转录
  audioStore[index] = {
    ...audio,
    transcription
  };
  
  logger.info(`音频转录已添加: ${audioId}`);
  return audioStore[index];
};
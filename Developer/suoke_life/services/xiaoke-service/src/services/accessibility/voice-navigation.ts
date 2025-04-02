import { v4 as uuidv4 } from 'uuid';
import { logger } from '../../utils/logger';
import { synthesizeDialectSpeech } from '../dialect/dialect-synthesis';
import { ChineseDialect } from '../dialect/dialect-recognition';
import { readText } from './screen-reader';

// 导航指令类型
export enum NavigationInstructionType {
  DIRECTION = 'direction',
  LOCATION = 'location',
  ACTION = 'action',
  CONFIRMATION = 'confirmation',
  WARNING = 'warning',
  INFORMATION = 'information'
}

// 导航指令
export interface NavigationInstruction {
  id: string;
  type: NavigationInstructionType;
  text: string;
  priority: number;
  timestamp: string;
  location?: {
    latitude?: number;
    longitude?: number;
    altitude?: number;
    accuracy?: number;
    floor?: number;
    buildingId?: string;
    roomId?: string;
  };
  context?: {
    previousInstruction?: string;
    nextExpectedAction?: string;
    landmark?: string;
    distanceToTarget?: number;
    targetName?: string;
    alternateRoutes?: boolean;
  };
  metadata?: Record<string, any>;
}

// 导航设置
export interface VoiceNavigationSettings {
  enabled: boolean;
  navigationVolume: number; // 音量，0.0-1.0
  navigationSpeed: number; // 语速，0.5-2.0
  dialect: ChineseDialect; // 使用的方言
  voiceId?: string; // 发音人ID
  distanceUnit: 'meters' | 'feet'; // 距离单位
  verbosityLevel: 'low' | 'medium' | 'high'; // 详细程度
  autoAnnouncePoints: boolean; // 自动播报兴趣点
  autoAnnounceObstacles: boolean; // 自动播报障碍物
  vibrateOnInstructions: boolean; // 导航指令时震动
  useBinauralAudio: boolean; // 使用双耳音效来表示方向
  repeatInstructionsInterval: number; // 重复指令的间隔（秒），0表示不重复
}

// 导航状态
export enum NavigationStatus {
  IDLE = 'idle',
  ACTIVE = 'active',
  PAUSED = 'paused',
  REROUTING = 'rerouting',
  COMPLETED = 'completed',
  ERROR = 'error'
}

// 导航会话
export interface NavigationSession {
  id: string;
  userId: string;
  startTime: string;
  endTime?: string;
  startLocation?: {
    latitude: number;
    longitude: number;
  };
  destination?: {
    latitude: number;
    longitude: number;
    name?: string;
  };
  currentLocation?: {
    latitude: number;
    longitude: number;
    timestamp: string;
  };
  status: NavigationStatus;
  instructions: NavigationInstruction[];
  settings: VoiceNavigationSettings;
  metadata?: Record<string, any>;
}

// 兴趣点
export interface PointOfInterest {
  id: string;
  name: string;
  category: string;
  subcategory?: string;
  description?: string;
  location: {
    latitude: number;
    longitude: number;
    altitude?: number;
    floor?: number;
    buildingId?: string;
    roomId?: string;
  };
  importance: number; // 1-10, 10为最重要
  tags?: string[];
  accessibilityFeatures?: string[];
  metadata?: Record<string, any>;
}

// 用户导航设置存储
const userSettingsStore: Record<string, VoiceNavigationSettings> = {};

// 活动导航会话
const activeSessions: Record<string, NavigationSession> = {};

// 兴趣点数据库
const pointsOfInterestDB: PointOfInterest[] = [];

// 默认导航设置
const defaultSettings: VoiceNavigationSettings = {
  enabled: false,
  navigationVolume: 1.0,
  navigationSpeed: 1.0,
  dialect: ChineseDialect.MANDARIN,
  distanceUnit: 'meters',
  verbosityLevel: 'medium',
  autoAnnouncePoints: true,
  autoAnnounceObstacles: true,
  vibrateOnInstructions: true,
  useBinauralAudio: true,
  repeatInstructionsInterval: 0
};

/**
 * 获取用户导航设置
 */
export const getUserNavigationSettings = (userId: string): VoiceNavigationSettings => {
  return userSettingsStore[userId] || defaultSettings;
};

/**
 * 更新用户导航设置
 */
export const updateUserNavigationSettings = (userId: string, settings: Partial<VoiceNavigationSettings>): VoiceNavigationSettings => {
  const currentSettings = getUserNavigationSettings(userId);
  const updatedSettings = { ...currentSettings, ...settings };
  userSettingsStore[userId] = updatedSettings;
  
  logger.info(`用户导航设置已更新: ${userId}`);
  return updatedSettings;
};

/**
 * 开始导航会话
 */
export const startNavigation = (
  userId: string, 
  destination: { latitude: number; longitude: number; name?: string },
  startLocation?: { latitude: number; longitude: number }
): NavigationSession => {
  // 检查是否有未结束的会话
  if (activeSessions[userId] && [NavigationStatus.ACTIVE, NavigationStatus.PAUSED, NavigationStatus.REROUTING].includes(activeSessions[userId].status)) {
    endNavigation(userId, 'new_navigation_started');
  }
  
  const settings = getUserNavigationSettings(userId);
  const session: NavigationSession = {
    id: uuidv4(),
    userId,
    startTime: new Date().toISOString(),
    startLocation,
    destination,
    status: NavigationStatus.ACTIVE,
    instructions: [],
    settings
  };
  
  activeSessions[userId] = session;
  logger.info(`开始导航会话: ${session.id}, 用户: ${userId}, 目的地: ${destination.name || '未命名位置'}`);
  
  // 添加首条导航指令
  const firstInstruction: NavigationInstruction = {
    id: uuidv4(),
    type: NavigationInstructionType.INFORMATION,
    text: `开始导航${destination.name ? `到${destination.name}` : ''}。请沿当前道路直行。`,
    priority: 1,
    timestamp: new Date().toISOString(),
    context: {
      targetName: destination.name
    }
  };
  
  addNavigationInstruction(userId, firstInstruction);
  
  return session;
};

/**
 * 结束导航会话
 */
export const endNavigation = (userId: string, reason?: string): NavigationSession | null => {
  const session = activeSessions[userId];
  if (!session) {
    logger.warn(`尝试结束不存在的导航会话, 用户: ${userId}`);
    return null;
  }
  
  session.endTime = new Date().toISOString();
  session.status = NavigationStatus.COMPLETED;
  
  const endInstruction: NavigationInstruction = {
    id: uuidv4(),
    type: NavigationInstructionType.CONFIRMATION,
    text: '导航已结束。',
    priority: 1,
    timestamp: new Date().toISOString(),
    metadata: { endReason: reason }
  };
  
  addNavigationInstruction(userId, endInstruction);
  
  logger.info(`结束导航会话: ${session.id}, 用户: ${userId}, 原因: ${reason || '用户请求'}`);
  
  // 立即朗读导航结束信息
  readText(endInstruction.text, userId, 1);
  
  // 将会话移除活动会话列表（但保留完整记录以备查询）
  delete activeSessions[userId];
  
  return session;
};

/**
 * 暂停导航
 */
export const pauseNavigation = (userId: string): NavigationSession | null => {
  const session = activeSessions[userId];
  if (!session || session.status !== NavigationStatus.ACTIVE) {
    logger.warn(`尝试暂停非活动导航会话, 用户: ${userId}`);
    return null;
  }
  
  session.status = NavigationStatus.PAUSED;
  
  const pauseInstruction: NavigationInstruction = {
    id: uuidv4(),
    type: NavigationInstructionType.INFORMATION,
    text: '导航已暂停。',
    priority: 2,
    timestamp: new Date().toISOString()
  };
  
  addNavigationInstruction(userId, pauseInstruction);
  logger.info(`暂停导航会话: ${session.id}, 用户: ${userId}`);
  
  return session;
};

/**
 * 恢复导航
 */
export const resumeNavigation = (userId: string): NavigationSession | null => {
  const session = activeSessions[userId];
  if (!session || session.status !== NavigationStatus.PAUSED) {
    logger.warn(`尝试恢复非暂停导航会话, 用户: ${userId}`);
    return null;
  }
  
  session.status = NavigationStatus.ACTIVE;
  
  const resumeInstruction: NavigationInstruction = {
    id: uuidv4(),
    type: NavigationInstructionType.INFORMATION,
    text: '导航已恢复。请继续沿当前路线行进。',
    priority: 2,
    timestamp: new Date().toISOString()
  };
  
  addNavigationInstruction(userId, resumeInstruction);
  logger.info(`恢复导航会话: ${session.id}, 用户: ${userId}`);
  
  return session;
};

/**
 * 添加导航指令
 */
export const addNavigationInstruction = (userId: string, instruction: Omit<NavigationInstruction, 'id' | 'timestamp'>): NavigationInstruction | null => {
  const session = activeSessions[userId];
  if (!session) {
    logger.warn(`尝试添加导航指令到不存在的会话, 用户: ${userId}`);
    return null;
  }
  
  const fullInstruction: NavigationInstruction = {
    ...instruction,
    id: instruction.id || uuidv4(),
    timestamp: instruction.timestamp || new Date().toISOString()
  };
  
  session.instructions.push(fullInstruction);
  
  // 朗读导航指令
  const { enabled, navigationSpeed, navigationVolume, dialect, voiceId } = session.settings;
  
  if (enabled) {
    readText(fullInstruction.text, userId, fullInstruction.priority);
    
    // 如果设置了震动反馈
    if (session.settings.vibrateOnInstructions) {
      // 这里可以触发设备震动，但需要客户端支持
      logger.debug(`应触发设备震动，用户: ${userId}`);
    }
  }
  
  logger.debug(`添加导航指令: ${fullInstruction.id}, 类型: ${fullInstruction.type}, 文本: "${fullInstruction.text}"`);
  return fullInstruction;
};

/**
 * 更新用户当前位置
 */
export const updateUserLocation = (
  userId: string, 
  location: { latitude: number; longitude: number; timestamp?: string }
): NavigationSession | null => {
  const session = activeSessions[userId];
  if (!session || session.status !== NavigationStatus.ACTIVE) {
    return null;
  }
  
  session.currentLocation = {
    ...location,
    timestamp: location.timestamp || new Date().toISOString()
  };
  
  // 检查是否到达目的地
  if (session.destination && isNearDestination(location, session.destination)) {
    return endNavigation(userId, 'arrived_at_destination');
  }
  
  // 检查是否经过兴趣点
  if (session.settings.autoAnnouncePoints) {
    const nearbyPOIs = findNearbyPointsOfInterest(location, 50); // 50米范围内
    
    for (const poi of nearbyPOIs) {
      // 判断是否已经播报过该兴趣点
      const alreadyAnnounced = session.instructions.some(
        inst => inst.metadata?.poiId === poi.id && 
        new Date(inst.timestamp).getTime() > Date.now() - 5 * 60 * 1000 // 5分钟内
      );
      
      if (!alreadyAnnounced) {
        const poiInstruction: NavigationInstruction = {
          id: uuidv4(),
          type: NavigationInstructionType.INFORMATION,
          text: `您的${getDirectionText(location, poi.location)}方向${getDistanceText(location, poi.location, session.settings.distanceUnit)}处有${poi.name}${poi.description ? `，${poi.description}` : ''}`,
          priority: 3,
          timestamp: new Date().toISOString(),
          location: poi.location,
          metadata: { poiId: poi.id, poiCategory: poi.category }
        };
        
        addNavigationInstruction(userId, poiInstruction);
      }
    }
  }
  
  return session;
};

/**
 * 判断是否接近目的地
 */
const isNearDestination = (
  currentLocation: { latitude: number; longitude: number },
  destination: { latitude: number; longitude: number }
): boolean => {
  const distance = calculateDistance(currentLocation, destination);
  return distance < 20; // 20米以内视为到达目的地
};

/**
 * 计算两点之间的距离（米）
 */
const calculateDistance = (
  point1: { latitude: number; longitude: number },
  point2: { latitude: number; longitude: number }
): number => {
  const R = 6371e3; // 地球半径（米）
  const φ1 = (point1.latitude * Math.PI) / 180;
  const φ2 = (point2.latitude * Math.PI) / 180;
  const Δφ = ((point2.latitude - point1.latitude) * Math.PI) / 180;
  const Δλ = ((point2.longitude - point1.longitude) * Math.PI) / 180;
  
  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  
  return R * c;
};

/**
 * 查找附近的兴趣点
 */
const findNearbyPointsOfInterest = (
  location: { latitude: number; longitude: number },
  radiusMeters: number
): PointOfInterest[] => {
  return pointsOfInterestDB.filter(poi => {
    const distance = calculateDistance(location, poi.location);
    return distance <= radiusMeters;
  }).sort((a, b) => a.importance - b.importance);
};

/**
 * 获取方向文本
 */
const getDirectionText = (
  from: { latitude: number; longitude: number },
  to: { latitude: number; longitude: number }
): string => {
  const bearing = calculateBearing(from, to);
  
  if (bearing >= 337.5 || bearing < 22.5) return '正前';
  if (bearing >= 22.5 && bearing < 67.5) return '右前';
  if (bearing >= 67.5 && bearing < 112.5) return '右侧';
  if (bearing >= 112.5 && bearing < 157.5) return '右后';
  if (bearing >= 157.5 && bearing < 202.5) return '正后';
  if (bearing >= 202.5 && bearing < 247.5) return '左后';
  if (bearing >= 247.5 && bearing < 292.5) return '左侧';
  return '左前';
};

/**
 * 计算方位角
 */
const calculateBearing = (
  from: { latitude: number; longitude: number },
  to: { latitude: number; longitude: number }
): number => {
  const φ1 = (from.latitude * Math.PI) / 180;
  const φ2 = (to.latitude * Math.PI) / 180;
  const λ1 = (from.longitude * Math.PI) / 180;
  const λ2 = (to.longitude * Math.PI) / 180;
  
  const y = Math.sin(λ2 - λ1) * Math.cos(φ2);
  const x = Math.cos(φ1) * Math.sin(φ2) -
            Math.sin(φ1) * Math.cos(φ2) * Math.cos(λ2 - λ1);
  
  const θ = Math.atan2(y, x);
  const bearing = (θ * 180 / Math.PI + 360) % 360;
  
  return bearing;
};

/**
 * 获取距离文本
 */
const getDistanceText = (
  from: { latitude: number; longitude: number },
  to: { latitude: number; longitude: number },
  unit: 'meters' | 'feet'
): string => {
  const distanceMeters = calculateDistance(from, to);
  
  if (unit === 'feet') {
    const distanceFeet = distanceMeters * 3.28084;
    if (distanceFeet < 10) return '很近';
    if (distanceFeet < 100) return `${Math.round(distanceFeet / 10) * 10}英尺`;
    if (distanceFeet < 1000) return `${Math.round(distanceFeet / 100) * 100}英尺`;
    return `${(distanceFeet / 5280).toFixed(1)}英里`;
  } else {
    if (distanceMeters < 10) return '很近';
    if (distanceMeters < 100) return `${Math.round(distanceMeters / 10) * 10}米`;
    if (distanceMeters < 1000) return `${Math.round(distanceMeters / 100) * 100}米`;
    return `${(distanceMeters / 1000).toFixed(1)}公里`;
  }
};

/**
 * 获取活动导航会话
 */
export const getActiveNavigationSession = (userId: string): NavigationSession | null => {
  return activeSessions[userId] || null;
};

/**
 * 重复播报当前导航指令
 */
export const repeatLastInstruction = (userId: string): NavigationInstruction | null => {
  const session = activeSessions[userId];
  if (!session || session.instructions.length === 0) {
    return null;
  }
  
  // 找到最近的非信息类指令
  const lastActionInstruction = [...session.instructions]
    .reverse()
    .find(inst => inst.type !== NavigationInstructionType.INFORMATION);
  
  if (lastActionInstruction) {
    // 创建重复指令
    const repeatInstruction: NavigationInstruction = {
      id: uuidv4(),
      type: lastActionInstruction.type,
      text: `重复：${lastActionInstruction.text}`,
      priority: lastActionInstruction.priority,
      timestamp: new Date().toISOString(),
      location: lastActionInstruction.location,
      context: lastActionInstruction.context,
      metadata: { 
        ...lastActionInstruction.metadata,
        isRepeat: true,
        originalInstructionId: lastActionInstruction.id
      }
    };
    
    addNavigationInstruction(userId, repeatInstruction);
    return repeatInstruction;
  }
  
  return null;
};

/**
 * 添加兴趣点
 */
export const addPointOfInterest = (poi: Omit<PointOfInterest, 'id'>): PointOfInterest => {
  const newPoi: PointOfInterest = {
    ...poi,
    id: uuidv4()
  };
  
  pointsOfInterestDB.push(newPoi);
  logger.info(`新增兴趣点: ${newPoi.id}, 名称: ${newPoi.name}, 类别: ${newPoi.category}`);
  
  return newPoi;
};

/**
 * 获取兴趣点
 */
export const getPointOfInterest = (id: string): PointOfInterest | null => {
  return pointsOfInterestDB.find(poi => poi.id === id) || null;
};

/**
 * 更新兴趣点
 */
export const updatePointOfInterest = (id: string, updates: Partial<PointOfInterest>): PointOfInterest | null => {
  const index = pointsOfInterestDB.findIndex(poi => poi.id === id);
  if (index === -1) {
    return null;
  }
  
  const updatedPoi = { ...pointsOfInterestDB[index], ...updates };
  pointsOfInterestDB[index] = updatedPoi;
  
  logger.info(`更新兴趣点: ${id}, 名称: ${updatedPoi.name}`);
  return updatedPoi;
};

/**
 * 删除兴趣点
 */
export const deletePointOfInterest = (id: string): boolean => {
  const index = pointsOfInterestDB.findIndex(poi => poi.id === id);
  if (index === -1) {
    return false;
  }
  
  pointsOfInterestDB.splice(index, 1);
  logger.info(`删除兴趣点: ${id}`);
  
  return true;
};

/**
 * 搜索兴趣点
 */
export const searchPointsOfInterest = (query: {
  name?: string;
  category?: string;
  tags?: string[];
  accessibilityFeatures?: string[];
  nearLocation?: { latitude: number; longitude: number; radiusMeters: number };
}): PointOfInterest[] => {
  let results = [...pointsOfInterestDB];
  
  if (query.name) {
    const nameLower = query.name.toLowerCase();
    results = results.filter(poi => 
      poi.name.toLowerCase().includes(nameLower) || 
      (poi.description && poi.description.toLowerCase().includes(nameLower))
    );
  }
  
  if (query.category) {
    results = results.filter(poi => 
      poi.category === query.category || 
      poi.subcategory === query.category
    );
  }
  
  if (query.tags && query.tags.length > 0) {
    results = results.filter(poi => 
      poi.tags && query.tags!.some(tag => poi.tags!.includes(tag))
    );
  }
  
  if (query.accessibilityFeatures && query.accessibilityFeatures.length > 0) {
    results = results.filter(poi => 
      poi.accessibilityFeatures && 
      query.accessibilityFeatures!.some(feature => poi.accessibilityFeatures!.includes(feature))
    );
  }
  
  if (query.nearLocation) {
    results = results.filter(poi => {
      const distance = calculateDistance(query.nearLocation!, poi.location);
      return distance <= query.nearLocation!.radiusMeters;
    });
    
    // 按距离排序
    results.sort((a, b) => {
      const distanceA = calculateDistance(query.nearLocation!, a.location);
      const distanceB = calculateDistance(query.nearLocation!, b.location);
      return distanceA - distanceB;
    });
  } else {
    // 按重要性排序
    results.sort((a, b) => b.importance - a.importance);
  }
  
  return results;
};

/**
 * 初始化示例兴趣点数据
 */
export const initSamplePointsOfInterest = (): void => {
  // 示例兴趣点数据
  const samplePOIs: Omit<PointOfInterest, 'id'>[] = [
    {
      name: '无障碍卫生间',
      category: '设施',
      subcategory: '卫生间',
      description: '配备无障碍设施的卫生间，有扶手和宽敞空间',
      location: {
        latitude: 31.2304,
        longitude: 121.4737,
        floor: 1
      },
      importance: 8,
      tags: ['卫生间', '无障碍'],
      accessibilityFeatures: ['轮椅通道', '扶手']
    },
    {
      name: '电梯',
      category: '设施',
      subcategory: '垂直交通',
      description: '通往所有楼层的无障碍电梯',
      location: {
        latitude: 31.2305,
        longitude: 121.4738,
        floor: 1
      },
      importance: 9,
      tags: ['电梯', '无障碍'],
      accessibilityFeatures: ['轮椅通道', '语音提示', '盲文按钮']
    },
    {
      name: '休息区',
      category: '设施',
      subcategory: '休息',
      description: '舒适的休息座椅区域',
      location: {
        latitude: 31.2306,
        longitude: 121.4735,
        floor: 1
      },
      importance: 6,
      tags: ['座椅', '休息'],
      accessibilityFeatures: ['轮椅通道']
    },
    {
      name: '服务台',
      category: '服务',
      description: '提供帮助和信息的服务台',
      location: {
        latitude: 31.2303,
        longitude: 121.4736,
        floor: 1
      },
      importance: 10,
      tags: ['帮助', '信息'],
      accessibilityFeatures: ['手语服务', '助听设备']
    },
    {
      name: '无障碍入口',
      category: '设施',
      subcategory: '入口',
      description: '配备坡道的无障碍入口',
      location: {
        latitude: 31.2302,
        longitude: 121.4734,
        floor: 1
      },
      importance: 10,
      tags: ['入口', '无障碍'],
      accessibilityFeatures: ['轮椅通道', '自动门']
    }
  ];
  
  // 清空现有数据并添加示例数据
  pointsOfInterestDB.length = 0;
  
  for (const poiData of samplePOIs) {
    addPointOfInterest(poiData);
  }
  
  logger.info(`已初始化${samplePOIs.length}个示例兴趣点`);
};
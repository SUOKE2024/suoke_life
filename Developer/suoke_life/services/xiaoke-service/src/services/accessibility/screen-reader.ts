import { v4 as uuidv4 } from 'uuid';
import { logger } from '../../utils/logger';
import { synthesizeDialectSpeech } from '../dialect/dialect-synthesis';
import { ChineseDialect } from '../dialect/dialect-recognition';

// 界面元素描述
export interface UIElementDescription {
  elementId: string;
  elementType: string;
  text?: string;
  role?: string;
  state?: {
    disabled?: boolean;
    checked?: boolean;
    selected?: boolean;
    expanded?: boolean;
  };
  ariaLabel?: string;
  hint?: string;
  position?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  children?: string[]; // 子元素ID列表
  parentId?: string; // 父元素ID
  customDescription?: string; // 自定义描述文本
  priority?: number; // 朗读优先级，数字越小优先级越高
}

// 屏幕阅读设置
export interface ScreenReaderSettings {
  enabled: boolean;
  readingSpeed: number; // 语速，0.5-2.0
  readingVolume: number; // 音量，0.0-1.0
  verbosityLevel: 'low' | 'medium' | 'high'; // 详细程度
  autoReadOnFocus: boolean; // 自动朗读获得焦点的元素
  autoReadOnHover: boolean; // 自动朗读鼠标悬停的元素
  dialect: ChineseDialect; // 使用的方言
  voiceId?: string; // 发音人ID
  interruptOnAction: boolean; // 当用户执行操作时是否中断朗读
  useCustomDescriptions: boolean; // 是否使用自定义描述
}

// 朗读请求
export interface ReadingRequest {
  id: string;
  userId: string;
  timestamp: string;
  elementId?: string;
  text: string;
  priority: number;
  synthesisResult?: any; // 语音合成结果
  status: 'pending' | 'reading' | 'completed' | 'interrupted';
}

// 页面结构元素缓存
const uiElementsCache: Record<string, UIElementDescription> = {};

// 用户屏幕阅读设置
const userSettingsStore: Record<string, ScreenReaderSettings> = {};

// 朗读队列
const readingQueue: ReadingRequest[] = [];

// 默认设置
const defaultSettings: ScreenReaderSettings = {
  enabled: false,
  readingSpeed: 1.0,
  readingVolume: 1.0,
  verbosityLevel: 'medium',
  autoReadOnFocus: true,
  autoReadOnHover: false,
  dialect: ChineseDialect.MANDARIN,
  interruptOnAction: true,
  useCustomDescriptions: true
};

/**
 * 获取用户屏幕阅读设置
 */
export const getUserSettings = (userId: string): ScreenReaderSettings => {
  return userSettingsStore[userId] || defaultSettings;
};

/**
 * 更新用户屏幕阅读设置
 */
export const updateUserSettings = (userId: string, settings: Partial<ScreenReaderSettings>): ScreenReaderSettings => {
  const currentSettings = getUserSettings(userId);
  const updatedSettings = { ...currentSettings, ...settings };
  userSettingsStore[userId] = updatedSettings;
  
  logger.info(`用户屏幕阅读设置已更新: ${userId}`);
  return updatedSettings;
};

/**
 * 注册UI元素
 */
export const registerUIElement = (element: UIElementDescription): void => {
  uiElementsCache[element.elementId] = element;
  logger.debug(`已注册UI元素: ${element.elementId}, 类型: ${element.elementType}`);
};

/**
 * 批量注册UI元素
 */
export const registerUIElements = (elements: UIElementDescription[]): void => {
  elements.forEach(element => {
    uiElementsCache[element.elementId] = element;
  });
  logger.debug(`已批量注册UI元素: ${elements.length}个元素`);
};

/**
 * 更新UI元素
 */
export const updateUIElement = (elementId: string, updates: Partial<UIElementDescription>): UIElementDescription | null => {
  const element = uiElementsCache[elementId];
  if (!element) {
    logger.warn(`尝试更新不存在的UI元素: ${elementId}`);
    return null;
  }
  
  uiElementsCache[elementId] = { ...element, ...updates };
  logger.debug(`已更新UI元素: ${elementId}`);
  return uiElementsCache[elementId];
};

/**
 * 移除UI元素
 */
export const removeUIElement = (elementId: string): boolean => {
  if (!uiElementsCache[elementId]) {
    logger.warn(`尝试移除不存在的UI元素: ${elementId}`);
    return false;
  }
  
  delete uiElementsCache[elementId];
  logger.debug(`已移除UI元素: ${elementId}`);
  return true;
};

/**
 * 构建元素描述文本
 */
export const buildElementDescriptionText = (element: UIElementDescription, verbosityLevel: ScreenReaderSettings['verbosityLevel']): string => {
  if (element.customDescription) {
    return element.customDescription;
  }
  
  let description = '';
  
  // 添加元素角色/类型
  if (element.role) {
    description += `${element.role} `;
  } else if (element.elementType) {
    description += `${translateElementType(element.elementType)} `;
  }
  
  // 添加元素文本或标签
  if (element.text) {
    description += element.text;
  } else if (element.ariaLabel) {
    description += element.ariaLabel;
  }
  
  // 根据详细程度添加状态信息
  if (verbosityLevel === 'medium' || verbosityLevel === 'high') {
    if (element.state) {
      if (element.state.disabled) {
        description += ' 已禁用';
      }
      if (element.state.checked) {
        description += ' 已选中';
      }
      if (element.state.selected) {
        description += ' 已选择';
      }
      if (element.state.expanded) {
        description += ' 已展开';
      }
    }
  }
  
  // 高详细程度时添加提示
  if (verbosityLevel === 'high' && element.hint) {
    description += ` ${element.hint}`;
  }
  
  return description.trim();
};

/**
 * 元素类型翻译
 */
const translateElementType = (type: string): string => {
  const typeMap: Record<string, string> = {
    'button': '按钮',
    'input': '输入框',
    'checkbox': '复选框',
    'radio': '单选按钮',
    'select': '下拉框',
    'textarea': '文本域',
    'link': '链接',
    'image': '图片',
    'heading': '标题',
    'list': '列表',
    'listitem': '列表项',
    'table': '表格',
    'menu': '菜单',
    'menuitem': '菜单项',
    'dialog': '对话框',
    'alert': '提醒',
    'tab': '选项卡',
    'tabpanel': '选项卡面板',
    'tree': '树形结构',
    'treeitem': '树形项',
    'slider': '滑块'
  };
  
  return typeMap[type.toLowerCase()] || type;
};

/**
 * 朗读元素
 */
export const readElement = async (elementId: string, userId: string): Promise<ReadingRequest | null> => {
  try {
    const element = uiElementsCache[elementId];
    if (!element) {
      logger.warn(`尝试朗读不存在的UI元素: ${elementId}`);
      return null;
    }
    
    const settings = getUserSettings(userId);
    if (!settings.enabled) {
      logger.info(`用户屏幕阅读功能已禁用: ${userId}`);
      return null;
    }
    
    const descriptionText = buildElementDescriptionText(element, settings.verbosityLevel);
    
    const request: ReadingRequest = {
      id: uuidv4(),
      userId,
      timestamp: new Date().toISOString(),
      elementId,
      text: descriptionText,
      priority: element.priority || 5,
      status: 'pending'
    };
    
    // 如果设置为中断当前朗读，则清空队列
    if (settings.interruptOnAction) {
      clearReadingQueue(userId);
    }
    
    // 添加到朗读队列
    addToReadingQueue(request);
    
    // 处理朗读队列
    await processReadingQueue(userId);
    
    return request;
  } catch (error) {
    logger.error('朗读元素失败:', error);
    throw new Error(`朗读元素失败: ${(error as Error).message}`);
  }
};

/**
 * 朗读文本
 */
export const readText = async (text: string, userId: string, priority: number = 5): Promise<ReadingRequest | null> => {
  try {
    const settings = getUserSettings(userId);
    if (!settings.enabled) {
      logger.info(`用户屏幕阅读功能已禁用: ${userId}`);
      return null;
    }
    
    const request: ReadingRequest = {
      id: uuidv4(),
      userId,
      timestamp: new Date().toISOString(),
      text,
      priority,
      status: 'pending'
    };
    
    // 如果设置为中断当前朗读，则清空队列
    if (settings.interruptOnAction) {
      clearReadingQueue(userId);
    }
    
    // 添加到朗读队列
    addToReadingQueue(request);
    
    // 处理朗读队列
    await processReadingQueue(userId);
    
    return request;
  } catch (error) {
    logger.error('朗读文本失败:', error);
    throw new Error(`朗读文本失败: ${(error as Error).message}`);
  }
};

/**
 * 停止朗读
 */
export const stopReading = (userId: string): void => {
  clearReadingQueue(userId);
  logger.info(`已停止用户朗读: ${userId}`);
};

/**
 * 添加到朗读队列
 */
const addToReadingQueue = (request: ReadingRequest): void => {
  // 按优先级插入队列
  const insertIndex = readingQueue.findIndex(item => item.priority > request.priority);
  
  if (insertIndex >= 0) {
    readingQueue.splice(insertIndex, 0, request);
  } else {
    readingQueue.push(request);
  }
  
  logger.debug(`已添加朗读请求到队列: ${request.id}, 优先级: ${request.priority}, 文本: "${request.text.substring(0, 20)}..."`);
};

/**
 * 清空用户的朗读队列
 */
const clearReadingQueue = (userId: string): void => {
  // 将正在朗读的项标记为中断
  const currentReading = readingQueue.find(item => item.userId === userId && item.status === 'reading');
  if (currentReading) {
    currentReading.status = 'interrupted';
  }
  
  // 移除所有待朗读的项
  const pendingIndexes = readingQueue
    .map((item, index) => item.userId === userId && item.status === 'pending' ? index : -1)
    .filter(index => index !== -1)
    .sort((a, b) => b - a); // 从后往前移除，避免索引变化
  
  for (const index of pendingIndexes) {
    readingQueue.splice(index, 1);
  }
  
  logger.debug(`已清空用户朗读队列: ${userId}`);
};

/**
 * 处理朗读队列
 */
const processReadingQueue = async (userId: string): Promise<void> => {
  // 如果已有正在处理的请求，直接返回
  if (readingQueue.some(item => item.status === 'reading')) {
    return;
  }
  
  // 获取下一个待处理的请求
  const nextRequest = readingQueue.find(item => item.status === 'pending');
  if (!nextRequest) {
    return;
  }
  
  try {
    // 标记为正在朗读
    nextRequest.status = 'reading';
    
    const settings = getUserSettings(userId);
    
    // 调用语音合成服务
    const synthesisResult = await synthesizeDialectSpeech({
      text: nextRequest.text,
      dialect: settings.dialect,
      voiceId: settings.voiceId,
      speed: settings.readingSpeed,
      volume: settings.readingVolume,
      userId,
      format: 'mp3'
    });
    
    // 更新请求状态
    nextRequest.synthesisResult = synthesisResult;
    nextRequest.status = 'completed';
    
    logger.info(`朗读完成: ${nextRequest.id}`);
    
    // 移除已完成的请求
    const index = readingQueue.findIndex(item => item.id === nextRequest.id);
    if (index >= 0) {
      readingQueue.splice(index, 1);
    }
    
    // 处理下一个请求
    await processReadingQueue(userId);
  } catch (error) {
    logger.error('处理朗读请求失败:', error);
    
    // 标记为完成（失败）并移除
    nextRequest.status = 'completed';
    const index = readingQueue.findIndex(item => item.id === nextRequest.id);
    if (index >= 0) {
      readingQueue.splice(index, 1);
    }
    
    // 尝试处理下一个请求
    await processReadingQueue(userId);
  }
};
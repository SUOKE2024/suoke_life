import { logger } from '../../utils/logger';
import { AgentConfig, AgentMessage } from './types';
import { getModel } from './models';

/**
 * 会话缓存
 */
interface SessionCache {
  [sessionId: string]: {
    messages: AgentMessage[];
    metadata: Record<string, any>;
    lastUpdated: number;
  };
}

// 会话缓存，用于存储会话历史
const sessions: SessionCache = {};
// 记忆持久化
let memoryPersistence: any = null;
// 向量存储
let vectorStore: any = null;

/**
 * 初始化智能体记忆系统
 * @param config 智能体配置
 */
export const initializeAgentMemory = async (config: AgentConfig): Promise<void> => {
  try {
    logger.info('初始化智能体记忆系统...');
    
    // 如果配置了持久化，初始化持久化
    if (process.env.MEMORY_PERSISTENCE === 'true') {
      await initializeMemoryPersistence();
    }
    
    // 初始化向量存储，用于语义搜索
    await initializeVectorStore(config);
    
    logger.info('智能体记忆系统初始化完成');
  } catch (error) {
    logger.error('智能体记忆系统初始化失败:', error);
    throw error;
  }
};

/**
 * 初始化记忆持久化
 */
const initializeMemoryPersistence = async (): Promise<void> => {
  try {
    logger.info('初始化记忆持久化...');
    
    // 动态加载持久化实现
    const persistenceModule = await import('../../services/memory/persistence');
    memoryPersistence = new persistenceModule.MemoryPersistence();
    await memoryPersistence.initialize();
    
    logger.info('记忆持久化初始化完成');
  } catch (error) {
    logger.error('记忆持久化初始化失败:', error);
    throw error;
  }
};

/**
 * 初始化向量存储
 * @param config 智能体配置
 */
const initializeVectorStore = async (config: AgentConfig): Promise<void> => {
  try {
    logger.info('初始化向量存储...');
    
    // 获取嵌入模型
    const embeddingModel = getModel('embedding');
    
    if (!embeddingModel) {
      logger.warn('未找到嵌入模型，跳过向量存储初始化');
      return;
    }
    
    // 动态加载向量存储实现
    const vectorStoreModule = await import('../../services/memory/vector-store');
    vectorStore = new vectorStoreModule.VectorStore(embeddingModel);
    await vectorStore.initialize();
    
    logger.info('向量存储初始化完成');
  } catch (error) {
    logger.error('向量存储初始化失败:', error);
    // 这里我们不抛出错误，因为向量存储不是必需的
    logger.warn('将继续而不使用向量存储');
  }
};

/**
 * 添加消息到会话
 * @param sessionId 会话ID
 * @param message 消息
 */
export const addMessage = async (sessionId: string, message: AgentMessage): Promise<void> => {
  // 确保会话存在
  if (!sessions[sessionId]) {
    sessions[sessionId] = {
      messages: [],
      metadata: {},
      lastUpdated: Date.now()
    };
  }
  
  // 添加消息
  sessions[sessionId].messages.push(message);
  sessions[sessionId].lastUpdated = Date.now();
  
  // 如果启用了向量存储，将消息添加到向量存储
  if (vectorStore && message.role === 'user') {
    try {
      await vectorStore.addText(message.content, {
        messageId: message.id,
        sessionId,
        timestamp: message.timestamp
      });
    } catch (error) {
      logger.error('向量存储添加消息失败:', error);
    }
  }
  
  // 如果启用了持久化，将消息持久化
  if (memoryPersistence) {
    try {
      await memoryPersistence.saveSession(sessionId, sessions[sessionId]);
    } catch (error) {
      logger.error('会话持久化失败:', error);
    }
  }
};

/**
 * 获取会话历史
 * @param sessionId 会话ID
 * @param limit 限制消息数量，默认不限制
 */
export const getMessages = (sessionId: string, limit?: number): AgentMessage[] => {
  const session = sessions[sessionId];
  
  if (!session) {
    return [];
  }
  
  const messages = session.messages;
  
  if (limit && limit > 0 && messages.length > limit) {
    return messages.slice(messages.length - limit);
  }
  
  return [...messages];
};

/**
 * 清除会话历史
 * @param sessionId 会话ID
 */
export const clearSession = async (sessionId: string): Promise<void> => {
  if (sessions[sessionId]) {
    delete sessions[sessionId];
    
    // 如果启用了持久化，从持久化中删除会话
    if (memoryPersistence) {
      try {
        await memoryPersistence.deleteSession(sessionId);
      } catch (error) {
        logger.error('删除会话持久化失败:', error);
      }
    }
  }
};

/**
 * 根据查询获取相关记忆
 * @param query 查询
 * @param sessionId 会话ID (可选)
 * @param limit 限制结果数量
 */
export const searchMemory = async (query: string, sessionId?: string, limit = 5): Promise<AgentMessage[]> => {
  if (!vectorStore) {
    logger.warn('向量存储未初始化，无法搜索记忆');
    return [];
  }
  
  try {
    const results = await vectorStore.search(query, limit, sessionId ? { sessionId } : undefined);
    return results.map(result => ({
      id: result.metadata.messageId,
      role: 'user',
      content: result.text,
      timestamp: result.metadata.timestamp
    }));
  } catch (error) {
    logger.error('搜索记忆失败:', error);
    return [];
  }
};

/**
 * 设置会话元数据
 * @param sessionId 会话ID
 * @param key 元数据键
 * @param value 元数据值
 */
export const setSessionMetadata = async (sessionId: string, key: string, value: any): Promise<void> => {
  // 确保会话存在
  if (!sessions[sessionId]) {
    sessions[sessionId] = {
      messages: [],
      metadata: {},
      lastUpdated: Date.now()
    };
  }
  
  // 设置元数据
  sessions[sessionId].metadata[key] = value;
  sessions[sessionId].lastUpdated = Date.now();
  
  // 如果启用了持久化，更新持久化
  if (memoryPersistence) {
    try {
      await memoryPersistence.saveSession(sessionId, sessions[sessionId]);
    } catch (error) {
      logger.error('更新会话元数据持久化失败:', error);
    }
  }
};

/**
 * 获取会话元数据
 * @param sessionId 会话ID
 * @param key 元数据键
 */
export const getSessionMetadata = (sessionId: string, key: string): any => {
  const session = sessions[sessionId];
  
  if (!session || !session.metadata[key]) {
    return null;
  }
  
  return session.metadata[key];
};

/**
 * 加载会话
 * @param sessionId 会话ID
 */
export const loadSession = async (sessionId: string): Promise<boolean> => {
  if (!memoryPersistence) {
    logger.warn('记忆持久化未初始化，无法加载会话');
    return false;
  }
  
  try {
    const session = await memoryPersistence.loadSession(sessionId);
    
    if (session) {
      sessions[sessionId] = session;
      return true;
    }
    
    return false;
  } catch (error) {
    logger.error('加载会话失败:', error);
    return false;
  }
};

/**
 * 清理过期会话
 * @param maxAge 最大会话年龄(毫秒)，默认24小时
 */
export const cleanupSessions = async (maxAge = 24 * 60 * 60 * 1000): Promise<void> => {
  const now = Date.now();
  const expiredSessionIds = [];
  
  for (const sessionId in sessions) {
    if (now - sessions[sessionId].lastUpdated > maxAge) {
      expiredSessionIds.push(sessionId);
    }
  }
  
  for (const sessionId of expiredSessionIds) {
    await clearSession(sessionId);
  }
  
  if (expiredSessionIds.length > 0) {
    logger.info(`已清理 ${expiredSessionIds.length} 个过期会话`);
  }
};

/**
 * 释放记忆资源
 */
export const releaseMemory = async (): Promise<void> => {
  try {
    logger.info('释放记忆资源...');
    
    if (memoryPersistence) {
      await memoryPersistence.close();
      memoryPersistence = null;
    }
    
    if (vectorStore) {
      await vectorStore.close();
      vectorStore = null;
    }
    
    logger.info('记忆资源已释放');
  } catch (error) {
    logger.error('释放记忆资源失败:', error);
  }
}; 
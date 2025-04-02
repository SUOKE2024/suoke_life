/**
 * 会话管理服务
 */
import { v4 as uuidv4 } from 'uuid';
import { getRedisClient } from './redis-service';
import { Session, SessionStatus, SessionMessage, SessionUpdate } from '../models/session';
import { loadConfig } from '../utils/config-loader';
import logger from '../utils/logger';

export class SessionService {
  private config = loadConfig();
  
  /**
   * 创建新会话
   */
  async createSession(
    userId: string,
    preferredAgentId?: string,
    initialContext?: Record<string, any>
  ): Promise<Session> {
    try {
      // 获取默认代理或指定代理
      const agentId = preferredAgentId || this.getDefaultAgentId();
      
      // 创建会话对象
      const session: Session = {
        id: uuidv4(),
        userId,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        expiresAt: this.calculateExpiryTime().toISOString(),
        status: SessionStatus.ACTIVE,
        currentAgentId: agentId,
        context: initialContext || {},
      };
      
      // 存储会话
      await this.saveSession(session);
      
      return session;
    } catch (error) {
      logger.error('创建会话失败', { error, userId });
      throw error;
    }
  }
  
  /**
   * 获取会话信息
   */
  async getSession(sessionId: string): Promise<Session | null> {
    try {
      const redis = getRedisClient();
      const sessionKey = `session:${sessionId}`;
      
      // 从Redis获取会话数据
      const sessionData = await redis.get(sessionKey);
      
      if (!sessionData) {
        return null;
      }
      
      return JSON.parse(sessionData) as Session;
    } catch (error) {
      logger.error('获取会话失败', { error, sessionId });
      throw error;
    }
  }
  
  /**
   * 更新会话信息
   */
  async updateSession(sessionId: string, update: SessionUpdate): Promise<Session | null> {
    try {
      // 获取现有会话
      const session = await this.getSession(sessionId);
      
      if (!session) {
        return null;
      }
      
      // 更新会话
      const updatedSession: Session = {
        ...session,
        ...update,
        updatedAt: new Date().toISOString(),
      };
      
      // 保存更新后的会话
      await this.saveSession(updatedSession);
      
      return updatedSession;
    } catch (error) {
      logger.error('更新会话失败', { error, sessionId });
      throw error;
    }
  }
  
  /**
   * 结束会话
   */
  async endSession(sessionId: string): Promise<boolean> {
    try {
      // 获取现有会话
      const session = await this.getSession(sessionId);
      
      if (!session) {
        return false;
      }
      
      // 更新会话状态为已完成
      const updatedSession: Session = {
        ...session,
        status: SessionStatus.COMPLETED,
        updatedAt: new Date().toISOString(),
      };
      
      // 保存更新后的会话
      await this.saveSession(updatedSession);
      
      return true;
    } catch (error) {
      logger.error('结束会话失败', { error, sessionId });
      throw error;
    }
  }
  
  /**
   * 获取会话消息历史
   */
  async getSessionMessages(
    sessionId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<SessionMessage[]> {
    try {
      const redis = getRedisClient();
      const messagesKey = `session:${sessionId}:messages`;
      
      // 从Redis获取消息历史
      const messages = await redis.lrange(messagesKey, offset, offset + limit - 1);
      
      return messages.map(msg => JSON.parse(msg) as SessionMessage);
    } catch (error) {
      logger.error('获取会话消息历史失败', { error, sessionId });
      throw error;
    }
  }
  
  /**
   * 添加会话消息
   */
  async addSessionMessage(message: SessionMessage): Promise<boolean> {
    try {
      const redis = getRedisClient();
      const messagesKey = `session:${message.sessionId}:messages`;
      
      // 将消息添加到Redis列表
      await redis.rpush(messagesKey, JSON.stringify(message));
      
      // 更新会话的更新时间
      await this.updateSessionTimestamp(message.sessionId);
      
      return true;
    } catch (error) {
      logger.error('添加会话消息失败', { error, sessionId: message.sessionId });
      throw error;
    }
  }
  
  /**
   * 保存会话到存储
   */
  private async saveSession(session: Session): Promise<void> {
    try {
      const redis = getRedisClient();
      const sessionKey = `session:${session.id}`;
      
      // 计算TTL (秒)
      const expiryDate = new Date(session.expiresAt);
      const now = new Date();
      const ttlSeconds = Math.max(1, Math.floor((expiryDate.getTime() - now.getTime()) / 1000));
      
      // 保存会话到Redis，设置过期时间
      await redis.set(sessionKey, JSON.stringify(session), 'EX', ttlSeconds);
      
      // 添加到用户会话索引
      await redis.sadd(`user:${session.userId}:sessions`, session.id);
    } catch (error) {
      logger.error('保存会话失败', { error, sessionId: session.id });
      throw error;
    }
  }
  
  /**
   * 更新会话时间戳
   */
  private async updateSessionTimestamp(sessionId: string): Promise<void> {
    try {
      const session = await this.getSession(sessionId);
      
      if (session) {
        session.updatedAt = new Date().toISOString();
        await this.saveSession(session);
      }
    } catch (error) {
      logger.error('更新会话时间戳失败', { error, sessionId });
      throw error;
    }
  }
  
  /**
   * 获取默认代理ID
   */
  private getDefaultAgentId(): string {
    // 查找默认代理
    const defaultAgent = this.config.agents.find(agent => agent.isDefault);
    
    // 如果找到默认代理，返回其ID
    if (defaultAgent) {
      return defaultAgent.id;
    }
    
    // 否则返回第一个代理ID，如果存在的话
    if (this.config.agents.length > 0) {
      return this.config.agents[0].id;
    }
    
    // 最后返回空字符串
    return '';
  }
  
  /**
   * 计算会话过期时间
   */
  private calculateExpiryTime(): Date {
    // 默认TTL为24小时
    const ttlSeconds = parseInt(process.env.SESSION_TTL_SECONDS || '86400', 10);
    
    // 计算过期时间
    const expiryTime = new Date();
    expiryTime.setSeconds(expiryTime.getSeconds() + ttlSeconds);
    
    return expiryTime;
  }
}
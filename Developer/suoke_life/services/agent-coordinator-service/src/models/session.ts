/**
 * 会话管理模型
 */

/**
 * 会话状态枚举
 */
export enum SessionStatus {
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed',
}

/**
 * 会话接口
 */
export interface Session {
  id: string;
  userId: string;
  createdAt: string;
  updatedAt: string;
  expiresAt: string;
  status: SessionStatus;
  currentAgentId: string;
  context?: Record<string, any>;
  metadata?: Record<string, any>;
}

/**
 * 会话消息接口
 */
export interface SessionMessage {
  id: string;
  sessionId: string;
  timestamp: string;
  role: 'user' | 'agent' | 'system';
  content: string;
  agentId?: string;
  metadata?: Record<string, any>;
}

/**
 * 会话更新接口
 */
export interface SessionUpdate {
  status?: SessionStatus;
  currentAgentId?: string;
  context?: Record<string, any>;
  metadata?: Record<string, any>;
}

/**
 * 会话工具调用接口
 */
export interface SessionToolCall {
  id: string;
  sessionId: string;
  messageId: string;
  timestamp: string;
  toolName: string;
  parameters: Record<string, any>;
  result?: string;
  status: 'pending' | 'completed' | 'failed';
  error?: string;
}
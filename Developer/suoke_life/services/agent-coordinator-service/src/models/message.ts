/**
 * 消息类型枚举
 */
export enum MessageType {
  TEXT = 'text',
  IMAGE = 'image',
  AUDIO = 'audio',
  VIDEO = 'video',
  FILE = 'file',
  SYSTEM = 'system',
  FUNCTION_CALL = 'function_call',
  FUNCTION_RETURN = 'function_return'
}

/**
 * 消息角色枚举
 */
export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system',
  FUNCTION = 'function'
}

/**
 * 会话消息接口
 */
export interface SessionMessage {
  role: MessageRole | string;
  content: string;
  type: MessageType | string;
  timestamp: number;
  agentId?: string;
  metadata?: Record<string, any>;
} 
/**
 * 统一错误处理类
 */
import { Response } from 'express';
import logger from './logger';

export enum ErrorCode {
  // 通用错误
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
  INVALID_REQUEST = 'INVALID_REQUEST',
  NOT_FOUND = 'NOT_FOUND',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  
  // 会话错误
  SESSION_NOT_FOUND = 'SESSION_NOT_FOUND',
  SESSION_EXPIRED = 'SESSION_EXPIRED',
  SESSION_CREATION_FAILED = 'SESSION_CREATION_FAILED',
  
  // 代理错误
  AGENT_NOT_FOUND = 'AGENT_NOT_FOUND',
  AGENT_UNAVAILABLE = 'AGENT_UNAVAILABLE',
  AGENT_RESPONSE_FAILED = 'AGENT_RESPONSE_FAILED',
  
  // 协调错误
  COORDINATION_FAILED = 'COORDINATION_FAILED',
  HANDOFF_FAILED = 'HANDOFF_FAILED',
  ROUTING_FAILED = 'ROUTING_FAILED',
  
  // 知识服务错误
  KNOWLEDGE_NOT_FOUND = 'KNOWLEDGE_NOT_FOUND',
  KNOWLEDGE_SERVICE_UNAVAILABLE = 'KNOWLEDGE_SERVICE_UNAVAILABLE',
  KNOWLEDGE_QUERY_FAILED = 'KNOWLEDGE_QUERY_FAILED',
  RAG_GENERATION_FAILED = 'RAG_GENERATION_FAILED'
}

export class AppError extends Error {
  public readonly statusCode: number;
  public readonly errorCode: ErrorCode;
  public readonly details?: Record<string, any>;
  
  constructor(
    message: string, 
    errorCode: ErrorCode = ErrorCode.UNKNOWN_ERROR, 
    statusCode: number = 500,
    details?: Record<string, any>
  ) {
    super(message);
    this.name = this.constructor.name;
    this.errorCode = errorCode;
    this.statusCode = statusCode;
    this.details = details;
    
    // 确保继承Error时，原型链正确
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

// 会话错误
export class SessionNotFoundError extends AppError {
  constructor(sessionId: string) {
    super(
      `未找到会话: ${sessionId}`,
      ErrorCode.SESSION_NOT_FOUND,
      404
    );
  }
}

// 代理错误
export class AgentNotFoundError extends AppError {
  constructor(agentId: string) {
    super(
      `未找到代理: ${agentId}`,
      ErrorCode.AGENT_NOT_FOUND,
      404
    );
  }
}

// 知识错误
export class KnowledgeNotFoundError extends AppError {
  constructor(knowledgeId: string) {
    super(
      `未找到知识条目: ${knowledgeId}`,
      ErrorCode.KNOWLEDGE_NOT_FOUND,
      404
    );
  }
}

// 路由处理
export function handleError(error: any, res: Response): Response {
  // 如果是我们的自定义错误类型
  if (error instanceof AppError) {
    logger.error(`应用错误: ${error.message}`, {
      errorCode: error.errorCode,
      statusCode: error.statusCode,
      details: error.details,
      stack: error.stack
    });
    
    return res.status(error.statusCode).json({
      success: false,
      error: {
        code: error.errorCode,
        message: error.message,
        details: error.details
      }
    });
  }
  
  // 未知错误
  logger.error(`未处理的错误: ${error.message || '未知错误'}`, {
    error,
    stack: error.stack
  });
  
  return res.status(500).json({
    success: false,
    error: {
      code: ErrorCode.UNKNOWN_ERROR,
      message: '服务器内部错误'
    }
  });
} 
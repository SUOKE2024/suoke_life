import { Request, Response, NextFunction } from 'express';
import { Logger } from '../utils/logger';

// 错误类型枚举
export enum ErrorType {
  VALIDATION_ERROR = 'ValidationError',
  AUTHENTICATION_ERROR = 'AuthenticationError',
  AUTHORIZATION_ERROR = 'AuthorizationError',
  NOT_FOUND_ERROR = 'NotFoundError',
  DATABASE_ERROR = 'DatabaseError',
  MICROSERVICE_ERROR = 'MicroserviceError',
  INTEGRATION_ERROR = 'IntegrationError',
  CONFLICT_ERROR = 'ConflictError',
  RATE_LIMIT_ERROR = 'RateLimitError',
  INVALID_DATA_ERROR = 'InvalidDataError',
  ANALYSIS_ERROR = 'AnalysisError',
  EDGE_CASE_ERROR = 'EdgeCaseError',
  UNKNOWN_ERROR = 'UnknownError',
  // 新增四诊特定错误类型
  INCOMPLETE_DIAGNOSIS_ERROR = 'IncompleteDiagnosisError',
  DIAGNOSIS_CONFLICT_ERROR = 'DiagnosisConflictError',
  LOOKING_SERVICE_ERROR = 'LookingServiceError',
  SMELL_SERVICE_ERROR = 'SmellServiceError',
  INQUIRY_SERVICE_ERROR = 'InquiryServiceError',
  TOUCH_SERVICE_ERROR = 'TouchServiceError',
  INVALID_PATTERN_ERROR = 'InvalidPatternError',
  DATA_SYNC_ERROR = 'DataSyncError',
  INSUFFICIENT_DATA_ERROR = 'InsufficientDataError'
}

// 应用错误类
export class AppError extends Error {
  public readonly type: ErrorType;
  public readonly statusCode: number;
  public readonly isOperational: boolean;
  public readonly details?: any;
  public readonly source?: string;
  public readonly diagnosisType?: string;
  public readonly patientId?: string;

  constructor(
    message: string,
    type: ErrorType = ErrorType.UNKNOWN_ERROR,
    statusCode: number = 500,
    isOperational: boolean = true,
    details?: any,
    source?: string,
    diagnosisType?: string,
    patientId?: string
  ) {
    super(message);
    this.type = type;
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    this.details = details;
    this.source = source;
    this.diagnosisType = diagnosisType;
    this.patientId = patientId;
    
    Error.captureStackTrace(this, this.constructor);
    
    Object.setPrototypeOf(this, AppError.prototype);
  }

  /**
   * 创建四诊服务特定错误
   */
  static diagnosisServiceError(
    diagnosisType: string,
    message: string,
    patientId?: string,
    details?: any
  ): AppError {
    const errorTypeMap: {[key: string]: ErrorType} = {
      'looking': ErrorType.LOOKING_SERVICE_ERROR,
      'smell': ErrorType.SMELL_SERVICE_ERROR,
      'inquiry': ErrorType.INQUIRY_SERVICE_ERROR,
      'touch': ErrorType.TOUCH_SERVICE_ERROR
    };

    const errorType = errorTypeMap[diagnosisType] || ErrorType.MICROSERVICE_ERROR;
    
    return new AppError(
      message,
      errorType,
      503,
      true,
      details,
      `${diagnosisType}-service`,
      diagnosisType,
      patientId
    );
  }

  /**
   * 创建诊断冲突错误
   */
  static diagnosisConflictError(
    message: string,
    conflictDetails: any,
    patientId?: string
  ): AppError {
    return new AppError(
      message,
      ErrorType.DIAGNOSIS_CONFLICT_ERROR,
      409,
      true,
      conflictDetails,
      'analysis-engine',
      undefined,
      patientId
    );
  }

  /**
   * 创建数据不足错误
   */
  static insufficientDataError(
    message: string,
    availableDiagnoses: string[],
    patientId?: string
  ): AppError {
    return new AppError(
      message,
      ErrorType.INSUFFICIENT_DATA_ERROR,
      400,
      true,
      { availableDiagnoses },
      'coordination-service',
      undefined,
      patientId
    );
  }
}

/**
 * 错误处理中间件
 * 处理应用程序中的各种错误，返回格式统一的错误响应
 */
export const errorMiddleware = (
  err: Error | AppError,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const logger = new Logger('ErrorHandler');
  let error: AppError;
  
  // 转换普通Error为AppError
  if (!(err instanceof AppError)) {
    // 处理MongoDB验证错误
    if (err.name === 'ValidationError') {
      error = new AppError(
        '数据验证失败',
        ErrorType.VALIDATION_ERROR,
        400,
        true,
        err
      );
    } 
    // 处理MongoDB重复键错误
    else if (err.name === 'MongoError' && (err as any).code === 11000) {
      error = new AppError(
        '数据冲突，可能存在重复记录',
        ErrorType.CONFLICT_ERROR,
        409,
        true,
        err
      );
    } 
    // 处理JWT错误
    else if (err.name === 'JsonWebTokenError') {
      error = new AppError(
        '无效的认证令牌',
        ErrorType.AUTHENTICATION_ERROR,
        401,
        true,
        err
      );
    }
    // 处理连接超时错误
    else if (err.name === 'TimeoutError' || (err.message && err.message.includes('timeout'))) {
      error = new AppError(
        '服务响应超时，请稍后重试',
        ErrorType.MICROSERVICE_ERROR,
        504,
        true,
        err
      );
    }
    // 处理网络连接错误
    else if (err.name === 'FetchError' || err.name === 'NetworkError' || 
            (err.message && (err.message.includes('ECONNREFUSED') || 
                             err.message.includes('network') || 
                             err.message.includes('connection')))) {
      error = new AppError(
        '无法连接到服务，请检查网络或稍后重试',
        ErrorType.MICROSERVICE_ERROR,
        503,
        true,
        err
      );
    }
    // 其他未知错误
    else {
      error = new AppError(
        err.message || '服务器内部错误',
        ErrorType.UNKNOWN_ERROR,
        500,
        false,
        err
      );
    }
  } else {
    error = err;
  }

  // 记录错误日志
  logError(error, req);
  
  // 发送错误响应
  sendErrorResponse(error, req, res);
};

/**
 * 记录错误日志
 */
const logError = (error: AppError, req: Request): void => {
  const logger = new Logger('ErrorHandler');
  const logData = {
    type: error.type,
    isOperational: error.isOperational,
    message: error.message,
    path: req.path,
    method: req.method,
    ip: req.ip,
    userId: (req as any).user?.id || 'anonymous',
    patientId: error.patientId || req.params.patientId || req.body.patientId || 'unknown',
    diagnosisType: error.diagnosisType,
    timestamp: new Date().toISOString()
  };
  
  if (error.statusCode >= 500) {
    logger.error('服务器错误', { error: logData, stack: error.stack });
  } else if (error.type.includes('Service')) {
    logger.error(`微服务错误: ${error.source || 'unknown'}`, { error: logData });
  } else {
    logger.warn('客户端错误', { error: logData });
  }
  
  // 特殊处理四诊冲突错误，记录详细冲突信息
  if (error.type === ErrorType.DIAGNOSIS_CONFLICT_ERROR) {
    logger.info('诊断冲突详情', { 
      patientId: error.patientId, 
      conflictDetails: error.details 
    });
  }
};

/**
 * 发送统一格式的错误响应
 */
const sendErrorResponse = (
  error: AppError,
  req: Request,
  res: Response
): void => {
  // 生产环境下隐藏错误详情
  const isDevelopment = process.env.NODE_ENV === 'development';
  
  // 定义响应类型，包括suggestion字段
  interface ErrorResponse {
    success: boolean;
    error: {
      type: ErrorType;
      message: string;
      code: number;
      diagnosisType?: string;
      details?: any;
      stack?: string;
      suggestion?: string;
    };
    requestId: string;
    timestamp: string;
  }
  
  const response: ErrorResponse = {
    success: false,
    error: {
      type: error.type,
      message: error.message,
      code: error.statusCode,
      ...(error.diagnosisType && { diagnosisType: error.diagnosisType }),
      ...(isDevelopment && { details: error.details }),
      ...(isDevelopment && { stack: error.stack })
    },
    requestId: req.headers['x-request-id']?.toString() || '',
    timestamp: new Date().toISOString()
  };
  
  // 添加用户友好建议
  if (error.type === ErrorType.INSUFFICIENT_DATA_ERROR) {
    response.error.suggestion = '请提供更多诊断数据以获得更准确的分析结果';
  } else if (error.type === ErrorType.DIAGNOSIS_CONFLICT_ERROR) {
    response.error.suggestion = '发现诊断结果存在冲突，系统已尝试自动解决，结果可能不完全准确';
  } else if (error.type.includes('Service')) {
    response.error.suggestion = '当前服务暂时不可用，请稍后再试';
  }
  
  res.status(error.statusCode).json(response);
};

/**
 * 请求ID中间件 - 为每个请求分配唯一ID
 */
export const requestIdMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  const { v4: uuidv4 } = require('uuid');
  req.headers['x-request-id'] = req.headers['x-request-id'] || uuidv4();
  next();
};

/**
 * 请求日志中间件
 */
export const requestLoggerMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  const logger = new Logger('RequestLogger');
  const start = Date.now();
  
  // 记录请求开始
  logger.debug(`${req.method} ${req.path} 开始处理`, {
    requestId: req.headers['x-request-id'],
    body: req.method !== 'GET' ? req.body : undefined,
    query: req.query,
    params: req.params,
    ip: req.ip
  });
  
  // 拦截响应完成事件
  res.on('finish', () => {
    const duration = Date.now() - start;
    const level = res.statusCode >= 500 ? 'error' : 
                  res.statusCode >= 400 ? 'warn' : 'info';
    
    logger[level](`${req.method} ${req.path} ${res.statusCode} [${duration}ms]`, {
      requestId: req.headers['x-request-id'],
      statusCode: res.statusCode,
      duration,
      ip: req.ip
    });
  });
  
  next();
};

/**
 * 404错误处理中间件
 */
export const notFoundHandler = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const error = new AppError(
    `找不到路径: ${req.originalUrl}`,
    ErrorType.NOT_FOUND_ERROR,
    404
  );
  
  next(error);
};

/**
 * 未捕获的异步错误处理
 */
export const setupUnhandledRejectionHandler = (): void => {
  const logger = new Logger('GlobalErrorHandler');
  
  process.on('unhandledRejection', (reason: Error) => {
    logger.error('未处理的Promise拒绝', {
      message: reason.message,
      stack: reason.stack
    });
    
    // 不立即崩溃，让进程正常结束或由进程管理器处理
    console.error('未处理的Promise拒绝:', reason);
  });
};

/**
 * 未捕获的异常处理
 */
export const setupUncaughtExceptionHandler = (): void => {
  const logger = new Logger('GlobalErrorHandler');
  
  process.on('uncaughtException', (error: Error) => {
    logger.error('未捕获的异常', {
      message: error.message,
      stack: error.stack
    });
    
    // 对于未捕获的异常，最安全的做法是终止进程
    console.error('未捕获的异常，进程即将终止:', error);
    
    // 给日志系统一点时间将日志写入
    setTimeout(() => {
      process.exit(1);
    }, 1000);
  });
}; 
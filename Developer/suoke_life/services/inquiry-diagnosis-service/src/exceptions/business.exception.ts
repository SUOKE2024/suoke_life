/**
 * 业务异常类
 * 用于处理业务逻辑相关的错误
 */

import { HttpException } from './http.exception';

export class BusinessException extends HttpException {
  public errorCode: string;

  constructor(message: string, errorCode: string, status = 400) {
    super(status, message, { errorCode });
    this.errorCode = errorCode;
    this.name = 'BusinessException';
  }
}

/**
 * 问诊相关异常
 */
export class InquiryNotFoundException extends BusinessException {
  constructor(id: string) {
    super(`未找到ID为${id}的问诊会话`, 'INQUIRY_NOT_FOUND', 404);
    this.name = 'InquiryNotFoundException';
  }
}

export class InquirySessionCompletedException extends BusinessException {
  constructor(id: string) {
    super(`问诊会话${id}已结束，无法继续交互`, 'INQUIRY_SESSION_COMPLETED', 400);
    this.name = 'InquirySessionCompletedException';
  }
}

export class InvalidSessionStatusException extends BusinessException {
  constructor(status: string) {
    super(`会话状态无效: ${status}`, 'INVALID_SESSION_STATUS', 400);
    this.name = 'InvalidSessionStatusException';
  }
}

/**
 * 诊断相关异常
 */
export class DiagnosisNotFoundException extends BusinessException {
  constructor(id: string) {
    super(`未找到ID为${id}的诊断记录`, 'DIAGNOSIS_NOT_FOUND', 404);
    this.name = 'DiagnosisNotFoundException';
  }
}

export class InsufficientDataException extends BusinessException {
  constructor() {
    super('诊断所需信息不足', 'INSUFFICIENT_DATA', 400);
    this.name = 'InsufficientDataException';
  }
}

export class DiagnosisFailedException extends BusinessException {
  constructor(reason: string = '诊断处理失败') {
    super(reason, 'DIAGNOSIS_FAILED', 500);
    this.name = 'DiagnosisFailedException';
  }
}

/**
 * 集成服务相关异常
 */
export class IntegrationServiceException extends BusinessException {
  constructor(service: string, message: string) {
    super(`${service}服务错误: ${message}`, 'INTEGRATION_SERVICE_ERROR', 502);
    this.name = 'IntegrationServiceException';
  }
}

export class CoordinatorServiceException extends BusinessException {
  constructor(message: string) {
    super(`四诊协调服务错误: ${message}`, 'COORDINATOR_SERVICE_ERROR', 502);
    this.name = 'CoordinatorServiceException';
  }
}
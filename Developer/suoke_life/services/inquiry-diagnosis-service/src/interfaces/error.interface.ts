/**
 * @swagger
 * components:
 *   schemas:
 *     Error:
 *       type: object
 *       required:
 *         - success
 *         - message
 *         - statusCode
 *       properties:
 *         success:
 *           type: boolean
 *           example: false
 *           description: 操作是否成功
 *         message:
 *           type: string
 *           description: 错误消息
 *         statusCode:
 *           type: integer
 *           description: HTTP状态码
 *         error:
 *           type: string
 *           description: 错误类型
 *         details:
 *           type: object
 *           description: 错误详情
 *         timestamp:
 *           type: string
 *           format: date-time
 *           description: 错误发生时间
 *
 *     ValidationError:
 *       allOf:
 *         - $ref: '#/components/schemas/Error'
 *         - type: object
 *           properties:
 *             error:
 *               example: ValidationError
 *             details:
 *               type: object
 *               properties:
 *                 errors:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       field:
 *                         type: string
 *                       message:
 *                         type: string
 */

// 错误响应接口
export interface ErrorResponse {
  success: boolean;
  message: string;
  statusCode: number;
  error?: string;
  details?: Record<string, any>;
  timestamp?: string;
}

// 验证错误详情
export interface ValidationErrorDetail {
  field: string;
  message: string;
  value?: any;
}

// 验证错误响应
export interface ValidationErrorResponse extends ErrorResponse {
  error: 'ValidationError';
  details: {
    errors: ValidationErrorDetail[];
  };
}

// 资源不存在错误响应
export interface NotFoundErrorResponse extends ErrorResponse {
  error: 'NotFoundError';
  details: {
    resource: string;
    id?: string;
  };
}

// 认证错误响应
export interface AuthErrorResponse extends ErrorResponse {
  error: 'AuthenticationError' | 'AuthorizationError';
}

// 业务逻辑错误响应
export interface BusinessErrorResponse extends ErrorResponse {
  error: 'BusinessLogicError';
  details: {
    code: string;
    [key: string]: any;
  };
}

// 服务错误响应
export interface ServiceErrorResponse extends ErrorResponse {
  error: 'ServiceError';
  details: {
    service: string;
    operation: string;
    [key: string]: any;
  };
} 
/**
 * @swagger
 * components:
 *   schemas:
 *     SuccessResponse:
 *       type: object
 *       required:
 *         - success
 *         - message
 *       properties:
 *         success:
 *           type: boolean
 *           description: 操作是否成功
 *           example: true
 *         message:
 *           type: string
 *           description: 操作结果描述
 *           example: "操作成功"
 *         data:
 *           type: object
 *           description: 响应数据，根据API不同而变化
 *     
 *     PaginatedResponse:
 *       type: object
 *       required:
 *         - success
 *         - message
 *         - data
 *       properties:
 *         success:
 *           type: boolean
 *           description: 操作是否成功
 *           example: true
 *         message:
 *           type: string
 *           description: 操作结果描述
 *           example: "查询成功"
 *         data:
 *           type: object
 *           required:
 *             - total
 *             - limit
 *             - offset
 *             - results
 *           properties:
 *             total:
 *               type: integer
 *               description: 总记录数
 *               example: 157
 *             limit:
 *               type: integer
 *               description: 每页记录数
 *               example: 10
 *             offset:
 *               type: integer
 *               description: 分页偏移量
 *               example: 0
 *             results:
 *               type: array
 *               description: 记录列表
 *               items:
 *                 type: object
 *     
 *     ErrorResponse:
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
 *           example: "请求参数错误"
 *         statusCode:
 *           type: integer
 *           description: HTTP状态码
 *           example: 400
 *         error:
 *           type: string
 *           description: 错误类型
 *           example: "ValidationError"
 *         details:
 *           type: object
 *           description: 错误详情
 *         timestamp:
 *           type: string
 *           format: date-time
 *           description: 错误发生时间
 *           example: "2023-04-02T10:30:15.123Z"
 */

// 成功响应接口
export interface SuccessResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

// 分页响应接口
export interface PaginatedResponse<T = any> {
  success: boolean;
  message: string;
  data: {
    total: number;
    limit: number;
    offset: number;
    results: T[];
  };
}

// 错误响应接口
export interface ErrorResponse {
  success: boolean;
  message: string;
  statusCode: number;
  error?: string;
  details?: Record<string, any>;
  timestamp: string;
}

// 分页查询参数
export interface PaginationParams {
  limit?: number;
  offset?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

// 健康检查响应
export interface HealthCheckResponse {
  status: 'UP' | 'DOWN';
  service: string;
  version: string;
  timestamp: string;
  details?: Record<string, any>;
}
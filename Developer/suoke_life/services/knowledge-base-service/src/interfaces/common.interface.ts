/**
 * 通用接口定义
 * @swagger
 * components:
 *   schemas:
 *     ApiResponse:
 *       type: object
 *       required:
 *         - success
 *       properties:
 *         success:
 *           type: boolean
 *           description: 操作是否成功
 *         message:
 *           type: string
 *           description: 操作结果描述
 *         data:
 *           type: object
 *           description: 响应数据
 *         error:
 *           type: string
 *           description: 错误类型（仅在失败时返回）
 *         statusCode:
 *           type: integer
 *           description: HTTP状态码（仅在失败时返回）
 *       example:
 *         success: true
 *         message: "操作成功"
 *         data: {}
 */

/**
 * API响应接口
 */
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
  statusCode?: number;
}

/**
 * 分页请求参数
 */
export interface PaginationQuery {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortDirection?: 'asc' | 'desc';
}

/**
 * 分页响应数据
 * @swagger
 * components:
 *   schemas:
 *     PaginatedResponse:
 *       type: object
 *       properties:
 *         success:
 *           type: boolean
 *           example: true
 *         message:
 *           type: string
 *           example: "查询成功"
 *         data:
 *           type: object
 *           properties:
 *             items:
 *               type: array
 *               items:
 *                 type: object
 *             pagination:
 *               type: object
 *               properties:
 *                 totalItems:
 *                   type: integer
 *                   example: 100
 *                 totalPages:
 *                   type: integer
 *                   example: 10
 *                 currentPage:
 *                   type: integer
 *                   example: 1
 *                 itemsPerPage:
 *                   type: integer
 *                   example: 10
 */
export interface PaginationData<T> {
  items: T[];
  pagination: {
    totalItems: number;
    totalPages: number;
    currentPage: number;
    itemsPerPage: number;
  };
}

/**
 * 文件上传响应
 * @swagger
 * components:
 *   schemas:
 *     FileUploadResponse:
 *       allOf:
 *         - $ref: '#/components/schemas/ApiResponse'
 *         - type: object
 *           properties:
 *             data:
 *               type: object
 *               properties:
 *                 fileUrl:
 *                   type: string
 *                   example: "https://storage.suoke.life/files/example.pdf"
 *                 fileName:
 *                   type: string
 *                   example: "example.pdf"
 *                 fileSize:
 *                   type: integer
 *                   example: 1048576
 *                 mimeType:
 *                   type: string
 *                   example: "application/pdf"
 */
export interface FileUploadResponse {
  fileUrl: string;
  fileName: string;
  fileSize: number;
  mimeType: string;
}

/**
 * 搜索查询参数
 */
export interface SearchQuery extends PaginationQuery {
  keyword?: string;
  tags?: string[];
  categories?: string[];
  startDate?: string;
  endDate?: string;
}

/**
 * 审核状态枚举
 * @swagger
 * components:
 *   schemas:
 *     ReviewStatus:
 *       type: string
 *       enum:
 *         - draft
 *         - pending
 *         - approved
 *         - rejected
 */
export enum ReviewStatus {
  DRAFT = 'draft',
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected'
}
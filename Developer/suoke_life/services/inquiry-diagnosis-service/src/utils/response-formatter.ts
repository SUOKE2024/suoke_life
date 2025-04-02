import { ErrorResponse, PaginatedResponse, SuccessResponse } from '../interfaces/common.interface';

/**
 * 格式化成功响应
 * @param data 响应数据
 * @param message 响应消息
 * @returns 格式化的成功响应对象
 */
export const formatSuccess = <T = any>(data?: T, message: string = '操作成功'): SuccessResponse<T> => {
  return {
    success: true,
    message,
    data
  };
};

/**
 * 格式化分页响应
 * @param total 总记录数
 * @param results 当前页数据
 * @param limit 每页记录数
 * @param offset 偏移量
 * @param message 响应消息
 * @returns 格式化的分页响应对象
 */
export const formatPagination = <T = any>(
  total: number, 
  results: T[], 
  limit: number = 10, 
  offset: number = 0, 
  message: string = '查询成功'
): PaginatedResponse<T> => {
  return {
    success: true,
    message,
    data: {
      total,
      limit,
      offset,
      results
    }
  };
};

/**
 * 格式化错误响应
 * @param message 错误消息
 * @param statusCode HTTP状态码
 * @param error 错误类型
 * @param details 错误详情
 * @returns 格式化的错误响应对象
 */
export const formatError = (
  message: string,
  statusCode: number = 500,
  error?: string,
  details?: Record<string, any>
): ErrorResponse => {
  return {
    success: false,
    message,
    statusCode,
    error,
    details,
    timestamp: new Date().toISOString()
  };
};

export default {
  formatSuccess,
  formatPagination,
  formatError
};
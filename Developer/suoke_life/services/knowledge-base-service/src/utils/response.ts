/**
 * 响应工具函数
 * 提供统一格式的API响应
 */
import { Response } from 'express';
import { ApiResponse, PaginationData } from '../interfaces/common.interface';

/**
 * 成功响应
 * @param res Express响应对象
 * @param data 响应数据
 * @param message 成功消息
 * @param statusCode HTTP状态码
 */
export const successResponse = <T>(
  res: Response,
  data: T = {} as T,
  message = '操作成功',
  statusCode = 200
): void => {
  const response: ApiResponse<T> = {
    success: true,
    message,
    data
  };
  res.status(statusCode).json(response);
};

/**
 * 错误响应
 * @param res Express响应对象
 * @param message 错误消息
 * @param error 错误类型
 * @param statusCode HTTP状态码
 */
export const errorResponse = (
  res: Response,
  message = '操作失败',
  error = 'InternalServerError',
  statusCode = 500
): void => {
  const response: ApiResponse = {
    success: false,
    message,
    error,
    statusCode
  };
  res.status(statusCode).json(response);
};

/**
 * 分页响应
 * @param res Express响应对象
 * @param data 分页数据
 * @param message 成功消息
 */
export const paginatedResponse = <T>(
  res: Response,
  data: PaginationData<T>,
  message = '查询成功'
): void => {
  const response: ApiResponse<PaginationData<T>> = {
    success: true,
    message,
    data
  };
  res.status(200).json(response);
};

/**
 * 创建成功响应
 * @param res Express响应对象
 * @param data 创建的数据
 * @param message 成功消息
 */
export const createdResponse = <T>(
  res: Response,
  data: T,
  message = '创建成功'
): void => {
  const response: ApiResponse<T> = {
    success: true,
    message,
    data
  };
  res.status(201).json(response);
};

/**
 * 无内容响应
 * @param res Express响应对象
 * @param message 成功消息
 */
export const noContentResponse = (
  res: Response,
  message = '操作成功'
): void => {
  res.status(204).send();
};
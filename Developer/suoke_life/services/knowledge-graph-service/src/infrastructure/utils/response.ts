import { FastifyReply } from 'fastify';
import { PaginatedData } from '../../domain/interfaces/api-response.interface';

/**
 * 发送成功响应
 * @param reply Fastify响应对象
 * @param data 响应数据
 * @param message 成功消息
 * @param statusCode HTTP状态码
 * @returns FastifyReply
 */
export const sendSuccessResponse = (
  reply: FastifyReply,
  data: any,
  message: string = '操作成功',
  statusCode: number = 200
): FastifyReply => {
  return reply.code(statusCode).send({
    success: true,
    message,
    data,
    timestamp: new Date().toISOString()
  });
};

/**
 * 发送创建成功响应
 * @param reply Fastify响应对象
 * @param data 响应数据
 * @param message 成功消息
 * @returns FastifyReply
 */
export const sendCreatedResponse = (
  reply: FastifyReply,
  data: any,
  message: string = '创建成功'
): FastifyReply => {
  return sendSuccessResponse(reply, data, message, 201);
};

/**
 * 发送无内容成功响应
 * @param reply Fastify响应对象
 * @returns FastifyReply
 */
export const sendNoContentResponse = (reply: FastifyReply): FastifyReply => {
  return reply.code(204).send();
};

/**
 * 发送分页响应
 * @param reply Fastify响应对象
 * @param data 分页数据
 * @param message 成功消息
 * @returns FastifyReply
 */
export const sendPaginatedResponse = <T>(
  reply: FastifyReply,
  data: PaginatedData<T>,
  message: string = '查询成功'
): FastifyReply => {
  return reply.code(200).send({
    success: true,
    message,
    data,
    timestamp: new Date().toISOString()
  });
};

/**
 * 发送错误响应
 * @param reply Fastify响应对象
 * @param message 错误消息
 * @param error 错误类型
 * @param statusCode HTTP状态码
 * @returns FastifyReply
 */
export const sendErrorResponse = (
  reply: FastifyReply,
  message: string,
  error: string = 'InternalServerError',
  statusCode: number = 500
): FastifyReply => {
  return reply.code(statusCode).send({
    success: false,
    message,
    error,
    statusCode,
    timestamp: new Date().toISOString()
  });
};

/**
 * 发送验证错误响应
 * @param reply Fastify响应对象
 * @param message 错误消息
 * @param details 验证错误详情
 * @returns FastifyReply
 */
export const sendValidationErrorResponse = (
  reply: FastifyReply,
  message: string = '请求参数验证失败',
  details: any[] = []
): FastifyReply => {
  return reply.code(400).send({
    success: false,
    message,
    error: 'ValidationError',
    statusCode: 400,
    details,
    timestamp: new Date().toISOString()
  });
};

/**
 * 发送未授权错误响应
 * @param reply Fastify响应对象
 * @param message 错误消息
 * @returns FastifyReply
 */
export const sendUnauthorizedResponse = (
  reply: FastifyReply,
  message: string = '未授权访问'
): FastifyReply => {
  return sendErrorResponse(reply, message, 'UnauthorizedError', 401);
};

/**
 * 发送禁止访问错误响应
 * @param reply Fastify响应对象
 * @param message 错误消息
 * @returns FastifyReply
 */
export const sendForbiddenResponse = (
  reply: FastifyReply,
  message: string = '禁止访问'
): FastifyReply => {
  return sendErrorResponse(reply, message, 'ForbiddenError', 403);
};

/**
 * 发送资源不存在错误响应
 * @param reply Fastify响应对象
 * @param message 错误消息
 * @returns FastifyReply
 */
export const sendNotFoundResponse = (
  reply: FastifyReply,
  message: string = '资源不存在'
): FastifyReply => {
  return sendErrorResponse(reply, message, 'NotFoundError', 404);
};

/**
 * 发送冲突错误响应
 * @param reply Fastify响应对象
 * @param message 错误消息
 * @returns FastifyReply
 */
export const sendConflictResponse = (
  reply: FastifyReply,
  message: string = '资源冲突'
): FastifyReply => {
  return sendErrorResponse(reply, message, 'ConflictError', 409);
};

/**
 * 发送请求超时错误响应
 * @param reply Fastify响应对象
 * @param message 错误消息
 * @returns FastifyReply
 */
export const sendTimeoutResponse = (
  reply: FastifyReply,
  message: string = '请求超时'
): FastifyReply => {
  return sendErrorResponse(reply, message, 'TimeoutError', 408);
};

/**
 * 发送服务不可用错误响应
 * @param reply Fastify响应对象
 * @param message 错误消息
 * @returns FastifyReply
 */
export const sendServiceUnavailableResponse = (
  reply: FastifyReply,
  message: string = '服务暂时不可用'
): FastifyReply => {
  return sendErrorResponse(reply, message, 'ServiceUnavailableError', 503);
};
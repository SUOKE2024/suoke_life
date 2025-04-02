"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.requestLoggerMiddleware = void 0;
const logger_1 = require("../../utils/logger");
/**
 * 请求日志中间件
 * 记录所有进入的HTTP请求信息
 */
const requestLoggerMiddleware = (req, res, next) => {
    const startTime = Date.now();
    // 为保护隐私，过滤敏感信息
    const filteredHeaders = { ...req.headers };
    if (filteredHeaders.authorization) {
        filteredHeaders.authorization = 'Bearer [FILTERED]';
    }
    // 请求开始日志
    logger_1.requestLogger.info('收到请求', {
        method: req.method,
        url: req.url,
        ip: req.ip,
        query: req.query,
        headers: filteredHeaders,
        requestId: req.headers['x-request-id'] || '',
        userAgent: req.headers['user-agent'] || ''
    });
    // 响应结束后的处理
    res.on('finish', () => {
        const duration = Date.now() - startTime;
        // 请求完成日志
        logger_1.requestLogger.info('请求完成', {
            method: req.method,
            url: req.url,
            statusCode: res.statusCode,
            duration: `${duration}ms`,
            requestId: req.headers['x-request-id'] || '',
            contentLength: res.getHeader('content-length') || 0
        });
    });
    next();
};
exports.requestLoggerMiddleware = requestLoggerMiddleware;

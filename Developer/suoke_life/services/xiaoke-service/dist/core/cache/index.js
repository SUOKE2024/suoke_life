"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deleteCacheByPattern = exports.deleteCache = exports.getCache = exports.setCache = exports.closeRedisConnection = exports.getRedisClient = exports.setupRedisClient = void 0;
const ioredis_1 = __importDefault(require("ioredis"));
const logger_1 = require("../../utils/logger");
let redisClient = null;
/**
 * 设置Redis客户端
 */
const setupRedisClient = async () => {
    try {
        if (redisClient) {
            return redisClient;
        }
        // 获取Redis连接配置
        const host = process.env.REDIS_HOST || 'localhost';
        const port = parseInt(process.env.REDIS_PORT || '6379', 10);
        const password = process.env.REDIS_PASSWORD || undefined;
        // 创建Redis客户端
        redisClient = new ioredis_1.default({
            host,
            port,
            password,
            lazyConnect: true,
            retryStrategy: (times) => {
                const delay = Math.min(times * 50, 2000);
                logger_1.logger.info(`Redis重连延迟: ${delay}ms`);
                return delay;
            }
        });
        // 连接Redis
        await redisClient.connect();
        // 设置事件监听器
        redisClient.on('connect', () => {
            logger_1.logger.info('Redis连接已建立');
        });
        redisClient.on('ready', () => {
            logger_1.logger.info('Redis服务器已就绪');
        });
        redisClient.on('error', (err) => {
            logger_1.logger.error('Redis错误:', err);
        });
        redisClient.on('close', () => {
            logger_1.logger.warn('Redis连接已关闭');
        });
        redisClient.on('reconnecting', () => {
            logger_1.logger.info('正在重新连接到Redis...');
        });
        return redisClient;
    }
    catch (error) {
        logger_1.logger.error('Redis连接失败:', error);
        throw error;
    }
};
exports.setupRedisClient = setupRedisClient;
/**
 * 获取Redis客户端实例
 */
const getRedisClient = () => {
    if (!redisClient) {
        throw new Error('Redis客户端未初始化');
    }
    return redisClient;
};
exports.getRedisClient = getRedisClient;
/**
 * 关闭Redis连接
 */
const closeRedisConnection = async () => {
    if (redisClient) {
        await redisClient.quit();
        redisClient = null;
        logger_1.logger.info('Redis连接已关闭');
    }
};
exports.closeRedisConnection = closeRedisConnection;
/**
 * 缓存帮助函数
 */
/**
 * 设置缓存
 */
const setCache = async (key, value, ttl) => {
    try {
        const client = (0, exports.getRedisClient)();
        const serializedValue = JSON.stringify(value);
        if (ttl) {
            await client.set(key, serializedValue, 'EX', ttl);
        }
        else {
            await client.set(key, serializedValue);
        }
    }
    catch (error) {
        logger_1.logger.error(`设置缓存[${key}]失败:`, error);
        throw error;
    }
};
exports.setCache = setCache;
/**
 * 获取缓存
 */
const getCache = async (key) => {
    try {
        const client = (0, exports.getRedisClient)();
        const value = await client.get(key);
        if (!value) {
            return null;
        }
        return JSON.parse(value);
    }
    catch (error) {
        logger_1.logger.error(`获取缓存[${key}]失败:`, error);
        return null;
    }
};
exports.getCache = getCache;
/**
 * 删除缓存
 */
const deleteCache = async (key) => {
    try {
        const client = (0, exports.getRedisClient)();
        await client.del(key);
    }
    catch (error) {
        logger_1.logger.error(`删除缓存[${key}]失败:`, error);
        throw error;
    }
};
exports.deleteCache = deleteCache;
/**
 * 使用模式匹配删除多个缓存
 */
const deleteCacheByPattern = async (pattern) => {
    try {
        const client = (0, exports.getRedisClient)();
        const keys = await client.keys(pattern);
        if (keys.length > 0) {
            await client.del(...keys);
            logger_1.logger.info(`已删除${keys.length}个匹配模式[${pattern}]的缓存`);
        }
    }
    catch (error) {
        logger_1.logger.error(`删除缓存模式[${pattern}]失败:`, error);
        throw error;
    }
};
exports.deleteCacheByPattern = deleteCacheByPattern;
exports.default = {
    setup: exports.setupRedisClient,
    getClient: exports.getRedisClient,
    close: exports.closeRedisConnection,
    set: exports.setCache,
    get: exports.getCache,
    delete: exports.deleteCache,
    deleteByPattern: exports.deleteCacheByPattern
};

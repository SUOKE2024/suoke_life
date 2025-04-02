"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.releaseMemory = exports.cleanupSessions = exports.loadSession = exports.getSessionMetadata = exports.setSessionMetadata = exports.searchMemory = exports.clearSession = exports.getMessages = exports.addMessage = exports.initializeAgentMemory = void 0;
const logger_1 = require("../../utils/logger");
const models_1 = require("./models");
// 会话缓存，用于存储会话历史
const sessions = {};
// 记忆持久化
let memoryPersistence = null;
// 向量存储
let vectorStore = null;
/**
 * 初始化智能体记忆系统
 * @param config 智能体配置
 */
const initializeAgentMemory = async (config) => {
    try {
        logger_1.logger.info('初始化智能体记忆系统...');
        // 如果配置了持久化，初始化持久化
        if (process.env.MEMORY_PERSISTENCE === 'true') {
            await initializeMemoryPersistence();
        }
        // 初始化向量存储，用于语义搜索
        await initializeVectorStore(config);
        logger_1.logger.info('智能体记忆系统初始化完成');
    }
    catch (error) {
        logger_1.logger.error('智能体记忆系统初始化失败:', error);
        throw error;
    }
};
exports.initializeAgentMemory = initializeAgentMemory;
/**
 * 初始化记忆持久化
 */
const initializeMemoryPersistence = async () => {
    try {
        logger_1.logger.info('初始化记忆持久化...');
        // 动态加载持久化实现
        const persistenceModule = await Promise.resolve().then(() => __importStar(require('../../services/memory/persistence')));
        memoryPersistence = new persistenceModule.MemoryPersistence();
        await memoryPersistence.initialize();
        logger_1.logger.info('记忆持久化初始化完成');
    }
    catch (error) {
        logger_1.logger.error('记忆持久化初始化失败:', error);
        throw error;
    }
};
/**
 * 初始化向量存储
 * @param config 智能体配置
 */
const initializeVectorStore = async (config) => {
    try {
        logger_1.logger.info('初始化向量存储...');
        // 获取嵌入模型
        const embeddingModel = (0, models_1.getModel)('embedding');
        if (!embeddingModel) {
            logger_1.logger.warn('未找到嵌入模型，跳过向量存储初始化');
            return;
        }
        // 动态加载向量存储实现
        const vectorStoreModule = await Promise.resolve().then(() => __importStar(require('../../services/memory/vector-store')));
        vectorStore = new vectorStoreModule.VectorStore(embeddingModel);
        await vectorStore.initialize();
        logger_1.logger.info('向量存储初始化完成');
    }
    catch (error) {
        logger_1.logger.error('向量存储初始化失败:', error);
        // 这里我们不抛出错误，因为向量存储不是必需的
        logger_1.logger.warn('将继续而不使用向量存储');
    }
};
/**
 * 添加消息到会话
 * @param sessionId 会话ID
 * @param message 消息
 */
const addMessage = async (sessionId, message) => {
    // 确保会话存在
    if (!sessions[sessionId]) {
        sessions[sessionId] = {
            messages: [],
            metadata: {},
            lastUpdated: Date.now()
        };
    }
    // 添加消息
    sessions[sessionId].messages.push(message);
    sessions[sessionId].lastUpdated = Date.now();
    // 如果启用了向量存储，将消息添加到向量存储
    if (vectorStore && message.role === 'user') {
        try {
            await vectorStore.addText(message.content, {
                messageId: message.id,
                sessionId,
                timestamp: message.timestamp
            });
        }
        catch (error) {
            logger_1.logger.error('向量存储添加消息失败:', error);
        }
    }
    // 如果启用了持久化，将消息持久化
    if (memoryPersistence) {
        try {
            await memoryPersistence.saveSession(sessionId, sessions[sessionId]);
        }
        catch (error) {
            logger_1.logger.error('会话持久化失败:', error);
        }
    }
};
exports.addMessage = addMessage;
/**
 * 获取会话历史
 * @param sessionId 会话ID
 * @param limit 限制消息数量，默认不限制
 */
const getMessages = (sessionId, limit) => {
    const session = sessions[sessionId];
    if (!session) {
        return [];
    }
    const messages = session.messages;
    if (limit && limit > 0 && messages.length > limit) {
        return messages.slice(messages.length - limit);
    }
    return [...messages];
};
exports.getMessages = getMessages;
/**
 * 清除会话历史
 * @param sessionId 会话ID
 */
const clearSession = async (sessionId) => {
    if (sessions[sessionId]) {
        delete sessions[sessionId];
        // 如果启用了持久化，从持久化中删除会话
        if (memoryPersistence) {
            try {
                await memoryPersistence.deleteSession(sessionId);
            }
            catch (error) {
                logger_1.logger.error('删除会话持久化失败:', error);
            }
        }
    }
};
exports.clearSession = clearSession;
/**
 * 根据查询获取相关记忆
 * @param query 查询
 * @param sessionId 会话ID (可选)
 * @param limit 限制结果数量
 */
const searchMemory = async (query, sessionId, limit = 5) => {
    if (!vectorStore) {
        logger_1.logger.warn('向量存储未初始化，无法搜索记忆');
        return [];
    }
    try {
        const results = await vectorStore.search(query, limit, sessionId ? { sessionId } : undefined);
        return results.map(result => ({
            id: result.metadata.messageId,
            role: 'user',
            content: result.text,
            timestamp: result.metadata.timestamp
        }));
    }
    catch (error) {
        logger_1.logger.error('搜索记忆失败:', error);
        return [];
    }
};
exports.searchMemory = searchMemory;
/**
 * 设置会话元数据
 * @param sessionId 会话ID
 * @param key 元数据键
 * @param value 元数据值
 */
const setSessionMetadata = async (sessionId, key, value) => {
    // 确保会话存在
    if (!sessions[sessionId]) {
        sessions[sessionId] = {
            messages: [],
            metadata: {},
            lastUpdated: Date.now()
        };
    }
    // 设置元数据
    sessions[sessionId].metadata[key] = value;
    sessions[sessionId].lastUpdated = Date.now();
    // 如果启用了持久化，更新持久化
    if (memoryPersistence) {
        try {
            await memoryPersistence.saveSession(sessionId, sessions[sessionId]);
        }
        catch (error) {
            logger_1.logger.error('更新会话元数据持久化失败:', error);
        }
    }
};
exports.setSessionMetadata = setSessionMetadata;
/**
 * 获取会话元数据
 * @param sessionId 会话ID
 * @param key 元数据键
 */
const getSessionMetadata = (sessionId, key) => {
    const session = sessions[sessionId];
    if (!session || !session.metadata[key]) {
        return null;
    }
    return session.metadata[key];
};
exports.getSessionMetadata = getSessionMetadata;
/**
 * 加载会话
 * @param sessionId 会话ID
 */
const loadSession = async (sessionId) => {
    if (!memoryPersistence) {
        logger_1.logger.warn('记忆持久化未初始化，无法加载会话');
        return false;
    }
    try {
        const session = await memoryPersistence.loadSession(sessionId);
        if (session) {
            sessions[sessionId] = session;
            return true;
        }
        return false;
    }
    catch (error) {
        logger_1.logger.error('加载会话失败:', error);
        return false;
    }
};
exports.loadSession = loadSession;
/**
 * 清理过期会话
 * @param maxAge 最大会话年龄(毫秒)，默认24小时
 */
const cleanupSessions = async (maxAge = 24 * 60 * 60 * 1000) => {
    const now = Date.now();
    const expiredSessionIds = [];
    for (const sessionId in sessions) {
        if (now - sessions[sessionId].lastUpdated > maxAge) {
            expiredSessionIds.push(sessionId);
        }
    }
    for (const sessionId of expiredSessionIds) {
        await (0, exports.clearSession)(sessionId);
    }
    if (expiredSessionIds.length > 0) {
        logger_1.logger.info(`已清理 ${expiredSessionIds.length} 个过期会话`);
    }
};
exports.cleanupSessions = cleanupSessions;
/**
 * 释放记忆资源
 */
const releaseMemory = async () => {
    try {
        logger_1.logger.info('释放记忆资源...');
        if (memoryPersistence) {
            await memoryPersistence.close();
            memoryPersistence = null;
        }
        if (vectorStore) {
            await vectorStore.close();
            vectorStore = null;
        }
        logger_1.logger.info('记忆资源已释放');
    }
    catch (error) {
        logger_1.logger.error('释放记忆资源失败:', error);
    }
};
exports.releaseMemory = releaseMemory;

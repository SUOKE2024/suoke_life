"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.KnowledgeGraphServiceImpl = void 0;
/**
 * 知识图谱服务实现
 */
const axios_1 = __importDefault(require("axios"));
const logger_1 = require("../../utils/logger");
const cache_1 = require("../../core/cache");
const config_1 = __importDefault(require("../../config"));
/**
 * 知识图谱服务实现类
 */
class KnowledgeGraphServiceImpl {
    constructor() {
        this.logger = new logger_1.Logger('KnowledgeGraphService');
        this.isInitialized = false;
        this.cache = new Map();
        /**
         * 缓存过期时间(毫秒)
         */
        this.CACHE_TTL = 60 * 60 * 1000; // 1小时
        /**
         * 节点缓存键前缀
         */
        this.NODE_CACHE_PREFIX = 'kg_node_';
        /**
         * 关系缓存键前缀
         */
        this.RELATION_CACHE_PREFIX = 'kg_relation_';
        /**
         * 路径缓存键前缀
         */
        this.PATH_CACHE_PREFIX = 'kg_path_';
        /**
         * 查询缓存键前缀
         */
        this.QUERY_CACHE_PREFIX = 'kg_query_';
        /**
         * 产品概念缓存键前缀
         */
        this.PRODUCT_CONCEPTS_PREFIX = 'kg_product_concepts_';
        /**
         * 产品知识缓存键前缀
         */
        this.PRODUCT_KNOWLEDGE_PREFIX = 'kg_product_knowledge_';
        this.cacheService = new cache_1.CacheService();
        this.apiEndpoint = config_1.default.KNOWLEDGE_GRAPH_URL || 'http://localhost:3003/api/graph';
    }
    /**
     * 初始化服务
     */
    async initialize() {
        this.logger.info('初始化知识图谱服务');
        try {
            // 验证API连接
            await axios_1.default.get(`${this.apiEndpoint}/health`);
            this.isInitialized = true;
            this.logger.info('知识图谱服务初始化完成');
        }
        catch (error) {
            this.logger.error('知识图谱服务初始化失败', error);
            // 设置重试逻辑
            setTimeout(() => this.initialize(), 10000); // 10秒后重试
        }
    }
    /**
     * 关闭服务
     */
    async shutdown() {
        this.logger.info('关闭知识图谱服务');
        this.isInitialized = false;
        this.cache.clear();
    }
    /**
     * 检查服务状态
     */
    checkServiceReady() {
        if (!this.isInitialized) {
            throw new Error('知识图谱服务未初始化');
        }
    }
    /**
     * 生成缓存键
     */
    getCacheKey(prefix, key, params) {
        if (params) {
            return `${prefix}${key}_${JSON.stringify(params)}`;
        }
        return `${prefix}${key}`;
    }
    /**
     * 从缓存获取数据
     */
    getFromCache(key) {
        const cachedItem = this.cache.get(key);
        if (cachedItem && cachedItem.expiry > Date.now()) {
            return cachedItem.data;
        }
        this.cache.delete(key);
        return null;
    }
    /**
     * 存入缓存
     */
    setToCache(key, data, ttl = this.CACHE_TTL) {
        this.cache.set(key, {
            data,
            expiry: Date.now() + ttl
        });
    }
    /**
     * 执行图谱查询
     */
    async query(query) {
        this.checkServiceReady();
        // 生成缓存键
        const cacheKey = this.getCacheKey(this.QUERY_CACHE_PREFIX, query);
        // 检查缓存
        const cachedResult = this.getFromCache(cacheKey);
        if (cachedResult) {
            this.logger.debug(`使用缓存的图谱查询: ${query}`);
            return cachedResult;
        }
        try {
            this.logger.debug(`执行图谱查询: ${query}`);
            const response = await axios_1.default.post(`${this.apiEndpoint}/query`, { query });
            const result = response.data;
            // 保存到缓存
            this.setToCache(cacheKey, result);
            return result;
        }
        catch (error) {
            this.logger.error(`图谱查询失败: ${query}`, error);
            throw new Error(`图谱查询失败: ${error.message}`);
        }
    }
    /**
     * 搜索图谱节点
     */
    async searchNodes(query) {
        this.checkServiceReady();
        try {
            this.logger.debug(`搜索图谱节点: ${query}`);
            const response = await axios_1.default.get(`${this.apiEndpoint}/nodes/search`, {
                params: { query }
            });
            return response.data;
        }
        catch (error) {
            this.logger.error(`搜索图谱节点失败: ${query}`, error);
            throw new Error(`搜索图谱节点失败: ${error.message}`);
        }
    }
    /**
     * 获取节点关系
     */
    async getNodeRelations(nodeId) {
        this.checkServiceReady();
        // 生成缓存键
        const cacheKey = this.getCacheKey(this.RELATION_CACHE_PREFIX, nodeId);
        // 检查缓存
        const cachedRelations = this.getFromCache(cacheKey);
        if (cachedRelations) {
            this.logger.debug(`使用缓存的节点关系: ${nodeId}`);
            return cachedRelations;
        }
        try {
            this.logger.debug(`获取节点关系: ${nodeId}`);
            const response = await axios_1.default.get(`${this.apiEndpoint}/nodes/${nodeId}/relations`);
            const relations = response.data;
            // 保存到缓存
            this.setToCache(cacheKey, relations);
            return relations;
        }
        catch (error) {
            this.logger.error(`获取节点关系失败: ${nodeId}`, error);
            throw new Error(`获取节点关系失败: ${error.message}`);
        }
    }
    /**
     * 查找最短路径
     */
    async findShortestPath(fromId, toId) {
        this.checkServiceReady();
        // 生成缓存键
        const cacheKey = this.getCacheKey(this.PATH_CACHE_PREFIX, `${fromId}_${toId}`);
        // 检查缓存
        const cachedPath = this.getFromCache(cacheKey);
        if (cachedPath) {
            this.logger.debug(`使用缓存的路径: ${fromId} -> ${toId}`);
            return cachedPath;
        }
        try {
            this.logger.debug(`查找路径: ${fromId} -> ${toId}`);
            const response = await axios_1.default.get(`${this.apiEndpoint}/path`, {
                params: { fromId, toId }
            });
            const pathResult = response.data;
            // 保存到缓存
            this.setToCache(cacheKey, pathResult);
            return pathResult;
        }
        catch (error) {
            this.logger.error(`查找路径失败: ${fromId} -> ${toId}`, error);
            throw new Error(`查找路径失败: ${error.message}`);
        }
    }
    /**
     * 获取产品关联概念
     */
    async getProductConcepts(productId) {
        this.checkServiceReady();
        // 生成缓存键
        const cacheKey = this.getCacheKey(this.PRODUCT_CONCEPTS_PREFIX, productId);
        // 检查缓存
        const cachedConcepts = this.getFromCache(cacheKey);
        if (cachedConcepts) {
            this.logger.debug(`使用缓存的产品概念: ${productId}`);
            return cachedConcepts;
        }
        try {
            this.logger.debug(`获取产品概念: ${productId}`);
            const response = await axios_1.default.get(`${this.apiEndpoint}/products/${productId}/concepts`);
            const concepts = response.data;
            // 保存到缓存
            this.setToCache(cacheKey, concepts);
            return concepts;
        }
        catch (error) {
            this.logger.error(`获取产品概念失败: ${productId}`, error);
            throw new Error(`获取产品概念失败: ${error.message}`);
        }
    }
    /**
     * 获取农产品相关知识
     */
    async getProductKnowledge(productId) {
        this.checkServiceReady();
        // 生成缓存键
        const cacheKey = this.getCacheKey(this.PRODUCT_KNOWLEDGE_PREFIX, productId);
        // 检查缓存
        const cachedKnowledge = this.getFromCache(cacheKey);
        if (cachedKnowledge) {
            this.logger.debug(`使用缓存的产品知识: ${productId}`);
            return cachedKnowledge;
        }
        try {
            this.logger.debug(`获取产品知识: ${productId}`);
            const response = await axios_1.default.get(`${this.apiEndpoint}/products/${productId}/knowledge`);
            const knowledge = response.data;
            // 保存到缓存
            this.setToCache(cacheKey, knowledge);
            return knowledge;
        }
        catch (error) {
            this.logger.error(`获取产品知识失败: ${productId}`, error);
            throw new Error(`获取产品知识失败: ${error.message}`);
        }
    }
}
exports.KnowledgeGraphServiceImpl = KnowledgeGraphServiceImpl;

"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.KnowledgeBaseServiceImpl = void 0;
/**
 * 知识库服务实现
 */
const axios_1 = __importDefault(require("axios"));
const logger_1 = require("../../utils/logger");
const cache_1 = require("../../core/cache");
const config_1 = __importDefault(require("../../config"));
/**
 * 知识库服务实现类
 */
class KnowledgeBaseServiceImpl {
    constructor() {
        this.logger = new logger_1.Logger('KnowledgeBaseService');
        this.isInitialized = false;
        this.cache = new Map();
        /**
         * 缓存过期时间(毫秒)
         */
        this.CACHE_TTL = 30 * 60 * 1000; // 30分钟
        /**
         * 搜索缓存键前缀
         */
        this.SEARCH_CACHE_PREFIX = 'kb_search_';
        /**
         * 知识条目缓存键前缀
         */
        this.ITEM_CACHE_PREFIX = 'kb_item_';
        /**
         * 分类条目缓存键前缀
         */
        this.CATEGORY_CACHE_PREFIX = 'kb_category_';
        /**
         * 标签条目缓存键前缀
         */
        this.TAG_CACHE_PREFIX = 'kb_tag_';
        this.cacheService = new cache_1.CacheService();
        this.apiEndpoint = config_1.default.KNOWLEDGE_SERVICE_URL || 'http://localhost:3002/api/knowledge';
    }
    /**
     * 初始化服务
     */
    async initialize() {
        this.logger.info('初始化知识库服务');
        try {
            // 验证API连接
            await axios_1.default.get(`${this.apiEndpoint}/health`);
            this.isInitialized = true;
            this.logger.info('知识库服务初始化完成');
        }
        catch (error) {
            this.logger.error('知识库服务初始化失败', error);
            // 设置重试逻辑
            setTimeout(() => this.initialize(), 10000); // 10秒后重试
        }
    }
    /**
     * 关闭服务
     */
    async shutdown() {
        this.logger.info('关闭知识库服务');
        this.isInitialized = false;
        this.cache.clear();
    }
    /**
     * 检查服务状态
     */
    checkServiceReady() {
        if (!this.isInitialized) {
            throw new Error('知识库服务未初始化');
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
     * 搜索知识库
     */
    async search(query, options) {
        this.checkServiceReady();
        // 生成缓存键
        const cacheKey = this.getCacheKey(this.SEARCH_CACHE_PREFIX, query, options);
        // 检查缓存
        const cachedResult = this.getFromCache(cacheKey);
        if (cachedResult) {
            this.logger.debug(`使用缓存的搜索结果: ${query}`);
            return cachedResult;
        }
        try {
            this.logger.debug(`执行知识库搜索: ${query}`);
            const startTime = Date.now();
            const response = await axios_1.default.post(`${this.apiEndpoint}/search`, {
                query,
                options
            });
            const result = {
                ...response.data,
                timeTaken: Date.now() - startTime
            };
            // 保存到缓存
            this.setToCache(cacheKey, result);
            return result;
        }
        catch (error) {
            this.logger.error(`知识库搜索失败: ${query}`, error);
            throw new Error(`知识库搜索失败: ${error.message}`);
        }
    }
    /**
     * 获取知识条目
     */
    async getItem(id) {
        this.checkServiceReady();
        // 生成缓存键
        const cacheKey = this.getCacheKey(this.ITEM_CACHE_PREFIX, id);
        // 检查缓存
        const cachedItem = this.getFromCache(cacheKey);
        if (cachedItem) {
            this.logger.debug(`使用缓存的知识条目: ${id}`);
            return cachedItem;
        }
        try {
            this.logger.debug(`获取知识条目: ${id}`);
            const response = await axios_1.default.get(`${this.apiEndpoint}/items/${id}`);
            const item = response.data;
            // 保存到缓存
            this.setToCache(cacheKey, item);
            return item;
        }
        catch (error) {
            this.logger.error(`获取知识条目失败: ${id}`, error);
            throw new Error(`获取知识条目失败: ${error.message}`);
        }
    }
    /**
     * 按分类获取知识条目
     */
    async getItemsByCategory(category, limit = 20) {
        this.checkServiceReady();
        // 生成缓存键
        const cacheKey = this.getCacheKey(this.CATEGORY_CACHE_PREFIX, category, { limit });
        // 检查缓存
        const cachedItems = this.getFromCache(cacheKey);
        if (cachedItems) {
            this.logger.debug(`使用缓存的分类条目: ${category}`);
            return cachedItems;
        }
        try {
            this.logger.debug(`获取分类条目: ${category}`);
            const response = await axios_1.default.get(`${this.apiEndpoint}/categories/${category}`, {
                params: { limit }
            });
            const items = response.data;
            // 保存到缓存
            this.setToCache(cacheKey, items);
            return items;
        }
        catch (error) {
            this.logger.error(`获取分类条目失败: ${category}`, error);
            throw new Error(`获取分类条目失败: ${error.message}`);
        }
    }
    /**
     * 按标签获取知识条目
     */
    async getItemsByTag(tag, limit = 20) {
        this.checkServiceReady();
        // 生成缓存键
        const cacheKey = this.getCacheKey(this.TAG_CACHE_PREFIX, tag, { limit });
        // 检查缓存
        const cachedItems = this.getFromCache(cacheKey);
        if (cachedItems) {
            this.logger.debug(`使用缓存的标签条目: ${tag}`);
            return cachedItems;
        }
        try {
            this.logger.debug(`获取标签条目: ${tag}`);
            const response = await axios_1.default.get(`${this.apiEndpoint}/tags/${tag}`, {
                params: { limit }
            });
            const items = response.data;
            // 保存到缓存
            this.setToCache(cacheKey, items);
            return items;
        }
        catch (error) {
            this.logger.error(`获取标签条目失败: ${tag}`, error);
            throw new Error(`获取标签条目失败: ${error.message}`);
        }
    }
}
exports.KnowledgeBaseServiceImpl = KnowledgeBaseServiceImpl;

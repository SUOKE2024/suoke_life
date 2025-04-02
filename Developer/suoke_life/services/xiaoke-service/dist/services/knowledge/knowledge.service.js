"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.KnowledgeService = void 0;
const axios_1 = __importDefault(require("axios"));
const logger_1 = require("../../utils/logger");
const cache_1 = require("../../core/cache");
/**
 * 知识服务 - 集成知识库和知识图谱功能
 * 为xiaoke-service提供知识查询和集成能力
 */
class KnowledgeService {
    constructor() {
        this.cacheTTL = 60 * 60; // 缓存1小时
        this.knowledgeBaseUrl = process.env.KNOWLEDGE_BASE_URL || 'http://knowledge-base-service:3000';
        this.knowledgeGraphUrl = process.env.KNOWLEDGE_GRAPH_URL || 'http://knowledge-graph-service:3010';
        logger_1.logger.info('知识服务已初始化');
    }
    /**
     * 根据关键词搜索相关农产品知识
     * @param keywords 关键词
     * @param limit 结果数量限制
     */
    async searchProductKnowledge(keywords, limit = 10) {
        const cacheKey = `product_knowledge:${keywords}:${limit}`;
        // 尝试从缓存获取数据
        const cachedData = await cache_1.redisClient.get(cacheKey);
        if (cachedData) {
            logger_1.logger.debug(`从缓存获取产品知识: ${keywords}`);
            return JSON.parse(cachedData);
        }
        try {
            // 调用知识库服务搜索API
            const response = await axios_1.default.get(`${this.knowledgeBaseUrl}/api/search`, {
                params: {
                    query: keywords,
                    category: 'agricultural_products',
                    limit
                }
            });
            // 缓存结果
            if (response.data && response.data.results) {
                await cache_1.redisClient.set(cacheKey, JSON.stringify(response.data.results), 'EX', this.cacheTTL);
            }
            return response.data.results;
        }
        catch (error) {
            logger_1.logger.error(`搜索产品知识失败: ${error.message}`);
            throw new Error(`无法获取产品知识: ${error.message}`);
        }
    }
    /**
     * 获取农产品的溯源信息和相关知识图谱
     * @param productId 产品ID
     */
    async getProductTraceabilityKnowledge(productId) {
        const cacheKey = `product_traceability:${productId}`;
        // 尝试从缓存获取数据
        const cachedData = await cache_1.redisClient.get(cacheKey);
        if (cachedData) {
            logger_1.logger.debug(`从缓存获取产品溯源知识: ${productId}`);
            return JSON.parse(cachedData);
        }
        try {
            // 调用知识图谱服务获取产品溯源信息
            const response = await axios_1.default.get(`${this.knowledgeGraphUrl}/api/nodes/product/${productId}/trace`);
            // 缓存结果
            if (response.data) {
                await cache_1.redisClient.set(cacheKey, JSON.stringify(response.data), 'EX', this.cacheTTL);
            }
            return response.data;
        }
        catch (error) {
            logger_1.logger.error(`获取产品溯源信息失败: ${error.message}`);
            throw new Error(`无法获取产品溯源信息: ${error.message}`);
        }
    }
    /**
     * 根据用户体质获取适合的农产品推荐
     * @param constitutionType 用户体质类型
     * @param limit 结果数量限制
     */
    async getProductsByConstitution(constitutionType, limit = 10) {
        const cacheKey = `constitution_products:${constitutionType}:${limit}`;
        // 尝试从缓存获取数据
        const cachedData = await cache_1.redisClient.get(cacheKey);
        if (cachedData) {
            logger_1.logger.debug(`从缓存获取体质相关产品: ${constitutionType}`);
            return JSON.parse(cachedData);
        }
        try {
            // 调用知识图谱服务获取体质相关产品信息
            const response = await axios_1.default.get(`${this.knowledgeGraphUrl}/api/relationships/query`, {
                params: {
                    startNodeType: 'ConstitutionType',
                    startNodeName: constitutionType,
                    relationshipType: 'RECOMMENDS',
                    endNodeType: 'AgriculturalProduct',
                    limit
                }
            });
            // 缓存结果
            if (response.data && response.data.relationships) {
                await cache_1.redisClient.set(cacheKey, JSON.stringify(response.data.relationships), 'EX', this.cacheTTL);
            }
            return response.data.relationships;
        }
        catch (error) {
            logger_1.logger.error(`获取体质相关产品推荐失败: ${error.message}`);
            throw new Error(`无法获取体质相关产品: ${error.message}`);
        }
    }
    /**
     * 获取节气相关农产品推荐
     * @param seasonalNode 节气名称
     * @param limit 结果数量限制
     */
    async getSeasonalProducts(seasonalNode, limit = 10) {
        const cacheKey = `seasonal_products:${seasonalNode}:${limit}`;
        // 尝试从缓存获取数据
        const cachedData = await cache_1.redisClient.get(cacheKey);
        if (cachedData) {
            logger_1.logger.debug(`从缓存获取节气相关产品: ${seasonalNode}`);
            return JSON.parse(cachedData);
        }
        try {
            // 调用知识图谱服务获取节气相关产品信息
            const response = await axios_1.default.get(`${this.knowledgeGraphUrl}/api/relationships/query`, {
                params: {
                    startNodeType: 'SeasonalNode',
                    startNodeName: seasonalNode,
                    relationshipType: 'IN_SEASON',
                    endNodeType: 'AgriculturalProduct',
                    limit
                }
            });
            // 缓存结果
            if (response.data && response.data.relationships) {
                await cache_1.redisClient.set(cacheKey, JSON.stringify(response.data.relationships), 'EX', this.cacheTTL);
            }
            return response.data.relationships;
        }
        catch (error) {
            logger_1.logger.error(`获取节气相关产品推荐失败: ${error.message}`);
            throw new Error(`无法获取节气相关产品: ${error.message}`);
        }
    }
    /**
     * 获取农产品的营养成分详细信息
     * @param productId 产品ID或名称
     */
    async getProductNutritionInfo(productId) {
        const cacheKey = `product_nutrition:${productId}`;
        // 尝试从缓存获取数据
        const cachedData = await cache_1.redisClient.get(cacheKey);
        if (cachedData) {
            logger_1.logger.debug(`从缓存获取产品营养信息: ${productId}`);
            return JSON.parse(cachedData);
        }
        try {
            // 调用知识库服务获取产品营养信息
            const response = await axios_1.default.get(`${this.knowledgeBaseUrl}/api/knowledge/products/${productId}/nutrition`);
            // 缓存结果
            if (response.data) {
                await cache_1.redisClient.set(cacheKey, JSON.stringify(response.data), 'EX', this.cacheTTL);
            }
            return response.data;
        }
        catch (error) {
            logger_1.logger.error(`获取产品营养信息失败: ${error.message}`);
            throw new Error(`无法获取产品营养信息: ${error.message}`);
        }
    }
    /**
     * 获取产品的中医功效信息
     * @param productId 产品ID或名称
     */
    async getProductTCMProperties(productId) {
        const cacheKey = `product_tcm:${productId}`;
        // 尝试从缓存获取数据
        const cachedData = await cache_1.redisClient.get(cacheKey);
        if (cachedData) {
            logger_1.logger.debug(`从缓存获取产品中医功效: ${productId}`);
            return JSON.parse(cachedData);
        }
        try {
            // 调用知识库服务获取产品中医功效
            const response = await axios_1.default.get(`${this.knowledgeBaseUrl}/api/knowledge/products/${productId}/tcm-properties`);
            // 缓存结果
            if (response.data) {
                await cache_1.redisClient.set(cacheKey, JSON.stringify(response.data), 'EX', this.cacheTTL);
            }
            return response.data;
        }
        catch (error) {
            logger_1.logger.error(`获取产品中医功效失败: ${error.message}`);
            throw new Error(`无法获取产品中医功效: ${error.message}`);
        }
    }
    /**
     * 获取知识库统计信息
     */
    async getKnowledgeBaseStats() {
        try {
            const response = await axios_1.default.get(`${this.knowledgeBaseUrl}/api/stats`);
            return response.data;
        }
        catch (error) {
            logger_1.logger.error(`获取知识库统计信息失败: ${error.message}`);
            throw new Error(`无法获取知识库统计信息: ${error.message}`);
        }
    }
    /**
     * 获取知识图谱统计信息
     */
    async getKnowledgeGraphStats() {
        try {
            const response = await axios_1.default.get(`${this.knowledgeGraphUrl}/api/stats`);
            return response.data;
        }
        catch (error) {
            logger_1.logger.error(`获取知识图谱统计信息失败: ${error.message}`);
            throw new Error(`无法获取知识图谱统计信息: ${error.message}`);
        }
    }
}
exports.KnowledgeService = KnowledgeService;
exports.default = new KnowledgeService();

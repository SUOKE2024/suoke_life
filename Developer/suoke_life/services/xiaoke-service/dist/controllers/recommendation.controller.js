"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.RecommendationController = void 0;
const logger_1 = require("../utils/logger");
const recommendation_service_1 = __importDefault(require("../services/recommendation/recommendation.service"));
const metrics_1 = require("../core/metrics");
/**
 * 推荐控制器
 * 处理与产品和活动推荐相关的HTTP请求
 */
class RecommendationController {
    constructor(recommendationService) {
        this.recommendationService = recommendationService;
    }
    /**
     * 获取个性化产品推荐
     */
    async getPersonalizedProductRecommendations(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/recommendations/products/personalized',
                status: '200'
            });
            // @ts-ignore - userId来自auth中间件
            const { userId } = req.user;
            const { limit } = req.query;
            const recommendations = await this.recommendationService.getPersonalizedProductRecommendations(userId, limit ? parseInt(limit, 10) : undefined);
            res.json({
                success: true,
                data: recommendations
            });
        }
        catch (error) {
            logger_1.logger.error('获取个性化产品推荐失败:', error);
            res.status(500).json({
                success: false,
                error: '获取个性化产品推荐失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 获取热门产品推荐
     */
    async getPopularProducts(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/recommendations/products/popular',
                status: '200'
            });
            const { limit } = req.query;
            const popularProducts = await this.recommendationService.getPopularProducts(limit ? parseInt(limit, 10) : undefined);
            res.json({
                success: true,
                data: popularProducts
            });
        }
        catch (error) {
            logger_1.logger.error('获取热门产品推荐失败:', error);
            res.status(500).json({
                success: false,
                error: '获取热门产品推荐失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 获取节气产品推荐
     */
    async getSeasonalProductRecommendations(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/recommendations/products/seasonal',
                status: '200'
            });
            const { limit } = req.query;
            const seasonalProducts = await this.recommendationService.getSeasonalProductRecommendations(limit ? parseInt(limit, 10) : undefined);
            res.json({
                success: true,
                data: seasonalProducts
            });
        }
        catch (error) {
            logger_1.logger.error('获取节气产品推荐失败:', error);
            res.status(500).json({
                success: false,
                error: '获取节气产品推荐失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 获取个性化活动推荐
     */
    async getPersonalizedActivityRecommendations(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/recommendations/activities/personalized',
                status: '200'
            });
            // @ts-ignore - userId来自auth中间件
            const { userId } = req.user;
            const { limit } = req.query;
            const recommendations = await this.recommendationService.getPersonalizedActivityRecommendations(userId, limit ? parseInt(limit, 10) : undefined);
            res.json({
                success: true,
                data: recommendations
            });
        }
        catch (error) {
            logger_1.logger.error('获取个性化活动推荐失败:', error);
            res.status(500).json({
                success: false,
                error: '获取个性化活动推荐失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 获取热门活动推荐
     */
    async getPopularActivities(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/recommendations/activities/popular',
                status: '200'
            });
            const { limit } = req.query;
            const popularActivities = await this.recommendationService.getPopularActivities(limit ? parseInt(limit, 10) : undefined);
            res.json({
                success: true,
                data: popularActivities
            });
        }
        catch (error) {
            logger_1.logger.error('获取热门活动推荐失败:', error);
            res.status(500).json({
                success: false,
                error: '获取热门活动推荐失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 获取节气活动推荐
     */
    async getSeasonalActivityRecommendations(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/recommendations/activities/seasonal',
                status: '200'
            });
            const { limit } = req.query;
            const seasonalActivities = await this.recommendationService.getSeasonalActivityRecommendations(limit ? parseInt(limit, 10) : undefined);
            res.json({
                success: true,
                data: seasonalActivities
            });
        }
        catch (error) {
            logger_1.logger.error('获取节气活动推荐失败:', error);
            res.status(500).json({
                success: false,
                error: '获取节气活动推荐失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
}
exports.RecommendationController = RecommendationController;
exports.default = new RecommendationController(recommendation_service_1.default);

"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = recommendationRoutes;
const express_1 = require("express");
const recommendation_controller_1 = __importDefault(require("../controllers/recommendation.controller"));
const auth_middleware_1 = require("../middleware/auth.middleware");
const logger_1 = require("../utils/logger");
const rate_limit_middleware_1 = require("../middleware/rate-limit.middleware");
const recommendation_service_1 = require("../services/recommendation/recommendation.service");
const auth_middleware_2 = require("../core/middleware/auth.middleware");
/**
 * 推荐路由配置
 * @param io Socket.IO 服务器实例
 * @returns 配置好的路由
 */
function recommendationRoutes(io) {
    const router = (0, express_1.Router)();
    const recommendationService = new recommendation_service_1.RecommendationService();
    logger_1.logger.info('初始化推荐路由...');
    // 产品推荐路由
    // 获取个性化产品推荐 - 需要用户认证
    router.get('/products/personalized', auth_middleware_2.requireAuth, (0, rate_limit_middleware_1.rateLimit)(20, 60), // 每分钟最多20次请求
    async (req, res) => {
        try {
            const userId = req.user.id;
            const limit = parseInt(req.query.limit) || 10;
            const userProfile = await recommendationService.getUserProfile(userId);
            const recommendations = await recommendationService.getPersonalizedProductRecommendations(userProfile, limit);
            res.json({ success: true, recommendations });
        }
        catch (error) {
            logger_1.logger.error('获取个性化产品推荐失败', error);
            res.status(500).json({ success: false, error: '获取推荐失败', message: error.message });
        }
    });
    // 获取热门产品推荐 - 公开访问
    router.get('/products/popular', (0, rate_limit_middleware_1.rateLimit)(30, 60), // 每分钟最多30次请求
    async (req, res) => {
        try {
            const limit = parseInt(req.query.limit) || 10;
            const recommendations = await recommendationService.getPopularProducts(limit);
            res.json({ success: true, recommendations });
        }
        catch (error) {
            logger_1.logger.error('获取热门产品推荐失败', error);
            res.status(500).json({ success: false, error: '获取推荐失败', message: error.message });
        }
    });
    // 获取节气产品推荐 - 公开访问
    router.get('/products/seasonal', (0, rate_limit_middleware_1.rateLimit)(30, 60), // 每分钟最多30次请求
    async (req, res) => {
        try {
            const limit = parseInt(req.query.limit) || 10;
            const recommendations = await recommendationService.getSeasonalProductRecommendations(limit);
            res.json({ success: true, recommendations });
        }
        catch (error) {
            logger_1.logger.error('获取季节性产品推荐失败', error);
            res.status(500).json({ success: false, error: '获取推荐失败', message: error.message });
        }
    });
    // 获取节气相关产品推荐
    router.get('/products/solar-term/:solarTerm', auth_middleware_2.requireAuth, async (req, res) => {
        try {
            const { solarTerm } = req.params;
            const userId = req.user.id;
            const limit = parseInt(req.query.limit) || 10;
            const userProfile = await recommendationService.getUserProfile(userId);
            const recommendations = await recommendationService.getSolarTermProductRecommendations(solarTerm, userProfile, limit);
            res.json({ success: true, recommendations });
        }
        catch (error) {
            logger_1.logger.error(`获取节气产品推荐失败: ${req.params.solarTerm}`, error);
            res.status(500).json({ success: false, error: '获取推荐失败', message: error.message });
        }
    });
    // 获取健康导向产品推荐
    router.post('/products/health-oriented', auth_middleware_2.requireAuth, async (req, res) => {
        try {
            const userId = req.user.id;
            const { healthConcepts } = req.body;
            const limit = parseInt(req.query.limit) || 10;
            if (!healthConcepts || !Array.isArray(healthConcepts) || healthConcepts.length === 0) {
                return res.status(400).json({
                    success: false,
                    error: '请提供有效的健康概念列表'
                });
            }
            const userProfile = await recommendationService.getUserProfile(userId);
            const recommendations = await recommendationService.getHealthOrientedProductRecommendations(userProfile, healthConcepts, limit);
            res.json({ success: true, recommendations });
        }
        catch (error) {
            logger_1.logger.error('获取健康导向产品推荐失败', error);
            res.status(500).json({ success: false, error: '获取推荐失败', message: error.message });
        }
    });
    // 活动推荐路由
    // 获取个性化活动推荐 - 需要用户认证
    router.get('/activities/personalized', auth_middleware_1.authenticateJwt, (0, rate_limit_middleware_1.rateLimit)(20, 60), // 每分钟最多20次请求
    recommendation_controller_1.default.getPersonalizedActivityRecommendations.bind(recommendation_controller_1.default));
    // 获取热门活动推荐 - 公开访问
    router.get('/activities/popular', (0, rate_limit_middleware_1.rateLimit)(30, 60), // 每分钟最多30次请求
    recommendation_controller_1.default.getPopularActivities.bind(recommendation_controller_1.default));
    // 获取节气活动推荐 - 公开访问
    router.get('/activities/seasonal', (0, rate_limit_middleware_1.rateLimit)(30, 60), // 每分钟最多30次请求
    recommendation_controller_1.default.getSeasonalActivityRecommendations.bind(recommendation_controller_1.default));
    // 设置实时推荐通知功能
    io.of('/recommendations').on('connection', (socket) => {
        logger_1.logger.info(`Socket connected for recommendations: ${socket.id}`);
        // 当用户登录时，可发送个性化推荐
        socket.on('user-login', async (userData) => {
            try {
                const { userId } = userData;
                // 获取个性化产品推荐
                const productRecommendations = await recommendation_controller_1.default.recommendationService.getPersonalizedProductRecommendations(userId, 5);
                socket.emit('personalized-product-recommendations', productRecommendations);
                // 获取个性化活动推荐
                const activityRecommendations = await recommendation_controller_1.default.recommendationService.getPersonalizedActivityRecommendations(userId, 3);
                socket.emit('personalized-activity-recommendations', activityRecommendations);
            }
            catch (error) {
                logger_1.logger.error('发送个性化推荐失败:', error);
            }
        });
        // 处理断开连接
        socket.on('disconnect', () => {
            logger_1.logger.info(`Socket disconnected from recommendations: ${socket.id}`);
        });
    });
    // WebSocket事件处理
    io.on('connection', (socket) => {
        socket.on('request_health_recommendations', async (data) => {
            try {
                const { userId, healthConcepts, limit } = data;
                if (!userId || !healthConcepts || !Array.isArray(healthConcepts)) {
                    socket.emit('health_recommendations_error', {
                        error: '无效的请求参数'
                    });
                    return;
                }
                const userProfile = await recommendationService.getUserProfile(userId);
                const recommendations = await recommendationService.getHealthOrientedProductRecommendations(userProfile, healthConcepts, limit || 10);
                socket.emit('health_recommendations_result', { recommendations });
            }
            catch (error) {
                logger_1.logger.error('WebSocket健康产品推荐请求失败', error);
                socket.emit('health_recommendations_error', {
                    error: '获取健康产品推荐失败',
                    message: error.message
                });
            }
        });
    });
    return router;
}

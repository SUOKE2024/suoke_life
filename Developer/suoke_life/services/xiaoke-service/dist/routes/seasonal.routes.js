"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = seasonalRoutes;
const express_1 = require("express");
const seasonal_controller_1 = __importDefault(require("../controllers/seasonal.controller"));
const validation_middleware_1 = require("../middleware/validation.middleware");
const auth_middleware_1 = require("../middleware/auth.middleware");
const logger_1 = require("../utils/logger");
const rate_limit_middleware_1 = require("../middleware/rate-limit.middleware");
/**
 * 节气路由配置
 * @param io Socket.IO 服务器实例
 * @returns 配置好的路由
 */
function seasonalRoutes(io) {
    const router = (0, express_1.Router)();
    logger_1.logger.info('初始化节气路由...');
    // 公共访问路由 - 基础节气信息
    // 获取当前节气信息
    router.get('/current', (0, rate_limit_middleware_1.rateLimit)(10, 60), // 每分钟最多10次请求
    seasonal_controller_1.default.getCurrentSolarTerm.bind(seasonal_controller_1.default));
    // 获取指定日期的节气信息
    router.get('/by-date', (0, rate_limit_middleware_1.rateLimit)(20, 60), // 每分钟最多20次请求
    (0, validation_middleware_1.validateRequest)({
        query: {
            date: { type: 'string', optional: false }
        }
    }), seasonal_controller_1.default.getSolarTermByDate.bind(seasonal_controller_1.default));
    // 获取所有节气列表
    router.get('/all', (0, rate_limit_middleware_1.rateLimit)(5, 60), // 每分钟最多5次请求
    seasonal_controller_1.default.getAllSolarTerms.bind(seasonal_controller_1.default));
    // 获取下一个节气信息
    router.get('/next', (0, rate_limit_middleware_1.rateLimit)(10, 60), // 每分钟最多10次请求
    seasonal_controller_1.default.getNextSolarTerm.bind(seasonal_controller_1.default));
    // 获取指定ID的节气信息
    router.get('/:id', (0, rate_limit_middleware_1.rateLimit)(15, 60), // 每分钟最多15次请求
    seasonal_controller_1.default.getSolarTermById.bind(seasonal_controller_1.default));
    // 需要认证的路由 - 特定节气功能
    // 获取当前节气饮食推荐
    router.get('/dietary-recommendations', auth_middleware_1.authenticateJwt, (0, rate_limit_middleware_1.rateLimit)(15, 60), // 每分钟最多15次请求
    seasonal_controller_1.default.getCurrentDietaryRecommendations.bind(seasonal_controller_1.default));
    // 获取当前节气健康建议
    router.get('/health-tips', auth_middleware_1.authenticateJwt, (0, rate_limit_middleware_1.rateLimit)(15, 60), // 每分钟最多15次请求
    seasonal_controller_1.default.getCurrentHealthTips.bind(seasonal_controller_1.default));
    // 设置实时节气通知功能
    io.of('/seasonal').on('connection', (socket) => {
        logger_1.logger.info(`Socket connected for seasonal updates: ${socket.id}`);
        // 当有用户连接时，发送当前节气信息
        seasonal_controller_1.default.seasonalService.getCurrentSolarTerm()
            .then((solarTerm) => {
            if (solarTerm) {
                socket.emit('current-solar-term', solarTerm);
            }
        })
            .catch((error) => {
            logger_1.logger.error('获取当前节气信息失败:', error);
        });
        // 处理断开连接
        socket.on('disconnect', () => {
            logger_1.logger.info(`Socket disconnected from seasonal updates: ${socket.id}`);
        });
    });
    return router;
}

"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const subscription_controller_1 = __importDefault(require("../../controllers/subscription.controller"));
const auth_middleware_1 = require("../middleware/auth.middleware");
// 创建路由
const createSubscriptionRoutes = (io) => {
    const router = express_1.default.Router();
    /**
     * @route   POST /api/v1/subscriptions
     * @desc    创建订阅
     * @access  Private
     */
    router.post('/', auth_middleware_1.authenticateJWT, async (req, res) => {
        await subscription_controller_1.default.createSubscription(req, res);
        // 通知新订阅创建
        const newSubData = res.locals.responseData;
        if (newSubData && newSubData.success) {
            io.to(`user:${req.user.userId}`).emit('subscription:created', {
                id: newSubData.data.id,
                serviceName: newSubData.data.serviceName,
                serviceType: newSubData.data.serviceType,
                status: newSubData.data.status,
                startDate: newSubData.data.startDate,
                endDate: newSubData.data.endDate,
                timestamp: new Date().toISOString()
            });
        }
    });
    /**
     * @route   GET /api/v1/subscriptions/:id
     * @desc    获取订阅详情
     * @access  Private
     */
    router.get('/:id', auth_middleware_1.authenticateJWT, (req, res) => {
        subscription_controller_1.default.getSubscriptionById(req, res);
    });
    /**
     * @route   GET /api/v1/subscriptions/user
     * @desc    获取用户订阅列表
     * @access  Private
     */
    router.get('/user', auth_middleware_1.authenticateJWT, (req, res) => {
        subscription_controller_1.default.getUserSubscriptions(req, res);
    });
    /**
     * @route   PUT /api/v1/subscriptions/:id/status
     * @desc    更新订阅状态
     * @access  Private
     */
    router.put('/:id/status', auth_middleware_1.authenticateJWT, async (req, res) => {
        await subscription_controller_1.default.updateSubscriptionStatus(req, res);
        // 通知订阅状态更新
        const updateData = res.locals.responseData;
        if (updateData && updateData.success) {
            io.to(`user:${updateData.data.userId}`).emit('subscription:status_updated', {
                id: updateData.data.id,
                status: updateData.data.status,
                serviceName: updateData.data.serviceName,
                timestamp: new Date().toISOString()
            });
        }
    });
    /**
     * @route   PUT /api/v1/subscriptions/:id/renew
     * @desc    续订服务
     * @access  Private
     */
    router.put('/:id/renew', auth_middleware_1.authenticateJWT, async (req, res) => {
        await subscription_controller_1.default.renewSubscription(req, res);
        // 通知订阅续订
        const renewData = res.locals.responseData;
        if (renewData && renewData.success) {
            io.to(`user:${renewData.data.userId}`).emit('subscription:renewed', {
                id: renewData.data.id,
                serviceName: renewData.data.serviceName,
                serviceType: renewData.data.serviceType,
                status: renewData.data.status,
                startDate: renewData.data.startDate,
                endDate: renewData.data.endDate,
                billingCycle: renewData.data.billingCycle,
                timestamp: new Date().toISOString()
            });
        }
    });
    // 中间件：捕获响应数据用于WebSocket通知
    router.use((req, res, next) => {
        const originalJson = res.json;
        res.json = function (data) {
            res.locals.responseData = data;
            return originalJson.call(this, data);
        };
        next();
    });
    return router;
};
exports.default = createSubscriptionRoutes;

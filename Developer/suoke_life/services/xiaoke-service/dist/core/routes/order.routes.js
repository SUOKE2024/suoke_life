"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const order_controller_1 = __importDefault(require("../../controllers/order.controller"));
const auth_middleware_1 = require("../middleware/auth.middleware");
// 创建路由
const createOrderRoutes = (io) => {
    const router = express_1.default.Router();
    /**
     * @route   POST /api/v1/orders
     * @desc    创建订单
     * @access  Private
     */
    router.post('/', auth_middleware_1.authenticateJWT, async (req, res) => {
        await order_controller_1.default.createOrder(req, res);
        // 通知新订单创建
        const newOrderData = res.locals.responseData;
        if (newOrderData && newOrderData.success) {
            io.to(`user:${req.user.userId}`).emit('order:created', {
                orderId: newOrderData.data.id,
                orderNumber: newOrderData.data.orderNumber,
                status: newOrderData.data.status,
                timestamp: new Date().toISOString()
            });
            // 通知管理员
            io.to('admin').emit('order:new', {
                orderId: newOrderData.data.id,
                orderNumber: newOrderData.data.orderNumber,
                userId: newOrderData.data.userId,
                timestamp: new Date().toISOString()
            });
        }
    });
    /**
     * @route   GET /api/v1/orders/:id
     * @desc    获取订单详情
     * @access  Private
     */
    router.get('/:id', auth_middleware_1.authenticateJWT, (req, res) => {
        order_controller_1.default.getOrderById(req, res);
    });
    /**
     * @route   GET /api/v1/orders/user
     * @desc    获取用户订单列表
     * @access  Private
     */
    router.get('/user', auth_middleware_1.authenticateJWT, (req, res) => {
        order_controller_1.default.getUserOrders(req, res);
    });
    /**
     * @route   PUT /api/v1/orders/:id/status
     * @desc    更新订单状态
     * @access  Private
     */
    router.put('/:id/status', auth_middleware_1.authenticateJWT, async (req, res) => {
        await order_controller_1.default.updateOrderStatus(req, res);
        // 通知订单状态更新
        const updateData = res.locals.responseData;
        if (updateData && updateData.success) {
            io.to(`user:${updateData.data.userId}`).emit('order:status_updated', {
                orderId: updateData.data.id,
                orderNumber: updateData.data.orderNumber,
                status: updateData.data.status,
                timestamp: new Date().toISOString()
            });
        }
    });
    /**
     * @route   PUT /api/v1/orders/:id/payment
     * @desc    更新支付状态
     * @access  Private
     */
    router.put('/:id/payment', auth_middleware_1.authenticateJWT, async (req, res) => {
        await order_controller_1.default.updatePaymentStatus(req, res);
        // 通知支付状态更新
        const updateData = res.locals.responseData;
        if (updateData && updateData.success) {
            io.to(`user:${updateData.data.userId}`).emit('order:payment_updated', {
                orderId: updateData.data.id,
                orderNumber: updateData.data.orderNumber,
                status: updateData.data.status,
                paymentStatus: updateData.data.paymentStatus,
                timestamp: new Date().toISOString()
            });
            // 如果支付成功，通知管理员
            if (updateData.data.paymentStatus === 'paid') {
                io.to('admin').emit('order:paid', {
                    orderId: updateData.data.id,
                    orderNumber: updateData.data.orderNumber,
                    userId: updateData.data.userId,
                    totalAmount: updateData.data.totalAmount,
                    timestamp: new Date().toISOString()
                });
            }
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
exports.default = createOrderRoutes;

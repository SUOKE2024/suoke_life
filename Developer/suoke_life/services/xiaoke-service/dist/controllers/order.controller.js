"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderController = void 0;
const logger_1 = require("../utils/logger");
const order_service_1 = __importDefault(require("../services/order/order.service"));
const metrics_1 = require("../core/metrics");
/**
 * 订单控制器
 * 处理与订单相关的HTTP请求
 */
class OrderController {
    constructor(orderService) {
        this.orderService = orderService;
    }
    /**
     * 创建订单
     */
    async createOrder(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/orders',
                status: '201'
            });
            const { userId } = req.user;
            const orderData = {
                ...req.body,
                userId
            };
            const order = await this.orderService.createOrder(orderData);
            res.status(201).json({
                success: true,
                data: order
            });
        }
        catch (error) {
            logger_1.logger.error('创建订单失败:', error);
            // 特定错误处理
            if (error instanceof Error && error.message.includes('库存不足')) {
                res.status(400).json({
                    success: false,
                    error: '库存不足',
                    message: error.message,
                    code: 'INSUFFICIENT_STOCK'
                });
                return;
            }
            res.status(500).json({
                success: false,
                error: '创建订单失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 获取订单详情
     */
    async getOrderById(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/orders/:id',
                status: '200'
            });
            const { id } = req.params;
            const order = await this.orderService.getOrderById(id);
            if (!order) {
                res.status(404).json({
                    success: false,
                    error: '订单不存在',
                    code: 'ORDER_NOT_FOUND'
                });
                return;
            }
            res.json({
                success: true,
                data: order
            });
        }
        catch (error) {
            logger_1.logger.error('获取订单详情失败:', error);
            res.status(500).json({
                success: false,
                error: '获取订单详情失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 获取用户订单列表
     */
    async getUserOrders(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/orders/user',
                status: '200'
            });
            const { userId } = req.user;
            const { status, startDate, endDate, limit = '20', page = '1' } = req.query;
            const skip = (parseInt(page, 10) - 1) * parseInt(limit, 10);
            const result = await this.orderService.getOrders({
                userId,
                status: status,
                startDate: startDate,
                endDate: endDate,
                limit: parseInt(limit, 10),
                skip
            });
            res.json({
                success: true,
                data: {
                    orders: result.orders,
                    pagination: {
                        total: result.total,
                        page: parseInt(page, 10),
                        limit: parseInt(limit, 10),
                        pages: Math.ceil(result.total / parseInt(limit, 10))
                    }
                }
            });
        }
        catch (error) {
            logger_1.logger.error('获取用户订单列表失败:', error);
            res.status(500).json({
                success: false,
                error: '获取用户订单列表失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 更新订单状态
     */
    async updateOrderStatus(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/orders/:id/status',
                status: '200'
            });
            const { id } = req.params;
            const { status } = req.body;
            if (!status) {
                res.status(400).json({
                    success: false,
                    error: '缺少状态参数',
                    code: 'MISSING_STATUS'
                });
                return;
            }
            const order = await this.orderService.updateOrderStatus(id, status);
            if (!order) {
                res.status(404).json({
                    success: false,
                    error: '订单不存在',
                    code: 'ORDER_NOT_FOUND'
                });
                return;
            }
            res.json({
                success: true,
                data: order
            });
        }
        catch (error) {
            logger_1.logger.error('更新订单状态失败:', error);
            // 特定错误处理
            if (error instanceof Error && error.message.includes('无效的订单状态')) {
                res.status(400).json({
                    success: false,
                    error: '无效的订单状态',
                    message: error.message,
                    code: 'INVALID_ORDER_STATUS'
                });
                return;
            }
            res.status(500).json({
                success: false,
                error: '更新订单状态失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 更新支付状态
     */
    async updatePaymentStatus(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/orders/:id/payment',
                status: '200'
            });
            const { id } = req.params;
            const { paymentStatus } = req.body;
            if (!paymentStatus) {
                res.status(400).json({
                    success: false,
                    error: '缺少支付状态参数',
                    code: 'MISSING_PAYMENT_STATUS'
                });
                return;
            }
            const order = await this.orderService.updatePaymentStatus(id, paymentStatus);
            if (!order) {
                res.status(404).json({
                    success: false,
                    error: '订单不存在',
                    code: 'ORDER_NOT_FOUND'
                });
                return;
            }
            res.json({
                success: true,
                data: order
            });
        }
        catch (error) {
            logger_1.logger.error('更新支付状态失败:', error);
            // 特定错误处理
            if (error instanceof Error && error.message.includes('无效的支付状态')) {
                res.status(400).json({
                    success: false,
                    error: '无效的支付状态',
                    message: error.message,
                    code: 'INVALID_PAYMENT_STATUS'
                });
                return;
            }
            res.status(500).json({
                success: false,
                error: '更新支付状态失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
}
exports.OrderController = OrderController;
exports.default = new OrderController(order_service_1.default);

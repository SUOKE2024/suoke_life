"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.OrderService = void 0;
const mongoose_1 = __importDefault(require("mongoose"));
const logger_1 = require("../../utils/logger");
const cache_1 = require("../../core/cache");
const order_model_1 = require("../../models/order.model");
const product_model_1 = require("../../models/product.model");
const metrics_1 = require("../../core/metrics");
// 缓存配置
const ORDER_CACHE_TTL = parseInt(process.env.ORDER_CACHE_TTL || '3600', 10); // 默认1小时
/**
 * 订单服务类
 * 负责处理订单相关业务逻辑
 */
class OrderService {
    /**
     * 创建新订单
     */
    async createOrder(orderData) {
        const session = await mongoose_1.default.startSession();
        session.startTransaction();
        try {
            const startTime = Date.now();
            // 计算订单总金额（重新计算以确保准确性）
            let calculatedTotalAmount = 0;
            for (const item of orderData.items) {
                const product = await product_model_1.ProductModel.findById(item.productId).session(session);
                if (!product) {
                    throw new Error(`产品不存在: ${item.productId}`);
                }
                // 验证库存
                if (product.stock < item.quantity) {
                    throw new Error(`产品 ${product.name} 库存不足`);
                }
                // 更新库存
                await product_model_1.ProductModel.findByIdAndUpdate(item.productId, { $inc: { stock: -item.quantity } }, { session });
                // 使用最新价格计算
                const itemTotal = product.price * item.quantity;
                calculatedTotalAmount += itemTotal;
                // 更新项目总金额
                item.price = product.price;
                item.totalPrice = itemTotal;
            }
            // 添加运费、税费，减去折扣
            calculatedTotalAmount += orderData.shippingCost || 0;
            calculatedTotalAmount += orderData.tax || 0;
            calculatedTotalAmount -= orderData.discount || 0;
            // 创建订单
            const order = await order_model_1.OrderModel.create([{
                    ...orderData,
                    totalAmount: calculatedTotalAmount
                }], { session });
            await session.commitTransaction();
            session.endSession();
            // 记录处理时间
            const processingTime = (Date.now() - startTime) / 1000;
            metrics_1.orderProcessingTime.observe({ operation: 'create', status: order_model_1.OrderStatus.PENDING }, processingTime);
            // 转换为Order类型
            const createdOrder = order[0];
            return {
                id: createdOrder._id.toString(),
                orderNumber: createdOrder.orderNumber,
                userId: createdOrder.userId,
                items: createdOrder.items,
                totalAmount: createdOrder.totalAmount,
                status: createdOrder.status,
                paymentMethod: createdOrder.paymentMethod,
                paymentStatus: createdOrder.paymentStatus,
                paymentTime: createdOrder.paymentTime?.toISOString(),
                shippingAddress: createdOrder.shippingAddress,
                trackingNumber: createdOrder.trackingNumber,
                shippingMethod: createdOrder.shippingMethod,
                shippingCost: createdOrder.shippingCost,
                discount: createdOrder.discount,
                tax: createdOrder.tax,
                notes: createdOrder.notes,
                metadata: createdOrder.metadata,
                createdAt: createdOrder.createdAt.toISOString(),
                updatedAt: createdOrder.updatedAt.toISOString()
            };
        }
        catch (error) {
            await session.abortTransaction();
            session.endSession();
            logger_1.logger.error('创建订单失败:', error);
            throw error;
        }
    }
    /**
     * 获取订单详情
     */
    async getOrderById(orderId) {
        try {
            // 尝试从缓存获取
            const cacheKey = `order:${orderId}`;
            const cachedOrder = await (0, cache_1.getCache)(cacheKey);
            if (cachedOrder) {
                logger_1.logger.debug(`从缓存获取订单信息: ${orderId}`);
                return cachedOrder;
            }
            // 从数据库获取
            const order = await order_model_1.OrderModel.findById(orderId).lean();
            if (!order) {
                logger_1.logger.debug(`订单不存在: ${orderId}`);
                return null;
            }
            // 转换为Order类型
            const orderInfo = {
                id: order._id.toString(),
                orderNumber: order.orderNumber,
                userId: order.userId,
                items: order.items,
                totalAmount: order.totalAmount,
                status: order.status,
                paymentMethod: order.paymentMethod,
                paymentStatus: order.paymentStatus,
                paymentTime: order.paymentTime?.toISOString(),
                shippingAddress: order.shippingAddress,
                trackingNumber: order.trackingNumber,
                shippingMethod: order.shippingMethod,
                shippingCost: order.shippingCost,
                discount: order.discount,
                tax: order.tax,
                notes: order.notes,
                metadata: order.metadata,
                createdAt: order.createdAt.toISOString(),
                updatedAt: order.updatedAt.toISOString()
            };
            // 更新缓存
            await (0, cache_1.setCache)(cacheKey, orderInfo, ORDER_CACHE_TTL);
            return orderInfo;
        }
        catch (error) {
            logger_1.logger.error(`获取订单信息失败:`, error);
            throw error;
        }
    }
    /**
     * 获取订单列表
     */
    async getOrders(options) {
        try {
            const { userId, status, startDate, endDate, limit = 20, skip = 0 } = options;
            // 构建查询条件
            const query = {};
            if (userId) {
                query.userId = userId;
            }
            if (status) {
                query.status = status;
            }
            if (startDate || endDate) {
                query.createdAt = {};
                if (startDate) {
                    query.createdAt.$gte = new Date(startDate);
                }
                if (endDate) {
                    query.createdAt.$lte = new Date(endDate);
                }
            }
            // 计算总数
            const total = await order_model_1.OrderModel.countDocuments(query);
            // 获取订单列表
            const orders = await order_model_1.OrderModel.find(query)
                .sort({ createdAt: -1 })
                .skip(skip)
                .limit(limit)
                .lean();
            // 转换为Order类型
            const orderInfos = orders.map(order => ({
                id: order._id.toString(),
                orderNumber: order.orderNumber,
                userId: order.userId,
                items: order.items,
                totalAmount: order.totalAmount,
                status: order.status,
                paymentMethod: order.paymentMethod,
                paymentStatus: order.paymentStatus,
                paymentTime: order.paymentTime?.toISOString(),
                shippingAddress: order.shippingAddress,
                trackingNumber: order.trackingNumber,
                shippingMethod: order.shippingMethod,
                shippingCost: order.shippingCost,
                discount: order.discount,
                tax: order.tax,
                notes: order.notes,
                metadata: order.metadata,
                createdAt: order.createdAt.toISOString(),
                updatedAt: order.updatedAt.toISOString()
            }));
            return { orders: orderInfos, total };
        }
        catch (error) {
            logger_1.logger.error(`获取订单列表失败:`, error);
            throw error;
        }
    }
    /**
     * 更新订单状态
     */
    async updateOrderStatus(orderId, status) {
        try {
            const startTime = Date.now();
            // 验证状态值
            if (!Object.values(order_model_1.OrderStatus).includes(status)) {
                throw new Error(`无效的订单状态: ${status}`);
            }
            // 更新订单
            const order = await order_model_1.OrderModel.findByIdAndUpdate(orderId, { status }, { new: true }).lean();
            if (!order) {
                logger_1.logger.debug(`订单不存在: ${orderId}`);
                return null;
            }
            // 清除缓存
            const cacheKey = `order:${orderId}`;
            await (0, cache_1.setCache)(cacheKey, null, 1);
            // 记录处理时间
            const processingTime = (Date.now() - startTime) / 1000;
            metrics_1.orderProcessingTime.observe({ operation: 'update', status }, processingTime);
            // 转换为Order类型
            const orderInfo = {
                id: order._id.toString(),
                orderNumber: order.orderNumber,
                userId: order.userId,
                items: order.items,
                totalAmount: order.totalAmount,
                status: order.status,
                paymentMethod: order.paymentMethod,
                paymentStatus: order.paymentStatus,
                paymentTime: order.paymentTime?.toISOString(),
                shippingAddress: order.shippingAddress,
                trackingNumber: order.trackingNumber,
                shippingMethod: order.shippingMethod,
                shippingCost: order.shippingCost,
                discount: order.discount,
                tax: order.tax,
                notes: order.notes,
                metadata: order.metadata,
                createdAt: order.createdAt.toISOString(),
                updatedAt: order.updatedAt.toISOString()
            };
            return orderInfo;
        }
        catch (error) {
            logger_1.logger.error(`更新订单状态失败:`, error);
            throw error;
        }
    }
    /**
     * 更新订单支付状态
     */
    async updatePaymentStatus(orderId, paymentStatus) {
        try {
            const startTime = Date.now();
            // 验证支付状态值
            if (!['pending', 'paid', 'failed', 'refunded'].includes(paymentStatus)) {
                throw new Error(`无效的支付状态: ${paymentStatus}`);
            }
            // 更新订单状态
            let updateData = { paymentStatus };
            // 如果支付成功，更新订单状态和支付时间
            if (paymentStatus === 'paid') {
                updateData.status = order_model_1.OrderStatus.PAID;
                updateData.paymentTime = new Date();
            }
            // 更新订单
            const order = await order_model_1.OrderModel.findByIdAndUpdate(orderId, updateData, { new: true }).lean();
            if (!order) {
                logger_1.logger.debug(`订单不存在: ${orderId}`);
                return null;
            }
            // 清除缓存
            const cacheKey = `order:${orderId}`;
            await (0, cache_1.setCache)(cacheKey, null, 1);
            // 记录处理时间
            const processingTime = (Date.now() - startTime) / 1000;
            metrics_1.orderProcessingTime.observe({ operation: 'payment', status: paymentStatus }, processingTime);
            // 转换为Order类型
            const orderInfo = {
                id: order._id.toString(),
                orderNumber: order.orderNumber,
                userId: order.userId,
                items: order.items,
                totalAmount: order.totalAmount,
                status: order.status,
                paymentMethod: order.paymentMethod,
                paymentStatus: order.paymentStatus,
                paymentTime: order.paymentTime?.toISOString(),
                shippingAddress: order.shippingAddress,
                trackingNumber: order.trackingNumber,
                shippingMethod: order.shippingMethod,
                shippingCost: order.shippingCost,
                discount: order.discount,
                tax: order.tax,
                notes: order.notes,
                metadata: order.metadata,
                createdAt: order.createdAt.toISOString(),
                updatedAt: order.updatedAt.toISOString()
            };
            return orderInfo;
        }
        catch (error) {
            logger_1.logger.error(`更新支付状态失败:`, error);
            throw error;
        }
    }
}
exports.OrderService = OrderService;
// 创建单例实例
exports.default = new OrderService();

import mongoose from 'mongoose';
import { logger } from '../../utils/logger';
import { getCache, setCache } from '../../core/cache';
import { OrderModel, OrderStatus } from '../../models/order.model';
import { ProductModel } from '../../models/product.model';
import { orderProcessingTime } from '../../core/metrics';

// 缓存配置
const ORDER_CACHE_TTL = parseInt(process.env.ORDER_CACHE_TTL || '3600', 10); // 默认1小时

// 订单接口
export interface Order {
  id: string;
  orderNumber: string;
  userId: string;
  items: OrderItem[];
  totalAmount: number;
  status: string;
  paymentMethod: string;
  paymentStatus: string;
  paymentTime?: string;
  shippingAddress: ShippingAddress;
  trackingNumber?: string;
  shippingMethod?: string;
  shippingCost: number;
  discount?: number;
  tax?: number;
  notes?: string;
  metadata?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

// 订单项接口
export interface OrderItem {
  productId: string;
  productName: string;
  quantity: number;
  price: number;
  totalPrice: number;
  metadata?: Record<string, any>;
}

// 收货地址接口
export interface ShippingAddress {
  name: string;
  phone: string;
  province: string;
  city: string;
  district: string;
  address: string;
  zipCode?: string;
}

/**
 * 订单服务类
 * 负责处理订单相关业务逻辑
 */
export class OrderService {
  /**
   * 创建新订单
   */
  async createOrder(orderData: Omit<Order, 'id' | 'orderNumber' | 'createdAt' | 'updatedAt'>): Promise<Order> {
    const session = await mongoose.startSession();
    session.startTransaction();

    try {
      const startTime = Date.now();

      // 计算订单总金额（重新计算以确保准确性）
      let calculatedTotalAmount = 0;
      for (const item of orderData.items) {
        const product = await ProductModel.findById(item.productId).session(session);
        if (!product) {
          throw new Error(`产品不存在: ${item.productId}`);
        }

        // 验证库存
        if (product.stock < item.quantity) {
          throw new Error(`产品 ${product.name} 库存不足`);
        }

        // 更新库存
        await ProductModel.findByIdAndUpdate(
          item.productId,
          { $inc: { stock: -item.quantity } },
          { session }
        );

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
      const order = await OrderModel.create([{
        ...orderData,
        totalAmount: calculatedTotalAmount
      }], { session });

      await session.commitTransaction();
      session.endSession();

      // 记录处理时间
      const processingTime = (Date.now() - startTime) / 1000;
      orderProcessingTime.observe({ operation: 'create', status: OrderStatus.PENDING }, processingTime);

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
    } catch (error) {
      await session.abortTransaction();
      session.endSession();
      logger.error('创建订单失败:', error);
      throw error;
    }
  }

  /**
   * 获取订单详情
   */
  async getOrderById(orderId: string): Promise<Order | null> {
    try {
      // 尝试从缓存获取
      const cacheKey = `order:${orderId}`;
      const cachedOrder = await getCache<Order>(cacheKey);
      
      if (cachedOrder) {
        logger.debug(`从缓存获取订单信息: ${orderId}`);
        return cachedOrder;
      }
      
      // 从数据库获取
      const order = await OrderModel.findById(orderId).lean();
      
      if (!order) {
        logger.debug(`订单不存在: ${orderId}`);
        return null;
      }
      
      // 转换为Order类型
      const orderInfo: Order = {
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
      await setCache(cacheKey, orderInfo, ORDER_CACHE_TTL);
      
      return orderInfo;
    } catch (error) {
      logger.error(`获取订单信息失败:`, error);
      throw error;
    }
  }

  /**
   * 获取订单列表
   */
  async getOrders(options: {
    userId?: string;
    status?: string;
    startDate?: string;
    endDate?: string;
    limit?: number;
    skip?: number;
  }): Promise<{ orders: Order[]; total: number }> {
    try {
      const { userId, status, startDate, endDate, limit = 20, skip = 0 } = options;
      
      // 构建查询条件
      const query: any = {};
      
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
      const total = await OrderModel.countDocuments(query);
      
      // 获取订单列表
      const orders = await OrderModel.find(query)
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit)
        .lean();
      
      // 转换为Order类型
      const orderInfos: Order[] = orders.map(order => ({
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
    } catch (error) {
      logger.error(`获取订单列表失败:`, error);
      throw error;
    }
  }

  /**
   * 更新订单状态
   */
  async updateOrderStatus(orderId: string, status: string): Promise<Order | null> {
    try {
      const startTime = Date.now();

      // 验证状态值
      if (!Object.values(OrderStatus).includes(status as OrderStatus)) {
        throw new Error(`无效的订单状态: ${status}`);
      }
      
      // 更新订单
      const order = await OrderModel.findByIdAndUpdate(
        orderId,
        { status },
        { new: true }
      ).lean();
      
      if (!order) {
        logger.debug(`订单不存在: ${orderId}`);
        return null;
      }
      
      // 清除缓存
      const cacheKey = `order:${orderId}`;
      await setCache(cacheKey, null, 1);
      
      // 记录处理时间
      const processingTime = (Date.now() - startTime) / 1000;
      orderProcessingTime.observe({ operation: 'update', status }, processingTime);
      
      // 转换为Order类型
      const orderInfo: Order = {
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
    } catch (error) {
      logger.error(`更新订单状态失败:`, error);
      throw error;
    }
  }

  /**
   * 更新订单支付状态
   */
  async updatePaymentStatus(orderId: string, paymentStatus: string): Promise<Order | null> {
    try {
      const startTime = Date.now();
      
      // 验证支付状态值
      if (!['pending', 'paid', 'failed', 'refunded'].includes(paymentStatus)) {
        throw new Error(`无效的支付状态: ${paymentStatus}`);
      }
      
      // 更新订单状态
      let updateData: any = { paymentStatus };
      
      // 如果支付成功，更新订单状态和支付时间
      if (paymentStatus === 'paid') {
        updateData.status = OrderStatus.PAID;
        updateData.paymentTime = new Date();
      }
      
      // 更新订单
      const order = await OrderModel.findByIdAndUpdate(
        orderId,
        updateData,
        { new: true }
      ).lean();
      
      if (!order) {
        logger.debug(`订单不存在: ${orderId}`);
        return null;
      }
      
      // 清除缓存
      const cacheKey = `order:${orderId}`;
      await setCache(cacheKey, null, 1);
      
      // 记录处理时间
      const processingTime = (Date.now() - startTime) / 1000;
      orderProcessingTime.observe({ operation: 'payment', status: paymentStatus }, processingTime);
      
      // 转换为Order类型
      const orderInfo: Order = {
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
    } catch (error) {
      logger.error(`更新支付状态失败:`, error);
      throw error;
    }
  }
}

// 创建单例实例
export default new OrderService(); 
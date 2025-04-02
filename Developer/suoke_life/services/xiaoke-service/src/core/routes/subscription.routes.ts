import express from 'express';
import { Server } from 'socket.io';
import subscriptionController from '../../controllers/subscription.controller';
import { authenticateJWT } from '../middleware/auth.middleware';
import { logger } from '../../utils/logger';

// 创建路由
const createSubscriptionRoutes = (io: Server) => {
  const router = express.Router();
  
  /**
   * @route   POST /api/v1/subscriptions
   * @desc    创建订阅
   * @access  Private
   */
  router.post('/', authenticateJWT, async (req, res) => {
    await subscriptionController.createSubscription(req, res);
    
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
  router.get('/:id', authenticateJWT, (req, res) => {
    subscriptionController.getSubscriptionById(req, res);
  });
  
  /**
   * @route   GET /api/v1/subscriptions/user
   * @desc    获取用户订阅列表
   * @access  Private
   */
  router.get('/user', authenticateJWT, (req, res) => {
    subscriptionController.getUserSubscriptions(req, res);
  });
  
  /**
   * @route   PUT /api/v1/subscriptions/:id/status
   * @desc    更新订阅状态
   * @access  Private
   */
  router.put('/:id/status', authenticateJWT, async (req, res) => {
    await subscriptionController.updateSubscriptionStatus(req, res);
    
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
  router.put('/:id/renew', authenticateJWT, async (req, res) => {
    await subscriptionController.renewSubscription(req, res);
    
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
    res.json = function(data) {
      res.locals.responseData = data;
      return originalJson.call(this, data);
    };
    next();
  });
  
  return router;
};

export default createSubscriptionRoutes; 
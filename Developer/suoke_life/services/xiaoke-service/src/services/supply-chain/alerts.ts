import { v4 as uuidv4 } from 'uuid';
import { logger } from '../../utils/logger';
import { SupplyChainAlert } from '../../models/supply-chain.model';

// 订阅者存储
const subscribers: Record<string, string[]> = {};

// 警报存储
const alertStore: SupplyChainAlert[] = [];

// 添加示例警报数据
const initSampleAlerts = () => {
  if (alertStore.length === 0) {
    const sampleAlerts: Partial<SupplyChainAlert>[] = [
      // 高级别警报 - 未解决
      {
        level: 'high',
        productId: 'PROD002',
        type: 'quality_issue',
        message: '蔬菜礼盒产品质量问题：部分菠菜叶片发黄',
        details: '质检环节发现部分菠菜新鲜度不足，需要替换',
        timestamp: new Date(Date.now() - 11 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'open',
        metadata: {
          affectedComponents: ['菠菜'],
          issueType: '新鲜度不足',
          location: '山东省青岛市质检中心'
        }
      },
      // 中级别警报 - 已确认
      {
        level: 'medium',
        productId: 'PROD002',
        type: 'shipment_delayed',
        message: '蔬菜礼盒运输延迟',
        details: '由于道路施工，运输延迟48小时',
        timestamp: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'acknowledged',
        acknowledgedBy: 'USER123',
        acknowledgedAt: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(),
        metadata: {
          expectedDelay: '48小时',
          reason: '高速道路维修',
          location: '江苏省南通市'
        }
      },
      // 低级别警报 - 已解决
      {
        level: 'low',
        productId: 'PROD001',
        type: 'storage_condition',
        message: '红薯存储温度波动',
        details: '仓库温度短暂超出理想范围 (18°C，理想范围 12-15°C)',
        timestamp: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'resolved',
        acknowledgedBy: 'USER456',
        acknowledgedAt: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000 + 1 * 60 * 60 * 1000).toISOString(),
        resolvedBy: 'USER456',
        resolvedAt: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000 + 3 * 60 * 60 * 1000).toISOString(),
        resolution: '已调整仓库温控系统，温度已恢复正常范围',
        metadata: {
          temperature: '18°C',
          idealRange: '12-15°C',
          location: '河南省郑州市中央仓库'
        }
      },
      // 中级别警报 - 未解决
      {
        level: 'medium',
        productId: 'PROD001',
        type: 'packaging_damage',
        message: '部分红薯包装破损',
        details: '运输过程中发现3箱包装破损，占总量的5%',
        timestamp: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'open',
        metadata: {
          damagedUnits: '3箱',
          totalPercentage: '5%',
          location: '运输途中'
        }
      },
      // 高级别警报 - 已解决
      {
        level: 'high',
        productId: 'PROD002',
        type: 'quality_issue',
        message: '蔬菜礼盒产品质量问题',
        details: '部分菠菜叶片发黄，需要替换',
        timestamp: new Date(Date.now() - 11 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'resolved',
        acknowledgedBy: 'USER789',
        acknowledgedAt: new Date(Date.now() - 11 * 24 * 60 * 60 * 1000 + 1 * 60 * 60 * 1000).toISOString(),
        resolvedBy: 'USER789',
        resolvedAt: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000).toISOString(),
        resolution: '已更换新鲜菠菜，产品重新包装并通过质检',
        metadata: {
          affectedComponents: ['菠菜'],
          correctionMethod: '更换新鲜菠菜',
          location: '山东省青岛市'
        }
      }
    ];

    // 为警报添加ID并存储
    sampleAlerts.forEach(alert => {
      const newAlert: SupplyChainAlert = {
        id: uuidv4(),
        ...alert
      } as SupplyChainAlert;
      
      alertStore.push(newAlert);
    });
    
    logger.info(`已初始化 ${sampleAlerts.length} 条示例供应链警报数据`);
  }
};

// 初始化示例警报
initSampleAlerts();

/**
 * 发送警报
 * @param alert 警报对象
 * @returns 生成的警报
 */
export const sendAlert = (alert: Omit<SupplyChainAlert, 'id' | 'timestamp' | 'status'>): SupplyChainAlert => {
  try {
    logger.info(`发送警报: ${alert.message}`);
    
    // 创建完整警报对象
    const newAlert: SupplyChainAlert = {
      id: uuidv4(),
      timestamp: new Date().toISOString(),
      status: 'open',
      ...alert
    };
    
    // 存储警报
    alertStore.push(newAlert);
    
    // 通知订阅者
    notifySubscribers(newAlert);
    
    logger.info(`警报已发送，ID: ${newAlert.id}`);
    return newAlert;
  } catch (error) {
    logger.error('发送警报失败:', error);
    throw new Error(`发送警报失败: ${(error as Error).message}`);
  }
};

/**
 * 通知订阅者
 * @param alert 警报对象
 */
const notifySubscribers = (alert: SupplyChainAlert): void => {
  try {
    // 查找与产品相关的订阅者
    const productSubscribers = subscribers[alert.productId] || [];
    
    // 通知订阅者
    if (productSubscribers.length > 0) {
      logger.info(`通知 ${productSubscribers.length} 个订阅者关于产品 ${alert.productId} 的警报`);
      
      // 模拟通知订阅者
      // 在实际应用中，这里会发送电子邮件、短信、推送通知等
      productSubscribers.forEach(subscriberId => {
        logger.info(`向订阅者 ${subscriberId} 发送警报通知: ${alert.message}`);
      });
    }
  } catch (error) {
    logger.error('通知订阅者失败:', error);
  }
};

/**
 * 订阅警报
 * @param productId 产品ID
 * @param subscriberId 订阅者ID
 */
export const subscribeToAlerts = (productId: string, subscriberId: string): void => {
  try {
    logger.info(`订阅者 ${subscriberId} 订阅产品 ${productId} 的警报`);
    
    // 如果没有该产品的订阅列表，创建一个
    if (!subscribers[productId]) {
      subscribers[productId] = [];
    }
    
    // 检查是否已经订阅
    if (!subscribers[productId].includes(subscriberId)) {
      subscribers[productId].push(subscriberId);
      logger.info(`订阅成功，当前有 ${subscribers[productId].length} 个订阅者`);
    } else {
      logger.info(`订阅者已经订阅了该产品的警报`);
    }
  } catch (error) {
    logger.error('订阅警报失败:', error);
    throw new Error(`订阅警报失败: ${(error as Error).message}`);
  }
};

/**
 * 取消订阅警报
 * @param productId 产品ID
 * @param subscriberId 订阅者ID
 */
export const unsubscribeFromAlerts = (productId: string, subscriberId: string): void => {
  try {
    logger.info(`订阅者 ${subscriberId} 取消订阅产品 ${productId} 的警报`);
    
    // 如果有该产品的订阅列表
    if (subscribers[productId]) {
      // 移除订阅者
      const index = subscribers[productId].indexOf(subscriberId);
      if (index !== -1) {
        subscribers[productId].splice(index, 1);
        logger.info(`取消订阅成功，当前有 ${subscribers[productId].length} 个订阅者`);
      } else {
        logger.info(`订阅者未订阅该产品的警报`);
      }
    } else {
      logger.info(`该产品没有订阅者`);
    }
  } catch (error) {
    logger.error('取消订阅警报失败:', error);
    throw new Error(`取消订阅警报失败: ${(error as Error).message}`);
  }
};

/**
 * 获取警报列表
 * @param level 可选的警报级别过滤
 * @param limit 可选的限制数量
 * @param productId 可选的产品ID过滤
 * @returns 警报列表
 */
export const getAlerts = (
  level?: 'high' | 'medium' | 'low',
  limit: number = 50,
  productId?: string
): SupplyChainAlert[] => {
  try {
    logger.info(`获取警报列表，级别: ${level || '所有'}，限制: ${limit}，产品ID: ${productId || '所有'}`);
    
    // 过滤和排序警报
    let filteredAlerts = [...alertStore];
    
    if (level) {
      filteredAlerts = filteredAlerts.filter(alert => alert.level === level);
    }
    
    if (productId) {
      filteredAlerts = filteredAlerts.filter(alert => alert.productId === productId);
    }
    
    // 按时间倒序排序，并限制数量
    const result = filteredAlerts
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, limit);
    
    logger.info(`找到 ${result.length} 条警报记录`);
    return result;
  } catch (error) {
    logger.error('获取警报列表失败:', error);
    throw new Error(`获取警报列表失败: ${(error as Error).message}`);
  }
};

/**
 * 确认警报
 * @param alertId 警报ID
 * @param userId 用户ID
 * @returns 已确认的警报
 */
export const acknowledgeAlert = (alertId: string, userId: string): SupplyChainAlert => {
  try {
    logger.info(`用户 ${userId} 确认警报 ${alertId}`);
    
    // 查找警报
    const alert = alertStore.find(a => a.id === alertId);
    if (!alert) {
      throw new Error(`未找到ID为 ${alertId} 的警报`);
    }
    
    // 如果警报已解决，则不能确认
    if (alert.status === 'resolved') {
      throw new Error('已解决的警报不能被确认');
    }
    
    // 更新警报状态
    alert.status = 'acknowledged';
    alert.acknowledgedBy = userId;
    alert.acknowledgedAt = new Date().toISOString();
    
    logger.info(`警报已确认`);
    return alert;
  } catch (error) {
    logger.error('确认警报失败:', error);
    throw new Error(`确认警报失败: ${(error as Error).message}`);
  }
};

/**
 * 解决警报
 * @param alertId 警报ID
 * @param userId 用户ID
 * @param resolution 解决方案
 * @returns 已解决的警报
 */
export const resolveAlert = (
  alertId: string,
  userId: string,
  resolution: string
): SupplyChainAlert => {
  try {
    logger.info(`用户 ${userId} 解决警报 ${alertId}`);
    
    // 查找警报
    const alert = alertStore.find(a => a.id === alertId);
    if (!alert) {
      throw new Error(`未找到ID为 ${alertId} 的警报`);
    }
    
    // 如果警报已解决，则不能再次解决
    if (alert.status === 'resolved') {
      throw new Error('警报已经被解决');
    }
    
    // 更新警报状态
    alert.status = 'resolved';
    alert.resolvedBy = userId;
    alert.resolvedAt = new Date().toISOString();
    alert.resolution = resolution;
    
    // 如果警报未被确认，则自动确认
    if (!alert.acknowledgedBy) {
      alert.acknowledgedBy = userId;
      alert.acknowledgedAt = alert.resolvedAt;
    }
    
    logger.info(`警报已解决`);
    return alert;
  } catch (error) {
    logger.error('解决警报失败:', error);
    throw new Error(`解决警报失败: ${(error as Error).message}`);
  }
};

/**
 * 获取警报统计信息
 * @returns 警报统计信息
 */
export const getAlertStatistics = (): Record<string, any> => {
  try {
    logger.info('获取警报统计信息');
    
    // 总警报数
    const totalAlerts = alertStore.length;
    
    // 按级别统计
    const alertsByLevel = {
      high: alertStore.filter(a => a.level === 'high').length,
      medium: alertStore.filter(a => a.level === 'medium').length,
      low: alertStore.filter(a => a.level === 'low').length
    };
    
    // 按状态统计
    const alertsByStatus = {
      open: alertStore.filter(a => a.status === 'open').length,
      acknowledged: alertStore.filter(a => a.status === 'acknowledged').length,
      resolved: alertStore.filter(a => a.status === 'resolved').length
    };
    
    // 按产品统计
    const alertsByProduct: Record<string, number> = {};
    alertStore.forEach(alert => {
      if (alertsByProduct[alert.productId]) {
        alertsByProduct[alert.productId]++;
      } else {
        alertsByProduct[alert.productId] = 1;
      }
    });
    
    // 按类型统计
    const alertsByType: Record<string, number> = {};
    alertStore.forEach(alert => {
      if (alertsByType[alert.type]) {
        alertsByType[alert.type]++;
      } else {
        alertsByType[alert.type] = 1;
      }
    });
    
    // 计算未解决的严重警报
    const unresolvedCritical = alertStore.filter(
      a => a.level === 'high' && a.status !== 'resolved'
    ).length;
    
    // 计算平均解决时间
    const resolvedAlerts = alertStore.filter(a => a.status === 'resolved' && a.resolvedAt && a.timestamp);
    let averageResolutionTime = 0;
    
    if (resolvedAlerts.length > 0) {
      const totalResolutionTime = resolvedAlerts.reduce((sum, alert) => {
        const createdTime = new Date(alert.timestamp).getTime();
        const resolvedTime = new Date(alert.resolvedAt!).getTime();
        return sum + (resolvedTime - createdTime);
      }, 0);
      
      // 平均解决时间（毫秒）
      averageResolutionTime = totalResolutionTime / resolvedAlerts.length;
    }
    
    return {
      totalAlerts,
      alertsByLevel,
      alertsByStatus,
      alertsByProduct,
      alertsByType,
      unresolvedCritical,
      averageResolutionTimeMs: averageResolutionTime,
      averageResolutionTimeHuman: `${Math.round(averageResolutionTime / (1000 * 60 * 60))} 小时`
    };
  } catch (error) {
    logger.error('获取警报统计信息失败:', error);
    throw new Error(`获取警报统计信息失败: ${(error as Error).message}`);
  }
}; 
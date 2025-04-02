import { v4 as uuidv4 } from 'uuid';
import { logger } from '../../utils/logger';
import { SupplyChainEvent } from '../../models/supply-chain.model';

// 模拟事件存储
const eventStore: SupplyChainEvent[] = [];

// 添加示例数据
const initSampleData = () => {
  if (eventStore.length === 0) {
    // 样品产品ID
    const productIds = ['PROD001', 'PROD002', 'PROD003'];
    
    // 红薯产品完整流程
    const sweetPotatoEvents: Partial<SupplyChainEvent>[] = [
      {
        productId: productIds[0],
        type: 'production_started',
        description: '有机红薯开始种植',
        timestamp: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        location: '河南省郑州市',
        metadata: { farmName: '阳光有机农场' }
      },
      {
        productId: productIds[0],
        type: 'production_completed',
        description: '有机红薯收获完成',
        timestamp: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
        location: '河南省郑州市',
        metadata: { yield: '5吨/亩', quality: '优' }
      },
      {
        productId: productIds[0],
        type: 'quality_check_started',
        description: '有机红薯开始质量检测',
        timestamp: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
        location: '河南省郑州市质检中心'
      },
      {
        productId: productIds[0],
        type: 'quality_check_passed',
        description: '有机红薯通过质量检测',
        timestamp: new Date(Date.now() - 13 * 24 * 60 * 60 * 1000).toISOString(),
        location: '河南省郑州市质检中心',
        metadata: { certifications: ['有机认证', '绿色食品认证'] }
      },
      {
        productId: productIds[0],
        type: 'packaging_started',
        description: '有机红薯开始包装',
        timestamp: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000).toISOString(),
        location: '河南省郑州市包装中心'
      },
      {
        productId: productIds[0],
        type: 'packaging_completed',
        description: '有机红薯包装完成',
        timestamp: new Date(Date.now() - 11 * 24 * 60 * 60 * 1000).toISOString(),
        location: '河南省郑州市包装中心',
        metadata: { packagingType: '环保包装', weight: '10kg/箱' }
      },
      {
        productId: productIds[0],
        type: 'storage_in',
        description: '有机红薯入库',
        timestamp: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
        location: '河南省郑州市中央仓库',
        metadata: { temperature: '15°C', humidity: '60%' }
      },
      {
        productId: productIds[0],
        type: 'shipment_started',
        description: '有机红薯开始运输',
        timestamp: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
        location: '河南省郑州市',
        metadata: { destination: '北京市', transportMethod: '冷链卡车' }
      },
      {
        productId: productIds[0],
        type: 'shipment_completed',
        description: '有机红薯运输完成',
        timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        location: '北京市',
        metadata: { arrivalCondition: '良好' }
      },
      {
        productId: productIds[0],
        type: 'storage_in',
        description: '有机红薯入北京仓库',
        timestamp: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
        location: '北京市丰台区仓库',
        metadata: { temperature: '15°C', humidity: '60%' }
      },
      {
        productId: productIds[0],
        type: 'delivery_started',
        description: '有机红薯开始配送到零售点',
        timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        location: '北京市',
        metadata: { destination: '北京市各大超市' }
      },
      {
        productId: productIds[0],
        type: 'delivery_completed',
        description: '有机红薯配送完成',
        timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        location: '北京市各大超市',
        metadata: { receivedBy: '超市采购部' }
      }
    ];
    
    // 蔬菜礼盒产品 - 有质量问题和延迟
    const vegetableBoxEvents: Partial<SupplyChainEvent>[] = [
      {
        productId: productIds[1],
        type: 'production_started',
        description: '绿色蔬菜礼盒产品开始生产',
        timestamp: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
        location: '山东省青岛市',
        metadata: { farmName: '绿盛农场' }
      },
      {
        productId: productIds[1],
        type: 'production_completed',
        description: '绿色蔬菜礼盒产品生产完成',
        timestamp: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000).toISOString(),
        location: '山东省青岛市',
        metadata: { components: ['胡萝卜', '白菜', '菠菜', '西红柿'] }
      },
      {
        productId: productIds[1],
        type: 'quality_check_started',
        description: '绿色蔬菜礼盒开始质检',
        timestamp: new Date(Date.now() - 11 * 24 * 60 * 60 * 1000).toISOString(),
        location: '山东省青岛市质检中心'
      },
      {
        productId: productIds[1],
        type: 'quality_issue',
        description: '部分菠菜叶片发黄',
        timestamp: new Date(Date.now() - 11 * 24 * 60 * 60 * 1000).toISOString(),
        location: '山东省青岛市质检中心',
        metadata: { issueType: '新鲜度不足', affectedComponents: ['菠菜'] }
      },
      {
        productId: productIds[1],
        type: 'quality_check_failed',
        description: '绿色蔬菜礼盒质检不通过',
        timestamp: new Date(Date.now() - 11 * 24 * 60 * 60 * 1000).toISOString(),
        location: '山东省青岛市质检中心'
      },
      {
        productId: productIds[1],
        type: 'production_started',
        description: '绿色蔬菜礼盒返回重新生产',
        timestamp: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
        location: '山东省青岛市',
        metadata: { correction: '更换新鲜菠菜' }
      },
      {
        productId: productIds[1],
        type: 'production_completed',
        description: '绿色蔬菜礼盒重新生产完成',
        timestamp: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000).toISOString(),
        location: '山东省青岛市'
      },
      {
        productId: productIds[1],
        type: 'quality_check_started',
        description: '绿色蔬菜礼盒重新质检',
        timestamp: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
        location: '山东省青岛市质检中心'
      },
      {
        productId: productIds[1],
        type: 'quality_check_passed',
        description: '绿色蔬菜礼盒通过质检',
        timestamp: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
        location: '山东省青岛市质检中心'
      },
      {
        productId: productIds[1],
        type: 'packaging_started',
        description: '绿色蔬菜礼盒开始包装',
        timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        location: '山东省青岛市包装中心'
      },
      {
        productId: productIds[1],
        type: 'packaging_completed',
        description: '绿色蔬菜礼盒包装完成',
        timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        location: '山东省青岛市包装中心',
        metadata: { packagingType: '可降解礼盒包装' }
      },
      {
        productId: productIds[1],
        type: 'shipment_started',
        description: '绿色蔬菜礼盒开始运输',
        timestamp: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
        location: '山东省青岛市',
        metadata: { destination: '上海市', transportMethod: '冷链物流' }
      },
      {
        productId: productIds[1],
        type: 'delay',
        description: '由于道路施工，运输延迟',
        timestamp: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
        location: '江苏省南通市',
        metadata: { expectedDelay: '48小时', reason: '高速道路维修' }
      },
      {
        productId: productIds[1],
        type: 'shipment_delayed',
        description: '运输延迟，预计晚到2天',
        timestamp: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
        location: '江苏省南通市'
      },
      {
        productId: productIds[1],
        type: 'shipment_completed',
        description: '绿色蔬菜礼盒运输完成',
        timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        location: '上海市'
      },
      {
        productId: productIds[1],
        type: 'delivery_started',
        description: '绿色蔬菜礼盒开始配送',
        timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        location: '上海市'
      },
      // 正在配送中...
    ];
    
    // 有机糙米产品 - 刚开始生产
    const brownRiceEvents: Partial<SupplyChainEvent>[] = [
      {
        productId: productIds[2],
        type: 'production_started',
        description: '有机糙米开始种植',
        timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        location: '黑龙江省哈尔滨市',
        metadata: { farmName: '北方有机农场', variety: '东北糯米' }
      },
      // 生产刚开始...
    ];
    
    // 将所有示例事件添加到事件存储
    const allSampleEvents = [...sweetPotatoEvents, ...vegetableBoxEvents, ...brownRiceEvents];
    
    // 为每个事件添加ID并存储
    allSampleEvents.forEach(event => {
      trackEvent({
        id: uuidv4(),
        ...event
      } as SupplyChainEvent);
    });
    
    logger.info(`已初始化 ${allSampleEvents.length} 条示例供应链事件数据`);
  }
};

// 初始化样例数据
initSampleData();

/**
 * 记录供应链事件
 * @param event 供应链事件
 * @returns 记录的事件
 */
export const trackEvent = (event: SupplyChainEvent): SupplyChainEvent => {
  try {
    logger.info(`记录供应链事件: ${event.type} 产品ID: ${event.productId}`);
    
    // 生成事件ID (如果没有提供)
    if (!event.id) {
      event.id = uuidv4();
    }
    
    // 设置时间戳 (如果没有提供)
    if (!event.timestamp) {
      event.timestamp = new Date().toISOString();
    }
    
    // 存储事件
    eventStore.push(event);
    
    // 更新产品状态
    updateProductStatus(event);
    
    logger.info(`事件已记录，ID: ${event.id}`);
    return event;
  } catch (error) {
    logger.error('记录供应链事件失败:', error);
    throw new Error(`记录供应链事件失败: ${(error as Error).message}`);
  }
};

/**
 * 根据事件类型更新产品状态
 * @param event 供应链事件
 */
const updateProductStatus = (event: SupplyChainEvent): void => {
  try {
    // 在真实系统中，这里会从数据库中获取产品并更新其状态
    // 在此模拟实现中，我们只记录状态变更
    const statusMap: Record<string, string> = {
      'production_started': '生产中',
      'production_completed': '生产完成',
      'packaging_started': '包装中',
      'packaging_completed': '包装完成',
      'quality_check_started': '质检中',
      'quality_check_passed': '质检通过',
      'quality_check_failed': '质检不通过',
      'shipment_started': '运输中',
      'shipment_completed': '运输完成',
      'storage_in': '入库',
      'storage_out': '出库',
      'delivered': '已交付',
      'returned': '已退回',
      'quality_issue': '质量问题',
      'delay': '延迟'
    };

    const status = statusMap[event.type];
    if (status) {
      logger.info(`更新产品 ${event.productId} 状态为: ${status}`);
    }
  } catch (error) {
    logger.error('更新产品状态失败:', error);
  }
};

/**
 * 获取产品事件历史
 * @param productId 产品ID
 * @returns 事件历史
 */
export const getProductEventHistory = (productId: string): SupplyChainEvent[] => {
  try {
    logger.info(`获取产品 ${productId} 的事件历史`);
    const events = eventStore.filter(event => event.productId === productId)
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    
    logger.info(`找到 ${events.length} 条事件记录`);
    return events;
  } catch (error) {
    logger.error(`获取产品 ${productId} 事件历史失败:`, error);
    throw new Error(`获取产品事件历史失败: ${(error as Error).message}`);
  }
};

/**
 * 获取最近的事件
 * @param limit 限制数量
 * @returns 最近的事件
 */
export const getRecentEvents = (limit: number = 10): SupplyChainEvent[] => {
  try {
    logger.info(`获取最近 ${limit} 条事件`);
    const events = [...eventStore]
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, limit);
    
    return events;
  } catch (error) {
    logger.error('获取最近事件失败:', error);
    throw new Error(`获取最近事件失败: ${(error as Error).message}`);
  }
};

/**
 * 获取事件统计信息
 * @returns 事件统计信息
 */
export const getEventStatistics = (): Record<string, any> => {
  try {
    logger.info('获取事件统计信息');
    
    // 总事件数
    const totalEvents = eventStore.length;
    
    // 按类型统计
    const eventsByType: Record<string, number> = {};
    eventStore.forEach(event => {
      if (eventsByType[event.type]) {
        eventsByType[event.type]++;
      } else {
        eventsByType[event.type] = 1;
      }
    });
    
    // 按产品统计
    const eventsByProduct: Record<string, number> = {};
    eventStore.forEach(event => {
      if (eventsByProduct[event.productId]) {
        eventsByProduct[event.productId]++;
      } else {
        eventsByProduct[event.productId] = 1;
      }
    });
    
    // 按日期统计
    const eventsByDate: Record<string, number> = {};
    eventStore.forEach(event => {
      const date = event.timestamp.split('T')[0]; // 取YYYY-MM-DD部分
      if (eventsByDate[date]) {
        eventsByDate[date]++;
      } else {
        eventsByDate[date] = 1;
      }
    });
    
    return {
      totalEvents,
      eventsByType,
      eventsByProduct,
      eventsByDate
    };
  } catch (error) {
    logger.error('获取事件统计信息失败:', error);
    throw new Error(`获取事件统计信息失败: ${(error as Error).message}`);
  }
}; 
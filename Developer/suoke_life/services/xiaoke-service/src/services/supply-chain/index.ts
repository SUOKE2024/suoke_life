import { logger } from '../../utils/logger';
import type { SupplyChainEvent, SupplyChainAlert } from '../../models/supply-chain.model';

// 导出供应链追踪服务
export { 
  trackEvent,
  getProductEventHistory,
  getRecentEvents,
  getEventStatistics
} from './tracking';

// 导出供应链分析服务
export {
  analyzeSupplyChain
} from './analytics';

// 导出供应链状态服务
export {
  getSupplyChainStatus
} from './status';

// 导出供应链预警服务
export {
  sendAlert,
  subscribeToAlerts,
  unsubscribeFromAlerts,
  getAlerts,
  acknowledgeAlert,
  resolveAlert,
  getAlertStatistics
} from './alerts';

/**
 * 供应链服务
 * 提供供应链跟踪、分析、状态监控和预警功能
 */

/**
 * 获取供应链信息
 * @param productId 产品ID
 * @returns 供应链综合信息
 */
export const getSupplyChainInfo = async (productId: string): Promise<any> => {
  try {
    logger.info(`请求供应链信息: ${productId}`);
    
    // 从各个服务获取信息
    const { getSupplyChainStatus } = await import('./status');
    const { analyzeSupplyChain } = await import('./analytics');
    const { getProductEventHistory } = await import('./tracking');
    
    // 获取供应链状态
    const status = getSupplyChainStatus(productId);
    
    // 获取供应链分析
    const analysis = analyzeSupplyChain(productId);
    
    // 获取事件历史
    const events = getProductEventHistory(productId);
    
    // 返回综合信息
    return {
      status,
      analysis,
      events: events.slice(0, 10), // 只返回最近10条事件
      summary: {
        productId,
        productName: status.productName,
        currentStage: status.currentStage,
        progress: status.progress,
        hasQualityIssues: status.hasQualityIssues,
        hasDelays: status.hasDelays,
        efficiencyScore: analysis.efficiencyScore,
        estimatedCompletionTime: status.estimatedCompletionTime,
        lastUpdateTime: status.lastUpdateTime,
        eventsCount: events.length
      }
    };
  } catch (error) {
    logger.error(`获取供应链信息失败: ${productId}`, error);
    throw new Error(`获取供应链信息失败: ${(error as Error).message}`);
  }
};

/**
 * 获取供应链可视化数据
 * @param productId 产品ID
 * @returns 供应链可视化数据
 */
export const getSupplyChainVisualization = async (productId: string): Promise<any> => {
  try {
    logger.info(`请求供应链可视化数据: ${productId}`);
    
    // 从各个服务获取信息
    const { getSupplyChainStatus } = await import('./status');
    const { getProductEventHistory } = await import('./tracking');
    
    // 获取供应链状态
    const status = getSupplyChainStatus(productId);
    
    // 获取事件历史
    const events = getProductEventHistory(productId);
    
    // 构建阶段节点数据
    const nodes = status.stages.map((stage: any, index: number) => ({
      id: `stage-${index}`,
      label: getStageLabel(stage.name),
      type: 'stage',
      status: stage.status,
      startTime: stage.startTime,
      endTime: stage.endTime,
      duration: stage.duration
    }));
    
    // 构建事件节点数据
    const eventNodes = events.map((event: any) => ({
      id: `event-${event.id || 'unknown'}`,
      label: event.type,
      type: 'event',
      description: event.description,
      timestamp: event.timestamp,
      location: event.location
    }));
    
    // 构建边数据 (阶段之间的连接)
    const edges = [];
    for (let i = 0; i < nodes.length - 1; i++) {
      edges.push({
        id: `edge-${i}`,
        source: nodes[i].id,
        target: nodes[i + 1].id,
        label: '下一阶段'
      });
    }
    
    // 构建事件与阶段的连接
    for (const event of events) {
      const stageIndex = getStageIndexByEventType(event.type);
      if (stageIndex >= 0) {
        edges.push({
          id: `edge-event-${event.id || 'unknown'}`,
          source: `event-${event.id || 'unknown'}`,
          target: `stage-${stageIndex}`,
          label: '关联'
        });
      }
    }
    
    return {
      nodes: [...nodes, ...eventNodes],
      edges,
      summary: {
        productId,
        productName: status.productName,
        currentStage: status.currentStage,
        progress: status.progress,
        hasQualityIssues: status.hasQualityIssues,
        hasDelays: status.hasDelays
      }
    };
  } catch (error) {
    logger.error(`获取供应链可视化数据失败: ${productId}`, error);
    throw new Error(`获取供应链可视化数据失败: ${(error as Error).message}`);
  }
};

/**
 * 记录供应链事件
 * @param event 供应链事件
 * @returns 记录的事件
 */
export const recordSupplyChainEvent = async (event: SupplyChainEvent): Promise<any> => {
  try {
    logger.info(`记录供应链事件: ${event.type} - ${event.productId}`);
    
    const { trackEvent } = await import('./tracking');
    const { sendAlert } = await import('./alerts');
    
    // 记录事件
    const recordedEvent = trackEvent(event);
    
    // 根据事件类型决定是否需要发送预警
    if (shouldSendAlert(event)) {
      await sendAlert({
        title: getAlertTitleByEventType(event.type),
        message: event.description,
        level: getAlertLevelByEventType(event.type) as any,
        productId: event.productId,
        eventId: recordedEvent.id,
        timestamp: new Date().toISOString()
      } as SupplyChainAlert);
    }
    
    return recordedEvent;
  } catch (error) {
    logger.error(`记录供应链事件失败: ${event.type} - ${event.productId}`, error);
    throw new Error(`记录供应链事件失败: ${(error as Error).message}`);
  }
};

/**
 * 获取阶段标签
 * @param stageName 阶段名称
 * @returns 阶段显示标签
 */
const getStageLabel = (stageName: string): string => {
  const stageLabels: Record<string, string> = {
    'production': '生产',
    'quality': '质检',
    'packaging': '包装',
    'storage': '仓储',
    'shipment': '运输',
    'delivery': '配送',
    'completed': '完成'
  };
  
  return stageLabels[stageName] || stageName;
};

/**
 * 获取事件类型对应的阶段索引
 * @param eventType 事件类型
 * @returns 阶段索引
 */
const getStageIndexByEventType = (eventType: string): number => {
  if (eventType.includes('production')) return 0;
  if (eventType.includes('quality')) return 1;
  if (eventType.includes('packaging')) return 2;
  if (eventType.includes('storage')) return 3;
  if (eventType.includes('shipment')) return 4;
  if (eventType.includes('delivery') || eventType === 'delivered') return 5;
  return -1;
};

/**
 * 判断是否需要发送预警
 * @param event 供应链事件
 * @returns 是否需要发送预警
 */
const shouldSendAlert = (event: SupplyChainEvent): boolean => {
  const alertTriggerTypes = [
    'quality_issue',
    'quality_check_failed',
    'delay',
    'damage',
    'shipment_delayed',
    'low_inventory'
  ];
  
  return alertTriggerTypes.includes(event.type);
};

/**
 * 获取事件类型对应的预警标题
 * @param eventType 事件类型
 * @returns 预警标题
 */
const getAlertTitleByEventType = (eventType: string): string => {
  const alertTitles: Record<string, string> = {
    'quality_issue': '产品质量问题',
    'quality_check_failed': '质检不通过',
    'delay': '供应链延迟',
    'damage': '产品损坏',
    'shipment_delayed': '运输延迟',
    'low_inventory': '库存不足'
  };
  
  return alertTitles[eventType] || `供应链问题: ${eventType}`;
};

/**
 * 获取事件类型对应的预警级别
 * @param eventType 事件类型
 * @returns 预警级别
 */
const getAlertLevelByEventType = (eventType: string): string => {
  const criticalAlerts = ['quality_issue', 'damage'];
  const warningAlerts = ['quality_check_failed', 'shipment_delayed', 'delay'];
  const infoAlerts = ['low_inventory'];
  
  if (criticalAlerts.includes(eventType)) return 'critical';
  if (warningAlerts.includes(eventType)) return 'warning';
  if (infoAlerts.includes(eventType)) return 'info';
  
  return 'info'; // 默认级别
}; 
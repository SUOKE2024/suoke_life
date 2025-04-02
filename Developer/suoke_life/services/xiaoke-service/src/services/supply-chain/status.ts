import { v4 as uuidv4 } from 'uuid';
import { logger } from '../../utils/logger';
import { getProductEventHistory } from './tracking';
import { SupplyChainStatus, SupplyChainStage, SupplyChainEvent } from '../../models/supply-chain.model';

// 模拟产品名称缓存
const productNameCache: Record<string, string> = {};

// 产品状态存储
const productStatusStore: Record<string, SupplyChainStatus> = {};

// 产品阶段映射
const stageMap: Record<string, string> = {
  'production_started': '生产',
  'production_completed': '生产完成',
  'quality_check_started': '质检',
  'quality_check_passed': '质检通过',
  'quality_check_failed': '质检不通过',
  'packaging_started': '包装',
  'packaging_completed': '包装完成',
  'shipment_started': '运输',
  'shipment_completed': '运输完成',
  'storage_in': '入库',
  'storage_out': '出库',
  'delivery_started': '配送',
  'delivery_completed': '配送完成'
};

// 产品状态示例数据
const initSampleStatusData = () => {
  // 产品ID
  const productIds = ['PROD001', 'PROD002', 'PROD003'];
  
  // 有机红薯 - 已完成配送
  const sweetPotatoStages: SupplyChainStage[] = [
    {
      id: 'stage-prod-001',
      name: '生产',
      status: 'completed',
      startTime: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      endTime: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
      duration: 15 * 24 * 60 * 60 * 1000,
      notes: '有机红薯种植与收获，由阳光有机农场完成'
    },
    {
      id: 'stage-qc-001',
      name: '质检',
      status: 'completed',
      startTime: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
      endTime: new Date(Date.now() - 13 * 24 * 60 * 60 * 1000).toISOString(),
      duration: 1 * 24 * 60 * 60 * 1000,
      notes: '有机认证和绿色食品认证'
    },
    {
      id: 'stage-pack-001',
      name: '包装',
      status: 'completed',
      startTime: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000).toISOString(),
      endTime: new Date(Date.now() - 11 * 24 * 60 * 60 * 1000).toISOString(),
      duration: 1 * 24 * 60 * 60 * 1000,
      notes: '使用环保材料包装，每箱10kg'
    },
    {
      id: 'stage-ship-001',
      name: '运输',
      status: 'completed',
      startTime: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
      endTime: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      duration: 3 * 24 * 60 * 60 * 1000,
      notes: '从河南郑州运往北京，使用冷链卡车'
    },
    {
      id: 'stage-deliver-001',
      name: '配送',
      status: 'completed',
      startTime: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      endTime: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      duration: 1 * 24 * 60 * 60 * 1000,
      notes: '配送至北京各大超市'
    }
  ];
  
  // 蔬菜礼盒 - 配送中
  const vegetableBoxStages: SupplyChainStage[] = [
    {
      id: 'stage-prod-002',
      name: '生产',
      status: 'completed',
      startTime: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
      endTime: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000).toISOString(),
      duration: 11 * 24 * 60 * 60 * 1000,
      notes: '包含重新生产环节，由于菠菜质量问题'
    },
    {
      id: 'stage-qc-002',
      name: '质检',
      status: 'completed',
      startTime: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
      endTime: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
      duration: 12 * 60 * 60 * 1000,
      notes: '二次质检通过'
    },
    {
      id: 'stage-pack-002',
      name: '包装',
      status: 'completed',
      startTime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      endTime: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      duration: 8 * 60 * 60 * 1000,
      notes: '使用可降解礼盒包装'
    },
    {
      id: 'stage-ship-002',
      name: '运输',
      status: 'completed',
      startTime: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
      endTime: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
      duration: 4 * 24 * 60 * 60 * 1000,
      notes: '从山东青岛运往上海，出现48小时延迟'
    },
    {
      id: 'stage-deliver-002',
      name: '配送',
      status: 'in_progress',
      startTime: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
      endTime: null,
      duration: null,
      notes: '正在配送至上海各零售点'
    }
  ];
  
  // 有机糙米 - 刚开始生产
  const brownRiceStages: SupplyChainStage[] = [
    {
      id: 'stage-prod-003',
      name: '生产',
      status: 'in_progress',
      startTime: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      endTime: null,
      duration: null,
      notes: '东北糯米品种，由北方有机农场种植'
    }
  ];
  
  // 初始化产品状态
  productStatusStore[productIds[0]] = {
    productId: productIds[0],
    currentStage: '配送完成',
    progress: 100,
    stages: sweetPotatoStages,
    startTime: sweetPotatoStages[0].startTime,
    lastUpdateTime: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    estimatedCompletion: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    actualCompletion: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    isCompleted: true,
    qualityIssues: []
  };
  
  productStatusStore[productIds[1]] = {
    productId: productIds[1],
    currentStage: '配送',
    progress: 90,
    stages: vegetableBoxStages,
    startTime: vegetableBoxStages[0].startTime,
    lastUpdateTime: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    estimatedCompletion: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString(),
    actualCompletion: null,
    isCompleted: false,
    qualityIssues: [
      {
        issueType: '新鲜度不足',
        description: '部分菠菜叶片发黄',
        detectedAt: new Date(Date.now() - 11 * 24 * 60 * 60 * 1000).toISOString(),
        resolvedAt: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000).toISOString(),
        resolution: '更换新鲜菠菜'
      }
    ]
  };
  
  productStatusStore[productIds[2]] = {
    productId: productIds[2],
    currentStage: '生产',
    progress: 10,
    stages: brownRiceStages,
    startTime: brownRiceStages[0].startTime,
    lastUpdateTime: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    estimatedCompletion: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000).toISOString(),
    actualCompletion: null,
    isCompleted: false,
    qualityIssues: []
  };
  
  logger.info('已初始化示例产品状态数据');
};

// 初始化示例数据
initSampleStatusData();

/**
 * 获取供应链状态
 * @param productId 产品ID
 * @returns 供应链状态
 */
export const getSupplyChainStatus = (productId: string): SupplyChainStatus => {
  try {
    logger.info(`获取产品 ${productId} 的供应链状态`);
    
    // 检查是否已有状态
    if (productStatusStore[productId]) {
      return productStatusStore[productId];
    }
    
    // 如果没有状态，根据事件生成新状态
    const events = getProductEventHistory(productId);
    if (events.length === 0) {
      throw new Error(`未找到产品 ${productId} 的事件记录`);
    }
    
    // 分析事件，构建供应链阶段
    const stages: SupplyChainStage[] = [];
    let currentStage = '';
    let currentStageStartTime = '';
    
    // 整理事件并构建阶段
    for (const event of events) {
      // 查找阶段名称
      const stageName = getStageFromEvent(event.type);
      if (!stageName) continue;
      
      // 检查是否为阶段开始事件
      if (event.type.endsWith('_started') || event.type === 'storage_in') {
        currentStage = stageName;
        currentStageStartTime = event.timestamp;
      } 
      // 检查是否为阶段结束事件
      else if (event.type.endsWith('_completed') || event.type === 'storage_out') {
        // 确认是同一阶段
        if (getBaseStage(event.type) === getBaseStage(currentStage)) {
          const stage: SupplyChainStage = {
            id: `stage-${getBaseStage(currentStage)}-${productId}`,
            name: currentStage,
            status: 'completed',
            startTime: currentStageStartTime,
            endTime: event.timestamp,
            duration: new Date(event.timestamp).getTime() - new Date(currentStageStartTime).getTime(),
            notes: `${currentStage}阶段从${new Date(currentStageStartTime).toLocaleString()}到${new Date(event.timestamp).toLocaleString()}`
          };
          
          stages.push(stage);
          currentStage = '';
          currentStageStartTime = '';
        }
      }
    }
    
    // 检查是否有未完成的阶段
    if (currentStage && currentStageStartTime) {
      const stage: SupplyChainStage = {
        id: `stage-${getBaseStage(currentStage)}-${productId}`,
        name: currentStage,
        status: 'in_progress',
        startTime: currentStageStartTime,
        endTime: null,
        duration: null,
        notes: `${currentStage}阶段从${new Date(currentStageStartTime).toLocaleString()}开始，尚未完成`
      };
      
      stages.push(stage);
    }
    
    // 计算进度
    const progress = calculateProgress(stages, events);
    
    // 检查质量问题
    const qualityIssues = events
      .filter(event => event.type === 'quality_issue')
      .map(event => ({
        issueType: event.metadata?.issueType || '未知问题',
        description: event.description,
        detectedAt: event.timestamp,
        resolvedAt: null,
        resolution: null
      }));
    
    // 构建状态
    const status: SupplyChainStatus = {
      productId,
      currentStage: currentStage || (stages.length > 0 ? stages[stages.length - 1].name : '未开始'),
      progress,
      stages,
      startTime: events[0].timestamp,
      lastUpdateTime: events[events.length - 1].timestamp,
      estimatedCompletion: calculateEstimatedCompletion(events, progress),
      actualCompletion: progress === 100 ? events[events.length - 1].timestamp : null,
      isCompleted: progress === 100,
      qualityIssues
    };
    
    // 存储状态
    productStatusStore[productId] = status;
    
    return status;
  } catch (error) {
    logger.error(`获取产品 ${productId} 供应链状态失败:`, error);
    throw new Error(`获取供应链状态失败: ${(error as Error).message}`);
  }
};

/**
 * 从事件类型中获取阶段名称
 * @param eventType 事件类型
 * @returns 阶段名称
 */
const getStageFromEvent = (eventType: string): string => {
  return stageMap[eventType] || '';
};

/**
 * 获取基础阶段名称
 * @param stageOrEvent 阶段名称或事件类型
 * @returns 基础阶段名称
 */
const getBaseStage = (stageOrEvent: string): string => {
  if (stageOrEvent.includes('production')) return 'prod';
  if (stageOrEvent.includes('quality')) return 'qc';
  if (stageOrEvent.includes('packaging')) return 'pack';
  if (stageOrEvent.includes('shipment')) return 'ship';
  if (stageOrEvent.includes('storage')) return 'storage';
  if (stageOrEvent.includes('delivery')) return 'deliver';
  return 'unknown';
};

/**
 * 计算供应链进度
 * @param stages 供应链阶段
 * @param events 供应链事件
 * @returns 进度百分比
 */
const calculateProgress = (stages: SupplyChainStage[], events: any[]): number => {
  // 如果没有阶段，返回0
  if (stages.length === 0) return 0;
  
  // 统计完成的阶段
  const completedStages = stages.filter(stage => stage.status === 'completed').length;
  
  // 如果存在进行中的阶段
  const inProgressStage = stages.find(stage => stage.status === 'in_progress');
  if (inProgressStage) {
    // 基于时间估算进行中阶段的完成百分比
    const now = new Date().getTime();
    const stageStartTime = new Date(inProgressStage.startTime).getTime();
    
    // 估算该阶段的总时间（基于历史数据或默认值）
    let estimatedStageDuration = 0;
    const similarStages = stages.filter(
      s => s.status === 'completed' && s.name === inProgressStage.name
    );
    
    if (similarStages.length > 0) {
      // 使用类似阶段的平均持续时间
      estimatedStageDuration = similarStages.reduce((sum, s) => sum + (s.duration || 0), 0) / similarStages.length;
    } else {
      // 默认阶段持续时间（3天）
      estimatedStageDuration = 3 * 24 * 60 * 60 * 1000;
    }
    
    // 计算进行中阶段的估计完成百分比
    const elapsedTime = now - stageStartTime;
    const stageProgress = Math.min(100, Math.round((elapsedTime / estimatedStageDuration) * 100));
    
    // 计算总进度
    return Math.round((completedStages * 100 + stageProgress) / stages.length);
  }
  
  // 如果没有进行中的阶段，直接计算完成的阶段比例
  return Math.round((completedStages / stages.length) * 100);
};

/**
 * 计算预计完成时间
 * @param events 供应链事件
 * @param progress 当前进度
 * @returns 预计完成时间
 */
const calculateEstimatedCompletion = (events: any[], progress: number): string => {
  // 如果已完成，返回最后一个事件的时间
  if (progress === 100) {
    return events[events.length - 1].timestamp;
  }
  
  // 分析事件时间间隔估算剩余时间
  const eventTimes = events.map(e => new Date(e.timestamp).getTime());
  const timeIntervals: number[] = [];
  
  for (let i = 1; i < eventTimes.length; i++) {
    timeIntervals.push(eventTimes[i] - eventTimes[i - 1]);
  }
  
  // 如果没有足够的数据点，使用默认值（7天）
  if (timeIntervals.length < 2) {
    return new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();
  }
  
  // 计算平均时间间隔
  const avgInterval = timeIntervals.reduce((sum, interval) => sum + interval, 0) / timeIntervals.length;
  
  // 估算剩余时间
  const remainingPercentage = 100 - progress;
  const estimatedRemainingTime = (avgInterval * remainingPercentage) / (100 / events.length);
  
  return new Date(Date.now() + estimatedRemainingTime).toISOString();
};

/**
 * 获取产品名称
 * @param productId 产品ID
 * @returns 产品名称
 */
const getProductName = (productId: string): string => {
  // 从缓存获取名称
  if (productNameCache[productId]) {
    return productNameCache[productId];
  }
  
  // 在生产环境中，这里应该从产品数据库获取
  // 这里仅作模拟
  const mockProductNames = [
    '有机红薯',
    '绿色蔬菜礼盒',
    '有机糙米',
    '野生蓝莓',
    '原生态蜂蜜'
  ];
  
  const randomName = mockProductNames[Math.floor(Math.random() * mockProductNames.length)];
  const productName = `${randomName} (${productId.substring(0, 8)})`;
  
  // 存入缓存
  productNameCache[productId] = productName;
  
  return productName;
};

/**
 * 构建供应链阶段信息
 * @param events 事件列表
 * @returns 阶段信息
 */
const buildStages = (events: SupplyChainEvent[]): SupplyChainStatus['stages'] => {
  // 定义所有阶段
  const stages: SupplyChainStatus['stages'] = [
    { name: 'production', status: 'pending' },
    { name: 'quality', status: 'pending' },
    { name: 'packaging', status: 'pending' },
    { name: 'storage', status: 'pending' },
    { name: 'shipment', status: 'pending' },
    { name: 'delivery', status: 'pending' },
    { name: 'completed', status: 'pending' }
  ];
  
  // 按照时间顺序处理事件
  const sortedEvents = [...events].sort((a, b) => 
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );
  
  // 映射事件类型到阶段
  const eventTypeToStage: Record<string, SupplyChainStage> = {
    // 生产阶段
    'production_started': 'production',
    'production_completed': 'production',
    
    // 质检阶段
    'quality_check_started': 'quality',
    'quality_check_passed': 'quality',
    'quality_check_failed': 'quality',
    
    // 包装阶段
    'packaging_started': 'packaging',
    'packaging_completed': 'packaging',
    
    // 仓储阶段
    'storage_in': 'storage',
    'storage_out': 'storage',
    
    // 运输阶段
    'shipment_started': 'shipment',
    'shipment_completed': 'shipment',
    
    // 配送阶段
    'delivery_started': 'delivery',
    'delivery_completed': 'delivery',
    'delivered': 'completed'
  };
  
  // 处理事件更新阶段状态
  sortedEvents.forEach(event => {
    const stage = eventTypeToStage[event.type];
    
    if (stage) {
      const stageIndex = getStageIndexByName(stages, stage);
      
      if (stageIndex !== -1) {
        const stageObj = stages[stageIndex];
        
        // 根据事件类型更新阶段状态
        if (event.type.includes('_started')) {
          stageObj.status = 'in_progress';
          stageObj.startTime = event.timestamp;
        } else if (event.type.includes('_completed') || event.type === 'delivered') {
          stageObj.status = 'completed';
          stageObj.endTime = event.timestamp;
          
          // 计算耗时
          if (stageObj.startTime) {
            const startTime = new Date(stageObj.startTime).getTime();
            const endTime = new Date(stageObj.endTime).getTime();
            stageObj.duration = endTime - startTime;
          }
          
          // 如果当前阶段完成，开始下一个阶段
          if (stageIndex < stages.length - 1) {
            stages[stageIndex + 1].status = 'in_progress';
            stages[stageIndex + 1].startTime = event.timestamp;
          }
        } else if (event.type.includes('_failed')) {
          stageObj.status = 'failed';
        }
      }
    }
  });
  
  return stages;
};

/**
 * 获取阶段索引
 * @param stages 阶段列表
 * @param stageName 阶段名称
 * @returns 阶段索引
 */
const getStageIndexByName = (stages: SupplyChainStatus['stages'], stageName: SupplyChainStage): number => {
  return stages.findIndex(stage => stage.name === stageName);
};

/**
 * 确定当前阶段
 * @param stages 阶段列表
 * @returns 当前阶段
 */
const determineCurrentStage = (stages: SupplyChainStatus['stages']): SupplyChainStage => {
  // 查找第一个正在进行中的阶段
  const inProgressStage = stages.find(stage => stage.status === 'in_progress');
  
  if (inProgressStage) {
    return inProgressStage.name;
  }
  
  // 查找第一个待处理的阶段
  const pendingStage = stages.find(stage => stage.status === 'pending');
  
  if (pendingStage) {
    return pendingStage.name;
  }
  
  // 如果所有阶段都已完成
  const completedStage = stages.find(stage => stage.name === 'completed');
  
  if (completedStage && completedStage.status === 'completed') {
    return 'completed';
  }
  
  // 默认返回生产阶段
  return 'production';
};

/**
 * 计算进度
 * @param stages 阶段列表
 * @param currentStage 当前阶段
 * @returns 进度（0-100）
 */
const calculateProgress = (stages: SupplyChainStatus['stages'], currentStage: SupplyChainStage): number => {
  // 阶段权重（总和为100）
  const stageWeights: Record<SupplyChainStage, number> = {
    'production': 20,
    'quality': 10,
    'packaging': 15,
    'storage': 10,
    'shipment': 20,
    'delivery': 15,
    'completed': 10
  };
  
  let progress = 0;
  let currentStageProgress = 0;
  
  // 计算已完成阶段的进度
  stages.forEach(stage => {
    if (stage.status === 'completed') {
      progress += stageWeights[stage.name as SupplyChainStage];
    } else if (stage.status === 'in_progress' && stage.name === currentStage) {
      // 计算当前阶段的进度
      if (stage.startTime) {
        const startTime = new Date(stage.startTime).getTime();
        const currentTime = new Date().getTime();
        const stageDuration = currentTime - startTime;
        
        // 估计当前阶段完成的百分比（简单模拟）
        const expectedDuration = getExpectedDuration(stage.name as SupplyChainStage);
        let stageProgressPercent = Math.min(stageDuration / expectedDuration, 1);
        
        if (isNaN(stageProgressPercent)) {
          stageProgressPercent = 0.5; // 默认50%
        }
        
        currentStageProgress = stageWeights[stage.name as SupplyChainStage] * stageProgressPercent;
      } else {
        // 如果没有开始时间，默认阶段进度为50%
        currentStageProgress = stageWeights[stage.name as SupplyChainStage] * 0.5;
      }
    }
  });
  
  // 总进度 = 已完成阶段进度 + 当前阶段进度
  progress += currentStageProgress;
  
  // 确保进度在0-100之间
  return Math.min(Math.max(0, Math.round(progress)), 100);
};

/**
 * 获取预期阶段持续时间（毫秒）
 * @param stageName 阶段名称
 * @returns 预期持续时间
 */
const getExpectedDuration = (stageName: SupplyChainStage): number => {
  // 各阶段预期持续时间（以小时为单位）
  const expectedHours: Record<SupplyChainStage, number> = {
    'production': 48,  // 2天
    'quality': 24,     // 1天
    'packaging': 24,   // 1天
    'storage': 72,     // 3天
    'shipment': 120,   // 5天
    'delivery': 48,    // 2天
    'completed': 0
  };
  
  return expectedHours[stageName] * 60 * 60 * 1000;
};

/**
 * 获取最后更新时间
 * @param events 事件列表
 * @returns 最后更新时间
 */
const getLastUpdateTime = (events: SupplyChainEvent[]): string => {
  // 按时间排序获取最新事件
  const sortedEvents = [...events].sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
  
  return sortedEvents[0]?.timestamp || new Date().toISOString();
};

/**
 * 估计完成时间
 * @param events 事件列表
 * @param stages 阶段列表
 * @param currentStage 当前阶段
 * @returns 估计完成时间
 */
const estimateCompletionTime = (
  events: SupplyChainEvent[], 
  stages: SupplyChainStatus['stages'],
  currentStage: SupplyChainStage
): string => {
  // 如果已完成，返回最后事件的时间
  if (currentStage === 'completed') {
    const completedEvents = events.filter(event => event.type === 'delivered');
    
    if (completedEvents.length > 0) {
      return completedEvents[completedEvents.length - 1].timestamp;
    }
  }
  
  // 获取当前时间
  const now = new Date();
  
  // 查找当前阶段索引
  const currentStageIndex = getStageIndexByName(stages, currentStage);
  
  if (currentStageIndex === -1) {
    return new Date(now.getTime() + (7 * 24 * 60 * 60 * 1000)).toISOString(); // 默认7天后
  }
  
  // 当前阶段剩余时间
  let remainingTime = 0;
  const currentStageObj = stages[currentStageIndex];
  
  if (currentStageObj.status === 'in_progress' && currentStageObj.startTime) {
    const startTime = new Date(currentStageObj.startTime).getTime();
    const elapsedTime = now.getTime() - startTime;
    const expectedDuration = getExpectedDuration(currentStage);
    
    // 剩余时间 = 预期时间 - 已经过时间
    remainingTime = Math.max(0, expectedDuration - elapsedTime);
  } else {
    // 如果阶段还未开始，使用完整的预期时间
    remainingTime = getExpectedDuration(currentStage);
  }
  
  // 未开始的后续阶段时间
  let futureStagesTime = 0;
  
  for (let i = currentStageIndex + 1; i < stages.length; i++) {
    if (stages[i].status === 'pending') {
      futureStagesTime += getExpectedDuration(stages[i].name as SupplyChainStage);
    }
  }
  
  // 估计完成时间 = 当前时间 + 当前阶段剩余时间 + 后续阶段时间
  const estimatedTime = now.getTime() + remainingTime + futureStagesTime;
  
  return new Date(estimatedTime).toISOString();
}; 
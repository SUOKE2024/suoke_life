import { v4 as uuidv4 } from 'uuid';
import { logger } from '../../utils/logger';
import { getProductEventHistory } from '../supply-chain/tracking';
import { getSupplyChainStatus } from '../supply-chain/status';
import { getProductEnvironmentData } from '../iot/supply-chain-sensors';

// 风险预测结果接口
export interface SupplyChainRiskPrediction {
  id: string;
  productId: string;
  timestamp: string;
  risks: {
    type: string;
    probability: number; // 0-1
    severity: number; // 1-10
    impact: number; // 1-10
    description: string;
    suggestedActions: string[];
    expectedTimeframe: string;
  }[];
  overallRiskScore: number; // 0-100
  confidenceScore: number; // 0-100
  nextUpdateTime: string;
}

// 存储预测结果
const predictionsStore: SupplyChainRiskPrediction[] = [];

/**
 * 预测供应链风险
 */
export const predictSupplyChainRisks = async (productId: string): Promise<SupplyChainRiskPrediction> => {
  try {
    logger.info(`预测供应链风险: ${productId}`);
    
    // 检查缓存中是否有最近的预测结果
    const cachedPrediction = predictionsStore.find(p => 
      p.productId === productId && 
      (new Date().getTime() - new Date(p.timestamp).getTime() < 3600000) // 一小时内的预测
    );
    
    if (cachedPrediction) {
      logger.info(`使用缓存的风险预测: ${cachedPrediction.id}`);
      return cachedPrediction;
    }
    
    // 收集预测所需的数据
    const events = getProductEventHistory(productId);
    const status = getSupplyChainStatus(productId);
    const environmentData = getProductEnvironmentData(productId);
    
    // 使用智能体预测风险
    const prediction = await predictRisksWithAgent(productId, events, status, environmentData);
    
    // 存储预测结果
    predictionsStore.push(prediction);
    
    // 计划下一次预测
    scheduleNextPrediction(productId);
    
    logger.info(`供应链风险预测完成: ${prediction.id}`);
    return prediction;
  } catch (error) {
    logger.error('预测供应链风险失败:', error);
    throw new Error(`预测供应链风险失败: ${(error as Error).message}`);
  }
};

/**
 * 使用智能体预测风险
 */
const predictRisksWithAgent = async (
  productId: string, 
  events: any[], 
  status: any, 
  environmentData: any[]
): Promise<SupplyChainRiskPrediction> => {
  try {
    // 准备数据
    const predictionData = preparePredictionData(productId, events, status, environmentData);
    
    // 在实际实现中，这里应该调用模型进行预测
    // 模拟预测结果
    const simulatedRisks = simulatePrediction(productId, events, status, environmentData);
    
    // 创建预测结果
    const prediction: SupplyChainRiskPrediction = {
      id: uuidv4(),
      productId,
      timestamp: new Date().toISOString(),
      risks: simulatedRisks,
      overallRiskScore: calculateOverallRiskScore(simulatedRisks),
      confidenceScore: 85, // 模拟置信度分数
      nextUpdateTime: new Date(Date.now() + 3600000).toISOString() // 一小时后更新
    };
    
    return prediction;
  } catch (error) {
    logger.error('智能体风险预测失败:', error);
    throw error;
  }
};

/**
 * 准备预测数据
 */
const preparePredictionData = (
  productId: string,
  events: any[],
  status: any,
  environmentData: any[]
): any => {
  // 提取相关特征用于预测
  return {
    productId,
    currentStage: status.currentStage,
    progress: status.progress,
    hasQualityIssues: status.hasQualityIssues,
    hasDelays: status.hasDelays,
    eventCount: events.length,
    eventTypes: events.reduce((counts: any, event: any) => {
      counts[event.type] = (counts[event.type] || 0) + 1;
      return counts;
    }, {}),
    stageDurations: status.stages.reduce((durations: any, stage: any) => {
      if (stage.startTime && stage.endTime) {
        durations[stage.name] = new Date(stage.endTime).getTime() - new Date(stage.startTime).getTime();
      }
      return durations;
    }, {}),
    environmentDataSummary: summarizeEnvironmentData(environmentData)
  };
};

/**
 * 总结环境数据
 */
const summarizeEnvironmentData = (data: any[]): any => {
  const summary: any = {};
  
  // 按类型分组
  const groupedData = data.reduce((groups: any, item: any) => {
    const group = groups[item.type] || [];
    group.push(item);
    groups[item.type] = group;
    return groups;
  }, {});
  
  // 计算每种类型的统计数据
  for (const type in groupedData) {
    const values = groupedData[type].map((item: any) => item.value);
    summary[type] = {
      min: Math.min(...values),
      max: Math.max(...values),
      avg: values.reduce((sum: number, val: number) => sum + val, 0) / values.length,
      count: values.length,
      hasAnomalies: values.some((val: number) => {
        const threshold = thresholdConfig[type];
        return threshold && (val < threshold.min || val > threshold.max);
      })
    };
  }
  
  return summary;
};

/**
 * 计算整体风险分数
 */
const calculateOverallRiskScore = (risks: any[]): number => {
  if (risks.length === 0) {
    return 0;
  }
  
  const riskScores = risks.map(risk => risk.probability * risk.severity * risk.impact);
  const maxPossibleScore = 10 * 10; // 最大可能分数 (probability * severity * impact)
  const avgRiskScore = riskScores.reduce((sum, score) => sum + score, 0) / risks.length;
  
  // 将分数标准化到0-100
  return Math.min(100, (avgRiskScore / maxPossibleScore) * 100);
};

/**
 * 模拟风险预测结果
 */
const simulatePrediction = (
  productId: string,
  events: any[],
  status: any,
  environmentData: any[]
): any[] => {
  const risks = [];
  
  // 基于产品当前状态生成可能的风险
  
  // 检查是否有质量问题
  if (status.hasQualityIssues) {
    risks.push({
      type: 'quality_degradation',
      probability: 0.8,
      severity: 7,
      impact: 8,
      description: '产品质量可能进一步下降，影响消费者满意度和品牌声誉',
      suggestedActions: [
        '立即进行全批次复检',
        '重新审核质量控制流程',
        '暂停相关产品线生产进行调整'
      ],
      expectedTimeframe: '3-5天内'
    });
  }
  
  // 检查是否有延迟
  if (status.hasDelays) {
    risks.push({
      type: 'delivery_delay',
      probability: 0.75,
      severity: 6,
      impact: 7,
      description: '配送延迟可能进一步扩大，导致配送窗口无法达成',
      suggestedActions: [
        '重新安排运输计划',
        '通知客户可能的延误',
        '启用备选物流供应商'
      ],
      expectedTimeframe: '1-2天内'
    });
  }
  
  // 基于环境数据检查潜在风险
  const tempData = environmentData.filter(d => d.type === 'temperature');
  if (tempData.length > 0) {
    const recentTemp = tempData[0].value;
    if (recentTemp > 25) {
      risks.push({
        type: 'spoilage_risk',
        probability: 0.6,
        severity: 8,
        impact: 9,
        description: '高温环境可能导致产品加速变质或损坏',
        suggestedActions: [
          '降低存储温度',
          '加速运输流程',
          '增加冷链监控频率'
        ],
        expectedTimeframe: '12-24小时内'
      });
    }
  }
  
  // 基于事件历史检查潜在风险
  const qualityIssueEvents = events.filter(e => e.type === 'quality_issue');
  if (qualityIssueEvents.length >= 2) {
    risks.push({
      type: 'systematic_quality_issue',
      probability: 0.65,
      severity: 9,
      impact: 8,
      description: '可能存在系统性质量问题，影响整批产品',
      suggestedActions: [
        '召开质量紧急会议',
        '审查所有相关供应商',
        '考虑召回风险评估'
      ],
      expectedTimeframe: '1-3天内'
    });
  }
  
  // 添加随机的季节性风险因素
  if (Math.random() > 0.7) {
    risks.push({
      type: 'weather_disruption',
      probability: 0.4,
      severity: 5,
      impact: 6,
      description: '最近的天气预报显示可能有恶劣天气，影响运输',
      suggestedActions: [
        '监控天气预报',
        '准备备选路线',
        '提前调整配送计划'
      ],
      expectedTimeframe: '3-7天内'
    });
  }
  
  return risks;
};

/**
 * 计划下一次预测
 */
const scheduleNextPrediction = (productId: string): void => {
  // 一小时后执行新的预测
  setTimeout(() => {
    predictSupplyChainRisks(productId).catch(err => 
      logger.error(`计划的风险预测失败: ${err.message}`)
    );
  }, 3600000); // 一小时
};

// 传感器阈值配置
const thresholdConfig: Record<string, {min: number, max: number}> = {
  temperature: { min: 0, max: 30 },
  humidity: { min: 20, max: 80 },
  light: { min: 0, max: 1000 },
  pressure: { min: 900, max: 1100 }
};
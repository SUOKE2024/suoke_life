import { logger } from '../../utils/logger';
import { SupplyChainAnalysis } from '../../models/supply-chain.model';
import { getProductEventHistory } from './tracking';
import { getSupplyChainStatus } from './status';

// 分析结果缓存
const analysisCache: Record<string, SupplyChainAnalysis> = {};

// 初始化样例分析数据
const initSampleAnalysisData = () => {
  // 样品产品ID
  const productIds = ['PROD001', 'PROD002', 'PROD003'];
  
  // 有机红薯 - 完整流程
  analysisCache[productIds[0]] = {
    productId: productIds[0],
    timeMetrics: {
      totalTime: 29 * 24 * 60 * 60 * 1000, // 29天
      productionTime: 15 * 24 * 60 * 60 * 1000, // 15天
      qualityCheckTime: 1 * 24 * 60 * 60 * 1000, // 1天
      packagingTime: 1 * 24 * 60 * 60 * 1000, // 1天
      shippingTime: 3 * 24 * 60 * 60 * 1000, // 3天
      storageTime: 8 * 24 * 60 * 60 * 1000, // 8天
      deliveryTime: 1 * 24 * 60 * 60 * 1000 // 1天
    },
    efficiencyScores: {
      overall: 85,
      production: 80,
      logistics: 90,
      quality: 95
    },
    bottlenecks: [
      {
        stage: "生产",
        score: 80,
        reason: "生产周期较长，可以通过优化种植方法提高效率"
      }
    ],
    recommendations: [
      "采用先进的农业技术缩短生产周期",
      "优化仓储流程，减少入库和出库时间",
      "建立更加直接的配送渠道，减少中间环节"
    ],
    risks: [
      {
        type: "环境风险",
        likelihood: "中",
        impact: "高",
        description: "极端天气可能影响农作物产量和质量"
      },
      {
        type: "物流风险",
        likelihood: "低",
        impact: "中",
        description: "长途运输可能造成产品损坏"
      }
    ],
    comparisonWithIndustry: {
      productionTimePerformance: "一般",
      qualityPerformance: "优秀",
      logisticsPerformance: "良好",
      overallPerformance: "良好"
    }
  };
  
  // 蔬菜礼盒 - 有质量问题和延迟
  analysisCache[productIds[1]] = {
    productId: productIds[1],
    timeMetrics: {
      totalTime: 19 * 24 * 60 * 60 * 1000, // 19天（还未完成）
      productionTime: 11 * 24 * 60 * 60 * 1000, // 11天（包括重新生产）
      qualityCheckTime: 2 * 24 * 60 * 60 * 1000, // 2天（包括两次质检）
      packagingTime: 1 * 24 * 60 * 60 * 1000, // 1天
      shippingTime: 4 * 24 * 60 * 60 * 1000, // 4天（包括延迟）
      storageTime: 0, // 无存储时间
      deliveryTime: 1 * 24 * 60 * 60 * 1000 // 1天（正在进行）
    },
    efficiencyScores: {
      overall: 65,
      production: 60,
      logistics: 70,
      quality: 50
    },
    bottlenecks: [
      {
        stage: "质量控制",
        score: 50,
        reason: "质检不通过导致返工，严重影响效率"
      },
      {
        stage: "运输",
        score: 70,
        reason: "道路施工导致延迟，可以提前规划路线"
      }
    ],
    recommendations: [
      "加强原材料质量控制，减少返工",
      "在运输前进行路线规划，避开施工路段",
      "建立更完善的质量预警机制，及早发现问题"
    ],
    risks: [
      {
        type: "质量风险",
        likelihood: "高",
        impact: "高",
        description: "新鲜蔬菜容易出现品质问题"
      },
      {
        type: "延迟风险",
        likelihood: "中",
        impact: "高",
        description: "运输延迟导致产品新鲜度下降"
      }
    ],
    comparisonWithIndustry: {
      productionTimePerformance: "较差",
      qualityPerformance: "较差",
      logisticsPerformance: "一般",
      overallPerformance: "较差"
    }
  };
  
  // 有机糙米 - 刚开始生产
  analysisCache[productIds[2]] = {
    productId: productIds[2],
    timeMetrics: {
      totalTime: 5 * 24 * 60 * 60 * 1000, // 5天（刚开始）
      productionTime: 5 * 24 * 60 * 60 * 1000, // 5天（正在进行）
      qualityCheckTime: 0, // 未开始
      packagingTime: 0, // 未开始
      shippingTime: 0, // 未开始
      storageTime: 0, // 未开始
      deliveryTime: 0 // 未开始
    },
    efficiencyScores: {
      overall: 90, // 预估值，实际进展良好
      production: 90,
      logistics: null, // 未开始
      quality: null // 未开始
    },
    bottlenecks: [], // 尚未发现瓶颈
    recommendations: [
      "监控天气变化，及时调整种植计划",
      "提前准备质检和包装资源，避免后续环节延迟"
    ],
    risks: [
      {
        type: "气候风险",
        likelihood: "中",
        impact: "高",
        description: "低温可能影响水稻生长"
      }
    ],
    comparisonWithIndustry: {
      productionTimePerformance: "优秀", // 预估值
      qualityPerformance: null, // 未开始
      logisticsPerformance: null, // 未开始
      overallPerformance: "待评估" // 尚未完成足够环节
    }
  };
  
  logger.info('已初始化示例供应链分析数据');
};

// 初始化示例数据
initSampleAnalysisData();

/**
 * 分析供应链
 * @param productId 产品ID
 * @returns 供应链分析结果
 */
export const analyzeSupplyChain = (productId: string): SupplyChainAnalysis => {
  try {
    logger.info(`分析产品 ${productId} 的供应链`);
    
    // 检查缓存
    if (analysisCache[productId]) {
      logger.info(`使用缓存的供应链分析结果`);
      return analysisCache[productId];
    }
    
    // 获取供应链状态和事件历史
    const status = getSupplyChainStatus(productId);
    const events = getProductEventHistory(productId);
    
    if (events.length === 0) {
      throw new Error(`未找到产品 ${productId} 的事件记录`);
    }
    
    // 计算时间指标
    const timeMetrics = calculateTimeMetrics(events, status);
    
    // 计算效率分数
    const efficiencyScores = calculateEfficiencyScores(events, timeMetrics, status);
    
    // 识别瓶颈
    const bottlenecks = identifyBottlenecks(efficiencyScores, events, status);
    
    // 生成建议
    const recommendations = generateRecommendations(bottlenecks, events, status);
    
    // 评估风险
    const risks = assessRisks(events, status);
    
    // 与行业比较
    const comparisonWithIndustry = compareWithIndustry(efficiencyScores, timeMetrics);
    
    // 构建分析结果
    const analysis: SupplyChainAnalysis = {
      productId,
      timeMetrics,
      efficiencyScores,
      bottlenecks,
      recommendations,
      risks,
      comparisonWithIndustry
    };
    
    // 缓存分析结果
    analysisCache[productId] = analysis;
    
    return analysis;
  } catch (error) {
    logger.error(`分析产品 ${productId} 供应链失败:`, error);
    throw new Error(`分析供应链失败: ${(error as Error).message}`);
  }
};

/**
 * 计算时间指标
 */
const calculateTimeMetrics = (events: any[], status: any): any => {
  // 计算各阶段时间
  const stageTimings: Record<string, number> = {};
  
  // 基于已完成的阶段计算时间
  status.stages.forEach((stage: any) => {
    if (stage.status === 'completed' && stage.duration) {
      const baseStage = getBaseStage(stage.name);
      if (stageTimings[baseStage]) {
        stageTimings[baseStage] += stage.duration;
      } else {
        stageTimings[baseStage] = stage.duration;
      }
    }
  });
  
  // 计算总时间
  const totalTime = Object.values(stageTimings).reduce((sum: number, time: number) => sum + time, 0);
  
  return {
    totalTime,
    productionTime: stageTimings.production || 0,
    qualityCheckTime: stageTimings.quality || 0,
    packagingTime: stageTimings.packaging || 0,
    shippingTime: stageTimings.shipping || 0,
    storageTime: stageTimings.storage || 0,
    deliveryTime: stageTimings.delivery || 0
  };
};

/**
 * 获取基础阶段名称
 */
const getBaseStage = (stageName: string): string => {
  if (stageName.includes('生产')) return 'production';
  if (stageName.includes('质检')) return 'quality';
  if (stageName.includes('包装')) return 'packaging';
  if (stageName.includes('运输')) return 'shipping';
  if (stageName.includes('仓储') || stageName.includes('入库')) return 'storage';
  if (stageName.includes('配送')) return 'delivery';
  return 'other';
};

/**
 * 计算效率分数
 */
const calculateEfficiencyScores = (events: any[], timeMetrics: any, status: any): any => {
  // 行业基准时间（毫秒）
  const benchmarks = {
    production: 20 * 24 * 60 * 60 * 1000, // 20天
    quality: 2 * 24 * 60 * 60 * 1000, // 2天
    packaging: 1 * 24 * 60 * 60 * 1000, // 1天
    shipping: 3 * 24 * 60 * 60 * 1000, // 3天
    storage: 5 * 24 * 60 * 60 * 1000, // 5天
    delivery: 1 * 24 * 60 * 60 * 1000 // 1天
  };
  
  // 计算生产效率分数
  const productionScore = calculateEfficiencyScore(
    timeMetrics.productionTime, 
    benchmarks.production
  );
  
  // 计算物流效率分数（包括运输、仓储和配送）
  const logisticsTime = timeMetrics.shippingTime + timeMetrics.storageTime + timeMetrics.deliveryTime;
  const logisticsBenchmark = benchmarks.shipping + benchmarks.storage + benchmarks.delivery;
  const logisticsScore = calculateEfficiencyScore(logisticsTime, logisticsBenchmark);
  
  // 计算质量效率分数（包括质检和包装）
  const qualityTime = timeMetrics.qualityCheckTime + timeMetrics.packagingTime;
  const qualityBenchmark = benchmarks.quality + benchmarks.packaging;
  const qualityScore = calculateEfficiencyScore(qualityTime, qualityBenchmark);
  
  // 检查是否有质量问题
  const hasQualityIssues = events.some(event => 
    event.type === 'quality_issue' || event.type === 'quality_check_failed'
  );
  
  // 如果有质量问题，降低质量分数
  const adjustedQualityScore = hasQualityIssues ? Math.max(0, qualityScore - 30) : qualityScore;
  
  // 检查是否有延迟
  const hasDelays = events.some(event => 
    event.type === 'delay' || event.type === 'shipment_delayed'
  );
  
  // 如果有延迟，降低物流分数
  const adjustedLogisticsScore = hasDelays ? Math.max(0, logisticsScore - 20) : logisticsScore;
  
  // 计算总体效率分数
  const overallScore = calculateWeightedAverage([
    { value: productionScore, weight: 0.4 },
    { value: adjustedLogisticsScore, weight: 0.3 },
    { value: adjustedQualityScore, weight: 0.3 }
  ]);
  
  return {
    overall: Math.round(overallScore),
    production: Math.round(productionScore),
    logistics: adjustedLogisticsScore ? Math.round(adjustedLogisticsScore) : null,
    quality: adjustedQualityScore ? Math.round(adjustedQualityScore) : null
  };
};

/**
 * 计算效率分数
 * @param actualTime 实际时间
 * @param benchmarkTime 基准时间
 * @returns 效率分数
 */
const calculateEfficiencyScore = (actualTime: number, benchmarkTime: number): number => {
  if (actualTime === 0) return null; // 如果时间为0，表示该阶段尚未开始
  
  // 分数计算公式：100 - 20 * (实际时间 / 基准时间 - 1)
  // 如果实际时间等于基准时间，得分为100
  // 如果实际时间为基准时间的150%，得分为90
  // 如果实际时间为基准时间的50%，得分为110
  const ratio = actualTime / benchmarkTime;
  
  if (ratio <= 0.5) {
    // 如果时间非常短，可能是数据问题，或者确实非常高效
    return 100 + 20;
  } else if (ratio >= 2) {
    // 如果时间是基准的两倍以上，效率很低
    return Math.max(0, 100 - 20 * (ratio - 1));
  } else {
    // 正常范围内的计算
    return 100 + 20 * (1 - ratio);
  }
};

/**
 * 计算加权平均值
 * @param items 带权重的项目
 * @returns 加权平均值
 */
const calculateWeightedAverage = (items: Array<{value: number, weight: number}>): number => {
  // 过滤掉null值
  const validItems = items.filter(item => item.value !== null);
  
  if (validItems.length === 0) return null;
  
  // 重新计算权重总和
  const totalWeight = validItems.reduce((sum, item) => sum + item.weight, 0);
  
  // 计算加权平均值
  return validItems.reduce((sum, item) => sum + item.value * (item.weight / totalWeight), 0);
};

/**
 * 识别瓶颈
 */
const identifyBottlenecks = (efficiencyScores: any, events: any[], status: any): any[] => {
  const bottlenecks = [];
  
  // 检查生产效率
  if (efficiencyScores.production !== null && efficiencyScores.production < 80) {
    bottlenecks.push({
      stage: "生产",
      score: efficiencyScores.production,
      reason: "生产周期较长，可考虑优化生产流程"
    });
  }
  
  // 检查物流效率
  if (efficiencyScores.logistics !== null && efficiencyScores.logistics < 80) {
    const delayEvents = events.filter(event => 
      event.type === 'delay' || event.type === 'shipment_delayed'
    );
    
    let reason = "物流效率较低";
    if (delayEvents.length > 0) {
      const latestDelay = delayEvents[delayEvents.length - 1];
      reason = `运输延迟: ${latestDelay.description || '未知原因'}`;
    }
    
    bottlenecks.push({
      stage: "物流",
      score: efficiencyScores.logistics,
      reason
    });
  }
  
  // 检查质量效率
  if (efficiencyScores.quality !== null && efficiencyScores.quality < 80) {
    const qualityIssueEvents = events.filter(event => 
      event.type === 'quality_issue' || event.type === 'quality_check_failed'
    );
    
    let reason = "质量控制效率较低";
    if (qualityIssueEvents.length > 0) {
      const latestIssue = qualityIssueEvents[qualityIssueEvents.length - 1];
      reason = `质量问题: ${latestIssue.description || '未知问题'}`;
    }
    
    bottlenecks.push({
      stage: "质量控制",
      score: efficiencyScores.quality,
      reason
    });
  }
  
  return bottlenecks;
};

/**
 * 生成建议
 */
const generateRecommendations = (bottlenecks: any[], events: any[], status: any): string[] => {
  const recommendations = [];
  
  // 根据瓶颈提供建议
  bottlenecks.forEach(bottleneck => {
    switch (bottleneck.stage) {
      case "生产":
        recommendations.push("优化生产流程，减少生产周期");
        recommendations.push("增加自动化程度，提高生产效率");
        break;
      case "物流":
        recommendations.push("优化运输路线，避开拥堵区域");
        recommendations.push("与多家物流供应商合作，减少依赖单一供应商的风险");
        break;
      case "质量控制":
        recommendations.push("加强原材料质量控制，减少后期问题");
        recommendations.push("完善质量检验标准，提高检测效率");
        break;
    }
  });
  
  // 如果没有瓶颈但有特定事件，也提供建议
  if (bottlenecks.length === 0) {
    // 检查是否有库存超时
    const storageEvents = events.filter(event => 
      event.type === 'storage_in' || event.type === 'storage_out'
    );
    
    if (storageEvents.length >= 2) {
      const storageDuration = calculateStorageDuration(storageEvents);
      if (storageDuration > 7 * 24 * 60 * 60 * 1000) { // 如果存储超过7天
        recommendations.push("减少仓储时间，加快周转率");
      }
    }
    
    // 如果没有任何建议，添加通用建议
    if (recommendations.length === 0) {
      recommendations.push("持续监控供应链各环节，保持高效运行");
      recommendations.push("建立供应商评估机制，确保合作伙伴质量");
    }
  }
  
  return recommendations;
};

/**
 * 计算存储时间
 */
const calculateStorageDuration = (storageEvents: any[]): number => {
  let totalDuration = 0;
  let inTime = null;
  
  for (const event of storageEvents) {
    if (event.type === 'storage_in') {
      inTime = new Date(event.timestamp).getTime();
    } else if (event.type === 'storage_out' && inTime) {
      const outTime = new Date(event.timestamp).getTime();
      totalDuration += outTime - inTime;
      inTime = null;
    }
  }
  
  return totalDuration;
};

/**
 * 评估风险
 */
const assessRisks = (events: any[], status: any): any[] => {
  const risks = [];
  
  // 检查质量风险
  const qualityIssueEvents = events.filter(event => 
    event.type === 'quality_issue' || event.type === 'quality_check_failed'
  );
  
  if (qualityIssueEvents.length > 0) {
    risks.push({
      type: "质量风险",
      likelihood: qualityIssueEvents.length > 1 ? "高" : "中",
      impact: "高",
      description: "历史数据显示存在质量问题，可能影响产品质量和客户满意度"
    });
  }
  
  // 检查延迟风险
  const delayEvents = events.filter(event => 
    event.type === 'delay' || event.type === 'shipment_delayed'
  );
  
  if (delayEvents.length > 0) {
    risks.push({
      type: "延迟风险",
      likelihood: delayEvents.length > 1 ? "高" : "中",
      impact: "中",
      description: "历史数据显示存在延迟情况，可能影响交付时间"
    });
  }
  
  // 检查环境风险（根据产品类型）
  // 假设我们能从产品ID或事件中确定产品类型
  const isAgriculturalProduct = true; // 这里应该有一个判断逻辑
  
  if (isAgriculturalProduct) {
    risks.push({
      type: "环境风险",
      likelihood: "中",
      impact: "高",
      description: "农产品受气候条件影响较大，极端天气可能影响产量和质量"
    });
  }
  
  // 如果没有识别到风险，添加通用风险
  if (risks.length === 0) {
    risks.push({
      type: "供应链中断风险",
      likelihood: "低",
      impact: "高",
      description: "潜在的供应链中断可能导致生产延迟和客户满意度下降"
    });
  }
  
  return risks;
};

/**
 * 与行业比较
 */
const compareWithIndustry = (efficiencyScores: any, timeMetrics: any): any => {
  // 评估生产时间表现
  const productionTimePerformance = evaluatePerformance(efficiencyScores.production);
  
  // 评估质量表现
  const qualityPerformance = evaluatePerformance(efficiencyScores.quality);
  
  // 评估物流表现
  const logisticsPerformance = evaluatePerformance(efficiencyScores.logistics);
  
  // 评估总体表现
  const overallPerformance = evaluatePerformance(efficiencyScores.overall);
  
  return {
    productionTimePerformance,
    qualityPerformance,
    logisticsPerformance,
    overallPerformance
  };
};

/**
 * 评估表现
 * @param score 分数
 * @returns 表现评级
 */
const evaluatePerformance = (score: number): string => {
  if (score === null) return null;
  
  if (score >= 90) return "优秀";
  if (score >= 80) return "良好";
  if (score >= 70) return "一般";
  if (score >= 60) return "较差";
  return "差";
}; 
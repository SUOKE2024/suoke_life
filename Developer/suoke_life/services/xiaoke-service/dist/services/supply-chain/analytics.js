"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.analyzeSupplyChain = void 0;
const logger_1 = require("../../utils/logger");
const tracking_1 = require("./tracking");
// 行业平均数据（模拟）
const industryAverages = {
    production_time: 3.5, // 天
    packaging_time: 0.5, // 天
    shipment_time: 2.0, // 天
    delivery_time: 1.0, // 天
    total_time: 7.0, // 天
    quality_issues_rate: 0.05, // 5%
    delay_rate: 0.08, // 8%
};
/**
 * 分析供应链数据
 * @param productId 产品ID
 */
const analyzeSupplyChain = async (productId) => {
    try {
        logger_1.logger.info(`分析供应链: ${productId}`);
        // 获取产品事件历史
        const events = (0, tracking_1.getProductEventHistory)(productId);
        if (events.length === 0) {
            throw new Error(`未找到产品的供应链事件: ${productId}`);
        }
        // 获取各阶段时间
        const timeMetrics = calculateTimeMetrics(events);
        // 计算效率分数
        const efficiencyScore = calculateEfficiencyScore(timeMetrics);
        // 识别瓶颈
        const bottlenecks = identifyBottlenecks(timeMetrics);
        // 生成推荐
        const recommendations = generateRecommendations(bottlenecks, events);
        // 评估风险
        const riskAssessment = assessRisks(events, timeMetrics);
        // 与行业平均值比较
        const comparison = compareWithIndustryAverages(timeMetrics);
        return {
            productId,
            insights: {
                efficiencyScore,
                bottlenecks,
                recommendations,
                keyMetrics: {
                    ...timeMetrics,
                    qualityIssueRate: calculateQualityIssueRate(events),
                    delayRate: calculateDelayRate(events)
                }
            },
            riskAssessment,
            comparisonWithAverage: comparison,
            timestamp: new Date().toISOString()
        };
    }
    catch (error) {
        logger_1.logger.error(`分析供应链失败: ${productId}`, error);
        throw error;
    }
};
exports.analyzeSupplyChain = analyzeSupplyChain;
/**
 * 计算各阶段时间
 */
const calculateTimeMetrics = (events) => {
    const metrics = {
        production_time: 0,
        packaging_time: 0,
        shipment_time: 0,
        delivery_time: 0,
        total_time: 0
    };
    // 查找各阶段的开始和结束时间
    const productionStart = events.find(e => e.type === 'production_started');
    const productionEnd = events.find(e => e.type === 'production_completed');
    const packagingStart = events.find(e => e.type === 'packaging_started');
    const packagingEnd = events.find(e => e.type === 'packaging_completed');
    const shipmentStart = events.find(e => e.type === 'shipment_started');
    const shipmentEnd = events.find(e => e.type === 'shipment_completed');
    const deliveryStart = events.find(e => e.type === 'delivery_started');
    const deliveryEnd = events.find(e => e.type === 'delivery_completed');
    // 计算生产时间
    if (productionStart && productionEnd) {
        const start = new Date(productionStart.timestamp).getTime();
        const end = new Date(productionEnd.timestamp).getTime();
        metrics.production_time = (end - start) / (1000 * 60 * 60 * 24); // 转换为天
    }
    // 计算包装时间
    if (packagingStart && packagingEnd) {
        const start = new Date(packagingStart.timestamp).getTime();
        const end = new Date(packagingEnd.timestamp).getTime();
        metrics.packaging_time = (end - start) / (1000 * 60 * 60 * 24);
    }
    // 计算运输时间
    if (shipmentStart && shipmentEnd) {
        const start = new Date(shipmentStart.timestamp).getTime();
        const end = new Date(shipmentEnd.timestamp).getTime();
        metrics.shipment_time = (end - start) / (1000 * 60 * 60 * 24);
    }
    // 计算配送时间
    if (deliveryStart && deliveryEnd) {
        const start = new Date(deliveryStart.timestamp).getTime();
        const end = new Date(deliveryEnd.timestamp).getTime();
        metrics.delivery_time = (end - start) / (1000 * 60 * 60 * 24);
    }
    // 计算总时间
    if (productionStart && deliveryEnd) {
        const start = new Date(productionStart.timestamp).getTime();
        const end = new Date(deliveryEnd.timestamp).getTime();
        metrics.total_time = (end - start) / (1000 * 60 * 60 * 24);
    }
    else {
        metrics.total_time =
            metrics.production_time +
                metrics.packaging_time +
                metrics.shipment_time +
                metrics.delivery_time;
    }
    return metrics;
};
/**
 * 计算效率分数
 */
const calculateEfficiencyScore = (timeMetrics) => {
    // 权重
    const weights = {
        production_time: 0.3,
        packaging_time: 0.2,
        shipment_time: 0.25,
        delivery_time: 0.25
    };
    // 各阶段得分（与行业平均比较）
    const productionScore = industryAverages.production_time / (timeMetrics.production_time || 1) * 100;
    const packagingScore = industryAverages.packaging_time / (timeMetrics.packaging_time || 1) * 100;
    const shipmentScore = industryAverages.shipment_time / (timeMetrics.shipment_time || 1) * 100;
    const deliveryScore = industryAverages.delivery_time / (timeMetrics.delivery_time || 1) * 100;
    // 加权总分
    let score = productionScore * weights.production_time +
        packagingScore * weights.packaging_time +
        shipmentScore * weights.shipment_time +
        deliveryScore * weights.delivery_time;
    // 控制在0-100之间
    score = Math.max(0, Math.min(100, score));
    return Math.round(score);
};
/**
 * 识别瓶颈
 */
const identifyBottlenecks = (timeMetrics) => {
    const bottlenecks = [];
    // 与行业平均比较，识别瓶颈
    if (timeMetrics.production_time > industryAverages.production_time * 1.2) {
        bottlenecks.push('生产时间过长');
    }
    if (timeMetrics.packaging_time > industryAverages.packaging_time * 1.2) {
        bottlenecks.push('包装时间过长');
    }
    if (timeMetrics.shipment_time > industryAverages.shipment_time * 1.2) {
        bottlenecks.push('运输时间过长');
    }
    if (timeMetrics.delivery_time > industryAverages.delivery_time * 1.2) {
        bottlenecks.push('配送时间过长');
    }
    return bottlenecks;
};
/**
 * 生成推荐
 */
const generateRecommendations = (bottlenecks, events) => {
    const recommendations = [];
    // 根据瓶颈生成推荐
    for (const bottleneck of bottlenecks) {
        switch (bottleneck) {
            case '生产时间过长':
                recommendations.push('优化生产流程，考虑增加自动化程度');
                break;
            case '包装时间过长':
                recommendations.push('改进包装设备，提高包装效率');
                break;
            case '运输时间过长':
                recommendations.push('寻找更高效的物流合作伙伴或优化运输路线');
                break;
            case '配送时间过长':
                recommendations.push('优化配送路线和配送区域划分');
                break;
        }
    }
    // 检查质量问题
    const qualityIssues = events.filter(e => e.type === 'quality_issue');
    if (qualityIssues.length > 0) {
        recommendations.push('加强质量控制，减少质量问题');
    }
    // 检查延迟问题
    const delays = events.filter(e => e.type === 'delay');
    if (delays.length > 0) {
        recommendations.push('改进计划管理，减少延迟事件');
    }
    // 如果没有特定推荐，提供通用的改进建议
    if (recommendations.length === 0) {
        recommendations.push('持续监控供应链各环节，保持高效运作');
        recommendations.push('定期评估供应商绩效，确保合作伙伴可靠性');
    }
    return recommendations;
};
/**
 * 评估风险
 */
const assessRisks = (events, timeMetrics) => {
    // 计算风险因素
    const qualityIssueRate = calculateQualityIssueRate(events);
    const delayRate = calculateDelayRate(events);
    const timeEfficiency = industryAverages.total_time / (timeMetrics.total_time || 1);
    const factors = [];
    let overallRisk = 'low';
    // 评估质量风险
    if (qualityIssueRate > 0.1) {
        factors.push({
            name: '质量控制',
            risk: 'high',
            description: '质量问题发生率高于行业平均水平'
        });
        overallRisk = 'high';
    }
    else if (qualityIssueRate > 0.05) {
        factors.push({
            name: '质量控制',
            risk: 'medium',
            description: '质量问题发生率略高于行业平均水平'
        });
        overallRisk = overallRisk === 'low' ? 'medium' : overallRisk;
    }
    else {
        factors.push({
            name: '质量控制',
            risk: 'low',
            description: '质量问题发生率处于可接受范围'
        });
    }
    // 评估延迟风险
    if (delayRate > 0.15) {
        factors.push({
            name: '交付可靠性',
            risk: 'high',
            description: '延迟率显著高于行业平均水平'
        });
        overallRisk = 'high';
    }
    else if (delayRate > 0.08) {
        factors.push({
            name: '交付可靠性',
            risk: 'medium',
            description: '延迟率略高于行业平均水平'
        });
        overallRisk = overallRisk === 'low' ? 'medium' : overallRisk;
    }
    else {
        factors.push({
            name: '交付可靠性',
            risk: 'low',
            description: '延迟率处于可接受范围'
        });
    }
    // 评估时间效率风险
    if (timeEfficiency < 0.7) {
        factors.push({
            name: '时间效率',
            risk: 'high',
            description: '总处理时间显著长于行业平均水平'
        });
        overallRisk = 'high';
    }
    else if (timeEfficiency < 0.9) {
        factors.push({
            name: '时间效率',
            risk: 'medium',
            description: '总处理时间略长于行业平均水平'
        });
        overallRisk = overallRisk === 'low' ? 'medium' : overallRisk;
    }
    else {
        factors.push({
            name: '时间效率',
            risk: 'low',
            description: '总处理时间处于可接受范围'
        });
    }
    return {
        overallRisk,
        factors
    };
};
/**
 * 与行业平均值比较
 */
const compareWithIndustryAverages = (timeMetrics) => {
    const comparison = {};
    // 生产时间比较
    comparison.production_time = {
        value: timeMetrics.production_time,
        average: industryAverages.production_time,
        difference: timeMetrics.production_time - industryAverages.production_time
    };
    // 包装时间比较
    comparison.packaging_time = {
        value: timeMetrics.packaging_time,
        average: industryAverages.packaging_time,
        difference: timeMetrics.packaging_time - industryAverages.packaging_time
    };
    // 运输时间比较
    comparison.shipment_time = {
        value: timeMetrics.shipment_time,
        average: industryAverages.shipment_time,
        difference: timeMetrics.shipment_time - industryAverages.shipment_time
    };
    // 配送时间比较
    comparison.delivery_time = {
        value: timeMetrics.delivery_time,
        average: industryAverages.delivery_time,
        difference: timeMetrics.delivery_time - industryAverages.delivery_time
    };
    // 总时间比较
    comparison.total_time = {
        value: timeMetrics.total_time,
        average: industryAverages.total_time,
        difference: timeMetrics.total_time - industryAverages.total_time
    };
    return comparison;
};
/**
 * 计算质量问题率
 */
const calculateQualityIssueRate = (events) => {
    const qualityIssues = events.filter(e => e.type === 'quality_issue').length;
    const qualityChecks = events.filter(e => e.type === 'quality_check').length;
    return qualityChecks > 0 ? qualityIssues / qualityChecks : 0;
};
/**
 * 计算延迟率
 */
const calculateDelayRate = (events) => {
    const delays = events.filter(e => e.type === 'delay').length;
    const totalStages = events.filter(e => e.type === 'production_started' ||
        e.type === 'packaging_started' ||
        e.type === 'shipment_started' ||
        e.type === 'delivery_started').length;
    return totalStages > 0 ? delays / totalStages : 0;
};

"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getSupplyChainVisualization = exports.recordSupplyChainEvent = exports.getSupplyChainInfo = void 0;
const logger_1 = require("../../utils/logger");
const tracking_1 = require("./tracking");
const analytics_1 = require("./analytics");
const status_1 = require("./status");
const alerts_1 = require("./alerts");
/**
 * 供应链服务
 * 提供供应链跟踪、分析、状态监控和预警功能
 */
/**
 * 获取供应链信息
 * @param productId 产品ID
 */
const getSupplyChainInfo = async (productId) => {
    try {
        logger_1.logger.info(`获取供应链信息: ${productId}`);
        // 获取供应链状态
        const status = await (0, status_1.getSupplyChainStatus)(productId);
        // 获取供应链分析
        const analysis = await (0, analytics_1.analyzeSupplyChain)(productId);
        return {
            productId,
            status,
            analysis,
            timestamp: new Date().toISOString()
        };
    }
    catch (error) {
        logger_1.logger.error(`获取供应链信息失败: ${productId}`, error);
        throw error;
    }
};
exports.getSupplyChainInfo = getSupplyChainInfo;
/**
 * 记录供应链事件
 * @param event 供应链事件
 */
const recordSupplyChainEvent = async (event) => {
    try {
        logger_1.logger.info(`记录供应链事件: ${event.type} - ${event.productId}`);
        // 跟踪事件
        await (0, tracking_1.trackEvent)(event);
        // 检查是否需要发送预警
        const shouldAlert = checkAlertCondition(event);
        if (shouldAlert) {
            await (0, alerts_1.sendAlert)({
                level: 'warning',
                message: `供应链事件: ${event.type} - ${event.productId}`,
                details: event,
                timestamp: new Date().toISOString()
            });
        }
    }
    catch (error) {
        logger_1.logger.error(`记录供应链事件失败: ${event.type} - ${event.productId}`, error);
        throw error;
    }
};
exports.recordSupplyChainEvent = recordSupplyChainEvent;
/**
 * 检查是否需要发送预警
 * @param event 供应链事件
 */
const checkAlertCondition = (event) => {
    // 检查是否是延迟事件
    if (event.type === 'delay') {
        return true;
    }
    // 检查是否是质量问题事件
    if (event.type === 'quality_issue') {
        return true;
    }
    // 检查是否是库存不足事件
    if (event.type === 'low_inventory' && event.metadata && event.metadata.level < 10) {
        return true;
    }
    return false;
};
/**
 * 获取供应链可视化数据
 * @param productId 产品ID
 */
const getSupplyChainVisualization = async (productId) => {
    try {
        logger_1.logger.info(`获取供应链可视化数据: ${productId}`);
        // 获取供应链状态
        const status = await (0, status_1.getSupplyChainStatus)(productId);
        // 转换为可视化数据
        const visualizationData = transformToVisualizationData(status);
        return visualizationData;
    }
    catch (error) {
        logger_1.logger.error(`获取供应链可视化数据失败: ${productId}`, error);
        throw error;
    }
};
exports.getSupplyChainVisualization = getSupplyChainVisualization;
/**
 * 转换为可视化数据
 * @param status 供应链状态
 */
const transformToVisualizationData = (status) => {
    // 生成节点数据
    const nodes = status.stages.map((stage, index) => ({
        id: `node_${index}`,
        name: stage.name,
        status: stage.status,
        type: 'stage',
        position: { x: index * 200, y: 100 }
    }));
    // 生成连接数据
    const edges = [];
    for (let i = 0; i < nodes.length - 1; i++) {
        edges.push({
            id: `edge_${i}_${i + 1}`,
            source: nodes[i].id,
            target: nodes[i + 1].id,
            status: nodes[i].status === 'completed' && nodes[i + 1].status === 'completed' ? 'completed' : 'in_progress'
        });
    }
    return {
        nodes,
        edges,
        metadata: {
            productId: status.productId,
            productName: status.productName,
            currentStage: status.currentStage,
            estimatedCompletion: status.estimatedCompletion,
            lastUpdated: status.lastUpdated
        }
    };
};
exports.default = {
    getSupplyChainInfo: exports.getSupplyChainInfo,
    recordSupplyChainEvent: exports.recordSupplyChainEvent,
    getSupplyChainVisualization: exports.getSupplyChainVisualization
};

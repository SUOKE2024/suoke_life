"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getSupplyChainStatus = void 0;
const logger_1 = require("../../utils/logger");
const tracking_1 = require("./tracking");
// 模拟产品名称缓存
const productNameCache = {};
/**
 * 获取供应链状态
 * @param productId 产品ID
 * @returns 供应链状态
 */
const getSupplyChainStatus = (productId) => {
    try {
        logger_1.logger.info(`获取产品 ${productId} 的供应链状态`);
        // 获取产品事件历史
        const events = (0, tracking_1.getProductEventHistory)(productId);
        // 检查是否有事件
        if (events.length === 0) {
            throw new Error(`没有找到产品 ${productId} 的事件记录`);
        }
        // 获取产品名称
        const productName = getProductName(productId);
        // 构建阶段信息
        const stages = buildStages(events);
        // 确定当前阶段
        const currentStage = determineCurrentStage(stages);
        // 计算进度
        const progress = calculateProgress(stages, currentStage);
        // 检查是否有质量问题或延迟
        const hasQualityIssues = events.some(event => event.type === 'quality_issue' || event.type === 'quality_check_failed');
        const hasDelays = events.some(event => event.type === 'delay' || event.type === 'shipment_delayed');
        // 获取最后更新时间
        const lastUpdateTime = getLastUpdateTime(events);
        // 估计完成时间
        const estimatedCompletionTime = estimateCompletionTime(events, stages, currentStage);
        // 返回状态
        return {
            productId,
            productName,
            currentStage,
            progress,
            stages,
            lastUpdateTime,
            estimatedCompletionTime,
            hasQualityIssues,
            hasDelays
        };
    }
    catch (error) {
        logger_1.logger.error(`获取产品 ${productId} 供应链状态失败:`, error);
        throw new Error(`获取供应链状态失败: ${error.message}`);
    }
};
exports.getSupplyChainStatus = getSupplyChainStatus;
/**
 * 获取产品名称
 * @param productId 产品ID
 * @returns 产品名称
 */
const getProductName = (productId) => {
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
const buildStages = (events) => {
    // 定义所有阶段
    const stages = [
        { name: 'production', status: 'pending' },
        { name: 'quality', status: 'pending' },
        { name: 'packaging', status: 'pending' },
        { name: 'storage', status: 'pending' },
        { name: 'shipment', status: 'pending' },
        { name: 'delivery', status: 'pending' },
        { name: 'completed', status: 'pending' }
    ];
    // 按照时间顺序处理事件
    const sortedEvents = [...events].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    // 映射事件类型到阶段
    const eventTypeToStage = {
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
                }
                else if (event.type.includes('_completed') || event.type === 'delivered') {
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
                }
                else if (event.type.includes('_failed')) {
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
const getStageIndexByName = (stages, stageName) => {
    return stages.findIndex(stage => stage.name === stageName);
};
/**
 * 确定当前阶段
 * @param stages 阶段列表
 * @returns 当前阶段
 */
const determineCurrentStage = (stages) => {
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
const calculateProgress = (stages, currentStage) => {
    // 阶段权重（总和为100）
    const stageWeights = {
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
            progress += stageWeights[stage.name];
        }
        else if (stage.status === 'in_progress' && stage.name === currentStage) {
            // 计算当前阶段的进度
            if (stage.startTime) {
                const startTime = new Date(stage.startTime).getTime();
                const currentTime = new Date().getTime();
                const stageDuration = currentTime - startTime;
                // 估计当前阶段完成的百分比（简单模拟）
                const expectedDuration = getExpectedDuration(stage.name);
                let stageProgressPercent = Math.min(stageDuration / expectedDuration, 1);
                if (isNaN(stageProgressPercent)) {
                    stageProgressPercent = 0.5; // 默认50%
                }
                currentStageProgress = stageWeights[stage.name] * stageProgressPercent;
            }
            else {
                // 如果没有开始时间，默认阶段进度为50%
                currentStageProgress = stageWeights[stage.name] * 0.5;
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
const getExpectedDuration = (stageName) => {
    // 各阶段预期持续时间（以小时为单位）
    const expectedHours = {
        'production': 48, // 2天
        'quality': 24, // 1天
        'packaging': 24, // 1天
        'storage': 72, // 3天
        'shipment': 120, // 5天
        'delivery': 48, // 2天
        'completed': 0
    };
    return expectedHours[stageName] * 60 * 60 * 1000;
};
/**
 * 获取最后更新时间
 * @param events 事件列表
 * @returns 最后更新时间
 */
const getLastUpdateTime = (events) => {
    // 按时间排序获取最新事件
    const sortedEvents = [...events].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    return sortedEvents[0]?.timestamp || new Date().toISOString();
};
/**
 * 估计完成时间
 * @param events 事件列表
 * @param stages 阶段列表
 * @param currentStage 当前阶段
 * @returns 估计完成时间
 */
const estimateCompletionTime = (events, stages, currentStage) => {
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
    }
    else {
        // 如果阶段还未开始，使用完整的预期时间
        remainingTime = getExpectedDuration(currentStage);
    }
    // 未开始的后续阶段时间
    let futureStagesTime = 0;
    for (let i = currentStageIndex + 1; i < stages.length; i++) {
        if (stages[i].status === 'pending') {
            futureStagesTime += getExpectedDuration(stages[i].name);
        }
    }
    // 估计完成时间 = 当前时间 + 当前阶段剩余时间 + 后续阶段时间
    const estimatedTime = now.getTime() + remainingTime + futureStagesTime;
    return new Date(estimatedTime).toISOString();
};

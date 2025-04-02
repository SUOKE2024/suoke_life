"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getAlertStatistics = exports.resolveAlert = exports.acknowledgeAlert = exports.getAlerts = exports.unsubscribeFromAlerts = exports.subscribeToAlerts = exports.sendAlert = void 0;
const uuid_1 = require("uuid");
const logger_1 = require("../../utils/logger");
// 模拟预警存储
const alertStore = [];
const alertSubscribers = [];
/**
 * 发送供应链预警
 * @param alert 供应链预警
 * @returns 发送的预警
 */
const sendAlert = async (alert) => {
    try {
        logger_1.logger.info(`发送供应链预警: ${alert.title}, 级别: ${alert.level}`);
        // 生成预警ID (如果没有提供)
        if (!alert.id) {
            alert.id = (0, uuid_1.v4)();
        }
        // 设置时间戳 (如果没有提供)
        if (!alert.timestamp) {
            alert.timestamp = new Date().toISOString();
        }
        // 确保状态正确
        if (!alert.status) {
            alert.status = 'pending';
        }
        // 存储预警
        alertStore.push(alert);
        // 通知订阅者
        await notifySubscribers(alert);
        logger_1.logger.info(`预警已发送，ID: ${alert.id}`);
        return alert;
    }
    catch (error) {
        logger_1.logger.error('发送供应链预警失败:', error);
        throw new Error(`发送供应链预警失败: ${error.message}`);
    }
};
exports.sendAlert = sendAlert;
/**
 * 通知所有预警订阅者
 * @param alert 供应链预警
 */
const notifySubscribers = async (alert) => {
    try {
        logger_1.logger.info(`通知 ${alertSubscribers.length} 个预警订阅者`);
        for (const subscriber of alertSubscribers) {
            try {
                await subscriber(alert);
            }
            catch (error) {
                logger_1.logger.error('通知预警订阅者失败:', error);
            }
        }
    }
    catch (error) {
        logger_1.logger.error('通知预警订阅者失败:', error);
    }
};
/**
 * 订阅供应链预警
 * @param subscriber 订阅者回调函数
 */
const subscribeToAlerts = (subscriber) => {
    alertSubscribers.push(subscriber);
    logger_1.logger.info(`新增预警订阅者，当前共有 ${alertSubscribers.length} 个订阅者`);
};
exports.subscribeToAlerts = subscribeToAlerts;
/**
 * 取消订阅供应链预警
 * @param subscriber 订阅者回调函数
 */
const unsubscribeFromAlerts = (subscriber) => {
    const index = alertSubscribers.indexOf(subscriber);
    if (index !== -1) {
        alertSubscribers.splice(index, 1);
        logger_1.logger.info(`移除预警订阅者，当前剩余 ${alertSubscribers.length} 个订阅者`);
    }
};
exports.unsubscribeFromAlerts = unsubscribeFromAlerts;
/**
 * 获取预警列表
 * @param level 预警级别过滤
 * @param limit 限制数量
 * @returns 预警列表
 */
const getAlerts = (level, limit = 100) => {
    try {
        logger_1.logger.info(`获取预警列表，级别: ${level || '全部'}, 限制: ${limit}`);
        let alerts = [...alertStore];
        // 按级别过滤
        if (level) {
            alerts = alerts.filter(alert => alert.level === level);
        }
        // 按时间排序并限制数量
        alerts = alerts
            .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
            .slice(0, limit);
        logger_1.logger.info(`返回 ${alerts.length} 条预警`);
        return alerts;
    }
    catch (error) {
        logger_1.logger.error('获取预警列表失败:', error);
        throw new Error(`获取预警列表失败: ${error.message}`);
    }
};
exports.getAlerts = getAlerts;
/**
 * 确认预警
 * @param alertId 预警ID
 * @param userId 确认用户ID
 * @returns 更新后的预警
 */
const acknowledgeAlert = (alertId, userId) => {
    try {
        logger_1.logger.info(`确认预警，ID: ${alertId}, 用户ID: ${userId}`);
        const alertIndex = alertStore.findIndex(alert => alert.id === alertId);
        if (alertIndex === -1) {
            throw new Error(`预警不存在: ${alertId}`);
        }
        const alert = alertStore[alertIndex];
        alert.status = 'acknowledged';
        alert.acknowledgedBy = userId;
        alert.acknowledgedAt = new Date().toISOString();
        // 更新预警
        alertStore[alertIndex] = alert;
        logger_1.logger.info(`预警已确认，ID: ${alertId}`);
        return alert;
    }
    catch (error) {
        logger_1.logger.error('确认预警失败:', error);
        throw new Error(`确认预警失败: ${error.message}`);
    }
};
exports.acknowledgeAlert = acknowledgeAlert;
/**
 * 解决预警
 * @param alertId 预警ID
 * @returns 更新后的预警
 */
const resolveAlert = (alertId) => {
    try {
        logger_1.logger.info(`解决预警，ID: ${alertId}`);
        const alertIndex = alertStore.findIndex(alert => alert.id === alertId);
        if (alertIndex === -1) {
            throw new Error(`预警不存在: ${alertId}`);
        }
        const alert = alertStore[alertIndex];
        alert.status = 'resolved';
        alert.resolvedAt = new Date().toISOString();
        // 更新预警
        alertStore[alertIndex] = alert;
        logger_1.logger.info(`预警已解决，ID: ${alertId}`);
        return alert;
    }
    catch (error) {
        logger_1.logger.error('解决预警失败:', error);
        throw new Error(`解决预警失败: ${error.message}`);
    }
};
exports.resolveAlert = resolveAlert;
/**
 * 获取预警统计信息
 * @returns 预警统计信息
 */
const getAlertStatistics = () => {
    try {
        logger_1.logger.info('获取预警统计信息');
        // 总预警数
        const totalAlerts = alertStore.length;
        // 按状态统计
        const acknowledgedAlerts = alertStore.filter(alert => alert.status === 'acknowledged').length;
        const unacknowledgedAlerts = alertStore.filter(alert => alert.status === 'pending').length;
        const resolvedAlerts = alertStore.filter(alert => alert.status === 'resolved').length;
        const unresolvedAlerts = totalAlerts - resolvedAlerts;
        // 按级别统计
        const alertsByLevel = {};
        alertStore.forEach(alert => {
            if (alertsByLevel[alert.level]) {
                alertsByLevel[alert.level]++;
            }
            else {
                alertsByLevel[alert.level] = 1;
            }
        });
        // 按产品统计
        const alertsByProduct = {};
        alertStore.forEach(alert => {
            if (alert.productId) {
                if (alertsByProduct[alert.productId]) {
                    alertsByProduct[alert.productId]++;
                }
                else {
                    alertsByProduct[alert.productId] = 1;
                }
            }
        });
        // 按日期统计
        const alertsByDate = {};
        alertStore.forEach(alert => {
            const date = alert.timestamp.split('T')[0]; // 取YYYY-MM-DD部分
            if (alertsByDate[date]) {
                alertsByDate[date]++;
            }
            else {
                alertsByDate[date] = 1;
            }
        });
        return {
            totalAlerts,
            acknowledgedAlerts,
            unacknowledgedAlerts,
            resolvedAlerts,
            unresolvedAlerts,
            alertsByLevel,
            alertsByProduct,
            alertsByDate
        };
    }
    catch (error) {
        logger_1.logger.error('获取预警统计信息失败:', error);
        throw new Error(`获取预警统计信息失败: ${error.message}`);
    }
};
exports.getAlertStatistics = getAlertStatistics;

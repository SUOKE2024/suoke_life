"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getEventStatistics = exports.getRecentEvents = exports.getProductEventHistory = exports.trackEvent = void 0;
const uuid_1 = require("uuid");
const logger_1 = require("../../utils/logger");
// 模拟事件存储
const eventStore = [];
/**
 * 记录供应链事件
 * @param event 供应链事件
 * @returns 记录的事件
 */
const trackEvent = (event) => {
    try {
        logger_1.logger.info(`记录供应链事件: ${event.type} 产品ID: ${event.productId}`);
        // 生成事件ID (如果没有提供)
        if (!event.id) {
            event.id = (0, uuid_1.v4)();
        }
        // 设置时间戳 (如果没有提供)
        if (!event.timestamp) {
            event.timestamp = new Date().toISOString();
        }
        // 存储事件
        eventStore.push(event);
        // 更新产品状态
        updateProductStatus(event);
        logger_1.logger.info(`事件已记录，ID: ${event.id}`);
        return event;
    }
    catch (error) {
        logger_1.logger.error('记录供应链事件失败:', error);
        throw new Error(`记录供应链事件失败: ${error.message}`);
    }
};
exports.trackEvent = trackEvent;
/**
 * 根据事件类型更新产品状态
 * @param event 供应链事件
 */
const updateProductStatus = (event) => {
    try {
        // 在真实系统中，这里会从数据库中获取产品并更新其状态
        // 在此模拟实现中，我们只记录状态变更
        const statusMap = {
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
            logger_1.logger.info(`更新产品 ${event.productId} 状态为: ${status}`);
        }
    }
    catch (error) {
        logger_1.logger.error('更新产品状态失败:', error);
    }
};
/**
 * 获取产品事件历史
 * @param productId 产品ID
 * @returns 事件历史
 */
const getProductEventHistory = (productId) => {
    try {
        logger_1.logger.info(`获取产品 ${productId} 的事件历史`);
        const events = eventStore.filter(event => event.productId === productId)
            .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
        logger_1.logger.info(`找到 ${events.length} 条事件记录`);
        return events;
    }
    catch (error) {
        logger_1.logger.error(`获取产品 ${productId} 事件历史失败:`, error);
        throw new Error(`获取产品事件历史失败: ${error.message}`);
    }
};
exports.getProductEventHistory = getProductEventHistory;
/**
 * 获取最近的事件
 * @param limit 限制数量
 * @returns 最近的事件
 */
const getRecentEvents = (limit = 10) => {
    try {
        logger_1.logger.info(`获取最近 ${limit} 条事件`);
        const events = [...eventStore]
            .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
            .slice(0, limit);
        return events;
    }
    catch (error) {
        logger_1.logger.error('获取最近事件失败:', error);
        throw new Error(`获取最近事件失败: ${error.message}`);
    }
};
exports.getRecentEvents = getRecentEvents;
/**
 * 获取事件统计信息
 * @returns 事件统计信息
 */
const getEventStatistics = () => {
    try {
        logger_1.logger.info('获取事件统计信息');
        // 总事件数
        const totalEvents = eventStore.length;
        // 按类型统计
        const eventsByType = {};
        eventStore.forEach(event => {
            if (eventsByType[event.type]) {
                eventsByType[event.type]++;
            }
            else {
                eventsByType[event.type] = 1;
            }
        });
        // 按产品统计
        const eventsByProduct = {};
        eventStore.forEach(event => {
            if (eventsByProduct[event.productId]) {
                eventsByProduct[event.productId]++;
            }
            else {
                eventsByProduct[event.productId] = 1;
            }
        });
        // 按日期统计
        const eventsByDate = {};
        eventStore.forEach(event => {
            const date = event.timestamp.split('T')[0]; // 取YYYY-MM-DD部分
            if (eventsByDate[date]) {
                eventsByDate[date]++;
            }
            else {
                eventsByDate[date] = 1;
            }
        });
        return {
            totalEvents,
            eventsByType,
            eventsByProduct,
            eventsByDate
        };
    }
    catch (error) {
        logger_1.logger.error('获取事件统计信息失败:', error);
        throw new Error(`获取事件统计信息失败: ${error.message}`);
    }
};
exports.getEventStatistics = getEventStatistics;

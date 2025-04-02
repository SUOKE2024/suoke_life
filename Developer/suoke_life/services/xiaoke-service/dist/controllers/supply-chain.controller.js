"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.getAlertStatistics = exports.resolveAlert = exports.acknowledgeAlert = exports.getAlerts = exports.getEventStatistics = exports.getRecentEvents = exports.getProductEventHistory = exports.recordSupplyChainEvent = exports.getSupplyChainVisualization = exports.getSupplyChainInfo = void 0;
const logger_1 = require("../utils/logger");
const supplyChainService = __importStar(require("../services/supply-chain"));
/**
 * 获取供应链信息
 * @route GET /api/v1/supply-chain/:productId
 */
const getSupplyChainInfo = async (req, res) => {
    try {
        const { productId } = req.params;
        logger_1.logger.info(`请求供应链信息: ${productId}`);
        const supplyChainInfo = await supplyChainService.getSupplyChainInfo(productId);
        res.status(200).json({
            success: true,
            data: supplyChainInfo
        });
    }
    catch (error) {
        logger_1.logger.error('获取供应链信息失败', error);
        res.status(500).json({
            success: false,
            message: error instanceof Error ? error.message : '内部服务器错误',
            error: process.env.NODE_ENV === 'development' ? error : undefined
        });
    }
};
exports.getSupplyChainInfo = getSupplyChainInfo;
/**
 * 获取供应链可视化数据
 * @route GET /api/v1/supply-chain/:productId/visualization
 */
const getSupplyChainVisualization = async (req, res) => {
    try {
        const { productId } = req.params;
        logger_1.logger.info(`请求供应链可视化数据: ${productId}`);
        const visualizationData = await supplyChainService.getSupplyChainVisualization(productId);
        res.status(200).json({
            success: true,
            data: visualizationData
        });
    }
    catch (error) {
        logger_1.logger.error('获取供应链可视化数据失败', error);
        res.status(500).json({
            success: false,
            message: error instanceof Error ? error.message : '内部服务器错误',
            error: process.env.NODE_ENV === 'development' ? error : undefined
        });
    }
};
exports.getSupplyChainVisualization = getSupplyChainVisualization;
/**
 * 记录供应链事件
 * @route POST /api/v1/supply-chain/events
 */
const recordSupplyChainEvent = async (req, res) => {
    try {
        const eventData = req.body;
        // 数据验证
        if (!eventData.productId || !eventData.type || !eventData.description) {
            res.status(400).json({
                success: false,
                message: '请提供必要的事件数据：productId, type, description'
            });
            return;
        }
        logger_1.logger.info(`记录供应链事件: ${eventData.type} - ${eventData.productId}`);
        // 如果未提供时间戳，添加当前时间
        if (!eventData.timestamp) {
            eventData.timestamp = new Date().toISOString();
        }
        await supplyChainService.recordSupplyChainEvent(eventData);
        res.status(201).json({
            success: true,
            message: '事件已记录',
            data: { eventId: eventData.id }
        });
    }
    catch (error) {
        logger_1.logger.error('记录供应链事件失败', error);
        res.status(500).json({
            success: false,
            message: error instanceof Error ? error.message : '内部服务器错误',
            error: process.env.NODE_ENV === 'development' ? error : undefined
        });
    }
};
exports.recordSupplyChainEvent = recordSupplyChainEvent;
/**
 * 获取产品事件历史
 * @route GET /api/v1/supply-chain/:productId/events
 */
const getProductEventHistory = async (req, res) => {
    try {
        const { productId } = req.params;
        logger_1.logger.info(`请求产品事件历史: ${productId}`);
        // 这里直接从服务获取事件历史
        const events = supplyChainService.getProductEventHistory(productId);
        res.status(200).json({
            success: true,
            data: events
        });
    }
    catch (error) {
        logger_1.logger.error('获取产品事件历史失败', error);
        res.status(500).json({
            success: false,
            message: error instanceof Error ? error.message : '内部服务器错误',
            error: process.env.NODE_ENV === 'development' ? error : undefined
        });
    }
};
exports.getProductEventHistory = getProductEventHistory;
/**
 * 获取最近的事件
 * @route GET /api/v1/supply-chain/events/recent
 */
const getRecentEvents = async (req, res) => {
    try {
        // 从查询参数获取限制数量
        const limit = req.query.limit ? parseInt(req.query.limit, 10) : 10;
        logger_1.logger.info(`请求最近的事件 (限制: ${limit})`);
        // 这里直接从服务获取最近事件
        const events = supplyChainService.getRecentEvents(limit);
        res.status(200).json({
            success: true,
            data: events
        });
    }
    catch (error) {
        logger_1.logger.error('获取最近事件失败', error);
        res.status(500).json({
            success: false,
            message: error instanceof Error ? error.message : '内部服务器错误',
            error: process.env.NODE_ENV === 'development' ? error : undefined
        });
    }
};
exports.getRecentEvents = getRecentEvents;
/**
 * 获取事件统计信息
 * @route GET /api/v1/supply-chain/events/statistics
 */
const getEventStatistics = async (req, res) => {
    try {
        logger_1.logger.info('请求事件统计信息');
        // 这里直接从服务获取事件统计
        const statistics = supplyChainService.getEventStatistics();
        res.status(200).json({
            success: true,
            data: statistics
        });
    }
    catch (error) {
        logger_1.logger.error('获取事件统计信息失败', error);
        res.status(500).json({
            success: false,
            message: error instanceof Error ? error.message : '内部服务器错误',
            error: process.env.NODE_ENV === 'development' ? error : undefined
        });
    }
};
exports.getEventStatistics = getEventStatistics;
/**
 * 获取预警列表
 * @route GET /api/v1/supply-chain/alerts
 */
const getAlerts = async (req, res) => {
    try {
        const limit = req.query.limit ? parseInt(req.query.limit, 10) : 100;
        const level = req.query.level;
        logger_1.logger.info(`请求预警列表 (限制: ${limit}, 级别: ${level || '全部'})`);
        // 这里直接从服务获取预警
        const alerts = supplyChainService.getAlerts(limit, level);
        res.status(200).json({
            success: true,
            data: alerts
        });
    }
    catch (error) {
        logger_1.logger.error('获取预警列表失败', error);
        res.status(500).json({
            success: false,
            message: error instanceof Error ? error.message : '内部服务器错误',
            error: process.env.NODE_ENV === 'development' ? error : undefined
        });
    }
};
exports.getAlerts = getAlerts;
/**
 * 确认预警
 * @route PUT /api/v1/supply-chain/alerts/:alertId/acknowledge
 */
const acknowledgeAlert = async (req, res) => {
    try {
        const { alertId } = req.params;
        const { userId } = req.body;
        if (!userId) {
            res.status(400).json({
                success: false,
                message: '请提供用户ID'
            });
            return;
        }
        logger_1.logger.info(`确认预警: ${alertId} (用户: ${userId})`);
        const success = supplyChainService.acknowledgeAlert(alertId, userId);
        if (!success) {
            res.status(404).json({
                success: false,
                message: '预警不存在'
            });
            return;
        }
        res.status(200).json({
            success: true,
            message: '预警已确认'
        });
    }
    catch (error) {
        logger_1.logger.error('确认预警失败', error);
        res.status(500).json({
            success: false,
            message: error instanceof Error ? error.message : '内部服务器错误',
            error: process.env.NODE_ENV === 'development' ? error : undefined
        });
    }
};
exports.acknowledgeAlert = acknowledgeAlert;
/**
 * 解决预警
 * @route PUT /api/v1/supply-chain/alerts/:alertId/resolve
 */
const resolveAlert = async (req, res) => {
    try {
        const { alertId } = req.params;
        logger_1.logger.info(`解决预警: ${alertId}`);
        const success = supplyChainService.resolveAlert(alertId);
        if (!success) {
            res.status(404).json({
                success: false,
                message: '预警不存在'
            });
            return;
        }
        res.status(200).json({
            success: true,
            message: '预警已解决'
        });
    }
    catch (error) {
        logger_1.logger.error('解决预警失败', error);
        res.status(500).json({
            success: false,
            message: error instanceof Error ? error.message : '内部服务器错误',
            error: process.env.NODE_ENV === 'development' ? error : undefined
        });
    }
};
exports.resolveAlert = resolveAlert;
/**
 * 获取预警统计信息
 * @route GET /api/v1/supply-chain/alerts/statistics
 */
const getAlertStatistics = async (req, res) => {
    try {
        logger_1.logger.info('请求预警统计信息');
        // 这里直接从服务获取预警统计
        const statistics = supplyChainService.getAlertStatistics();
        res.status(200).json({
            success: true,
            data: statistics
        });
    }
    catch (error) {
        logger_1.logger.error('获取预警统计信息失败', error);
        res.status(500).json({
            success: false,
            message: error instanceof Error ? error.message : '内部服务器错误',
            error: process.env.NODE_ENV === 'development' ? error : undefined
        });
    }
};
exports.getAlertStatistics = getAlertStatistics;

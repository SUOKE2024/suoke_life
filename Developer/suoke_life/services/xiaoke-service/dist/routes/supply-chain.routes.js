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
exports.default = default_1;
const express_1 = require("express");
const supplyChainController = __importStar(require("../controllers/supply-chain.controller"));
/**
 * 供应链路由模块
 * @param {Server} io - Socket.IO服务器实例
 * @returns {Router} Express路由实例
 */
function default_1(io) {
    const router = (0, express_1.Router)();
    /**
     * 供应链信息
     * @route GET /api/v1/supply-chain/:productId
     * @group 供应链管理 - 供应链追踪和管理相关接口
     * @param {string} productId.path.required - 产品ID
     * @returns {object} 200 - 供应链信息
     * @returns {Error} 404 - 产品不存在
     * @returns {Error} 500 - 服务器错误
     */
    router.get('/:productId', supplyChainController.getSupplyChainInfo);
    /**
     * 供应链可视化数据
     * @route GET /api/v1/supply-chain/:productId/visualization
     * @group 供应链管理 - 供应链追踪和管理相关接口
     * @param {string} productId.path.required - 产品ID
     * @returns {object} 200 - 供应链可视化数据
     * @returns {Error} 404 - 产品不存在
     * @returns {Error} 500 - 服务器错误
     */
    router.get('/:productId/visualization', supplyChainController.getSupplyChainVisualization);
    /**
     * 获取产品事件历史
     * @route GET /api/v1/supply-chain/:productId/events
     * @group 供应链管理 - 供应链追踪和管理相关接口
     * @param {string} productId.path.required - 产品ID
     * @returns {Array.<object>} 200 - 产品事件历史列表
     * @returns {Error} 404 - 产品不存在
     * @returns {Error} 500 - 服务器错误
     */
    router.get('/:productId/events', supplyChainController.getProductEventHistory);
    /**
     * 记录供应链事件
     * @route POST /api/v1/supply-chain/events
     * @group 供应链管理 - 供应链追踪和管理相关接口
     * @param {object} eventData.body.required - 事件数据
     * @returns {object} 201 - 事件已记录
     * @returns {Error} 400 - 请求参数错误
     * @returns {Error} 500 - 服务器错误
     */
    router.post('/events', supplyChainController.recordSupplyChainEvent);
    /**
     * 获取最近的事件
     * @route GET /api/v1/supply-chain/events/recent
     * @group 供应链管理 - 供应链追踪和管理相关接口
     * @param {number} limit.query - 限制数量，默认10
     * @returns {Array.<object>} 200 - 最近事件列表
     * @returns {Error} 500 - 服务器错误
     */
    router.get('/events/recent', supplyChainController.getRecentEvents);
    /**
     * 获取事件统计信息
     * @route GET /api/v1/supply-chain/events/statistics
     * @group 供应链管理 - 供应链追踪和管理相关接口
     * @returns {object} 200 - 事件统计信息
     * @returns {Error} 500 - 服务器错误
     */
    router.get('/events/statistics', supplyChainController.getEventStatistics);
    /**
     * 获取预警列表
     * @route GET /api/v1/supply-chain/alerts
     * @group 供应链管理 - 供应链追踪和管理相关接口
     * @param {number} limit.query - 限制数量，默认100
     * @param {string} level.query - 预警级别过滤
     * @returns {Array.<object>} 200 - 预警列表
     * @returns {Error} 500 - 服务器错误
     */
    router.get('/alerts', supplyChainController.getAlerts);
    /**
     * 获取预警统计信息
     * @route GET /api/v1/supply-chain/alerts/statistics
     * @group 供应链管理 - 供应链追踪和管理相关接口
     * @returns {object} 200 - 预警统计信息
     * @returns {Error} 500 - 服务器错误
     */
    router.get('/alerts/statistics', supplyChainController.getAlertStatistics);
    /**
     * 确认预警
     * @route PUT /api/v1/supply-chain/alerts/:alertId/acknowledge
     * @group 供应链管理 - 供应链追踪和管理相关接口
     * @param {string} alertId.path.required - 预警ID
     * @param {object} userData.body.required - 用户数据
     * @returns {object} 200 - 预警已确认
     * @returns {Error} 400 - 请求参数错误
     * @returns {Error} 404 - 预警不存在
     * @returns {Error} 500 - 服务器错误
     */
    router.put('/alerts/:alertId/acknowledge', supplyChainController.acknowledgeAlert);
    /**
     * 解决预警
     * @route PUT /api/v1/supply-chain/alerts/:alertId/resolve
     * @group 供应链管理 - 供应链追踪和管理相关接口
     * @param {string} alertId.path.required - 预警ID
     * @returns {object} 200 - 预警已解决
     * @returns {Error} 404 - 预警不存在
     * @returns {Error} 500 - 服务器错误
     */
    router.put('/alerts/:alertId/resolve', supplyChainController.resolveAlert);
    // 如果提供了Socket.IO实例，设置实时事件通知
    if (io) {
        io.on('connection', (socket) => {
            socket.on('join-supply-chain-channel', (productId) => {
                socket.join(`supply-chain:${productId}`);
            });
            socket.on('leave-supply-chain-channel', (productId) => {
                socket.leave(`supply-chain:${productId}`);
            });
        });
    }
    return router;
}

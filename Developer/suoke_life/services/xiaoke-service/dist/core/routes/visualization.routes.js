"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = default_1;
const express_1 = require("express");
const visualization_controller_1 = __importDefault(require("../../controllers/visualization.controller"));
const auth_middleware_1 = require("../middleware/auth.middleware");
/**
 * 溯源可视化路由
 * 处理与溯源数据可视化相关的HTTP路由
 */
function default_1(io) {
    const router = (0, express_1.Router)();
    /**
     * @route   GET /api/v1/visualization/chain/:id
     * @desc    获取溯源链数据（用于前端绘制流程图）
     * @access  Public
     */
    router.get('/chain/:id', (req, res) => {
        visualization_controller_1.default.getTraceabilityChain(req, res);
    });
    /**
     * @route   GET /api/v1/visualization/geo-distribution
     * @desc    获取供应链地理分布数据（用于地图可视化）
     * @access  Private (Admin, Producer)
     */
    router.get('/geo-distribution', (0, auth_middleware_1.auth)(['admin', 'producer']), (req, res) => {
        visualization_controller_1.default.getSupplyChainGeoDistribution(req, res);
    });
    /**
     * @route   GET /api/v1/visualization/analytics
     * @desc    获取溯源数据分析和趋势
     * @access  Private (Admin)
     */
    router.get('/analytics', (0, auth_middleware_1.auth)(['admin']), (req, res) => {
        visualization_controller_1.default.getTraceabilityAnalytics(req, res);
    });
    /**
     * @route   GET /api/v1/visualization/quality-monitoring
     * @desc    获取质量监控数据
     * @access  Private (Admin, Producer)
     */
    router.get('/quality-monitoring', (0, auth_middleware_1.auth)(['admin', 'producer']), (req, res) => {
        visualization_controller_1.default.getQualityMonitoringData(req, res);
    });
    return router;
}

"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.VisualizationController = void 0;
const logger_1 = require("../utils/logger");
const visualization_service_1 = __importDefault(require("../services/traceability/visualization.service"));
const metrics_1 = require("../core/metrics");
/**
 * 溯源可视化控制器
 * 处理与溯源数据可视化和分析相关的HTTP请求
 */
class VisualizationController {
    constructor(visualizationService) {
        this.visualizationService = visualizationService;
    }
    /**
     * 获取溯源链数据（用于前端绘制流程图）
     */
    async getTraceabilityChain(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/visualization/chain/:id',
                status: '200'
            });
            const { id } = req.params;
            const chainData = await this.visualizationService.getTraceabilityChain(id);
            if (!chainData) {
                res.status(404).json({
                    success: false,
                    error: '溯源链数据不存在',
                    code: 'TRACEABILITY_CHAIN_NOT_FOUND'
                });
                return;
            }
            res.json({
                success: true,
                data: chainData
            });
        }
        catch (error) {
            logger_1.logger.error('获取溯源链数据失败:', error);
            res.status(500).json({
                success: false,
                error: '获取溯源链数据失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 获取供应链地理分布数据（用于地图可视化）
     */
    async getSupplyChainGeoDistribution(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/visualization/geo-distribution',
                status: '200'
            });
            const { category } = req.query;
            const geoData = await this.visualizationService.getSupplyChainGeoDistribution(category);
            res.json({
                success: true,
                data: geoData
            });
        }
        catch (error) {
            logger_1.logger.error('获取供应链地理分布数据失败:', error);
            res.status(500).json({
                success: false,
                error: '获取供应链地理分布数据失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 获取溯源数据分析和趋势
     */
    async getTraceabilityAnalytics(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/visualization/analytics',
                status: '200'
            });
            const { startDate, endDate } = req.query;
            const analyticsData = await this.visualizationService.getTraceabilityAnalytics(startDate, endDate);
            res.json({
                success: true,
                data: analyticsData
            });
        }
        catch (error) {
            logger_1.logger.error('获取溯源数据分析失败:', error);
            res.status(500).json({
                success: false,
                error: '获取溯源数据分析失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
    /**
     * 获取质量监控数据
     */
    async getQualityMonitoringData(req, res) {
        try {
            // 追踪请求指标
            metrics_1.httpRequestsTotal.inc({
                method: req.method,
                path: '/api/v1/visualization/quality-monitoring',
                status: '200'
            });
            const { productId } = req.query;
            const qualityData = await this.visualizationService.getQualityMonitoringData(productId);
            res.json({
                success: true,
                data: qualityData
            });
        }
        catch (error) {
            logger_1.logger.error('获取质量监控数据失败:', error);
            res.status(500).json({
                success: false,
                error: '获取质量监控数据失败',
                message: error instanceof Error ? error.message : '未知错误'
            });
        }
    }
}
exports.VisualizationController = VisualizationController;
exports.default = new VisualizationController(visualization_service_1.default);

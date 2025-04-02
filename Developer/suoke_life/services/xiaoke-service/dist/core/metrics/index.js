"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.setupMetrics = exports.farmActivityCounter = exports.serviceSubscriptionCounter = exports.seasonalRecommendationCounter = exports.productInventoryGauge = exports.orderProcessingTimeSeconds = exports.orderProcessCounter = exports.productQueryCounter = exports.httpRequestDurationSeconds = exports.httpRequestsTotal = exports.register = void 0;
const express_1 = __importDefault(require("express"));
const prom_client_1 = __importDefault(require("prom-client"));
const logger_1 = require("../../utils/logger");
// 创建默认的注册表
exports.register = new prom_client_1.default.Registry();
// 添加默认指标
prom_client_1.default.collectDefaultMetrics({
    prefix: 'xiaoke_',
    register: exports.register
});
// HTTP请求计数器
exports.httpRequestsTotal = new prom_client_1.default.Counter({
    name: 'xiaoke_http_requests_total',
    help: '总HTTP请求数',
    labelNames: ['method', 'path', 'status'],
    registers: [exports.register]
});
// HTTP请求持续时间
exports.httpRequestDurationSeconds = new prom_client_1.default.Histogram({
    name: 'xiaoke_http_request_duration_seconds',
    help: 'HTTP请求持续时间(秒)',
    labelNames: ['method', 'path', 'status'],
    buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
    registers: [exports.register]
});
// 供应链产品查询计数器
exports.productQueryCounter = new prom_client_1.default.Counter({
    name: 'xiaoke_product_queries_total',
    help: '产品信息查询总数',
    labelNames: ['product_type', 'source', 'result'],
    registers: [exports.register]
});
// 订单处理计数器
exports.orderProcessCounter = new prom_client_1.default.Counter({
    name: 'xiaoke_order_processing_total',
    help: '订单处理总数',
    labelNames: ['order_type', 'status'],
    registers: [exports.register]
});
// 订单处理时间
exports.orderProcessingTimeSeconds = new prom_client_1.default.Histogram({
    name: 'xiaoke_order_processing_seconds',
    help: '订单处理时间(秒)',
    labelNames: ['order_type'],
    buckets: [1, 5, 15, 30, 60, 120, 300, 600],
    registers: [exports.register]
});
// 产品库存数量
exports.productInventoryGauge = new prom_client_1.default.Gauge({
    name: 'xiaoke_product_inventory',
    help: '产品库存数量',
    labelNames: ['product_id', 'product_name', 'category'],
    registers: [exports.register]
});
// 节气食材推荐查询
exports.seasonalRecommendationCounter = new prom_client_1.default.Counter({
    name: 'xiaoke_seasonal_recommendations_total',
    help: '节气食材推荐查询总数',
    labelNames: ['solar_term', 'season', 'constitution'],
    registers: [exports.register]
});
// 服务订阅计数器
exports.serviceSubscriptionCounter = new prom_client_1.default.Counter({
    name: 'xiaoke_service_subscriptions_total',
    help: '服务订阅总数',
    labelNames: ['service_type', 'duration', 'status'],
    registers: [exports.register]
});
// 农事活动计数器
exports.farmActivityCounter = new prom_client_1.default.Counter({
    name: 'xiaoke_farm_activities_total',
    help: '农事活动预订总数',
    labelNames: ['activity_type', 'location', 'status'],
    registers: [exports.register]
});
// 初始化指标服务器
const setupMetrics = (app, metricsPort) => {
    const port = Number(metricsPort);
    const metricsApp = (0, express_1.default)();
    // 仅导出指标端点
    metricsApp.get('/metrics', async (req, res) => {
        try {
            res.set('Content-Type', exports.register.contentType);
            res.end(await exports.register.metrics());
        }
        catch (error) {
            logger_1.logger.error('获取指标失败:', error);
            res.status(500).end();
        }
    });
    // 健康检查端点
    metricsApp.get('/health', (req, res) => {
        res.status(200).json({ status: 'ok', service: 'xiaoke-metrics' });
    });
    // 启动专用的指标服务器
    const server = metricsApp.listen(port, () => {
        logger_1.logger.info(`指标服务器监听端口 ${port}`);
    });
    // 为主应用添加指标中间件
    app.use((req, res, next) => {
        const start = Date.now();
        // 记录请求结束和持续时间
        res.on('finish', () => {
            const duration = (Date.now() - start) / 1000;
            const path = req.path || req.url || '/unknown';
            const method = req.method;
            const status = res.statusCode.toString();
            exports.httpRequestsTotal.inc({ method, path, status });
            exports.httpRequestDurationSeconds.observe({ method, path, status }, duration);
        });
        next();
    });
    return server;
};
exports.setupMetrics = setupMetrics;
exports.default = {
    register: exports.register,
    httpRequestsTotal: exports.httpRequestsTotal,
    httpRequestDurationSeconds: exports.httpRequestDurationSeconds,
    productQueryCounter: exports.productQueryCounter,
    orderProcessCounter: exports.orderProcessCounter,
    orderProcessingTimeSeconds: exports.orderProcessingTimeSeconds,
    productInventoryGauge: exports.productInventoryGauge,
    seasonalRecommendationCounter: exports.seasonalRecommendationCounter,
    serviceSubscriptionCounter: exports.serviceSubscriptionCounter,
    farmActivityCounter: exports.farmActivityCounter,
    setupMetrics: exports.setupMetrics
};

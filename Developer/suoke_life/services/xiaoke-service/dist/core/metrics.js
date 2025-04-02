"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.initMetrics = exports.orderProcessingTime = exports.orderAmountGauge = exports.orderCounter = exports.apiResponseTime = exports.httpRequestsTotal = exports.traceabilityProcessingTime = exports.traceabilityVerificationGauge = exports.traceabilityQueryCounter = exports.farmActivityCounter = void 0;
const prom_client_1 = require("prom-client");
/**
 * 农场活动计数器
 * 用于跟踪不同类型、地点和状态的活动访问情况
 */
exports.farmActivityCounter = new prom_client_1.Counter({
    name: 'farm_activity_metrics',
    help: '农场活动访问指标',
    labelNames: ['activity_type', 'location', 'status']
});
/**
 * 溯源查询计数器
 * 跟踪溯源信息查询次数
 */
exports.traceabilityQueryCounter = new prom_client_1.Counter({
    name: 'traceability_query_total',
    help: '溯源信息查询总次数',
    labelNames: ['method', 'queryType', 'productCategory']
});
/**
 * 溯源验证状态仪表盘
 * 跟踪溯源验证状态
 */
exports.traceabilityVerificationGauge = new prom_client_1.Gauge({
    name: 'traceability_verification_status',
    help: '溯源验证状态统计',
    labelNames: ['status', 'productCategory', 'origin']
});
/**
 * 溯源处理时间直方图
 * 测量溯源请求处理时间
 */
exports.traceabilityProcessingTime = new prom_client_1.Histogram({
    name: 'traceability_processing_seconds',
    help: '溯源请求处理时间(秒)',
    labelNames: ['operation'],
    buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
});
/**
 * HTTP请求计数器
 * 用于跟踪API请求情况
 */
exports.httpRequestsTotal = new prom_client_1.Counter({
    name: 'http_requests_total',
    help: 'HTTP请求总数',
    labelNames: ['method', 'path', 'status']
});
/**
 * API响应时间直方图
 * 用于测量API响应时间
 */
exports.apiResponseTime = new prom_client_1.Histogram({
    name: 'api_response_time_seconds',
    help: 'API响应时间（秒）',
    labelNames: ['method', 'path', 'status'],
    buckets: [0.1, 0.5, 1, 2, 5, 10]
});
/**
 * 订单计数器
 * 用于跟踪订单创建、更新和状态变化
 */
exports.orderCounter = new prom_client_1.Counter({
    name: 'orders_total',
    help: '订单总数统计',
    labelNames: ['status', 'paymentMethod', 'productCategory']
});
/**
 * 订单金额仪表盘
 * 跟踪不同类别订单的总金额
 */
exports.orderAmountGauge = new prom_client_1.Gauge({
    name: 'order_amount_total',
    help: '订单金额总计',
    labelNames: ['status', 'productCategory', 'paymentStatus']
});
/**
 * 订单处理时间直方图
 * 测量订单处理时间
 */
exports.orderProcessingTime = new prom_client_1.Histogram({
    name: 'order_processing_seconds',
    help: '订单处理时间(秒)',
    labelNames: ['operation'],
    buckets: [0.1, 0.5, 1, 3, 5, 10, 30]
});
/**
 * 初始化所有指标
 */
const initMetrics = () => {
    // 重置所有指标
    exports.traceabilityVerificationGauge.reset();
    exports.orderAmountGauge.reset();
    // 设置默认值
    exports.traceabilityVerificationGauge.set({ status: 'verified', productCategory: 'all', origin: 'all' }, 0);
    exports.traceabilityVerificationGauge.set({ status: 'pending', productCategory: 'all', origin: 'all' }, 0);
    exports.traceabilityVerificationGauge.set({ status: 'failed', productCategory: 'all', origin: 'all' }, 0);
    // 订单初始值
    exports.orderAmountGauge.set({ status: 'completed', productCategory: 'all', paymentStatus: 'paid' }, 0);
    exports.orderAmountGauge.set({ status: 'pending', productCategory: 'all', paymentStatus: 'pending' }, 0);
};
exports.initMetrics = initMetrics;

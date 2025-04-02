import { Counter, Gauge, Histogram } from 'prom-client';

/**
 * 农场活动计数器
 * 用于跟踪不同类型、地点和状态的活动访问情况
 */
export const farmActivityCounter = new Counter({
  name: 'farm_activity_metrics',
  help: '农场活动访问指标',
  labelNames: ['activity_type', 'location', 'status']
});

/**
 * 溯源查询计数器
 * 跟踪溯源信息查询次数
 */
export const traceabilityQueryCounter = new Counter({
  name: 'traceability_query_total',
  help: '溯源信息查询总次数',
  labelNames: ['method', 'queryType', 'productCategory']
});

/**
 * 溯源验证状态仪表盘
 * 跟踪溯源验证状态
 */
export const traceabilityVerificationGauge = new Gauge({
  name: 'traceability_verification_status',
  help: '溯源验证状态统计',
  labelNames: ['status', 'productCategory', 'origin']
});

/**
 * 溯源处理时间直方图
 * 测量溯源请求处理时间
 */
export const traceabilityProcessingTime = new Histogram({
  name: 'traceability_processing_seconds',
  help: '溯源请求处理时间(秒)',
  labelNames: ['operation'],
  buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
});

/**
 * HTTP请求计数器
 * 用于跟踪API请求情况
 */
export const httpRequestsTotal = new Counter({
  name: 'http_requests_total',
  help: 'HTTP请求总数',
  labelNames: ['method', 'path', 'status']
});

/**
 * API响应时间直方图
 * 用于测量API响应时间
 */
export const apiResponseTime = new Histogram({
  name: 'api_response_time_seconds',
  help: 'API响应时间（秒）',
  labelNames: ['method', 'path', 'status'],
  buckets: [0.1, 0.5, 1, 2, 5, 10]
});

/**
 * 订单计数器
 * 用于跟踪订单创建、更新和状态变化
 */
export const orderCounter = new Counter({
  name: 'orders_total',
  help: '订单总数统计',
  labelNames: ['status', 'paymentMethod', 'productCategory']
});

/**
 * 订单金额仪表盘
 * 跟踪不同类别订单的总金额
 */
export const orderAmountGauge = new Gauge({
  name: 'order_amount_total',
  help: '订单金额总计',
  labelNames: ['status', 'productCategory', 'paymentStatus']
});

/**
 * 订单处理时间直方图
 * 测量订单处理时间
 */
export const orderProcessingTime = new Histogram({
  name: 'order_processing_seconds',
  help: '订单处理时间(秒)',
  labelNames: ['operation'],
  buckets: [0.1, 0.5, 1, 3, 5, 10, 30]
});

/**
 * 初始化所有指标
 */
export const initMetrics = () => {
  // 重置所有指标
  traceabilityVerificationGauge.reset();
  orderAmountGauge.reset();
  
  // 设置默认值
  traceabilityVerificationGauge.set({ status: 'verified', productCategory: 'all', origin: 'all' }, 0);
  traceabilityVerificationGauge.set({ status: 'pending', productCategory: 'all', origin: 'all' }, 0);
  traceabilityVerificationGauge.set({ status: 'failed', productCategory: 'all', origin: 'all' }, 0);
  
  // 订单初始值
  orderAmountGauge.set({ status: 'completed', productCategory: 'all', paymentStatus: 'paid' }, 0);
  orderAmountGauge.set({ status: 'pending', productCategory: 'all', paymentStatus: 'pending' }, 0);
}; 
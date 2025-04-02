"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.setupOpenTelemetry = setupOpenTelemetry;
const sdk_node_1 = require("@opentelemetry/sdk-node");
const exporter_trace_otlp_proto_1 = require("@opentelemetry/exporter-trace-otlp-proto");
const exporter_metrics_otlp_proto_1 = require("@opentelemetry/exporter-metrics-otlp-proto");
const resources_1 = require("@opentelemetry/resources");
const semantic_conventions_1 = require("@opentelemetry/semantic-conventions");
const sdk_trace_node_1 = require("@opentelemetry/sdk-trace-node");
const auto_instrumentations_node_1 = require("@opentelemetry/auto-instrumentations-node");
const sdk_metrics_1 = require("@opentelemetry/sdk-metrics");
const logger_1 = require("./logger");
/**
 * 设置OpenTelemetry SDK
 * 启用自动仪表化并配置导出器
 */
function setupOpenTelemetry() {
    const serviceName = process.env.SERVICE_NAME || 'xiaoke-service';
    const serviceVersion = process.env.SERVICE_VERSION || '1.0.0';
    const environment = process.env.NODE_ENV || 'development';
    const otlpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318';
    // 创建资源属性
    let resourceAttributes = {
        [semantic_conventions_1.SemanticResourceAttributes.SERVICE_NAME]: serviceName,
        [semantic_conventions_1.SemanticResourceAttributes.SERVICE_VERSION]: serviceVersion,
        [semantic_conventions_1.SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: environment,
        'ai.type': 'xiaoke',
        'ai.role': 'secondary-agent'
    };
    // 添加来自环境变量的资源属性
    if (process.env.OTEL_RESOURCE_ATTRIBUTES) {
        const customAttributes = process.env.OTEL_RESOURCE_ATTRIBUTES.split(',');
        customAttributes.forEach(attr => {
            const [key, value] = attr.split('=');
            if (key && value) {
                resourceAttributes[key] = value.replace(/\${([^}]+)}/g, (_, varName) => {
                    return process.env[varName] || '';
                });
            }
        });
    }
    // 创建OTLP导出器
    const traceExporter = new exporter_trace_otlp_proto_1.OTLPTraceExporter({
        url: `${otlpEndpoint}/v1/traces`,
    });
    const metricExporter = new exporter_metrics_otlp_proto_1.OTLPMetricExporter({
        url: `${otlpEndpoint}/v1/metrics`,
    });
    // 配置监控读取器
    const metricReader = new sdk_metrics_1.PeriodicExportingMetricReader({
        exporter: metricExporter,
        exportIntervalMillis: 15000, // 每15秒导出一次
    });
    // 初始化OpenTelemetry SDK
    try {
        const sdk = new sdk_node_1.NodeSDK({
            resource: new resources_1.Resource(resourceAttributes),
            traceExporter: traceExporter,
            metricReader: metricReader,
            spanProcessors: [
                new sdk_trace_node_1.SimpleSpanProcessor(traceExporter),
                // 在开发环境中添加控制台导出器
                ...(environment === 'development' ? [new sdk_trace_node_1.SimpleSpanProcessor(new sdk_trace_node_1.ConsoleSpanExporter())] : []),
            ],
            instrumentations: [
                (0, auto_instrumentations_node_1.getNodeAutoInstrumentations)({
                    '@opentelemetry/instrumentation-fs': { enabled: false },
                    '@opentelemetry/instrumentation-express': { enabled: true },
                    '@opentelemetry/instrumentation-http': { enabled: true },
                    '@opentelemetry/instrumentation-mongodb': { enabled: true },
                    '@opentelemetry/instrumentation-redis': { enabled: true },
                }),
            ],
        });
        // 启动SDK
        sdk.start();
        logger_1.logger.info('OpenTelemetry 监控已初始化');
        // 处理关闭事件
        const shutdownHandler = async () => {
            try {
                await sdk.shutdown();
                logger_1.logger.info('OpenTelemetry 已正常关闭');
            }
            catch (err) {
                logger_1.logger.error('关闭 OpenTelemetry 时出错:', err);
            }
            finally {
                process.exit(0);
            }
        };
        process.on('SIGTERM', shutdownHandler);
        process.on('SIGINT', shutdownHandler);
        return sdk;
    }
    catch (error) {
        logger_1.logger.error('初始化 OpenTelemetry 失败:', error);
        return null;
    }
}
exports.default = setupOpenTelemetry;

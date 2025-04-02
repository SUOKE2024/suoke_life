/**
 * OpenTelemetry 集成工具
 * 为用户服务提供分布式追踪、度量和日志功能
 */
const opentelemetry = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-proto');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-proto');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

/**
 * 初始化 OpenTelemetry SDK
 */
function initTelemetry() {
  const exporterOptions = {
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://suoke-collector-collector.monitoring:4317',
  };

  const metricReader = new PeriodicExportingMetricReader({
    exporter: new OTLPMetricExporter(exporterOptions),
    exportIntervalMillis: 60000,
  });

  const sdk = new opentelemetry.NodeSDK({
    resource: new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: 'user-service',
      [SemanticResourceAttributes.SERVICE_VERSION]: process.env.npm_package_version || '1.0.0',
      [SemanticResourceAttributes.SERVICE_NAMESPACE]: 'suoke',
      [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'production',
    }),
    traceExporter: new OTLPTraceExporter(exporterOptions),
    metricReader,
    instrumentations: [
      getNodeAutoInstrumentations({
        '@opentelemetry/instrumentation-fs': {
          enabled: false,
        },
        '@opentelemetry/instrumentation-express': {
          enabled: true,
        },
        '@opentelemetry/instrumentation-http': {
          enabled: true,
        },
        '@opentelemetry/instrumentation-redis': {
          enabled: true,
        },
        '@opentelemetry/instrumentation-mysql2': {
          enabled: true,
        },
      }),
    ],
  });

  // 启动 SDK
  sdk.start()
    .then(() => console.log('OpenTelemetry 追踪初始化成功'))
    .catch((error) => console.error('OpenTelemetry 追踪初始化失败', error));

  // 优雅关闭
  const shutdownTelemetry = async () => {
    try {
      await sdk.shutdown();
      console.log('OpenTelemetry SDK 已关闭');
    } catch (e) {
      console.error('关闭 OpenTelemetry SDK 时出错', e);
    }
  };

  process.on('SIGTERM', shutdownTelemetry);
  process.on('SIGINT', shutdownTelemetry);

  return sdk;
}

module.exports = { initTelemetry };
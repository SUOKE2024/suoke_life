import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-http';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import logger from './logger';

let sdk: NodeSDK;

/**
 * 设置OpenTelemetry
 */
export const setupOpenTelemetry = () => {
  try {
    if (process.env.NODE_ENV === 'test') {
      logger.info('测试环境中跳过OpenTelemetry初始化');
      return;
    }
    
    const endpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318';
    
    sdk = new NodeSDK({
      resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: process.env.SERVICE_NAME || 'laoke-service',
        [SemanticResourceAttributes.SERVICE_VERSION]: process.env.SERVICE_VERSION || '1.0.0',
        [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development'
      }),
      traceExporter: new OTLPTraceExporter({
        url: `${endpoint}/v1/traces`
      }),
      metricExporter: new OTLPMetricExporter({
        url: `${endpoint}/v1/metrics`
      }),
      instrumentations: [
        getNodeAutoInstrumentations({
          '@opentelemetry/instrumentation-http': { enabled: true },
          '@opentelemetry/instrumentation-express': { enabled: true },
          '@opentelemetry/instrumentation-mongodb': { enabled: true },
          '@opentelemetry/instrumentation-redis': { enabled: true },
        })
      ]
    });
    
    // 启动SDK
    sdk.start();
    logger.info('OpenTelemetry初始化成功');
    
    // 设置进程退出处理
    process.on('SIGTERM', () => {
      shutdownTelemetry()
        .then(() => logger.info('OpenTelemetry已关闭'))
        .catch(err => logger.error('关闭OpenTelemetry出错:', err));
    });
    
    return sdk;
  } catch (error) {
    logger.error('OpenTelemetry初始化失败:', error);
  }
};

/**
 * 关闭OpenTelemetry
 */
export const shutdownTelemetry = async () => {
  if (sdk) {
    return sdk.shutdown();
  }
}; 
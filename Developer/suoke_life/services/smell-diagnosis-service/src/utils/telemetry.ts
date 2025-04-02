import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { Logger } from './logger';

const logger = new Logger('Telemetry');

/**
 * 初始化OpenTelemetry
 */
export function setupOpenTelemetry(): void {
  // 确保在生产环境中启用
  if (process.env.NODE_ENV !== 'production') {
    logger.info('OpenTelemetry未在非生产环境启用');
    return;
  }

  // 如果没有配置OTLP端点，则不启用
  if (!process.env.OTEL_EXPORTER_OTLP_ENDPOINT) {
    logger.info('未配置OTLP端点，OpenTelemetry未启用');
    return;
  }

  try {
    const sdk = new NodeSDK({
      resource: new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: process.env.OTEL_SERVICE_NAME || 'smell-diagnosis-service',
        [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
        [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'production',
      }),
      traceExporter: new OTLPTraceExporter({
        url: `${process.env.OTEL_EXPORTER_OTLP_ENDPOINT}/v1/traces`,
      }),
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
          '@opentelemetry/instrumentation-winston': {
            enabled: true,
          },
        }),
      ],
    });

    // 启动SDK
    sdk.start();
    logger.info('OpenTelemetry已初始化', {
      endpoint: process.env.OTEL_EXPORTER_OTLP_ENDPOINT,
      serviceName: process.env.OTEL_SERVICE_NAME || 'smell-diagnosis-service',
    });

    // 确保在应用关闭时关闭遥测
    process.on('SIGTERM', () => {
      sdk.shutdown()
        .then(() => logger.info('OpenTelemetry已关闭'))
        .catch((error) => logger.error('关闭OpenTelemetry时出错', { error }));
    });
  } catch (error) {
    logger.error('初始化OpenTelemetry失败', { error });
  }
} 
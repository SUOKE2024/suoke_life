import { NodeSDK } from '@opentelemetry/sdk-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-proto';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-proto';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { SimpleSpanProcessor, ConsoleSpanExporter } from '@opentelemetry/sdk-trace-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';
import { logger } from './logger';

/**
 * 设置OpenTelemetry SDK
 * 启用自动仪表化并配置导出器
 */
export function setupOpenTelemetry() {
  const serviceName = process.env.SERVICE_NAME || 'xiaoke-service';
  const serviceVersion = process.env.SERVICE_VERSION || '1.0.0';
  const environment = process.env.NODE_ENV || 'development';
  const otlpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318';
  
  // 创建资源属性
  let resourceAttributes: Record<string, any> = {
    [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
    [SemanticResourceAttributes.SERVICE_VERSION]: serviceVersion,
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: environment,
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
  const traceExporter = new OTLPTraceExporter({
    url: `${otlpEndpoint}/v1/traces`,
  });
  
  const metricExporter = new OTLPMetricExporter({
    url: `${otlpEndpoint}/v1/metrics`,
  });
  
  // 配置监控读取器
  const metricReader = new PeriodicExportingMetricReader({
    exporter: metricExporter,
    exportIntervalMillis: 15000, // 每15秒导出一次
  });
  
  // 初始化OpenTelemetry SDK
  try {
    const sdk = new NodeSDK({
      resource: new Resource(resourceAttributes),
      traceExporter: traceExporter,
      metricReader: metricReader,
      spanProcessors: [
        new SimpleSpanProcessor(traceExporter),
        // 在开发环境中添加控制台导出器
        ...(environment === 'development' ? [new SimpleSpanProcessor(new ConsoleSpanExporter())] : []),
      ],
      instrumentations: [
        getNodeAutoInstrumentations({
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
    logger.info('OpenTelemetry 监控已初始化');
    
    // 处理关闭事件
    const shutdownHandler = async () => {
      try {
        await sdk.shutdown();
        logger.info('OpenTelemetry 已正常关闭');
      } catch (err) {
        logger.error('关闭 OpenTelemetry 时出错:', err);
      } finally {
        process.exit(0);
      }
    };
    
    process.on('SIGTERM', shutdownHandler);
    process.on('SIGINT', shutdownHandler);
    
    return sdk;
  } catch (error) {
    logger.error('初始化 OpenTelemetry 失败:', error);
    return null;
  }
}

export default setupOpenTelemetry; 
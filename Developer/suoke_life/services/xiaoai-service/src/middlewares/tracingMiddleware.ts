import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-proto';
import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-node';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import dotenv from 'dotenv';

// 加载环境变量
dotenv.config();

// 跟踪初始化
export const initTracing = (): NodeSDK | null => {
  // 如果未启用跟踪，则直接返回
  if (process.env.ENABLE_TRACING !== 'true') {
    return null;
  }

  // 配置OTLP导出器
  const otlpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://otel-collector:4317';
  const traceExporter = new OTLPTraceExporter({
    url: `${otlpEndpoint}/v1/traces`,
  });

  // 创建资源属性
  const resource = new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'xiaoai-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development',
  });

  // 创建SDK
  const sdk = new NodeSDK({
    resource: resource,
    spanProcessor: new BatchSpanProcessor(traceExporter),
    instrumentations: [getNodeAutoInstrumentations()],
  });

  // 启动SDK
  sdk.start();

  // 注册关闭处理程序
  process.on('SIGTERM', () => {
    sdk.shutdown()
      .then(() => console.log('Tracing terminated'))
      .catch((error) => console.log('Error terminating tracing', error))
      .finally(() => process.exit(0));
  });

  return sdk;
};
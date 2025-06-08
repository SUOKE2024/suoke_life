// services 统一导出文件   索克生活APP - 架构优化
// 基础服务导出
export { default as agentService } from './agentService';
export { default as authService } from './authService';
export { default as enhancedApiClient } from './enhancedApiClient';
export { default as realTimeSync } from './realTimeSync';
export { unifiedApiService } from './unifiedApiService';
export { ragService } from './ragService';
export { messageBusService } from './messageBusService';
export { cornMazeService, CornMazeService, createCornMazeService } from './cornMazeService';
export { benchmarkService, BenchmarkService } from './benchmarkService';
export { benchmarkStreamingService, BenchmarkStreamingService } from './benchmarkStreamingService';
//
export {
  UIUXOptimizationService,
  AnimationManager,
  PerformanceOptimizer,
  InteractionEnhancer,
  VisualEffectManager,
  ResponsiveManager,
  createUIUXOptimizationService,
  defaultPerformanceConfig,
  defaultVisualEffectConfig,
  defaultResponsiveConfig,
  defaultThemeConfig,
} from './uiUxOptimizationService';
//
export type {
  AnimationConfig,
  AdvancedAnimationType,
  PerformanceConfig,
  PerformanceMetrics,
  PerformanceWarningLevel,
  InteractionFeedback,
  VisualEffectConfig,
  ResponsiveConfig,
  ThemeConfig,
} from './uiUxOptimizationService';
// RAG服务相关类型导出
export type {
  RAGQueryRequest,
  RAGQueryResponse,
  StreamResponse,
  TCMAnalysisRequest,
  TCMAnalysisResponse,
  HerbRecommendationRequest,
  HerbRecommendationResponse,
  DocumentIndexRequest,
} from './ragService';
// 消息总线服务相关类型导出
export type {
  Message,
  Topic,
  PublishRequest,
  PublishResponse,
  CreateTopicRequest,
  CreateTopicResponse,
  Subscription,
  MessageBusConfig,
} from './messageBusService';
// 基准测试服务相关类型导出
export type {
  BenchmarkConfig,
  BenchmarkTask,
  BenchmarkResult,
  ModelPrediction,
  ModelConfig,
  Plugin,
  BenchmarkStatus,
  HealthStatus,
} from './benchmarkService';
// 基准测试流式服务相关类型导出
export type { StreamEvent, StreamConfig, EventListener } from './benchmarkStreamingService';
// 导出所有服务
export { apiClient } from './apiClient';
export { healthDataService } from './healthDataService';
export { fiveDiagnosisService } from './fiveDiagnosisService';
// 导出类型
export type {
  FiveDiagnosisInput,
  FiveDiagnosisResult,
  FiveDiagnosisError,
  DiagnosisResult,
  LookDiagnosisData,
  ListenDiagnosisData,
  InquiryDiagnosisData,
  PalpationDiagnosisData,
  CalculationDiagnosisData,
} from './fiveDiagnosisService';
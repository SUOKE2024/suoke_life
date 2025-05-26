/**
 * 工具函数统一导出
 */

// 存储工具
export * from './storageUtils';

// 验证工具
export {
  validateEmail,
  validatePassword,
  validatePhone,
  validateUsername,
  validateIdCard,
  validateRequired,
  validateNumberRange,
  validateAge,
  validateHeight,
  validateWeight,
  validateUrl,
  validateField,
  type ValidationRule,
} from './validationUtils';

// 日期工具
export * from './dateUtils';

// 通用工具函数
export * from './commonUtils';

// API集成测试工具
export { apiIntegrationTest } from './apiIntegrationTest';

// 错误处理工具
export {
  ErrorHandler,
  errorHandler,
  handleError,
  getErrorStats,
  clearErrorLog,
  type ErrorInfo,
} from './errorHandler';

// 性能监控工具
export {
  PerformanceMonitor,
  performanceMonitor,
  startPerformanceMeasure,
  endPerformanceMeasure,
  recordNetworkPerformance,
  recordRenderPerformance,
  recordUserInteraction,
  getPerformanceStats,
  getNetworkPerformanceStats,
  clearPerformanceMetrics,
  type PerformanceMetric,
  type NetworkMetric,
  type RenderMetric,
  type MemoryMetric,
  type UserInteractionMetric,
} from './performanceMonitor';

// 缓存管理工具
export {
  CacheManager,
  cacheManager,
  setCache,
  getCache,
  deleteCache,
  clearCache,
  getCacheStats,
  getCacheDetailedStats,
  type CacheItem,
  type CacheOptions,
  type CacheStats,
} from './cacheManager';

// 网络优化工具
export {
  NetworkOptimizer,
  networkOptimizer,
  optimizedRequest,
  batchRequest,
  cancelAllNetworkRequests,
  getNetworkStats,
  type RequestConfig,
  type RequestResponse,
  type BatchRequest,
} from './networkOptimizer';

// 内存优化工具
export {
  MemoryOptimizer,
  memoryOptimizer,
  registerComponent,
  unregisterComponent,
  registerListener,
  unregisterListener,
  getMemoryStats,
  takeMemorySnapshot,
  detectMemoryLeaks,
  type MemorySnapshot,
  type MemoryLeak,
  type MemoryOptimizationSuggestion,
} from './memoryOptimizer';

// 组件性能优化工具
export {
  ComponentOptimizer,
  componentOptimizer,
  useComponentPerformance,
  useOptimizedCallback,
  useOptimizedMemo,
  withPerformanceMonitoring,
  getComponentPerformanceData,
  getComponentOptimizationSuggestions,
  getComponentPerformanceStats,
  clearComponentPerformanceData,
  type ComponentPerformanceData,
  type RenderOptimizationSuggestion,
} from './componentOptimizer';

// 状态管理优化工具
export {
  StateOptimizer,
  stateOptimizer,
  trackStateUpdate,
  batchStateUpdate,
  getStatePerformanceData,
  getStateOptimizationSuggestions,
  getStateStats,
  clearStatePerformanceData,
  type StateChangeEvent,
  type StatePerformanceData,
  type StateOptimizationSuggestion,
} from './stateOptimizer';

// 认证工具
export {
  validateEmail as validateAuthEmail,
  validatePhone as validateAuthPhone,
  validatePassword as validateAuthPassword,
  getPasswordStrength,
  validateUsername as validateAuthUsername,
  validateVerificationCode,
  validateLoginForm,
  validateRegisterForm,
  type LoginFormData,
  type LoginFormErrors,
  type RegisterFormData,
  type RegisterFormErrors,
  type ForgotPasswordFormData,
  type ForgotPasswordFormErrors,
  getAuthToken,
  getRefreshToken,
  clearAuthTokens,
  isAuthenticated,
  formatAuthError,
  generateDeviceId,
  storeDeviceId,
  getDeviceId,
} from './authUtils';

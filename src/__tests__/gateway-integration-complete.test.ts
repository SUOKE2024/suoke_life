import { analyticsService } from '../services/analyticsService';
// Mock dependencies
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}));
describe('Gateway Integration - Complete Test Suite', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  describe('Analytics Service', () => {
    it('should track events correctly', () => {
      const eventData = {
      action: "test_action",
      value: 123,
      };
      analyticsService.trackEvent('user_action', eventData);
      const stats = analyticsService.getEventStats();
      expect(stats.user_action).toBe(1);
    });
    it('should track API calls with performance metrics', () => {
      analyticsService.trackApiCall("user-service",/profile', 'GET', 250, 200);
      const metrics = analyticsService.getPerformanceMetrics();
      expect(metrics.responseTime).toBe(250);
      expect(metrics.throughput).toBe(1);
      expect(metrics.errorRate).toBe(0);
    });
    it('should generate service usage statistics', () => {
      analyticsService.trackApiCall("user-service",/profile', 'GET', 100, 200);
      analyticsService.trackApiCall("user-service",/settings', 'POST', 200, 200);
      analyticsService.trackApiCall("auth-service",/login', 'POST', 150, 200);
      const usage = analyticsService.getServiceUsage();
      expect(usage).toHaveLength(2);
      expect(usage.find(s => s.service === 'user-service')?.calls).toBe(2);
      expect(usage.find(s => s.service === 'auth-service')?.calls).toBe(1);
    });
  });
  describe('Config Service', () => {
    it('should get configuration values', () => {
      const timeout = configService.get('gateway.timeout');
      expect(typeof timeout).toBe('number');
      expect(timeout).toBeGreaterThan(0);
    });
    it('should set configuration values', async () => {
      await configService.set('gateway.timeout', 45000);
      const timeout = configService.get('gateway.timeout');
      expect(timeout).toBe(45000);
    });
    it('should check feature flags', () => {
      const isEnabled = configService.isFeatureEnabled('ai-diagnosis');
      expect(typeof isEnabled).toBe('boolean');
    });
  });
  describe('Integration Tests', () => {
    it('should handle configuration changes across services', async () => {
      // 更新配置
      await configService.set('analytics.enabled', false);
      // 应用到分析服务
      analyticsService.updateConfig({ enabled: false });
      // 验证配置生效
      analyticsService.trackEvent('system', { data: 'test' });
      const stats = analyticsService.getEventStats();
      expect(Object.keys(stats)).toHaveLength(0);
    });
  });
});
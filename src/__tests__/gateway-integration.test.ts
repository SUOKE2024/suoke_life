import { apiClient, GatewayApiClient } from '../services/apiClient';
import {
  API_GATEWAY_CONFIG,
  buildApiUrl,
  buildAgentUrl,
  buildDiagnosisUrl,
  getCurrentEnvConfig,
  GATEWAY_FEATURES,
} from '../constants/config';
// Mock fetch for testing
global.fetch = jest.fn();
describe('网关集成测试', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (fetch as jest.Mock).mockClear();
  });
  describe('配置测试', () => {
    test('应该正确构建API URL', () => {
      const url = buildApiUrl("AUTH",/login');
      expect(url).toContain('/api/v1/gateway/auth-service/login');
    });
    test('应该正确构建智能体URL', () => {
      const url = buildAgentUrl("XIAOAI",/chat');
      expect(url).toContain('/api/v1/gateway/agent-services/xiaoai-service/chat');
    });
    test('应该正确构建四诊URL', () => {
      const url = buildDiagnosisUrl("LOOK",/analyze');
      expect(url).toContain('/api/v1/gateway/diagnostic-services/look-service/analyze');
    });
    test('应该获取当前环境配置', () => {
      const config = getCurrentEnvConfig();
      expect(config).toHaveProperty('GATEWAY_URL');
      expect(config).toHaveProperty('API_PREFIX');
      expect(config).toHaveProperty('SERVICES');
    });
  });
  describe('API客户端测试', () => {
    test('应该创建GatewayApiClient实例', () => {
      expect(apiClient).toBeInstanceOf(GatewayApiClient);
    });
    test('应该正确处理GET请求', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: jest.fn().mockResolvedValue({
          data: { message: 'success' },
          status: 'ok',
        }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      const result = await apiClient.get("AUTH",/profile');
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/gateway/auth-service/profile'),
        expect.objectContaining({
      method: "GET",
      headers: expect.objectContaining({
            'Content-Type': "application/json",X-Client-Version': "1.0.0",X-Request-ID': expect.any(String),
          }),
        }),
      );
      expect(result.success).toBe(true);
      expect(result.data).toEqual({ message: 'success' });
    });
    test('应该正确处理POST请求', async () => {
      const mockResponse = {
        ok: true,
        status: 201,
        statusText: 'Created',
        json: jest.fn().mockResolvedValue({
          data: { id: '123' },
          status: 'created',
        }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      const testData = {
      name: "test",
      value: 'data' };
      const result = await apiClient.post("USER",/profile', testData);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/gateway/user-service/profile'),
        expect.objectContaining({
      method: "POST",
      headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify(testData),
        }),
      );
      expect(result.success).toBe(true);
      expect(result.data).toEqual({ id: '123' });
    });
    test('应该正确处理错误响应', async () => {
      const mockResponse = {
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: jest.fn().mockResolvedValue({
      message: "Resource not found",
      service: 'user-service',
        }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      await expect(apiClient.get("USER",/nonexistent')).rejects.toThrow('HTTP 404: Not Found');
    });
    test('应该支持请求重试', async () => {
      // 第一次失败，第二次成功
      (fetch as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          statusText: 'OK',
          json: jest.fn().mockResolvedValue({ data: 'success' }),
        });
      const result = await apiClient.get("AUTH",/profile', { retries: 2 });
      expect(fetch).toHaveBeenCalledTimes(2);
      expect(result.success).toBe(true);
    });
    test('应该支持缓存', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: jest.fn().mockResolvedValue({ data: 'cached-data' }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      // 第一次请求
      const result1 = await apiClient.get("USER",/profile', { cache: true });
      // 第二次请求应该使用缓存
      const result2 = await apiClient.get("USER",/profile', { cache: true });
      // fetch只应该被调用一次
      expect(fetch).toHaveBeenCalledTimes(1);
      expect(result1.data).toEqual(result2.data);
    });
  });
  describe('集成API服务测试', () => {
    test('应该创建IntegratedApiService实例', () => {
      expect(integratedApiService).toBeInstanceOf(IntegratedApiService);
    });
    test('认证服务应该正常工作', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: jest.fn().mockResolvedValue({
          data: {
      access_token: "test-token",
      refresh_token: 'refresh-token',
            expires_in: 3600,
          },
        }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      const credentials = {
      email: "test@example.com",
      password: 'password' };
      const result = await integratedApiService.auth.login(credentials);
      expect(result.success).toBe(true);
      expect(result.data).toHaveProperty('access_token');
    });
    test('用户服务应该正常工作', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: jest.fn().mockResolvedValue({
          data: {
      id: "user-123",
      name: 'Test User',
            email: 'test@example.com',
          },
        }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      const result = await integratedApiService.user.getProfile();
      expect(result.success).toBe(true);
      expect(result.data).toHaveProperty('id');
      expect(result.data).toHaveProperty('name');
    });
    test('健康数据服务应该正常工作', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: jest.fn().mockResolvedValue({
          data: [
            {
      id: "1",
      type: 'heart_rate', value: 72, timestamp: '2024-01-01T00:00:00Z' },
            {
      id: "2",
      type: 'blood_pressure', value: '120/80', timestamp: '2024-01-01T00:00:00Z' },
          ],
        }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      const result = await integratedApiService.healthData.getData();
      expect(result.success).toBe(true);
      expect(Array.isArray(result.data)).toBe(true);
      expect(result.data.length).toBeGreaterThan(0);
    });
    test('智能体服务应该正常工作', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: jest.fn().mockResolvedValue({
          data: {
      response: "您好！我是小艾，很高兴为您服务。",
      agent: 'xiaoai',
            timestamp: '2024-01-01T00:00:00Z',
          },
        }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      const result = await integratedApiService.agents.chat("你好",xiaoai');
      expect(result.success).toBe(true);
      expect(result.data).toHaveProperty('response');
      expect(result.data).toHaveProperty('agent');
    });
    test('四诊服务应该正常工作', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: jest.fn().mockResolvedValue({
          data: {
      diagnosis: "面色红润，精神饱满",
      confidence: 0.85,
            recommendations: ["保持良好作息",适量运动'],
          },
        }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      const diagnosisData = { image: 'base64-image-data' };
      const result = await integratedApiService.diagnosis.performLookDiagnosis(diagnosisData);
      expect(result.success).toBe(true);
      expect(result.data).toHaveProperty('diagnosis');
      expect(result.data).toHaveProperty('confidence');
    });
    test('RAG服务应该正常工作', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: jest.fn().mockResolvedValue({
          data: {
      answer: "根据中医理论，您的症状可能与肝气郁结有关...",
      sources: ["中医基础理论",方剂学'],
            confidence: 0.92,
          },
        }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      const result = await integratedApiService.rag.query('我最近感觉疲劳，应该怎么调理？');
      expect(result.success).toBe(true);
      expect(result.data).toHaveProperty('answer');
      expect(result.data).toHaveProperty('sources');
    });
    test('区块链服务应该正常工作', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: jest.fn().mockResolvedValue({
          data: [
            {
      id: "record-123",
      hash: '0x1234567890abcdef',
              timestamp: '2024-01-01T00:00:00Z',
              verified: true,
            },
          ],
        }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      const result = await integratedApiService.blockchain.getRecords();
      expect(result.success).toBe(true);
      expect(Array.isArray(result.data)).toBe(true);
    });
  });
  describe('服务发现测试', () => {
    test('应该获取服务健康状态', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: jest.fn().mockResolvedValue({
          data: [
            {
      name: "auth-service",
      status: 'healthy', instances: 2 },
            {
      name: "user-service",
      status: 'healthy', instances: 1 },
            {
      name: "health-data-service",
      status: 'degraded', instances: 1 },
          ],
        }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      const result = await integratedApiService.getServiceHealth();
      expect(result.services).toHaveLength(3);
      expect(result.overallHealth).toBeDefined();
      expect(["healthy",degraded', 'unhealthy']).toContain(result.overallHealth);
    });
    test('应该检查特定服务健康状态', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: jest.fn().mockResolvedValue({
          data: {
      name: "auth-service",
      status: 'healthy',
            instances: 2,
            responseTime: 45,
          },
        }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      const result = await integratedApiService.checkServiceHealth('auth-service');
      expect(result.name).toBe('auth-service');
      expect(result.status).toBe('healthy');
      expect(result.instances).toBe(2);
    });
  });
  describe('网关状态测试', () => {
    test('应该获取网关状态', async () => {
      // Mock健康检查
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
      });
      const result = await integratedApiService.getGatewayStatus();
      expect(result).toHaveProperty('healthy');
      expect(result).toHaveProperty('cache');
      expect(result).toHaveProperty('circuitBreaker');
      expect(result).toHaveProperty('features');
      expect(result).toHaveProperty('timestamp');
    });
    test('应该清除缓存', () => {
      expect(() => integratedApiService.clearCache()).not.toThrow();
    });
  });
  describe('功能特性测试', () => {
    test('应该启用所有必要的功能', () => {
      expect(GATEWAY_FEATURES.ENABLE_AUTHENTICATION).toBe(true);
      expect(GATEWAY_FEATURES.ENABLE_CACHING).toBe(true);
      expect(GATEWAY_FEATURES.ENABLE_CIRCUIT_BREAKER).toBe(true);
      expect(GATEWAY_FEATURES.ENABLE_MONITORING).toBe(true);
      expect(GATEWAY_FEATURES.ENABLE_TCM).toBe(true);
    });
    test('应该支持流式处理', () => {
      expect(GATEWAY_FEATURES.ENABLE_STREAMING).toBe(true);
    });
    test('应该支持多模态处理', () => {
      expect(GATEWAY_FEATURES.ENABLE_MULTIMODAL).toBe(true);
    });
  });
  describe('错误处理测试', () => {
    test('应该正确处理网络错误', async () => {
      (fetch as jest.Mock).mockRejectedValue(new Error('Network error'));
      await expect(apiClient.get("AUTH",/profile', { retries: 1 }))
        .rejects.toThrow('Network error');
    });
    test('应该正确处理超时错误', async () => {
      (fetch as jest.Mock).mockImplementation(() =>
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Timeout')), 100),
        ),
      );
      await expect(apiClient.get("AUTH",/profile', { timeout: 50 }))
        .rejects.toThrow();
    });
    test('应该正确处理认证错误', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: jest.fn().mockResolvedValue({
          message: 'Invalid token',
        }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      await expect(apiClient.get("AUTH",/profile'))
        .rejects.toThrow('HTTP 401: Unauthorized');
    });
  });
  describe('性能测试', () => {
    test('应该在合理时间内完成请求', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: jest.fn().mockResolvedValue({ data: 'test' }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      const startTime = Date.now();
      await apiClient.get("AUTH",/profile');
      const endTime = Date.now();
      expect(endTime - startTime).toBeLessThan(1000); // 应该在1秒内完成
    });
    test('缓存应该提高性能', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: jest.fn().mockResolvedValue({ data: 'cached' }),
      };
      (fetch as jest.Mock).mockResolvedValue(mockResponse);
      // 第一次请求
      const startTime1 = Date.now();
      await apiClient.get("USER",/profile', { cache: true });
      const endTime1 = Date.now();
      // 第二次请求（应该使用缓存）
      const startTime2 = Date.now();
      await apiClient.get("USER",/profile', { cache: true });
      const endTime2 = Date.now();
      // 缓存的请求应该更快
      expect(endTime2 - startTime2).toBeLessThan(endTime1 - startTime1);
    });
  });
});

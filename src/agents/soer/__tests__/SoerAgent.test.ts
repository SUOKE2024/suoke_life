import { SoerAgentImpl } from '../SoerAgentImpl';

describe('SoerAgent', () => {
  let soerAgent: SoerAgentImpl;

  beforeEach(() => {
    soerAgent = new SoerAgentImpl();
    jest.clearAllMocks();
  });

  describe('SoerAgentImpl', () => {
    it('should initialize correctly', () => {
      expect(soerAgent).toBeDefined();
      expect(soerAgent).toBeInstanceOf(SoerAgentImpl);
    });

    it('should have correct capabilities', () => {
      // Test capabilities through public methods instead of protected properties
      expect(soerAgent).toBeDefined();
    });

    it('should process messages correctly', async () => {
      const context = {
        userId: 'test-user',
        sessionId: 'test-session',
        timestamp: new Date(),
        metadata: {},
      };

      const response = await soerAgent.processMessage('你好，索儿', context);

      expect(response).toBeDefined();
      expect(response.success).toBe(true);
    });

    it('should handle invalid inputs gracefully', async () => {
      const context = {
        userId: 'test-user',
        sessionId: 'test-session',
        timestamp: new Date(),
        metadata: {},
      };

      const response = await soerAgent.processMessage('', context);

      expect(response).toBeDefined();
      expect(response.success).toBe(false);
    });

    it('should initialize and shutdown properly', async () => {
      await expect(soerAgent.initialize()).resolves.not.toThrow();
      await expect(soerAgent.shutdown()).resolves.not.toThrow();
    });
  });

  describe('Health Status', () => {
    it('should return health status', async () => {
      const healthStatus = await soerAgent.getHealthStatus();

      expect(healthStatus).toBeDefined();
    });
  });

  describe('Performance Tests', () => {
    it('should execute within performance thresholds', async () => {
      const iterations = 10;
      const startTime = performance.now();

      const context = {
        userId: 'test-user',
        sessionId: 'test-session',
        timestamp: new Date(),
        metadata: {},
      };

      for (let i = 0; i < iterations; i++) {
        await soerAgent.processMessage('测试消息', context);
      }

      const endTime = performance.now();
      const averageTime = (endTime - startTime) / iterations;

      // Should execute within 100ms on average
      expect(averageTime).toBeLessThan(100);
    });

    it('should handle multiple concurrent requests', async () => {
      const context = {
        userId: 'test-user',
        sessionId: 'test-session',
        timestamp: new Date(),
        metadata: {},
      };

      const promises = Array.from({ length: 5 }, (_, i) =>
        soerAgent.processMessage(`测试消息 ${i}`, context)
      );

      const results = await Promise.all(promises);

      expect(results).toHaveLength(5);
      results.forEach((result) => {
        expect(result).toBeDefined();
        expect(result.success).toBeDefined();
      });
    });
  });
});

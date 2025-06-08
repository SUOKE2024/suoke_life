import { localAIService } from '../../services/localAIService';
import { diagnosisCacheManager } from '../../services/diagnosisCacheManager';
describe('诊断服务集成测试', () => {
  beforeAll(async () => {
    // 初始化所有服务
    await localAIService.initialize();
    await performanceOptimizer.initialize();
    await diagnosisCacheManager.initialize();
  });
  afterAll(async () => {
    // 清理资源
    await localAIService.clearModelCache();
    await performanceOptimizer.clearAllCaches();
    await diagnosisCacheManager.clearCache();
  });
  describe('本地AI服务集成', () => {
    it('应该成功初始化本地AI模型', async () => {
      const modelStatus = localAIService.getModelStatus();
      expect(Object.keys(modelStatus)).toContain('tcm_symptom_classifier');
      expect(Object.keys(modelStatus)).toContain('constitution_analyzer');
      expect(Object.keys(modelStatus)).toContain('pulse_pattern_recognizer');
    });
    it('应该能够进行本地症状分类', async () => {
      const symptoms = ["头痛",失眠', '乏力'];
      const result = await localAIService.classifySymptoms(symptoms);
      expect(result.confidence).toBeGreaterThan(0.8);
      expect(result.result.classifications).toHaveLength(3);
      expect(result.processingTime).toBeLessThan(1000);
      expect(result.modelUsed).toBe('tcm_symptom_classifier');
    });
    it('应该能够进行本地体质分析', async () => {
      const userData = {symptoms: ["乏力",气短', '容易疲劳'],age: 30,gender: 'male';
      };
      const result = await localAIService.analyzeConstitution(userData);
      expect(result.confidence).toBeGreaterThan(0.8);
      expect(result.result.primaryConstitution).toBeDefined();
      expect(result.result.recommendations).toBeInstanceOf(Array);
      expect(result.processingTime).toBeLessThan(500);
    });
    it('应该能够进行本地脉象识别', async () => {
      const pulseData = {pressure: 0.5,frequency: 75,smoothness: 0.7;
      };
      const result = await localAIService.recognizePulse(pulseData);
      expect(result.confidence).toBeGreaterThan(0.8);
      expect(result.result.patterns).toBeInstanceOf(Array);
      expect(result.processingTime).toBeLessThan(300);
    });
  });
  describe('性能优化器集成', () => {
    it('应该成功初始化性能监控', async () => {
      const metrics = performanceOptimizer.getPerformanceMetrics();
      expect(metrics).toHaveProperty('renderTime');
      expect(metrics).toHaveProperty('memoryUsage');
      expect(metrics).toHaveProperty('networkLatency');
      expect(metrics).toHaveProperty('cacheHitRate');
      expect(metrics).toHaveProperty('errorRate');
    });
    it('应该能够优化图像', async () => {
      const imageUri = 'https://example.com/test-image.jpg';
      const optimizedUri = await performanceOptimizer.optimizeImage(imageUri, {quality: 0.8,maxWidth: 800,maxHeight: 600;
      });
      expect(optimizedUri).toContain('w=800');
      expect(optimizedUri).toContain('h=600');
      expect(optimizedUri).toContain('q=80');
    });
    it('应该能够优化网络请求', async () => {
      const mockResponse = new Response(JSON.stringify({ success: true }), {status: 200,headers: { 'Content-Type': 'application/json' };
      });
      // 模拟fetch
      global.fetch = jest.fn().mockResolvedValue(mockResponse);
      const response = await performanceOptimizer.optimizeNetworkRequest(;
        'https://api.example.com/test',{ method: 'GET' },{ enableCaching: true, retryAttempts: 2 };
      );
      expect(response.status).toBe(200);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });
    it('应该生成性能报告', () => {
      const report = performanceOptimizer.generatePerformanceReport();
      const reportData = JSON.parse(report);
      expect(reportData).toHaveProperty('timestamp');
      expect(reportData).toHaveProperty('metrics');
      expect(reportData).toHaveProperty('cacheStats');
      expect(reportData).toHaveProperty('recommendations');
    });
  });
  describe('缓存管理器集成', () => {
    it('应该能够缓存和检索诊断结果', async () => {
      const sessionId = 'test-session-123';
      const diagnosisData = {
      constitution: "气虚质",
      healthScore: 75,recommendations: ["多休息",适量运动'];
      };
      await diagnosisCacheManager.cacheDiagnosisResult(sessionId, diagnosisData);
      const cachedData = await diagnosisCacheManager.getCachedResult(sessionId);
      expect(cachedData).toEqual(diagnosisData);
    });
    it('应该能够管理缓存生命周期', async () => {
      const sessionId = 'test-session-ttl';
      const data = { test: 'data' };
      await diagnosisCacheManager.cacheDiagnosisResult(sessionId, data, 100); // 100ms TTL
      // 立即检索应该成功
      let cachedData = await diagnosisCacheManager.getCachedResult(sessionId);
      expect(cachedData).toEqual(data);
      // 等待TTL过期
      await new Promise(resolve => setTimeout(resolve, 150));
      // 过期后应该返回null
      cachedData = await diagnosisCacheManager.getCachedResult(sessionId);
      expect(cachedData).toBeNull();
    });
    it('应该提供缓存统计信息', async () => {
      const stats = await diagnosisCacheManager.getCacheStats();
      expect(stats).toHaveProperty('totalEntries');
      expect(stats).toHaveProperty('hitRate');
      expect(stats).toHaveProperty('memoryUsage');
      expect(stats).toHaveProperty('lastCleanup');
    });
  });
  describe('五诊服务集成', () => {
    it('应该能够执行完整的五诊流程', async () => {
      const diagnosisData = {basicInfo: {age: 30,gender: 'male',height: 175,weight: 70;
        },lookDiagnosis: {
      faceImage: "data:image/jpeg;base64,test",
      tongueImage: 'data:image/jpeg;base64,test'
        },
        listenDiagnosis: {
          voiceData: 'data:audio/wav;base64,test'
        },
        inquiryDiagnosis: {
          symptoms: ["头痛",失眠'],
          sleepQuality: 'poor',
          appetite: 'normal'
        },
        palpationDiagnosis: {
          pulseData: {
            pressure: 0.6,
            frequency: 80,
            smoothness: 0.8
          }
        }
      };
      const result = await fiveDiagnosisService.performComprehensiveDiagnosis(diagnosisData);
      expect(result).toHaveProperty('sessionId');
      expect(result).toHaveProperty('constitution');
      expect(result).toHaveProperty('healthScore');
      expect(result).toHaveProperty('recommendations');
      expect(result).toHaveProperty('detailedAnalysis');
      expect(result.healthScore).toBeGreaterThan(0);
      expect(result.healthScore).toBeLessThanOrEqual(100);
    });
    it('应该能够处理部分诊断数据', async () => {
      const partialData = {basicInfo: {age: 25,gender: 'female';
        },inquiryDiagnosis: {symptoms: ["乏力",气短'];
        };
      };
      const result = await fiveDiagnosisService.performComprehensiveDiagnosis(partialData);
      expect(result).toHaveProperty('sessionId');
      expect(result).toHaveProperty('constitution');
      expect(result.healthScore).toBeGreaterThan(0);
    });
    it('应该能够获取诊断历史', async () => {
      const history = await fiveDiagnosisService.getDiagnosisHistory();
      expect(Array.isArray(history)).toBe(true);
      if (history.length > 0) {
        const firstRecord = history[0];
        expect(firstRecord).toHaveProperty('sessionId');
        expect(firstRecord).toHaveProperty('timestamp');
        expect(firstRecord).toHaveProperty('constitution');
        expect(firstRecord).toHaveProperty('healthScore');
      }
    });
  });
  describe('服务间协作测试', () => {
    it('应该能够协调本地AI和缓存服务', async () => {
      const symptoms = ["头痛",失眠'];
      const cacheKey = `symptoms_${symptoms.join('_')}`;
      // 第一次调用，应该使用AI服务
      const result1 = await localAIService.classifySymptoms(symptoms);
      // 缓存结果
      await diagnosisCacheManager.cacheAnalysisResult(cacheKey, result1);
      // 第二次调用，应该从缓存获取
      const cachedResult = await diagnosisCacheManager.getCachedResult(cacheKey);
      expect(cachedResult).toEqual(result1);
    });
    it('应该能够协调性能优化和网络请求', async () => {
      const testUrl = 'https://api.example.com/diagnosis';
      const testData = { symptoms: ['头痛'] };
      // 模拟网络响应
      global.fetch = jest.fn().mockResolvedValue(
        new Response(JSON.stringify({ result: 'success' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        })
      );
      const response = await performanceOptimizer.optimizeNetworkRequest(testUrl, {
      method: "POST",
      body: JSON.stringify(testData),headers: { 'Content-Type': 'application/json' };
      });
      expect(response.status).toBe(200);
      const metrics = performanceOptimizer.getPerformanceMetrics();
      expect(metrics.networkLatency).toBeGreaterThan(0);
    });
    it('应该能够处理服务故障和降级', async () => {
      // 模拟网络故障
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
      try {
        await performanceOptimizer.optimizeNetworkRequest(
          'https://api.example.com/failing-endpoint',
          { method: 'GET' },
          { retryAttempts: 2 }
        );
      } catch (error) {
        expect(error).toBeInstanceOf(Error);
      }
      // 验证本地AI服务仍然可用
      const symptoms = ['头痛'];
      const result = await localAIService.classifySymptoms(symptoms);
      expect(result.confidence).toBeGreaterThan(0);
    });
  });
  describe('数据一致性测试', () => {
    it('应该保持诊断数据的一致性', async () => {
      const diagnosisData = {basicInfo: { age: 30, gender: 'male' },inquiryDiagnosis: { symptoms: ["头痛",失眠'] };
      };
      const result = await fiveDiagnosisService.performComprehensiveDiagnosis(diagnosisData);
      // 验证结果的一致性
      expect(result.sessionId).toMatch(/^[a-f0-9-]{36}$/); // UUID格式
      expect(typeof result.healthScore).toBe('number');
      expect(Array.isArray(result.recommendations)).toBe(true);
      // 验证缓存的一致性
      const cachedResult = await diagnosisCacheManager.getCachedResult(result.sessionId);
      expect(cachedResult).toBeDefined();
    });
    it('应该正确处理并发诊断请求', async () => {
      const requests = Array.from({ length: 5 }, (_, i) => ({basicInfo: { age: 25 + i, gender: i % 2 === 0 ? 'male' : 'female' },inquiryDiagnosis: { symptoms: ['症状' + i] };
      }));
      const results = await Promise.all(;
        requests.map(data => fiveDiagnosisService.performComprehensiveDiagnosis(data));
      );
      // 验证所有结果都是唯一的
      const sessionIds = results.map(r => r.sessionId);
      const uniqueSessionIds = new Set(sessionIds);
      expect(uniqueSessionIds.size).toBe(sessionIds.length);
      // 验证所有结果都有效
      results.forEach(result => {
        expect(result.healthScore).toBeGreaterThan(0);
        expect(result.constitution).toBeDefined();
      });
    });
  });
  describe('性能基准测试', () => {
    it('本地AI推理应该在合理时间内完成', async () => {
      const startTime = Date.now();
      await Promise.all([
        localAIService.classifySymptoms(["头痛",失眠']),
        localAIService.analyzeConstitution({ symptoms: ['乏力'] }),
        localAIService.recognizePulse({ pressure: 0.5, frequency: 75, smoothness: 0.7 });
      ]);
      const duration = Date.now() - startTime;
      expect(duration).toBeLessThan(2000); // 应在2秒内完成
    });
    it('缓存操作应该快速响应', async () => {
      const operations = [];
      for (let i = 0; i < 100; i++) {
        operations.push(diagnosisCacheManager.cacheDiagnosisResult(`test-${i}`, { data: i }));
      }
      const startTime = Date.now();
      await Promise.all(operations);
      const duration = Date.now() - startTime;
      expect(duration).toBeLessThan(1000); // 100个缓存操作应在1秒内完成
    });
    it('完整诊断流程应该在合理时间内完成', async () => {
      const diagnosisData = {basicInfo: { age: 30, gender: 'male' },inquiryDiagnosis: { symptoms: ['头痛'] };
      };
      const startTime = Date.now();
      const result = await fiveDiagnosisService.performComprehensiveDiagnosis(diagnosisData);
      const duration = Date.now() - startTime;
      expect(duration).toBeLessThan(5000); // 应在5秒内完成
      expect(result).toBeDefined();
    });
  });
});
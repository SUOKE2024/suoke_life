import { RAGService } from '../ragService';
// Mock dependencies
jest.mock('../../utils/eventEmitter');
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn();
}));
describe('RAGService', () => {
  let ragService: RAGService;
  let mockEventEmitter: jest.Mocked<EventEmitter>;
  beforeEach(() => {
    mockEventEmitter = new EventEmitter() as jest.Mocked<EventEmitter>;
    ragService = new RAGService();
    jest.clearAllMocks();
  });
  afterEach(() => {
    ragService.destroy();
  });
  describe('基础查询功能', () => {
    it('应该成功执行基础查询', async () => {
      const query = '什么是高血压？';
      const mockResponse = {success: true,data: {
      answer: "高血压是一种常见的心血管疾病...",
      confidence: 0.95,sources: ["医学百科", "临床指南'];
        };
      };
      // Mock fetch response
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse);
      });
      const result = await ragService.query(query);
      expect(result.success).toBe(true);
      expect(result.data.answer).toContain('高血压');
      expect(result.data.confidence).toBeGreaterThan(0.8);
    });
    it('应该处理查询错误', async () => {
      const query = '无效查询';
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
      const result = await ragService.query(query);
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });
    it('应该支持不同的查询类型', async () => {
      const queries = [;
        {
      text: "诊断查询",
      type: 'diagnosis' as const },{
      text: "治疗查询",
      type: 'treatment' as const },{
      text: "预防查询", "
      type: 'prevention' as const };
      ];
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { answer: 'test' } });
      });
      for (const query of queries) {
        const result = await ragService.query(query.text, { type: query.type });
        expect(result.success).toBe(true);
      }
    });
  });
  describe('流式查询功能', () => {
    it('应该支持流式查询', async () => {
      const query = '详细解释糖尿病的治疗方案';
      const chunks = ["糖尿病", "是一种', '代谢性疾病'];
      let chunkIndex = 0;
      // Mock EventSource
      const mockEventSource = {addEventListener: jest.fn((event, callback) => {if (event === 'message') {chunks.forEach((((chunk, index) => {setTimeout(() => {callback({ data: JSON.stringify({ chunk, done: index === chunks.length - 1 }) });)))))
              }, index * 100);
            });
          }
        }),
        close: jest.fn();
      };
      global.EventSource = jest.fn().mockImplementation(() => mockEventSource);
      const receivedChunks: string[] = [];
      await ragService.streamQuery(query, chunk => {
        receivedChunks.push(chunk);
      });
      // Wait for all chunks
      await new Promise(resolve => setTimeout(resolve, 500));
      expect(receivedChunks).toEqual(chunks);
    });
  });
  describe('中医分析功能', () => {
    it('应该执行中医证候分析', async () => {
      const symptoms = ["头痛", "失眠', '心悸'];
      const constitution = '气虚质';
      const mockResponse = {success: true,data: {
      syndrome: "心脾两虚证", "
      confidence: 0.88,description: '心脾两虚，气血不足...',recommendations: ["补益心脾", "养血安神'];
        };
      };
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse);
      });
      const result = await ragService.analyzeTCMSyndrome(symptoms, constitution);
      expect(result.success).toBe(true);
      expect(result.data.syndrome).toBe('心脾两虚证');
      expect(result.data.confidence).toBeGreaterThan(0.8);
    });
    it('应该提供中药推荐', async () => {
      const syndrome = '肝郁气滞证';
      const constitution = '气郁质';
      const mockResponse = {success: true,data: {formulas: [;
            {
      name: "逍遥散",
      ingredients: ["柴胡", "当归', '白芍'],dosage: '每日两次，每次6g',duration: '2-4周';
            };
          ],precautions: ["孕妇慎用", "过敏体质注意'];
        };
      };
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse);
      });
      const result = await ragService.recommendHerbs(syndrome, constitution);
      expect(result.success).toBe(true);
      expect(result.data.formulas).toHaveLength(1);
      expect(result.data.formulas[0].name).toBe('逍遥散');
    });
  });
  describe('多模态查询功能', () => {
    it('应该处理图像查询', async () => {
      const imageData = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...';
      const query = '分析这张舌诊图片';
      const mockResponse = {success: true,data: {
      analysis: "舌质淡红，苔薄白，属正常舌象",
      confidence: 0.92,features: ["舌质淡红", "苔薄白', '舌体适中'];
        };
      };
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse);
      });
      const result = await ragService.multimodalQuery({text: query,images: [imageData],modality: 'image';)
      });
      expect(result.success).toBe(true);
      expect(result.data.analysis).toContain('舌象');
    });
    it('应该处理音频查询', async () => {
      const audioData = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10...';
      const query = '分析这段咳嗽声音';
      const mockResponse = {success: true,data: {
      analysis: "干咳，频率较高，可能为燥咳",
      confidence: 0.85,characteristics: ["干咳", "频率高', '无痰音'];
        };
      };
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse);
      });
      const result = await ragService.multimodalQuery({text: query,audio: audioData,modality: 'audio';)
      });
      expect(result.success).toBe(true);
      expect(result.data.analysis).toContain('咳嗽');
    });
  });
  describe('缓存功能', () => {
    it('应该缓存查询结果', async () => {
      const query = '什么是感冒？';
      const mockResponse = {success: true,data: { answer: '感冒是常见的呼吸道疾病' };
      };
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse);
      });
      // 第一次查询
      await ragService.query(query);
      expect(fetch).toHaveBeenCalledTimes(1);
      // 第二次查询应该使用缓存
      await ragService.query(query);
      expect(fetch).toHaveBeenCalledTimes(1); // 仍然是1次，说明使用了缓存
    });
    it('应该正确管理缓存大小', async () => {
      // 模拟大量查询以测试LRU缓存
      const queries = Array.from({ length: 150 }, (_, i) => `查询${i}`);
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { answer: 'test' } });
      });
      for (const query of queries) {
        await ragService.query(query);
      }
      const cacheStats = ragService.getCacheStats();
      expect(cacheStats.size).toBeLessThanOrEqual(100); // 默认缓存大小限制
    });
    it('应该提供缓存统计信息', () => {
      const stats = ragService.getCacheStats();
      expect(stats).toHaveProperty('size');
      expect(stats).toHaveProperty('hits');
      expect(stats).toHaveProperty('misses');
      expect(stats).toHaveProperty('hitRate');
      expect(typeof stats.size).toBe('number');
      expect(typeof stats.hitRate).toBe('number');
    });
  });
  describe('性能监控', () => {
    it('应该记录查询性能指标', async () => {
      const query = '性能测试查询';
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { answer: 'test' } });
      });
      await ragService.query(query);
      const metrics = ragService.getPerformanceMetrics();
      expect(metrics.totalQueries).toBeGreaterThan(0);
      expect(metrics.averageResponseTime).toBeGreaterThan(0);
      expect(metrics.successRate).toBeGreaterThanOrEqual(0);
      expect(metrics.successRate).toBeLessThanOrEqual(1);
    });
    it('应该正确计算成功率', async () => {
      // 成功查询
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { answer: 'test' } });
      });
      await ragService.query('成功查询');
      // 失败查询
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
      await ragService.query('失败查询');
      const metrics = ragService.getPerformanceMetrics();
      expect(metrics.successRate).toBe(0.5); // 50%成功率
    });
  });
  describe('事件系统', () => {
    it('应该触发查询开始事件', async () => {
      const onQueryStart = jest.fn();
      ragService.on('queryStart', onQueryStart);
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { answer: 'test' } });
      });
      await ragService.query('测试查询');
      expect(onQueryStart).toHaveBeenCalledWith({
      query: "测试查询", "
      timestamp: expect.any(Number);
      });
    });
    it('应该触发查询完成事件', async () => {
      const onQueryComplete = jest.fn();
      ragService.on('queryComplete', onQueryComplete);
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true, data: { answer: 'test' } });
      });
      await ragService.query('测试查询');
      expect(onQueryComplete).toHaveBeenCalledWith({
      query: "测试查询", "
      success: true,
        responseTime: expect.any(Number);
      });
    });
    it('应该触发错误事件', async () => {
      const onError = jest.fn();
      ragService.on('error', onError);
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
      await ragService.query('错误查询');
      expect(onError).toHaveBeenCalledWith({
      query: "错误查询",
      error: expect.any(Error);
      });
    });
  });
  describe('配置管理', () => {
    it('应该支持自定义配置', () => {
      const customConfig = {maxCacheSize: 200,cacheTimeout: 600000,retryAttempts: 5;
      };
      const customRagService = new RAGService(customConfig);
      expect(customRagService).toBeDefined();
      // 配置应该被正确应用（通过行为验证）
    });
    it('应该使用默认配置', () => {
      const defaultRagService = new RAGService();
      expect(defaultRagService).toBeDefined();
      expect(defaultRagService.getCacheStats().size).toBe(0);
    });
  });
  describe('资源清理', () => {
    it('应该正确清理资源', () => {
      const ragServiceToDestroy = new RAGService();
      expect(() => {
        ragServiceToDestroy.destroy();
      }).not.toThrow();
    });
    it('应该清除所有缓存', () => {
      ragService.clearCache();
      const stats = ragService.getCacheStats();
      expect(stats.size).toBe(0);
      expect(stats.hits).toBe(0);
      expect(stats.misses).toBe(0);
    });
  });
});
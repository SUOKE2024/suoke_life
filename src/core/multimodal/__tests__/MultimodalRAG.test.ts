import { 
  MultimodalRAGService, 
  VectorDatabase, 
  LanguageModel,
  MultimodalQuery,
  { RetrievalResult  } from '../MultimodalRAGService';
import { ModalityType } from '../MultimodalEmbeddingFusion';

// 模拟向量数据库实现
class MockVectorDatabase implements VectorDatabase {
  private documents: Map<string, { embedding: number[]; metadata: Record<string, any> }> = new Map();
  private indices: Set<number> = new Set();

  async search(embedding: number[], topK: number, filter?: Record<string, any>): Promise<RetrievalResult[]> {
    const results: RetrievalResult[] = [];
    
    for (const [id, doc] of this.documents) {
      // 计算余弦相似度
      const score = this.cosineSimilarity(embedding, doc.embedding);
      
      if (score > 0.5) { // 简单的阈值过滤
        results.push({
          id,
          content: doc.metadata.content || '',
          modality: doc.metadata.modality || ModalityType.TEXT,
          score,
          metadata: doc.metadata,
          embedding: doc.embedding
        });
      }
    }
    
    // 按分数排序并返回topK个结果
    return results
      .sort((a, b) => b.score - a.score)
      .slice(0, topK);
  }

  async insert(id: string, embedding: number[], metadata: Record<string, any>): Promise<void> {
    this.documents.set(id, { embedding, metadata });
  }

  async update(id: string, embedding: number[], metadata: Record<string, any>): Promise<void> {
    if (this.documents.has(id)) {
      this.documents.set(id, { embedding, metadata });
    }
  }

  async delete(id: string): Promise<void> {
    this.documents.delete(id);
  }

  async createIndex(dimension: number, metric?: string): Promise<void> {
    this.indices.add(dimension);
  }

  private cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) return 0;
    
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }
}

// 模拟语言模型实现
class MockLanguageModel implements LanguageModel {
  async generate(prompt: string, context: string[], options?: Record<string, any>): Promise<string> {
    // 模拟生成回答
    return `基于提供的信息，这是一个模拟的中医诊断回答。上下文包含${context.length}个相关文档。`;
  }

  async generateWithReasoning(prompt: string, context: string[]): Promise<{ answer: string; reasoning: string }> {
    const answer = await this.generate(prompt, context);
    const reasoning = `推理过程：
1. 分析了用户提供的多模态信息
2. 检索了${context.length}个相关的医学文档
3. 结合中医理论进行综合分析
4. 给出了专业的诊断建议`;
    
    return { answer, reasoning };
  }
}

describe('MultimodalRAGService', () => {
  let ragService: MultimodalRAGService;
  let mockVectorDB: MockVectorDatabase;
  let mockLanguageModel: MockLanguageModel;

  beforeEach(async () => {
    mockVectorDB = new MockVectorDatabase();
    mockLanguageModel = new MockLanguageModel();
    ragService = new MultimodalRAGService(mockVectorDB, mockLanguageModel);
    
    // 添加一些测试文档
    await ragService.addDocuments([
      {
        id: 'doc1',
        content: '舌质红，苔薄黄，脉数，多见于热证。治疗宜清热解毒。',
        modality: ModalityType.TEXT,
        metadata: { category: '中医诊断', syndrome: '热证' }
      },
      {
        id: 'doc2',
        content: '舌质淡，苔白厚，脉缓，多见于寒证。治疗宜温阳散寒。',
        modality: ModalityType.TEXT,
        metadata: { category: '中医诊断', syndrome: '寒证' }
      },
      {
        id: 'doc3',
        content: '脉象浮数，主表热证；脉象沉迟，主里寒证。',
        modality: ModalityType.TEXT,
        metadata: { category: '脉诊', type: '脉象分析' }
      }
    ]);
  });

  afterEach(async () => {
    await ragService.cleanup();
  });

  test('应该能够初始化服务', async () => {
    await ragService.initialize();
    const stats = ragService.getStats();
    expect(stats.isInitialized).toBe(true);
    expect(stats.supportedModalities).toContain(ModalityType.TEXT);
    expect(stats.supportedModalities).toContain(ModalityType.TONGUE);
    expect(stats.supportedModalities).toContain(ModalityType.PULSE);
  });

  test('应该能够处理纯文本查询', async () => {
    const query: MultimodalQuery = {
      text: '患者舌质红，苔薄黄，应该如何治疗？',
      strategy: 'text_dominant',
      topK: 3,
      threshold: 0.5
    };

    const response = await ragService.query(query);

    expect(response).toBeDefined();
    expect(response.answer).toContain('模拟的中医诊断回答');
    expect(response.confidence).toBeGreaterThan(0);
    expect(response.sources.length).toBeGreaterThan(0);
    expect(response.fusionResult).toBeDefined();
    expect(response.reasoning).toContain('推理过程');
  });

  test('应该能够处理多模态查询', async () => {
    // 模拟舌象图像数据
    const mockTongueImage = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...';
    
    // 模拟脉象信号数据
    const mockPulseSignal = Array.from({ length: 1000 }, (_, i) => 
      Math.sin(i * 0.1) + Math.random() * 0.1
    );

    const query: MultimodalQuery = {
      text: '请分析这个患者的舌象和脉象',
      tongueImage: mockTongueImage,
      pulseSignal: mockPulseSignal,
      strategy: 'tcm_diagnosis',
      topK: 5,
      threshold: 0.6
    };

    const response = await ragService.query(query);

    expect(response).toBeDefined();
    expect(response.metadata.queryModalities).toContain(ModalityType.TEXT);
    expect(response.metadata.queryModalities).toContain(ModalityType.TONGUE);
    expect(response.metadata.queryModalities).toContain(ModalityType.PULSE);
    expect(response.metadata.fusionStrategy).toBe('tcm_diagnosis');
  });

  test('应该能够缓存查询结果', async () => {
    const query: MultimodalQuery = {
      text: '测试缓存功能',
      strategy: 'text_dominant'
    };

    // 第一次查询
    const response1 = await ragService.query(query);
    
    // 第二次查询应该从缓存返回
    const response2 = await ragService.query(query);

    expect(response1).toEqual(response2);
    
    const stats = ragService.getStats();
    expect(stats.queryCacheSize).toBeGreaterThan(0);
  });

  test('应该能够添加自定义融合策略', () => {
    const customStrategy = {
      name: 'custom_strategy',
      weights: {
        [ModalityType.TEXT]: 0.5,
        [ModalityType.TONGUE]: 0.3,
        [ModalityType.PULSE]: 0.2,
        [ModalityType.AUDIO]: 0.0,
        [ModalityType.IMAGE]: 0.0
      },
      method: 'weighted_sum' as const
    };

    ragService.addFusionStrategy(customStrategy);
    
    const strategies = ragService.getSupportedStrategies();
    expect(strategies).toContain('custom_strategy');
  });

  test('应该能够处理错误情况', async () => {
    const invalidQuery: MultimodalQuery = {
      // 没有提供任何模态数据
      strategy: 'tcm_diagnosis'
    };

    await expect(ragService.query(invalidQuery)).rejects.toThrow();
  });

  test('应该能够清理缓存', async () => {
    const query: MultimodalQuery = {
      text: '测试缓存清理',
      strategy: 'text_dominant'
    };

    await ragService.query(query);
    
    let stats = ragService.getStats();
    expect(stats.queryCacheSize).toBeGreaterThan(0);

    ragService.clearCache();
    
    stats = ragService.getStats();
    expect(stats.queryCacheSize).toBe(0);
  });

  test('应该能够批量添加文档', async () => {
    const documents = [
      {
        id: 'batch1',
        content: '批量添加的文档1',
        modality: ModalityType.TEXT,
        metadata: { batch: true }
      },
      {
        id: 'batch2',
        content: '批量添加的文档2',
        modality: ModalityType.TEXT,
        metadata: { batch: true }
      }
    ];

    await expect(ragService.addDocuments(documents)).resolves.not.toThrow();
  });
});

// 集成测试示例
describe('MultimodalRAG Integration Tests', () => {
  test('完整的中医诊断流程', async () => {
    const mockVectorDB = new MockVectorDatabase();
    const mockLanguageModel = new MockLanguageModel();
    const ragService = new MultimodalRAGService(mockVectorDB, mockLanguageModel);

    // 1. 初始化服务
    await ragService.initialize();

    // 2. 添加中医知识库
    await ragService.addDocuments([
      {
        id: 'tcm_knowledge_1',
        content: '舌红苔黄，脉数有力，为实热证。治宜清热泻火，方用白虎汤。',
        modality: ModalityType.TEXT,
        metadata: { 
          category: '中医诊断',
          syndrome: '实热证',
          prescription: '白虎汤'
        }
      },
      {
        id: 'tcm_knowledge_2',
        content: '舌淡苔白，脉沉细，为虚寒证。治宜温阳补气，方用四君子汤。',
        modality: ModalityType.TEXT,
        metadata: { 
          category: '中医诊断',
          syndrome: '虚寒证',
          prescription: '四君子汤'
        }
      }
    ]);

    // 3. 模拟患者多模态数据
    const patientQuery: MultimodalQuery = {
      text: '患者主诉：口干舌燥，大便干结，小便黄赤',
      tongueImage: 'mock_tongue_image_data',
      pulseSignal: Array.from({ length: 500 }, (_, i) => 
        Math.sin(i * 0.2) * 2 + Math.random() * 0.5 // 模拟数脉
      ),
      strategy: 'tcm_diagnosis',
      topK: 3,
      threshold: 0.6,
      metadata: {
        patientId: 'patient_001',
        consultationDate: new Date().toISOString()
      }
    };

    // 4. 执行诊断查询
    const diagnosis = await ragService.query(patientQuery);

    // 5. 验证诊断结果
    expect(diagnosis.answer).toBeDefined();
    expect(diagnosis.confidence).toBeGreaterThan(0);
    expect(diagnosis.sources.length).toBeGreaterThan(0);
    expect(diagnosis.fusionResult.modalityWeights).toHaveProperty(ModalityType.TEXT);
    expect(diagnosis.fusionResult.modalityWeights).toHaveProperty(ModalityType.TONGUE);
    expect(diagnosis.fusionResult.modalityWeights).toHaveProperty(ModalityType.PULSE);
    expect(diagnosis.reasoning).toContain('推理过程');

    // 6. 清理资源
    await ragService.cleanup();
  });
}); 
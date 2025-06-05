import { medKnowledgeService } from '../services/medKnowledgeService';
import { laokeKnowledgeIntegration } from '../agents/laoke/medKnowledgeIntegration';

// Mock the service
jest.mock('../services/medKnowledgeService');

describe('医疗知识服务集成测试', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('API客户端测试', () => {
    it('应该能够获取体质列表', async () => {
      const mockConstitutions = [
        {
          id: '1',
          name: '平和质',
          type: '平和质',
          characteristics: ['体形匀称', '面色润泽', '精力充沛'],
          description: '阴阳气血调和，体质平和',
          recommendations: ['保持规律作息', '适量运动'],
          symptoms: [],
          lifestyle: {
            diet: ['均衡饮食'],
            exercise: ['适量运动'],
            sleep: ['规律作息'],
            emotion: ['保持平和心态']
          },
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ];

      (medKnowledgeService.getConstitutions as jest.Mock).mockResolvedValue(mockConstitutions);

      const result = await medKnowledgeService.getConstitutions();
      expect(result).toEqual(mockConstitutions);
      expect(medKnowledgeService.getConstitutions).toHaveBeenCalledTimes(1);
    });

    it('应该能够搜索症状', async () => {
      const mockSymptoms = [
        {
          id: '1',
          name: '头痛',
          category: '神经系统',
          description: '头部疼痛',
          severity: 'moderate' as const,
          related_constitutions: ['气虚质'],
          related_syndromes: ['肝阳上亢'],
          treatments: ['针灸', '中药'],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ];

      (medKnowledgeService.searchSymptoms as jest.Mock).mockResolvedValue(mockSymptoms);

      const result = await medKnowledgeService.searchSymptoms('头痛');
      expect(result).toEqual(mockSymptoms);
      expect(medKnowledgeService.searchSymptoms).toHaveBeenCalledWith('头痛');
    });

    it('应该能够进行知识搜索', async () => {
      const mockSearchResults = [
        {
          id: '1',
          title: '头痛的中医治疗',
          content: '中医认为头痛多由风邪上扰、肝阳上亢等引起',
          type: 'treatment',
          relevance: 0.95,
          source: 'med-knowledge',
          metadata: {}
        }
      ];

      (medKnowledgeService.searchKnowledge as jest.Mock).mockResolvedValue(mockSearchResults);

      const query = { query: '头痛治疗', type: 'treatment' as const };
      const result = await medKnowledgeService.searchKnowledge(query);
      expect(result).toEqual(mockSearchResults);
      expect(medKnowledgeService.searchKnowledge).toHaveBeenCalledWith(query);
    });
  });

  describe('智能体集成测试', () => {
    it('应该能够基于症状分析体质', async () => {
      const mockConstitutions = [
        {
          id: '1',
          name: '气虚质',
          type: '气虚质',
          characteristics: ['气短懒言', '容易疲劳'],
          description: '元气不足，以疲乏、气短为主要特征',
          recommendations: ['补气养血'],
          symptoms: ['疲劳', '气短'],
          lifestyle: {
            diet: ['补气食物'],
            exercise: ['轻度运动'],
            sleep: ['充足睡眠'],
            emotion: ['避免过度思虑']
          },
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ];

      (medKnowledgeService.getConstitutions as jest.Mock).mockResolvedValue(mockConstitutions);

      const symptoms = ['疲劳', '气短'];
      const result = await laokeKnowledgeIntegration.analyzeConstitutionBySymptoms(symptoms);

      expect(result.constitutions).toHaveLength(1);
      expect(result.constitutions[0].type).toBe('气虚质');
      expect(result.confidence).toBeGreaterThan(0);
      expect(result.reasoning).toContain('气虚质');
    });

    it('应该能够获取个性化健康建议', async () => {
      const mockConstitution = {
        id: '1',
        name: '气虚质',
        type: '气虚质',
        characteristics: ['气短懒言'],
        description: '元气不足',
        recommendations: ['补气养血'],
        symptoms: ['疲劳'],
        lifestyle: {
          diet: ['补气食物'],
          exercise: ['轻度运动'],
          sleep: ['充足睡眠'],
          emotion: ['避免过度思虑']
        },
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      const mockRecommendations = [
        {
          id: '1',
          type: 'lifestyle',
          category: 'diet',
          title: '饮食建议',
          description: '多食用补气食物',
          priority: 'high',
          evidence_level: 'strong',
          implementation: {
            frequency: 'daily',
            duration: '长期',
            instructions: ['选择温补食物', '避免生冷食物']
          },
          created_at: '2024-01-01T00:00:00Z'
        }
      ];

      (medKnowledgeService.getConstitutionById as jest.Mock).mockResolvedValue(mockConstitution);
      (medKnowledgeService.getPersonalizedRecommendations as jest.Mock).mockResolvedValue(mockRecommendations);

      const userContext = {
        age: 30,
        gender: 'female',
        currentSymptoms: ['疲劳'],
        lifestyle: ['久坐']
      };

      const result = await laokeKnowledgeIntegration.getPersonalizedAdvice('1', userContext);

      expect(result.constitution).toEqual(mockConstitution);
      expect(result.recommendations).toEqual(mockRecommendations);
      expect(result.customAdvice).toContain('气虚质');
    });

    it('应该能够进行智能症状搜索', async () => {
      const mockSymptoms = [
        {
          id: '1',
          name: '头痛',
          category: '神经系统',
          description: '头部疼痛',
          severity: 'moderate' as const,
          related_constitutions: ['肝郁质'],
          related_syndromes: ['肝阳上亢'],
          treatments: ['针灸', '中药'],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ];

      const mockConstitutions = [
        {
          id: '1',
          name: '肝郁质',
          type: '肝郁质',
          characteristics: ['情志不畅'],
          description: '肝气郁结',
          recommendations: ['疏肝理气'],
          symptoms: ['头痛'],
          lifestyle: {
            diet: ['疏肝食物'],
            exercise: ['舒缓运动'],
            sleep: ['规律作息'],
            emotion: ['调节情绪']
          },
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ];

      (medKnowledgeService.searchSymptoms as jest.Mock).mockResolvedValue(mockSymptoms);
      (medKnowledgeService.getConstitutions as jest.Mock).mockResolvedValue(mockConstitutions);

      const result = await laokeKnowledgeIntegration.intelligentSymptomSearch('头痛');

      expect(result.symptoms).toEqual(mockSymptoms);
      expect(result.relatedConstitutions).toHaveLength(1);
      expect(result.suggestedTreatments).toContain('针灸');
      expect(result.tcmAnalysis).toContain('中医分析');
    });
  });

  describe('错误处理测试', () => {
    it('应该正确处理API错误', async () => {
      (medKnowledgeService.getConstitutions as jest.Mock).mockRejectedValue(
        new Error('网络错误')
      );

      await expect(medKnowledgeService.getConstitutions()).rejects.toThrow('网络错误');
    });

    it('应该正确处理智能体集成错误', async () => {
      (medKnowledgeService.getConstitutions as jest.Mock).mockRejectedValue(
        new Error('服务不可用')
      );

      await expect(
        laokeKnowledgeIntegration.analyzeConstitutionBySymptoms(['头痛'])
      ).rejects.toThrow('体质分析失败');
    });
  });

  describe('服务健康检查测试', () => {
    it('应该能够检查服务健康状态', async () => {
      const mockHealthStatus = {
        status: 'healthy',
        timestamp: '2024-01-01T00:00:00Z',
        version: '1.0.0',
        dependencies: {
          database: 'healthy',
          redis: 'healthy'
        }
      };

      (medKnowledgeService.healthCheck as jest.Mock).mockResolvedValue(mockHealthStatus);

      const result = await medKnowledgeService.healthCheck();
      expect(result).toEqual(mockHealthStatus);
      expect(result.status).toBe('healthy');
    });
  });

  describe('知识图谱测试', () => {
    it('应该能够获取知识图谱数据', async () => {
      const mockGraphData = {
        nodes: [
          {
            id: '1',
            label: '头痛',
            type: 'symptom',
            properties: { severity: 'moderate' }
          },
          {
            id: '2',
            label: '肝阳上亢',
            type: 'syndrome',
            properties: { category: '肝系病证' }
          }
        ],
        edges: [
          {
            id: '1',
            source: '1',
            target: '2',
            type: 'related_to',
            weight: 0.8,
            properties: { relationship: 'symptom_syndrome' }
          }
        ],
        statistics: {
          total_nodes: 2,
          total_edges: 1,
          node_types: {
            symptom: 1,
            syndrome: 1
          }
        }
      };

      (medKnowledgeService.getKnowledgeGraph as jest.Mock).mockResolvedValue(mockGraphData);

      const result = await medKnowledgeService.getKnowledgeGraph();
      expect(result).toEqual(mockGraphData);
      expect(result.nodes).toHaveLength(2);
      expect(result.edges).toHaveLength(1);
    });
  });
}); 
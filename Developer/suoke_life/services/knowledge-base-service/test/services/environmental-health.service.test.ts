/**
 * 环境健康服务单元测试
 */
import mongoose from 'mongoose';
import { EnvironmentalHealthService } from '../../src/services/environmental-health.service';
import EnvironmentalHealthModel from '../../src/models/environmental-health.model';
import { KnowledgeGraphIntegrationService } from '../../src/integrations/knowledge-graph-integration.service';
import { RagIntegrationService } from '../../src/integrations/rag-integration.service';

// 模拟集成服务
jest.mock('../../src/integrations/knowledge-graph-integration.service');
jest.mock('../../src/integrations/rag-integration.service');

describe('环境健康服务测试', () => {
  let environmentalHealthService: EnvironmentalHealthService;
  
  beforeEach(() => {
    // 重置模拟
    jest.clearAllMocks();
    
    // 创建服务实例
    environmentalHealthService = new EnvironmentalHealthService();
    
    // 模拟集成服务方法
    (KnowledgeGraphIntegrationService.prototype.syncEnvironmentalHealth as jest.Mock).mockResolvedValue(undefined);
    (KnowledgeGraphIntegrationService.prototype.deleteEnvironmentalHealth as jest.Mock).mockResolvedValue(undefined);
    (RagIntegrationService.prototype.syncEnvironmentalHealth as jest.Mock).mockResolvedValue(undefined);
    (RagIntegrationService.prototype.deleteEnvironmentalHealth as jest.Mock).mockResolvedValue(undefined);
  });
  
  describe('创建环境健康知识', () => {
    it('应成功创建环境健康知识条目', async () => {
      // 准备测试数据
      const testData = {
        title: '空气污染与健康',
        description: '空气污染对人体健康的影响',
        content: '详细内容...',
        environmentType: '空气',
        pollutantType: ['PM2.5', '臭氧'],
        healthImpacts: ['呼吸系统疾病', '心血管疾病'],
        riskLevel: 4,
        vulnerableGroups: ['老人', '儿童', '孕妇'],
        protectiveMeasures: ['减少外出', '佩戴口罩'],
        preventiveAdvice: ['关闭门窗', '使用空气净化器'],
        keywords: ['空气污染', '健康', 'PM2.5']
      };
      
      // 执行测试
      const result = await environmentalHealthService.createEnvironmentalHealth(testData as any);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.title).toBe(testData.title);
      expect(result.environmentType).toBe(testData.environmentType);
      expect(result.riskLevel).toBe(testData.riskLevel);
      expect(result.createdAt).toBeDefined();
      expect(result.updatedAt).toBeDefined();
      
      // 验证知识图谱同步
      expect(KnowledgeGraphIntegrationService.prototype.syncEnvironmentalHealth).toHaveBeenCalledTimes(1);
      
      // 验证RAG同步
      expect(RagIntegrationService.prototype.syncEnvironmentalHealth).toHaveBeenCalledTimes(1);
    });
  });
  
  describe('获取环境健康知识', () => {
    it('应根据ID获取环境健康知识条目', async () => {
      // 准备测试数据
      const testData = {
        title: '水污染与健康',
        description: '水污染对人体健康的影响',
        content: '详细内容...',
        environmentType: '水',
        pollutantType: ['重金属', '有机物'],
        healthImpacts: ['消化系统疾病', '皮肤病'],
        riskLevel: 3,
        vulnerableGroups: ['儿童', '孕妇'],
        protectiveMeasures: ['饮用纯净水', '过滤水'],
        preventiveAdvice: ['避免饮用未经处理的水'],
        keywords: ['水污染', '健康', '重金属']
      };
      
      // 创建测试数据
      const savedData = await environmentalHealthService.createEnvironmentalHealth(testData as any);
      
      // 执行测试
      const result = await environmentalHealthService.getEnvironmentalHealth(savedData._id);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result!.title).toBe(testData.title);
      expect(result!.environmentType).toBe(testData.environmentType);
      expect(result!.riskLevel).toBe(testData.riskLevel);
    });
    
    it('对于不存在的ID应返回null', async () => {
      // 创建一个有效但不存在的ID
      const nonExistentId = new mongoose.Types.ObjectId().toString();
      
      // 执行测试
      const result = await environmentalHealthService.getEnvironmentalHealth(nonExistentId);
      
      // 验证结果
      expect(result).toBeNull();
    });
  });
  
  describe('更新环境健康知识', () => {
    it('应成功更新环境健康知识条目', async () => {
      // 准备测试数据
      const testData = {
        title: '土壤污染与健康',
        description: '土壤污染对人体健康的影响',
        content: '详细内容...',
        environmentType: '土壤',
        pollutantType: ['农药', '化肥'],
        healthImpacts: ['消化系统疾病', '神经系统疾病'],
        riskLevel: 3,
        vulnerableGroups: ['农民', '儿童'],
        protectiveMeasures: ['洗手', '清洗食物'],
        preventiveAdvice: ['避免直接接触污染土壤'],
        keywords: ['土壤污染', '健康', '农药']
      };
      
      // 创建测试数据
      const savedData = await environmentalHealthService.createEnvironmentalHealth(testData as any);
      
      // 更新数据
      const updateData = {
        title: '土壤重金属污染与健康',
        riskLevel: 4,
        pollutantType: ['重金属', '农药']
      };
      
      // 执行测试
      const result = await environmentalHealthService.updateEnvironmentalHealth(savedData._id, updateData as any);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result!.title).toBe(updateData.title);
      expect(result!.riskLevel).toBe(updateData.riskLevel);
      expect(result!.pollutantType).toContain('重金属');
      expect(result!.environmentType).toBe(testData.environmentType); // 未更新的字段应保持不变
      
      // 验证知识图谱同步
      expect(KnowledgeGraphIntegrationService.prototype.syncEnvironmentalHealth).toHaveBeenCalledTimes(2);
      
      // 验证RAG同步
      expect(RagIntegrationService.prototype.syncEnvironmentalHealth).toHaveBeenCalledTimes(2);
    });
    
    it('对于不存在的ID应返回null', async () => {
      // 创建一个有效但不存在的ID
      const nonExistentId = new mongoose.Types.ObjectId().toString();
      
      // 更新数据
      const updateData = {
        title: '更新的标题',
        riskLevel: 5
      };
      
      // 执行测试
      const result = await environmentalHealthService.updateEnvironmentalHealth(nonExistentId, updateData as any);
      
      // 验证结果
      expect(result).toBeNull();
    });
  });
  
  describe('删除环境健康知识', () => {
    it('应成功删除环境健康知识条目', async () => {
      // 准备测试数据
      const testData = {
        title: '噪音污染与健康',
        description: '噪音污染对人体健康的影响',
        content: '详细内容...',
        environmentType: '噪音',
        pollutantType: ['交通噪音', '工业噪音'],
        healthImpacts: ['听力损伤', '睡眠障碍'],
        riskLevel: 2,
        vulnerableGroups: ['老人', '儿童'],
        protectiveMeasures: ['使用耳塞', '隔音'],
        preventiveAdvice: ['减少噪音暴露'],
        keywords: ['噪音污染', '健康', '听力']
      };
      
      // 创建测试数据
      const savedData = await environmentalHealthService.createEnvironmentalHealth(testData as any);
      
      // 执行测试
      const result = await environmentalHealthService.deleteEnvironmentalHealth(savedData._id);
      
      // 验证结果
      expect(result).toBe(true);
      
      // 验证知识图谱删除
      expect(KnowledgeGraphIntegrationService.prototype.deleteEnvironmentalHealth).toHaveBeenCalledTimes(1);
      
      // 验证RAG删除
      expect(RagIntegrationService.prototype.deleteEnvironmentalHealth).toHaveBeenCalledTimes(1);
      
      // 验证记录已被删除
      const deletedRecord = await environmentalHealthService.getEnvironmentalHealth(savedData._id);
      expect(deletedRecord).toBeNull();
    });
    
    it('对于不存在的ID应返回false', async () => {
      // 创建一个有效但不存在的ID
      const nonExistentId = new mongoose.Types.ObjectId().toString();
      
      // 执行测试
      const result = await environmentalHealthService.deleteEnvironmentalHealth(nonExistentId);
      
      // 验证结果
      expect(result).toBe(false);
    });
  });
  
  describe('获取环境健康知识列表', () => {
    beforeEach(async () => {
      // 创建测试数据
      const testData = [
        {
          title: '空气污染与健康',
          description: '空气污染对人体健康的影响',
          content: '详细内容...',
          environmentType: '空气',
          pollutantType: ['PM2.5', '臭氧'],
          healthImpacts: ['呼吸系统疾病', '心血管疾病'],
          riskLevel: 4,
          vulnerableGroups: ['老人', '儿童', '孕妇'],
          keywords: ['空气污染', '健康', 'PM2.5'],
          regionSpecific: ['北方', '工业区']
        },
        {
          title: '水污染与健康',
          description: '水污染对人体健康的影响',
          content: '详细内容...',
          environmentType: '水',
          pollutantType: ['重金属', '有机物'],
          healthImpacts: ['消化系统疾病', '皮肤病'],
          riskLevel: 3,
          vulnerableGroups: ['儿童', '孕妇'],
          keywords: ['水污染', '健康', '重金属'],
          regionSpecific: ['南方', '工业区']
        },
        {
          title: '土壤污染与健康',
          description: '土壤污染对人体健康的影响',
          content: '详细内容...',
          environmentType: '土壤',
          pollutantType: ['农药', '化肥'],
          healthImpacts: ['消化系统疾病', '神经系统疾病'],
          riskLevel: 3,
          vulnerableGroups: ['农民', '儿童'],
          keywords: ['土壤污染', '健康', '农药'],
          regionSpecific: ['农村', '城郊']
        }
      ];
      
      // 批量创建测试数据
      for (const data of testData) {
        await environmentalHealthService.createEnvironmentalHealth(data as any);
      }
    });
    
    it('应获取所有环境健康知识条目', async () => {
      // 执行测试
      const result = await environmentalHealthService.getEnvironmentalHealthList();
      
      // 验证结果
      expect(result.data).toBeDefined();
      expect(result.data.length).toBe(3);
      expect(result.total).toBe(3);
      expect(result.page).toBe(1);
      expect(result.limit).toBe(20);
      expect(result.totalPages).toBe(1);
    });
    
    it('应根据环境类型过滤结果', async () => {
      // 执行测试
      const result = await environmentalHealthService.getEnvironmentalHealthByType('空气');
      
      // 验证结果
      expect(result.data).toBeDefined();
      expect(result.data.length).toBe(1);
      expect(result.data[0].environmentType).toBe('空气');
      expect(result.total).toBe(1);
    });
    
    it('应根据污染物类型过滤结果', async () => {
      // 执行测试
      const result = await environmentalHealthService.getEnvironmentalHealthByPollutant('重金属');
      
      // 验证结果
      expect(result.data).toBeDefined();
      expect(result.data.length).toBe(1);
      expect(result.data[0].pollutantType).toContain('重金属');
      expect(result.total).toBe(1);
    });
    
    it('应根据健康影响过滤结果', async () => {
      // 执行测试
      const result = await environmentalHealthService.getEnvironmentalHealthByHealthImpact('呼吸系统疾病');
      
      // 验证结果
      expect(result.data).toBeDefined();
      expect(result.data.length).toBe(1);
      expect(result.data[0].healthImpacts).toContain('呼吸系统疾病');
      expect(result.total).toBe(1);
    });
    
    it('应根据地区过滤结果', async () => {
      // 执行测试
      const result = await environmentalHealthService.getEnvironmentalHealthByRegion('工业区');
      
      // 验证结果
      expect(result.data).toBeDefined();
      expect(result.data.length).toBe(2);
      expect(result.total).toBe(2);
    });
    
    it('应根据风险级别过滤结果', async () => {
      // 执行测试
      const result = await environmentalHealthService.getEnvironmentalHealthByRiskLevel(3);
      
      // 验证结果
      expect(result.data).toBeDefined();
      expect(result.data.length).toBe(2);
      expect(result.data[0].riskLevel).toBe(3);
      expect(result.data[1].riskLevel).toBe(3);
      expect(result.total).toBe(2);
    });
    
    it('应支持关键词搜索', async () => {
      // 执行测试
      const result = await environmentalHealthService.searchEnvironmentalHealth('空气');
      
      // 验证结果
      expect(result.data).toBeDefined();
      expect(result.data.length).toBe(1);
      expect(result.data[0].title).toContain('空气');
      expect(result.total).toBe(1);
    });
  });
});
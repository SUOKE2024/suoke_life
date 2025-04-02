/**
 * 心理健康服务单元测试
 */
import mongoose from 'mongoose';
import { MentalHealthService } from '../../src/services/mental-health.service';
import PsychologicalHealthModel from '../../src/models/psychological-health.model';
import { KnowledgeGraphIntegrationService } from '../../src/integrations/knowledge-graph-integration.service';
import { RagIntegrationService } from '../../src/integrations/rag-integration.service';

// 模拟集成服务
jest.mock('../../src/integrations/knowledge-graph-integration.service');
jest.mock('../../src/integrations/rag-integration.service');

describe('心理健康服务测试', () => {
  let mentalHealthService: MentalHealthService;
  
  beforeEach(() => {
    // 重置模拟
    jest.clearAllMocks();
    
    // 创建服务实例
    mentalHealthService = new MentalHealthService();
    
    // 模拟集成服务方法
    (KnowledgeGraphIntegrationService.prototype.syncMentalHealth as jest.Mock).mockResolvedValue(undefined);
    (KnowledgeGraphIntegrationService.prototype.deleteMentalHealth as jest.Mock).mockResolvedValue(undefined);
    (RagIntegrationService.prototype.syncMentalHealth as jest.Mock).mockResolvedValue(undefined);
    (RagIntegrationService.prototype.deleteMentalHealth as jest.Mock).mockResolvedValue(undefined);
  });
  
  describe('创建心理健康知识', () => {
    it('应成功创建心理健康知识条目', async () => {
      // 准备测试数据
      const testData = {
        title: '焦虑障碍管理',
        description: '焦虑障碍的识别与管理方法',
        content: '详细内容...',
        issueType: '焦虑障碍',
        symptoms: ['担忧', '紧张', '心悸'],
        possibleCauses: ['遗传因素', '环境压力', '性格特质'],
        interventionMethods: ['认知行为疗法', '放松训练'],
        treatmentMethods: ['药物治疗', '心理治疗'],
        selfHelpMeasures: ['正念冥想', '规律作息'],
        targetAgeGroups: ['青少年', '成人'],
        keywords: ['焦虑', '心理健康', '认知行为疗法']
      };
      
      // 执行测试
      const result = await mentalHealthService.createMentalHealth(testData as any);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.title).toBe(testData.title);
      expect(result.issueType).toBe(testData.issueType);
      expect(result.symptoms).toEqual(expect.arrayContaining(testData.symptoms));
      expect(result.createdAt).toBeDefined();
      expect(result.updatedAt).toBeDefined();
      
      // 验证知识图谱同步
      expect(KnowledgeGraphIntegrationService.prototype.syncMentalHealth).toHaveBeenCalledTimes(1);
      
      // 验证RAG同步
      expect(RagIntegrationService.prototype.syncMentalHealth).toHaveBeenCalledTimes(1);
    });
  });
  
  describe('获取心理健康知识', () => {
    it('应根据ID获取心理健康知识条目', async () => {
      // 准备测试数据
      const testData = {
        title: '抑郁症治疗指南',
        description: '抑郁症的识别与治疗方法',
        content: '详细内容...',
        issueType: '抑郁症',
        symptoms: ['持续低落情绪', '兴趣丧失', '疲劳'],
        possibleCauses: ['遗传因素', '生化失衡', '压力事件'],
        interventionMethods: ['认知行为疗法', '人际关系疗法'],
        treatmentMethods: ['抗抑郁药物', '精神动力学疗法'],
        selfHelpMeasures: ['规律运动', '社交支持'],
        targetAgeGroups: ['青少年', '成人', '老年人'],
        keywords: ['抑郁', '心理健康', '治疗']
      };
      
      // 创建测试数据
      const savedData = await mentalHealthService.createMentalHealth(testData as any);
      
      // 执行测试
      const result = await mentalHealthService.getMentalHealth(savedData._id);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result!.title).toBe(testData.title);
      expect(result!.issueType).toBe(testData.issueType);
      expect(result!.symptoms).toEqual(expect.arrayContaining(testData.symptoms));
    });
    
    it('对于不存在的ID应返回null', async () => {
      // 创建一个有效但不存在的ID
      const nonExistentId = new mongoose.Types.ObjectId().toString();
      
      // 执行测试
      const result = await mentalHealthService.getMentalHealth(nonExistentId);
      
      // 验证结果
      expect(result).toBeNull();
    });
  });
  
  describe('更新心理健康知识', () => {
    it('应成功更新心理健康知识条目', async () => {
      // 准备测试数据
      const testData = {
        title: '强迫症干预方法',
        description: '强迫症的识别与干预方法',
        content: '详细内容...',
        issueType: '强迫症',
        symptoms: ['反复检查', '过度清洁', '反复思维'],
        possibleCauses: ['遗传因素', '大脑化学物质失衡'],
        interventionMethods: ['暴露与反应预防', '认知行为疗法'],
        treatmentMethods: ['选择性5-羟色胺再摄取抑制剂', '心理治疗'],
        selfHelpMeasures: ['渐进式放松', '思维记录'],
        targetAgeGroups: ['青少年', '成人'],
        keywords: ['强迫症', '心理健康', 'OCD']
      };
      
      // 创建测试数据
      const savedData = await mentalHealthService.createMentalHealth(testData as any);
      
      // 更新数据
      const updateData = {
        title: '强迫障碍(OCD)综合干预方法',
        interventionMethods: ['暴露与反应预防', '认知行为疗法', '接受与承诺疗法'],
        symptoms: ['反复检查', '过度清洁', '反复思维', '仪式化行为']
      };
      
      // 执行测试
      const result = await mentalHealthService.updateMentalHealth(savedData._id, updateData as any);
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result!.title).toBe(updateData.title);
      expect(result!.interventionMethods).toEqual(expect.arrayContaining(updateData.interventionMethods));
      expect(result!.symptoms).toEqual(expect.arrayContaining(updateData.symptoms));
      expect(result!.issueType).toBe(testData.issueType); // 未更新的字段应保持不变
      
      // 验证知识图谱同步
      expect(KnowledgeGraphIntegrationService.prototype.syncMentalHealth).toHaveBeenCalledTimes(2);
      
      // 验证RAG同步
      expect(RagIntegrationService.prototype.syncMentalHealth).toHaveBeenCalledTimes(2);
    });
    
    it('对于不存在的ID应返回null', async () => {
      // 创建一个有效但不存在的ID
      const nonExistentId = new mongoose.Types.ObjectId().toString();
      
      // 更新数据
      const updateData = {
        title: '更新的标题',
        symptoms: ['新症状1', '新症状2']
      };
      
      // 执行测试
      const result = await mentalHealthService.updateMentalHealth(nonExistentId, updateData as any);
      
      // 验证结果
      expect(result).toBeNull();
    });
  });
  
  describe('删除心理健康知识', () => {
    it('应成功删除心理健康知识条目', async () => {
      // 准备测试数据
      const testData = {
        title: '社交焦虑障碍指南',
        description: '社交焦虑障碍的识别与治疗方法',
        content: '详细内容...',
        issueType: '社交焦虑障碍',
        symptoms: ['社交场合恐惧', '过度自我意识', '回避行为'],
        possibleCauses: ['遗传因素', '负面社交经历'],
        interventionMethods: ['认知行为疗法', '社交技能训练'],
        treatmentMethods: ['药物治疗', '系统化脱敏'],
        selfHelpMeasures: ['渐进式暴露', '自我肯定训练'],
        targetAgeGroups: ['青少年', '成人'],
        keywords: ['社交焦虑', '社恐', '心理健康']
      };
      
      // 创建测试数据
      const savedData = await mentalHealthService.createMentalHealth(testData as any);
      
      // 执行测试
      const result = await mentalHealthService.deleteMentalHealth(savedData._id);
      
      // 验证结果
      expect(result).toBe(true);
      
      // 验证知识图谱删除
      expect(KnowledgeGraphIntegrationService.prototype.deleteMentalHealth).toHaveBeenCalledTimes(1);
      
      // 验证RAG删除
      expect(RagIntegrationService.prototype.deleteMentalHealth).toHaveBeenCalledTimes(1);
      
      // 验证记录已被删除
      const deletedRecord = await mentalHealthService.getMentalHealth(savedData._id);
      expect(deletedRecord).toBeNull();
    });
    
    it('对于不存在的ID应返回false', async () => {
      // 创建一个有效但不存在的ID
      const nonExistentId = new mongoose.Types.ObjectId().toString();
      
      // 执行测试
      const result = await mentalHealthService.deleteMentalHealth(nonExistentId);
      
      // 验证结果
      expect(result).toBe(false);
    });
  });
  
  describe('获取心理健康知识列表', () => {
    beforeEach(async () => {
      // 创建测试数据
      const testData = [
        {
          title: '焦虑障碍管理',
          description: '焦虑障碍的识别与管理方法',
          content: '详细内容...',
          issueType: '焦虑障碍',
          symptoms: ['担忧', '紧张', '心悸'],
          interventionMethods: ['认知行为疗法', '放松训练'],
          targetAgeGroups: ['青少年', '成人'],
          keywords: ['焦虑', '心理健康', '认知行为疗法']
        },
        {
          title: '抑郁症治疗指南',
          description: '抑郁症的识别与治疗方法',
          content: '详细内容...',
          issueType: '抑郁症',
          symptoms: ['持续低落情绪', '兴趣丧失', '疲劳'],
          interventionMethods: ['认知行为疗法', '人际关系疗法'],
          targetAgeGroups: ['青少年', '成人', '老年人'],
          keywords: ['抑郁', '心理健康', '治疗']
        },
        {
          title: '儿童注意力缺陷多动障碍',
          description: 'ADHD的识别与管理',
          content: '详细内容...',
          issueType: 'ADHD',
          symptoms: ['注意力不集中', '多动', '冲动'],
          interventionMethods: ['行为疗法', '药物治疗'],
          targetAgeGroups: ['儿童', '青少年'],
          keywords: ['ADHD', '注意力', '多动']
        }
      ];
      
      // 批量创建测试数据
      for (const data of testData) {
        await mentalHealthService.createMentalHealth(data as any);
      }
    });
    
    it('应获取所有心理健康知识条目', async () => {
      // 执行测试
      const result = await mentalHealthService.getMentalHealthList();
      
      // 验证结果
      expect(result.data).toBeDefined();
      expect(result.data.length).toBe(3);
      expect(result.total).toBe(3);
      expect(result.page).toBe(1);
      expect(result.limit).toBe(20);
      expect(result.totalPages).toBe(1);
    });
    
    it('应根据心理问题类型过滤结果', async () => {
      // 执行测试
      const result = await mentalHealthService.getMentalHealthByIssueType('焦虑障碍');
      
      // 验证结果
      expect(result.data).toBeDefined();
      expect(result.data.length).toBe(1);
      expect(result.data[0].issueType).toBe('焦虑障碍');
      expect(result.total).toBe(1);
    });
    
    it('应根据年龄组过滤结果', async () => {
      // 执行测试
      const result = await mentalHealthService.getMentalHealthByAgeGroup('儿童');
      
      // 验证结果
      expect(result.data).toBeDefined();
      expect(result.data.length).toBe(1);
      expect(result.data[0].targetAgeGroups).toContain('儿童');
      expect(result.total).toBe(1);
    });
    
    it('应根据干预方法过滤结果', async () => {
      // 执行测试
      const result = await mentalHealthService.getMentalHealthByInterventionMethod('认知行为疗法');
      
      // 验证结果
      expect(result.data).toBeDefined();
      expect(result.data.length).toBe(2);
      expect(result.data[0].interventionMethods).toContain('认知行为疗法');
      expect(result.data[1].interventionMethods).toContain('认知行为疗法');
      expect(result.total).toBe(2);
    });
    
    it('应支持关键词搜索', async () => {
      // 执行测试
      const result = await mentalHealthService.searchMentalHealth('ADHD');
      
      // 验证结果
      expect(result.data).toBeDefined();
      expect(result.data.length).toBe(1);
      expect(result.data[0].keywords).toContain('ADHD');
      expect(result.total).toBe(1);
    });
  });
});
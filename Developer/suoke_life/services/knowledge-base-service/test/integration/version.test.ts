/**
 * 版本管理功能集成测试
 */
import mongoose from 'mongoose';
import { MentalHealthService } from '../../src/services/mental-health.service';
import { VersionService } from '../../src/services/version.service';
import { KnowledgeGraphIntegrationService } from '../../src/integrations/knowledge-graph-integration.service';
import { RagIntegrationService } from '../../src/integrations/rag-integration.service';

// 模拟集成服务
jest.mock('../../src/integrations/knowledge-graph-integration.service');
jest.mock('../../src/integrations/rag-integration.service');

describe('版本管理集成测试', () => {
  let mentalHealthService: MentalHealthService;
  let versionService: VersionService;
  let documentId: string;
  
  beforeEach(async () => {
    // 重置模拟
    jest.clearAllMocks();
    
    // 创建服务实例
    mentalHealthService = new MentalHealthService();
    versionService = new VersionService();
    
    // 模拟集成服务方法
    (KnowledgeGraphIntegrationService.prototype.syncMentalHealth as jest.Mock).mockResolvedValue(undefined);
    (RagIntegrationService.prototype.syncMentalHealth as jest.Mock).mockResolvedValue(undefined);
    
    // 创建测试数据
    const testData = {
      title: '焦虑障碍管理',
      description: '焦虑障碍的识别与管理方法',
      content: '详细内容...',
      issueType: '焦虑障碍',
      symptoms: ['担忧', '紧张', '心悸'],
      interventionMethods: ['认知行为疗法', '放松训练'],
      targetAgeGroups: ['青少年', '成人'],
      keywords: ['焦虑', '心理健康', '认知行为疗法'],
      version: 1
    };
    
    const savedData = await mentalHealthService.createMentalHealth(testData as any);
    documentId = savedData._id;
  });
  
  describe('版本历史', () => {
    it('应能获取版本历史', async () => {
      // 创建初始版本
      await versionService.saveVersion(
        'mental-health',
        documentId,
        await mentalHealthService.getMentalHealth(documentId),
        1,
        'test-user-id'
      );
      
      // 更新文档创建新版本
      await mentalHealthService.updateMentalHealth(documentId, {
        title: '焦虑障碍综合管理',
        symptoms: ['担忧', '紧张', '心悸', '失眠']
      } as any);
      
      // 保存新版本
      await versionService.saveVersion(
        'mental-health',
        documentId,
        await mentalHealthService.getMentalHealth(documentId),
        2,
        'test-user-id'
      );
      
      // 执行测试
      const history = await versionService.getVersionHistory('mental-health', documentId);
      
      // 验证结果
      expect(history).toBeDefined();
      expect(history.length).toBe(3); // 当前版本 + 2个历史版本
      expect(history[0].current).toBe(true);
      expect(history[0].version).toBe(2);
    });
  });
  
  describe('获取特定版本', () => {
    it('应能获取特定版本的知识条目', async () => {
      // 保存初始版本
      await versionService.saveVersion(
        'mental-health',
        documentId,
        await mentalHealthService.getMentalHealth(documentId),
        1,
        'test-user-id'
      );
      
      // 更新文档创建新版本
      const updatedData = await mentalHealthService.updateMentalHealth(documentId, {
        title: '焦虑障碍综合管理',
        symptoms: ['担忧', '紧张', '心悸', '失眠']
      } as any);
      
      // 执行测试 - 获取版本1
      const version1 = await versionService.getSpecificVersion('mental-health', documentId, 1);
      
      // 验证结果
      expect(version1).toBeDefined();
      expect(version1.title).toBe('焦虑障碍管理');
      expect(version1.symptoms).toHaveLength(3);
      
      // 执行测试 - 获取当前版本
      const currentVersion = await versionService.getSpecificVersion('mental-health', documentId, 2);
      
      // 验证结果
      expect(currentVersion).toBeDefined();
      expect(currentVersion.title).toBe('焦虑障碍综合管理');
      expect(currentVersion.symptoms).toHaveLength(4);
      expect(currentVersion.symptoms).toContain('失眠');
    });
  });
  
  describe('版本比较', () => {
    it('应能比较两个版本的差异', async () => {
      // 保存初始版本
      await versionService.saveVersion(
        'mental-health',
        documentId,
        await mentalHealthService.getMentalHealth(documentId),
        1,
        'test-user-id'
      );
      
      // 更新文档创建新版本
      await mentalHealthService.updateMentalHealth(documentId, {
        title: '焦虑障碍综合管理',
        symptoms: ['担忧', '紧张', '心悸', '失眠']
      } as any);
      
      // 保存新版本
      await versionService.saveVersion(
        'mental-health',
        documentId,
        await mentalHealthService.getMentalHealth(documentId),
        2,
        'test-user-id'
      );
      
      // 执行测试
      const diff = await versionService.compareVersions('mental-health', documentId, 1, 2);
      
      // 验证结果
      expect(diff).toBeDefined();
      expect(diff.fromVersion).toBe(1);
      expect(diff.toVersion).toBe(2);
      expect(diff.differences).toBeDefined();
      expect(diff.differences.length).toBeGreaterThan(0);
    });
  });
  
  describe('版本回滚', () => {
    it('应能回滚到特定版本', async () => {
      // 保存初始版本
      await versionService.saveVersion(
        'mental-health',
        documentId,
        await mentalHealthService.getMentalHealth(documentId),
        1,
        'test-user-id'
      );
      
      // 更新文档创建新版本 - 版本2
      await mentalHealthService.updateMentalHealth(documentId, {
        title: '焦虑障碍综合管理',
        symptoms: ['担忧', '紧张', '心悸', '失眠']
      } as any);
      
      // 保存版本2
      await versionService.saveVersion(
        'mental-health',
        documentId,
        await mentalHealthService.getMentalHealth(documentId),
        2,
        'test-user-id'
      );
      
      // 再次更新文档 - 版本3
      await mentalHealthService.updateMentalHealth(documentId, {
        description: '焦虑障碍的识别、预防与综合管理方法',
        interventionMethods: ['认知行为疗法', '放松训练', '正念冥想']
      } as any);
      
      // 保存版本3
      await versionService.saveVersion(
        'mental-health',
        documentId,
        await mentalHealthService.getMentalHealth(documentId),
        3,
        'test-user-id'
      );
      
      // 验证当前版本是版本3
      let currentData = await mentalHealthService.getMentalHealth(documentId);
      expect(currentData!.version).toBe(3);
      expect(currentData!.title).toBe('焦虑障碍综合管理');
      expect(currentData!.description).toBe('焦虑障碍的识别、预防与综合管理方法');
      expect(currentData!.interventionMethods).toHaveLength(3);
      
      // 执行测试 - 回滚到版本1
      await versionService.rollbackToVersion('mental-health', documentId, 1, 'test-admin-id');
      
      // 验证回滚结果
      currentData = await mentalHealthService.getMentalHealth(documentId);
      expect(currentData!.version).toBe(4); // 回滚后版本号应该增加
      expect(currentData!.title).toBe('焦虑障碍管理'); // 应该回到版本1的标题
      expect(currentData!.symptoms).toHaveLength(3); // 应该回到版本1的症状数量
      expect(currentData!.interventionMethods).toHaveLength(2); // 应该回到版本1的干预方法数量
    });
  });
});
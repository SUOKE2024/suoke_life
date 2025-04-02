/**
 * 知识审核功能集成测试
 */
import mongoose from 'mongoose';
import { EnvironmentalHealthService } from '../../src/services/environmental-health.service';
import { ReviewService } from '../../src/services/review.service';
import { KnowledgeGraphIntegrationService } from '../../src/integrations/knowledge-graph-integration.service';
import { RagIntegrationService } from '../../src/integrations/rag-integration.service';

// 模拟集成服务
jest.mock('../../src/integrations/knowledge-graph-integration.service');
jest.mock('../../src/integrations/rag-integration.service');

describe('知识审核集成测试', () => {
  let environmentalHealthService: EnvironmentalHealthService;
  let reviewService: ReviewService;
  let documentId: string;
  
  beforeEach(async () => {
    // 重置模拟
    jest.clearAllMocks();
    
    // 创建服务实例
    environmentalHealthService = new EnvironmentalHealthService();
    reviewService = new ReviewService();
    
    // 模拟集成服务方法
    (KnowledgeGraphIntegrationService.prototype.syncEnvironmentalHealth as jest.Mock).mockResolvedValue(undefined);
    (RagIntegrationService.prototype.syncEnvironmentalHealth as jest.Mock).mockResolvedValue(undefined);
    
    // 创建测试数据
    const testData = {
      title: '空气污染与健康',
      description: '空气污染对人体健康的影响',
      content: '详细内容...',
      environmentType: '空气',
      pollutantType: ['PM2.5', '臭氧'],
      healthImpacts: ['呼吸系统疾病', '心血管疾病'],
      riskLevel: 4,
      vulnerableGroups: ['老人', '儿童', '孕妇'],
      keywords: ['空气污染', '健康', 'PM2.5'],
      version: 1
    };
    
    const savedData = await environmentalHealthService.createEnvironmentalHealth(testData as any);
    documentId = savedData._id;
  });
  
  describe('提交审核', () => {
    it('应能成功提交审核请求', async () => {
      // 执行测试
      const review = await reviewService.submitForReview(
        'environmental-health',
        documentId,
        'test-user-id',
        '请检查并更新PM2.5的健康影响信息'
      );
      
      // 验证结果
      expect(review).toBeDefined();
      expect(review.knowledgeType).toBe('environmental-health');
      expect(review.documentId).toBe(documentId);
      expect(review.status).toBe('pending');
      expect(review.submittedBy).toBe('test-user-id');
      expect(review.submitterComments).toBe('请检查并更新PM2.5的健康影响信息');
      expect(review.content).toBeDefined();
    });
    
    it('对同一文档的重复提交应该失败', async () => {
      // 首次提交
      await reviewService.submitForReview(
        'environmental-health',
        documentId,
        'test-user-id',
        '请检查内容'
      );
      
      // 重复提交应该失败
      await expect(
        reviewService.submitForReview(
          'environmental-health',
          documentId,
          'test-user-id',
          '再次请求审核'
        )
      ).rejects.toThrow('该知识条目已有待审核的记录');
    });
  });
  
  describe('获取审核记录', () => {
    it('应能获取待审核记录列表', async () => {
      // 提交多个审核请求
      await reviewService.submitForReview(
        'environmental-health',
        documentId,
        'test-user-id',
        '请检查内容'
      );
      
      // 创建另一个测试数据
      const testData2 = {
        title: '水污染与健康',
        description: '水污染对人体健康的影响',
        content: '详细内容...',
        environmentType: '水',
        pollutantType: ['重金属', '有机物'],
        healthImpacts: ['消化系统疾病', '皮肤病'],
        riskLevel: 3,
        vulnerableGroups: ['儿童', '孕妇'],
        keywords: ['水污染', '健康', '重金属'],
        version: 1
      };
      
      const savedData2 = await environmentalHealthService.createEnvironmentalHealth(testData2 as any);
      
      await reviewService.submitForReview(
        'environmental-health',
        savedData2._id,
        'another-user-id',
        '请审核这个新条目'
      );
      
      // 执行测试
      const result = await reviewService.getReviews({ status: 'pending' });
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.data).toHaveLength(2);
      expect(result.total).toBe(2);
      expect(result.data[0].status).toBe('pending');
      expect(result.data[1].status).toBe('pending');
    });
    
    it('应能获取知识条目的审核历史', async () => {
      // 提交审核
      const review = await reviewService.submitForReview(
        'environmental-health',
        documentId,
        'test-user-id',
        '请检查内容'
      );
      
      // 审核通过
      await reviewService.approveReview(
        review._id,
        'test-admin-id',
        '内容已检查，符合标准'
      );
      
      // 再次提交审核
      const review2 = await reviewService.submitForReview(
        'environmental-health',
        documentId,
        'test-user-id',
        '请检查更新后的内容'
      );
      
      // 拒绝审核
      await reviewService.rejectReview(
        review2._id,
        'test-admin-id',
        '内容需要更多详细说明'
      );
      
      // 执行测试
      const history = await reviewService.getReviewHistory('environmental-health', documentId);
      
      // 验证结果
      expect(history).toBeDefined();
      expect(history).toHaveLength(2);
      expect(history[0].status).toBe('rejected');
      expect(history[1].status).toBe('approved');
    });
  });
  
  describe('审核流程', () => {
    it('应能通过审核', async () => {
      // 提交审核
      const review = await reviewService.submitForReview(
        'environmental-health',
        documentId,
        'test-user-id',
        '请检查内容'
      );
      
      // 执行测试
      const result = await reviewService.approveReview(
        review._id,
        'test-admin-id',
        '内容已检查，符合标准'
      );
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.status).toBe('approved');
      expect(result.reviewedBy).toBe('test-admin-id');
      expect(result.reviewerComments).toBe('内容已检查，符合标准');
      expect(result.reviewedAt).toBeDefined();
    });
    
    it('应能拒绝审核', async () => {
      // 提交审核
      const review = await reviewService.submitForReview(
        'environmental-health',
        documentId,
        'test-user-id',
        '请检查内容'
      );
      
      // 执行测试
      const result = await reviewService.rejectReview(
        review._id,
        'test-admin-id',
        '内容需要更多详细说明和参考文献'
      );
      
      // 验证结果
      expect(result).toBeDefined();
      expect(result.status).toBe('rejected');
      expect(result.reviewedBy).toBe('test-admin-id');
      expect(result.reviewerComments).toBe('内容需要更多详细说明和参考文献');
      expect(result.reviewedAt).toBeDefined();
    });
    
    it('拒绝审核时必须提供理由', async () => {
      // 提交审核
      const review = await reviewService.submitForReview(
        'environmental-health',
        documentId,
        'test-user-id',
        '请检查内容'
      );
      
      // 执行测试 - 没有提供理由应该失败
      await expect(
        reviewService.rejectReview(
          review._id,
          'test-admin-id',
          ''
        )
      ).rejects.toThrow('拒绝审核必须提供理由');
    });
    
    it('已处理的审核不能再次处理', async () => {
      // 提交审核
      const review = await reviewService.submitForReview(
        'environmental-health',
        documentId,
        'test-user-id',
        '请检查内容'
      );
      
      // 通过审核
      await reviewService.approveReview(
        review._id,
        'test-admin-id',
        '内容已检查，符合标准'
      );
      
      // 尝试再次处理同一审核应该失败
      await expect(
        reviewService.rejectReview(
          review._id,
          'another-admin-id',
          '内容存在问题'
        )
      ).rejects.toThrow('该审核记录已处理');
    });
  });
});
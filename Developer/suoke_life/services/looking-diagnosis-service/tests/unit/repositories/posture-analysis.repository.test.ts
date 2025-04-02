import mongoose from 'mongoose';
import { PostureAnalysisRepository } from '../../../src/repositories/posture-analysis.repository';
import PostureDiagnosisModel, { PostureDiagnosis } from '../../../src/models/diagnosis/posture.model';

/**
 * 体态分析存储库单元测试
 */
describe('PostureAnalysisRepository', () => {
  let repository: PostureAnalysisRepository;
  
  beforeAll(async () => {
    // 连接到测试数据库
    const mongoUri = process.env.MONGODB_URI_TEST || 'mongodb://localhost:27017/looking_diagnosis_test';
    await mongoose.connect(mongoUri);
  });
  
  afterAll(async () => {
    // 清空测试数据
    await PostureDiagnosisModel.deleteMany({});
    
    // 关闭数据库连接
    await mongoose.connection.close();
  });
  
  beforeEach(async () => {
    // 重置数据
    await PostureDiagnosisModel.deleteMany({});
    
    // 创建新的存储库实例
    repository = new PostureAnalysisRepository();
  });
  
  describe('savePostureDiagnosis', () => {
    it('应该保存体态诊断数据', async () => {
      const diagnosisData: Partial<PostureDiagnosis> = {
        diagnosisId: 'test-diagnosis-id',
        sessionId: 'test-session-id',
        userId: 'test-user-id',
        features: {
          overallPosture: '正常',
          shoulderAlignment: '对称',
          spineAlignment: '正常',
          hipAlignment: '对称',
          hasForwardHeadPosture: false,
          hasRoundedShoulders: false,
          hasSwaybBack: false,
          hasFlatBack: false,
          posturalDeviation: 0,
          comments: '测试描述'
        }
      };
      
      const savedDiagnosis = await repository.savePostureDiagnosis(diagnosisData);
      
      expect(savedDiagnosis).toBeDefined();
      expect(savedDiagnosis.diagnosisId).toBe('test-diagnosis-id');
      expect(savedDiagnosis.sessionId).toBe('test-session-id');
      expect(savedDiagnosis.userId).toBe('test-user-id');
      expect(savedDiagnosis.features.overallPosture).toBe('正常');
    });
    
    it('如果未提供diagnosisId应自动生成', async () => {
      const diagnosisData: Partial<PostureDiagnosis> = {
        sessionId: 'test-session',
        features: {
          overallPosture: '正常',
          shoulderAlignment: '对称',
          spineAlignment: '正常',
          hipAlignment: '对称',
          hasForwardHeadPosture: false,
          hasRoundedShoulders: false,
          hasSwaybBack: false,
          hasFlatBack: false,
          posturalDeviation: 0,
          comments: '测试描述'
        }
      };
      
      const savedDiagnosis = await repository.savePostureDiagnosis(diagnosisData);
      
      expect(savedDiagnosis.diagnosisId).toBeDefined();
      expect(savedDiagnosis.diagnosisId).toMatch(/^ld-posture-/);
    });
    
    it('应该抛出数据验证错误', async () => {
      // 缺少必需字段
      const invalidData: Partial<PostureDiagnosis> = {
        diagnosisId: 'test-id',
        // 缺少sessionId
      };
      
      await expect(
        repository.savePostureDiagnosis(invalidData)
      ).rejects.toThrow();
    });
  });
  
  describe('getPostureDiagnosisById', () => {
    it('应该通过ID检索诊断记录', async () => {
      // 先创建记录
      const diagnosisData: Partial<PostureDiagnosis> = {
        diagnosisId: 'test-retrieval-id',
        sessionId: 'test-session',
        features: {
          overallPosture: '正常',
          shoulderAlignment: '对称',
          spineAlignment: '正常',
          hipAlignment: '对称',
          hasForwardHeadPosture: false,
          hasRoundedShoulders: false,
          hasSwaybBack: false,
          hasFlatBack: false,
          posturalDeviation: 0,
          comments: '测试描述'
        }
      };
      
      await repository.savePostureDiagnosis(diagnosisData);
      
      // 然后检索
      const retrievedDiagnosis = await repository.getPostureDiagnosisById('test-retrieval-id');
      
      expect(retrievedDiagnosis).not.toBeNull();
      expect(retrievedDiagnosis?.diagnosisId).toBe('test-retrieval-id');
      expect(retrievedDiagnosis?.sessionId).toBe('test-session');
    });
    
    it('应该为不存在的ID返回null', async () => {
      const result = await repository.getPostureDiagnosisById('non-existent-id');
      expect(result).toBeNull();
    });
  });
  
  describe('getPostureDiagnosisByUserId', () => {
    it('应该检索用户的所有诊断记录', async () => {
      // 创建多条记录
      const userId = 'user-with-multiple-records';
      
      await Promise.all([
        repository.savePostureDiagnosis({
          diagnosisId: 'user-test-1',
          sessionId: 'session-1',
          userId,
          features: {
            overallPosture: '正常',
            shoulderAlignment: '对称',
            spineAlignment: '正常',
            hipAlignment: '对称',
            hasForwardHeadPosture: false,
            hasRoundedShoulders: false,
            hasSwaybBack: false,
            hasFlatBack: false,
            posturalDeviation: 0,
            comments: '记录1'
          }
        }),
        repository.savePostureDiagnosis({
          diagnosisId: 'user-test-2',
          sessionId: 'session-2',
          userId,
          features: {
            overallPosture: '前倾',
            shoulderAlignment: '左高',
            spineAlignment: '正常',
            hipAlignment: '对称',
            hasForwardHeadPosture: true,
            hasRoundedShoulders: false,
            hasSwaybBack: false,
            hasFlatBack: false,
            posturalDeviation: 2,
            comments: '记录2'
          }
        })
      ]);
      
      // 检索用户记录
      const userRecords = await repository.getPostureDiagnosisByUserId(userId);
      
      expect(userRecords).toHaveLength(2);
      expect(userRecords[0].userId).toBe(userId);
      expect(userRecords[1].userId).toBe(userId);
      
      // 检查排序 (按时间倒序)
      expect(new Date(userRecords[0].createdAt).getTime())
        .toBeGreaterThanOrEqual(new Date(userRecords[1].createdAt).getTime());
    });
    
    it('应该支持分页', async () => {
      // 创建5条记录
      const userId = 'user-pagination-test';
      
      for (let i = 0; i < 5; i++) {
        await repository.savePostureDiagnosis({
          diagnosisId: `page-test-${i}`,
          sessionId: `session-${i}`,
          userId,
          features: {
            overallPosture: '正常',
            shoulderAlignment: '对称',
            spineAlignment: '正常',
            hipAlignment: '对称',
            hasForwardHeadPosture: false,
            hasRoundedShoulders: false,
            hasSwaybBack: false,
            hasFlatBack: false,
            posturalDeviation: 0,
            comments: `记录${i}`
          }
        });
      }
      
      // 检索第一页 (限制2条)
      const page1 = await repository.getPostureDiagnosisByUserId(userId, 2, 0);
      expect(page1).toHaveLength(2);
      
      // 检索第二页
      const page2 = await repository.getPostureDiagnosisByUserId(userId, 2, 2);
      expect(page2).toHaveLength(2);
      
      // 检索第三页
      const page3 = await repository.getPostureDiagnosisByUserId(userId, 2, 4);
      expect(page3).toHaveLength(1);
      
      // 验证页面内容不同
      expect(page1[0].diagnosisId).not.toBe(page2[0].diagnosisId);
    });
    
    it('应该对不存在的用户返回空数组', async () => {
      const result = await repository.getPostureDiagnosisByUserId('non-existent-user');
      expect(result).toEqual([]);
    });
  });
  
  describe('getPostureDiagnosisBySessionId', () => {
    it('应该检索会话的所有诊断记录', async () => {
      // 创建多条记录
      const sessionId = 'session-with-multiple-records';
      
      await Promise.all([
        repository.savePostureDiagnosis({
          diagnosisId: 'session-test-1',
          sessionId,
          userId: 'user-1',
          features: {
            overallPosture: '正常',
            shoulderAlignment: '对称',
            spineAlignment: '正常',
            hipAlignment: '对称',
            hasForwardHeadPosture: false,
            hasRoundedShoulders: false,
            hasSwaybBack: false,
            hasFlatBack: false,
            posturalDeviation: 0,
            comments: '会话记录1'
          }
        }),
        repository.savePostureDiagnosis({
          diagnosisId: 'session-test-2',
          sessionId,
          userId: 'user-2',
          features: {
            overallPosture: '前倾',
            shoulderAlignment: '左高',
            spineAlignment: '正常',
            hipAlignment: '对称',
            hasForwardHeadPosture: true,
            hasRoundedShoulders: false,
            hasSwaybBack: false,
            hasFlatBack: false,
            posturalDeviation: 2,
            comments: '会话记录2'
          }
        })
      ]);
      
      // 检索会话记录
      const sessionRecords = await repository.getPostureDiagnosisBySessionId(sessionId);
      
      expect(sessionRecords).toHaveLength(2);
      expect(sessionRecords[0].sessionId).toBe(sessionId);
      expect(sessionRecords[1].sessionId).toBe(sessionId);
    });
  });
  
  describe('updatePostureDiagnosis', () => {
    it('应该更新现有诊断记录', async () => {
      // 先创建记录
      const initialData: Partial<PostureDiagnosis> = {
        diagnosisId: 'update-test-id',
        sessionId: 'update-test-session',
        features: {
          overallPosture: '正常',
          shoulderAlignment: '对称',
          spineAlignment: '正常',
          hipAlignment: '对称',
          hasForwardHeadPosture: false,
          hasRoundedShoulders: false,
          hasSwaybBack: false,
          hasFlatBack: false,
          posturalDeviation: 0,
          comments: '更新前'
        }
      };
      
      await repository.savePostureDiagnosis(initialData);
      
      // 然后更新
      const updateData: Partial<PostureDiagnosis> = {
        features: {
          overallPosture: '前倾',
          shoulderAlignment: '左高',
          spineAlignment: '正常',
          hipAlignment: '对称',
          hasForwardHeadPosture: true,
          hasRoundedShoulders: false,
          hasSwaybBack: false,
          hasFlatBack: false,
          posturalDeviation: 2,
          comments: '更新后'
        },
        recommendations: ['新建议1', '新建议2']
      };
      
      const updatedDiagnosis = await repository.updatePostureDiagnosis('update-test-id', updateData);
      
      expect(updatedDiagnosis).not.toBeNull();
      expect(updatedDiagnosis?.features.overallPosture).toBe('前倾');
      expect(updatedDiagnosis?.features.comments).toBe('更新后');
      expect(updatedDiagnosis?.recommendations).toEqual(['新建议1', '新建议2']);
      
      // 验证数据库更新
      const retrievedDiagnosis = await repository.getPostureDiagnosisById('update-test-id');
      expect(retrievedDiagnosis?.features.overallPosture).toBe('前倾');
    });
    
    it('更新不存在的ID应返回null', async () => {
      const result = await repository.updatePostureDiagnosis('non-existent-id', {
        features: { comments: '不会更新' }
      } as any);
      
      expect(result).toBeNull();
    });
  });
  
  describe('deletePostureDiagnosis', () => {
    it('应该删除诊断记录', async () => {
      // 先创建记录
      await repository.savePostureDiagnosis({
        diagnosisId: 'delete-test-id',
        sessionId: 'delete-test-session',
        features: {
          overallPosture: '正常',
          shoulderAlignment: '对称',
          spineAlignment: '正常',
          hipAlignment: '对称',
          hasForwardHeadPosture: false,
          hasRoundedShoulders: false,
          hasSwaybBack: false,
          hasFlatBack: false,
          posturalDeviation: 0,
          comments: '将被删除'
        }
      });
      
      // 然后删除
      const deleteResult = await repository.deletePostureDiagnosis('delete-test-id');
      
      expect(deleteResult).toBe(true);
      
      // 验证记录已删除
      const retrievedDiagnosis = await repository.getPostureDiagnosisById('delete-test-id');
      expect(retrievedDiagnosis).toBeNull();
    });
    
    it('删除不存在的ID应返回false', async () => {
      const result = await repository.deletePostureDiagnosis('non-existent-id');
      expect(result).toBe(false);
    });
  });
});
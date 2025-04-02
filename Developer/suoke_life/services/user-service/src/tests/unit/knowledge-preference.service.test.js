/**
 * 知识偏好服务单元测试
 */
const { describe, it, beforeEach, afterEach, expect, jest } = require('@jest/globals');
const knowledgePreferenceService = require('../../services/knowledge-preference.service');
const knowledgePreferenceRepository = require('../../repositories/knowledge-preference.repository');

// 模拟依赖
jest.mock('../../repositories/knowledge-preference.repository');
jest.mock('../../utils/logger');

describe('知识偏好服务测试', () => {
  beforeEach(() => {
    // 重置所有模拟
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('getUserKnowledgePreferences', () => {
    it('应该返回用户的知识偏好', async () => {
      // 准备
      const userId = '12345';
      const mockPreferences = {
        domains: ['中医药', '营养健康'],
        contentTypes: ['文章', '视频'],
        difficultyLevel: '中级'
      };
      
      knowledgePreferenceRepository.getUserPreferences.mockResolvedValue(mockPreferences);
      
      // 执行
      const result = await knowledgePreferenceService.getUserKnowledgePreferences(userId);
      
      // 验证
      expect(knowledgePreferenceRepository.getUserPreferences).toHaveBeenCalledWith(userId);
      expect(result).toEqual(mockPreferences);
    });

    it('当用户不存在偏好时应返回默认偏好', async () => {
      // 准备
      const userId = 'non-existent-user';
      
      knowledgePreferenceRepository.getUserPreferences.mockResolvedValue(null);
      
      // 执行
      const result = await knowledgePreferenceService.getUserKnowledgePreferences(userId);
      
      // 验证
      expect(knowledgePreferenceRepository.getUserPreferences).toHaveBeenCalledWith(userId);
      expect(result).toHaveProperty('domains');
      expect(result).toHaveProperty('contentTypes');
      expect(result).toHaveProperty('difficultyLevel');
    });

    it('应该处理存储库错误', async () => {
      // 准备
      const userId = '12345';
      const mockError = new Error('数据库错误');
      
      knowledgePreferenceRepository.getUserPreferences.mockRejectedValue(mockError);
      
      // 执行和验证
      await expect(knowledgePreferenceService.getUserKnowledgePreferences(userId))
        .rejects.toThrow('获取用户知识偏好失败');
    });
  });

  describe('updateUserKnowledgePreferences', () => {
    it('应该更新用户的知识偏好', async () => {
      // 准备
      const userId = '12345';
      const preferences = {
        domains: ['精准医疗', '养生保健'],
        contentTypes: ['图解', '视频'],
        difficultyLevel: '高级'
      };
      
      knowledgePreferenceRepository.updateUserPreferences.mockResolvedValue(true);
      
      // 执行
      const result = await knowledgePreferenceService.updateUserKnowledgePreferences(userId, preferences);
      
      // 验证
      expect(knowledgePreferenceRepository.updateUserPreferences).toHaveBeenCalledWith(userId, preferences);
      expect(result).toBe(true);
    });

    it('应该验证更新的偏好数据', async () => {
      // 准备
      const userId = '12345';
      const invalidPreferences = {
        domains: ['非法领域'],
        contentTypes: [],
        difficultyLevel: '超高级' // 不支持的难度级别
      };
      
      // 执行和验证
      await expect(knowledgePreferenceService.updateUserKnowledgePreferences(userId, invalidPreferences))
        .rejects.toThrow('知识偏好数据无效');
    });
  });

  describe('recordContentView', () => {
    it('应该记录用户内容查看', async () => {
      // 准备
      const userId = '12345';
      const contentId = 'content-123';
      const contentType = '文章';
      const viewData = { contentId, contentType };
      
      knowledgePreferenceRepository.recordContentView.mockResolvedValue(true);
      
      // 执行
      const result = await knowledgePreferenceService.recordContentView(userId, viewData);
      
      // 验证
      expect(knowledgePreferenceRepository.recordContentView).toHaveBeenCalledWith(userId, viewData);
      expect(result).toBe(true);
    });

    it('应该验证查看记录数据', async () => {
      // 准备
      const userId = '12345';
      const invalidViewData = { contentType: '文章' }; // 缺少contentId
      
      // 执行和验证
      await expect(knowledgePreferenceService.recordContentView(userId, invalidViewData))
        .rejects.toThrow('内容查看数据无效');
    });
  });

  describe('getUserContentViewHistory', () => {
    it('应该返回用户内容查看历史', async () => {
      // 准备
      const userId = '12345';
      const limit = 10;
      const offset = 0;
      const mockHistory = [
        { contentId: 'content-1', contentType: '文章', viewedAt: new Date() },
        { contentId: 'content-2', contentType: '视频', viewedAt: new Date() }
      ];
      
      knowledgePreferenceRepository.getUserContentViewHistory.mockResolvedValue(mockHistory);
      
      // 执行
      const result = await knowledgePreferenceService.getUserContentViewHistory(userId, limit, offset);
      
      // 验证
      expect(knowledgePreferenceRepository.getUserContentViewHistory).toHaveBeenCalledWith(userId, limit, offset);
      expect(result).toEqual(mockHistory);
    });
  });

  describe('toggleFavoriteContent', () => {
    it('应该添加内容到收藏', async () => {
      // 准备
      const userId = '12345';
      const contentId = 'content-123';
      const contentType = '文章';
      const favoriteData = { contentId, contentType };
      
      knowledgePreferenceRepository.checkFavoriteExists.mockResolvedValue(false);
      knowledgePreferenceRepository.addFavoriteContent.mockResolvedValue(true);
      
      // 执行
      const result = await knowledgePreferenceService.toggleFavoriteContent(userId, favoriteData);
      
      // 验证
      expect(knowledgePreferenceRepository.checkFavoriteExists).toHaveBeenCalledWith(userId, contentId);
      expect(knowledgePreferenceRepository.addFavoriteContent).toHaveBeenCalledWith(userId, favoriteData);
      expect(result).toEqual({ added: true, removed: false });
    });

    it('应该从收藏中移除内容', async () => {
      // 准备
      const userId = '12345';
      const contentId = 'content-123';
      const contentType = '文章';
      const favoriteData = { contentId, contentType };
      
      knowledgePreferenceRepository.checkFavoriteExists.mockResolvedValue(true);
      knowledgePreferenceRepository.removeFavoriteContent.mockResolvedValue(true);
      
      // 执行
      const result = await knowledgePreferenceService.toggleFavoriteContent(userId, favoriteData);
      
      // 验证
      expect(knowledgePreferenceRepository.checkFavoriteExists).toHaveBeenCalledWith(userId, contentId);
      expect(knowledgePreferenceRepository.removeFavoriteContent).toHaveBeenCalledWith(userId, contentId);
      expect(result).toEqual({ added: false, removed: true });
    });
  });

  describe('getUserFavorites', () => {
    it('应该返回用户收藏内容', async () => {
      // 准备
      const userId = '12345';
      const limit = 10;
      const offset = 0;
      const mockFavorites = [
        { contentId: 'content-1', contentType: '文章', addedAt: new Date() },
        { contentId: 'content-2', contentType: '视频', addedAt: new Date() }
      ];
      
      knowledgePreferenceRepository.getUserFavorites.mockResolvedValue(mockFavorites);
      
      // 执行
      const result = await knowledgePreferenceService.getUserFavorites(userId, limit, offset);
      
      // 验证
      expect(knowledgePreferenceRepository.getUserFavorites).toHaveBeenCalledWith(userId, limit, offset);
      expect(result).toEqual(mockFavorites);
    });
  });

  describe('recordKnowledgeGraphInteraction', () => {
    it('应该记录知识图谱交互', async () => {
      // 准备
      const userId = '12345';
      const interactionData = {
        nodeId: 'node-123',
        nodeType: '中医术语',
        interactionType: '查询',
        details: '查询了"阴虚"的详细信息'
      };
      
      knowledgePreferenceRepository.recordKnowledgeGraphInteraction.mockResolvedValue(true);
      
      // 执行
      const result = await knowledgePreferenceService.recordKnowledgeGraphInteraction(userId, interactionData);
      
      // 验证
      expect(knowledgePreferenceRepository.recordKnowledgeGraphInteraction).toHaveBeenCalledWith(userId, interactionData);
      expect(result).toBe(true);
    });

    it('应该验证交互数据', async () => {
      // 准备
      const userId = '12345';
      const invalidInteractionData = {
        nodeType: '中医术语',
        interactionType: '查询'
        // 缺少nodeId
      };
      
      // 执行和验证
      await expect(knowledgePreferenceService.recordKnowledgeGraphInteraction(userId, invalidInteractionData))
        .rejects.toThrow('知识图谱交互数据无效');
    });
  });

  describe('getUserKnowledgeGraphInteractions', () => {
    it('应该返回用户知识图谱交互历史', async () => {
      // 准备
      const userId = '12345';
      const limit = 10;
      const offset = 0;
      const mockInteractions = [
        { 
          nodeId: 'node-1', 
          nodeType: '中医术语', 
          interactionType: '查询',
          interactedAt: new Date()
        },
        { 
          nodeId: 'node-2', 
          nodeType: '食疗方案', 
          interactionType: '收藏',
          interactedAt: new Date()
        }
      ];
      
      knowledgePreferenceRepository.getUserKnowledgeGraphInteractions.mockResolvedValue(mockInteractions);
      
      // 执行
      const result = await knowledgePreferenceService.getUserKnowledgeGraphInteractions(userId, limit, offset);
      
      // 验证
      expect(knowledgePreferenceRepository.getUserKnowledgeGraphInteractions).toHaveBeenCalledWith(userId, limit, offset);
      expect(result).toEqual(mockInteractions);
    });
  });
});
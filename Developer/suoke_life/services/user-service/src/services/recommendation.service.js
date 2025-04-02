/**
 * 知识内容推荐服务
 * 基于用户历史交互和偏好实现智能推荐
 */
const axios = require('axios');
const config = require('../config');
const { knowledgePreferenceRepository, recommendationRepository } = require('../repositories');
const logger = require('../utils/logger');
const cacheService = require('../utils/cache');
const { shuffleArray, calculateContentScore } = require('../utils/algorithm');

/**
 * 知识内容推荐服务
 */
const recommendationService = {
  /**
   * 获取用户推荐内容
   * @param {string} userId - 用户ID
   * @param {Object} options - 推荐选项
   * @param {number} options.limit - 返回结果数量
   * @param {boolean} options.includeHistory - 是否包含历史内容
   * @param {string[]} options.domainFilter - 领域过滤器
   * @param {string[]} options.typeFilter - 内容类型过滤器
   * @returns {Promise<Array>} 推荐内容列表
   */
  async getRecommendedContent(userId, options = {}) {
    try {
      const {
        limit = 10,
        includeHistory = false,
        domainFilter = [],
        typeFilter = []
      } = options;

      // 1. 获取用户偏好
      const userPreferences = await knowledgePreferenceRepository.getUserPreferences(userId);
      
      // 2. 获取用户查看历史
      const viewHistory = await knowledgePreferenceRepository.getUserContentViewHistory(userId, 100, 0);
      
      // 3. 获取用户收藏
      const favorites = await knowledgePreferenceRepository.getUserFavorites(userId, 100, 0);
      
      // 4. 获取知识图谱交互
      const graphInteractions = await knowledgePreferenceRepository.getUserKnowledgeGraphInteractions(userId, 100, 0);
      
      // 5. 从知识库服务获取候选内容
      const candidateContent = await this._fetchCandidateContent(
        userPreferences,
        domainFilter,
        typeFilter,
        limit * 3
      );
      
      // 6. 过滤已查看内容（如果不包含历史）
      let filteredContent = candidateContent;
      if (!includeHistory) {
        const viewedIds = viewHistory.map(item => item.contentId);
        filteredContent = candidateContent.filter(content => !viewedIds.includes(content.id));
      }
      
      // 7. 使用算法对内容评分并排序
      const scoredContent = filteredContent.map(content => {
        const score = this._calculateContentScore(
          content,
          userPreferences,
          viewHistory,
          favorites,
          graphInteractions
        );
        return { ...content, score };
      }).sort((a, b) => b.score - a.score);
      
      // 8. 加入一些随机性，避免推荐过于单一
      const topRankedContent = scoredContent.slice(0, Math.ceil(limit * 1.5));
      const shuffledTopContent = shuffleArray(topRankedContent);
      
      // 9. 返回最终推荐结果
      return shuffledTopContent.slice(0, limit);
    } catch (error) {
      logger.error('获取推荐内容失败:', error);
      throw new Error('获取推荐内容失败');
    }
  },
  
  /**
   * 基于LLM的个性化内容推荐
   * @param {string} userId - 用户ID
   * @param {Object} options - 推荐选项
   * @returns {Promise<Array>} 推荐内容列表
   */
  async getLLMRecommendedContent(userId, options = {}) {
    try {
      const { limit = 5 } = options;
      
      // 1. 获取用户偏好和交互历史
      const userPreferences = await knowledgePreferenceRepository.getUserPreferences(userId);
      const viewHistory = await knowledgePreferenceRepository.getUserContentViewHistory(userId, 20, 0);
      const favorites = await knowledgePreferenceRepository.getUserFavorites(userId, 20, 0);
      
      // 2. 构建用户兴趣概要
      const userInterestSummary = this._buildUserInterestSummary(userPreferences, viewHistory, favorites);
      
      // 3. 调用OpenAI服务
      const openaiResponse = await axios.post(`${config.openaiService.url}/api/recommendations`, {
        userInterestSummary,
        limit
      }, {
        headers: {
          'Authorization': `Bearer ${config.openaiService.apiKey}`,
          'Content-Type': 'application/json'
        }
      });
      
      // 4. 从知识库获取推荐的内容详情
      const recommendedContentIds = openaiResponse.data.recommendations.map(rec => rec.contentId);
      const contentDetails = await this._fetchContentDetails(recommendedContentIds);
      
      // 5. 合并AI推荐原因和内容详情
      return openaiResponse.data.recommendations.map(rec => {
        const contentDetail = contentDetails.find(c => c.id === rec.contentId);
        return {
          ...contentDetail,
          recommendationReason: rec.reason
        };
      });
    } catch (error) {
      logger.error('获取LLM推荐内容失败:', error);
      // 如果LLM推荐失败，回退到基础推荐
      return this.getRecommendedContent(userId, options);
    }
  },
  
  /**
   * 记录推荐反馈
   * @param {string} userId - 用户ID
   * @param {string} contentId - 内容ID
   * @param {string} feedbackType - 反馈类型 (clicked, liked, disliked, ignored)
   * @returns {Promise<boolean>} 操作结果
   */
  async recordRecommendationFeedback(userId, contentId, feedbackType) {
    try {
      return await recommendationRepository.recordRecommendationFeedback(
        userId,
        contentId,
        feedbackType
      );
    } catch (error) {
      logger.error('记录推荐反馈失败:', error);
      throw new Error('记录推荐反馈失败');
    }
  },
  
  /**
   * 从知识库服务获取候选内容
   * @private
   */
  async _fetchCandidateContent(userPreferences, domainFilter, typeFilter, limit) {
    try {
      // 构建缓存键
      const domains = domainFilter.length > 0 ? domainFilter : userPreferences.domains;
      const types = typeFilter.length > 0 ? typeFilter : userPreferences.contentTypes;
      const cacheKey = `content:${domains.join(',')}-${types.join(',')}-${userPreferences.difficultyLevel}-${limit}`;
      
      // 尝试从缓存获取
      const cachedContent = await cacheService.get(cacheKey);
      if (cachedContent) {
        logger.info(`从缓存中返回候选内容: ${cacheKey}`);
        return cachedContent;
      }
      
      // 从知识库服务获取
      const response = await axios.get(`${config.knowledgeBaseUrl}/api/content`, {
        params: {
          domains,
          types,
          difficulty: userPreferences.difficultyLevel,
          limit
        }
      });
      
      // 存入缓存，有效期10分钟
      if (response.data && response.data.length > 0) {
        await cacheService.set(cacheKey, response.data, 600);
      }
      
      return response.data;
    } catch (error) {
      logger.error('获取候选内容失败:', error);
      return [];
    }
  },
  
  /**
   * 获取内容详情
   * @private
   */
  async _fetchContentDetails(contentIds) {
    try {
      // 构建缓存键 - 内容ID数组排序后连接为字符串
      const sortedIds = [...contentIds].sort();
      const cacheKey = `content-details:${sortedIds.join(',')}`;
      
      // 尝试从缓存获取
      const cachedDetails = await cacheService.get(cacheKey);
      if (cachedDetails) {
        logger.info(`从缓存中返回内容详情: ${cacheKey}`);
        return cachedDetails;
      }
      
      // 从知识库服务获取
      const response = await axios.post(`${config.knowledgeBaseUrl}/api/content/details`, {
        contentIds
      });
      
      // 存入缓存，有效期30分钟
      if (response.data && response.data.length > 0) {
        await cacheService.set(cacheKey, response.data, 1800);
      }
      
      return response.data;
    } catch (error) {
      logger.error('获取内容详情失败:', error);
      return [];
    }
  },
  
  /**
   * 计算内容得分
   * @private
   */
  _calculateContentScore(content, userPreferences, viewHistory, favorites, graphInteractions) {
    // 基础分数
    let score = 50;
    
    // 领域匹配加分
    if (userPreferences.domains.includes(content.domain)) {
      score += 15;
    }
    
    // 内容类型匹配加分
    if (userPreferences.contentTypes.includes(content.type)) {
      score += 10;
    }
    
    // 难度级别匹配加分
    if (content.difficultyLevel === userPreferences.difficultyLevel) {
      score += 10;
    }
    
    // 已查看内容领域相似加分
    const viewedDomains = viewHistory.map(item => item.domain);
    if (viewedDomains.includes(content.domain)) {
      score += 5;
    }
    
    // 收藏内容相似加分
    const favoriteDomains = favorites.map(item => item.domain);
    if (favoriteDomains.includes(content.domain)) {
      score += 8;
    }
    
    // 知识图谱交互相关性加分
    const interactedNodes = graphInteractions.map(item => item.nodeId);
    if (content.relatedNodes && content.relatedNodes.some(node => interactedNodes.includes(node))) {
      score += 12;
    }
    
    // 最近更新内容加分（鼓励新内容）
    const contentAge = (new Date() - new Date(content.updatedAt)) / (1000 * 60 * 60 * 24); // 天数
    if (contentAge < 7) { // 一周内
      score += 8;
    }
    
    // 热门内容加分
    if (content.viewCount > 1000) {
      score += 5;
    }
    
    return score;
  },
  
  /**
   * 构建用户兴趣概要（用于LLM推荐）
   * @private
   */
  _buildUserInterestSummary(userPreferences, viewHistory, favorites) {
    // 获取最近查看的内容
    const recentViews = viewHistory.slice(0, 5).map(v => ({
      title: v.title,
      domain: v.domain,
      type: v.contentType
    }));
    
    // 获取收藏内容
    const userFavorites = favorites.slice(0, 5).map(f => ({
      title: f.title,
      domain: f.domain,
      type: f.contentType
    }));
    
    return {
      preferredDomains: userPreferences.domains,
      preferredContentTypes: userPreferences.contentTypes,
      difficultyLevel: userPreferences.difficultyLevel,
      recentViews,
      favorites: userFavorites
    };
  }
};

module.exports = recommendationService;
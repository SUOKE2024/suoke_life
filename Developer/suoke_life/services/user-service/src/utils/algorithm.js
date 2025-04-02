/**
 * 算法工具函数
 * 用于推荐系统和数据处理
 */

/**
 * Fisher-Yates 洗牌算法
 * 用于随机化数组元素顺序
 * @param {Array} array - 要洗牌的数组
 * @returns {Array} 洗牌后的数组
 */
function shuffleArray(array) {
  const result = [...array];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

/**
 * 计算内容相似度
 * @param {Object} contentA - 内容A
 * @param {Object} contentB - 内容B
 * @returns {number} 相似度得分 (0-1)
 */
function calculateContentSimilarity(contentA, contentB) {
  if (!contentA || !contentB) return 0;
  
  let score = 0;
  let factors = 0;
  
  // 领域相似性
  if (contentA.domain && contentB.domain) {
    score += contentA.domain === contentB.domain ? 1 : 0;
    factors++;
  }
  
  // 类型相似性
  if (contentA.type && contentB.type) {
    score += contentA.type === contentB.type ? 1 : 0;
    factors++;
  }
  
  // 难度相似性
  if (contentA.difficultyLevel && contentB.difficultyLevel) {
    score += contentA.difficultyLevel === contentB.difficultyLevel ? 1 : 0;
    factors++;
  }
  
  // 标签相似性
  if (contentA.tags && contentB.tags && contentA.tags.length > 0 && contentB.tags.length > 0) {
    const commonTags = contentA.tags.filter(tag => contentB.tags.includes(tag));
    score += commonTags.length / Math.max(contentA.tags.length, contentB.tags.length);
    factors++;
  }
  
  // 相关节点相似性
  if (contentA.relatedNodes && contentB.relatedNodes && contentA.relatedNodes.length > 0 && contentB.relatedNodes.length > 0) {
    const commonNodes = contentA.relatedNodes.filter(node => contentB.relatedNodes.includes(node));
    score += commonNodes.length / Math.max(contentA.relatedNodes.length, contentB.relatedNodes.length);
    factors++;
  }
  
  return factors > 0 ? score / factors : 0;
}

/**
 * 计算内容与用户偏好的匹配分数
 * @param {Object} content - 内容对象
 * @param {Object} userPreferences - 用户偏好
 * @returns {number} 匹配分数 (0-100)
 */
function calculateContentScore(content, userPreferences, viewHistory = [], favorites = []) {
  if (!content || !userPreferences) return 0;
  
  let score = 50; // 基础分数
  
  // 领域匹配
  if (userPreferences.domains && userPreferences.domains.length > 0) {
    if (userPreferences.domains.includes(content.domain)) {
      score += 15;
    }
  }
  
  // 内容类型匹配
  if (userPreferences.contentTypes && userPreferences.contentTypes.length > 0) {
    if (userPreferences.contentTypes.includes(content.type)) {
      score += 10;
    }
  }
  
  // 难度匹配
  if (userPreferences.difficultyLevel && content.difficultyLevel) {
    if (content.difficultyLevel === userPreferences.difficultyLevel) {
      score += 10;
    } else if (
      (userPreferences.difficultyLevel === '中级' && content.difficultyLevel === '初级') ||
      (userPreferences.difficultyLevel === '高级' && content.difficultyLevel === '中级')
    ) {
      score += 5; // 相邻难度级别也有一定匹配度
    }
  }
  
  // 查看历史相似性加分
  if (viewHistory && viewHistory.length > 0) {
    // 计算与历史查看内容的平均相似度
    const similarityScores = viewHistory.map(item => 
      calculateContentSimilarity(content, item)
    );
    const avgSimilarity = similarityScores.reduce((sum, score) => sum + score, 0) / similarityScores.length;
    score += avgSimilarity * 10; // 最多加10分
  }
  
  // 收藏内容相似性加分
  if (favorites && favorites.length > 0) {
    // 计算与收藏内容的最大相似度
    const similarityScores = favorites.map(item => 
      calculateContentSimilarity(content, item)
    );
    const maxSimilarity = Math.max(...similarityScores);
    score += maxSimilarity * 15; // 最多加15分
  }
  
  // 确保分数在0-100范围内
  return Math.max(0, Math.min(100, score));
}

/**
 * 利用向量相似度计算推荐内容
 * 注意：需要知识库服务提供向量表示
 * @param {Array} contentVectors - 内容向量数据
 * @param {Array} userInterestVector - 用户兴趣向量
 * @param {number} limit - 返回数量
 * @returns {Array} 推荐内容ID
 */
async function getVectorSimilarContent(contentVectors, userInterestVector, limit = 10) {
  if (!contentVectors || !userInterestVector) return [];
  
  // 计算余弦相似度
  const similarities = contentVectors.map(content => {
    const similarity = calculateCosineSimilarity(content.vector, userInterestVector);
    return {
      contentId: content.id,
      similarity
    };
  });
  
  // 按相似度排序并返回前N个结果
  return similarities
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, limit)
    .map(item => item.contentId);
}

/**
 * 计算余弦相似度
 * @param {Array} vectorA - 向量A
 * @param {Array} vectorB - 向量B
 * @returns {number} 余弦相似度 (-1到1之间)
 */
function calculateCosineSimilarity(vectorA, vectorB) {
  if (vectorA.length !== vectorB.length) return 0;
  
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  
  for (let i = 0; i < vectorA.length; i++) {
    dotProduct += vectorA[i] * vectorB[i];
    normA += vectorA[i] * vectorA[i];
    normB += vectorB[i] * vectorB[i];
  }
  
  if (normA === 0 || normB === 0) return 0;
  
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

module.exports = {
  shuffleArray,
  calculateContentSimilarity,
  calculateContentScore,
  getVectorSimilarContent,
  calculateCosineSimilarity
};
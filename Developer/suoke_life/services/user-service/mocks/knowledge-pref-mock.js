/**
 * 知识偏好模拟服务
 * 
 * 该服务模拟知识偏好API，用于本地开发和测试环境
 * 运行在3006端口
 */

const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3006;

// 中间件配置
app.use(cors());
app.use(express.json());

// 内存存储
const knowledgePreferences = {};
const viewHistory = {};
const favorites = {};

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'knowledge-preference-mock',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// 获取用户知识偏好
app.get('/api/v1/users/:userId/knowledge-preferences', (req, res) => {
  const userId = req.params.userId;
  console.log(`获取用户 ${userId} 的知识偏好`);
  
  // 如果用户偏好不存在，创建默认偏好
  if (!knowledgePreferences[userId]) {
    knowledgePreferences[userId] = generateDefaultPreferences(userId);
  }
  
  setTimeout(() => {
    res.json({
      success: true,
      userId,
      preferences: knowledgePreferences[userId]
    });
  }, 200);
});

// 更新用户知识偏好
app.put('/api/v1/users/:userId/knowledge-preferences', (req, res) => {
  const userId = req.params.userId;
  const updatedPreferences = req.body;
  console.log(`更新用户 ${userId} 的知识偏好:`, updatedPreferences);
  
  // 更新存储的偏好
  knowledgePreferences[userId] = {
    ...knowledgePreferences[userId] || {},
    ...updatedPreferences,
    lastUpdated: new Date().toISOString()
  };
  
  setTimeout(() => {
    res.json({
      success: true,
      userId,
      message: '知识偏好已更新',
      preferences: knowledgePreferences[userId]
    });
  }, 300);
});

// 获取用户感兴趣的知识领域
app.get('/api/v1/users/:userId/interested-domains', (req, res) => {
  const userId = req.params.userId;
  console.log(`获取用户 ${userId} 感兴趣的知识领域`);
  
  // 如果用户偏好不存在，创建默认偏好
  if (!knowledgePreferences[userId]) {
    knowledgePreferences[userId] = generateDefaultPreferences(userId);
  }
  
  const domains = knowledgePreferences[userId].interestedDomains || [];
  
  setTimeout(() => {
    res.json({
      success: true,
      userId,
      domains: domains
    });
  }, 200);
});

// 获取用户知识内容访问历史
app.get('/api/v1/users/:userId/view-history', (req, res) => {
  const userId = req.params.userId;
  console.log(`获取用户 ${userId} 的内容访问历史`);
  
  // 如果历史记录不存在，创建空数组
  if (!viewHistory[userId]) {
    viewHistory[userId] = [];
  }
  
  setTimeout(() => {
    // 支持分页
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const startIndex = (page - 1) * limit;
    const endIndex = page * limit;
    
    const paginatedHistory = viewHistory[userId].slice(startIndex, endIndex);
    
    res.json({
      success: true,
      userId,
      history: paginatedHistory,
      pagination: {
        total: viewHistory[userId].length,
        page,
        limit,
        pages: Math.ceil(viewHistory[userId].length / limit)
      }
    });
  }, 300);
});

// 记录用户知识内容访问
app.post('/api/v1/users/view-history', (req, res) => {
  const { userId, contentId, contentType, title, domain, timeSpent } = req.body;
  console.log(`记录用户 ${userId} 对内容 ${contentId} 的访问`);
  
  // 如果历史记录不存在，创建空数组
  if (!viewHistory[userId]) {
    viewHistory[userId] = [];
  }
  
  // 添加新记录
  const viewRecord = {
    id: `view-${Date.now()}`,
    userId,
    contentId,
    contentType,
    title,
    domain,
    timeSpent: timeSpent || 0,
    viewedAt: new Date().toISOString()
  };
  
  // 添加到历史记录开头
  viewHistory[userId].unshift(viewRecord);
  
  setTimeout(() => {
    res.json({
      success: true,
      record: viewRecord,
      message: '访问记录已添加'
    });
  }, 200);
});

// 获取推荐给用户的知识内容
app.get('/api/v1/users/:userId/recommended-content', (req, res) => {
  const userId = req.params.userId;
  console.log(`获取推荐给用户 ${userId} 的内容`);
  
  setTimeout(() => {
    // 生成推荐内容
    const recommendations = generateRecommendedContent(userId);
    
    res.json({
      success: true,
      userId,
      recommendations,
      generatedAt: new Date().toISOString()
    });
  }, 500);
});

// 获取用户收藏的知识内容
app.get('/api/v1/users/:userId/favorites', (req, res) => {
  const userId = req.params.userId;
  console.log(`获取用户 ${userId} 的收藏内容`);
  
  // 如果收藏不存在，创建空数组
  if (!favorites[userId]) {
    favorites[userId] = [];
  }
  
  setTimeout(() => {
    // 支持分页
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const startIndex = (page - 1) * limit;
    const endIndex = page * limit;
    
    const paginatedFavorites = favorites[userId].slice(startIndex, endIndex);
    
    res.json({
      success: true,
      userId,
      favorites: paginatedFavorites,
      pagination: {
        total: favorites[userId].length,
        page,
        limit,
        pages: Math.ceil(favorites[userId].length / limit)
      }
    });
  }, 300);
});

// 添加知识内容到用户收藏
app.post('/api/v1/users/favorites', (req, res) => {
  const { userId, contentId, contentType, title, domain } = req.body;
  console.log(`用户 ${userId} 收藏内容 ${contentId}`);
  
  // 如果收藏不存在，创建空数组
  if (!favorites[userId]) {
    favorites[userId] = [];
  }
  
  // 检查是否已收藏
  const existingIndex = favorites[userId].findIndex(item => item.contentId === contentId);
  
  if (existingIndex !== -1) {
    return setTimeout(() => {
      res.status(400).json({
        success: false,
        message: '内容已经收藏过了'
      });
    }, 200);
  }
  
  // 添加新收藏
  const favoriteRecord = {
    id: `fav-${Date.now()}`,
    userId,
    contentId,
    contentType,
    title,
    domain,
    favoredAt: new Date().toISOString()
  };
  
  favorites[userId].unshift(favoriteRecord);
  
  setTimeout(() => {
    res.json({
      success: true,
      record: favoriteRecord,
      message: '内容已添加到收藏'
    });
  }, 200);
});

// 从用户收藏中移除知识内容
app.delete('/api/v1/users/favorites/:contentId', (req, res) => {
  const contentId = req.params.contentId;
  const userId = req.query.userId;
  console.log(`从用户 ${userId} 的收藏中移除内容 ${contentId}`);
  
  // 如果收藏不存在，返回错误
  if (!favorites[userId]) {
    return setTimeout(() => {
      res.status(404).json({
        success: false,
        message: '未找到用户收藏'
      });
    }, 200);
  }
  
  // 查找并移除收藏
  const initialLength = favorites[userId].length;
  favorites[userId] = favorites[userId].filter(item => item.contentId !== contentId);
  
  // 检查是否有任何变化
  const removed = initialLength !== favorites[userId].length;
  
  setTimeout(() => {
    if (removed) {
      res.json({
        success: true,
        message: '内容已从收藏中移除'
      });
    } else {
      res.status(404).json({
        success: false,
        message: '未找到指定内容'
      });
    }
  }, 200);
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`知识偏好模拟服务运行在 http://localhost:${PORT}`);
});

/**
 * 生成默认用户偏好
 */
function generateDefaultPreferences(userId) {
  // 所有可能的知识领域
  const allDomains = [
    '中医理论', '经络穴位', '食疗养生', '中药材', '气功', 
    '推拿按摩', '太极', '自然疗法', '健康饮食', '运动健身',
    '心理健康', '睡眠管理', '环境健康', '家庭医疗', '防病养生'
  ];
  
  // 所有可能的内容类型
  const allContentTypes = ['文章', '视频', '音频', '图解', '互动工具', '课程'];
  
  // 随机选择3-5个兴趣领域
  const numDomains = Math.floor(Math.random() * 3) + 3; // 3-5个
  const selectedDomains = [];
  for (let i = 0; i < numDomains; i++) {
    const domain = allDomains[Math.floor(Math.random() * allDomains.length)];
    if (!selectedDomains.includes(domain)) {
      selectedDomains.push(domain);
    }
  }
  
  // 随机选择2-3个内容类型
  const numContentTypes = Math.floor(Math.random() * 2) + 2; // 2-3个
  const selectedContentTypes = [];
  for (let i = 0; i < numContentTypes; i++) {
    const type = allContentTypes[Math.floor(Math.random() * allContentTypes.length)];
    if (!selectedContentTypes.includes(type)) {
      selectedContentTypes.push(type);
    }
  }
  
  return {
    userId,
    interestedDomains: selectedDomains,
    preferredContentTypes: selectedContentTypes,
    difficultyLevel: ['初级', '中级', '高级'][Math.floor(Math.random() * 3)],
    weeklyReadingTime: Math.floor(Math.random() * 300) + 60, // 60-360分钟/周
    createdAt: new Date().toISOString(),
    lastUpdated: new Date().toISOString()
  };
}

/**
 * 生成推荐内容
 */
function generateRecommendedContent(userId) {
  // 用户偏好（如果存在）
  const userPreferences = knowledgePreferences[userId] || generateDefaultPreferences(userId);
  
  // 可能的内容标题模板
  const titleTemplates = [
    '{domain}基础知识详解',
    '{domain}入门指南',
    '{domain}高级技巧',
    '{domain}实用案例分析',
    '{domain}中的常见误区',
    '{domain}与健康的关系',
    '如何利用{domain}改善生活',
    '{domain}的历史与发展',
    '{domain}的科学解释',
    '专家谈{domain}的重要性'
  ];
  
  // 基于用户偏好生成推荐
  const recommendations = [];
  const count = Math.floor(Math.random() * 5) + 5; // 5-10个推荐
  
  for (let i = 0; i < count; i++) {
    // 随机选择一个用户感兴趣的领域
    const domain = userPreferences.interestedDomains[
      Math.floor(Math.random() * userPreferences.interestedDomains.length)
    ];
    
    // 随机选择一个用户偏好的内容类型
    const contentType = userPreferences.preferredContentTypes[
      Math.floor(Math.random() * userPreferences.preferredContentTypes.length)
    ];
    
    // 随机选择一个标题模板
    const titleTemplate = titleTemplates[Math.floor(Math.random() * titleTemplates.length)];
    const title = titleTemplate.replace('{domain}', domain);
    
    // 创建推荐项
    recommendations.push({
      id: `content-${Date.now()}-${i}`,
      title,
      domain,
      contentType,
      difficulty: userPreferences.difficultyLevel,
      relevanceScore: (0.7 + Math.random() * 0.3).toFixed(2), // 0.7-1.0
      createdAt: new Date(Date.now() - Math.floor(Math.random() * 30 * 86400000)).toISOString(), // 过去30天内
      estimatedReadingTime: Math.floor(Math.random() * 20) + 5, // 5-25分钟
      thumbnailUrl: `https://example.com/thumbnails/${Math.floor(Math.random() * 1000)}.jpg`
    });
  }
  
  return recommendations;
} 
/**
 * 用户画像模拟服务
 * 
 * 该服务模拟用户画像API，用于本地开发和测试环境
 * 运行在3005端口
 */

const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3005;

// 中间件配置
app.use(cors());
app.use(express.json());

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'user-profile-mock',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// 用户画像生成端点
app.post('/generate-profile', (req, res) => {
  console.log('收到用户画像生成请求:', req.body);
  
  // 模拟处理延迟
  setTimeout(() => {
    // 提取请求数据
    const { userId, healthData, interactionHistory, knowledgePreferences } = req.body;
    
    // 生成模拟用户画像
    const userProfile = generateMockUserProfile(userId, healthData, interactionHistory, knowledgePreferences);
    
    res.json({
      success: true,
      userId,
      profile: userProfile,
      generatedAt: new Date().toISOString(),
      confidence: 0.85 + (Math.random() * 0.1) // 85-95% 置信度
    });
  }, 800); // 模拟800ms延迟
});

// 用户画像查询端点
app.get('/users/:userId/profile', (req, res) => {
  console.log(`收到用户 ${req.params.userId} 的画像查询请求`);
  
  // 模拟处理延迟
  setTimeout(() => {
    const userId = req.params.userId;
    
    // 生成模拟用户画像
    const userProfile = generateMockUserProfile(userId);
    
    res.json({
      success: true,
      userId,
      profile: userProfile,
      lastUpdated: new Date().toISOString(),
      dataPoints: Math.floor(Math.random() * 500) + 1000 // 1000-1500 数据点
    });
  }, 300); // 模拟300ms延迟
});

// 用户画像更新端点
app.put('/users/:userId/profile', (req, res) => {
  console.log(`收到用户 ${req.params.userId} 的画像更新请求:`, req.body);
  
  // 模拟处理延迟
  setTimeout(() => {
    const userId = req.params.userId;
    const updateData = req.body;
    
    res.json({
      success: true,
      userId,
      message: '用户画像已成功更新',
      updatedAt: new Date().toISOString(),
      changedFields: Object.keys(updateData),
      nextScheduledUpdate: new Date(Date.now() + 86400000).toISOString() // 24小时后
    });
  }, 500); // 模拟500ms延迟
});

// 用户画像比较端点
app.post('/compare-profiles', (req, res) => {
  console.log('收到用户画像比较请求:', req.body);
  
  // 模拟处理延迟
  setTimeout(() => {
    const { userIds, compareAspects } = req.body;
    
    // 生成模拟比较结果
    const comparisonResult = {
      comparisonId: `comp-${Date.now()}`,
      timestamp: new Date().toISOString(),
      users: userIds,
      results: {}
    };
    
    // 生成各方面的比较结果
    const aspects = compareAspects || ['healthCondition', 'knowledgeInterests', 'lifestyleHabits', 'activityLevel'];
    aspects.forEach(aspect => {
      comparisonResult.results[aspect] = {
        similarity: Math.random().toFixed(2),
        differences: generateRandomDifferences(),
        recommendations: generateRandomRecommendations(aspect)
      };
    });
    
    // 生成总体相似度
    comparisonResult.overallSimilarity = (
      Object.values(comparisonResult.results)
        .reduce((sum, item) => sum + parseFloat(item.similarity), 0) / aspects.length
    ).toFixed(2);
    
    res.json({
      success: true,
      comparison: comparisonResult
    });
  }, 1200); // 模拟1.2秒延迟
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`用户画像模拟服务运行在 http://localhost:${PORT}`);
});

/**
 * 生成模拟用户画像
 */
function generateMockUserProfile(userId, healthData, interactionHistory, knowledgePreferences) {
  // 体质类型列表
  const constitutionTypes = [
    '平和质', '气虚质', '阳虚质', '阴虚质', 
    '痰湿质', '湿热质', '血瘀质', '气郁质', '特禀质'
  ];
  
  // 兴趣领域列表
  const interestDomains = [
    '中医理论', '经络穴位', '食疗养生', '中药材', '气功', 
    '推拿按摩', '太极', '自然疗法', '健康饮食', '运动健身',
    '心理健康', '睡眠管理', '环境健康', '家庭医疗', '防病养生'
  ];
  
  // 随机选择2-4个体质类型，第一个权重更高
  const primaryConstType = constitutionTypes[Math.floor(Math.random() * constitutionTypes.length)];
  const secondaryConstTypes = [];
  const numSecondaryTypes = Math.floor(Math.random() * 3) + 1; // 1-3个次要体质
  
  for (let i = 0; i < numSecondaryTypes; i++) {
    let type = constitutionTypes[Math.floor(Math.random() * constitutionTypes.length)];
    // 确保不重复
    while (type === primaryConstType || secondaryConstTypes.includes(type)) {
      type = constitutionTypes[Math.floor(Math.random() * constitutionTypes.length)];
    }
    secondaryConstTypes.push(type);
  }
  
  // 随机选择3-7个兴趣领域
  const numInterests = Math.floor(Math.random() * 5) + 3; // 3-7个兴趣
  const interests = [];
  for (let i = 0; i < numInterests; i++) {
    let interest = interestDomains[Math.floor(Math.random() * interestDomains.length)];
    // 确保不重复
    while (interests.includes(interest)) {
      interest = interestDomains[Math.floor(Math.random() * interestDomains.length)];
    }
    interests.push(interest);
  }
  
  // 生成兴趣权重
  const interestWeights = {};
  interests.forEach(interest => {
    interestWeights[interest] = (Math.random() * 0.6 + 0.4).toFixed(2); // 权重范围0.4-1.0
  });
  
  // 生成模拟用户画像
  return {
    basicInfo: {
      userId: userId || `user-${Math.floor(Math.random() * 10000)}`,
      ageGroup: ['18-24', '25-34', '35-44', '45-54', '55-64', '65+'][Math.floor(Math.random() * 6)],
      gender: ['男', '女'][Math.floor(Math.random() * 2)],
      location: ['北京', '上海', '广州', '深圳', '杭州', '成都', '重庆', '西安', '武汉'][Math.floor(Math.random() * 9)]
    },
    tcmConstitution: {
      primaryType: primaryConstType,
      primaryTypeConfidence: (0.7 + Math.random() * 0.3).toFixed(2), // 0.7-1.0
      secondaryTypes: secondaryConstTypes.map(type => ({
        type,
        confidence: (0.4 + Math.random() * 0.3).toFixed(2) // 0.4-0.7
      })),
      lastAssessmentDate: new Date(Date.now() - Math.floor(Math.random() * 90 * 86400000)).toISOString() // 过去90天内
    },
    healthCondition: {
      overallScore: Math.floor(Math.random() * 40) + 60, // 60-100分
      sleepQuality: Math.floor(Math.random() * 5) + 1, // 1-5分
      stressLevel: Math.floor(Math.random() * 5) + 1, // 1-5分
      exerciseFrequency: Math.floor(Math.random() * 7), // 0-6次每周
      dietQuality: Math.floor(Math.random() * 5) + 1, // 1-5分
      healthRisks: generateRandomHealthRisks(),
      recommendations: generateRandomHealthRecommendations()
    },
    knowledgeProfile: {
      interestDomains: Object.keys(interestWeights).map(domain => ({
        domain,
        weight: interestWeights[domain]
      })),
      contentPreferences: {
        preferredFormats: generateRandomPreferredFormats(),
        difficultyLevel: ['初级', '中级', '高级'][Math.floor(Math.random() * 3)],
        readingTime: Math.floor(Math.random() * 60) + 30 // 30-90分钟/周
      },
      knowledgeLevel: {
        overall: ['入门', '基础', '进阶', '专业', '专家'][Math.floor(Math.random() * 5)],
        domainSpecific: generateRandomDomainKnowledge(interests)
      }
    },
    behaviorPatterns: {
      appUsage: {
        averageDailyTime: Math.floor(Math.random() * 60) + 15, // 15-75分钟/天
        peakUsageHours: [Math.floor(Math.random() * 12) + 8, Math.floor(Math.random() * 12) + 8], // 8-20点
        frequentFeatures: generateRandomFrequentFeatures()
      },
      contentInteraction: {
        readArticlesPerWeek: Math.floor(Math.random() * 15) + 5, // 5-20篇/周
        watchVideosPerWeek: Math.floor(Math.random() * 10) + 2, // 2-12个/周
        practiceSessionsPerWeek: Math.floor(Math.random() * 7) + 1, // 1-8次/周
        favoriteContentCategories: generateRandomFavoriteCategories()
      },
      socialBehavior: {
        sharingFrequency: Math.floor(Math.random() * 10), // 0-10次/周
        commentsPerMonth: Math.floor(Math.random() * 20), // 0-20次/月
        communityParticipation: ['低', '中', '高'][Math.floor(Math.random() * 3)],
        influenceScore: Math.floor(Math.random() * 100) // 0-100分
      }
    },
    predictiveInsights: {
      likelyInterests: generateRandomLikelyInterests(interestDomains, interests),
      recommendedContent: generateRandomRecommendedContent(),
      healthTrends: {
        improving: generateRandomHealthAspects(),
        concerning: generateRandomHealthAspects(),
        stable: generateRandomHealthAspects()
      },
      engagementPrediction: {
        nextMonthEngagement: ['下降', '稳定', '上升'][Math.floor(Math.random() * 3)],
        retentionProbability: (0.6 + Math.random() * 0.4).toFixed(2), // 0.6-1.0
        contentRecommendationSuccess: (0.5 + Math.random() * 0.5).toFixed(2) // 0.5-1.0
      }
    },
    metaData: {
      profileVersion: '2.1',
      lastUpdated: new Date().toISOString(),
      dataPointsAnalyzed: Math.floor(Math.random() * 1000) + 500, // 500-1500
      confidenceScore: (0.75 + Math.random() * 0.25).toFixed(2), // 0.75-1.0
      nextUpdateScheduled: new Date(Date.now() + 7 * 86400000).toISOString() // 7天后
    }
  };
}

// 辅助函数：生成随机健康风险
function generateRandomHealthRisks() {
  const allRisks = [
    '免疫力下降', '睡眠不足', '情绪波动', '气血亏虚', 
    '肝郁气滞', '脾胃不和', '肾气不足', '心神不宁'
  ];
  
  const risks = [];
  const numRisks = Math.floor(Math.random() * 3); // 0-2个风险
  
  for (let i = 0; i < numRisks; i++) {
    const risk = allRisks[Math.floor(Math.random() * allRisks.length)];
    if (!risks.includes(risk)) {
      risks.push(risk);
    }
  }
  
  return risks;
}

// 辅助函数：生成随机健康建议
function generateRandomHealthRecommendations() {
  const allRecommendations = [
    '增加优质睡眠时间', '养成规律作息习惯', '适度增加有氧运动', 
    '保持情绪稳定', '增加蔬果摄入', '减少加工食品', 
    '增加优质蛋白质', '定期进行中医体质调理', '练习八段锦'
  ];
  
  const recommendations = [];
  const numRecommendations = Math.floor(Math.random() * 3) + 2; // 2-4个建议
  
  for (let i = 0; i < numRecommendations; i++) {
    const recommendation = allRecommendations[Math.floor(Math.random() * allRecommendations.length)];
    if (!recommendations.includes(recommendation)) {
      recommendations.push(recommendation);
    }
  }
  
  return recommendations;
}

// 辅助函数：生成随机内容格式偏好
function generateRandomPreferredFormats() {
  const allFormats = ['文章', '视频', '音频', '图解', '互动工具', '课程'];
  const formats = [];
  const numFormats = Math.floor(Math.random() * 3) + 2; // 2-4个格式
  
  for (let i = 0; i < numFormats; i++) {
    const format = allFormats[Math.floor(Math.random() * allFormats.length)];
    if (!formats.includes(format)) {
      formats.push(format);
    }
  }
  
  return formats;
}

// 辅助函数：生成随机领域知识水平
function generateRandomDomainKnowledge(interests) {
  const levels = ['初学', '基础', '进阶', '熟练', '精通'];
  const domainLevels = {};
  
  interests.forEach(interest => {
    domainLevels[interest] = levels[Math.floor(Math.random() * levels.length)];
  });
  
  return domainLevels;
}

// 辅助函数：生成随机常用功能
function generateRandomFrequentFeatures() {
  const allFeatures = [
    '每日健康提醒', '中医知识阅读', '体质测评', '穴位查询', 
    '健康数据记录', '社区互动', '专家咨询', '智能诊断'
  ];
  
  const features = [];
  const numFeatures = Math.floor(Math.random() * 3) + 2; // 2-4个功能
  
  for (let i = 0; i < numFeatures; i++) {
    const feature = allFeatures[Math.floor(Math.random() * allFeatures.length)];
    if (!features.includes(feature)) {
      features.push(feature);
    }
  }
  
  return features;
}

// 辅助函数：生成随机喜爱内容类别
function generateRandomFavoriteCategories() {
  const allCategories = [
    '中医基础理论', '穴位按摩指南', '季节养生方案', '常见疾病调理', 
    '药膳食疗', '经络健康', '情志养生', '养生运动'
  ];
  
  const categories = [];
  const numCategories = Math.floor(Math.random() * 3) + 2; // 2-4个类别
  
  for (let i = 0; i < numCategories; i++) {
    const category = allCategories[Math.floor(Math.random() * allCategories.length)];
    if (!categories.includes(category)) {
      categories.push(category);
    }
  }
  
  return categories;
}

// 辅助函数：生成随机可能兴趣
function generateRandomLikelyInterests(allDomains, currentInterests) {
  const potentialInterests = allDomains.filter(domain => !currentInterests.includes(domain));
  const likelyInterests = [];
  const numInterests = Math.min(Math.floor(Math.random() * 3) + 1, potentialInterests.length); // 1-3个可能兴趣
  
  for (let i = 0; i < numInterests; i++) {
    if (potentialInterests.length > 0) {
      const randomIndex = Math.floor(Math.random() * potentialInterests.length);
      likelyInterests.push({
        domain: potentialInterests[randomIndex],
        likelihood: (0.6 + Math.random() * 0.3).toFixed(2) // 0.6-0.9
      });
      potentialInterests.splice(randomIndex, 1);
    }
  }
  
  return likelyInterests;
}

// 辅助函数：生成随机推荐内容
function generateRandomRecommendedContent() {
  const contentTypes = ['文章', '视频', '音频', '互动工具', '课程'];
  const recommendations = [];
  const numRecommendations = Math.floor(Math.random() * 3) + 2; // 2-4个推荐
  
  for (let i = 0; i < numRecommendations; i++) {
    recommendations.push({
      id: `content-${Math.floor(Math.random() * 10000)}`,
      title: `推荐内容标题-${Math.floor(Math.random() * 100)}`,
      type: contentTypes[Math.floor(Math.random() * contentTypes.length)],
      relevanceScore: (0.7 + Math.random() * 0.3).toFixed(2), // 0.7-1.0
      reason: ['兴趣匹配', '历史偏好', '体质相关', '热门推荐'][Math.floor(Math.random() * 4)]
    });
  }
  
  return recommendations;
}

// 辅助函数：生成随机健康方面
function generateRandomHealthAspects() {
  const allAspects = [
    '睡眠质量', '情绪稳定性', '免疫功能', '消化功能', 
    '能量水平', '专注度', '心肺功能', '肌肉力量', '灵活性'
  ];
  
  const aspects = [];
  const numAspects = Math.floor(Math.random() * 2) + 1; // 1-2个方面
  
  for (let i = 0; i < numAspects; i++) {
    const aspect = allAspects[Math.floor(Math.random() * allAspects.length)];
    if (!aspects.includes(aspect)) {
      aspects.push(aspect);
    }
  }
  
  return aspects;
}

// 辅助函数：生成随机差异点
function generateRandomDifferences() {
  const allDifferences = [
    '年龄段差异', '体质类型差异', '生活习惯差异', '运动频率差异',
    '饮食偏好差异', '睡眠模式差异', '知识水平差异', '兴趣领域差异'
  ];
  
  const differences = [];
  const numDifferences = Math.floor(Math.random() * 3) + 1; // 1-3个差异
  
  for (let i = 0; i < numDifferences; i++) {
    const difference = allDifferences[Math.floor(Math.random() * allDifferences.length)];
    if (!differences.includes(difference)) {
      differences.push(difference);
    }
  }
  
  return differences;
}

// 辅助函数：生成随机建议
function generateRandomRecommendations(aspect) {
  const recommendationsByAspect = {
    healthCondition: [
      '共同参与户外活动', '分享健康食谱', '互相督促锻炼', '一起参加健康讲座'
    ],
    knowledgeInterests: [
      '交流学习经验', '组织读书会', '分享优质内容', '一起参加线下课程'
    ],
    lifestyleHabits: [
      '建立共同的作息时间', '交流时间管理技巧', '分享健康生活窍门', '互相监督良好习惯'
    ],
    activityLevel: [
      '制定共同的活动计划', '尝试新的运动方式', '参加线下活动', '建立运动小组'
    ]
  };
  
  const defaultRecommendations = [
    '定期交流经验', '分享各自领域知识', '互相鼓励进步', '建立共同目标'
  ];
  
  const options = recommendationsByAspect[aspect] || defaultRecommendations;
  
  const recommendations = [];
  const numRecommendations = Math.floor(Math.random() * 2) + 1; // 1-2个建议
  
  for (let i = 0; i < numRecommendations; i++) {
    const recommendation = options[Math.floor(Math.random() * options.length)];
    if (!recommendations.includes(recommendation)) {
      recommendations.push(recommendation);
    }
  }
  
  return recommendations;
} 
/**
 * OpenAI工具控制器
 * 处理AI工具函数调用
 */
const { userService, profileService, healthProfileService } = require('../services');
const { logger } = require('@suoke/shared').utils;
const config = require('../config');
const { encryption, db, metrics } = require('../utils');

// 获取用户资料
const getUserProfile = async (req, res) => {
  try {
    const { user_id, fields } = req.body;
    
    // 使用当前认证用户或指定用户ID
    const userId = user_id || req.user.id;
    
    // 检查权限（只有管理员可以查看其他用户资料）
    if (userId !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({
        status: 'error',
        message: '无权限查看其他用户资料'
      });
    }
    
    // 获取用户基本信息
    const user = await userService.getUserById(userId);
    if (!user) {
      return res.status(404).json({
        status: 'error',
        message: '用户不存在'
      });
    }
    
    // 获取用户资料
    const profile = await profileService.getProfileByUserId(userId);
    
    // 根据请求的字段过滤结果
    let result = {
      id: user.id,
      username: user.username,
      email: user.email,
      phone: user.phone,
      role: user.role,
      status: user.status,
      created_at: user.created_at,
      profile: profile || {}
    };
    
    // 如果指定了字段，只返回请求的字段
    if (fields && Array.isArray(fields) && fields.length > 0) {
      const filteredResult = {};
      fields.forEach(field => {
        if (field.includes('.')) {
          // 处理嵌套字段，如 profile.nickname
          const [parent, child] = field.split('.');
          if (!filteredResult[parent]) filteredResult[parent] = {};
          if (result[parent] && result[parent][child]) {
            filteredResult[parent][child] = result[parent][child];
          }
        } else if (result[field]) {
          filteredResult[field] = result[field];
        }
      });
      result = filteredResult;
    }
    
    // 解密敏感字段
    result = encryption.decryptSensitiveFields(result);
    
    return res.status(200).json({
      status: 'success',
      data: result
    });
  } catch (error) {
    logger.error('获取用户资料失败', { error: error.message });
    return res.status(500).json({
      status: 'error',
      message: '获取用户资料失败',
      error: error.message
    });
  }
};

// 获取用户体质资料
const getConstitutionProfile = async (req, res) => {
  try {
    const { user_id, include_history } = req.body;
    
    // 使用当前认证用户或指定用户ID
    const userId = user_id || req.user.id;
    
    // 检查权限
    if (userId !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({
        status: 'error',
        message: '无权限查看其他用户体质资料'
      });
    }
    
    // 获取用户健康资料
    const healthProfile = await healthProfileService.getHealthProfileByUserId(userId);
    if (!healthProfile) {
      return res.status(404).json({
        status: 'error',
        message: '未找到健康资料'
      });
    }
    
    // 基本体质信息
    let result = {
      constitution_type: healthProfile.constitution_type,
      last_assessment_date: healthProfile.updated_at
    };
    
    // 如果需要获取历史体质数据
    if (include_history) {
      const history = await healthProfileService.getConstitutionHistory(userId);
      result.history = history || [];
    }
    
    return res.status(200).json({
      status: 'success',
      data: result
    });
  } catch (error) {
    logger.error('获取用户体质资料失败', { error: error.message });
    return res.status(500).json({
      status: 'error',
      message: '获取用户体质资料失败',
      error: error.message
    });
  }
};

// 获取健康建议
const getHealthRecommendations = async (req, res) => {
  try {
    const { user_id, category, season } = req.body;
    
    // 使用当前认证用户或指定用户ID
    const userId = user_id || req.user.id;
    
    // 检查权限
    if (userId !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({
        status: 'error',
        message: '无权限获取其他用户健康建议'
      });
    }
    
    // 获取用户健康资料
    const healthProfile = await healthProfileService.getHealthProfileByUserId(userId);
    if (!healthProfile) {
      return res.status(404).json({
        status: 'error',
        message: '未找到健康资料'
      });
    }
    
    // 获取当前季节（如果未指定）
    const currentSeason = season || getCurrentSeason();
    
    // 根据体质和季节获取建议
    const recommendations = await healthProfileService.getRecommendationsByConstitution(
      healthProfile.constitution_type,
      currentSeason,
      category || 'all'
    );
    
    return res.status(200).json({
      status: 'success',
      data: {
        constitution_type: healthProfile.constitution_type,
        season: currentSeason,
        category: category || 'all',
        recommendations
      }
    });
  } catch (error) {
    logger.error('获取健康建议失败', { error: error.message });
    return res.status(500).json({
      status: 'error',
      message: '获取健康建议失败',
      error: error.message
    });
  }
};

// 更新用户偏好设置
const updateUserPreference = async (req, res) => {
  try {
    const { user_id, preferences } = req.body;
    
    if (!preferences || typeof preferences !== 'object') {
      return res.status(400).json({
        status: 'error',
        message: '偏好设置数据无效'
      });
    }
    
    // 使用当前认证用户或指定用户ID
    const userId = user_id || req.user.id;
    
    // 检查权限
    if (userId !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({
        status: 'error',
        message: '无权限更新其他用户的偏好设置'
      });
    }
    
    // 更新偏好设置
    const result = await userService.updateUserPreferences(userId, preferences);
    
    return res.status(200).json({
      status: 'success',
      message: '偏好设置已更新',
      data: result
    });
  } catch (error) {
    logger.error('更新用户偏好设置失败', { error: error.message });
    return res.status(500).json({
      status: 'error',
      message: '更新用户偏好设置失败',
      error: error.message
    });
  }
};

// 获取成就状态
const getAchievementStatus = async (req, res) => {
  const metricsLabels = {
    function: 'getAchievementStatus',
    service: 'openai-tools'
  };
  
  const timer = metrics.functionDurationHistogram.startTimer(metricsLabels);
  
  try {
    const { user_id, category } = req.body;
    
    // 使用当前认证用户或指定用户ID
    const userId = user_id || req.user.id;
    
    // 检查权限
    if (userId !== req.user.id && req.user.role !== 'admin') {
      metrics.functionErrorCounter.inc({
        ...metricsLabels,
        error_type: 'permission_denied'
      });
      
      return res.status(403).json({
        status: 'error',
        message: '无权限查看其他用户的成就状态'
      });
    }
    
    // 尝试从数据库获取成就数据
    let achievements = [];
    
    try {
      // 查询数据库获取用户成就
      const conn = await db.getConnection();
      
      const query = `
        SELECT 
          a.id, a.name, a.description, a.category, 
          ua.completed, ua.progress, a.reward
        FROM 
          achievements a
        LEFT JOIN 
          user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = ?
        WHERE 
          ${category !== 'all' ? 'a.category = ? AND' : ''} 
          (ua.user_id = ? OR ua.user_id IS NULL)
        ORDER BY 
          a.category, a.name
      `;
      
      const params = category !== 'all' 
        ? [userId, category, userId]
        : [userId, userId];
      
      const [rows] = await conn.execute(query, params);
      conn.release();
      
      if (rows && rows.length > 0) {
        achievements = rows.map(row => ({
          id: row.id,
          name: row.name,
          description: row.description,
          category: row.category,
          completed: row.completed === 1,
          progress: row.progress || 0,
          reward: row.reward
        }));
      } else {
        // 如果数据库中没有数据，则使用模拟数据
        achievements = getMockAchievements(category || 'all');
      }
    } catch (dbError) {
      logger.error('从数据库获取成就数据失败', { error: dbError.message });
      metrics.functionErrorCounter.inc({
        ...metricsLabels,
        error_type: 'database_error'
      });
      
      // 数据库查询失败时使用模拟数据
      achievements = getMockAchievements(category || 'all');
    }
    
    // 记录指标
    metrics.functionCallCounter.inc(metricsLabels);
    timer();
    
    return res.status(200).json({
      status: 'success',
      data: {
        category: category || 'all',
        achievements
      }
    });
  } catch (error) {
    // 记录错误指标
    metrics.functionErrorCounter.inc({
      ...metricsLabels,
      error_type: 'general_error'
    });
    timer();
    
    logger.error('获取成就状态失败', { 
      error: error.message,
      stack: error.stack,
      user_id: req.body.user_id || req.user?.id
    });
    
    return res.status(500).json({
      status: 'error',
      message: '获取成就状态失败',
      error: config.env === 'development' ? error.message : undefined
    });
  }
};

// 获取用户优惠券
const getVouchers = async (req, res) => {
  const metricsLabels = {
    function: 'getVouchers',
    service: 'openai-tools'
  };
  
  const timer = metrics.functionDurationHistogram.startTimer(metricsLabels);
  
  try {
    const { user_id, status, type } = req.body;
    
    // 使用当前认证用户或指定用户ID
    const userId = user_id || req.user.id;
    
    // 检查权限
    if (userId !== req.user.id && req.user.role !== 'admin') {
      metrics.functionErrorCounter.inc({
        ...metricsLabels,
        error_type: 'permission_denied'
      });
      
      return res.status(403).json({
        status: 'error',
        message: '无权限查看其他用户的优惠券'
      });
    }
    
    // 尝试从数据库获取优惠券数据
    let vouchers = [];
    
    try {
      // 获取当前日期
      const now = new Date();
      const dateStr = now.toISOString().split('T')[0];
      
      // 构建查询条件
      let statusCondition = '';
      if (status === 'available') {
        statusCondition = `AND v.expiry_date >= ? AND v.used_at IS NULL`;
      } else if (status === 'used') {
        statusCondition = `AND v.used_at IS NOT NULL`;
      } else if (status === 'expired') {
        statusCondition = `AND v.expiry_date < ? AND v.used_at IS NULL`;
      }
      
      let typeCondition = '';
      if (type !== 'all') {
        typeCondition = `AND v.type = ?`;
      }
      
      // 查询数据库获取用户优惠券
      const conn = await db.getConnection();
      
      const query = `
        SELECT 
          v.id, v.name, v.description, v.type, v.value,
          v.expiry_date, v.used_at, v.issued_at
        FROM 
          vouchers v
        WHERE 
          v.user_id = ?
          ${statusCondition}
          ${typeCondition}
        ORDER BY 
          v.expiry_date, v.type
      `;
      
      // 构建参数数组
      let params = [userId];
      if (status === 'available' || status === 'expired') {
        params.push(dateStr);
      }
      if (type !== 'all') {
        params.push(type);
      }
      
      const [rows] = await conn.execute(query, params);
      conn.release();
      
      if (rows && rows.length > 0) {
        vouchers = rows.map(row => ({
          id: row.id,
          name: row.name,
          description: row.description,
          type: row.type,
          value: row.value,
          expiry: row.expiry_date,
          used_at: row.used_at,
          issued_at: row.issued_at
        }));
      } else {
        // 如果数据库中没有数据，则使用模拟数据
        vouchers = getMockVouchers(status || 'all', type || 'all');
      }
    } catch (dbError) {
      logger.error('从数据库获取优惠券数据失败', { error: dbError.message });
      metrics.functionErrorCounter.inc({
        ...metricsLabels,
        error_type: 'database_error'
      });
      
      // 数据库查询失败时使用模拟数据
      vouchers = getMockVouchers(status || 'all', type || 'all');
    }
    
    // 记录指标
    metrics.functionCallCounter.inc(metricsLabels);
    timer();
    
    return res.status(200).json({
      status: 'success',
      data: {
        status: status || 'all',
        type: type || 'all',
        vouchers
      }
    });
  } catch (error) {
    // 记录错误指标
    metrics.functionErrorCounter.inc({
      ...metricsLabels,
      error_type: 'general_error'
    });
    timer();
    
    logger.error('获取用户优惠券失败', { 
      error: error.message,
      stack: error.stack,
      user_id: req.body.user_id || req.user?.id
    });
    
    return res.status(500).json({
      status: 'error',
      message: '获取用户优惠券失败',
      error: config.env === 'development' ? error.message : undefined
    });
  }
};

// 辅助函数：获取当前季节
const getCurrentSeason = () => {
  const now = new Date();
  const month = now.getMonth() + 1;
  
  if (month >= 3 && month <= 5) return '春季';
  if (month >= 6 && month <= 8) return '夏季';
  if (month >= 9 && month <= 11) return '秋季';
  return '冬季';
};

// 辅助函数：生成模拟成就数据
const getMockAchievements = (category) => {
  const allAchievements = {
    health_tracking: [
      { id: "ht1", name: "健康记录新手", description: "首次记录健康数据", completed: true, progress: 100, reward: 10 },
      { id: "ht2", name: "健康跟踪达人", description: "连续30天记录健康数据", completed: false, progress: 40, reward: 50 }
    ],
    learning: [
      { id: "l1", name: "知识探索者", description: "阅读10篇健康文章", completed: true, progress: 100, reward: 20 },
      { id: "l2", name: "学习达人", description: "完成所有中医基础课程", completed: false, progress: 60, reward: 100 }
    ],
    social: [
      { id: "s1", name: "社区新手", description: "首次参与社区讨论", completed: true, progress: 100, reward: 10 },
      { id: "s2", name: "社区活跃者", description: "发布10个帖子", completed: false, progress: 30, reward: 50 }
    ],
    lifestyle: [
      { id: "ls1", name: "作息规律", description: "一周内按时睡觉7天", completed: false, progress: 70, reward: 30 },
      { id: "ls2", name: "饮食均衡", description: "记录30天健康饮食", completed: false, progress: 60, reward: 50 }
    ],
    tcm_knowledge: [
      { id: "tcm1", name: "中医入门", description: "完成中医基础知识测试", completed: true, progress: 100, reward: 30 },
      { id: "tcm2", name: "草药专家", description: "识别50种中药材", completed: false, progress: 40, reward: 80 }
    ]
  };
  
  if (category === 'all') {
    return Object.values(allAchievements).flat();
  }
  
  return allAchievements[category] || [];
};

// 辅助函数：生成模拟优惠券数据
const getMockVouchers = (status, type) => {
  const allVouchers = {
    available: {
      physical_service: [
        { id: "ps1", name: "按摩体验券", description: "可兑换一次专业按摩服务", expiry: "2023-12-31", value: "200元" },
        { id: "ps2", name: "中医咨询券", description: "可兑换一次中医专家咨询", expiry: "2023-12-31", value: "300元" }
      ],
      product_discount: [
        { id: "pd1", name: "商品9折券", description: "任意商品可使用", expiry: "2023-11-30", value: "9折" },
        { id: "pd2", name: "保健品满减券", description: "保健品满200减30", expiry: "2023-11-30", value: "30元" }
      ],
      experience_ticket: [
        { id: "et1", name: "农场体验券", description: "一次农场采摘体验", expiry: "2023-12-31", value: "100元" }
      ]
    },
    used: {
      physical_service: [
        { id: "ps3", name: "健康检查券", description: "免费健康检查一次", used_at: "2023-10-01", value: "500元" }
      ],
      product_discount: [
        { id: "pd3", name: "商品8折券", description: "任意商品可使用", used_at: "2023-09-15", value: "8折" }
      ],
      experience_ticket: []
    },
    expired: {
      physical_service: [
        { id: "ps4", name: "足疗体验券", description: "一次足疗服务", expired_at: "2023-08-31", value: "150元" }
      ],
      product_discount: [
        { id: "pd4", name: "新人优惠券", description: "首次购物7折", expired_at: "2023-07-31", value: "7折" }
      ],
      experience_ticket: [
        { id: "et2", name: "瑜伽课体验券", description: "一次瑜伽课程", expired_at: "2023-08-31", value: "80元" }
      ]
    }
  };
  
  // 根据请求的状态和类型过滤优惠券
  let result = [];
  
  if (status === 'all') {
    Object.values(allVouchers).forEach(statusGroup => {
      if (type === 'all') {
        Object.values(statusGroup).forEach(typeGroup => {
          result = result.concat(typeGroup);
        });
      } else {
        result = result.concat(statusGroup[type] || []);
      }
    });
  } else {
    if (type === 'all') {
      Object.values(allVouchers[status] || {}).forEach(typeGroup => {
        result = result.concat(typeGroup);
      });
    } else {
      result = allVouchers[status]?.[type] || [];
    }
  }
  
  return result;
};

module.exports = {
  getUserProfile,
  getConstitutionProfile,
  getHealthRecommendations,
  updateUserPreference,
  getAchievementStatus,
  getVouchers
}; 
/**
 * OpenAI兼容服务
 */
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const config = require('../config');
const { userService } = require('./');
const { profileService } = require('./');
const { healthProfileService } = require('./');
const { logger } = require('@suoke/shared').utils;

// 加载工具配置
const loadToolsConfig = () => {
  try {
    const toolsConfigPath = path.resolve(process.cwd(), config.openai.toolsConfigPath);
    if (fs.existsSync(toolsConfigPath)) {
      const toolsConfig = JSON.parse(fs.readFileSync(toolsConfigPath, 'utf8'));
      return toolsConfig.tools || [];
    }
    logger.warn('OpenAI工具配置文件不存在', { path: toolsConfigPath });
    return [];
  } catch (error) {
    logger.error('加载OpenAI工具配置失败', { error: error.message });
    return [];
  }
};

// 工具函数实现映射
const toolFunctions = {
  // 获取用户资料
  get_user_profile: async (userId, params) => {
    try {
      // 如果没有提供用户ID，则使用当前用户
      const targetUserId = params.user_id || userId;
      // 检查权限（只能获取自己的或有权限查看的用户资料）
      if (targetUserId !== userId) {
        // 这里应该有更详细的权限检查
        throw new Error('无权访问其他用户资料');
      }
      
      // 获取用户资料
      const fields = params.fields || [];
      const userProfile = await profileService.getProfileByUserId(targetUserId);
      
      // 如果有指定字段，只返回这些字段
      if (fields.length > 0) {
        const filteredProfile = {};
        fields.forEach(field => {
          if (userProfile[field] !== undefined) {
            filteredProfile[field] = userProfile[field];
          }
        });
        return filteredProfile;
      }
      
      return userProfile;
    } catch (error) {
      logger.error('执行get_user_profile工具失败', { 
        userId, 
        params, 
        error: error.message 
      });
      throw error;
    }
  },
  
  // 获取用户体质资料
  get_constitution_profile: async (userId, params) => {
    try {
      // 如果没有提供用户ID，则使用当前用户
      const targetUserId = params.user_id || userId;
      // 检查权限
      if (targetUserId !== userId) {
        throw new Error('无权访问其他用户体质资料');
      }
      
      // 获取体质资料
      const healthProfile = await healthProfileService.getHealthProfileByUserId(targetUserId);
      const includeHistory = params.include_history || false;
      
      const result = {
        constitution_type: healthProfile.constitution_type,
        last_checkup: healthProfile.last_checkup
      };
      
      // 如果需要历史数据
      if (includeHistory) {
        result.history = []; // 这里应该从历史记录中获取
      }
      
      return result;
    } catch (error) {
      logger.error('执行get_constitution_profile工具失败', { 
        userId, 
        params, 
        error: error.message 
      });
      throw error;
    }
  },
  
  // 获取健康建议
  get_health_recommendations: async (userId, params) => {
    try {
      // 如果没有提供用户ID，则使用当前用户
      const targetUserId = params.user_id || userId;
      // 检查权限
      if (targetUserId !== userId) {
        throw new Error('无权获取其他用户健康建议');
      }
      
      // 获取用户健康资料
      const healthProfile = await healthProfileService.getHealthProfileByUserId(targetUserId);
      
      // 根据体质类型、类别和季节生成建议
      const category = params.category || 'all';
      const season = params.season || getCurrentSeason();
      
      // 这里应该有更复杂的逻辑来基于用户体质、季节等生成建议
      // 目前使用简化的演示数据
      const recommendations = {
        dietary: [
          { content: '多食用温性食物，如生姜、羊肉等', reason: '根据您的体质特点，需要温补阳气' },
          { content: '少食生冷瓜果，避免伤及脾胃', reason: '您的脾胃功能较弱，需避免寒凉食物' }
        ],
        lifestyle: [
          { content: '保持规律作息，避免熬夜', reason: '有助于阴阳平衡，改善体质' },
          { content: '适当进行温和运动，如太极、散步', reason: '增强体质，避免过度劳累' }
        ],
        herbal: [
          { content: '可适当服用人参、黄芪等补气类中药', reason: '补益元气，增强体质' },
          { content: '使用艾灸进行温补调理', reason: '温阳散寒，调和气血' }
        ]
      };
      
      // 根据请求的类别返回对应建议
      if (category !== 'all') {
        return { [category]: recommendations[category] };
      }
      
      return recommendations;
    } catch (error) {
      logger.error('执行get_health_recommendations工具失败', { 
        userId, 
        params, 
        error: error.message 
      });
      throw error;
    }
  },
  
  // 更新用户偏好设置
  update_user_preference: async (userId, params) => {
    try {
      // 如果没有提供用户ID，则使用当前用户
      const targetUserId = params.user_id || userId;
      // 检查权限
      if (targetUserId !== userId) {
        throw new Error('无权修改其他用户偏好设置');
      }
      
      // 获取要更新的偏好设置
      const preferences = params.preferences;
      if (!preferences || Object.keys(preferences).length === 0) {
        throw new Error('未提供偏好设置数据');
      }
      
      // 更新用户偏好设置
      // 这里应该有实际的存储逻辑
      
      return {
        success: true,
        message: '偏好设置已更新',
        updated_preferences: preferences
      };
    } catch (error) {
      logger.error('执行update_user_preference工具失败', { 
        userId, 
        params, 
        error: error.message 
      });
      throw error;
    }
  },
  
  // 获取用户成就状态
  get_achievement_status: async (userId, params) => {
    try {
      // 如果没有提供用户ID，则使用当前用户
      const targetUserId = params.user_id || userId;
      // 检查权限
      if (targetUserId !== userId) {
        throw new Error('无权访问其他用户成就状态');
      }
      
      // 获取成就类别
      const category = params.category || 'all';
      
      // 模拟成就数据（实际应从数据库获取）
      const achievements = {
        health_tracking: [
          { id: 'ht_001', name: '健康记录者', description: '连续7天记录健康数据', progress: 5, max: 7, completed: false },
          { id: 'ht_002', name: '健康达人', description: '连续30天记录健康数据', progress: 15, max: 30, completed: false },
          { id: 'ht_003', name: '数据专家', description: '记录所有类型的健康数据', progress: 8, max: 10, completed: false }
        ],
        learning: [
          { id: 'le_001', name: '知识探索者', description: '浏览10篇健康文章', progress: 10, max: 10, completed: true },
          { id: 'le_002', name: '中医学徒', description: '完成中医基础知识测验', progress: 1, max: 1, completed: true },
          { id: 'le_003', name: '草药专家', description: '学习30种常用中药', progress: 12, max: 30, completed: false }
        ],
        social: [
          { id: 'so_001', name: '社区新人', description: '参与社区讨论', progress: 1, max: 1, completed: true },
          { id: 'so_002', name: '社区贡献者', description: '回答10个健康问题', progress: 3, max: 10, completed: false }
        ],
        lifestyle: [
          { id: 'li_001', name: '早起达人', description: '连续7天早起', progress: 4, max: 7, completed: false },
          { id: 'li_002', name: '饮食均衡', description: '记录7天饮食数据', progress: 7, max: 7, completed: true }
        ],
        tcm_knowledge: [
          { id: 'tk_001', name: '体质入门', description: '完成体质测试', progress: 1, max: 1, completed: true },
          { id: 'tk_002', name: '穴位专家', description: '学习20个常用穴位', progress: 8, max: 20, completed: false }
        ]
      };
      
      // 按类别返回成就
      if (category !== 'all') {
        return { 
          category,
          achievements: achievements[category] || [],
          total: achievements[category]?.length || 0,
          completed: achievements[category]?.filter(a => a.completed).length || 0
        };
      }
      
      // 返回所有类别的成就统计
      const allAchievements = Object.values(achievements).flat();
      return {
        categories: Object.keys(achievements),
        total_achievements: allAchievements.length,
        completed_achievements: allAchievements.filter(a => a.completed).length,
        completion_rate: Math.round((allAchievements.filter(a => a.completed).length / allAchievements.length) * 100),
        category_stats: Object.keys(achievements).map(cat => ({
          category: cat,
          total: achievements[cat].length,
          completed: achievements[cat].filter(a => a.completed).length
        }))
      };
    } catch (error) {
      logger.error('执行get_achievement_status工具失败', { 
        userId, 
        params, 
        error: error.message 
      });
      throw error;
    }
  },
  
  // 获取用户可用优惠券
  get_vouchers: async (userId, params) => {
    try {
      // 如果没有提供用户ID，则使用当前用户
      const targetUserId = params.user_id || userId;
      // 检查权限
      if (targetUserId !== userId) {
        throw new Error('无权访问其他用户优惠券');
      }
      
      // 获取优惠券状态和类型过滤器
      const status = params.status || 'available';
      const type = params.type || 'all';
      
      // 模拟优惠券数据（实际应从数据库获取）
      const allVouchers = [
        {
          id: 'v001',
          name: '春季养生体验券',
          description: '可兑换一次春季养生体验服务',
          type: 'physical_service',
          discount_amount: null,
          discount_percentage: null,
          status: 'available',
          valid_from: '2023-03-01T00:00:00Z',
          valid_until: '2023-05-31T23:59:59Z',
          redemption_code: 'SPRING2023',
          terms_conditions: '仅限工作日使用，需提前预约'
        },
        {
          id: 'v002',
          name: '健康食品9折券',
          description: '购买健康食品可享9折优惠',
          type: 'product_discount',
          discount_amount: null,
          discount_percentage: 10,
          status: 'available',
          valid_from: '2023-04-01T00:00:00Z',
          valid_until: '2023-06-30T23:59:59Z',
          redemption_code: 'HEALTH10',
          terms_conditions: '单笔订单满100元可用'
        },
        {
          id: 'v003',
          name: '中医诊断体验券',
          description: '免费体验一次中医诊断服务',
          type: 'experience_ticket',
          discount_amount: null,
          discount_percentage: null,
          status: 'used',
          valid_from: '2023-02-01T00:00:00Z',
          valid_until: '2023-04-30T23:59:59Z',
          redemption_code: 'TCMEXP2023',
          terms_conditions: '仅限新用户使用',
          used_at: '2023-03-15T14:30:00Z'
        },
        {
          id: 'v004',
          name: '夏季清凉饮品券',
          description: '购买夏季特饮立减15元',
          type: 'product_discount',
          discount_amount: 15,
          discount_percentage: null,
          status: 'expired',
          valid_from: '2022-06-01T00:00:00Z',
          valid_until: '2022-08-31T23:59:59Z',
          redemption_code: 'SUMMER15',
          terms_conditions: '每用户限用一次'
        },
        {
          id: 'v005',
          name: '农场采摘体验券',
          description: '参与一次有机农场采摘活动',
          type: 'experience_ticket',
          discount_amount: null,
          discount_percentage: null,
          status: 'available',
          valid_from: '2023-05-01T00:00:00Z',
          valid_until: '2023-10-31T23:59:59Z',
          redemption_code: 'FARM2023',
          terms_conditions: '周末使用需提前3天预约'
        }
      ];
      
      // 根据状态和类型筛选优惠券
      let filteredVouchers = allVouchers;
      
      if (status !== 'all') {
        filteredVouchers = filteredVouchers.filter(v => v.status === status);
      }
      
      if (type !== 'all') {
        filteredVouchers = filteredVouchers.filter(v => v.type === type);
      }
      
      // 返回筛选后的优惠券
      return {
        total: filteredVouchers.length,
        vouchers: filteredVouchers,
        status_summary: {
          available: allVouchers.filter(v => v.status === 'available').length,
          used: allVouchers.filter(v => v.status === 'used').length,
          expired: allVouchers.filter(v => v.status === 'expired').length
        },
        type_summary: {
          physical_service: allVouchers.filter(v => v.type === 'physical_service').length,
          product_discount: allVouchers.filter(v => v.type === 'product_discount').length,
          experience_ticket: allVouchers.filter(v => v.type === 'experience_ticket').length
        }
      };
    } catch (error) {
      logger.error('执行get_vouchers工具失败', { 
        userId, 
        params, 
        error: error.message 
      });
      throw error;
    }
  }
};

// 执行工具函数
const executeToolFunction = async (functionName, userId, params) => {
  try {
    // 检查函数是否存在
    if (!toolFunctions[functionName]) {
      throw new Error(`未找到工具函数: ${functionName}`);
    }
    
    // 执行工具函数
    return await toolFunctions[functionName](userId, params);
  } catch (error) {
    logger.error('工具函数执行失败', { 
      functionName, 
      userId, 
      params, 
      error: error.message 
    });
    throw error;
  }
};

// 获取当前季节
const getCurrentSeason = () => {
  const month = new Date().getMonth() + 1;
  if (month >= 3 && month <= 5) return '春季';
  if (month >= 6 && month <= 8) return '夏季';
  if (month >= 9 && month <= 11) return '秋季';
  return '冬季';
};

// 获取可用工具列表
exports.listTools = async (userId) => {
  const tools = loadToolsConfig();
  return {
    object: 'list',
    data: tools,
    has_more: false,
    first_id: tools.length > 0 ? '1' : null,
    last_id: tools.length > 0 ? String(tools.length) : null,
    total_count: tools.length
  };
};

// 执行工具函数
exports.executeFunction = async (userId, functionName, params) => {
  try {
    const result = await executeToolFunction(functionName, userId, params);
    return {
      object: 'function_execution',
      id: `fe_${uuidv4()}`,
      function_name: functionName,
      status: 'success',
      result: JSON.stringify(result)
    };
  } catch (error) {
    return {
      object: 'function_execution',
      id: `fe_${uuidv4()}`,
      function_name: functionName,
      status: 'error',
      error: {
        message: error.message,
        code: 'function_execution_error'
      }
    };
  }
};

// 提供OpenAI API兼容的工具接口
// 这部分根据实际情况扩展
exports.listAssistants = async (userId, params) => {
  // 实际实现应该查询用户的助手列表
  return {
    object: 'list',
    data: [],
    has_more: false,
    first_id: null,
    last_id: null
  };
};

exports.createAssistant = async (userId, data) => {
  // 实际实现应该创建一个新助手
  return {
    object: 'assistant',
    id: `asst_${uuidv4()}`,
    created_at: Math.floor(Date.now() / 1000),
    name: data.name || null,
    description: data.description || null,
    model: data.model || 'gpt-3.5-turbo',
    instructions: data.instructions || null,
    tools: data.tools || [],
    metadata: data.metadata || {}
  };
}; 
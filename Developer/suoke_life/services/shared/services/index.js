/**
 * 共享服务模块索引
 * 集成所有共享服务功能
 */

const dialectService = require('./dialect');

/**
 * 共享服务集合
 */
const sharedServices = {
  // 方言服务 - 提供方言样本收集、模型训练和识别/翻译功能
  dialect: dialectService,
  
  // 其他共享服务可在此添加
};

module.exports = sharedServices;
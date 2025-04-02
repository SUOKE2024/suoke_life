/**
 * 索克生活共享模块
 * 为微服务架构提供共享的工具、模型、中间件和配置
 * @version 1.1.0
 */

// 导入子模块
const models = require('./models');
const utils = require('./utils');
const middlewares = require('./middlewares');
const config = require('./config');
const constants = require('./constants');

// 导出所有模块
module.exports = {
  models,
  utils,
  middlewares,
  config,
  constants
};

// 如果直接运行此文件，则显示模块信息
if (require.main === module) {
  console.log('\n索克生活共享模块');
  console.log('版本: 1.1.0');
  console.log('描述: 为微服务架构提供共享的工具、模型、中间件和配置');
  console.log('\n可用模块:');
  console.log('- models: 数据模型');
  console.log('- utils: 工具函数');
  console.log('- middlewares: 中间件');
  console.log('- config: 配置');
  console.log('- constants: 常量定义\n');
} 
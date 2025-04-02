/**
 * 控制器索引文件
 */
const userController = require('./user.controller');
const profileController = require('./profile.controller');
const healthProfileController = require('./health-profile.controller');
const openaiController = require('./openai.controller');
const openaiToolsController = require('./openai-tools.controller');
const knowledgePreferenceController = require('./knowledge-preference.controller');
const recommendationController = require('./recommendation.controller');

module.exports = {
  userController,
  profileController,
  healthProfileController,
  openaiController,
  openaiToolsController,
  knowledgePreferenceController,
  recommendationController
}; 
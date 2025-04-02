/**
 * 服务索引文件
 */
const userService = require('./user.service');
const profileService = require('./profile.service');
const healthProfileService = require('./health-profile.service');
const sessionService = require('./session.service');
const openaiService = require('./openai.service');
const knowledgePreferenceService = require('./knowledge-preference.service');
const recommendationService = require('./recommendation.service');

module.exports = {
  userService,
  profileService,
  healthProfileService,
  sessionService,
  openaiService,
  knowledgePreferenceService,
  recommendationService
}; 
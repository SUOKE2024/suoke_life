/**
 * 存储库索引文件
 */
const userRepository = require('./user.repository');
const profileRepository = require('./profile.repository');
const healthProfileRepository = require('./health-profile.repository');
const knowledgePreferenceRepository = require('./knowledge-preference.repository');
const recommendationRepository = require('./recommendation.repository');

module.exports = {
  userRepository,
  profileRepository,
  healthProfileRepository,
  knowledgePreferenceRepository,
  recommendationRepository
}; 
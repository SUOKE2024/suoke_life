/**
 * 推荐反馈相关表结构迁移文件
 */
const knowledgePreferenceModel = require('../models/knowledge-preference.model');

exports.up = function(knex) {
  return knex.schema
    .raw(knowledgePreferenceModel.recommendationFeedbackTableStructure);
};

exports.down = function(knex) {
  return knex.schema
    .dropTableIfExists('user_recommendation_feedback');
};
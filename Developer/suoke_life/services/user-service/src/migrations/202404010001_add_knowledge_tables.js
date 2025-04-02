/**
 * 知识相关表迁移文件
 */
const knowledgePreferenceModel = require('../models/knowledge-preference.model');

exports.up = function(knex) {
  return knex.schema
    .raw(knowledgePreferenceModel.tableStructure)
    .raw(knowledgePreferenceModel.viewHistoryTableStructure)
    .raw(knowledgePreferenceModel.favoritesTableStructure)
    .raw(knowledgePreferenceModel.knowledgeGraphInteractionTableStructure);
};

exports.down = function(knex) {
  return knex.schema
    .dropTableIfExists('user_knowledge_graph_interactions')
    .dropTableIfExists('user_content_favorites')
    .dropTableIfExists('user_content_view_history')
    .dropTableIfExists('user_knowledge_preferences');
};
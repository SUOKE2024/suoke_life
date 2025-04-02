/**
 * 用户兴趣匹配表结构迁移文件
 */
const userMatchingModel = require('../models/user-matching.model');

exports.up = function(knex) {
  return knex.schema
    .raw(userMatchingModel.tableStructure)
    .raw(userMatchingModel.matchInteractionsTableStructure)
    .raw(userMatchingModel.userInterestVectorsTableStructure);
};

exports.down = function(knex) {
  return knex.schema
    .dropTableIfExists('user_match_interactions')
    .dropTableIfExists('user_interest_vectors')
    .dropTableIfExists(userMatchingModel.TABLE_NAME);
};
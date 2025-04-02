/**
 * 用户匹配相关表结构迁移文件
 */
const userMatchModel = require('../models/user-match.model');

exports.up = function(knex) {
  return knex.schema
    .raw(userMatchModel.tableStructure)
    .raw(userMatchModel.userConnectionTableStructure)
    .raw(userMatchModel.userInterestVectorTableStructure);
};

exports.down = function(knex) {
  return knex.schema
    .dropTableIfExists('user_interest_vectors')
    .dropTableIfExists('user_connections')
    .dropTableIfExists(userMatchModel.TABLE_NAME);
};
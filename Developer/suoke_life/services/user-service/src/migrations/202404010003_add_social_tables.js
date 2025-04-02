/**
 * 社交分享表结构迁移文件
 */
const socialShareModel = require('../models/social-share.model');

exports.up = function(knex) {
  return knex.schema
    .raw(socialShareModel.tableStructure)
    .raw(socialShareModel.shareStatsTableStructure)
    .raw(socialShareModel.shareInteractionsTableStructure);
};

exports.down = function(knex) {
  return knex.schema
    .dropTableIfExists('social_share_interactions')
    .dropTableIfExists('social_share_stats')
    .dropTableIfExists(socialShareModel.TABLE_NAME);
};
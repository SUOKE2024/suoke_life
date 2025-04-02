/**
 * 社交分享相关表结构迁移文件
 */
const socialShareModel = require('../models/social-share.model');

exports.up = function(knex) {
  return knex.schema
    .raw(socialShareModel.tableStructure)
    .raw(socialShareModel.shareInteractionTableStructure);
};

exports.down = function(knex) {
  return knex.schema
    .dropTableIfExists('social_share_interactions')
    .dropTableIfExists(socialShareModel.TABLE_NAME);
};
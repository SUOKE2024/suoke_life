/**
 * 数据模型索引
 * 导出所有数据模型
 */

// 导入模型
const User = require('./user.model');
const Profile = require('./profile.model');

// 健康相关模型
const HealthRecordModel = require('./health-record.model');
const ConstitutionModel = require('./constitution.model');

// 知识相关模型
const KnowledgeNodeModel = require('./knowledge-node.model');
const KnowledgeRelationModel = require('./knowledge-relation.model');

/**
 * 导出所有模型
 */
module.exports = {
  User,
  Profile,
  HealthRecordModel,
  ConstitutionModel,
  KnowledgeNodeModel,
  KnowledgeRelationModel
}; 
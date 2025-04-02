/**
 * 工具模块索引
 * 导出所有工具模块
 */
const metrics = require('./metrics');
const db = require('./db');
const encryption = require('./encryption');
const i18n = require('./i18n');
const i18nTools = require('./i18n-tools');
const { cacheService } = require('./cache-service');
const { logger, createLogger } = require('./logger');

module.exports = {
  metrics,
  db,
  encryption,
  i18n,
  i18nTools,
  cacheService,
  logger,
  createLogger
}; 
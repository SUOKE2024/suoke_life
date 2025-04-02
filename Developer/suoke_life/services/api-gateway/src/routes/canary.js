/**
 * 灰度发布管理路由
 */

const express = require('express');
const router = express.Router();
const { getCanaryConfig, setCanaryConfig, getAllCanaryConfigs } = require('../middlewares/canary-router');
const logger = require('../utils/logger');

/**
 * 获取所有灰度发布配置
 * GET /api/canary
 */
router.get('/', (req, res) => {
  const configs = getAllCanaryConfigs();
  res.json({
    status: 'success',
    data: configs
  });
});

/**
 * 获取特定服务的灰度发布配置
 * GET /api/canary/:serviceName
 */
router.get('/:serviceName', (req, res) => {
  const { serviceName } = req.params;
  const config = getCanaryConfig(serviceName);
  
  if (!config) {
    return res.status(404).json({
      status: 'error',
      message: `未找到服务 ${serviceName} 的灰度发布配置`
    });
  }
  
  res.json({
    status: 'success',
    data: {
      serviceName: config.serviceName,
      enabled: config.enabled,
      versions: config.versions,
      defaultVersion: config.defaultVersion,
      rules: config.rules,
      metrics: config.getMetrics()
    }
  });
});

/**
 * 创建或更新灰度发布配置
 * PUT /api/canary/:serviceName
 */
router.put('/:serviceName', (req, res) => {
  const { serviceName } = req.params;
  const options = req.body;
  
  try {
    // 基础参数验证
    if (options.versions && !Array.isArray(options.versions)) {
      return res.status(400).json({
        status: 'error',
        message: 'versions必须是数组'
      });
    }
    
    if (options.rules && !Array.isArray(options.rules)) {
      return res.status(400).json({
        status: 'error',
        message: 'rules必须是数组'
      });
    }
    
    // 验证版本配置
    if (options.versions) {
      for (const version of options.versions) {
        if (!version.name || !version.url) {
          return res.status(400).json({
            status: 'error',
            message: '每个版本必须包含name和url属性'
          });
        }
      }
    }
    
    // 更新配置
    const config = setCanaryConfig(serviceName, options);
    
    logger.info(`已更新服务 ${serviceName} 的灰度发布配置，已${config.enabled ? '启用' : '禁用'}`);
    
    res.json({
      status: 'success',
      message: `成功更新 ${serviceName} 灰度发布配置`,
      data: {
        serviceName: config.serviceName,
        enabled: config.enabled,
        versions: config.versions,
        defaultVersion: config.defaultVersion,
        rules: config.rules
      }
    });
  } catch (error) {
    logger.error(`更新灰度发布配置失败: ${error.message}`);
    res.status(500).json({
      status: 'error',
      message: '更新灰度发布配置失败',
      error: process.env.NODE_ENV === 'production' ? undefined : error.message
    });
  }
});

/**
 * 启用/禁用灰度发布
 * PATCH /api/canary/:serviceName/toggle
 */
router.patch('/:serviceName/toggle', (req, res) => {
  const { serviceName } = req.params;
  const { enabled } = req.body;
  
  if (typeof enabled !== 'boolean') {
    return res.status(400).json({
      status: 'error',
      message: 'enabled参数必须是布尔值'
    });
  }
  
  try {
    const config = getCanaryConfig(serviceName);
    // 只更新enabled状态
    const updatedConfig = setCanaryConfig(serviceName, { 
      ...config, 
      enabled 
    });
    
    logger.info(`服务 ${serviceName} 的灰度发布已${enabled ? '启用' : '禁用'}`);
    
    res.json({
      status: 'success',
      message: `已${enabled ? '启用' : '禁用'} ${serviceName} 的灰度发布`,
      data: { enabled: updatedConfig.enabled }
    });
  } catch (error) {
    logger.error(`切换灰度发布状态失败: ${error.message}`);
    res.status(500).json({
      status: 'error',
      message: '切换灰度发布状态失败',
      error: process.env.NODE_ENV === 'production' ? undefined : error.message
    });
  }
});

/**
 * 重置服务的灰度发布指标
 * POST /api/canary/:serviceName/reset-metrics
 */
router.post('/:serviceName/reset-metrics', (req, res) => {
  const { serviceName } = req.params;
  
  try {
    const config = getCanaryConfig(serviceName);
    config.resetMetrics();
    
    logger.info(`已重置服务 ${serviceName} 的灰度发布指标`);
    
    res.json({
      status: 'success',
      message: `已重置 ${serviceName} 的灰度发布指标`
    });
  } catch (error) {
    logger.error(`重置灰度发布指标失败: ${error.message}`);
    res.status(500).json({
      status: 'error',
      message: '重置灰度发布指标失败',
      error: process.env.NODE_ENV === 'production' ? undefined : error.message
    });
  }
});

/**
 * 添加路由规则
 * POST /api/canary/:serviceName/rules
 */
router.post('/:serviceName/rules', (req, res) => {
  const { serviceName } = req.params;
  const rule = req.body;
  
  try {
    // 验证规则
    if (!rule.type) {
      return res.status(400).json({
        status: 'error',
        message: '规则必须包含type属性'
      });
    }
    
    if (!rule.targetVersion) {
      return res.status(400).json({
        status: 'error',
        message: '规则必须包含targetVersion属性'
      });
    }
    
    const config = getCanaryConfig(serviceName);
    const newRules = [...config.rules, rule];
    
    // 更新配置
    const updatedConfig = setCanaryConfig(serviceName, {
      ...config,
      rules: newRules
    });
    
    logger.info(`已向服务 ${serviceName} 添加新的灰度发布规则`);
    
    res.json({
      status: 'success',
      message: '成功添加规则',
      data: {
        rules: updatedConfig.rules
      }
    });
  } catch (error) {
    logger.error(`添加灰度发布规则失败: ${error.message}`);
    res.status(500).json({
      status: 'error',
      message: '添加灰度发布规则失败',
      error: process.env.NODE_ENV === 'production' ? undefined : error.message
    });
  }
});

/**
 * 删除路由规则
 * DELETE /api/canary/:serviceName/rules/:ruleIndex
 */
router.delete('/:serviceName/rules/:ruleIndex', (req, res) => {
  const { serviceName, ruleIndex } = req.params;
  const index = parseInt(ruleIndex, 10);
  
  if (isNaN(index) || index < 0) {
    return res.status(400).json({
      status: 'error',
      message: '无效的规则索引'
    });
  }
  
  try {
    const config = getCanaryConfig(serviceName);
    
    if (index >= config.rules.length) {
      return res.status(404).json({
        status: 'error',
        message: '规则不存在'
      });
    }
    
    // 移除规则
    const newRules = [...config.rules];
    newRules.splice(index, 1);
    
    // 更新配置
    const updatedConfig = setCanaryConfig(serviceName, {
      ...config,
      rules: newRules
    });
    
    logger.info(`已从服务 ${serviceName} 删除灰度发布规则`);
    
    res.json({
      status: 'success',
      message: '成功删除规则',
      data: {
        rules: updatedConfig.rules
      }
    });
  } catch (error) {
    logger.error(`删除灰度发布规则失败: ${error.message}`);
    res.status(500).json({
      status: 'error',
      message: '删除灰度发布规则失败',
      error: process.env.NODE_ENV === 'production' ? undefined : error.message
    });
  }
});

module.exports = router; 
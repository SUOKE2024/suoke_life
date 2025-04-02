/**
 * 安全控制面板控制器
 */
const { security } = require('../services');
const securityLogService = require('../services/security-log.service');
const deviceService = require('../services/device.service');
const sessionService = require('../services/session.service');
const { ResponseTemplate } = require('@suoke/shared').utils;
const securityConfig = require('../config/security');

/**
 * 渲染安全控制面板
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const renderDashboard = async (req, res) => {
  try {
    res.render('security-dashboard');
  } catch (error) {
    res.status(500).send('渲染安全控制面板失败');
  }
};

/**
 * 获取安全统计数据
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getSecurityStats = async (req, res) => {
  try {
    // 获取安全评分
    const securityScore = await calculateSecurityScore();
    
    // 获取活跃警报数量
    const activeAlerts = await getActiveAlerts();
    
    // 获取活跃设备数量
    const activeDevicesCount = await deviceService.getActiveDevicesCount();
    
    // 获取活跃会话数量
    const activeSessionsCount = await sessionService.getActiveSessionsCount();
    
    return ResponseTemplate.success(res, {
      securityScore,
      activeAlerts: activeAlerts.count,
      activeDevices: activeDevicesCount,
      activeSessions: activeSessionsCount
    });
  } catch (error) {
    return ResponseTemplate.internalServerError(res, '获取安全统计数据失败', error);
  }
};

/**
 * 获取安全活动图表数据
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getSecurityChartData = async (req, res) => {
  try {
    const { timeRange = '30d' } = req.query;
    
    // 计算日期范围
    const endDate = new Date();
    const startDate = new Date();
    
    switch (timeRange) {
      case '7d':
        startDate.setDate(endDate.getDate() - 7);
        break;
      case '90d':
        startDate.setDate(endDate.getDate() - 90);
        break;
      default: // 30d
        startDate.setDate(endDate.getDate() - 30);
    }
    
    // 获取安全事件数据
    const successfulLogins = await getEventCountByDateRange(
      securityConfig.SECURITY_EVENT_TYPES.LOGIN_SUCCESS,
      startDate,
      endDate
    );
    
    const failedLogins = await getEventCountByDateRange(
      securityConfig.SECURITY_EVENT_TYPES.LOGIN_FAILED,
      startDate,
      endDate
    );
    
    const suspiciousActivities = await getEventCountByDateRange(
      securityConfig.SECURITY_EVENT_TYPES.SUSPICIOUS_ACTIVITY,
      startDate,
      endDate
    );
    
    // 生成日期标签
    const labels = generateDateLabels(startDate, endDate);
    
    return ResponseTemplate.success(res, {
      labels,
      datasets: [
        {
          label: '成功登录',
          data: successfulLogins
        },
        {
          label: '失败尝试',
          data: failedLogins
        },
        {
          label: '可疑活动',
          data: suspiciousActivities
        }
      ]
    });
  } catch (error) {
    return ResponseTemplate.internalServerError(res, '获取安全活动图表数据失败', error);
  }
};

/**
 * 获取最近登录活动
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getRecentLoginActivities = async (req, res) => {
  try {
    const { limit = 10 } = req.query;
    
    // 获取登录活动
    const loginEvents = await securityLogService.getRecentEvents([
      securityConfig.SECURITY_EVENT_TYPES.LOGIN_SUCCESS,
      securityConfig.SECURITY_EVENT_TYPES.LOGIN_FAILED
    ], { limit: parseInt(limit) });
    
    // 格式化数据
    const activities = await Promise.all(loginEvents.map(async (event) => {
      const deviceInfo = event.deviceInfo ? 
        (typeof event.deviceInfo === 'string' ? JSON.parse(event.deviceInfo) : event.deviceInfo) : 
        { name: '未知设备' };
      
      return {
        userId: event.userId,
        timestamp: event.timestamp,
        ipAddress: event.ipAddress || '未知IP',
        device: deviceInfo.name || deviceInfo.deviceName || '未知设备',
        status: event.type === securityConfig.SECURITY_EVENT_TYPES.LOGIN_SUCCESS ? 'success' : 'failed',
        eventType: event.type,
        details: event
      };
    }));
    
    return ResponseTemplate.success(res, activities);
  } catch (error) {
    return ResponseTemplate.internalServerError(res, '获取最近登录活动失败', error);
  }
};

/**
 * 获取异常活动
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getAnomalies = async (req, res) => {
  try {
    const { limit = 5 } = req.query;
    
    // 获取异常事件
    const anomalyEvents = await securityLogService.getRecentEvents([
      securityConfig.SECURITY_EVENT_TYPES.SUSPICIOUS_ACTIVITY,
      securityConfig.SECURITY_EVENT_TYPES.UNUSUAL_LOCATION_ACCESS,
      securityConfig.SECURITY_EVENT_TYPES.UNUSUAL_BEHAVIOR,
      securityConfig.SECURITY_EVENT_TYPES.MULTIPLE_FAILED_ATTEMPTS,
      securityConfig.SECURITY_EVENT_TYPES.BRUTE_FORCE_ATTEMPT
    ], { limit: parseInt(limit) });
    
    // 格式化数据
    const anomalies = anomalyEvents.map((event) => {
      let message = '检测到可疑活动';
      let riskLevel = 'medium';
      
      // 根据事件类型设置消息和风险级别
      switch (event.type) {
        case securityConfig.SECURITY_EVENT_TYPES.UNUSUAL_LOCATION_ACCESS:
          message = '非典型登录位置';
          riskLevel = 'medium';
          break;
        case securityConfig.SECURITY_EVENT_TYPES.MULTIPLE_FAILED_ATTEMPTS:
          message = '多次失败的登录尝试';
          riskLevel = 'high';
          break;
        case securityConfig.SECURITY_EVENT_TYPES.BRUTE_FORCE_ATTEMPT:
          message = '检测到暴力破解尝试';
          riskLevel = 'high';
          break;
        case securityConfig.SECURITY_EVENT_TYPES.UNUSUAL_BEHAVIOR:
          message = '检测到异常行为';
          riskLevel = 'medium';
          break;
      }
      
      return {
        id: event.id,
        message,
        details: `用户${event.userId}，IP地址：${event.ipAddress || '未知'}`,
        timestamp: event.timestamp,
        riskLevel,
        eventType: event.type,
        raw: event
      };
    });
    
    return ResponseTemplate.success(res, {
      count: anomalies.length,
      anomalies
    });
  } catch (error) {
    return ResponseTemplate.internalServerError(res, '获取异常活动失败', error);
  }
};

/**
 * 获取活跃设备列表
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getActiveDevices = async (req, res) => {
  try {
    const { limit = 5 } = req.query;
    
    // 获取活跃设备
    const devices = await deviceService.getRecentActiveDevices(parseInt(limit));
    
    // 格式化数据
    const activeDevices = devices.map((device) => {
      return {
        id: device.id,
        name: device.name || '未知设备',
        userId: device.userId,
        status: device.lastActivityAt && (new Date() - new Date(device.lastActivityAt) < 24 * 60 * 60 * 1000) 
          ? 'active' 
          : 'inactive',
        trusted: device.isTrusted,
        lastActivityAt: device.lastActivityAt,
        type: device.type || 'unknown'
      };
    });
    
    return ResponseTemplate.success(res, activeDevices);
  } catch (error) {
    return ResponseTemplate.internalServerError(res, '获取活跃设备列表失败', error);
  }
};

/**
 * 获取安全建议
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getSecurityRecommendations = async (req, res) => {
  try {
    // 进行安全评估并生成建议
    const recommendations = await generateSecurityRecommendations();
    
    return ResponseTemplate.success(res, recommendations);
  } catch (error) {
    return ResponseTemplate.internalServerError(res, '获取安全建议失败', error);
  }
};

/**
 * 计算安全评分
 * @private
 * @returns {Promise<number>} 安全评分
 */
const calculateSecurityScore = async () => {
  // 这里应该实现安全评分的逻辑
  // 示例实现
  return 85;
};

/**
 * 获取活跃警报
 * @private
 * @returns {Promise<Object>} 警报信息
 */
const getActiveAlerts = async () => {
  // 示例实现
  return {
    count: 12,
    alerts: []
  };
};

/**
 * 按日期范围获取事件计数
 * @private
 * @param {string} eventType 事件类型
 * @param {Date} startDate 开始日期
 * @param {Date} endDate 结束日期
 * @returns {Promise<Array<number>>} 事件计数数组
 */
const getEventCountByDateRange = async (eventType, startDate, endDate) => {
  // 示例实现
  return Array(getDateDifference(startDate, endDate) + 1).fill(0).map(() => 
    Math.floor(Math.random() * 100)
  );
};

/**
 * 生成日期范围的标签
 * @private
 * @param {Date} startDate 开始日期
 * @param {Date} endDate 结束日期
 * @returns {Array<string>} 日期标签数组
 */
const generateDateLabels = (startDate, endDate) => {
  const labels = [];
  const currentDate = new Date(startDate);
  
  while (currentDate <= endDate) {
    labels.push(formatDateLabel(currentDate));
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return labels;
};

/**
 * 格式化日期标签
 * @private
 * @param {Date} date 日期
 * @returns {string} 格式化的日期
 */
const formatDateLabel = (date) => {
  return `${date.getMonth() + 1}/${date.getDate()}`;
};

/**
 * 获取两个日期之间的天数差
 * @private
 * @param {Date} startDate 开始日期
 * @param {Date} endDate 结束日期
 * @returns {number} 天数差
 */
const getDateDifference = (startDate, endDate) => {
  return Math.round((endDate - startDate) / (1000 * 60 * 60 * 24));
};

/**
 * 生成安全建议
 * @private
 * @returns {Promise<Array<Object>>} 安全建议
 */
const generateSecurityRecommendations = async () => {
  // 示例实现
  return [
    {
      id: '1',
      title: '更新设备识别算法',
      description: '当前版本存在碰撞风险',
      severity: 'warning'
    },
    {
      id: '2',
      title: '提高恢复码安全性',
      description: '建议增加恢复码长度',
      severity: 'warning'
    },
    {
      id: '3',
      title: '双因素认证配置良好',
      description: '当前设置符合安全标准',
      severity: 'good'
    }
  ];
};

module.exports = {
  renderDashboard,
  getSecurityStats,
  getSecurityChartData,
  getRecentLoginActivities,
  getAnomalies,
  getActiveDevices,
  getSecurityRecommendations
};
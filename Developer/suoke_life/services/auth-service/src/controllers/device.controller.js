/**
 * 设备管理控制器
 */
const deviceService = require('../services/device.service');
const { logger } = require('@suoke/shared').utils;

/**
 * 获取用户设备列表
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getUserDevices = async (req, res, next) => {
  try {
    const userId = req.user.id;
    
    const devices = await deviceService.getUserDevices(userId);
    
    res.json({
      success: true,
      data: {
        devices,
        currentDeviceId: req.headers['x-device-id'] || null
      }
    });
  } catch (error) {
    logger.error(`获取用户设备列表失败: ${error.message}`, { error, userId: req.user?.id });
    next(error);
  }
};

/**
 * 删除用户设备
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const removeDevice = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { deviceId } = req.params;
    
    if (!deviceId) {
      return res.status(400).json({
        success: false,
        message: '缺少设备ID',
        code: 'device/missing-id'
      });
    }
    
    // 检查是否是当前设备
    const currentDeviceId = req.headers['x-device-id'];
    if (currentDeviceId && currentDeviceId === deviceId) {
      return res.status(400).json({
        success: false,
        message: '不能删除当前正在使用的设备',
        code: 'device/cannot-remove-current'
      });
    }
    
    await deviceService.removeDevice(userId, deviceId);
    
    res.json({
      success: true,
      message: '设备已删除'
    });
  } catch (error) {
    logger.error(`删除设备失败: ${error.message}`, { error, userId: req.user?.id });
    
    if (error.message.includes('设备不存在或不属于该用户')) {
      return res.status(404).json({
        success: false,
        message: '设备不存在或不属于该用户',
        code: 'device/not-found'
      });
    }
    
    next(error);
  }
};

/**
 * 信任设备
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const trustDevice = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { deviceId } = req.params;
    
    if (!deviceId) {
      return res.status(400).json({
        success: false,
        message: '缺少设备ID',
        code: 'device/missing-id'
      });
    }
    
    await deviceService.trustDevice(userId, deviceId);
    
    res.json({
      success: true,
      message: '设备已标记为可信任'
    });
  } catch (error) {
    logger.error(`信任设备失败: ${error.message}`, { error, userId: req.user?.id });
    
    if (error.message.includes('设备不存在或不属于该用户')) {
      return res.status(404).json({
        success: false,
        message: '设备不存在或不属于该用户',
        code: 'device/not-found'
      });
    }
    
    next(error);
  }
};

/**
 * 取消信任设备
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const untrustDevice = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { deviceId } = req.params;
    
    if (!deviceId) {
      return res.status(400).json({
        success: false,
        message: '缺少设备ID',
        code: 'device/missing-id'
      });
    }
    
    await deviceService.untrustDevice(userId, deviceId);
    
    res.json({
      success: true,
      message: '设备已取消信任'
    });
  } catch (error) {
    logger.error(`取消信任设备失败: ${error.message}`, { error, userId: req.user?.id });
    
    if (error.message.includes('设备不存在或不属于该用户')) {
      return res.status(404).json({
        success: false,
        message: '设备不存在或不属于该用户',
        code: 'device/not-found'
      });
    }
    
    next(error);
  }
};

module.exports = {
  getUserDevices,
  removeDevice,
  trustDevice,
  untrustDevice
}; 
/**
 * 设备验证控制器
 * 处理设备验证相关的API请求
 */
const { security } = require('../services');
const { ResponseTemplate } = require('@suoke/shared').utils;

/**
 * 验证设备验证码
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @returns {Promise<Object>} 响应
 */
const verifyDeviceCode = async (req, res) => {
  try {
    const { verificationId, code } = req.body;

    if (!verificationId || !code) {
      return ResponseTemplate.badRequest(res, '验证ID和验证码不能为空');
    }

    const result = await security.verifyDevice(verificationId, code);

    if (result.verified) {
      return ResponseTemplate.success(res, {
        verified: true,
        deviceId: result.deviceId,
        message: '设备验证成功'
      });
    } else {
      return ResponseTemplate.badRequest(res, result.message || '验证失败', {
        verified: false,
        reason: result.reason
      });
    }
  } catch (error) {
    return ResponseTemplate.internalServerError(res, '设备验证过程中发生错误', error);
  }
};

/**
 * 重新发送验证码
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @returns {Promise<Object>} 响应
 */
const resendVerificationCode = async (req, res) => {
  try {
    const { verificationId } = req.body;

    if (!verificationId) {
      return ResponseTemplate.badRequest(res, '验证ID不能为空');
    }

    const result = await security.deviceVerification.resendVerificationCode(verificationId);

    if (result.sent) {
      return ResponseTemplate.success(res, {
        sent: true,
        method: result.method,
        maskedDestination: result.maskedDestination,
        message: '验证码已重新发送'
      });
    } else {
      return ResponseTemplate.badRequest(res, result.message || '发送验证码失败', {
        sent: false,
        reason: result.reason
      });
    }
  } catch (error) {
    return ResponseTemplate.internalServerError(res, '重新发送验证码过程中发生错误', error);
  }
};

/**
 * 使用备用方法验证设备
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @returns {Promise<Object>} 响应
 */
const verifyWithAlternativeMethod = async (req, res) => {
  try {
    const { verificationId, method } = req.body;

    if (!verificationId || !method) {
      return ResponseTemplate.badRequest(res, '验证ID和验证方法不能为空');
    }

    const result = await security.deviceVerification.switchVerificationMethod(verificationId, method);

    if (result.switched) {
      return ResponseTemplate.success(res, {
        switched: true,
        method: result.method,
        maskedDestination: result.maskedDestination,
        message: '验证方法已切换'
      });
    } else {
      return ResponseTemplate.badRequest(res, result.message || '切换验证方法失败', {
        switched: false,
        reason: result.reason
      });
    }
  } catch (error) {
    return ResponseTemplate.internalServerError(res, '切换验证方法过程中发生错误', error);
  }
};

/**
 * 使用恢复码验证设备
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @returns {Promise<Object>} 响应
 */
const verifyWithRecoveryCode = async (req, res) => {
  try {
    const { verificationId, recoveryCode } = req.body;

    if (!verificationId || !recoveryCode) {
      return ResponseTemplate.badRequest(res, '验证ID和恢复码不能为空');
    }

    const result = await security.deviceVerification.verifyWithRecoveryCode(verificationId, recoveryCode);

    if (result.verified) {
      return ResponseTemplate.success(res, {
        verified: true,
        deviceId: result.deviceId,
        message: '使用恢复码验证成功'
      });
    } else {
      return ResponseTemplate.badRequest(res, result.message || '恢复码验证失败', {
        verified: false,
        reason: result.reason
      });
    }
  } catch (error) {
    return ResponseTemplate.internalServerError(res, '使用恢复码验证过程中发生错误', error);
  }
};

module.exports = {
  verifyDeviceCode,
  resendVerificationCode,
  verifyWithAlternativeMethod,
  verifyWithRecoveryCode
};
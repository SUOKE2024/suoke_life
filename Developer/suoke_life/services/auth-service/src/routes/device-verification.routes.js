/**
 * 设备验证路由
 * 处理设备验证相关的路由
 */
const express = require('express');
const router = express.Router();
const deviceVerificationController = require('../controllers/device-verification.controller');
const { ApiRateLimit } = require('@suoke/shared').middlewares;

// 创建专门的速率限制器，防止暴力破解设备验证
const verificationLimiter = ApiRateLimit.createLimiter({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 10, // 15分钟内最多10次尝试
  message: {
    status: 'error',
    code: 429,
    message: '验证尝试次数过多，请稍后再试'
  },
  keyGenerator: (req) => {
    // 基于验证ID或IP来限制
    return req.body.verificationId || req.ip;
  }
});

// 设备验证码验证
router.post('/verify', verificationLimiter, deviceVerificationController.verifyDeviceCode);

// 重新发送验证码
router.post('/resend', ApiRateLimit.createLimiter({
  windowMs: 60 * 1000, // 1分钟
  max: 3, // 1分钟内最多3次请求
  message: {
    status: 'error',
    code: 429,
    message: '请求过于频繁，请稍后再试'
  }
}), deviceVerificationController.resendVerificationCode);

// 切换验证方法
router.post('/switch-method', ApiRateLimit.createLimiter({
  windowMs: 5 * 60 * 1000, // 5分钟
  max: 5, // 5分钟内最多5次切换
  message: {
    status: 'error',
    code: 429,
    message: '切换验证方法次数过多，请稍后再试'
  }
}), deviceVerificationController.verifyWithAlternativeMethod);

// 使用恢复码验证
router.post('/recovery', verificationLimiter, deviceVerificationController.verifyWithRecoveryCode);

module.exports = router;
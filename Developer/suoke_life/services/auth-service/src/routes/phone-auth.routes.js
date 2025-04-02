/**
 * 手机验证码登录路由
 */
const express = require('express');
const router = express.Router();
const phoneAuthService = require('../services/phone-auth.service');
const { validateSchema } = require('../middlewares/validation');
const { rateLimit } = require('../middlewares/rate-limit');
const authMiddleware = require('../middlewares/auth');
const { getClientInfo } = require('../utils/request-utils');
const logger = require('../utils/logger');

// 手机号验证schema
const phoneVerificationSchema = {
  phoneNumber: {
    notEmpty: { errorMessage: '手机号不能为空' },
    matches: {
      options: /^1[3-9]\d{9}$/,
      errorMessage: '手机号格式不正确'
    }
  }
};

// 手机验证码验证schema
const phoneCodeSchema = {
  ...phoneVerificationSchema,
  code: {
    notEmpty: { errorMessage: '验证码不能为空' },
    isLength: {
      options: { min: 4, max: 8 },
      errorMessage: '验证码长度不正确'
    },
    isNumeric: { errorMessage: '验证码只能是数字' }
  }
};

// 速率限制配置
const codeSendLimit = rateLimit({
  windowMs: 24 * 60 * 60 * 1000, // 24小时
  max: 20, // 每个IP限制请求20次
  message: '发送请求过于频繁，请24小时后再试',
  keyGenerator: (req) => req.body.phoneNumber || req.ip,
});

const verifyCodeLimit = rateLimit({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 10, // 每个IP限制请求10次
  message: '验证请求过于频繁，请15分钟后再试',
});

/**
 * 发送登录验证码
 * @route POST /phone/send-code
 */
router.post('/send-code', 
  codeSendLimit,
  validateSchema(phoneVerificationSchema),
  async (req, res) => {
    try {
      const { phoneNumber } = req.body;
      const purpose = req.body.purpose || 'login';
      
      // 只允许特定用途
      const allowedPurposes = ['login', 'register', 'reset', 'bind'];
      if (!allowedPurposes.includes(purpose)) {
        return res.status(400).json({
          success: false,
          message: '不支持的验证码用途'
        });
      }
      
      const result = await phoneAuthService.sendVerificationCode(phoneNumber, purpose);
      
      if (result.success) {
        res.status(200).json(result);
      } else {
        res.status(400).json(result);
      }
    } catch (error) {
      logger.error(`发送验证码错误: ${error.message}`, { error });
      res.status(500).json({
        success: false,
        message: '系统错误，请稍后再试'
      });
    }
  }
);

/**
 * 手机号登录/注册
 * @route POST /phone/login
 */
router.post('/login',
  verifyCodeLimit,
  validateSchema(phoneCodeSchema),
  async (req, res) => {
    try {
      const { phoneNumber, code } = req.body;
      const clientInfo = getClientInfo(req);
      
      const result = await phoneAuthService.login(phoneNumber, code, clientInfo);
      
      if (result.success) {
        // 设置认证Cookie
        if (result.accessToken) {
          res.cookie('accessToken', result.accessToken, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            maxAge: 60 * 60 * 1000 // 1小时
          });
        }
        
        if (result.refreshToken) {
          res.cookie('refreshToken', result.refreshToken, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            path: '/auth/refresh',
            maxAge: 30 * 24 * 60 * 60 * 1000 // 30天
          });
        }
        
        res.status(200).json(result);
      } else {
        res.status(400).json(result);
      }
    } catch (error) {
      logger.error(`手机登录错误: ${error.message}`, { error });
      res.status(500).json({
        success: false,
        message: '登录失败，请稍后再试'
      });
    }
  }
);

/**
 * 绑定手机号
 * @route POST /phone/bind
 */
router.post('/bind',
  authMiddleware.authenticate,
  validateSchema(phoneCodeSchema),
  async (req, res) => {
    try {
      const { phoneNumber, code } = req.body;
      const userId = req.user.id;
      
      const result = await phoneAuthService.bindPhone(userId, phoneNumber, code);
      
      if (result.success) {
        res.status(200).json(result);
      } else {
        res.status(400).json(result);
      }
    } catch (error) {
      logger.error(`绑定手机号错误: ${error.message}`, { error });
      res.status(500).json({
        success: false,
        message: '绑定失败，请稍后再试'
      });
    }
  }
);

/**
 * 验证手机验证码
 * @route POST /phone/verify-code
 */
router.post('/verify-code',
  verifyCodeLimit,
  validateSchema(phoneCodeSchema),
  async (req, res) => {
    try {
      const { phoneNumber, code, purpose } = req.body;
      
      const result = await phoneAuthService.verifyCode(phoneNumber, code, purpose || 'login');
      
      if (result.success) {
        res.status(200).json(result);
      } else {
        res.status(400).json(result);
      }
    } catch (error) {
      logger.error(`验证验证码错误: ${error.message}`, { error });
      res.status(500).json({
        success: false,
        message: '验证失败，请稍后再试'
      });
    }
  }
);

module.exports = router; 
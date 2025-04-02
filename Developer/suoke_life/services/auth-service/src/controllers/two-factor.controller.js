/**
 * 双因素认证控制器
 */
const twoFactorService = require('../services/two-factor.service');
const authService = require('../services/auth.service');
const securityLogService = require('../services/security-log.service');
const { responseHandler, errorHandler } = require('@suoke/shared').utils;

/**
 * 生成二因素认证密钥
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const generateTwoFactorSecret = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const username = req.user.username;
    
    if (!userId || !username) {
      return res.status(400).json({
        success: false,
        message: '请求缺少必要参数',
        code: 'auth/missing-parameters'
      });
    }
    
    const result = await twoFactorService.generateTOTPSecret(userId, username);
    
    return res.status(200).json({
      success: true,
      message: '二因素认证密钥生成成功',
      data: {
        setupId: result.setupId,
        secret: result.secret,
        qrCode: result.qrCode
      }
    });
  } catch (error) {
    return next(error);
  }
};

/**
 * 验证并激活二因素认证
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const verifyAndActivateTwoFactor = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { setupId, token } = req.body;
    
    if (!setupId || !token) {
      return res.status(400).json({
        success: false,
        message: '请求缺少必要参数',
        code: 'auth/missing-parameters'
      });
    }
    
    const result = await twoFactorService.verifyAndActivateTOTP(userId, setupId, token);
    
    return res.status(200).json({
      success: true,
      message: '二因素认证激活成功',
      data: {
        activated: result.activated,
        recoveryCodes: result.recoveryCodes
      }
    });
  } catch (error) {
    // 错误处理
    if (error.message.includes('验证码无效')) {
      return res.status(400).json({
        success: false,
        message: '验证码无效',
        code: 'auth/invalid-token'
      });
    } else if (error.message.includes('设置已过期')) {
      return res.status(400).json({
        success: false,
        message: '设置已过期，请重新生成密钥',
        code: 'auth/setup-expired'
      });
    }
    
    return next(error);
  }
};

/**
 * 验证二因素认证令牌
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const verifyTwoFactor = async (req, res, next) => {
  try {
    const { userId, token } = req.body;
    
    if (!userId || !token) {
      return res.status(400).json({
        success: false,
        message: '请求缺少必要参数',
        code: 'auth/missing-parameters'
      });
    }
    
    const verified = await twoFactorService.verifyTOTP(userId, token);
    
    if (!verified) {
      // 记录失败的验证尝试
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.LOGIN_FAILED,
        {
          userId,
          reason: '二因素认证失败',
          twoFactorFailed: true
        }
      );
      
      return res.status(401).json({
        success: false,
        message: '二因素认证失败',
        code: 'auth/2fa-failed'
      });
    }
    
    return res.status(200).json({
      success: true,
      message: '二因素认证成功'
    });
  } catch (error) {
    return next(error);
  }
};

/**
 * 获取新的恢复码
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const regenerateRecoveryCodes = async (req, res, next) => {
  try {
    const userId = req.user.id;
    
    // 验证用户已启用二因素认证
    const { db } = require('../config/database');
    const user = await db('users')
      .where('id', userId)
      .select('two_factor_enabled')
      .first();
    
    if (!user || !user.two_factor_enabled) {
      return res.status(400).json({
        success: false,
        message: '用户未启用二因素认证',
        code: 'auth/2fa-not-enabled'
      });
    }
    
    const recoveryCodes = await twoFactorService.generateRecoveryCodes(userId);
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.TWO_FACTOR_ENABLED,
      {
        userId,
        action: 'regenerate_recovery_codes'
      }
    );
    
    return res.status(200).json({
      success: true,
      message: '恢复码重新生成成功',
      data: {
        recoveryCodes
      }
    });
  } catch (error) {
    return next(error);
  }
};

/**
 * 禁用二因素认证
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const disableTwoFactor = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { password } = req.body;
    
    if (!password) {
      return res.status(400).json({
        success: false,
        message: '请提供当前密码以验证身份',
        code: 'auth/missing-parameters'
      });
    }
    
    const result = await twoFactorService.disableTwoFactor(userId, password);
    
    if (!result) {
      return res.status(400).json({
        success: false,
        message: '禁用二因素认证失败',
        code: 'auth/disable-2fa-failed'
      });
    }
    
    return res.status(200).json({
      success: true,
      message: '二因素认证已禁用'
    });
  } catch (error) {
    // 错误处理
    if (error.message.includes('用户未启用二因素认证')) {
      return res.status(400).json({
        success: false,
        message: '用户未启用二因素认证',
        code: 'auth/2fa-not-enabled'
      });
    } else if (error.message.includes('密码错误')) {
      return res.status(401).json({
        success: false,
        message: '密码验证失败',
        code: 'auth/invalid-password'
      });
    }
    
    return next(error);
  }
};

/**
 * 检查用户是否已启用二因素认证
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getTwoFactorStatus = async (req, res, next) => {
  try {
    const userId = req.user.id;
    
    const { db } = require('../config/database');
    const user = await db('users')
      .where('id', userId)
      .select('two_factor_enabled', 'two_factor_method')
      .first();
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: '用户不存在',
        code: 'auth/user-not-found'
      });
    }
    
    return res.status(200).json({
      success: true,
      data: {
        enabled: user.two_factor_enabled || false,
        method: user.two_factor_method || null
      }
    });
  } catch (error) {
    return next(error);
  }
};

/**
 * 验证二因素认证码并完成登录流程
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 * @returns {Promise<void>}
 */
const verifyTwoFactorAndLogin = async (req, res, next) => {
  try {
    const { userId, token, tempSessionId, rememberDevice, deviceInfo } = req.body;
    const ipAddress = req.ip || req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    const userAgent = req.headers['user-agent'];
    
    if (!userId || !token || !tempSessionId) {
      return res.status(400).json({
        success: false,
        message: '缺少必要参数'
      });
    }
    
    const result = await authService.verifyTwoFactorAndLogin(
      userId, 
      token, 
      tempSessionId, 
      rememberDevice === true, 
      deviceInfo || {},
      ipAddress, 
      userAgent
    );
    
    // 如果启用了CSRF保护，生成CSRF令牌
    const config = require('../config');
    if (config.security && config.security.csrf && config.security.csrf.enabled) {
      const csrfService = require('../services/csrf.service');
      const csrfToken = await csrfService.generateToken(userId);
      res.cookie('XSRF-TOKEN', csrfToken, {
        httpOnly: false,
        secure: config.app.environment !== 'development',
        sameSite: 'lax',
        maxAge: 24 * 60 * 60 * 1000 // 24小时
      });
    }
    
    // 设置刷新令牌到安全cookie
    if (config.security && config.security.refreshToken && config.security.refreshToken.useCookie) {
      res.cookie('refresh_token', result.token.refreshToken, {
        httpOnly: true,
        secure: config.app.environment !== 'development',
        sameSite: 'strict',
        maxAge: result.token.refreshExpiresIn * 1000
      });
    }
    
    res.json({
      success: true,
      message: '二因素认证成功，登录完成',
      user: {
        id: result.user.id,
        username: result.user.username,
        email: result.user.email,
        name: result.user.name,
        avatar: result.user.avatar,
        phone: result.user.phone,
        roles: result.user.roles
      },
      token: {
        accessToken: result.token.accessToken,
        expiresIn: result.token.expiresIn,
        tokenType: result.token.tokenType
      },
      session: {
        id: result.session.id,
        status: result.session.status
      },
      device: result.device ? {
        id: result.device.id,
        name: result.device.name,
        trusted: result.device.trusted,
        lastUsed: result.device.lastUsed
      } : null,
      // 只有在配置不使用cookie时才在JSON中返回刷新令牌
      ...(config.security && config.security.refreshToken && config.security.refreshToken.useCookie ? {} : {
        refreshToken: result.token.refreshToken
      })
    });
  } catch (error) {
    if (error.message.includes('二因素认证码无效')) {
      return res.status(401).json({
        success: false,
        message: '二因素认证码无效',
        code: 'auth/invalid-2fa-code'
      });
    }
    
    if (error.message.includes('无效的二因素认证会话')) {
      return res.status(401).json({
        success: false,
        message: '认证会话已过期，请重新登录',
        code: 'auth/invalid-2fa-session'
      });
    }
    
    next(error);
  }
};

module.exports = {
  generateTwoFactorSecret,
  verifyAndActivateTwoFactor,
  verifyTwoFactor,
  regenerateRecoveryCodes,
  disableTwoFactor,
  getTwoFactorStatus,
  verifyTwoFactorAndLogin
}; 
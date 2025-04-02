/**
 * 认证控制器
 */
const passport = require('passport');
const { responseHandler, errorHandler } = require('@suoke/shared').utils;
const authService = require('../services/auth.service');
const config = require('../config');
const csrfService = require('../services/csrf.service');

/**
 * 用户注册
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const register = async (req, res) => {
  try {
    const result = await authService.register(req.body);
    return responseHandler.success(res, '注册成功', result);
  } catch (error) {
    return errorHandler.handleError(error, res);
  }
};

/**
 * 用户登录
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const login = async (req, res) => {
  try {
    const { identifier, password, rememberDevice, deviceInfo } = req.body;
    const ipAddress = req.ip || req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    const userAgent = req.headers['user-agent'];
    
    const result = await authService.login(
      identifier, 
      password, 
      deviceInfo || {}, // 确保deviceInfo存在
      ipAddress, 
      userAgent
    );
    
    // 如果需要设备验证
    if (result.requiresDeviceVerification) {
      return res.status(200).json({
        success: true,
        status: 'requires_device_verification',
        message: '需要验证此设备',
        userId: result.userId,
        verificationInfo: result.verificationInfo
      });
    }
    
    // 如果需要2FA
    if (result.requiresTwoFactor) {
      return res.status(200).json({
        success: true,
        status: 'requires_2fa',
        message: '需要二因素认证',
        userId: result.userId,
        tempSessionId: result.tempSessionId,
        twoFactorMethod: result.twoFactorMethod
      });
    }
    
    // 登录成功，不需要额外验证
    
    // 如果启用了CSRF保护，生成CSRF令牌
    if (config.security.csrf.enabled) {
      const csrfToken = await csrfService.generateToken(result.user.id);
      res.cookie('XSRF-TOKEN', csrfToken, {
        httpOnly: false,
        secure: config.app.environment !== 'development',
        sameSite: 'lax',
        maxAge: 24 * 60 * 60 * 1000 // 24小时
      });
    }
    
    // 设置刷新令牌到安全cookie
    if (config.security.refreshToken.useCookie) {
      res.cookie('refresh_token', result.token.refreshToken, {
        httpOnly: true,
        secure: config.app.environment !== 'development',
        sameSite: 'strict',
        maxAge: result.token.refreshExpiresIn * 1000
      });
    }
    
    return res.status(200).json({
      success: true,
      message: '登录成功',
      user: {
        id: result.user.id,
        username: result.user.username,
        email: result.user.email,
        name: result.user.name,
        avatar: result.user.avatar,
        phone: result.user.phone,
        roles: result.user.roles,
        createdAt: result.user.created_at,
        updatedAt: result.user.updated_at
      },
      token: {
        accessToken: result.token.accessToken,
        expiresIn: result.token.expiresIn,
        tokenType: result.token.tokenType
      },
      session: {
        id: result.session.id,
        status: result.session.status,
        deviceInfo: result.session.deviceInfo,
        createdAt: result.session.createdAt
      },
      device: result.device ? {
        id: result.device.id,
        name: result.device.name,
        trusted: result.device.trusted,
        lastUsed: result.device.lastUsed
      } : null,
      // 只有在配置不使用cookie时才在JSON中返回刷新令牌
      ...(config.security.refreshToken.useCookie ? {} : {
        refreshToken: result.token.refreshToken
      }),
      requires2FA: result.user.twoFactorEnabled || false
    });
  } catch (error) {
    // 为特定错误添加错误代码
    let status = error.status || 500;
    let message = error.message || '登录失败';
    let code = 'auth/unknown';
    
    if (message.includes('密码错误') || message.includes('用户名或密码错误')) {
      status = 401;
      code = 'auth/invalid-credentials';
    } else if (message.includes('用户不存在')) {
      status = 401;
      code = 'auth/user-not-found';
    } else if (message.includes('账户锁定')) {
      status = 403;
      code = 'auth/account-locked';
    } else if (message.includes('未激活')) {
      status = 403;
      code = 'auth/account-inactive';
    } else if (message.includes('需要二因素认证')) {
      status = 200; // 这是一个预期的情况，返回200但标记requires2FA
      code = 'auth/requires-2fa';
    } else if (message.includes('需要设备验证')) {
      status = 200; // 这是一个预期的情况，返回200但标记requiresDeviceVerification
      code = 'auth/requires-device-verification';
    }
    
    return res.status(status).json({
      success: false,
      message: message,
      code: code,
      errors: error.errors || null,
      tempSessionId: error.tempSessionId, // 如果是二因素认证需要的临时会话ID
      requires2FA: code === 'auth/requires-2fa',
      requiresDeviceVerification: code === 'auth/requires-device-verification'
    });
  }
};

/**
 * 刷新令牌
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const refreshToken = async (req, res) => {
  try {
    // 从请求体或cookie获取刷新令牌
    let refreshToken = req.body.refreshToken;
    
    if (!refreshToken && config.security.refreshToken.useCookie) {
      refreshToken = req.cookies.refresh_token;
    }
    
    if (!refreshToken) {
      return res.status(400).json({
        success: false,
        message: '未提供刷新令牌',
        code: 'auth/no-refresh-token'
      });
    }
    
    const result = await authService.refreshToken(refreshToken);
    
    // 如果启用了CSRF保护，生成新的CSRF令牌
    if (config.security.csrf.enabled) {
      const csrfToken = await csrfService.generateToken(result.user.id);
      res.cookie('XSRF-TOKEN', csrfToken, {
        httpOnly: false,
        secure: config.app.environment !== 'development',
        sameSite: 'lax',
        maxAge: 24 * 60 * 60 * 1000 // 24小时
      });
    }
    
    // 更新刷新令牌cookie
    if (config.security.refreshToken.useCookie) {
      res.cookie('refresh_token', result.token.refreshToken, {
        httpOnly: true,
        secure: config.app.environment !== 'development',
        sameSite: 'strict',
        maxAge: result.token.refreshExpiresIn * 1000
      });
    }
    
    return res.status(200).json({
      success: true,
      message: '令牌刷新成功',
      user: {
        id: result.user.id,
        username: result.user.username,
        email: result.user.email,
        roles: result.user.roles
      },
      token: {
        accessToken: result.token.accessToken,
        expiresIn: result.token.expiresIn,
        tokenType: result.token.tokenType
      },
      // 只有在配置不使用cookie时才在JSON中返回刷新令牌
      ...(config.security.refreshToken.useCookie ? {} : {
        refreshToken: result.token.refreshToken
      })
    });
  } catch (error) {
    // 为特定错误添加错误代码
    let status = error.status || 500;
    let message = error.message || '刷新令牌失败';
    let code = 'auth/unknown';
    
    if (message.includes('过期') || message.includes('无效')) {
      status = 401;
      code = 'auth/token-expired';
    } else if (message.includes('用户不存在')) {
      status = 401;
      code = 'auth/user-not-found';
    } else if (message.includes('已被撤销')) {
      status = 401;
      code = 'auth/token-revoked';
    } else if (message.includes('令牌类型')) {
      status = 401;
      code = 'auth/invalid-token-type';
    }
    
    return res.status(status).json({
      success: false,
      message: message,
      code: code,
      errors: error.errors || null
    });
  }
};

/**
 * 用户登出
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const logout = async (req, res) => {
  try {
    const userId = req.user.id;
    const accessToken = req.headers.authorization?.split(' ')[1];
    const refreshToken = req.body.refreshToken || req.cookies?.refresh_token;
    const logoutAll = req.body.all === true; // 是否登出所有设备
    
    await authService.logout(userId, accessToken, refreshToken, logoutAll);
    
    // 清除cookie
    if (config.security.refreshToken.useCookie) {
      res.clearCookie('refresh_token');
    }
    
    if (config.security.csrf.enabled) {
      res.clearCookie('XSRF-TOKEN');
    }
    
    return res.status(200).json({
      success: true,
      message: logoutAll ? '已登出所有设备' : '登出成功'
    });
  } catch (error) {
    return res.status(error.status || 500).json({
      success: false,
      message: error.message || '登出失败',
      code: 'auth/logout-failed'
    });
  }
};

/**
 * 忘记密码
 */
const forgotPassword = async (req, res, next) => {
  try {
    const { email } = req.body;
    await authService.forgotPassword(email);
    return responseHandler.success(res, { message: '密码重置链接已发送至您的邮箱' });
  } catch (error) {
    return next(error);
  }
};

/**
 * 重置密码
 */
const resetPassword = async (req, res, next) => {
  try {
    const { token, password } = req.body;
    const result = await authService.resetPassword(token, password);
    
    if (!result) {
      return next(errorHandler.createError(400, '重置密码令牌无效或已过期'));
    }
    
    return responseHandler.success(res, { message: '密码重置成功' });
  } catch (error) {
    return next(error);
  }
};

module.exports = {
  register,
  login,
  refreshToken,
  logout,
  forgotPassword,
  resetPassword
}; 
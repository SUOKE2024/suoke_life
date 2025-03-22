/**
 * 认证控制器
 */
const passport = require('passport');
const { responseHandler, errorHandler } = require('@suoke/shared').utils;
const authService = require('../services/auth.service');

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
    const { username, password } = req.body;
    const result = await authService.login(username, password);
    
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
        createdAt: result.user.created_at,
        updatedAt: result.user.updated_at
      },
      token: {
        accessToken: result.accessToken,
        refreshToken: result.refreshToken,
        expiresIn: result.expiresIn
      },
      requires2FA: false // 如果实现了双因素认证，这里需要判断
    });
  } catch (error) {
    // 为特定错误添加错误代码
    let status = error.status || 500;
    let message = error.message || '登录失败';
    let code = 'auth/unknown';
    
    if (message.includes('密码错误')) {
      status = 401;
      code = 'auth/invalid-credentials';
    } else if (message.includes('用户不存在')) {
      status = 401;
      code = 'auth/user-not-found';
    } else if (message.includes('账户锁定')) {
      status = 403;
      code = 'auth/account-locked';
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
 * 刷新令牌
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const refreshToken = async (req, res) => {
  try {
    const { refreshToken } = req.body;
    const result = await authService.refreshToken(refreshToken);
    
    return res.status(200).json({
      success: true,
      message: '令牌刷新成功',
      user: result.user,
      token: {
        accessToken: result.accessToken,
        refreshToken: result.refreshToken,
        expiresIn: result.expiresIn
      }
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
    const { refreshToken } = req.body;
    await authService.logout(refreshToken);
    return responseHandler.success(res, '登出成功');
  } catch (error) {
    return errorHandler.handleError(error, res);
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
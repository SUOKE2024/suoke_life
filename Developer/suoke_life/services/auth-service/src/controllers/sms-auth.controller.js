/**
 * 短信认证控制器
 */
const smsService = require('../services/sms.service');
const authService = require('../services/auth.service');
const tokenService = require('../services/token.service');
const userService = require('../services/user.service');
const securityLogService = require('../services/security-log.service');
const { logger } = require('@suoke/shared').utils;

/**
 * 发送短信验证码
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const sendVerificationCode = async (req, res, next) => {
  try {
    const { phone, type, userId } = req.body;
    
    if (!phone) {
      return res.status(400).json({
        success: false,
        message: '手机号不能为空',
        code: 'auth/missing-phone'
      });
    }
    
    if (!Object.values(smsService.CODE_TYPES).includes(type)) {
      return res.status(400).json({
        success: false,
        message: '验证码类型无效',
        code: 'auth/invalid-code-type'
      });
    }
    
    // 如果是登录或重置密码，需要检查手机号是否存在
    if ([smsService.CODE_TYPES.LOGIN, smsService.CODE_TYPES.RESET_PASSWORD].includes(type)) {
      const userExists = await userService.checkUserExistsByPhone(phone);
      if (!userExists) {
        // 为安全起见，依然返回成功，但记录日志
        logger.warn(`尝试向未注册手机号发送${type}验证码`, { phone });
        
        // 为了防止泄露用户信息，我们返回成功，但实际上不发送短信
        return res.status(200).json({
          success: true,
          message: '验证码已发送，请注意查收'
        });
      }
    }
    
    // 如果是注册，需要检查手机号是否已注册
    if (type === smsService.CODE_TYPES.REGISTER) {
      const userExists = await userService.checkUserExistsByPhone(phone);
      if (userExists) {
        return res.status(400).json({
          success: false,
          message: '该手机号已注册',
          code: 'auth/phone-exists'
        });
      }
    }
    
    // 如果是变更手机号，需要验证用户是否已登录
    if (type === smsService.CODE_TYPES.CHANGE_PHONE) {
      if (!req.user || !req.user.id) {
        return res.status(401).json({
          success: false,
          message: '需要登录才能更改手机号',
          code: 'auth/unauthorized'
        });
      }
      
      // 验证新手机号是否已被其他用户使用
      const existingUser = await userService.getUserByPhone(phone);
      if (existingUser && existingUser.id !== req.user.id) {
        return res.status(400).json({
          success: false,
          message: '该手机号已被使用',
          code: 'auth/phone-exists'
        });
      }
    }
    
    // 准备元数据
    const metadata = {
      ...(userId ? { userId } : {}),
      ...(req.user ? { requestUserId: req.user.id } : {}),
      ipAddress: req.ip,
      userAgent: req.headers['user-agent']
    };
    
    // 发送验证码
    const result = await smsService.sendVerificationCode(phone, type, metadata);
    
    if (!result.success) {
      return res.status(400).json({
        success: false,
        message: result.message,
        code: 'auth/sms-send-failed',
        ...(result.remainingTime ? { remainingTime: result.remainingTime } : {})
      });
    }
    
    return res.status(200).json({
      success: true,
      message: '验证码已发送，请注意查收',
      ...(result.code ? { code: result.code } : {}) // 仅在开发环境下返回验证码
    });
  } catch (error) {
    return next(error);
  }
};

/**
 * 短信验证码登录
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const loginWithSmsCode = async (req, res, next) => {
  try {
    const { phone, code } = req.body;
    
    if (!phone || !code) {
      return res.status(400).json({
        success: false,
        message: '手机号和验证码不能为空',
        code: 'auth/missing-parameters'
      });
    }
    
    // 验证验证码
    const verifyResult = await smsService.verifyCode(phone, code, smsService.CODE_TYPES.LOGIN);
    
    if (!verifyResult.valid) {
      return res.status(401).json({
        success: false,
        message: verifyResult.message,
        code: 'auth/invalid-code'
      });
    }
    
    // 获取用户信息
    const user = await userService.getUserByPhone(phone);
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: '用户不存在',
        code: 'auth/user-not-found'
      });
    }
    
    // 检查账户状态
    if (user.status !== 'active') {
      let errorMessage = '账户状态异常，无法登录';
      let errorCode = 'auth/account-inactive';
      
      if (user.status === 'locked') {
        errorMessage = '账户已锁定，请联系客服';
        errorCode = 'auth/account-locked';
      } else if (user.status === 'pending') {
        errorMessage = '账户未激活，请先激活账户';
        errorCode = 'auth/account-pending';
      }
      
      return res.status(403).json({
        success: false,
        message: errorMessage,
        code: errorCode
      });
    }
    
    // 生成令牌
    const tokens = await tokenService.generateAuthTokens(user);
    
    // 检查是否需要进行二因素认证
    const requireTwoFactor = user.two_factor_enabled;
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.LOGIN_SUCCESS,
      {
        userId: user.id,
        method: 'sms',
        requireTwoFactor,
        ipAddress: req.ip,
        userAgent: req.headers['user-agent']
      }
    );
    
    // 如果启用了双因素认证，只返回部分信息
    if (requireTwoFactor) {
      return res.status(200).json({
        success: true,
        message: '需要进行二因素认证',
        requireTwoFactor: true,
        userId: user.id
      });
    }
    
    // 设置刷新令牌cookie（如果配置使用cookie）
    if (config.security.refreshToken.useCookie && tokens.refreshToken) {
      res.cookie('refreshToken', tokens.refreshToken, {
        httpOnly: true,
        secure: req.secure || req.headers['x-forwarded-proto'] === 'https',
        sameSite: 'strict',
        maxAge: config.security.jwt.refreshTokenExpiration * 1000
      });
    }
    
    // 返回登录成功响应
    return res.status(200).json({
      success: true,
      message: '登录成功',
      data: {
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          phone: user.phone,
          role: user.role
        },
        tokens: {
          accessToken: tokens.accessToken,
          expiresIn: config.security.jwt.accessTokenExpiration,
          ...(config.security.refreshToken.useCookie ? {} : { refreshToken: tokens.refreshToken })
        }
      }
    });
  } catch (error) {
    return next(error);
  }
};

/**
 * 短信验证码注册
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const registerWithSmsCode = async (req, res, next) => {
  try {
    const { phone, code, username, password } = req.body;
    
    if (!phone || !code || !username) {
      return res.status(400).json({
        success: false,
        message: '手机号、验证码和用户名不能为空',
        code: 'auth/missing-parameters'
      });
    }
    
    // 验证验证码
    const verifyResult = await smsService.verifyCode(phone, code, smsService.CODE_TYPES.REGISTER);
    
    if (!verifyResult.valid) {
      return res.status(401).json({
        success: false,
        message: verifyResult.message,
        code: 'auth/invalid-code'
      });
    }
    
    // 检查手机号是否已注册
    const phoneExists = await userService.checkUserExistsByPhone(phone);
    if (phoneExists) {
      return res.status(400).json({
        success: false,
        message: '该手机号已注册',
        code: 'auth/phone-exists'
      });
    }
    
    // 检查用户名是否已存在
    const usernameExists = await userService.checkUserExistsByUsername(username);
    if (usernameExists) {
      return res.status(400).json({
        success: false,
        message: '用户名已存在',
        code: 'auth/username-exists'
      });
    }
    
    // 创建用户
    const userData = {
      username,
      phone,
      ...(password ? { password } : {})
    };
    
    const user = await userService.createUser(userData);
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.USER_REGISTERED,
      {
        userId: user.id,
        method: 'sms',
        ipAddress: req.ip,
        userAgent: req.headers['user-agent']
      }
    );
    
    // 生成令牌
    const tokens = await tokenService.generateAuthTokens(user);
    
    // 设置刷新令牌cookie（如果配置使用cookie）
    if (config.security.refreshToken.useCookie && tokens.refreshToken) {
      res.cookie('refreshToken', tokens.refreshToken, {
        httpOnly: true,
        secure: req.secure || req.headers['x-forwarded-proto'] === 'https',
        sameSite: 'strict',
        maxAge: config.security.jwt.refreshTokenExpiration * 1000
      });
    }
    
    // 返回注册成功响应
    return res.status(201).json({
      success: true,
      message: '注册成功',
      data: {
        user: {
          id: user.id,
          username: user.username,
          phone: user.phone,
          role: user.role
        },
        tokens: {
          accessToken: tokens.accessToken,
          expiresIn: config.security.jwt.accessTokenExpiration,
          ...(config.security.refreshToken.useCookie ? {} : { refreshToken: tokens.refreshToken })
        }
      }
    });
  } catch (error) {
    return next(error);
  }
};

/**
 * 使用短信验证码重置密码
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const resetPasswordWithSmsCode = async (req, res, next) => {
  try {
    const { phone, code, newPassword } = req.body;
    
    if (!phone || !code || !newPassword) {
      return res.status(400).json({
        success: false,
        message: '手机号、验证码和新密码不能为空',
        code: 'auth/missing-parameters'
      });
    }
    
    // 验证验证码
    const verifyResult = await smsService.verifyCode(
      phone, 
      code, 
      smsService.CODE_TYPES.RESET_PASSWORD
    );
    
    if (!verifyResult.valid) {
      return res.status(401).json({
        success: false,
        message: verifyResult.message,
        code: 'auth/invalid-code'
      });
    }
    
    // 获取用户
    const user = await userService.getUserByPhone(phone);
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: '用户不存在',
        code: 'auth/user-not-found'
      });
    }
    
    // 更新密码
    await userService.updateUserPassword(user.id, newPassword);
    
    // 吊销所有现有令牌
    await tokenService.revokeAllUserTokens(user.id);
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.PASSWORD_CHANGED,
      {
        userId: user.id,
        method: 'sms_reset',
        ipAddress: req.ip,
        userAgent: req.headers['user-agent']
      }
    );
    
    return res.status(200).json({
      success: true,
      message: '密码重置成功，请重新登录'
    });
  } catch (error) {
    return next(error);
  }
};

/**
 * 验证手机号归属
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const verifyPhone = async (req, res, next) => {
  try {
    const { phone, code } = req.body;
    const userId = req.user.id;
    
    if (!phone || !code) {
      return res.status(400).json({
        success: false,
        message: '手机号和验证码不能为空',
        code: 'auth/missing-parameters'
      });
    }
    
    // 验证验证码
    const verifyResult = await smsService.verifyCode(
      phone, 
      code, 
      smsService.CODE_TYPES.VERIFY_PHONE
    );
    
    if (!verifyResult.valid) {
      return res.status(401).json({
        success: false,
        message: verifyResult.message,
        code: 'auth/invalid-code'
      });
    }
    
    // 检查手机号是否已绑定到其他账户
    const existingUser = await userService.getUserByPhone(phone);
    if (existingUser && existingUser.id !== userId) {
      return res.status(400).json({
        success: false,
        message: '该手机号已被其他账户使用',
        code: 'auth/phone-exists'
      });
    }
    
    // 更新用户手机号（如果尚未设置）
    const user = await userService.getUserById(userId);
    if (!user.phone) {
      await userService.updateUser(userId, { phone });
    }
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.PHONE_VERIFIED,
      {
        userId,
        phone,
        ipAddress: req.ip,
        userAgent: req.headers['user-agent']
      }
    );
    
    return res.status(200).json({
      success: true,
      message: '手机号验证成功'
    });
  } catch (error) {
    return next(error);
  }
};

/**
 * 更改绑定手机号
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const changePhone = async (req, res, next) => {
  try {
    const { newPhone, code } = req.body;
    const userId = req.user.id;
    
    if (!newPhone || !code) {
      return res.status(400).json({
        success: false,
        message: '新手机号和验证码不能为空',
        code: 'auth/missing-parameters'
      });
    }
    
    // 验证验证码
    const verifyResult = await smsService.verifyCode(
      newPhone, 
      code, 
      smsService.CODE_TYPES.CHANGE_PHONE
    );
    
    if (!verifyResult.valid) {
      return res.status(401).json({
        success: false,
        message: verifyResult.message,
        code: 'auth/invalid-code'
      });
    }
    
    // 检查手机号是否已绑定到其他账户
    const existingUser = await userService.getUserByPhone(newPhone);
    if (existingUser && existingUser.id !== userId) {
      return res.status(400).json({
        success: false,
        message: '该手机号已被其他账户使用',
        code: 'auth/phone-exists'
      });
    }
    
    // 获取用户当前手机号
    const user = await userService.getUserById(userId);
    const oldPhone = user.phone;
    
    // 更新用户手机号
    await userService.updateUser(userId, { phone: newPhone });
    
    // 记录安全日志
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.PHONE_CHANGED,
      {
        userId,
        oldPhone,
        newPhone,
        ipAddress: req.ip,
        userAgent: req.headers['user-agent']
      }
    );
    
    return res.status(200).json({
      success: true,
      message: '手机号更改成功'
    });
  } catch (error) {
    return next(error);
  }
};

module.exports = {
  sendVerificationCode,
  loginWithSmsCode,
  registerWithSmsCode,
  resetPasswordWithSmsCode,
  verifyPhone,
  changePhone
}; 
/**
 * 认证服务
 */
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const Redis = require('ioredis');
const { db } = require('../config/database');
const config = require('../config');
const { logger, errorHandler } = require('@suoke/shared').utils;
const userRepository = require('../repositories/user.repository');
const tokenService = require('./token.service');
const sessionService = require('./session.service');
const securityLogService = require('./security-log.service');
const statusCodes = require('../config/status-codes');
const ApiError = require('../utils/api-error');
const security = require('./security'); // 引入安全服务主入口

// 创建Redis客户端
const redis = new Redis({
  host: config.redis.host,
  port: config.redis.port
});

/**
 * 生成令牌
 * @param {Object} user - 用户对象
 * @param {Object} options - 选项对象
 * @param {string} options.tokenType - 令牌类型 (access, refresh, passwordReset, etc.)
 * @param {number} options.expiresIn - 过期时间（秒）
 * @returns {Object} 包含访问令牌和刷新令牌的对象
 */
const generateTokens = async (user, options = {}) => {
  // 创建JWT负载
  const payload = {
    sub: user.id,
    role: user.role,
    type: options.tokenType || 'access',
    iat: Math.floor(Date.now() / 1000),
    jti: uuidv4() // JWT ID, 用于标识特定的令牌
  };

  // 设置过期时间
  const accessTokenExpiry = options.expiresIn || config.jwt.accessTokenExpiry || 24 * 60 * 60; // 默认24小时
  const refreshTokenExpiry = config.jwt.refreshTokenExpiry || 7 * 24 * 60 * 60; // 默认7天
  
  if (payload.type === 'access') {
    payload.exp = Math.floor(Date.now() / 1000) + accessTokenExpiry;
  } else if (payload.type === 'reset') {
    payload.exp = Math.floor(Date.now() / 1000) + (60 * 30); // 30分钟
  }

  // 添加其他安全特性
  payload.iss = config.app.name || 'suoke-auth-service'; // 签发者
  payload.aud = config.app.baseUrl || 'https://suoke.life'; // 接收者

  // 生成访问令牌
  const accessToken = jwt.sign(payload, config.jwt.secret, {
    algorithm: 'HS256' // 指定算法
  });

  // 生成刷新令牌
  const refreshToken = uuidv4();

  // 将刷新令牌存储在Redis中
  const refreshTokenKey = `refresh_token:${refreshToken}`;
  const refreshTokenData = JSON.stringify({
    userId: user.id,
    jti: payload.jti,
    createdAt: new Date().toISOString()
  });
  
  await redis.set(
    refreshTokenKey,
    refreshTokenData,
    'EX',
    refreshTokenExpiry
  );

  // 记录活跃令牌，用于注销所有会话
  await redis.sadd(`user_tokens:${user.id}`, refreshTokenKey);

  return {
    accessToken,
    refreshToken,
    expiresIn: accessTokenExpiry
  };
};

/**
 * 将令牌添加到黑名单
 * @param {string} token - JWT令牌
 * @param {number} exp - 过期时间戳
 */
const blacklistToken = async (token) => {
  try {
    // 解码JWT获取过期时间和jti
    const decoded = jwt.decode(token);
    if (!decoded || !decoded.exp || !decoded.jti) {
      throw new Error('无效的令牌格式');
    }
    
    // 计算剩余有效期
    const now = Math.floor(Date.now() / 1000);
    const remainingTime = decoded.exp - now;
    
    // 如果令牌已过期，不需要加入黑名单
    if (remainingTime <= 0) return;
    
    // 将令牌加入黑名单，使用jti作为键
    await redis.set(
      `blacklist:${decoded.jti}`,
      '1',
      'EX',
      remainingTime + 60 // 额外添加60秒缓冲
    );
  } catch (error) {
    logger.error(`将令牌加入黑名单失败: ${error.message}`);
    // 继续流程，不因黑名单操作失败而中断
  }
};

/**
 * 注册新用户
 * @param {Object} userData - 用户数据
 * @returns {Promise<Object>} 注册结果
 */
const register = async (userData) => {
  try {
    // 检查用户名是否已存在
    const existingUsername = await userRepository.getUserByUsername(userData.username);
    if (existingUsername) {
      throw new Error('用户名已存在');
    }
    
    // 检查邮箱是否已存在
    const existingEmail = await userRepository.getUserByEmail(userData.email);
    if (existingEmail) {
      throw new Error('邮箱已被注册');
    }
    
    // 加密密码
    const hashedPassword = await bcrypt.hash(userData.password, 10);
    
    // 创建用户
    const user = await userRepository.createUser({
      ...userData,
      password: hashedPassword
    });
    
    // 生成令牌
    const tokens = await generateTokens(user);
    
    // 如果提供了邮箱，发送欢迎邮件
    if (userData.email) {
      try {
        const emailService = require('./email.service');
        await emailService.sendWelcomeEmail(
          userData.email, 
          userData.username
        );
      } catch (emailError) {
        logger.error(`发送欢迎邮件失败: ${emailError.message}`, { error: emailError });
        // 继续流程，不因邮件发送失败而中断注册
      }
    }

    return {
      user,
      tokens
    };
  } catch (error) {
    logger.error(`注册错误: ${error.message}`);
    throw error;
  }
};

/**
 * 用户登录
 * @param {string} identifier 用户名、邮箱或手机号
 * @param {string} password 密码
 * @param {Object} deviceInfo 设备信息
 * @param {string} ipAddress IP地址
 * @param {string} userAgent 用户代理
 * @returns {Promise<Object>} 登录结果，包含token和用户信息
 */
const login = async (identifier, password, deviceInfo, ipAddress, userAgent) => {
  let user = null; // 在try外部声明user
  try {
    // 查找用户
    user = await findUserByIdentifier(identifier);
    
    if (!user) {
      // 即使找不到用户，也需要记录登录失败事件，可能用于检测用户名枚举攻击
      await security.recordLoginFailure(null, { ipAddress, userAgent, reason: 'user_not_found' });
      throw new ApiError(statusCodes.UNAUTHORIZED, '凭据无效');
    }
    
    if (user.status !== 'active') {
      await security.recordLoginFailure(user.id, { ipAddress, userAgent, reason: 'account_disabled' });
      throw new ApiError(statusCodes.FORBIDDEN, '账户已被禁用，请联系管理员');
    }
    
    // 密码验证
    const isPasswordValid = await bcrypt.compare(password, user.password);
    
    if (!isPasswordValid) {
      // 记录失败登录
      await security.recordLoginFailure(user.id, { ipAddress, userAgent, reason: 'invalid_password' });
      throw new ApiError(statusCodes.UNAUTHORIZED, '凭据无效');
    }
    
    // 密码验证通过，进行安全检查
    const securityResult = await security.processLoginSecurity({
      userId: user.id,
      deviceInfo,
      ipAddress,
      userAgent,
      deviceId: deviceInfo?.deviceId // 如果有传入deviceId
    });
    
    // 如果安全检查需要设备验证
    if (securityResult.verificationRequired) {
      // 创建临时会话用于设备验证流程
      const tempSession = await sessionService.createSession({
        userId: user.id,
        deviceInfo: { ...deviceInfo, fingerprint: securityResult.deviceFingerprint }, // 更新指纹
        status: 'pending_device_verification',
        expiresIn: config.security.deviceVerification.codeTTL || 900 // 15分钟
      });
      
      return {
        requiresDeviceVerification: true,
        verificationInfo: { 
          ...securityResult.verificationInfo, 
          tempSessionId: tempSession.id 
        },
        userId: user.id
      };
    }
    
    // 设备不需要验证或验证已通过（例如通过安全检查内部处理）
    // 检查用户是否启用了二因素认证
    if (user.two_factor_enabled) {
      // 创建临时会话用于二因素认证流程
      const tempSession = await sessionService.createSession({
        userId: user.id,
        deviceInfo: { ...deviceInfo, fingerprint: securityResult.deviceFingerprint },
        status: 'pending_2fa',
        expiresIn: 60 * 5 // 5分钟内有效的临时会话
      });
      
      // 返回二因素认证需要完成的信息
      return {
        requiresTwoFactor: true,
        twoFactorMethod: user.two_factor_method,
        tempSessionId: tempSession.id,
        userId: user.id
      };
    }
    
    // 用户没有启用二因素认证，完成登录
    // 创建正式会话
    const session = await sessionService.createSession({
      userId: user.id,
      deviceInfo: { ...deviceInfo, fingerprint: securityResult.deviceFingerprint }
    });
    
    // 生成令牌
    const tokens = await tokenService.generateTokens(user, { 
      sessionId: session.id, 
      deviceId: session.deviceId // 使用会话关联的设备ID
    });
    
    // 更新用户最后登录时间
    await updateLastLogin(user.id);
    
    // 记录登录成功事件
    await security.recordLoginSuccess(user.id, { 
      ipAddress, 
      userAgent, 
      deviceId: session.deviceId, 
      sessionId: session.id 
    });

    return {
      user: userRepository.sanitizeUser(user),
      tokens,
      session
    };
  } catch (error) {
    logger.error(`登录错误: ${error.message}`, { 
      error, 
      userId: user?.id, 
      identifier, 
      ipAddress 
    });
    // 如果没有记录失败，这里补充记录
    if (error instanceof ApiError && error.statusCode === statusCodes.UNAUTHORIZED && user) {
      // 密码错误或用户不存在的失败已经在前面记录
    } else if (user) {
      await security.recordLoginFailure(user.id, { 
        ipAddress, 
        userAgent, 
        reason: 'login_error' 
      });
    }
    
    // 重新抛出错误，让控制器处理
    throw error;
  }
};

/**
 * 刷新令牌
 * @param {string} refreshToken - 刷新令牌
 * @returns {Object} 新的访问令牌和刷新令牌
 */
const refreshToken = async (refreshToken) => {
  try {
    // 使用token服务验证刷新令牌
    const decoded = await tokenService.verifyRefreshToken(refreshToken);
    
    // 获取会话ID
    const sessionId = decoded.sid;
    
    // 查找用户
    const user = await db('users')
      .where('id', decoded.sub)
      .first();

    if (!user) {
      throw errorHandler.createError(401, '用户不存在');
    }
    
    // 检查账户状态
    if (user.status === 'locked') {
      throw errorHandler.createError(403, '账户已锁定，请联系管理员');
    }
    
    if (user.status === 'inactive') {
      throw errorHandler.createError(403, '账户未激活，请检查邮箱激活账户');
    }

    // 移除敏感信息
    delete user.password;
    
    // 获取用户权限
    const userRoles = await db('user_roles')
      .join('roles', 'user_roles.role_id', 'roles.id')
      .where('user_roles.user_id', user.id)
      .select('roles.name');
    
    user.roles = userRoles.map(r => r.name);

    // 撤销旧的刷新令牌
    await tokenService.revokeToken(refreshToken);

    // 生成新的令牌，保留会话ID
    const tokens = await tokenService.generateTokens(user, {
      sessionId: sessionId
    });
    
    // 如果有会话ID，更新会话活动时间
    if (sessionId) {
      const sessionService = require('./session.service');
      await sessionService.updateSessionActivity(sessionId);
    }

    return {
      user,
      token: tokens
    };
  } catch (error) {
    logger.error(`刷新令牌错误: ${error.message}`);
    throw error;
  }
};

/**
 * 用户登出
 * @param {string} userId - 用户ID
 * @param {string} accessToken - 访问令牌
 * @param {string} refreshToken - 刷新令牌
 * @param {boolean} allDevices - 是否登出所有设备
 * @returns {boolean} 是否成功登出
 */
const logout = async (userId, accessToken, refreshToken, allDevices = false) => {
  try {
    // 记录登出事件
    await db('user_events').insert({
      user_id: userId,
      event_type: 'logout',
      created_at: new Date()
    });
    
    // 获取会话服务
    const sessionService = require('./session.service');
    
    // 如果有访问令牌，获取会话ID
    let sessionId = null;
    if (accessToken) {
      try {
        const decoded = jwt.decode(accessToken);
        if (decoded && decoded.sid) {
          sessionId = decoded.sid;
        }
      } catch (error) {
        logger.error(`解析访问令牌获取会话ID失败: ${error.message}`);
      }
    }
    
    if (allDevices) {
      // 撤销用户所有令牌
      await tokenService.revokeAllUserTokens(userId);
      
      // 撤销用户所有会话
      const revokedCount = await sessionService.revokeAllUserSessions(userId, {
        reason: '用户登出所有设备'
      });
      
      logger.info(`用户登出所有设备: ${userId}, 撤销会话数: ${revokedCount}`);
      return true;
    } else {
      // 仅撤销当前令牌
      let success = true;
      
      if (accessToken) {
        const accessRevoked = await tokenService.revokeToken(accessToken);
        if (!accessRevoked) {
          logger.warn(`撤销访问令牌失败: ${userId}`);
          success = false;
        }
      }
      
      if (refreshToken) {
        const refreshRevoked = await tokenService.revokeToken(refreshToken);
        if (!refreshRevoked) {
          logger.warn(`撤销刷新令牌失败: ${userId}`);
          success = false;
        }
      }
      
      // 撤销当前会话
      if (sessionId) {
        const sessionRevoked = await sessionService.revokeSession(sessionId, {
          userId,
          reason: '用户主动登出'
        });
        
        if (!sessionRevoked) {
          logger.warn(`撤销会话失败: ${userId}, 会话ID: ${sessionId}`);
          success = false;
        }
      }
      
      return success;
    }
  } catch (error) {
    logger.error(`登出错误: ${error.message}`);
    throw error;
  }
};

/**
 * 忘记密码
 * @param {string} email - 邮箱
 * @returns {Promise<boolean>} 是否成功发送重置邮件
 */
const forgotPassword = async (email) => {
  try {
    const emailService = require('./email.service');
    
    // 查找用户
    const user = await db('users')
      .where('email', email)
      .first();

    if (!user) {
      // 为了安全，我们仍然返回成功，不暴露用户是否存在
      return true;
    }

    // 生成重置令牌
    const resetToken = uuidv4();
    const resetExpiration = 60 * 60; // 1小时

    // 存储重置令牌
    await redis.set(
      `reset_token:${resetToken}`,
      user.id,
      'EX',
      resetExpiration
    );

    // 发送重置邮件
    await emailService.sendPasswordResetEmail(
      email,
      resetToken,
      user.username || user.name || '用户'
    );
    
    logger.info(`密码重置邮件已发送给用户 ${user.id}`);

    return true;
  } catch (error) {
    logger.error(`忘记密码错误: ${error.message}`);
    throw error;
  }
};

/**
 * 重置密码
 * @param {string} token - 重置令牌
 * @param {string} password - 新密码
 * @returns {boolean} 是否成功重置密码
 */
const resetPassword = async (token, password) => {
  try {
    // 从Redis获取用户ID
    const userId = await redis.get(`reset_token:${token}`);

    if (!userId) {
      throw errorHandler.createError(401, '重置令牌无效或已过期');
    }

    // 查找用户
    const user = await db('users')
      .where('id', userId)
      .first();

    if (!user) {
      throw errorHandler.createError(401, '用户不存在');
    }

    // 哈希新密码
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // 更新密码
    await db('users')
      .where('id', userId)
      .update({
        password: hashedPassword,
        updated_at: new Date()
      });

    // 删除重置令牌
    await redis.del(`reset_token:${token}`);

    // 使该用户的所有刷新令牌失效
    const keys = await redis.keys(`refresh_token:*`);
    
    for (const key of keys) {
      const tokenUserId = await redis.get(key);
      if (tokenUserId === userId.toString()) {
        await redis.del(key);
      }
    }

    return true;
  } catch (error) {
    logger.error(`重置密码错误: ${error.message}`);
    throw error;
  }
};

/**
 * 通过手机号登录
 * @param {string} phone - 手机号码
 * @param {Object} options - 登录选项
 * @param {string} options.clientIp - 客户端IP地址
 * @param {string} options.userAgent - 客户端User-Agent
 * @param {Object} options.deviceInfo - 设备信息
 * @returns {Promise<Object>} 登录结果，包含用户信息和令牌
 */
const phoneLogin = async (phone, options = {}) => {
  try {
    // 查找用户
    const user = await db('users')
      .where({ phone })
      .first();
    
    if (!user) {
      throw errorHandler.createError(401, '用户不存在');
    }
    
    // 检查用户状态
    if (!user.is_active) {
      throw errorHandler.createError(401, '用户账号已被禁用');
    }
    
    // 生成令牌
    const tokens = await generateTokens(user);
    
    // 记录登录信息
    await db('users')
      .where({ id: user.id })
      .update({
        last_login_at: new Date(),
        updated_at: new Date()
      });
    
    // 返回用户信息（排除密码）
    const userResponse = { ...user };
    delete userResponse.password;
    
    return {
      user: userResponse,
      tokens
    };
  } catch (error) {
    logger.error(`手机号登录错误: ${error.message}`);
    throw error;
  }
};

/**
 * 通过手机号注册用户
 * @param {Object} userData - 用户数据
 * @param {string} userData.phone - 手机号码
 * @param {string} userData.username - 用户名
 * @param {string} [userData.password] - 密码（可选）
 * @param {string} userData.clientIp - 客户端IP地址
 * @param {string} userData.userAgent - 客户端User-Agent
 * @param {Object} userData.deviceInfo - 设备信息
 * @returns {Promise<Object>} 注册结果，包含用户信息和令牌
 */
const registerByPhone = async (userData) => {
  const { phone, username, password, clientIp, userAgent, deviceInfo } = userData;
  
  try {
    // 检查手机号是否已存在
    const existingPhoneUser = await db('users')
      .where({ phone })
      .first();
    
    if (existingPhoneUser) {
      throw errorHandler.createError(400, '该手机号已注册');
    }
    
    // 检查用户名是否已存在
    const existingUser = await db('users')
      .where({ username })
      .first();
    
    if (existingUser) {
      throw errorHandler.createError(400, '用户名已存在');
    }
    
    // 生成随机密码（如果未提供）
    const finalPassword = password || _generateRandomPassword();
    
    // 哈希密码
    const hashedPassword = await bcrypt.hash(finalPassword, 10);
    
    // 创建用户
    const now = new Date();
    const userId = uuidv4();
    
    const newUser = {
      id: userId,
      username,
      phone,
      password: hashedPassword,
      email: null,
      role: 'user',
      is_active: true,
      created_at: now,
      updated_at: now,
      last_login_at: now
    };
    
    // 插入用户数据
    await db('users').insert(newUser);
    
    // 生成令牌
    const tokens = await generateTokens(newUser);
    
    // 返回用户信息（排除密码）
    const userResponse = { ...newUser };
    delete userResponse.password;
    
    return {
      user: userResponse,
      tokens
    };
  } catch (error) {
    if (error.code === 'ER_DUP_ENTRY') {
      throw errorHandler.createError(400, '用户名或手机号已存在');
    }
    throw error;
  }
};

/**
 * 通过手机号重置密码
 * @param {string} phone - 手机号码
 * @param {string} newPassword - 新密码
 * @returns {Promise<boolean>} 重置结果
 */
const resetPasswordByPhone = async (phone, newPassword) => {
  try {
    // 查找用户
    const user = await db('users')
      .where({ phone })
      .first();
    
    if (!user) {
      throw errorHandler.createError(400, '未找到该手机号关联的用户');
    }
    
    // 哈希新密码
    const hashedPassword = await bcrypt.hash(newPassword, 10);
    
    // 更新密码
    await db('users')
      .where({ id: user.id })
      .update({
        password: hashedPassword,
        updated_at: new Date()
      });
    
    // 使该用户的所有刷新令牌失效
    const keys = await redis.keys(`refresh_token:*`);
    
    for (const key of keys) {
      const tokenUserId = await redis.get(key);
      if (tokenUserId === user.id.toString()) {
        await redis.del(key);
      }
    }
    
    return true;
  } catch (error) {
    logger.error(`通过手机号重置密码错误: ${error.message}`);
    throw error;
  }
};

/**
 * 更新用户手机号
 * @param {string} userId - 用户ID
 * @param {string} phone - 新手机号
 * @returns {Promise<boolean>} 更新结果
 */
const updateUserPhone = async (userId, phone) => {
  try {
    // 检查手机号是否已被其他用户使用
    const existingUser = await db('users')
      .where({ phone })
      .whereNot({ id: userId })
      .first();
    
    if (existingUser) {
      throw errorHandler.createError(400, '该手机号已被其他用户使用');
    }
    
    // 更新手机号
    await db('users')
      .where({ id: userId })
      .update({
        phone,
        updated_at: new Date()
      });
    
    return true;
  } catch (error) {
    logger.error(`更新用户手机号错误: ${error.message}`);
    throw error;
  }
};

/**
 * 检查手机号是否已存在
 * @param {string} phone - 手机号码
 * @returns {Promise<boolean>} 是否存在
 */
const checkPhoneExists = async (phone) => {
  try {
    const user = await db('users')
      .where({ phone })
      .first();
    
    return !!user;
  } catch (error) {
    logger.error(`检查手机号是否已存在错误: ${error.message}`);
    throw error;
  }
};

/**
 * 生成随机密码
 * @private
 * @returns {string} 随机密码
 */
const _generateRandomPassword = () => {
  const length = 12;
  const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+';
  let password = '';
  
  // 确保至少包含一个小写字母、大写字母、数字和特殊字符
  password += 'abcdefghijklmnopqrstuvwxyz'[Math.floor(Math.random() * 26)];
  password += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[Math.floor(Math.random() * 26)];
  password += '0123456789'[Math.floor(Math.random() * 10)];
  password += '!@#$%^&*()-_=+'[Math.floor(Math.random() * 14)];
  
  // 生成剩余字符
  for (let i = 0; i < length - 4; i++) {
    const randomIndex = Math.floor(Math.random() * charset.length);
    password += charset[randomIndex];
  }
  
  // 打乱密码字符顺序
  password = password.split('').sort(() => Math.random() - 0.5).join('');
  
  return password;
};

/**
 * 验证二因素认证代码并完成登录
 * @param {string} userId 用户ID
 * @param {string} tempSessionId 临时会话ID
 * @param {string} twoFactorCode 二因素认证代码
 * @param {boolean} rememberDevice 是否记住设备
 * @param {Object} deviceInfo 设备信息
 * @param {string} ipAddress IP地址
 * @param {string} userAgent 用户代理
 * @returns {Promise<Object>} 登录结果
 */
const verifyTwoFactorAndLogin = async (
  userId, 
  tempSessionId, 
  twoFactorCode, 
  rememberDevice = false, 
  deviceInfo = null,
  ipAddress,
  userAgent
) => {
  try {
    // 验证临时会话
    const tempSession = await sessionService.getSessionById(tempSessionId);
    
    if (!tempSession || tempSession.userId !== userId || tempSession.status !== 'pending_2fa') {
      await security.recordLoginFailure(userId, { ipAddress, userAgent, reason: 'invalid_session' });
      throw new ApiError(statusCodes.UNAUTHORIZED, '无效或已过期的会话');
    }
    
    // 查找用户
    const user = await userRepository.getUserById(userId);
    if (!user || !user.two_factor_enabled) {
      await security.recordLoginFailure(userId, { ipAddress, userAgent, reason: '2fa_not_enabled' });
      throw new ApiError(statusCodes.BAD_REQUEST, '用户未启用二因素认证');
    }
    
    // 验证二因素认证代码
    const { verifyTOTP, verifyRecoveryCode } = require('./two-factor.service');
    let isValid = false;
    let verifiedMethod = 'unknown';
    
    // 优先尝试TOTP
    if (user.two_factor_method === 'totp') {
      isValid = await verifyTOTP(userId, twoFactorCode);
      if(isValid) verifiedMethod = 'totp';
    }
    
    // 如果TOTP无效，尝试恢复码
    if (!isValid) {
      isValid = await verifyRecoveryCode(userId, twoFactorCode);
      if(isValid) verifiedMethod = 'recovery_code';
    }
    
    if (!isValid) {
      // 记录失败尝试
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.TWO_FACTOR_FAILED,
        { userId, method: user.two_factor_method, sessionId: tempSessionId }
      );
      await security.recordLoginFailure(userId, { ipAddress, userAgent, reason: 'invalid_2fa_code' });
      throw new ApiError(statusCodes.UNAUTHORIZED, '无效的二因素认证代码');
    }
    
    // 二因素认证成功，进行设备相关的安全检查
    const effectiveDeviceInfo = deviceInfo || tempSession.deviceInfo; // 优先使用请求中的设备信息
    
    const securityResult = await security.processLoginSecurity({
      userId,
      deviceInfo: effectiveDeviceInfo,
      ipAddress,
      userAgent,
      deviceId: effectiveDeviceInfo?.deviceId
    });
    
    // 如果需要设备验证
    if (securityResult.verificationRequired) {
      // 更新临时会话状态为等待设备验证
      await sessionService.updateSessionStatus(tempSessionId, 'pending_device_verification');
      
      // 更新会话中的设备信息指纹
      await sessionService.updateSessionDevice(tempSessionId, null, { 
        ...effectiveDeviceInfo, 
        fingerprint: securityResult.deviceFingerprint 
      });
      
      return {
        requiresDeviceVerification: true,
        verificationInfo: securityResult.verificationInfo,
        userId
      };
    }
    
    // 二因素认证和安全检查均通过，完成登录
    // 更新会话状态为活跃
    const sessionExpiresIn = rememberDevice ? 
      config.session.trustedDeviceDuration : 
      config.session.defaultDuration;
      
    await sessionService.updateSessionStatus(tempSessionId, 'active', sessionExpiresIn);
    
    // 处理设备注册和信任
    let finalDeviceId = null;
    if (effectiveDeviceInfo) {
      try {
        const deviceService = require('./device.service');
        const deviceResult = await deviceService.registerAndTrustDevice(
          userId, 
          { ...effectiveDeviceInfo, fingerprint: securityResult.deviceFingerprint }, 
          rememberDevice // 如果用户选择记住，则信任设备
        );
        finalDeviceId = deviceResult.id;
        // 更新会话中的设备ID
        await sessionService.updateSessionDevice(tempSessionId, finalDeviceId);
      } catch (deviceError) {
        logger.error(`2FA后设备处理失败: ${deviceError.message}`, { 
          error: deviceError, 
          userId 
        });
        // 设备处理失败不应阻止登录，但需要记录
      }
    }
    
    // 生成令牌
    const tokens = await tokenService.generateTokens(user, { 
      sessionId: tempSessionId, 
      deviceId: finalDeviceId 
    });
    
    // 更新用户最后登录时间
    await updateLastLogin(userId);
    
    // 记录成功事件
    await securityLogService.logSecurityEvent(
      securityLogService.EVENT_TYPES.TWO_FACTOR_VERIFIED,
      { userId, method: verifiedMethod, sessionId: tempSessionId }
    );
    await security.recordLoginSuccess(userId, { 
      ipAddress, 
      userAgent, 
      deviceId: finalDeviceId, 
      sessionId: tempSessionId 
    });

    return {
      user: userRepository.sanitizeUser(user),
      tokens,
      session: { id: tempSessionId, deviceId: finalDeviceId } // 返回会话信息
    };
  } catch (error) {
    logger.error(`二因素认证登录错误: ${error.message}`, { error, userId, tempSessionId });
    // 记录失败尝试（如果尚未记录）
    if (!(error instanceof ApiError && error.statusCode === statusCodes.UNAUTHORIZED)) {
        await security.recordLoginFailure(userId, { 
          ipAddress, 
          userAgent, 
          reason: '2fa_login_error' 
        });
    }
    throw error;
  }
};

/**
 * 根据ID查找用户
 * @param {string} userId 用户ID
 * @returns {Promise<Object>} 用户信息
 */
const findUserById = async (userId) => {
  try {
    const { db } = require('../config/database');
    const user = await db('users')
      .where('id', userId)
      .select('id', 'username', 'email', 'phone', 'role', 'status', 'two_factor_enabled')
      .first();
      
    return user;
  } catch (error) {
    logger.error(`查找用户错误: ${error.message}`, { error, userId });
    throw error;
  }
};

/**
 * 根据标识符查找用户（用户名、邮箱或手机号）
 * @param {string} identifier 用户标识符
 * @returns {Promise<Object>} 用户信息
 */
const findUserByIdentifier = async (identifier) => {
  try {
    const { db } = require('../config/database');
    const user = await db('users')
      .where('username', identifier)
      .orWhere('email', identifier)
      .orWhere('phone', identifier)
      .select('*')
      .first();
      
    return user;
  } catch (error) {
    logger.error(`查找用户错误: ${error.message}`, { error, identifier });
    throw error;
  }
};

/**
 * 更新用户最后登录时间
 * @param {string} userId 用户ID
 */
const updateLastLogin = async (userId) => {
  try {
    const { db } = require('../config/database');
    await db('users')
      .where('id', userId)
      .update({
        last_login_at: new Date(),
        updated_at: new Date()
      });
  } catch (error) {
    logger.error(`更新登录时间错误: ${error.message}`, { error, userId });
    // 不抛出错误，这不是关键操作
  }
};

const authService = {
  register,
  login,
  refreshToken,
  logout,
  forgotPassword,
  resetPassword,
  phoneLogin,
  registerByPhone,
  resetPasswordByPhone,
  updateUserPhone,
  checkPhoneExists,
  verifyTwoFactorAndLogin,
  findUserById,
  findUserByIdentifier
};

module.exports = authService; 
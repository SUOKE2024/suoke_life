/**
 * Token服务 - 管理令牌的生成、验证和撤销
 */
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const Redis = require('ioredis');
const config = require('../config');
const { logger } = require('@suoke/shared').utils;
const userService = require('./user.service');
const securityLogService = require('./security-log.service');

// 创建Redis客户端
const redis = new Redis({
  host: config.redis.host,
  port: config.redis.port
});

const tokenService = {
  /**
   * 生成访问令牌和刷新令牌
   * @param {Object} user 用户对象
   * @param {Object} options 选项
   * @param {string} options.sessionId 会话ID
   * @param {string} options.deviceId 设备ID
   * @param {string} options.clientId 客户端ID
   * @param {number} options.accessTokenExpiry 访问令牌过期时间（秒）
   * @param {number} options.refreshTokenExpiry 刷新令牌过期时间（秒）
   * @returns {Promise<Object>} 令牌对象
   */
  generateTokens: async (user, options = {}) => {
    try {
      // 创建JWT负载
      const jti = uuidv4(); // 令牌唯一标识符
      
      const accessTokenPayload = {
        sub: user.id,
        role: user.role,
        permissions: user.permissions,
        type: 'access',
        iat: Math.floor(Date.now() / 1000),
        jti: jti,
        iss: config.app.name || 'suoke-auth-service',
        aud: config.app.baseUrl || 'https://suoke.life'
      };
      
      // 如果提供了会话ID，添加到令牌中
      if (options.sessionId) {
        accessTokenPayload.sid = options.sessionId;
      }
      
      // 如果提供了设备ID，添加到令牌中
      if (options.deviceId) {
        accessTokenPayload.did = options.deviceId;
      }
      
      const refreshTokenPayload = {
        sub: user.id,
        type: 'refresh',
        iat: Math.floor(Date.now() / 1000),
        jti: uuidv4(),
        iss: config.app.name || 'suoke-auth-service',
        aud: config.app.baseUrl || 'https://suoke.life'
      };
      
      // 如果提供了会话ID，添加到刷新令牌中
      if (options.sessionId) {
        refreshTokenPayload.sid = options.sessionId;
      }
      
      // 如果提供了设备ID，添加到刷新令牌中
      if (options.deviceId) {
        refreshTokenPayload.did = options.deviceId;
      }
      
      // 设置过期时间
      const accessTokenExpiry = options.accessTokenExpiry || config.jwt.accessTokenExpiry || 24 * 60 * 60; // 默认24小时
      const refreshTokenExpiry = options.refreshTokenExpiry || config.jwt.refreshTokenExpiry || 7 * 24 * 60 * 60; // 默认7天
      
      accessTokenPayload.exp = Math.floor(Date.now() / 1000) + accessTokenExpiry;
      refreshTokenPayload.exp = Math.floor(Date.now() / 1000) + refreshTokenExpiry;
      
      // 生成令牌
      const accessToken = jwt.sign(accessTokenPayload, config.jwt.secret, {
        algorithm: 'HS256'
      });
      
      const refreshToken = jwt.sign(refreshTokenPayload, config.jwt.secret, {
        algorithm: 'HS256'
      });
      
      // 存储令牌关联信息到Redis，用于令牌撤销和会话管理
      const tokenKey = `token:${jti}`;
      const tokenData = {
        'userId': user.id,
        'clientId': options.clientId || 'default',
        'createdAt': new Date().toISOString(),
        'expiresAt': new Date(accessTokenPayload.exp * 1000).toISOString()
      };
      
      // 如果提供了会话ID，添加到令牌数据中
      if (options.sessionId) {
        tokenData.sessionId = options.sessionId;
      }
      
      // 如果提供了设备ID，添加到令牌数据中
      if (options.deviceId) {
        tokenData.deviceId = options.deviceId;
      }
      
      await redis.hmset(tokenKey, tokenData);
      await redis.expire(tokenKey, accessTokenExpiry);
      
      // 跟踪用户的活跃令牌
      await redis.sadd(`user_tokens:${user.id}`, jti);
      
      // 记录安全日志
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.TOKEN_ISSUED,
        {
          userId: user.id,
          tokenId: jti,
          sessionId: options.sessionId,
          deviceId: options.deviceId,
          expiresAt: new Date(accessTokenPayload.exp * 1000).toISOString()
        }
      );
      
      return { 
        accessToken, 
        refreshToken,
        expiresIn: accessTokenExpiry,
        refreshExpiresIn: refreshTokenExpiry,
        tokenType: 'Bearer',
        tokenId: jti
      };
    } catch (error) {
      logger.error(`生成令牌错误: ${error.message}`, { error });
      throw error;
    }
  },
  
  /**
   * 验证访问令牌
   * @param {string} accessToken 访问令牌
   * @returns {Promise<Object>} 解码后的负载
   */
  verifyAccessToken: async (accessToken) => {
    try {
      // 验证令牌
      const decoded = jwt.verify(accessToken, config.jwt.secret, {
        algorithms: ['HS256'],
        issuer: config.app.name || 'suoke-auth-service',
        audience: config.app.baseUrl || 'https://suoke.life'
      });
      
      // 检查令牌类型
      if (decoded.type !== 'access') {
        throw new Error('无效的令牌类型');
      }
      
      // 检查令牌是否在黑名单中
      if (decoded.jti) {
        const blacklisted = await redis.exists(`blacklist:${decoded.jti}`);
        if (blacklisted) {
          throw new Error('令牌已被撤销');
        }
      }
      
      return decoded;
    } catch (error) {
      logger.warn(`访问令牌验证失败: ${error.message}`, { error });
      throw error;
    }
  },
  
  /**
   * 验证刷新令牌
   * @param {string} refreshToken 刷新令牌
   * @returns {Promise<Object>} 解码后的负载
   */
  verifyRefreshToken: async (refreshToken) => {
    try {
      // 验证令牌
      const decoded = jwt.verify(refreshToken, config.jwt.secret, {
        algorithms: ['HS256'],
        issuer: config.app.name || 'suoke-auth-service',
        audience: config.app.baseUrl || 'https://suoke.life'
      });
      
      // 检查令牌类型
      if (decoded.type !== 'refresh') {
        throw new Error('无效的令牌类型');
      }
      
      // 检查令牌是否在黑名单中
      if (decoded.jti) {
        const blacklisted = await redis.exists(`blacklist:${decoded.jti}`);
        if (blacklisted) {
          throw new Error('令牌已被撤销');
        }
      }
      
      return decoded;
    } catch (error) {
      logger.warn(`刷新令牌验证失败: ${error.message}`, { error });
      throw error;
    }
  },
  
  /**
   * 撤销令牌
   * @param {string} token JWT令牌或令牌ID(jti)
   * @returns {Promise<boolean>} 是否成功撤销
   */
  revokeToken: async (token) => {
    try {
      let jti;
      
      // 检查参数是JWT令牌还是jti
      if (token.includes('.')) {
        // 如果包含点，视为JWT令牌并解码获取jti
        const decoded = jwt.decode(token);
        if (!decoded || !decoded.jti) {
          throw new Error('无效的令牌格式');
        }
        jti = decoded.jti;
      } else {
        // 直接使用作为jti
        jti = token;
      }
      
      // 计算剩余有效期
      const tokenData = await redis.hgetall(`token:${jti}`);
      if (!tokenData || !tokenData.expiresAt) {
        // 找不到令牌数据，可能已过期
        return false;
      }
      
      const expiresAt = new Date(tokenData.expiresAt).getTime() / 1000;
      const now = Math.floor(Date.now() / 1000);
      const remainingTime = expiresAt - now;
      
      // 如果令牌已过期，不需要加入黑名单
      if (remainingTime <= 0) {
        return true;
      }
      
      // 将令牌ID加入黑名单
      await redis.set(
        `blacklist:${jti}`,
        '1',
        'EX',
        Math.max(remainingTime + 60, 3600) // 至少保持1小时，避免时钟偏差问题
      );
      
      // 从用户的活跃令牌集合中移除
      if (tokenData.userId) {
        await redis.srem(`user_tokens:${tokenData.userId}`, jti);
      }
      
      return true;
    } catch (error) {
      logger.error(`撤销令牌错误: ${error.message}`, { error, token });
      return false;
    }
  },
  
  /**
   * 撤销用户的所有令牌
   * @param {string} userId 用户ID
   * @returns {Promise<number>} 撤销的令牌数量
   */
  revokeAllUserTokens: async (userId) => {
    try {
      // 获取用户的所有活跃令牌
      const tokenIds = await redis.smembers(`user_tokens:${userId}`);
      if (!tokenIds || tokenIds.length === 0) {
        return 0;
      }
      
      // 批量撤销所有令牌
      const revokePromises = tokenIds.map(jti => tokenService.revokeToken(jti));
      const results = await Promise.all(revokePromises);
      
      // 计算成功撤销的数量
      return results.filter(Boolean).length;
    } catch (error) {
      logger.error(`撤销用户所有令牌错误: ${error.message}`, { error, userId });
      return 0;
    }
  },
  
  /**
   * 生成密码重置令牌
   * @param {string} userId 用户ID
   * @param {string} email 用户邮箱
   * @returns {Promise<string>} 密码重置令牌
   */
  generatePasswordResetToken: async (userId, email) => {
    const jti = uuidv4();
    const payload = {
      sub: userId,
      email: email,
      type: 'reset',
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + (60 * 30), // 30分钟
      jti: jti,
      iss: config.app.name || 'suoke-auth-service',
      aud: config.app.baseUrl || 'https://suoke.life'
    };
    
    const token = jwt.sign(payload, config.jwt.secret, {
      algorithm: 'HS256'
    });
    
    // 记录密码重置令牌
    await redis.set(
      `password_reset:${userId}`,
      jti,
      'EX',
      60 * 30 // 30分钟
    );
    
    return token;
  },
  
  /**
   * 验证密码重置令牌
   * @param {string} token 密码重置令牌
   * @returns {Promise<Object>} 用户ID和邮箱
   */
  verifyPasswordResetToken: async (token) => {
    try {
      // 验证令牌
      const decoded = jwt.verify(token, config.jwt.secret, {
        algorithms: ['HS256'],
        issuer: config.app.name || 'suoke-auth-service',
        audience: config.app.baseUrl || 'https://suoke.life'
      });
      
      // 检查令牌类型
      if (decoded.type !== 'reset') {
        throw new Error('无效的令牌类型');
      }
      
      // 检查令牌是否在黑名单中
      if (decoded.jti) {
        const blacklisted = await redis.exists(`blacklist:${decoded.jti}`);
        if (blacklisted) {
          throw new Error('令牌已被使用');
        }
      }
      
      // 检查与存储的重置令牌是否匹配
      const storedJti = await redis.get(`password_reset:${decoded.sub}`);
      if (!storedJti || storedJti !== decoded.jti) {
        throw new Error('密码重置令牌已失效');
      }
      
      return {
        userId: decoded.sub,
        email: decoded.email
      };
    } catch (error) {
      logger.warn(`密码重置令牌验证失败: ${error.message}`, { error });
      throw error;
    }
  },
  
  /**
   * 使密码重置令牌失效
   * @param {string} userId 用户ID
   * @param {string} token 可选的令牌，如果提供则会被加入黑名单
   * @returns {Promise<boolean>} 是否成功使令牌失效
   */
  invalidatePasswordResetToken: async (userId, token = null) => {
    try {
      // 移除存储的重置令牌
      await redis.del(`password_reset:${userId}`);
      
      // 如果提供了令牌，将其加入黑名单
      if (token) {
        const decoded = jwt.decode(token);
        if (decoded && decoded.jti) {
          await redis.set(
            `blacklist:${decoded.jti}`,
            '1',
            'EX',
            60 * 60 // 保留1小时
          );
        }
      }
      
      return true;
    } catch (error) {
      logger.error(`使密码重置令牌失效错误: ${error.message}`, { error, userId });
      return false;
    }
  },
  
  /**
   * 刷新令牌 - 使用有效的刷新令牌生成新的访问令牌和刷新令牌
   * @param {string} refreshToken 刷新令牌
   * @returns {Promise<Object>} 新的令牌对象
   */
  refreshToken: async (refreshToken) => {
    try {
      // 验证刷新令牌
      const decoded = await tokenService.verifyRefreshToken(refreshToken);
      
      // 获取用户信息
      const user = await userService.getUserById(decoded.sub);
      if (!user) {
        throw new Error('用户不存在');
      }
      
      // 获取用户当前会话
      let sessionId = decoded.sid || null;
      let deviceId = decoded.did || null;
      
      // 准备选项
      const options = {
        clientId: user.clientId || 'default'
      };
      
      // 添加会话ID
      if (sessionId) {
        options.sessionId = sessionId;
      }
      
      // 添加设备ID
      if (deviceId) {
        options.deviceId = deviceId;
      }
      
      // 撤销旧的刷新令牌
      await tokenService.revokeToken(decoded.jti);
      
      // 生成新的令牌
      const tokens = await tokenService.generateTokens(user, options);
      
      // 记录刷新令牌事件
      await securityLogService.logSecurityEvent(
        securityLogService.EVENT_TYPES.TOKEN_REFRESHED, 
        {
          userId: user.id,
          tokenId: tokens.tokenId,
          sessionId: sessionId,
          deviceId: deviceId
        }
      );
      
      return tokens;
    } catch (error) {
      logger.error(`刷新令牌错误: ${error.message}`, { error });
      throw error;
    }
  }
};

module.exports = tokenService; 
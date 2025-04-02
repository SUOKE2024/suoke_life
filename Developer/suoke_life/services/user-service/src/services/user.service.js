/**
 * 用户服务
 */
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');
const { userRepository, sessionRepository } = require('../repositories');
const { logger } = require('@suoke/shared').utils;
const config = require('../config');
const { redisClient } = require('../utils/redis');
const { sendEmail } = require('../utils/email');
const { generateVerificationCode } = require('../utils/verification');
const { ApiError } = require('@suoke/shared').errors;

class UserService {
  /**
   * 用户注册
   */
  async register(userData) {
    try {
      // 检查用户名是否已存在
      const existingUser = await userRepository.findByUsername(userData.username);
      if (existingUser) {
        throw new ApiError('USERNAME_EXISTS', '用户名已存在');
      }

      // 检查邮箱是否已存在
      const existingEmail = await userRepository.findByEmail(userData.email);
      if (existingEmail) {
        throw new ApiError('EMAIL_EXISTS', '邮箱已被注册');
      }

      // 检查手机号是否已存在
      const existingPhone = await userRepository.findByPhone(userData.phone);
      if (existingPhone) {
        throw new ApiError('PHONE_EXISTS', '手机号已被注册');
      }

      // 加密密码
      const salt = await bcrypt.genSalt(10);
      const hashedPassword = await bcrypt.hash(userData.password, salt);

      // 创建用户
      const user = await userRepository.create({
        ...userData,
        password: hashedPassword,
        status: 'pending'
      });

      // 生成验证令牌
      const verificationToken = jwt.sign(
        { userId: user.id },
        config.jwt.secret,
        { expiresIn: '24h' }
      );

      // 发送验证邮件
      await sendEmail({
        to: user.email,
        subject: '验证您的邮箱',
        template: 'verification',
        context: {
          name: user.nickname,
          verificationUrl: `${config.app.frontendUrl}/verify-email?token=${verificationToken}`
        }
      });

      logger.info('用户注册成功', { userId: user.id });
      return user;
    } catch (error) {
      logger.error('用户注册失败', { error: error.message });
      throw error;
    }
  }

  /**
   * 用户登录
   */
  async login(loginData) {
    try {
      // 根据登录类型查找用户
      let user;
      switch (loginData.loginType) {
        case 'email':
          user = await userRepository.findByEmail(loginData.loginId);
          break;
        case 'phone':
          user = await userRepository.findByPhone(loginData.loginId);
          break;
        case 'username':
          user = await userRepository.findByUsername(loginData.loginId);
          break;
        default:
          throw new ApiError('INVALID_LOGIN_TYPE', '无效的登录类型');
      }

      if (!user) {
        throw new ApiError('USER_NOT_FOUND', '用户不存在');
      }

      // 验证密码
      const isValidPassword = await bcrypt.compare(loginData.password, user.password);
      if (!isValidPassword) {
        throw new ApiError('INVALID_PASSWORD', '密码错误');
      }

      // 检查用户状态
      if (user.status !== 'active') {
        throw new ApiError('USER_INACTIVE', '用户账号未激活');
      }

      // 创建会话
      const session = await sessionRepository.create({
        userId: user.id,
        deviceInfo: loginData.deviceInfo,
        ipAddress: loginData.ipAddress,
        userAgent: loginData.userAgent
      });

      // 生成令牌
      const tokens = await this.generateTokens(user, session.id);

      // 更新用户最后登录时间
      await userRepository.update(user.id, {
        lastLoginAt: new Date()
      });

      logger.info('用户登录成功', { userId: user.id });
      return {
        user,
        session,
        tokens
      };
    } catch (error) {
      logger.error('用户登录失败', { error: error.message });
      throw error;
    }
  }

  /**
   * 生成访问令牌和刷新令牌
   */
  async generateTokens(user, sessionId) {
    const accessToken = jwt.sign(
      {
        userId: user.id,
        sessionId,
        role: user.role
      },
      config.jwt.secret,
      { expiresIn: config.jwt.accessTokenExpiresIn }
    );

    const refreshToken = jwt.sign(
      {
        userId: user.id,
        sessionId
      },
      config.jwt.refreshSecret,
      { expiresIn: config.jwt.refreshTokenExpiresIn }
    );

    return {
      accessToken,
      refreshToken
    };
  }

  /**
   * 验证令牌
   */
  async verifyToken(token) {
    try {
      // 检查令牌是否在黑名单中
      const isBlacklisted = await redisClient.get(`blacklist:${token}`);
      if (isBlacklisted) {
        return false;
      }

      // 验证令牌
      const decoded = jwt.verify(token, config.jwt.secret);

      // 检查会话是否有效
      const session = await sessionRepository.findById(decoded.sessionId);
      if (!session || session.expiresAt < new Date()) {
        return false;
      }

      return true;
    } catch (error) {
      logger.error('令牌验证失败', { error: error.message });
      return false;
    }
  }

  /**
   * 用户登出
   */
  async logout(userId, sessionId) {
    try {
      // 删除会话
      await sessionRepository.delete(sessionId);

      // 将访问令牌加入黑名单
      const token = await redisClient.get(`session:${sessionId}:token`);
      if (token) {
        const decoded = jwt.decode(token);
        const ttl = decoded.exp - Math.floor(Date.now() / 1000);
        if (ttl > 0) {
          await redisClient.set(`blacklist:${token}`, '1', 'EX', ttl);
        }
      }

      logger.info('用户登出成功', { userId, sessionId });
      return true;
    } catch (error) {
      logger.error('用户登出失败', { error: error.message });
      throw error;
    }
  }

  /**
   * 获取用户会话列表
   */
  async getUserSessions(userId, options = {}) {
    try {
      const sessions = await sessionRepository.findByUserId(userId, options);
      return sessions;
    } catch (error) {
      logger.error('获取用户会话列表失败', { error: error.message });
      throw error;
    }
  }

  /**
   * 终止指定会话
   */
  async terminateSession(userId, sessionId) {
    try {
      const session = await sessionRepository.findById(sessionId);
      if (!session || session.userId !== userId) {
        throw new ApiError('SESSION_NOT_FOUND', '会话不存在');
      }

      await this.logout(userId, sessionId);
      logger.info('会话终止成功', { userId, sessionId });
      return true;
    } catch (error) {
      logger.error('终止会话失败', { error: error.message });
      throw error;
    }
  }

  /**
   * 终止用户所有会话
   */
  async terminateAllSessions(userId) {
    try {
      const sessions = await sessionRepository.findByUserId(userId);
      await Promise.all(sessions.map(session => this.logout(userId, session.id)));
      logger.info('终止用户所有会话成功', { userId });
      return true;
    } catch (error) {
      logger.error('终止用户所有会话失败', { error: error.message });
      throw error;
    }
  }

  /**
   * 根据ID获取用户
   */
  async getUserById(userId) {
    try {
      const user = await userRepository.findById(userId);
      if (!user) {
        throw new ApiError('USER_NOT_FOUND', '用户不存在');
      }
      return user;
    } catch (error) {
      logger.error('获取用户信息失败', { error: error.message });
      throw error;
    }
  }

  /**
   * 更新用户信息
   */
  async updateUser(userId, updateData) {
    try {
      // 如果更新密码,需要加密
      if (updateData.password) {
        const salt = await bcrypt.genSalt(10);
        updateData.password = await bcrypt.hash(updateData.password, salt);
      }

      const user = await userRepository.update(userId, updateData);
      logger.info('更新用户信息成功', { userId });
      return user;
    } catch (error) {
      logger.error('更新用户信息失败', { error: error.message });
      throw error;
    }
  }

  /**
   * 删除用户
   */
  async deleteUser(userId) {
    try {
      // 终止用户所有会话
      await this.terminateAllSessions(userId);

      // 删除用户
      await userRepository.delete(userId);
      logger.info('删除用户成功', { userId });
      return true;
    } catch (error) {
      logger.error('删除用户失败', { error: error.message });
      throw error;
    }
  }

  /**
   * 启用多因素认证
   */
  async enableMFA(userId) {
    try {
      const user = await userRepository.findById(userId);
      if (!user) {
        throw new Error('用户不存在');
      }

      // 生成MFA密钥
      const secret = speakeasy.generateSecret({
        length: 20,
        name: `索克生活:${user.email}`
      });

      // 生成备用码
      const backupCodes = Array.from({ length: 8 }, () => 
        Math.random().toString(36).substring(2, 8).toUpperCase()
      );

      // 更新用户MFA设置
      await userRepository.update(userId, {
        mfa_enabled: true,
        mfa_secret: secret.base32,
        mfa_backup_codes: backupCodes
      });

      // 生成二维码
      const qrCode = await QRCode.toDataURL(secret.otpauth_url);

      return {
        qrCode,
        backupCodes,
        secret: secret.base32
      };
    } catch (error) {
      logger.error('启用多因素认证失败', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * 禁用多因素认证
   */
  async disableMFA(userId) {
    try {
      const user = await userRepository.findById(userId);
      if (!user) {
        throw new Error('用户不存在');
      }

      // 更新用户MFA设置
      await userRepository.update(userId, {
        mfa_enabled: false,
        mfa_secret: null,
        mfa_backup_codes: null
      });

      return true;
    } catch (error) {
      logger.error('禁用多因素认证失败', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * 验证MFA码
   */
  verifyMFACode(secret, code) {
    return speakeasy.totp.verify({
      secret: secret,
      encoding: 'base32',
      token: code
    });
  }

  /**
   * 验证用户
   */
  async verifyUser(token) {
    try {
      // 检查令牌是否有效
      const user = await userRepository.checkVerificationToken(token);
      
      if (!user) {
        throw new Error('验证令牌无效或已过期');
      }

      // 更新用户状态为已验证
      const verifiedUser = await userRepository.verifyUser(user.id);

      // 如果配置了自动创建用户资料，则创建
      if (config.userManagement.healthProfile.autoCreateOnRegistration) {
        try {
          await healthProfileRepository.create({
            user_id: user.id,
            privacy_level: config.userManagement.healthProfile.privacyLevel
          });
        } catch (error) {
          logger.error('自动创建健康资料失败', { error: error.message, userId: user.id });
          // 不影响用户验证流程，继续执行
        }
      }

      // 返回用户数据（不包含敏感信息）
      const { password, verification_token, verification_expires, ...userWithoutSensitiveData } = verifiedUser;
      return userWithoutSensitiveData;
    } catch (error) {
      logger.error('用户验证失败', { error: error.message, token });
      throw error;
    }
  }

  /**
   * 重置密码
   */
  async resetPassword(email, newPassword) {
    try {
      // 查找用户
      const user = await userRepository.getByEmail(email);
      
      if (!user) {
        throw new Error('用户不存在');
      }

      // 哈希新密码
      const hashedPassword = await userModel.hashPassword(newPassword);

      // 更新密码
      await userRepository.update(user.id, { password: hashedPassword });

      return true;
    } catch (error) {
      logger.error('重置密码失败', { error: error.message, email });
      throw error;
    }
  }

  /**
   * 发送验证码
   */
  async sendVerificationCode(type, contact) {
    try {
      let user;
      
      // 根据类型查找用户
      if (type === 'email') {
        user = await userRepository.getByEmail(contact);
      } else if (type === 'phone') {
        user = await userRepository.getByPhone(contact);
      } else {
        throw new Error('不支持的验证类型');
      }

      if (!user) {
        throw new Error('用户不存在');
      }

      // 生成验证码，6位数字
      const verificationCode = Math.floor(100000 + Math.random() * 900000).toString();
      
      // 生成验证令牌，包含验证码信息
      const verificationData = {
        code: verificationCode,
        type,
        contact,
        userId: user.id
      };

      // 加密令牌数据
      const verificationToken = this.encryptVerificationData(verificationData);

      // 更新用户的验证令牌
      await userRepository.updateVerificationToken(user.id, verificationToken);
      
      // 这里应该调用实际的发送验证码逻辑，比如短信服务或邮件服务
      // 在实际环境中要替换为真实的实现
      logger.info('发送验证码', { type, contact, code: verificationCode });

      return {
        success: true,
        message: `验证码已发送至${type === 'email' ? '邮箱' : '手机'}`,
        // 注意：实际生产环境中不应返回验证码，这里仅用于测试
        code: process.env.NODE_ENV === 'development' ? verificationCode : undefined
      };
    } catch (error) {
      logger.error('发送验证码失败', { error: error.message, type, contact });
      throw error;
    }
  }

  /**
   * 验证验证码
   */
  async verifyCode(token, code) {
    try {
      // 检查令牌是否有效
      const user = await userRepository.checkVerificationToken(token);
      
      if (!user) {
        throw new Error('验证令牌无效或已过期');
      }

      // 解密令牌数据
      const verificationData = this.decryptVerificationData(token);
      
      // 检查验证码是否匹配
      if (verificationData.code !== code) {
        throw new Error('验证码错误');
      }

      // 验证成功，清除验证令牌
      await userRepository.update(user.id, { 
        verification_token: null,
        verification_expires: null
      });

      return {
        success: true,
        userId: user.id
      };
    } catch (error) {
      logger.error('验证码验证失败', { error: error.message, token });
      throw error;
    }
  }

  /**
   * 获取用户信息
   */
  async getUserInfo(userId) {
    try {
      // 获取用户基本信息
      const user = await userRepository.getById(userId);
      
      if (!user) {
        throw new Error('用户不存在');
      }

      // 获取用户资料
      const profile = await profileRepository.getByUserId(userId);
      
      // 获取用户健康资料
      const healthProfile = await healthProfileRepository.getByUserId(userId);

      // 返回用户信息（不包含敏感信息）
      const { password, verification_token, verification_expires, ...userWithoutSensitiveData } = user;
      
      return {
        user: userWithoutSensitiveData,
        profile,
        healthProfile
      };
    } catch (error) {
      logger.error('获取用户信息失败', { error: error.message, userId });
      throw error;
    }
  }

  /**
   * 加密验证数据
   */
  encryptVerificationData(data) {
    // 简单实现，实际应该使用更安全的加密方式
    return Buffer.from(JSON.stringify(data)).toString('base64');
  }

  /**
   * 解密验证数据
   */
  decryptVerificationData(token) {
    try {
      // 简单实现，实际应该使用更安全的解密方式
      return JSON.parse(Buffer.from(token, 'base64').toString('utf8'));
    } catch (error) {
      logger.error('解密验证数据失败', { error: error.message });
      throw new Error('无效的验证数据');
    }
  }
}

module.exports = new UserService(); 
/**
 * 优化的OAuth认证服务
 */
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');
const { logger } = require('@suoke/shared').utils;
const userCacheRepository = require('../repositories/user-cache.repository');
const tokenService = require('./token.service');
const cacheService = require('./cache.service');

// 缓存相关常量
const STATE_TTL = 10 * 60; // 状态码有效期10分钟
const TOKEN_CACHE_TTL = 30 * 60; // OAuth令牌缓存30分钟
const PROFILE_CACHE_TTL = 60 * 60; // 用户资料缓存1小时

/**
 * 优化的OAuth服务
 */
const oauthOptimizedService = {
  /**
   * 生成OAuth状态
   * 
   * @param {Object} stateData - 状态数据
   * @returns {Promise<string>} 状态码
   */
  async generateState(stateData = {}) {
    const state = uuidv4();
    const stateObj = {
      ...stateData,
      state,
      timestamp: Date.now()
    };
    
    // 缓存状态
    await cacheService.set(`oauth:state:${state}`, stateObj, STATE_TTL);
    
    return state;
  },
  
  /**
   * 验证OAuth状态
   * 
   * @param {string} state - 状态码
   * @returns {Promise<Object|null>} 状态数据
   */
  async verifyState(state) {
    if (!state) {
      return null;
    }
    
    const stateObj = await cacheService.get(`oauth:state:${state}`);
    
    if (!stateObj) {
      return null;
    }
    
    // 删除已使用的状态
    await cacheService.del(`oauth:state:${state}`);
    
    // 检查状态是否过期
    const now = Date.now();
    if (now - stateObj.timestamp > STATE_TTL * 1000) {
      return null;
    }
    
    return stateObj;
  },
  
  /**
   * 处理微信OAuth认证
   * 
   * @param {string} code - 授权码
   * @returns {Promise<Object>} 用户信息和令牌
   */
  async handleWechatOAuth(code) {
    try {
      // 尝试从缓存获取令牌
      const cachedToken = await cacheService.get(`oauth:wechat:token:${code}`);
      
      let accessToken, openId;
      if (cachedToken) {
        accessToken = cachedToken.access_token;
        openId = cachedToken.openid;
      } else {
        // 获取访问令牌
        const tokenResponse = await axios.get('https://api.weixin.qq.com/sns/oauth2/access_token', {
          params: {
            appid: process.env.WECHAT_APP_ID,
            secret: process.env.WECHAT_APP_SECRET,
            code,
            grant_type: 'authorization_code'
          }
        });
        
        if (tokenResponse.data.errcode) {
          throw new Error(`微信OAuth错误: ${tokenResponse.data.errmsg}`);
        }
        
        accessToken = tokenResponse.data.access_token;
        openId = tokenResponse.data.openid;
        
        // 缓存令牌
        await cacheService.set(`oauth:wechat:token:${code}`, tokenResponse.data, TOKEN_CACHE_TTL);
      }
      
      // 尝试从缓存获取用户资料
      const cachedProfile = await cacheService.get(`oauth:wechat:profile:${openId}`);
      
      let userProfile;
      if (cachedProfile) {
        userProfile = cachedProfile;
      } else {
        // 获取用户信息
        const userInfoResponse = await axios.get('https://api.weixin.qq.com/sns/userinfo', {
          params: {
            access_token: accessToken,
            openid: openId,
            lang: 'zh_CN'
          }
        });
        
        if (userInfoResponse.data.errcode) {
          throw new Error(`微信获取用户信息错误: ${userInfoResponse.data.errmsg}`);
        }
        
        userProfile = userInfoResponse.data;
        
        // 缓存用户资料
        await cacheService.set(`oauth:wechat:profile:${openId}`, userProfile, PROFILE_CACHE_TTL);
      }
      
      // 查找或创建用户
      let user = await userCacheRepository.getUserByUsername(`wechat_${openId}`);
      
      if (!user) {
        // 创建新用户
        user = await userCacheRepository.createUser({
          username: `wechat_${openId}`,
          email: `${openId}@wechat.user`,
          password: uuidv4(), // 生成随机密码
          provider: 'wechat',
          provider_id: openId,
          name: userProfile.nickname,
          avatar: userProfile.headimgurl
        });
      }
      
      // 生成JWT令牌
      const tokens = await tokenService.generateTokens({ userId: user.id });
      
      return {
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
        user: {
          id: user.id,
          username: user.username,
          name: user.name,
          avatar: user.avatar,
          provider: 'wechat'
        }
      };
    } catch (error) {
      logger.error(`微信OAuth处理失败: ${error.message}`);
      throw error;
    }
  },
  
  /**
   * 处理支付宝OAuth认证
   * 
   * @param {string} authCode - 授权码
   * @returns {Promise<Object>} 用户信息和令牌
   */
  async handleAlipayOAuth(authCode) {
    // 类似微信OAuth的实现...
    // 此处省略具体实现，实际使用中需要按照支付宝OAuth流程实现
    throw new Error('支付宝OAuth暂未实现');
  },
  
  /**
   * 处理Google OAuth认证
   * 
   * @param {string} code - 授权码
   * @param {string} redirectUri - 重定向URI
   * @returns {Promise<Object>} 用户信息和令牌
   */
  async handleGoogleOAuth(code, redirectUri) {
    try {
      // 尝试从缓存获取令牌
      const cacheKey = `oauth:google:token:${code}`;
      const cachedToken = await cacheService.get(cacheKey);
      
      let tokenData;
      if (cachedToken) {
        tokenData = cachedToken;
      } else {
        // 获取访问令牌
        const tokenResponse = await axios.post('https://oauth2.googleapis.com/token', {
          code,
          client_id: process.env.GOOGLE_CLIENT_ID,
          client_secret: process.env.GOOGLE_CLIENT_SECRET,
          redirect_uri: redirectUri,
          grant_type: 'authorization_code'
        });
        
        tokenData = tokenResponse.data;
        
        // 缓存令牌
        await cacheService.set(cacheKey, tokenData, TOKEN_CACHE_TTL);
      }
      
      // 使用令牌获取用户信息
      const userInfoResponse = await axios.get('https://www.googleapis.com/oauth2/v3/userinfo', {
        headers: {
          Authorization: `Bearer ${tokenData.access_token}`
        }
      });
      
      const userProfile = userInfoResponse.data;
      
      // 缓存用户资料
      await cacheService.set(`oauth:google:profile:${userProfile.sub}`, userProfile, PROFILE_CACHE_TTL);
      
      // 查找或创建用户
      let user = await userCacheRepository.getUserByEmail(userProfile.email);
      
      if (!user) {
        // 创建新用户
        user = await userCacheRepository.createUser({
          username: `google_${userProfile.sub}`,
          email: userProfile.email,
          password: uuidv4(), // 生成随机密码
          provider: 'google',
          provider_id: userProfile.sub,
          name: userProfile.name,
          avatar: userProfile.picture
        });
      } else if (user.provider !== 'google') {
        // 更新现有用户，链接Google账号
        user = await userCacheRepository.updateUser(user.id, {
          provider: 'google',
          provider_id: userProfile.sub,
          avatar: user.avatar || userProfile.picture
        });
      }
      
      // 生成JWT令牌
      const tokens = await tokenService.generateTokens({ userId: user.id });
      
      return {
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          name: user.name,
          avatar: user.avatar,
          provider: 'google'
        }
      };
    } catch (error) {
      logger.error(`Google OAuth处理失败: ${error.message}`);
      throw error;
    }
  },
  
  /**
   * 使用令牌信息链接OAuth账号
   * 
   * @param {string} userId - 用户ID
   * @param {string} provider - 提供商
   * @param {string} providerId - 提供商ID
   * @param {Object} profile - 用户资料
   * @returns {Promise<Object>} 更新后的用户
   */
  async linkOAuthAccount(userId, provider, providerId, profile) {
    try {
      // 更新用户信息
      const user = await userCacheRepository.updateUser(userId, {
        provider,
        provider_id: providerId,
        name: profile.name || user.name,
        avatar: profile.avatar || user.avatar
      });
      
      return user;
    } catch (error) {
      logger.error(`链接OAuth账号失败: ${error.message}`);
      throw error;
    }
  },
  
  /**
   * 解除OAuth账号链接
   * 
   * @param {string} userId - 用户ID
   * @returns {Promise<Object>} 更新后的用户
   */
  async unlinkOAuthAccount(userId) {
    try {
      // 清除OAuth相关信息
      const user = await userCacheRepository.updateUser(userId, {
        provider: null,
        provider_id: null
      });
      
      return user;
    } catch (error) {
      logger.error(`解除OAuth账号链接失败: ${error.message}`);
      throw error;
    }
  }
};

module.exports = oauthOptimizedService; 
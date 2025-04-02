/**
 * OAuth相关路由
 */
const express = require('express');
const passport = require('passport');
const { responseHandler } = require('@suoke/shared').utils;
const authService = require('../services/auth.service');
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');
const oauthService = require('../services/oauth');
const userRepository = require('../models/repositories/user.repository');
const redisClient = require('../utils/redis');
const logger = require('../utils/logger');
const { getClientInfo } = require('../utils/request-utils');
const { ValidationError } = require('../utils/errors');
const config = require('../config');

const router = express.Router();

// OAuth状态缓存前缀
const OAUTH_STATE_PREFIX = 'oauth:state:';
// OAuth状态有效期（秒）
const OAUTH_STATE_EXPIRES = 600; // 10分钟

/**
 * @route GET /api/v1/oauth/google
 * @desc Google OAuth登录
 * @access 公开
 */
router.get('/google', (req, res, next) => {
  // 实际上这里应该使用passport-google-oauth20，但为了简化示例，仅提供路由
  // 在生产环境下，这里应该调用passport.authenticate('google', { scope: ['profile', 'email'] })
  res.status(501).json({ message: 'Google OAuth功能尚未完全实现' });
});

/**
 * @route GET /api/v1/oauth/google/callback
 * @desc Google OAuth回调
 * @access 公开
 */
router.get('/google/callback', (req, res, next) => {
  // 实际上这里应该使用passport.authenticate('google', { failureRedirect: '/login' })
  // 在生产环境下，这里应该处理回调并生成令牌
  res.status(501).json({ message: 'Google OAuth回调功能尚未完全实现' });
});

/**
 * @route GET /api/auth/oauth/providers
 * @desc 获取所有可用的OAuth提供商
 * @access 公开
 */
router.get('/providers', (req, res) => {
  try {
    // 获取已启用的提供商
    const enabledProviders = oauthService.getEnabledProviders();
    
    const providers = [
      {
        name: 'wechat',
        displayName: '微信',
        url: '/api/auth/oauth/wechat/authorize',
        icon: '/assets/icons/wechat.svg',
        isAvailable: enabledProviders.includes('wechat')
      },
      {
        name: 'alipay',
        displayName: '支付宝',
        url: '/api/auth/oauth/alipay/authorize',
        icon: '/assets/icons/alipay.svg',
        isAvailable: enabledProviders.includes('alipay')
      }
    ];

    return res.status(200).json({
      success: true,
      data: providers
    });
  } catch (error) {
    logger.error(`获取OAuth提供商错误: ${error.message}`, { error });
    return res.status(500).json({
      success: false,
      message: '获取OAuth提供商失败'
    });
  }
});

/**
 * 微信OAuth授权
 * @route GET /wechat/authorize
 */
router.get('/wechat/authorize', async (req, res) => {
  try {
    if (!oauthService.isProviderEnabled('wechat')) {
      return res.status(400).json({
        success: false,
        message: '微信登录功能未启用'
      });
    }
    
    // 生成状态参数防止CSRF攻击
    const state = uuidv4();
    
    // 获取重定向地址
    const redirectUri = req.query.redirect_uri || config.oauth.wechat.callbackUrl;
    
    // 保存状态和重定向URI到Redis
    const stateData = {
      redirect_uri: redirectUri,
      created_at: Date.now()
    };
    
    await redisClient.set(
      `${OAUTH_STATE_PREFIX}${state}`, 
      JSON.stringify(stateData), 
      'EX', 
      OAUTH_STATE_EXPIRES
    );
    
    // 获取授权URL
    const provider = oauthService.getProvider('wechat');
    const authUrl = provider.getAuthorizationUrl(redirectUri, state);
    
    // 重定向到授权页面
    res.redirect(authUrl);
  } catch (error) {
    logger.error(`微信OAuth授权错误: ${error.message}`, { error });
    
    res.status(500).json({
      success: false,
      message: '微信授权过程发生错误，请稍后再试'
    });
  }
});

/**
 * 微信OAuth回调
 * @route GET /wechat/callback
 */
router.get('/wechat/callback', async (req, res) => {
  try {
    const { code, state, error, error_description } = req.query;
    
    // 检查错误
    if (error) {
      logger.warn(`微信OAuth回调错误: ${error} - ${error_description}`);
      return res.redirect(`/auth/error?error=${encodeURIComponent(error_description || error)}`);
    }
    
    // 验证状态参数
    if (!state) {
      return res.redirect('/auth/error?error=无效的授权请求');
    }
    
    // 从Redis获取状态数据
    const stateDataStr = await redisClient.get(`${OAUTH_STATE_PREFIX}${state}`);
    
    if (!stateDataStr) {
      return res.redirect('/auth/error?error=授权会话已过期或无效');
    }
    
    const stateData = JSON.parse(stateDataStr);
    
    // 验证授权码
    if (!code) {
      return res.redirect('/auth/error?error=未收到授权码');
    }
    
    // 删除Redis中的状态数据
    await redisClient.del(`${OAUTH_STATE_PREFIX}${state}`);
    
    // 交换授权码获取令牌
    const provider = oauthService.getProvider('wechat');
    const tokenInfo = await provider.exchangeCodeForToken(code, stateData.redirect_uri);
    
    // 获取用户信息
    const userProfile = await provider.getUserProfile(tokenInfo.accessToken, tokenInfo.openId);
    
    // 查找或创建用户
    const user = await findOrCreateOAuthUser('wechat', userProfile);
    
    // 获取客户端信息
    const clientInfo = getClientInfo(req);
    
    // 生成JWT令牌
    const authData = await authService.generateTokens(user, clientInfo);
    
    // 构建成功重定向URL
    const clientRedirectUri = stateData.redirect_uri || '/auth/success';
    let redirectUrl = clientRedirectUri;
    
    if (redirectUrl.includes('?')) {
      redirectUrl += '&';
    } else {
      redirectUrl += '?';
    }
    
    redirectUrl += `token=${encodeURIComponent(authData.accessToken)}`;
    redirectUrl += `&token_type=${encodeURIComponent(authData.tokenType)}`;
    redirectUrl += `&expires_in=${encodeURIComponent(authData.expiresIn)}`;
    
    // 重定向回客户端
    res.redirect(redirectUrl);
  } catch (error) {
    logger.error(`微信OAuth回调处理错误: ${error.message}`, { error });
    
    const errorMessage = error instanceof ValidationError
      ? error.message
      : '微信授权过程发生错误，请稍后再试';
    
    res.redirect(`/auth/error?error=${encodeURIComponent(errorMessage)}`);
  }
});

/**
 * 支付宝OAuth授权
 * @route GET /alipay/authorize
 */
router.get('/alipay/authorize', async (req, res) => {
  try {
    if (!oauthService.isProviderEnabled('alipay')) {
      return res.status(400).json({
        success: false,
        message: '支付宝登录功能未启用'
      });
    }
    
    // 生成状态参数防止CSRF攻击
    const state = uuidv4();
    
    // 获取重定向地址
    const redirectUri = req.query.redirect_uri || config.oauth.alipay.callbackUrl;
    
    // 保存状态和重定向URI到Redis
    const stateData = {
      redirect_uri: redirectUri,
      created_at: Date.now()
    };
    
    await redisClient.set(
      `${OAUTH_STATE_PREFIX}${state}`, 
      JSON.stringify(stateData), 
      'EX', 
      OAUTH_STATE_EXPIRES
    );
    
    // 获取授权URL
    const provider = oauthService.getProvider('alipay');
    const authUrl = provider.getAuthorizationUrl(redirectUri, state);
    
    // 重定向到授权页面
    res.redirect(authUrl);
  } catch (error) {
    logger.error(`支付宝OAuth授权错误: ${error.message}`, { error });
    
    res.status(500).json({
      success: false,
      message: '支付宝授权过程发生错误，请稍后再试'
    });
  }
});

/**
 * 支付宝OAuth回调
 * @route GET /alipay/callback
 */
router.get('/alipay/callback', async (req, res) => {
  try {
    const { code, state, error, error_description } = req.query;
    
    // 检查错误
    if (error) {
      logger.warn(`支付宝OAuth回调错误: ${error} - ${error_description}`);
      return res.redirect(`/auth/error?error=${encodeURIComponent(error_description || error)}`);
    }
    
    // 验证状态参数
    if (!state) {
      return res.redirect('/auth/error?error=无效的授权请求');
    }
    
    // 从Redis获取状态数据
    const stateDataStr = await redisClient.get(`${OAUTH_STATE_PREFIX}${state}`);
    
    if (!stateDataStr) {
      return res.redirect('/auth/error?error=授权会话已过期或无效');
    }
    
    const stateData = JSON.parse(stateDataStr);
    
    // 验证授权码
    if (!code) {
      return res.redirect('/auth/error?error=未收到授权码');
    }
    
    // 删除Redis中的状态数据
    await redisClient.del(`${OAUTH_STATE_PREFIX}${state}`);
    
    // 交换授权码获取令牌
    const provider = oauthService.getProvider('alipay');
    const tokenInfo = await provider.exchangeCodeForToken(code, stateData.redirect_uri);
    
    // 获取用户信息
    const userProfile = await provider.getUserProfile(tokenInfo.accessToken);
    
    // 查找或创建用户
    const user = await findOrCreateOAuthUser('alipay', userProfile);
    
    // 获取客户端信息
    const clientInfo = getClientInfo(req);
    
    // 生成JWT令牌
    const authData = await authService.generateTokens(user, clientInfo);
    
    // 构建成功重定向URL
    const clientRedirectUri = stateData.redirect_uri || '/auth/success';
    let redirectUrl = clientRedirectUri;
    
    if (redirectUrl.includes('?')) {
      redirectUrl += '&';
    } else {
      redirectUrl += '?';
    }
    
    redirectUrl += `token=${encodeURIComponent(authData.accessToken)}`;
    redirectUrl += `&token_type=${encodeURIComponent(authData.tokenType)}`;
    redirectUrl += `&expires_in=${encodeURIComponent(authData.expiresIn)}`;
    
    // 重定向回客户端
    res.redirect(redirectUrl);
  } catch (error) {
    logger.error(`支付宝OAuth回调处理错误: ${error.message}`, { error });
    
    const errorMessage = error instanceof ValidationError
      ? error.message
      : '支付宝授权过程发生错误，请稍后再试';
    
    res.redirect(`/auth/error?error=${encodeURIComponent(errorMessage)}`);
  }
});

/**
 * 查找或创建OAuth用户
 * @param {string} provider - OAuth提供商
 * @param {Object} profile - 用户信息
 * @returns {Promise<Object>} 用户对象
 */
async function findOrCreateOAuthUser(provider, profile) {
  try {
    // 查找是否已存在关联的用户
    let user = await userRepository.findByOAuthId(provider, profile.id);
    
    // 如果用户已存在，更新OAuth信息
    if (user) {
      const updateData = {
        oauth_info: {
          ...user.oauth_info,
          [provider]: {
            id: profile.id,
            profile_url: profile.avatar,
            updated_at: new Date()
          }
        },
        updated_at: new Date(),
        last_login: new Date()
      };
      
      await userRepository.update(user.id, updateData);
      
      // 重新获取更新后的用户
      user = await userRepository.findById(user.id);
    } else {
      // 创建新用户
      const newUser = {
        id: uuidv4(),
        username: `${provider}_${profile.id.substring(0, 8)}`,
        name: profile.name || profile.nickname || `${provider}用户`,
        role: 'user',
        is_active: true,
        oauth_provider: provider,
        oauth_id: profile.id,
        oauth_info: {
          [provider]: {
            id: profile.id,
            profile_url: profile.avatar,
            created_at: new Date(),
            updated_at: new Date()
          }
        },
        avatar: profile.avatar,
        created_at: new Date(),
        updated_at: new Date(),
        last_login: new Date()
      };
      
      // 检查用户名是否重复，如果重复则添加随机数
      const existingUser = await userRepository.findByUsername(newUser.username);
      if (existingUser) {
        newUser.username = `${newUser.username}_${Math.floor(Math.random() * 1000)}`;
      }
      
      user = await userRepository.create(newUser);
      logger.info(`已创建新的OAuth用户: ${provider} - ${profile.id}`);
    }
    
    return user;
  } catch (error) {
    logger.error(`查找或创建OAuth用户失败: ${error.message}`, { error });
    throw new Error(`OAuth用户处理失败: ${error.message}`);
  }
}

module.exports = router; 
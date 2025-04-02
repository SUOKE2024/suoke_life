/**
 * OAuth提供商服务索引
 * 整合所有OAuth提供商
 */
const config = require('../../config');
const logger = require('../../utils/logger');

// 导入OAuth提供商
const wechatProvider = require('./wechat.provider');
const alipayProvider = require('./alipay.provider');

// 将来可能添加的更多提供商
// const douyinProvider = require('./douyin.provider');
// const xiaohongshuProvider = require('./xiaohongshu.provider');
// const appleProvider = require('./apple.provider');
// const facebookProvider = require('./facebook.provider');
// const youtubeProvider = require('./youtube.provider');
// const tiktokProvider = require('./tiktok.provider');

class OAuthService {
  constructor() {
    // 初始化提供商映射
    this.providers = {
      wechat: wechatProvider,
      alipay: alipayProvider
      // 未来支持更多提供商时添加到这里
      // douyin: douyinProvider,
      // xiaohongshu: xiaohongshuProvider,
      // apple: appleProvider,
      // facebook: facebookProvider, 
      // youtube: youtubeProvider,
      // tiktok: tiktokProvider
    };
    
    // 获取已启用的提供商列表
    this.enabledProviders = this._getEnabledProviders();
    
    // 记录已加载的提供商
    logger.info(`OAuth服务已初始化，已启用的提供商: ${this.enabledProviders.join(', ')}`);
  }
  
  /**
   * 获取指定提供商
   * @param {string} providerName - 提供商名称
   * @returns {Object} 提供商实例
   * @throws {Error} 如果提供商不存在或未启用
   */
  getProvider(providerName) {
    if (!this.providers[providerName]) {
      throw new Error(`未知的OAuth提供商: ${providerName}`);
    }
    
    if (!this.enabledProviders.includes(providerName)) {
      throw new Error(`OAuth提供商 ${providerName} 未启用`);
    }
    
    return this.providers[providerName];
  }
  
  /**
   * 获取所有已启用的提供商名称
   * @returns {Array<string>} 已启用的提供商名称列表
   */
  getEnabledProviders() {
    return [...this.enabledProviders];
  }
  
  /**
   * 检查提供商是否已启用
   * @param {string} providerName - 提供商名称
   * @returns {boolean} 是否已启用
   */
  isProviderEnabled(providerName) {
    return this.enabledProviders.includes(providerName);
  }
  
  /**
   * 获取提供商的授权URL
   * @param {string} providerName - 提供商名称
   * @param {string} redirectUri - 回调地址
   * @param {string} state - 状态参数
   * @returns {string} 授权URL
   */
  getAuthorizationUrl(providerName, redirectUri, state) {
    const provider = this.getProvider(providerName);
    return provider.getAuthorizationUrl(redirectUri, state);
  }
  
  /**
   * 交换授权码获取令牌
   * @param {string} providerName - 提供商名称
   * @param {string} code - 授权码
   * @param {string} redirectUri - 回调地址
   * @returns {Promise<Object>} 令牌信息
   */
  async exchangeCodeForToken(providerName, code, redirectUri) {
    const provider = this.getProvider(providerName);
    return provider.exchangeCodeForToken(code, redirectUri);
  }
  
  /**
   * 获取用户信息
   * @param {string} providerName - 提供商名称
   * @param {string} accessToken - 访问令牌
   * @param {string} [openId] - 开放ID (仅部分提供商需要，如微信)
   * @returns {Promise<Object>} 用户信息
   */
  async getUserProfile(providerName, accessToken, openId) {
    const provider = this.getProvider(providerName);
    
    // 针对不同提供商的特殊处理
    if (providerName === 'wechat') {
      if (!openId) {
        throw new Error('微信获取用户信息需要提供openId');
      }
      return provider.getUserProfile(accessToken, openId);
    }
    
    return provider.getUserProfile(accessToken);
  }
  
  /**
   * 获取启用的提供商列表
   * @private
   * @returns {Array<string>} 已启用的提供商名称列表
   */
  _getEnabledProviders() {
    const enabledProviders = [];
    const oauthConfig = config.oauth?.providers || {};
    
    // 如果存在EnabledProviders配置，直接使用
    const configuredProviders = config.oauth2?.enabledProviders;
    if (configuredProviders && typeof configuredProviders === 'string') {
      const providers = configuredProviders.split(',').map(p => p.trim());
      
      // 过滤已实现的提供商
      return providers.filter(p => this.providers[p]);
    }
    
    // 否则检查每个提供商的配置
    for (const [name, provider] of Object.entries(this.providers)) {
      const providerConfig = oauthConfig[name];
      if (providerConfig && providerConfig.enabled !== false && 
          providerConfig.clientId && providerConfig.clientSecret) {
        enabledProviders.push(name);
      }
    }
    
    return enabledProviders;
  }
}

module.exports = new OAuthService(); 
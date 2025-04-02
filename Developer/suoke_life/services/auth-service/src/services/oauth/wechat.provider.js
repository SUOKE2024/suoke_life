/**
 * 微信OAuth认证提供商
 */
const axios = require('axios');
const config = require('../../config');
const logger = require('../../utils/logger');
const { ValidationError } = require('../../utils/errors');

class WechatOAuthProvider {
  constructor() {
    this.providerName = 'wechat';
    this.providerConfig = config.oauth?.providers?.wechat || {};
    
    // 必要参数检查
    if (!this.providerConfig.clientId || !this.providerConfig.clientSecret) {
      logger.warn('微信OAuth配置缺失，微信登录功能将不可用');
    }
    
    // 微信API端点
    this.endpoints = {
      authorize: 'https://open.weixin.qq.com/connect/qrconnect',
      accessToken: 'https://api.weixin.qq.com/sns/oauth2/access_token',
      userInfo: this.providerConfig.userProfileURL || 'https://api.weixin.qq.com/sns/userinfo',
      check: 'https://api.weixin.qq.com/sns/auth',
      refresh: 'https://api.weixin.qq.com/sns/oauth2/refresh_token'
    };
  }
  
  /**
   * 获取授权URL
   * @param {string} redirectUri - 回调地址
   * @param {string} state - 状态参数
   * @returns {string} 授权URL
   */
  getAuthorizationUrl(redirectUri, state) {
    // 微信使用 redirect_uri 而不是 redirect_url
    const queryParams = new URLSearchParams({
      appid: this.providerConfig.clientId,
      redirect_uri: redirectUri,
      response_type: 'code',
      scope: this.providerConfig.scope?.join(',') || 'snsapi_login',
      state: state
    });
    
    return `${this.endpoints.authorize}?${queryParams.toString()}#wechat_redirect`;
  }
  
  /**
   * 交换授权码获取令牌
   * @param {string} code - 授权码
   * @param {string} redirectUri - 回调地址
   * @returns {Promise<Object>} 令牌信息
   */
  async exchangeCodeForToken(code, redirectUri) {
    try {
      // 微信不需要redirectUri参数
      const response = await axios.get(this.endpoints.accessToken, {
        params: {
          appid: this.providerConfig.clientId,
          secret: this.providerConfig.clientSecret,
          code: code,
          grant_type: 'authorization_code'
        }
      });
      
      const data = response.data;
      
      if (data.errcode) {
        logger.error(`微信授权码交换失败: ${data.errmsg}`, { error: data });
        throw new ValidationError(`微信授权失败: ${data.errmsg}`);
      }
      
      return {
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        openId: data.openid,
        unionId: data.unionid, // 可能不存在
        expiresIn: data.expires_in,
        scope: data.scope,
        tokenType: 'Bearer',
        raw: data
      };
    } catch (error) {
      logger.error(`微信授权码交换异常: ${error.message}`, { error });
      if (error instanceof ValidationError) {
        throw error;
      }
      throw new ValidationError('微信授权失败，请稍后再试');
    }
  }
  
  /**
   * 获取用户信息
   * @param {string} accessToken - 访问令牌
   * @param {string} openId - 微信开放ID
   * @returns {Promise<Object>} 用户信息
   */
  async getUserProfile(accessToken, openId) {
    try {
      const response = await axios.get(this.endpoints.userInfo, {
        params: {
          access_token: accessToken,
          openid: openId,
          lang: 'zh_CN'
        }
      });
      
      const data = response.data;
      
      if (data.errcode) {
        logger.error(`微信获取用户信息失败: ${data.errmsg}`, { error: data });
        throw new ValidationError(`获取微信用户信息失败: ${data.errmsg}`);
      }
      
      // 格式化用户信息
      return {
        id: data.openid,
        unionId: data.unionid, // 可能不存在
        name: data.nickname,
        nickname: data.nickname,
        avatar: data.headimgurl,
        gender: this._mapGender(data.sex),
        country: data.country,
        province: data.province,
        city: data.city,
        language: data.language,
        raw: data
      };
    } catch (error) {
      logger.error(`微信获取用户信息异常: ${error.message}`, { error });
      if (error instanceof ValidationError) {
        throw error;
      }
      throw new ValidationError('获取微信用户信息失败，请稍后再试');
    }
  }
  
  /**
   * 刷新访问令牌
   * @param {string} refreshToken - 刷新令牌
   * @returns {Promise<Object>} 新的令牌信息
   */
  async refreshToken(refreshToken) {
    try {
      const response = await axios.get(this.endpoints.refresh, {
        params: {
          appid: this.providerConfig.clientId,
          grant_type: 'refresh_token',
          refresh_token: refreshToken
        }
      });
      
      const data = response.data;
      
      if (data.errcode) {
        logger.error(`微信刷新令牌失败: ${data.errmsg}`, { error: data });
        throw new ValidationError(`微信刷新令牌失败: ${data.errmsg}`);
      }
      
      return {
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        openId: data.openid,
        expiresIn: data.expires_in,
        scope: data.scope,
        raw: data
      };
    } catch (error) {
      logger.error(`微信刷新令牌异常: ${error.message}`, { error });
      if (error instanceof ValidationError) {
        throw error;
      }
      throw new ValidationError('微信刷新令牌失败，请稍后再试');
    }
  }
  
  /**
   * 验证访问令牌是否有效
   * @param {string} accessToken - 访问令牌
   * @param {string} openId - 微信开放ID
   * @returns {Promise<boolean>} 令牌是否有效
   */
  async validateToken(accessToken, openId) {
    try {
      const response = await axios.get(this.endpoints.check, {
        params: {
          access_token: accessToken,
          openid: openId
        }
      });
      
      const data = response.data;
      
      // errcode为0表示有效，非0表示无效
      return data.errcode === 0;
    } catch (error) {
      logger.error(`微信令牌验证异常: ${error.message}`, { error });
      return false;
    }
  }
  
  /**
   * 映射微信性别到标准格式
   * @private
   * @param {number} gender - 微信性别代码 (1为男，2为女，0为未知)
   * @returns {string} 性别字符串
   */
  _mapGender(gender) {
    const genderMap = {
      1: 'male',
      2: 'female',
      0: 'unknown'
    };
    return genderMap[gender] || 'unknown';
  }
}

module.exports = new WechatOAuthProvider(); 
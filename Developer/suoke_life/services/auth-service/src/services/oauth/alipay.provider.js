/**
 * 支付宝OAuth认证提供商
 */
const axios = require('axios');
const crypto = require('crypto');
const config = require('../../config');
const logger = require('../../utils/logger');
const { ValidationError } = require('../../utils/errors');

class AlipayOAuthProvider {
  constructor() {
    this.providerName = 'alipay';
    this.providerConfig = config.oauth?.providers?.alipay || {};
    
    // 必要参数检查
    if (!this.providerConfig.clientId || !this.providerConfig.clientSecret) {
      logger.warn('支付宝OAuth配置缺失，支付宝登录功能将不可用');
    }
    
    // 支付宝API端点
    this.endpoints = {
      authorize: 'https://openauth.alipay.com/oauth2/publicAppAuthorize.htm',
      accessToken: 'https://openapi.alipay.com/gateway.do',
      userInfo: 'https://openapi.alipay.com/gateway.do',
      app_authorize: 'https://openauth.alipay.com/oauth2/appToAppAuth.htm'
    };
    
    // 支付宝API方法
    this.apiMethods = {
      accessToken: 'alipay.system.oauth.token',
      userInfo: 'alipay.user.info.share'
    };
  }
  
  /**
   * 获取授权URL
   * @param {string} redirectUri - 回调地址
   * @param {string} state - 状态参数
   * @returns {string} 授权URL
   */
  getAuthorizationUrl(redirectUri, state) {
    const queryParams = new URLSearchParams({
      app_id: this.providerConfig.clientId,
      scope: 'auth_user',
      redirect_uri: redirectUri,
      state: state
    });
    
    return `${this.endpoints.authorize}?${queryParams.toString()}`;
  }
  
  /**
   * 交换授权码获取令牌
   * @param {string} code - 授权码
   * @param {string} redirectUri - 回调地址
   * @returns {Promise<Object>} 令牌信息
   */
  async exchangeCodeForToken(code, redirectUri) {
    try {
      // 构建请求参数
      const bizContent = {
        grant_type: 'authorization_code',
        code: code
      };
      
      // 请求参数
      const params = {
        app_id: this.providerConfig.clientId,
        method: this.apiMethods.accessToken,
        format: 'JSON',
        charset: 'utf-8',
        sign_type: 'RSA2',
        timestamp: this._getTimestamp(),
        version: '1.0',
        biz_content: JSON.stringify(bizContent)
      };
      
      // 计算签名
      params.sign = this._generateSign(params);
      
      // 发送请求
      const response = await axios.post(this.endpoints.accessToken, null, {
        params: params
      });
      
      const responseKey = 'alipay_system_oauth_token_response';
      const errorKey = 'error_response';
      
      if (response.data[errorKey]) {
        const error = response.data[errorKey];
        logger.error(`支付宝授权码交换失败: ${error.msg}`, { error });
        throw new ValidationError(`支付宝授权失败: ${error.msg}`);
      }
      
      const data = response.data[responseKey];
      
      return {
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        userId: data.user_id,
        expiresIn: data.expires_in,
        scope: data.scope,
        tokenType: 'Bearer',
        raw: data
      };
    } catch (error) {
      logger.error(`支付宝授权码交换异常: ${error.message}`, { error });
      if (error instanceof ValidationError) {
        throw error;
      }
      throw new ValidationError('支付宝授权失败，请稍后再试');
    }
  }
  
  /**
   * 获取用户信息
   * @param {string} accessToken - 访问令牌
   * @returns {Promise<Object>} 用户信息
   */
  async getUserProfile(accessToken) {
    try {
      // 支付宝不需要额外参数，只需令牌
      const bizContent = {};
      
      // 请求参数
      const params = {
        app_id: this.providerConfig.clientId,
        method: this.apiMethods.userInfo,
        format: 'JSON',
        charset: 'utf-8',
        sign_type: 'RSA2',
        timestamp: this._getTimestamp(),
        version: '1.0',
        auth_token: accessToken,
        biz_content: JSON.stringify(bizContent)
      };
      
      // 计算签名
      params.sign = this._generateSign(params);
      
      // 发送请求
      const response = await axios.post(this.endpoints.userInfo, null, {
        params: params
      });
      
      const responseKey = 'alipay_user_info_share_response';
      const errorKey = 'error_response';
      
      if (response.data[errorKey]) {
        const error = response.data[errorKey];
        logger.error(`支付宝获取用户信息失败: ${error.msg}`, { error });
        throw new ValidationError(`获取支付宝用户信息失败: ${error.msg}`);
      }
      
      const data = response.data[responseKey];
      
      // 格式化用户信息
      return {
        id: data.user_id,
        name: data.nick_name,
        nickname: data.nick_name,
        avatar: data.avatar,
        gender: this._mapGender(data.gender),
        province: data.province,
        city: data.city,
        raw: data
      };
    } catch (error) {
      logger.error(`支付宝获取用户信息异常: ${error.message}`, { error });
      if (error instanceof ValidationError) {
        throw error;
      }
      throw new ValidationError('获取支付宝用户信息失败，请稍后再试');
    }
  }
  
  /**
   * 刷新访问令牌
   * @param {string} refreshToken - 刷新令牌
   * @returns {Promise<Object>} 新的令牌信息
   */
  async refreshToken(refreshToken) {
    try {
      // 构建请求参数
      const bizContent = {
        grant_type: 'refresh_token',
        refresh_token: refreshToken
      };
      
      // 请求参数
      const params = {
        app_id: this.providerConfig.clientId,
        method: this.apiMethods.accessToken,
        format: 'JSON',
        charset: 'utf-8',
        sign_type: 'RSA2',
        timestamp: this._getTimestamp(),
        version: '1.0',
        biz_content: JSON.stringify(bizContent)
      };
      
      // 计算签名
      params.sign = this._generateSign(params);
      
      // 发送请求
      const response = await axios.post(this.endpoints.accessToken, null, {
        params: params
      });
      
      const responseKey = 'alipay_system_oauth_token_response';
      const errorKey = 'error_response';
      
      if (response.data[errorKey]) {
        const error = response.data[errorKey];
        logger.error(`支付宝刷新令牌失败: ${error.msg}`, { error });
        throw new ValidationError(`支付宝刷新令牌失败: ${error.msg}`);
      }
      
      const data = response.data[responseKey];
      
      return {
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        userId: data.user_id,
        expiresIn: data.expires_in,
        scope: data.scope,
        raw: data
      };
    } catch (error) {
      logger.error(`支付宝刷新令牌异常: ${error.message}`, { error });
      if (error instanceof ValidationError) {
        throw error;
      }
      throw new ValidationError('支付宝刷新令牌失败，请稍后再试');
    }
  }
  
  /**
   * 获取时间戳
   * @private
   * @returns {string} 格式化的时间戳
   */
  _getTimestamp() {
    const date = new Date();
    
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }
  
  /**
   * 生成签名
   * @private
   * @param {Object} params - 要签名的参数
   * @returns {string} 签名
   */
  _generateSign(params) {
    // 1. 将参数按照键名的字母升序排列
    const sortedKeys = Object.keys(params).sort();
    
    // 2. 将排序后的参数转为字符串，格式为 key=value&key=value
    let stringToSign = '';
    sortedKeys.forEach((key, index) => {
      if (params[key] !== '' && params[key] !== undefined && params[key] !== null && key !== 'sign') {
        stringToSign += `${key}=${params[key]}`;
        if (index < sortedKeys.length - 1) {
          stringToSign += '&';
        }
      }
    });
    
    // 3. 使用私钥签名
    try {
      const privateKey = this.providerConfig.clientSecret.replace(/\\n/g, '\n');
      const sign = crypto.createSign('RSA-SHA256');
      sign.update(stringToSign);
      return sign.sign(privateKey, 'base64');
    } catch (error) {
      logger.error(`支付宝签名生成失败: ${error.message}`, { error });
      throw new Error('签名生成失败');
    }
  }
  
  /**
   * 映射支付宝性别到标准格式
   * @private
   * @param {string} gender - 支付宝性别代码 (F为女，M为男)
   * @returns {string} 性别字符串
   */
  _mapGender(gender) {
    const genderMap = {
      'F': 'female',
      'M': 'male'
    };
    return genderMap[gender] || 'unknown';
  }
}

module.exports = new AlipayOAuthProvider(); 
/**
 * 短信验证码服务
 * 用于短信验证码登录和注册功能
 */
const axios = require('axios');
const crypto = require('crypto');
const config = require('../config');
const logger = require('../utils/logger');
const { redis } = require('../utils/redis');
const { ApplicationError } = require('../utils/errors');
const Redis = require('ioredis');
const securityLogService = require('./security-log.service');

// 创建Redis客户端用于存储验证码
const redisCode = new Redis({
  host: config.redis.host,
  port: config.redis.port,
  keyPrefix: 'sms_code:'
});

/**
 * 短信服务类
 */
class SmsService {
  constructor() {
    // 从配置中获取短信服务商设置
    this.smsConfig = config.sms || {};
    this.provider = this.smsConfig.provider || 'none'; // 默认无提供商
    this.providerConfig = this.smsConfig.providers?.[this.provider] || {};
    
    // 验证码设置
    this.codeConfig = this.smsConfig.verification || {};
    this.codeLength = this.codeConfig.codeLength || 6;
    this.codeExpiry = this.codeConfig.expiry || 300; // 默认5分钟
    this.maxAttempts = this.codeConfig.maxAttempts || 3;
    this.throttleLimit = this.codeConfig.throttleLimit || 60; // 默认60秒限制
    
    // 初始化短信提供商客户端
    this._initSmsClient();
    
    logger.info(`短信服务初始化完成，提供商: ${this.provider}`);
  }
  
  /**
   * 初始化短信提供商客户端
   * @private
   */
  _initSmsClient() {
    // 根据配置的提供商初始化不同的客户端
    switch (this.provider) {
      case 'alicloud':
        // 初始化阿里云短信服务
        this._initAliCloudSms();
        break;
        
      case 'tencent':
        // 初始化腾讯云短信服务
        this._initTencentCloudSms();
        break;
        
      case 'test':
        // 测试模式，不实际发送短信
        this.testMode = true;
        logger.warn('短信服务运行在测试模式，不会实际发送短信');
        break;
        
      case 'none':
        // 无提供商模式
        logger.warn('未配置短信服务提供商，短信功能将不可用');
        break;
        
      default:
        logger.error(`不支持的短信提供商: ${this.provider}`);
    }
  }
  
  /**
   * 初始化阿里云短信服务
   * @private
   */
  _initAliCloudSms() {
    // 获取阿里云配置
    const accessKeyId = this.providerConfig.accessKeyId;
    const accessKeySecret = this.providerConfig.accessKeySecret;
    
    if (!accessKeyId || !accessKeySecret) {
      logger.error('阿里云短信服务配置不完整，服务无法初始化');
      return;
    }
    
    // 设置阿里云短信参数
    this.alicloudConfig = {
      accessKeyId,
      accessKeySecret,
      endpoint: this.providerConfig.endpoint || 'https://dysmsapi.aliyuncs.com',
      apiVersion: this.providerConfig.apiVersion || '2017-05-25',
      signName: this.providerConfig.signName,
      templateCode: this.providerConfig.templateCode
    };
    
    logger.info('阿里云短信服务初始化完成');
  }
  
  /**
   * 初始化腾讯云短信服务
   * @private
   */
  _initTencentCloudSms() {
    // 获取腾讯云配置
    const secretId = this.providerConfig.secretId;
    const secretKey = this.providerConfig.secretKey;
    
    if (!secretId || !secretKey) {
      logger.error('腾讯云短信服务配置不完整，服务无法初始化');
      return;
    }
    
    // 设置腾讯云短信参数
    this.tencentConfig = {
      secretId,
      secretKey,
      endpoint: this.providerConfig.endpoint || 'sms.tencentcloudapi.com',
      region: this.providerConfig.region || 'ap-guangzhou',
      sdkAppId: this.providerConfig.sdkAppId,
      signName: this.providerConfig.signName,
      templateId: this.providerConfig.templateId
    };
    
    logger.info('腾讯云短信服务初始化完成');
  }
  
  /**
   * 生成随机验证码
   * @private
   * @returns {string} 生成的验证码
   */
  _generateCode() {
    // 生成指定长度的随机数字验证码
    const min = Math.pow(10, this.codeLength - 1);
    const max = Math.pow(10, this.codeLength) - 1;
    return Math.floor(min + Math.random() * (max - min + 1)).toString();
  }
  
  /**
   * 生成Redis缓存键
   * @private
   * @param {string} type - 键类型 (code, attempts, throttle)
   * @param {string} phoneNumber - 手机号码
   * @returns {string} Redis键
   */
  _generateKey(type, phoneNumber) {
    return `sms:${type}:${phoneNumber}`;
  }
  
  /**
   * 向阿里云发送短信
   * @private
   * @param {string} phoneNumber - 手机号码
   * @param {string} code - 验证码
   * @returns {Promise<Object>} 发送结果
   */
  async _sendViaTencentCloud(phoneNumber, code) {
    try {
      const { secretId, secretKey, endpoint, region, sdkAppId, templateId, signName } = this.tencentConfig;
      
      // 生成随机字符串
      const randomStr = Math.random().toString(36).substring(2, 15);
      const timestamp = Math.floor(Date.now() / 1000);
      
      // 构建请求参数
      const params = {
        PhoneNumberSet: [`+86${phoneNumber}`],
        TemplateID: templateId,
        SmsSdkAppid: sdkAppId,
        Sign: signName,
        TemplateParamSet: [code]
      };
      
      // 构建请求签名
      const service = 'sms';
      const action = 'SendSms';
      const version = '2021-01-11';
      const payload = JSON.stringify(params);
      
      // 构建签名
      const date = new Date();
      const dateStr = date.toISOString().substr(0, 10);
      
      // 构建规范请求串
      const canonicalHeaders = `content-type:application/json; charset=utf-8\nhost:${endpoint}\n`;
      const signedHeaders = 'content-type;host';
      
      const hashedPayload = crypto.createHash('sha256').update(payload).digest('hex');
      const canonicalRequest = [
        'POST',
        '/',
        '',
        canonicalHeaders,
        signedHeaders,
        hashedPayload
      ].join('\n');
      
      // 构建待签字符串
      const algorithm = 'TC3-HMAC-SHA256';
      const hashedCanonicalRequest = crypto.createHash('sha256').update(canonicalRequest).digest('hex');
      const credentialScope = `${dateStr}/${service}/tc3_request`;
      const stringToSign = [
        algorithm,
        timestamp,
        credentialScope,
        hashedCanonicalRequest
      ].join('\n');
      
      // 计算签名
      const kDate = crypto.createHmac('sha256', `TC3${secretKey}`).update(dateStr).digest();
      const kService = crypto.createHmac('sha256', kDate).update(service).digest();
      const kSigning = crypto.createHmac('sha256', kService).update('tc3_request').digest();
      const signature = crypto.createHmac('sha256', kSigning).update(stringToSign).digest('hex');
      
      // 构建授权头
      const authorization = `${algorithm} Credential=${secretId}/${credentialScope}, SignedHeaders=${signedHeaders}, Signature=${signature}`;
      
      // 发送请求
      const response = await axios.post(`https://${endpoint}`, payload, {
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'Host': endpoint,
          'X-TC-Action': action,
          'X-TC-Timestamp': timestamp.toString(),
          'X-TC-Version': version,
          'X-TC-Region': region,
          'Authorization': authorization
        }
      });
      
      // 检查响应
      if (response.data && response.data.Response) {
        if (response.data.Response.Error) {
          throw new Error(`${response.data.Response.Error.Code}: ${response.data.Response.Error.Message}`);
        }
        
        logger.info(`向 ${phoneNumber} 发送短信成功，消息ID: ${response.data.Response.SendStatusSet?.[0]?.SerialNo || '未知'}`);
        return {
          success: true,
          messageId: response.data.Response.SendStatusSet?.[0]?.SerialNo || '',
          requestId: response.data.Response.RequestId
        };
      }
      
      throw new Error('发送短信失败: 无效的响应格式');
    } catch (error) {
      logger.error(`向 ${phoneNumber} 发送腾讯云短信失败: ${error.message}`, { error });
      throw new ApplicationError(`短信发送失败: ${error.message}`);
    }
  }
  
  /**
   * 向阿里云发送短信
   * @private
   * @param {string} phoneNumber - 手机号码
   * @param {string} code - 验证码
   * @returns {Promise<Object>} 发送结果
   */
  async _sendViaAliCloud(phoneNumber, code) {
    try {
      const { accessKeyId, accessKeySecret, endpoint, apiVersion, signName, templateCode } = this.alicloudConfig;
      
      // 生成随机字符串
      const nonce = Math.random().toString(36).substring(2, 15);
      const timestamp = new Date().toISOString();
      
      // 构建请求参数
      const params = {
        AccessKeyId: accessKeyId,
        Timestamp: timestamp,
        Format: 'JSON',
        SignatureMethod: 'HMAC-SHA1',
        SignatureVersion: '1.0',
        SignatureNonce: nonce,
        Version: apiVersion,
        Action: 'SendSms',
        RegionId: 'cn-hangzhou',
        PhoneNumbers: phoneNumber,
        SignName: signName,
        TemplateCode: templateCode,
        TemplateParam: JSON.stringify({ code })
      };
      
      // 准备签名
      const sortedKeys = Object.keys(params).sort();
      let canonicalizedQueryString = '';
      
      for (const key of sortedKeys) {
        canonicalizedQueryString += `&${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`;
      }
      
      // 构建待签名字符串
      const stringToSign = 'POST&' + encodeURIComponent('/') + '&' + encodeURIComponent(canonicalizedQueryString.substr(1));
      
      // 计算签名
      const signature = crypto.createHmac('sha1', accessKeySecret + '&')
        .update(stringToSign)
        .digest('base64');
      
      params.Signature = signature;
      
      // 发送请求
      const response = await axios.post(endpoint, null, {
        params,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      // 检查响应
      if (response.data && response.data.Code === 'OK') {
        logger.info(`向 ${phoneNumber} 发送短信成功，消息ID: ${response.data.BizId}`);
        return {
          success: true,
          messageId: response.data.BizId,
          requestId: response.data.RequestId
        };
      }
      
      throw new Error(`发送短信失败: ${response.data.Message || '未知错误'}`);
    } catch (error) {
      logger.error(`向 ${phoneNumber} 发送阿里云短信失败: ${error.message}`, { error });
      throw new ApplicationError(`短信发送失败: ${error.message}`);
    }
  }
  
  /**
   * 发送短信验证码
   * @param {string} phoneNumber - 手机号码
   * @param {Object} options - 选项
   * @param {string} [options.type='login'] - 短信类型 (login, register, reset)
   * @param {string} [options.templateId] - 覆盖默认模板ID
   * @returns {Promise<Object>} 发送结果
   */
  async sendVerificationCode(phoneNumber, options = {}) {
    // 检查服务是否可用
    if (this.provider === 'none') {
      throw new ApplicationError('短信服务未配置');
    }
    
    // 规范化手机号
    phoneNumber = this._normalizePhoneNumber(phoneNumber);
    
    // 检查手机号码格式
    if (!this._validatePhoneNumber(phoneNumber)) {
      throw new ApplicationError('无效的手机号码格式');
    }
    
    // 检查发送频率限制
    const throttleKey = this._generateKey('throttle', phoneNumber);
    const throttleExists = await redis.exists(throttleKey);
    
    if (throttleExists) {
      const ttl = await redis.ttl(throttleKey);
      throw new ApplicationError(`发送过于频繁，请在${ttl}秒后重试`);
    }
    
    // 生成验证码
    const code = this._generateCode();
    const type = options.type || 'login';
    
    // 测试模式下不实际发送短信
    let result;
    
    if (this.testMode) {
      logger.info(`测试模式: 向 ${phoneNumber} 发送验证码 ${code}`);
      result = {
        success: true,
        messageId: `test-${Date.now()}`,
        code // 测试模式返回验证码
      };
    } else {
      // 根据提供商发送短信
      switch (this.provider) {
        case 'alicloud':
          result = await this._sendViaAliCloud(phoneNumber, code);
          break;
          
        case 'tencent':
          result = await this._sendViaTencentCloud(phoneNumber, code);
          break;
          
        default:
          throw new ApplicationError('不支持的短信提供商');
      }
    }
    
    // 存储验证码
    const codeKey = this._generateKey('code', phoneNumber);
    const attemptsKey = this._generateKey('attempts', phoneNumber);
    
    // 保存验证码和类型信息
    await redis.set(codeKey, JSON.stringify({
      code,
      type,
      createdAt: Date.now()
    }), 'EX', this.codeExpiry);
    
    // 重置尝试次数
    await redis.set(attemptsKey, 0, 'EX', this.codeExpiry);
    
    // 设置频率限制
    await redis.set(throttleKey, 1, 'EX', this.throttleLimit);
    
    return {
      success: result.success,
      message: '验证码已发送',
      expiry: this.codeExpiry,
      ...(this.testMode ? { code } : {}) // 仅在测试模式下返回验证码
    };
  }
  
  /**
   * 验证短信验证码
   * @param {string} phoneNumber - 手机号码
   * @param {string} code - 待验证的验证码
   * @param {Object} options - 选项
   * @param {string} [options.type='login'] - 短信类型 (login, register, reset)
   * @param {boolean} [options.consume=true] - 验证成功后是否删除验证码
   * @returns {Promise<boolean>} 验证结果
   */
  async verifyCode(phoneNumber, code, options = {}) {
    // 规范化手机号
    phoneNumber = this._normalizePhoneNumber(phoneNumber);
    
    // 检查手机号码格式
    if (!this._validatePhoneNumber(phoneNumber)) {
      throw new ApplicationError('无效的手机号码格式');
    }
    
    // 获取验证码信息
    const codeKey = this._generateKey('code', phoneNumber);
    const attemptsKey = this._generateKey('attempts', phoneNumber);
    
    const codeData = await redis.get(codeKey);
    
    if (!codeData) {
      throw new ApplicationError('验证码不存在或已过期');
    }
    
    // 检查尝试次数
    const attempts = parseInt(await redis.get(attemptsKey) || 0);
    
    if (attempts >= this.maxAttempts) {
      // 删除验证码和尝试次数
      await redis.del(codeKey);
      await redis.del(attemptsKey);
      
      throw new ApplicationError('验证尝试次数过多，请重新获取验证码');
    }
    
    // 增加尝试次数
    await redis.incr(attemptsKey);
    
    // 解析验证码数据
    const { code: storedCode, type: storedType, createdAt } = JSON.parse(codeData);
    const requestedType = options.type || 'login';
    
    // 检查验证码类型
    if (storedType !== requestedType) {
      throw new ApplicationError(`验证码类型不匹配，期望 ${requestedType}，实际 ${storedType}`);
    }
    
    // 验证码不正确
    if (code !== storedCode) {
      throw new ApplicationError('验证码不正确');
    }
    
    // 验证码过期检查
    const now = Date.now();
    const expiryTime = createdAt + (this.codeExpiry * 1000);
    
    if (now > expiryTime) {
      await redis.del(codeKey);
      await redis.del(attemptsKey);
      
      throw new ApplicationError('验证码已过期');
    }
    
    // 验证成功，是否消费验证码
    const consume = options.consume !== false;
    
    if (consume) {
      // 删除验证码和尝试次数
      await redis.del(codeKey);
      await redis.del(attemptsKey);
    }
    
    return true;
  }
  
  /**
   * 规范化手机号码格式
   * @private
   * @param {string} phoneNumber - 手机号码
   * @returns {string} 规范化后的手机号码
   */
  _normalizePhoneNumber(phoneNumber) {
    // 去除所有非数字字符
    return phoneNumber.replace(/\D/g, '');
  }
  
  /**
   * 验证手机号码格式
   * @private
   * @param {string} phoneNumber - 手机号码
   * @returns {boolean} 是否有效
   */
  _validatePhoneNumber(phoneNumber) {
    // 简单的中国大陆手机号验证规则
    const phoneRegex = /^1[3-9]\d{9}$/;
    return phoneRegex.test(phoneNumber);
  }
}

// 单例模式
const smsService = new SmsService();

module.exports = smsService; 
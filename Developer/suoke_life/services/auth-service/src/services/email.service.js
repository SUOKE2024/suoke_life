/**
 * 邮件发送服务
 */
const nodemailer = require('nodemailer');
const config = require('../config');
const logger = require('../utils/logger');
const { ValidationError } = require('../utils/errors');

class EmailService {
  constructor() {
    this.enabled = config.email?.enabled !== false;
    this.config = config.email || {};
    this.transporter = null;
    
    // 初始化邮件传输器
    this._initTransporter();
  }
  
  /**
   * 初始化邮件传输器
   * @private
   */
  _initTransporter() {
    try {
      if (!this.enabled) {
        logger.info('邮件服务已禁用');
        return;
      }
      
      // 检查是否在测试模式
      if (this.config.provider === 'test' || config.env === 'test') {
        this.transporter = {
          sendMail: async (mailOptions) => {
            logger.debug('测试邮件模式', { mail: mailOptions });
            return { messageId: 'test-message-id' };
          }
        };
        logger.info('邮件服务已初始化（测试模式）');
        return;
      }
      
      // 创建真实的邮件传输器
      const transportConfig = this._getTransportConfig();
      this.transporter = nodemailer.createTransport(transportConfig);
      
      // 验证连接
      this.transporter.verify((error) => {
        if (error) {
          logger.error(`邮件传输器验证失败: ${error.message}`, { error });
        } else {
          logger.info('邮件服务已初始化并成功连接');
        }
      });
    } catch (error) {
      logger.error(`邮件传输器初始化失败: ${error.message}`, { error });
      this.transporter = null;
    }
  }
  
  /**
   * 获取邮件传输配置
   * @private
   * @returns {Object} 传输配置
   */
  _getTransportConfig() {
    const provider = this.config.provider || 'smtp';
    
    switch (provider) {
      case 'smtp':
        return {
          host: this.config.smtp?.host || 'smtp.example.com',
          port: this.config.smtp?.port || 587,
          secure: this.config.smtp?.secure || false,
          auth: {
            user: this.config.smtp?.user,
            pass: this.config.smtp?.password
          }
        };
        
      case 'sendgrid':
        return {
          service: 'SendGrid',
          auth: {
            user: this.config.sendgrid?.user || 'apikey',
            pass: this.config.sendgrid?.apiKey
          }
        };
        
      case 'aliyun':
        return {
          host: 'smtp.dm.aliyun.com',
          port: 465,
          secure: true,
          auth: {
            user: this.config.aliyun?.user,
            pass: this.config.aliyun?.password
          }
        };
        
      default:
        logger.warn(`未知的邮件提供商: ${provider}，将使用默认SMTP配置`);
        return {
          host: this.config.smtp?.host || 'smtp.example.com',
          port: this.config.smtp?.port || 587,
          secure: this.config.smtp?.secure || false,
          auth: {
            user: this.config.smtp?.user,
            pass: this.config.smtp?.password
          }
        };
    }
  }
  
  /**
   * 发送邮件
   * @param {Object} options - 邮件选项
   * @param {string} options.to - 收件人
   * @param {string} options.subject - 主题
   * @param {string} options.text - 文本内容
   * @param {string} options.html - HTML内容
   * @param {string} [options.from] - 发件人，默认使用配置的发件人
   * @returns {Promise<Object>} 发送结果
   */
  async sendEmail(options) {
    try {
      if (!this.enabled) {
        logger.warn('邮件服务已禁用，邮件未发送');
        return { success: false, message: '邮件服务已禁用' };
      }
      
      if (!this.transporter) {
        this._initTransporter();
        
        if (!this.transporter) {
          throw new Error('邮件传输器未初始化');
        }
      }
      
      // 验证必需字段
      if (!options.to) {
        throw new ValidationError('收件人地址不能为空');
      }
      
      if (!options.subject) {
        throw new ValidationError('邮件主题不能为空');
      }
      
      if (!options.text && !options.html) {
        throw new ValidationError('邮件内容不能为空');
      }
      
      // 准备邮件选项
      const mailOptions = {
        from: options.from || this.config.defaultFrom || 'noreply@suoke.life',
        to: options.to,
        subject: options.subject,
        text: options.text,
        html: options.html
      };
      
      // 发送邮件
      const info = await this.transporter.sendMail(mailOptions);
      
      logger.info(`邮件已发送: ${info.messageId}`, {
        to: options.to,
        subject: options.subject
      });
      
      return {
        success: true,
        messageId: info.messageId
      };
    } catch (error) {
      logger.error(`邮件发送失败: ${error.message}`, {
        error,
        to: options.to,
        subject: options.subject
      });
      
      if (error instanceof ValidationError) {
        throw error;
      }
      
      throw new Error(`邮件发送失败: ${error.message}`);
    }
  }
  
  /**
   * 发送密码重置邮件
   * @param {string} to - 收件人邮箱
   * @param {string} resetToken - 重置令牌
   * @param {string} username - 用户名
   * @returns {Promise<Object>} 发送结果
   */
  async sendPasswordResetEmail(to, resetToken, username) {
    const baseUrl = this.config.baseUrl || 'http://localhost:3000';
    const resetUrl = `${baseUrl}/reset-password?token=${resetToken}`;
    
    const subject = '密码重置 - 索克生活';
    
    const text = `
亲爱的 ${username}，

您收到此邮件是因为您（或其他人）请求重置您索克生活账户的密码。

请点击以下链接或将其复制到浏览器中来重置您的密码：
${resetUrl}

如果您没有请求重置密码，请忽略此邮件，您的密码将保持不变。

此链接将在1小时后过期。

祝好，
索克生活团队
`;
    
    const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {
      font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
      color: #333;
      line-height: 1.6;
    }
    .container {
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
      border: 1px solid #eee;
      border-radius: 5px;
    }
    .header {
      text-align: center;
      margin-bottom: 20px;
    }
    .header img {
      max-height: 60px;
    }
    .content {
      margin: 20px 0;
    }
    .button {
      display: inline-block;
      background-color: #35BB78;
      color: white;
      text-decoration: none;
      padding: 10px 20px;
      border-radius: 5px;
      margin: 20px 0;
    }
    .footer {
      margin-top: 30px;
      font-size: 12px;
      color: #666;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>索克生活 - 密码重置</h2>
    </div>
    
    <div class="content">
      <p>亲爱的 ${username}，</p>
      
      <p>您收到此邮件是因为您（或其他人）请求重置您索克生活账户的密码。</p>
      
      <p>请点击以下按钮重置您的密码：</p>
      
      <p style="text-align: center;">
        <a href="${resetUrl}" class="button">重置密码</a>
      </p>
      
      <p>或者，您可以将以下链接复制到浏览器地址栏：</p>
      <p><a href="${resetUrl}">${resetUrl}</a></p>
      
      <p>如果您没有请求重置密码，请忽略此邮件，您的密码将保持不变。</p>
      
      <p>此链接将在1小时后过期。</p>
    </div>
    
    <div class="footer">
      <p>祝好，</p>
      <p>索克生活团队</p>
      <p>&copy; ${new Date().getFullYear()} 索克生活. 保留所有权利。</p>
    </div>
  </div>
</body>
</html>
`;
    
    return this.sendEmail({
      to,
      subject,
      text,
      html
    });
  }
  
  /**
   * 发送欢迎邮件
   * @param {string} to - 收件人邮箱
   * @param {string} username - 用户名
   * @returns {Promise<Object>} 发送结果
   */
  async sendWelcomeEmail(to, username) {
    const subject = '欢迎加入索克生活';
    
    const text = `
亲爱的 ${username}，

欢迎加入索克生活！

您的账户已成功创建，您现在可以使用我们的服务了。

感谢您的注册！

祝好，
索克生活团队
`;
    
    const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {
      font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
      color: #333;
      line-height: 1.6;
    }
    .container {
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
      border: 1px solid #eee;
      border-radius: 5px;
    }
    .header {
      text-align: center;
      margin-bottom: 20px;
    }
    .header img {
      max-height: 60px;
    }
    .content {
      margin: 20px 0;
    }
    .button {
      display: inline-block;
      background-color: #35BB78;
      color: white;
      text-decoration: none;
      padding: 10px 20px;
      border-radius: 5px;
      margin: 20px 0;
    }
    .footer {
      margin-top: 30px;
      font-size: 12px;
      color: #666;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>欢迎加入索克生活！</h2>
    </div>
    
    <div class="content">
      <p>亲爱的 ${username}，</p>
      
      <p>感谢您注册索克生活！我们很高兴您加入我们的社区。</p>
      
      <p>索克生活是一个融合中国传统中医辨证治未病和现代预防医学理念的健康管理平台。</p>
      
      <p>您现在可以登录应用，探索我们丰富的功能：</p>
      <ul>
        <li>个性化健康管理</li>
        <li>中医体质分析</li>
        <li>智能健康助手</li>
        <li>专业知识库</li>
      </ul>
      
      <p style="text-align: center;">
        <a href="https://app.suoke.life/login" class="button">立即登录</a>
      </p>
    </div>
    
    <div class="footer">
      <p>祝好，</p>
      <p>索克生活团队</p>
      <p>&copy; ${new Date().getFullYear()} 索克生活. 保留所有权利。</p>
    </div>
  </div>
</body>
</html>
`;
    
    return this.sendEmail({
      to,
      subject,
      text,
      html
    });
  }
}

module.exports = new EmailService(); 
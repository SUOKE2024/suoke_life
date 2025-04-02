/**
 * 国际化中间件
 * 添加多语言支持功能，并集成到Express请求响应周期
 */
const { t, getLocaleFromRequest, createNamespacedT } = require('../utils/i18n');
const { logger } = require('@suoke/shared').utils;
const config = require('../config');

// 检查标头，确保设置了响应语言
const setLanguageHeaders = (req, res, next) => {
  const locale = req.locale || req.lang || config.i18n.defaultLanguage;
  
  // 在响应头中设置语言信息
  res.setHeader('Content-Language', locale);
  
  // 如果启用了cookie存储语言偏好
  if (config.i18n.storeLangInCookie !== false) {
    // 检查是否需要更新cookie
    const cookieLang = req.cookies && req.cookies.lang;
    
    if (cookieLang !== locale) {
      res.cookie('lang', locale, {
        maxAge: 365 * 24 * 60 * 60 * 1000, // 一年
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax'
      });
    }
  }
  
  next();
};

// i18n中间件，附加翻译功能到请求对象
const i18nMiddleware = (req, res, next) => {
  try {
    // 获取请求的首选语言
    const locale = getLocaleFromRequest(req);
    
    // 添加到请求对象
    req.locale = locale;
    req.lang = locale; // 兼容旧代码
    
    // 添加翻译函数到请求对象
    req.t = (key, options = {}) => t(key, { ...options, locale });
    
    // 添加命名空间翻译函数
    req.tCommon = createNamespacedT('common');
    req.tErrors = createNamespacedT('errors');
    req.tValidation = createNamespacedT('validation');
    req.tResponses = createNamespacedT('responses');
    
    // 便捷的命名空间翻译函数生成器
    req.createNamespacedT = (namespace) => (key, options = {}) => t(key, { ...options, locale, namespace });
    
    // 添加到响应本地变量，供模板使用
    res.locals = res.locals || {};
    res.locals.t = req.t;
    res.locals.tCommon = req.tCommon;
    res.locals.tErrors = req.tErrors;
    res.locals.tValidation = req.tValidation;
    res.locals.tResponses = req.tResponses;
    res.locals.locale = locale;
    res.locals.lang = locale;
    res.locals.dir = ['ar', 'he', 'fa', 'ur'].includes(locale.split('-')[0]) ? 'rtl' : 'ltr';
    res.locals.availableLanguages = config.i18n.supportedLanguages;
    
    // 国际化格式化函数
    // 格式化日期
    req.formatDate = (date, options = {}) => {
      const dateObj = date instanceof Date ? date : new Date(date);
      return new Intl.DateTimeFormat(locale, {
        dateStyle: 'medium',
        ...options
      }).format(dateObj);
    };
    
    // 格式化数字
    req.formatNumber = (number, options = {}) => {
      return new Intl.NumberFormat(locale, options).format(number);
    };
    
    // 格式化货币
    req.formatCurrency = (amount, currency = 'CNY', options = {}) => {
      return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency,
        ...options
      }).format(amount);
    };
    
    // 将格式化函数添加到响应本地变量
    res.locals.formatDate = req.formatDate;
    res.locals.formatNumber = req.formatNumber;
    res.locals.formatCurrency = req.formatCurrency;
    
    // 在开发环境中记录检测到的语言
    if (process.env.NODE_ENV === 'development') {
      logger.debug(`检测到客户端语言: ${locale}`);
    }
    
    next();
  } catch (err) {
    logger.error('国际化中间件错误', { error: err.message });
    // 出错时使用默认设置继续
    req.locale = config.i18n.defaultLanguage;
    req.t = (key) => key;
    next();
  }
};

// 翻译验证错误，将错误信息转换为当前语言
const translateValidationErrors = (req, res, next) => {
  if (res.locals && res.locals.validationErrors) {
    const errors = res.locals.validationErrors;
    
    // 翻译错误消息
    for (const field in errors) {
      if (errors[field].message) {
        // 尝试使用验证错误键
        const key = `validation.${errors[field].type}`;
        errors[field].message = req.t(key, { 
          field: req.t(`fields.${field}`),
          limit: errors[field].limit,
          namespace: 'validation'
        });
      }
    }
  }
  
  next();
};

// 响应国际化辅助函数
// 创建本地化的响应
const createLocalizedResponse = (req, res, next) => {
  // 添加本地化的成功响应方法
  res.successLocalized = (messageKey, data = {}, options = {}) => {
    const message = req.t(messageKey, { namespace: 'responses', ...options });
    
    return res.json({
      success: true,
      message,
      data
    });
  };
  
  // 添加本地化的错误响应方法
  res.errorLocalized = (messageKey, statusCode = 400, errors = {}, options = {}) => {
    const message = req.t(messageKey, { namespace: 'errors', ...options });
    
    return res.status(statusCode).json({
      success: false,
      message,
      errors
    });
  };
  
  next();
};

module.exports = {
  i18nMiddleware,
  setLanguageHeaders,
  translateValidationErrors,
  createLocalizedResponse
}; 
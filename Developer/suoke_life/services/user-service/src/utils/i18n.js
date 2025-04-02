/**
 * i18n国际化工具模块
 * 提供多语言支持功能
 */
const path = require('path');
const fs = require('fs');
const config = require('../config');
const { logger } = require('@suoke/shared').utils;
const { createLogger } = require('./logger');
const { cacheService } = require('./cache-service');

const logger = createLogger('i18n');

// 从配置中获取国际化设置
const LOCALE_DIR = path.resolve(__dirname, '../../locales');
const DEFAULT_LANG = config.i18n.defaultLanguage;
const SUPPORTED_LANGS = config.i18n.supportedLanguages;
const DETECT_FROM = config.i18n.detectFrom;

// 所有翻译资源
const translations = {};

// 翻译缓存，格式为 {locale: {namespace: {key: value}}}
const translationCache = {};

// 初始化翻译资源
const initTranslations = () => {
  try {
    if (!fs.existsSync(LOCALE_DIR)) {
      fs.mkdirSync(LOCALE_DIR, { recursive: true });
    }
    
    // 初始化每种语言的翻译资源
    SUPPORTED_LANGS.forEach(lang => {
      const langDir = path.join(LOCALE_DIR, lang);
      
      if (!fs.existsSync(langDir)) {
        fs.mkdirSync(langDir, { recursive: true });
      }
      
      translations[lang] = {};
      
      // 模块目录：通用、验证、错误、响应等
      const modules = ['common', 'validation', 'errors', 'responses'];
      
      modules.forEach(module => {
        const filePath = path.join(langDir, `${module}.json`);
        
        // 如果翻译文件不存在，创建默认文件
        if (!fs.existsSync(filePath)) {
          fs.writeFileSync(filePath, JSON.stringify({}, null, 2), 'utf8');
        }
        
        try {
          const content = fs.readFileSync(filePath, 'utf8');
          translations[lang][module] = JSON.parse(content);
        } catch (err) {
          logger.error(`加载语言文件失败: ${filePath}`, { error: err.message });
          translations[lang][module] = {};
        }
      });
    });
    
    logger.info('国际化翻译资源加载完成', { 
      languages: Object.keys(translations),
      modules: Object.keys(translations[DEFAULT_LANG] || {})
    });
  } catch (err) {
    logger.error('初始化国际化资源失败', { error: err.message });
  }
};

/**
 * 获取指定语言和模块的翻译资源
 * @param {string} lang - 语言代码
 * @param {string} module - 模块名称
 * @returns {Object} - 翻译资源对象
 */
const getTranslations = (lang, module = 'common') => {
  // 如果请求的语言不存在，使用默认语言
  const langToUse = translations[lang] ? lang : DEFAULT_LANG;
  return translations[langToUse]?.[module] || {};
};

/**
 * 加载翻译文件
 * @param {string} locale - 语言代码
 * @param {string} namespace - 命名空间
 * @returns {Object} - 翻译对象
 */
const loadTranslations = (locale, namespace) => {
  // 尝试从缓存中获取
  const cacheKey = `i18n:${locale}:${namespace}`;
  const cachedTranslations = cacheService.get(cacheKey);
  
  if (cachedTranslations) {
    return cachedTranslations;
  }
  
  try {
    const filePath = path.join(LOCALE_DIR, locale, `${namespace}.json`);
    
    if (fs.existsSync(filePath)) {
      const fileContent = fs.readFileSync(filePath, 'utf8');
      const translations = JSON.parse(fileContent);
      
      // 存入缓存
      cacheService.set(cacheKey, translations, 3600); // 缓存1小时
      
      return translations;
    }
    
    // 如果文件不存在，尝试使用默认语言
    if (locale !== DEFAULT_LANG) {
      logger.warn(`找不到 ${locale} 语言的 ${namespace} 翻译文件，尝试使用默认语言`);
      return loadTranslations(DEFAULT_LANG, namespace);
    }
    
    logger.error(`找不到 ${namespace} 的翻译文件，即使在默认语言中也无法找到`);
    return {};
  } catch (error) {
    logger.error(`加载翻译文件失败: ${locale}/${namespace}`, { error: error.message });
    return {};
  }
};

/**
 * 获取翻译值
 * @param {string} key - 翻译键
 * @param {Object} options - 翻译选项
 * @param {string} options.locale - 目标语言，默认为默认语言
 * @param {string} options.namespace - 命名空间，默认为 'common'
 * @param {Object} options.variables - 变量替换，格式为 {name: value}
 * @param {boolean} options.fallbackToKey - 找不到翻译时是否返回键名，默认为 true
 * @returns {string} - 翻译后的文本
 */
const t = (key, options = {}) => {
  const locale = options.locale || options.lang || DEFAULT_LANG;
  const namespace = options.namespace || options.module || 'common';
  const variables = options.variables || options.data || {};
  const fallbackToKey = options.fallbackToKey !== false;
  
  // 如果翻译键为空，直接返回空字符串
  if (!key) {
    return '';
  }
  
  // 加载翻译
  const translations = loadTranslations(locale, namespace);
  
  // 获取翻译
  let translation = translations[key];
  
  // 如果找不到翻译，尝试使用默认语言
  if (translation === undefined && locale !== DEFAULT_LANG) {
    const defaultTranslations = loadTranslations(DEFAULT_LANG, namespace);
    translation = defaultTranslations[key];
  }
  
  // 如果仍然找不到翻译，返回键名或空字符串
  if (translation === undefined) {
    logger.debug(`找不到翻译键: ${namespace}.${key}`);
    return fallbackToKey ? key : '';
  }
  
  // 变量替换
  return replaceVariables(translation, variables);
};

/**
 * 翻译指定的文本（兼容旧接口）
 * @param {string} key - 翻译键
 * @param {Object} options - 翻译选项
 * @returns {string} - 翻译后的文本
 */
const translate = (key, options = {}) => {
  return t(key, options);
};

/**
 * 替换文本中的变量
 * @param {string} text - 文本
 * @param {Object} variables - 变量对象
 * @returns {string} - 替换后的文本
 */
const replaceVariables = (text, variables) => {
  if (!text || typeof text !== 'string' || Object.keys(variables).length === 0) {
    return text;
  }
  
  return text.replace(/\{\{([^}]+)\}\}/g, (match, name) => {
    const parts = name.trim().split('.');
    let value = variables;
    
    for (const part of parts) {
      if (value === undefined || value === null) {
        return match;
      }
      value = value[part];
    }
    
    return value !== undefined && value !== null ? value : match;
  });
};

/**
 * 创建指定命名空间的翻译函数
 * @param {string} namespace - 命名空间
 * @returns {Function} - 翻译函数
 */
const createNamespacedT = (namespace) => {
  return (key, options = {}) => {
    return t(key, { ...options, namespace });
  };
};

/**
 * 获取指定请求的首选语言
 * @param {Object} req - Express请求对象
 * @returns {string} - 语言代码
 */
const getLocaleFromRequest = (req) => {
  // 优先使用查询参数
  if (req.query && req.query.locale && isValidLocale(req.query.locale)) {
    return req.query.locale;
  }
  
  // 查询参数使用lang参数（兼容旧代码）
  if (req.query && req.query.lang && isValidLocale(req.query.lang)) {
    return req.query.lang;
  }
  
  // 检查cookie
  if (req.cookies && req.cookies.lang && isValidLocale(req.cookies.lang)) {
    return req.cookies.lang;
  }
  
  // 其次使用请求头
  if (req.headers && req.headers['accept-language']) {
    const acceptedLanguages = req.headers['accept-language']
      .split(',')
      .map(lang => lang.split(';')[0].trim());
    
    for (const lang of acceptedLanguages) {
      if (isValidLocale(lang)) {
        return lang;
      }
      
      // 尝试匹配语言部分
      const langBase = lang.split('-')[0];
      const matchedLocale = SUPPORTED_LANGS.find(locale => 
        locale.startsWith(langBase + '-')
      );
      
      if (matchedLocale) {
        return matchedLocale;
      }
    }
  }
  
  // 最后使用用户偏好或默认语言
  if (req.user && req.user.preferredLanguage && isValidLocale(req.user.preferredLanguage)) {
    return req.user.preferredLanguage;
  }
  
  return DEFAULT_LANG;
};

/**
 * 检查语言代码是否有效
 * @param {string} locale - 语言代码
 * @returns {boolean} - 是否有效
 */
const isValidLocale = (locale) => {
  return SUPPORTED_LANGS.includes(locale);
};

/**
 * 清除特定语言和命名空间的缓存
 * @param {string} locale - 语言代码，不提供则清除所有语言
 * @param {string} namespace - 命名空间，不提供则清除所有命名空间
 */
const clearCache = (locale, namespace) => {
  if (locale && namespace) {
    const cacheKey = `i18n:${locale}:${namespace}`;
    cacheService.del(cacheKey);
    logger.debug(`已清除缓存: ${cacheKey}`);
  } else if (locale) {
    SUPPORTED_LANGS.forEach(lang => {
      if (lang === locale) {
        ['common', 'errors', 'validation', 'responses'].forEach(ns => {
          const cacheKey = `i18n:${locale}:${ns}`;
          cacheService.del(cacheKey);
        });
      }
    });
    logger.debug(`已清除语言缓存: ${locale}`);
  } else {
    SUPPORTED_LANGS.forEach(lang => {
      ['common', 'errors', 'validation', 'responses'].forEach(ns => {
        const cacheKey = `i18n:${lang}:${ns}`;
        cacheService.del(cacheKey);
      });
    });
    logger.debug('已清除所有翻译缓存');
  }
};

/**
 * 翻译中间件
 * 为请求添加翻译函数
 */
const i18nMiddleware = (req, res, next) => {
  const locale = getLocaleFromRequest(req);
  
  // 添加翻译功能到请求对象
  req.locale = locale;
  req.lang = locale; // 兼容旧代码
  req.t = (key, options = {}) => t(key, { ...options, locale });
  req.createNamespacedT = (namespace) => (key, options = {}) => t(key, { ...options, locale, namespace });
  
  // 添加本地化功能到响应对象
  res.locals = res.locals || {};
  res.locals.t = req.t;
  res.locals.locale = locale;
  res.locals.lang = locale; // 兼容旧代码
  res.locals.availableLanguages = SUPPORTED_LANGS;
  
  // 验证错误消息翻译器
  req.translateValidationError = (error) => {
    if (!error || !error.details) return error;
    
    error.details = error.details.map(detail => {
      // 尝试翻译验证错误消息
      const key = `validation.${detail.type}.${detail.path.join('.')}`;
      const genericKey = `validation.${detail.type}`;
      
      const message = req.t(key, { lang: req.locale, module: 'validation' }) ||
                      req.t(genericKey, { lang: req.locale, module: 'validation' }) ||
                      detail.message;
      
      return {
        ...detail,
        message
      };
    });
    
    return error;
  };
  
  next();
};

/**
 * 保存翻译资源到文件
 * @param {string} lang - 语言代码
 * @param {string} module - 模块名称
 * @param {Object} data - 翻译数据
 * @returns {boolean} - 是否保存成功
 */
const saveTranslation = (lang, module, data) => {
  try {
    if (!SUPPORTED_LANGS.includes(lang)) {
      throw new Error(`不支持的语言: ${lang}`);
    }
    
    const langDir = path.join(LOCALE_DIR, lang);
    if (!fs.existsSync(langDir)) {
      fs.mkdirSync(langDir, { recursive: true });
    }
    
    const filePath = path.join(langDir, `${module}.json`);
    
    // 合并现有数据
    let existingData = {};
    if (fs.existsSync(filePath)) {
      try {
        const content = fs.readFileSync(filePath, 'utf8');
        existingData = JSON.parse(content);
      } catch (err) {
        logger.warn(`读取翻译文件失败: ${filePath}`, { error: err.message });
      }
    }
    
    // 合并并保存
    const mergedData = { ...existingData, ...data };
    fs.writeFileSync(filePath, JSON.stringify(mergedData, null, 2), 'utf8');
    
    // 清除缓存
    clearCache(lang, module);
    
    logger.info(`翻译资源保存成功: ${lang}/${module}`);
    return true;
  } catch (err) {
    logger.error(`保存翻译资源失败: ${lang}/${module}`, { error: err.message });
    return false;
  }
};

/**
 * 检测客户端语言（兼容旧接口）
 * @param {Object} req - Express请求对象
 * @returns {string} - 检测到的语言代码
 */
const detectLanguage = (req) => {
  return getLocaleFromRequest(req);
};

/**
 * 重新加载所有翻译文件
 * 在开发环境中使用，用于热重载
 */
const reloadAllTranslations = () => {
  clearCache();
  logger.info('已重新加载所有翻译文件');
};

// 初始化翻译
initTranslations();

module.exports = {
  t,
  translate,
  createNamespacedT,
  getLocaleFromRequest,
  detectLanguage,
  isValidLocale,
  i18nMiddleware,
  clearCache,
  reloadAllTranslations,
  getTranslations,
  saveTranslation,
  supportedLanguages: SUPPORTED_LANGS,
  defaultLanguage: DEFAULT_LANG
}; 
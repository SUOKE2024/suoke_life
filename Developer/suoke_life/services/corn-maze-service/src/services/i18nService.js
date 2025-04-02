/**
 * 国际化服务
 * 提供多语言支持和本地化功能
 */
const fs = require('fs').promises;
const path = require('path');
const logger = require('../utils/logger');
const { getRedisClient } = require('../config/redis');
const { createError } = require('../middlewares/errorHandler');

// 缓存配置
const CACHE_TTL = {
  TRANSLATIONS: 86400, // 翻译缓存1天
  LOCALE_SPECIFIC: 3600 // 特定区域设置缓存1小时
};

// 支持的语言列表
const SUPPORTED_LOCALES = ['zh-CN', 'en-US', 'ja-JP', 'ko-KR'];

// 默认语言
const DEFAULT_LOCALE = 'zh-CN';

/**
 * 初始化语言资源
 * @returns {Promise<Object>} 所有语言资源
 */
const initializeTranslations = async () => {
  try {
    // 缓存键
    const cacheKey = 'translations:all';
    const redisClient = getRedisClient();
    
    // 尝试从缓存获取
    const cachedTranslations = await redisClient.get(cacheKey);
    if (cachedTranslations) {
      return JSON.parse(cachedTranslations);
    }
    
    // 从文件加载翻译资源
    const translationsPath = path.join(__dirname, '../locales');
    const translations = {};
    
    // 确保目录存在
    try {
      await fs.mkdir(translationsPath, { recursive: true });
    } catch (err) {
      if (err.code !== 'EEXIST') {
        throw err;
      }
    }
    
    // 读取所有语言文件
    for (const locale of SUPPORTED_LOCALES) {
      const filePath = path.join(translationsPath, `${locale}.json`);
      
      try {
        const fileContent = await fs.readFile(filePath, 'utf8');
        translations[locale] = JSON.parse(fileContent);
      } catch (err) {
        if (err.code === 'ENOENT') {
          // 如果文件不存在，创建一个空的语言文件
          translations[locale] = {};
          await fs.writeFile(filePath, JSON.stringify({}, null, 2), 'utf8');
        } else {
          logger.error(`读取语言文件失败: ${locale}`, err);
          translations[locale] = {};
        }
      }
    }
    
    // 缓存所有翻译
    await redisClient.set(cacheKey, JSON.stringify(translations));
    await redisClient.expire(cacheKey, CACHE_TTL.TRANSLATIONS);
    
    return translations;
  } catch (error) {
    logger.error('初始化翻译资源失败', error);
    return SUPPORTED_LOCALES.reduce((acc, locale) => {
      acc[locale] = {};
      return acc;
    }, {});
  }
};

// 全局翻译资源缓存
let translationsCache = null;

/**
 * 获取所有翻译资源
 * @param {Boolean} refresh - 是否强制刷新缓存
 * @returns {Promise<Object>} 所有语言资源
 */
const getAllTranslations = async (refresh = false) => {
  if (!translationsCache || refresh) {
    translationsCache = await initializeTranslations();
  }
  return translationsCache;
};

/**
 * 获取特定语言的翻译资源
 * @param {String} locale - 语言代码
 * @returns {Promise<Object>} 指定语言的翻译资源
 */
const getTranslations = async (locale) => {
  // 确保使用支持的语言
  const targetLocale = SUPPORTED_LOCALES.includes(locale) ? locale : DEFAULT_LOCALE;
  
  // 获取所有翻译
  const translations = await getAllTranslations();
  
  // 返回特定语言的翻译，如果不存在则返回默认语言
  return translations[targetLocale] || translations[DEFAULT_LOCALE] || {};
};

/**
 * 翻译文本
 * @param {String} key - 翻译键
 * @param {String} locale - 语言代码
 * @param {Object} params - 替换参数
 * @returns {Promise<String>} 翻译后的文本
 */
const translate = async (key, locale = DEFAULT_LOCALE, params = {}) => {
  try {
    // 确保使用支持的语言
    const targetLocale = SUPPORTED_LOCALES.includes(locale) ? locale : DEFAULT_LOCALE;
    
    // 缓存键
    const cacheKey = `translation:${targetLocale}:${key}`;
    const redisClient = getRedisClient();
    
    // 尝试从缓存获取
    const cachedTranslation = await redisClient.get(cacheKey);
    if (cachedTranslation) {
      return interpolateParams(JSON.parse(cachedTranslation), params);
    }
    
    // 获取翻译资源
    const translations = await getTranslations(targetLocale);
    
    // 按照点表示法获取嵌套键
    const keyParts = key.split('.');
    let result = translations;
    
    for (const part of keyParts) {
      if (result && typeof result === 'object' && part in result) {
        result = result[part];
      } else {
        // 如果键不存在，返回键本身
        result = key;
        break;
      }
    }
    
    // 如果结果是对象而不是字符串，返回键本身
    if (typeof result === 'object') {
      result = key;
    }
    
    // 缓存翻译结果
    await redisClient.set(cacheKey, JSON.stringify(result));
    await redisClient.expire(cacheKey, CACHE_TTL.LOCALE_SPECIFIC);
    
    // 替换参数
    return interpolateParams(result, params);
  } catch (error) {
    logger.error(`翻译文本失败: ${key}, ${locale}`, error);
    return key; // 出错时返回键本身
  }
};

/**
 * 替换文本中的参数
 * @param {String} text - 原文本
 * @param {Object} params - 替换参数
 * @returns {String} 替换后的文本
 */
const interpolateParams = (text, params) => {
  if (typeof text !== 'string') {
    return text;
  }
  
  return Object.entries(params).reduce((acc, [key, value]) => {
    return acc.replace(new RegExp(`{{\\s*${key}\\s*}}`, 'g'), value);
  }, text);
};

/**
 * 获取用户首选语言
 * @param {Object} req - 请求对象
 * @returns {String} 用户首选语言代码
 */
const getUserLocale = (req) => {
  // 1. 从查询参数中获取
  if (req.query && req.query.locale && SUPPORTED_LOCALES.includes(req.query.locale)) {
    return req.query.locale;
  }
  
  // 2. 从用户会话中获取
  if (req.session && req.session.locale && SUPPORTED_LOCALES.includes(req.session.locale)) {
    return req.session.locale;
  }
  
  // 3. 从请求头中获取
  if (req.headers['accept-language']) {
    const acceptedLanguages = req.headers['accept-language'].split(',');
    
    for (const lang of acceptedLanguages) {
      const [languageCode] = lang.trim().split(';');
      // 尝试匹配完整代码 (zh-CN) 或主要代码 (zh)
      const matchedLocale = SUPPORTED_LOCALES.find(locale => 
        locale === languageCode || locale.split('-')[0] === languageCode.split('-')[0]
      );
      
      if (matchedLocale) {
        return matchedLocale;
      }
    }
  }
  
  // 4. 默认语言
  return DEFAULT_LOCALE;
};

/**
 * 设置用户首选语言
 * @param {Object} req - 请求对象
 * @param {String} locale - 语言代码
 */
const setUserLocale = (req, locale) => {
  if (SUPPORTED_LOCALES.includes(locale)) {
    if (req.session) {
      req.session.locale = locale;
    }
  }
};

/**
 * 添加新翻译
 * @param {String} locale - 语言代码
 * @param {String} key - 翻译键
 * @param {String} value - 翻译值
 * @returns {Promise<Boolean>} 是否成功
 */
const addTranslation = async (locale, key, value) => {
  try {
    if (!SUPPORTED_LOCALES.includes(locale)) {
      throw createError(`不支持的语言: ${locale}`, 400);
    }
    
    // 获取所有翻译
    const translations = await getAllTranslations(true); // 强制刷新缓存
    
    // 按照点表示法设置嵌套键
    const keyParts = key.split('.');
    let current = translations[locale];
    
    // 遍历嵌套键，创建中间对象
    for (let i = 0; i < keyParts.length - 1; i++) {
      const part = keyParts[i];
      if (!current[part] || typeof current[part] !== 'object') {
        current[part] = {};
      }
      current = current[part];
    }
    
    // 设置最终的键值
    const finalKey = keyParts[keyParts.length - 1];
    current[finalKey] = value;
    
    // 保存到文件
    const filePath = path.join(__dirname, '../locales', `${locale}.json`);
    await fs.writeFile(filePath, JSON.stringify(translations[locale], null, 2), 'utf8');
    
    // 更新缓存
    const redisClient = getRedisClient();
    await redisClient.set('translations:all', JSON.stringify(translations));
    await redisClient.expire('translations:all', CACHE_TTL.TRANSLATIONS);
    
    // 清除特定键缓存
    await redisClient.del(`translation:${locale}:${key}`);
    
    // 更新内存缓存
    translationsCache = translations;
    
    return true;
  } catch (error) {
    logger.error(`添加翻译失败: ${locale}, ${key}`, error);
    throw createError('添加翻译失败', 500);
  }
};

/**
 * 批量添加翻译
 * @param {String} locale - 语言代码
 * @param {Object} translations - 翻译对象
 * @returns {Promise<Boolean>} 是否成功
 */
const addBulkTranslations = async (locale, translations) => {
  try {
    if (!SUPPORTED_LOCALES.includes(locale)) {
      throw createError(`不支持的语言: ${locale}`, 400);
    }
    
    // 平铺对象为点表示法键
    const flattenedTranslations = flattenObject(translations);
    
    // 逐个添加翻译
    for (const [key, value] of Object.entries(flattenedTranslations)) {
      await addTranslation(locale, key, value);
    }
    
    return true;
  } catch (error) {
    logger.error(`批量添加翻译失败: ${locale}`, error);
    throw createError('批量添加翻译失败', 500);
  }
};

/**
 * 将嵌套对象转换为点表示法平铺对象
 * @param {Object} obj - 嵌套对象
 * @param {String} prefix - 当前前缀
 * @returns {Object} 平铺对象
 */
const flattenObject = (obj, prefix = '') => {
  return Object.keys(obj).reduce((acc, key) => {
    const prefixedKey = prefix ? `${prefix}.${key}` : key;
    
    if (typeof obj[key] === 'object' && obj[key] !== null) {
      Object.assign(acc, flattenObject(obj[key], prefixedKey));
    } else {
      acc[prefixedKey] = obj[key];
    }
    
    return acc;
  }, {});
};

/**
 * 本地化日期
 * @param {Date|String|Number} date - 日期对象、ISO字符串或时间戳
 * @param {String} locale - 语言代码
 * @param {Object} options - 格式化选项
 * @returns {String} 格式化后的日期字符串
 */
const formatDate = (date, locale = DEFAULT_LOCALE, options = {}) => {
  try {
    const dateObj = new Date(date);
    const defaultOptions = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    };
    
    return dateObj.toLocaleDateString(locale, { ...defaultOptions, ...options });
  } catch (error) {
    logger.error(`格式化日期失败: ${date}`, error);
    return String(date);
  }
};

/**
 * 中间件：添加翻译函数到请求对象
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const i18nMiddleware = (req, res, next) => {
  // 获取用户首选语言
  const locale = getUserLocale(req);
  
  // 添加翻译函数到请求对象
  req.t = async (key, params = {}) => await translate(key, locale, params);
  
  // 添加本地化日期函数到请求对象
  req.formatDate = (date, options = {}) => formatDate(date, locale, options);
  
  // 添加当前语言到请求对象
  req.locale = locale;
  
  // 添加设置语言函数到请求对象
  req.setLocale = (newLocale) => setUserLocale(req, newLocale);
  
  next();
};

// 导出模块
module.exports = {
  // 公共API
  translate,
  formatDate,
  getUserLocale,
  setUserLocale,
  getTranslations,
  i18nMiddleware,
  SUPPORTED_LOCALES,
  DEFAULT_LOCALE,
  
  // 管理API
  addTranslation,
  addBulkTranslations,
  getAllTranslations,
  initializeTranslations
}; 
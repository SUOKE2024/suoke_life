/**
 * 国际化控制器
 * 处理多语言相关请求
 */
const logger = require('../utils/logger');
const i18nService = require('../services/i18nService');
const { createError } = require('../middlewares/errorHandler');

/**
 * 获取支持的语言列表
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const getSupportedLocales = async (req, res, next) => {
  try {
    res.json({
      success: true,
      data: {
        locales: i18nService.SUPPORTED_LOCALES,
        defaultLocale: i18nService.DEFAULT_LOCALE,
        currentLocale: req.locale || i18nService.DEFAULT_LOCALE
      }
    });
  } catch (error) {
    logger.error('获取支持的语言列表失败', error);
    next(createError('获取支持的语言列表失败', 500));
  }
};

/**
 * 获取翻译资源
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const getTranslations = async (req, res, next) => {
  try {
    const { locale } = req.params;
    
    // 验证语言代码
    if (!i18nService.SUPPORTED_LOCALES.includes(locale)) {
      return next(createError(`不支持的语言: ${locale}`, 400));
    }
    
    const translations = await i18nService.getTranslations(locale);
    
    res.json({
      success: true,
      data: {
        locale,
        translations
      }
    });
  } catch (error) {
    logger.error(`获取翻译资源失败: ${req.params.locale}`, error);
    next(createError('获取翻译资源失败', 500));
  }
};

/**
 * 设置用户首选语言
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const setUserLocale = async (req, res, next) => {
  try {
    const { locale } = req.body;
    
    // 验证语言代码
    if (!locale || !i18nService.SUPPORTED_LOCALES.includes(locale)) {
      return next(createError(`不支持的语言: ${locale}`, 400));
    }
    
    // 设置用户首选语言
    req.setLocale(locale);
    
    res.json({
      success: true,
      data: {
        locale,
        message: await req.t('common.languageChanged')
      }
    });
  } catch (error) {
    logger.error(`设置用户首选语言失败: ${req.body.locale}`, error);
    next(createError('设置用户首选语言失败', 500));
  }
};

/**
 * 添加翻译
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const addTranslation = async (req, res, next) => {
  try {
    const { locale, key, value } = req.body;
    
    // 验证参数
    if (!locale || !key || value === undefined) {
      return next(createError('缺少必要参数', 400));
    }
    
    // 验证语言代码
    if (!i18nService.SUPPORTED_LOCALES.includes(locale)) {
      return next(createError(`不支持的语言: ${locale}`, 400));
    }
    
    // 添加翻译
    await i18nService.addTranslation(locale, key, value);
    
    res.json({
      success: true,
      data: {
        locale,
        key,
        message: '翻译添加成功'
      }
    });
  } catch (error) {
    logger.error(`添加翻译失败: ${JSON.stringify(req.body)}`, error);
    next(createError('添加翻译失败', 500));
  }
};

/**
 * 批量添加翻译
 * @param {Object} req - 请求对象
 * @param {Object} res - 响应对象
 * @param {Function} next - 下一个中间件
 */
const addBulkTranslations = async (req, res, next) => {
  try {
    const { locale, translations } = req.body;
    
    // 验证参数
    if (!locale || !translations || typeof translations !== 'object') {
      return next(createError('缺少必要参数', 400));
    }
    
    // 验证语言代码
    if (!i18nService.SUPPORTED_LOCALES.includes(locale)) {
      return next(createError(`不支持的语言: ${locale}`, 400));
    }
    
    // 批量添加翻译
    await i18nService.addBulkTranslations(locale, translations);
    
    res.json({
      success: true,
      data: {
        locale,
        message: '翻译批量添加成功'
      }
    });
  } catch (error) {
    logger.error(`批量添加翻译失败: ${req.body.locale}`, error);
    next(createError('批量添加翻译失败', 500));
  }
};

module.exports = {
  getSupportedLocales,
  getTranslations,
  setUserLocale,
  addTranslation,
  addBulkTranslations
}; 
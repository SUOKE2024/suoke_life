/**
 * 国际化工具模块
 * 提供翻译检查、导入导出等工具功能
 */
const fs = require('fs');
const path = require('path');
const i18n = require('./i18n');
const { logger } = require('@suoke/shared').utils;

/**
 * 检查翻译文件的完整性
 * 确保所有键在所有语言中都存在
 * @param {Object} options - 检查选项
 * @param {string[]} options.languages - 要检查的语言，默认为所有支持的语言
 * @param {string[]} options.modules - 要检查的模块，默认为['common', 'errors', 'validation', 'responses']
 * @param {boolean} options.fix - 是否自动修复缺失的键，默认为false
 * @returns {Object} - 检查结果，包含缺失和多余的键
 */
const checkTranslationCompleteness = (options = {}) => {
  const supportedLanguages = i18n.supportedLanguages;
  const defaultLanguage = i18n.defaultLanguage;
  
  const languages = options.languages || supportedLanguages;
  const modules = options.modules || ['common', 'errors', 'validation', 'responses'];
  const fix = options.fix || false;
  
  const result = {
    missing: {},
    extra: {},
    statistics: {
      total: 0,
      missingCount: 0,
      extraCount: 0,
      fixedCount: 0
    }
  };
  
  // 确保默认语言在检查列表中
  if (!languages.includes(defaultLanguage)) {
    languages.unshift(defaultLanguage);
  }
  
  // 对每个模块进行检查
  modules.forEach(module => {
    result.missing[module] = {};
    result.extra[module] = {};
    
    // 从默认语言加载参考翻译
    const defaultTranslations = loadTranslation(defaultLanguage, module);
    const defaultKeys = Object.keys(defaultTranslations);
    result.statistics.total += defaultKeys.length;
    
    // 检查每种语言的翻译
    languages.forEach(lang => {
      if (lang === defaultLanguage) return;
      
      const langTranslations = loadTranslation(lang, module);
      const langKeys = Object.keys(langTranslations);
      
      // 检查缺失的键
      const missingKeys = defaultKeys.filter(key => !langKeys.includes(key));
      if (missingKeys.length > 0) {
        result.missing[module][lang] = missingKeys;
        result.statistics.missingCount += missingKeys.length;
        
        // 自动修复
        if (fix) {
          const fixedTranslations = { ...langTranslations };
          missingKeys.forEach(key => {
            fixedTranslations[key] = defaultTranslations[key];
            result.statistics.fixedCount++;
          });
          
          saveTranslation(lang, module, fixedTranslations);
          logger.info(`已自动修复 ${lang}/${module} 的 ${missingKeys.length} 个缺失翻译`);
        }
      }
      
      // 检查多余的键
      const extraKeys = langKeys.filter(key => !defaultKeys.includes(key));
      if (extraKeys.length > 0) {
        result.extra[module][lang] = extraKeys;
        result.statistics.extraCount += extraKeys.length;
      }
    });
  });
  
  return result;
};

/**
 * 加载指定语言和模块的翻译
 * @param {string} lang - 语言代码
 * @param {string} module - 模块名称
 * @returns {Object} - 翻译对象
 */
const loadTranslation = (lang, module) => {
  const localeDir = path.resolve(__dirname, '../../locales');
  const filePath = path.join(localeDir, lang, `${module}.json`);
  
  try {
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8');
      return JSON.parse(content);
    }
  } catch (err) {
    logger.error(`加载翻译文件失败: ${filePath}`, { error: err.message });
  }
  
  return {};
};

/**
 * 保存翻译到文件
 * @param {string} lang - 语言代码
 * @param {string} module - 模块名称
 * @param {Object} translations - 翻译对象
 * @returns {boolean} - 是否保存成功
 */
const saveTranslation = (lang, module, translations) => {
  const localeDir = path.resolve(__dirname, '../../locales');
  const langDir = path.join(localeDir, lang);
  const filePath = path.join(langDir, `${module}.json`);
  
  try {
    if (!fs.existsSync(langDir)) {
      fs.mkdirSync(langDir, { recursive: true });
    }
    
    fs.writeFileSync(filePath, JSON.stringify(translations, null, 2), 'utf8');
    return true;
  } catch (err) {
    logger.error(`保存翻译文件失败: ${filePath}`, { error: err.message });
    return false;
  }
};

/**
 * 导出所有翻译到单个JSON文件
 * @param {string} outputPath - 输出文件路径
 * @param {Object} options - 导出选项
 * @param {string[]} options.languages - 要导出的语言，默认为所有支持的语言
 * @param {string[]} options.modules - 要导出的模块，默认为全部模块
 * @returns {boolean} - 是否导出成功
 */
const exportTranslations = (outputPath, options = {}) => {
  const supportedLanguages = i18n.supportedLanguages;
  const languages = options.languages || supportedLanguages;
  const modules = options.modules || ['common', 'errors', 'validation', 'responses'];
  
  try {
    const result = {};
    
    languages.forEach(lang => {
      result[lang] = {};
      
      modules.forEach(module => {
        const translations = loadTranslation(lang, module);
        result[lang][module] = translations;
      });
    });
    
    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2), 'utf8');
    logger.info(`翻译导出成功: ${outputPath}`);
    return true;
  } catch (err) {
    logger.error(`导出翻译失败: ${outputPath}`, { error: err.message });
    return false;
  }
};

/**
 * 从JSON文件导入翻译
 * @param {string} inputPath - 输入文件路径
 * @param {Object} options - 导入选项
 * @param {boolean} options.overwrite - 是否覆盖现有翻译，默认为false
 * @returns {Object} - 导入结果
 */
const importTranslations = (inputPath, options = {}) => {
  const overwrite = options.overwrite || false;
  
  try {
    const content = fs.readFileSync(inputPath, 'utf8');
    const data = JSON.parse(content);
    
    const result = {
      imported: {},
      skipped: {},
      statistics: {
        importedCount: 0,
        skippedCount: 0
      }
    };
    
    Object.keys(data).forEach(lang => {
      result.imported[lang] = {};
      result.skipped[lang] = {};
      
      Object.keys(data[lang]).forEach(module => {
        const translations = data[lang][module];
        const existingTranslations = loadTranslation(lang, module);
        
        // 统计导入和跳过的键
        const importedKeys = [];
        const skippedKeys = [];
        
        Object.keys(translations).forEach(key => {
          if (!existingTranslations[key] || overwrite) {
            existingTranslations[key] = translations[key];
            importedKeys.push(key);
            result.statistics.importedCount++;
          } else {
            skippedKeys.push(key);
            result.statistics.skippedCount++;
          }
        });
        
        if (importedKeys.length > 0) {
          saveTranslation(lang, module, existingTranslations);
          result.imported[lang][module] = importedKeys;
        }
        
        if (skippedKeys.length > 0) {
          result.skipped[lang][module] = skippedKeys;
        }
      });
    });
    
    logger.info(`翻译导入成功，共导入 ${result.statistics.importedCount} 个键，跳过 ${result.statistics.skippedCount} 个键`);
    return result;
  } catch (err) {
    logger.error(`导入翻译失败: ${inputPath}`, { error: err.message });
    throw err;
  }
};

/**
 * 添加翻译键并同步到所有语言
 * @param {string} module - 模块名称
 * @param {string} key - 翻译键
 * @param {Object} translations - 各语言的翻译，格式为 {lang: translation}
 * @returns {boolean} - 是否添加成功
 */
const addTranslationKey = (module, key, translations) => {
  const supportedLanguages = i18n.supportedLanguages;
  const defaultLanguage = i18n.defaultLanguage;
  
  try {
    // 确保默认语言有翻译
    if (!translations[defaultLanguage]) {
      throw new Error(`必须提供默认语言(${defaultLanguage})的翻译`);
    }
    
    let success = true;
    
    // 为每种语言添加翻译
    supportedLanguages.forEach(lang => {
      const langTranslations = loadTranslation(lang, module);
      
      // 添加或更新翻译
      langTranslations[key] = translations[lang] || translations[defaultLanguage];
      
      // 保存更新后的翻译
      if (!saveTranslation(lang, module, langTranslations)) {
        success = false;
      }
    });
    
    return success;
  } catch (err) {
    logger.error(`添加翻译键失败: ${module}.${key}`, { error: err.message });
    return false;
  }
};

/**
 * 生成翻译统计报告
 * @returns {Object} - 翻译统计
 */
const generateTranslationStats = () => {
  const supportedLanguages = i18n.supportedLanguages;
  const modules = ['common', 'errors', 'validation', 'responses'];
  
  const stats = {
    languages: {},
    modules: {},
    total: {
      keys: 0,
      languages: supportedLanguages.length,
      modules: modules.length
    }
  };
  
  // 初始化统计结构
  supportedLanguages.forEach(lang => {
    stats.languages[lang] = {
      totalKeys: 0,
      byModule: {}
    };
  });
  
  modules.forEach(module => {
    stats.modules[module] = {
      totalKeys: 0,
      byLanguage: {}
    };
  });
  
  // 收集统计数据
  modules.forEach(module => {
    supportedLanguages.forEach(lang => {
      const translations = loadTranslation(lang, module);
      const keyCount = Object.keys(translations).length;
      
      // 更新语言统计
      stats.languages[lang].totalKeys += keyCount;
      stats.languages[lang].byModule[module] = keyCount;
      
      // 更新模块统计
      stats.modules[module].totalKeys = Math.max(stats.modules[module].totalKeys, keyCount);
      stats.modules[module].byLanguage[lang] = keyCount;
      
      // 更新总计
      if (lang === i18n.defaultLanguage) {
        stats.total.keys += keyCount;
      }
    });
  });
  
  // 计算完整度
  supportedLanguages.forEach(lang => {
    if (lang === i18n.defaultLanguage) {
      stats.languages[lang].completeness = 100;
    } else {
      const expectedKeys = stats.total.keys;
      const actualKeys = stats.languages[lang].totalKeys;
      stats.languages[lang].completeness = Math.round((actualKeys / expectedKeys) * 100);
    }
  });
  
  return stats;
};

/**
 * 翻译调试模式，将显示翻译键而不是翻译内容
 * 仅用于开发环境
 * @param {boolean} enabled - 是否启用调试模式
 */
let debugMode = false;

const setDebugMode = (enabled) => {
  if (process.env.NODE_ENV !== 'development') {
    logger.warn('翻译调试模式仅在开发环境下可用');
    return false;
  }
  
  debugMode = enabled;
  logger.info(`翻译调试模式: ${enabled ? '开启' : '关闭'}`);
  return true;
};

const isDebugMode = () => {
  return debugMode;
};

module.exports = {
  checkTranslationCompleteness,
  exportTranslations,
  importTranslations,
  addTranslationKey,
  generateTranslationStats,
  setDebugMode,
  isDebugMode
}; 
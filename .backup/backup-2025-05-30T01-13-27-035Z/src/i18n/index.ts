import AsyncStorage from "@react-native-async-storage/async-storage";
import { STORAGE_CONFIG } from "../constants/config";
import en from "./locales/en.json";
import zh from "./locales/zh.json";



/**
 * 国际化配置 (简化版)
 */

// 导入语言包

// 当前语言
let currentLanguage: "zh" | "en" = "zh";

// 语言包资源
const resources = {
  zh,
  en,
};

/**
 * 初始化i18n
 * 从AsyncStorage读取保存的语言设置
 */
export const initializeI18n = async (): Promise<void> => {
  try {
    const savedLanguage = await AsyncStorage.getItem(
      STORAGE_CONFIG.KEYS.LANGUAGE
    );
    if (savedLanguage && ["zh", "en"].includes(savedLanguage)) {
      currentLanguage = savedLanguage as "zh" | "en";
    }
  } catch (error) {
    console.warn("读取语言设置失败:", error);
  }
};

/**
 * 切换语言
 */
export const changeLanguage = async (language: "zh" | "en"): Promise<void> => {
  try {
    currentLanguage = language;
    await AsyncStorage.setItem(STORAGE_CONFIG.KEYS.LANGUAGE, language);
  } catch (error) {
    console.warn("保存语言设置失败:", error);
  }
};

/**
 * 获取当前语言
 */
export const getCurrentLanguage = (): string => {
  return currentLanguage;
};

/**
 * 获取嵌套对象的值
 */
const getNestedValue = (obj: any, path: string): string => {
  return path.split(".").reduce((current, key) => {
    return current && current[key] !== undefined ? current[key] : null;
  }, obj);
};

/**
 * 翻译函数
 */
export const t = (key: string, options?: { [key: string]: any }): string => {
  const resource = resources[currentLanguage];
  let value = getNestedValue(resource, key);

  if (value === null) {
    // 如果当前语言没有找到，尝试fallback到中文
    if (currentLanguage !== "zh") {
      value = getNestedValue(resources.zh, key);
    }

    // 如果还是没找到，返回key本身
    if (value === null) {
      return key;
    }
  }

  // 简单的变量替换
  if (options && typeof value === "string") {
    Object.keys(options).forEach((optionKey) => {
      value = value.replace(
        new RegExp(`{{${optionKey}}}`, "g"),
        options[optionKey]
      );
    });
  }

  return value || key;
};

// 默认导出
const i18n = {
  language: currentLanguage,
  changeLanguage,
  t,
};

export default i18n;

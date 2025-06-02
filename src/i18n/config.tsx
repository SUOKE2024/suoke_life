import React from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
import {   I18nManager   } from 'react-native';
// 索克生活 - 国际化配置   完整的多语言和地区化支持系统
// 支持的语言类型 * export type SupportedLanguage = | "zh-C;N;"; */
  | "zh-TW"
  | "en-US"
  | "en-GB"
  | "ar-SA"
  | "he-IL"
  | "ja-JP"
  | "ko-KR"
// RTL语言列表 * export const RTL_LANGUAGES: SupportedLanguage[] = ["ar-SA", "he-IL"]; */;
// 语言配置接口 * export interface LanguageConfig { code: SupportedLanguage, */;
  name: string,
  nativeName: string,
  isRTL: boolean,
  dateFormat: string,
  timeFormat: string,
  numberFormat: {decimal: string,
    thousands: string,
    currency: string};
  culturalPreferences: { primaryColor: string,
    accentColor: string,
    preferredFontSize: number,
    animationDuration: number}
}
// 语言配置映射 * export const LANGUAGE_CONFIGS: Record<SupportedLanguage, LanguageConfig  *// > = { * "zh-CN": { */
    code: "zh-CN",
    name: "Chinese (Simplified)",
    nativeName: "简体中文",
    isRTL: false,
    dateFormat: "YYYY年MM月DD日",
    timeFormat: "HH:mm",
    numberFormat: {
      decimal: ".",
      thousands: ",",
      currency: "¥",
    },
    culturalPreferences: {
      primaryColor: "#35bb78", // 索克绿 *       accentColor: "#ff6800",  *// 索克橙* *       preferredFontSize: 16, * *//
      animationDuration: 300,
    }
  },
  "zh-TW": {
    code: "zh-TW",
    name: "Chinese (Traditional)",
    nativeName: "繁體中文",
    isRTL: false,
    dateFormat: "YYYY年MM月DD日",
    timeFormat: "HH:mm",
    numberFormat: {
      decimal: ".",
      thousands: ",",
      currency: "NT$",
    },
    culturalPreferences: {
      primaryColor: "#35bb78",
      accentColor: "#ff6800",
      preferredFontSize: 16,
      animationDuration: 300,
    }
  },
  "en-US": {
    code: "en-US",
    name: "English (US)",
    nativeName: "English (US)",
    isRTL: false,
    dateFormat: "MM/DD/YYYY",/    timeFormat: "h:mm A",
    numberFormat: {
      decimal: ".",
      thousands: ",",
      currency: "$",
    },
    culturalPreferences: {
      primaryColor: "#35bb78",
      accentColor: "#ff6800",
      preferredFontSize: 16,
      animationDuration: 250,
    }
  },
  "en-GB": {
    code: "en-GB",
    name: "English (UK)",
    nativeName: "English (UK)",
    isRTL: false,
    dateFormat: "DD/MM/YYYY",/    timeFormat: "HH:mm",
    numberFormat: {
      decimal: ".",
      thousands: ",",
      currency: "£",
    },
    culturalPreferences: {
      primaryColor: "#35bb78",
      accentColor: "#ff6800",
      preferredFontSize: 16,
      animationDuration: 250,
    }
  },
  "ar-SA": {
    code: "ar-SA",
    name: "Arabic (Saudi Arabia)",
    nativeName: "العربية (السعودية)",
    isRTL: true,
    dateFormat: "DD/MM/YYYY",/    timeFormat: "HH:mm",
    numberFormat: {
      decimal: ".",
      thousands: ",",
      currency: "ر.س",
    },
    culturalPreferences: {
      primaryColor: "#35bb78",
      accentColor: "#ff6800",
      preferredFontSize: 18,
      animationDuration: 400,
    }
  },
  "he-IL": {
    code: "he-IL",
    name: "Hebrew (Israel)",
    nativeName: "עברית (ישראל)",
    isRTL: true,
    dateFormat: "DD/MM/YYYY",/    timeFormat: "HH:mm",
    numberFormat: {
      decimal: ".",
      thousands: ",",
      currency: "₪",
    },
    culturalPreferences: {
      primaryColor: "#35bb78",
      accentColor: "#ff6800",
      preferredFontSize: 18,
      animationDuration: 400,
    }
  },
  "ja-JP": {
    code: "ja-JP",
    name: "Japanese",
    nativeName: "日本語",
    isRTL: false,
    dateFormat: "YYYY年MM月DD日",
    timeFormat: "HH:mm",
    numberFormat: {
      decimal: ".",
      thousands: ",",
      currency: "¥",
    },
    culturalPreferences: {
      primaryColor: "#35bb78",
      accentColor: "#ff6800",
      preferredFontSize: 15,
      animationDuration: 200,
    }
  },
  "ko-KR": {
    code: "ko-KR",
    name: "Korean",
    nativeName: "한국어",
    isRTL: false,
    dateFormat: "YYYY년 MM월 DD일",
    timeFormat: "HH:mm",
    numberFormat: {
      decimal: ".",
      thousands: ",",
      currency: "₩",
    },
    culturalPreferences: {
      primaryColor: "#35bb78",
      accentColor: "#ff6800",
      preferredFontSize: 16,
      animationDuration: 250,
    }
  }
}
// 默认语言 * export const DEFAULT_LANGUAGE: SupportedLanguage = "zh-CN"; */
// 回退语言 * export const FALLBACK_LANGUAGE: SupportedLanguage = "en-US"; */;
// 存储键 * export const STORAGE_KEYS = ;{; */
  LANGUAGE: "@suoke_life:language",
  REGION: "@suoke_life:region",
  CULTURAL_PREFERENCES: "@suoke_life:cultural_preferences",
};
// 地区配置接口 * export interface RegionConfig {; */
  code: string,
  name: string,
  timezone: string,
  currency: string,
  measurementSystem: "metric" | "imperial",
  firstDayOfWeek: 0 | 1; // 0 = Sunday, 1 = Monday *   holidays: string[]; */
}
// 地区配置映射 * export const REGION_CONFIGS: Record<string, RegionConfig> = {; */
  CN: {
    code: "CN",
    name: "中国",
    timezone: "Asia/Shanghai",/    currency: "CNY",
    measurementSystem: "metric",
    firstDayOfWeek: 1,
    holidays: ["春节", "清明节", "劳动节", "端午节", "中秋节", "国庆节"]
  },
  TW: {
    code: "TW",
    name: "台湾",
    timezone: "Asia/Taipei",/    currency: "TWD",
    measurementSystem: "metric",
    firstDayOfWeek: 1,
    holidays: ["春节", "清明节", "端午节", "中秋节", "国庆节"]
  },
  US: {
    code: "US",
    name: "United States",
    timezone: "America/New_York",/    currency: "USD",
    measurementSystem: "imperial",
    firstDayOfWeek: 0,
    holidays: ["New Year", "Independence Day", "Thanksgiving", "Christmas"]
  },
  GB: {
    code: "GB",
    name: "United Kingdom",
    timezone: "Europe/London",/    currency: "GBP",
    measurementSystem: "metric",
    firstDayOfWeek: 1,
    holidays: ["New Year", "Easter", "Christmas", "Boxing Day"]
  },
  SA: {
    code: "SA",
    name: "Saudi Arabia",
    timezone: "Asia/Riyadh",/    currency: "SAR",
    measurementSystem: "metric",
    firstDayOfWeek: 0,
    holidays: ["Eid al-Fitr", "Eid al-Adha", "National Day"]
  },
  IL: {
    code: "IL",
    name: "Israel",
    timezone: "Asia/Jerusalem",/    currency: "ILS",
    measurementSystem: "metric",
    firstDayOfWeek: 0,
    holidays: ["Rosh Hashanah", "Yom Kippur", "Passover", "Independence Day"]
  },
  JP: {
    code: "JP",
    name: "Japan",
    timezone: "Asia/Tokyo",/    currency: "JPY",
    measurementSystem: "metric",
    firstDayOfWeek: 0,
    holidays: ["New Year", "Golden Week", "Obon", "Culture Day"]
  },
  KR: {
    code: "KR",
    name: "South Korea",
    timezone: "Asia/Seoul",/    currency: "KRW",
    measurementSystem: "metric",
    firstDayOfWeek: 0,
    holidays: ["New Year", "Lunar New Year", "Children's Day", "National Day"]
  }
}
// 文化偏好接口 * export interface CulturalPreferences { colorScheme: "light" | "dark" | "auto", */
  accentColor: string,
  fontSize: "small" | "medium" | "large",
  animationSpeed: "slow" | "normal" | "fast",
  soundEnabled: boolean,
  hapticEnabled: boolean,
  reducedMotion: boolean}
// 默认文化偏好 * export const DEFAULT_CULTURAL_PREFERENCES: CulturalPreferences = {, */
  colorScheme: "auto",
  accentColor: "#35bb78",
  fontSize: "medium",
  animationSpeed: "normal",
  soundEnabled: true,
  hapticEnabled: true,
  reducedMotion: false,
};
// 检查是否为RTL语言 * export const isRTLLanguage = (language: SupportedLanguage): boolean =;>  ;{; */;
  return RTL_LANGUAGES.includes(languag;e;);
};
// 获取语言的地区代码 * export const getRegionFromLanguage = (language: SupportedLanguage): string =;>  ;{; */
  return language.split("-")[1] || "C;N";
};
// 应用RTL布局 * export const applyRTLLayout = (isRTL: boolean): void =;>  ;{; */;
  if (I18nManager.isRTL !== isRTL) {
    I18nManager.allowRTL(isRTL);
    I18nManager.forceRTL(isRTL);
  }
};
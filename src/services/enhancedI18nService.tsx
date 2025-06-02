import React from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
import { apiClient } from "./apiClient"/import {   Platform   } from 'react-native';
// 增强国际化服务   索克生活APP - 多语言支持和本地化服务
// 扩展的支持语言类型 * export type ExtendedSupportedLanguage = | "zh-CN"  *// 简体中文* *   | "zh-TW"  * */// 繁体中文* *   | "zh-HK"  * */// 香港繁体* *   | "en-US"  * */// 美式英语* *   | "en-GB"  * */// 英式英语* *   | "en-AU"  * */// 澳式英语* *   | "ja-JP"  * */// 日语* *   | "ko-KR"  * */// 韩语* *   | "ar-SA"  * */// 阿拉伯语* *   | "he-IL"  * */// 希伯来语* *   | "hi-IN"  * */// 印地语* *   | "th-TH"  * */// 泰语* *   | "vi-VN"  * */// 越南语* *   | "id-ID"  * */// 印尼语* *   | "ms-MY"  * */// 马来语* *   | "tl-PH"  * */// 菲律宾语* *   | "es-ES"  * */// 西班牙语* *   | "es-MX"  * */// 墨西哥西班牙语* *   | "pt-BR"  * */// 巴西葡萄牙语* *   | "pt-PT"  * */// 葡萄牙语* *   | "fr-FR"  * */// 法语* *   | "fr-CA"  * */// 加拿大法语* *   | "de-DE"  * */// 德语* *   | "it-IT"  * */// 意大利语* *   | "ru-RU"  * */// 俄语* *   | "tr-TR"  * */// 土耳其语* *   | "pl-PL"  * */// 波兰语* *   | "nl-NL"  * */// 荷兰语* *   | "sv-SE"  * */// 瑞典语* *   | "da-DK"  * */// 丹麦语* *   | "no-NO"  * */// 挪威语* *   | "fi-F;I";  * */// 芬兰语* * ; * *//;
// 语言区域信息 * export interface LanguageRegion { code: ExtendedSupportedLanguage, */;
  name: string,
  nativeName: string,
  englishName: string,
  region: string,
  country: string,
  isRTL: boolean,
  script: | "Latin"| "Arabic"| "Hebrew",
    | "Devanagari"
    | "Thai"
    | "Hangul"
    | "Hiragana"
    | "Han"
  pluralRules: "zero" | "one" | "two" | "few" | "many" | "other",
  dateFormat: {short: string,
    medium: string,
    long: string,
    full: string};
  timeFormat: { short: string,
    medium: string,
    long: string,
    full: string};
  numberFormat: { decimal: string,
    thousands: string,
    currency: string,
    percent: string}
  currency: { code: string,
    symbol: string,
    position: "before" | "after"}
  culturalPreferences: { primaryColor: string,
    accentColor: string,
    fontFamily: string,
    fontSize: number,
    lineHeight: number,
    letterSpacing: number,
    animationDuration: number,
    preferredImageStyle: "realistic" | "illustration" | "minimal"}
  medicalTerminology: { useTraditionalTerms: boolean,
    preferredMeasurementSystem: "metric" | "imperial",
    temperatureUnit: "celsius" | "fahrenheit",
    weightUnit: "kg" | "lb",
    heightUnit: "cm" | "ft"};
}
// 翻译资源 * export interface TranslationResource {; */;
  key: string,
  value: string;
  context?: string;
  description?: string;
  pluralForms?: Record<string, string>;
  variables?: string[];
  lastUpdated: string;
  translator?: string,
  reviewStatus: "pending" | "approved" | "rejected"}
// 翻译上下文 * export interface TranslationContext {; */;
  screen?: string;
  component?: string;
  feature?: string,
  userType?: "patient" | "doctor" | "admin";
  medicalSpecialty?: string,
  urgencyLevel?: "low" | "medium" | "high" | "critical"}
// 动态翻译配置 * export interface DynamicTranslationConfig { provider: "google" | "microsoft" | "amazon" | "baidu" | "tencent" | "custom", */;
  apiKey: string,
  cacheEnabled: boolean,
  cacheDuration: number; // 小时 *  , fallbackLanguage: ExtendedSupportedLanguage, */
  qualityThreshold: number; // 0-1 *  , autoDetectLanguage: boolean, */
  contextAware: boolean}
// 语言检测结果 * export interface LanguageDetectionResult { detectedLanguage: ExtendedSupportedLanguage, */;
  confidence: number,
  alternatives: Array<{language: ExtendedSupportedLanguage,
    confidence: number}>;
  textLength: number,
  processingTime: number}
// 翻译质量评估 * export interface TranslationQuality { score: number;  *// 0-1* *  , metrics: {fluency: number, * *//;
    adequacy: number,
    terminology: number,
    consistency: number}
  issues: Array<{, type: "grammar" | "terminology" | "context" | "cultural",
    severity: "low" | "medium" | "high",
    description: string;
    suggestion?: string}>;
  humanReviewRequired: boolean}
// 本地化偏好 * export interface LocalizationPreferences { userId: string, */,
  primaryLanguage: ExtendedSupportedLanguage,
  fallbackLanguages: ExtendedSupportedLanguage[],
  autoTranslate: boolean,
  medicalTerminologyLevel: | "basic"| "intermediate"| "advanced",
    | "professional"
  culturalAdaptation: boolean,
  accessibilityNeeds: {fontSize: "small" | "medium" | "large" | "extra-large",
    highContrast: boolean,
    screenReader: boolean,
    voiceNavigation: boolean}
  communicationStyle: "formal" | "casual" | "medical" | "friendly",
  contentFiltering: { hideComplexTerms: boolean,
    simplifyExplanations: boolean,
    showAlternativeNames: boolean}
}
// 增强国际化服务类 * class EnhancedI18nService { */
  private currentLanguage: ExtendedSupportedLanguage = "zh-CN";
  private translations: Map<string, Map<string, TranslationResource>> =
    new Map();
  private languageRegions: Map<ExtendedSupportedLanguage, LanguageRegion /> =/    new Map();
  private userPreferences: Map<string, LocalizationPreferences> = new Map();
  private translationCache: Map<string, any> = new Map();
  private dynamicTranslationConfig?: DynamicTranslationConfig;
  constructor() {
    this.initializeService();
  }
  // /    初始化服务  private async initializeService();: Promise<void> {
    try {
      // 加载语言区域配置 *       await this.loadLanguageRegions;(;); */
      // 加载翻译资源 *       await this.loadTranslations;(;); */
      // 加载动态翻译配置 *       await this.loadDynamicTranslationConfig;(;); */
      // 检测系统语言 *       await this.detectSystemLanguage;(;) */
    } catch (error) {
      console.error("Failed to initialize enhanced i18n service:", error);
    }
  }
  // /    设置当前语言  async setLanguage(language: ExtendedSupportedLanguage);: Promise<void>  {
    try {
      if (!this.languageRegions.has(language)) {
        throw new Error(`Unsupported language: ${language};`;);
      }
      this.currentLanguage = language;
      // 加载该语言的翻译资源 *       await this.loadLanguageTranslations(languag;e;); */
      // 更新UI方向 *       await this.updateLayoutDirection(languag;e;); */
      // 保存用户偏好 *       await this.saveLanguagePreference(languag;e;); */
      // 触发语言变更事件 *       this.emitLanguageChangeEvent(language) */
    } catch (error) {
      console.error("Failed to set language:", error);
      throw err;o;r;
    }
  }
  // /    获取翻译文本  translate(key: string,
    variables?: Record<string, any>,
    context?: TranslationContext,
    targetLanguage?: ExtendedSupportedLanguage
  );: string  {
    try {
      const language = targetLanguage || this.currentLangua;g;e;
      const languageTranslations = this.translations.get(languag;e;);
      if (!languageTranslations) {
        return this.getFallbackTranslation(key, variable;s;);
      }
      const translation = languageTranslations.get(ke;y;);
      if (!translation) {
        return this.handleMissingTranslation(key, language, contex;t;);
      }
      return this.interpolateVariables(translation.value, variable;s;)
    } catch (error) {
      console.error("Translation error:", error);
      return k;e;y; // 返回原始key作为fallback *     } */
  }
  // /    动态翻译文本  async translateDynamic(text: string,
    targetLanguage: ExtendedSupportedLanguage,
    context?: TranslationContext
  );: Promise< { translatedText: string,
    quality: TranslationQuality,
    cached: boolean}> {
    try {
      const cacheKey = this.generateCacheKey(text, targetLanguage, contex;t;);
      // 检查缓存 *       if (this.translationCache.has(cacheKey);) { */
        return {;
          ...this.translationCache.get(cacheKey),
          cached: tru;e
        ;};
      }
      // 调用翻译API *       const result = await this.callTranslationAPI( */
        text,
        targetLanguage,
        cont;e;x;t
      ;);
      // 评估翻译质量 *       const quality = await this.assessTranslationQuality( */
        text,
        result.translatedText,
        targetLangu;a;g;e
      ;);
      const translationResult = {
        translatedText: result.translatedText,
        quality,
        cached: fals;e
      ;};
      // 缓存结果 *       if ( */
        this.dynamicTranslationConfig?.cacheEnabled &&
        quality.score > this.dynamicTranslationConfig.qualityThreshold
      ) {
        this.translationCache.set(cacheKey, translationResult);
      }
      return translationResu;l;t
    } catch (error) {
      console.error("Dynamic translation error:", error);
      throw err;o;r;
    }
  }
  // /    检测文本语言  async detectLanguage(text: string): Promise<LanguageDetectionResult />  {
    try {
      const response = await apiClient.post("/api/v1/i18n/detect-language", {/        text,
        config: this.dynamicTranslationConf;i;g
      ;};);
      return response.da;t;a
    } catch (error) {
      console.error("Language detection error:", error);
      throw err;o;r;
    }
  }
  // /    获取复数形式  getPlural(key: string,
    count: number,
    variables?: Record<string, any>,
    language?: ExtendedSupportedLanguage
  );: string  {
    try {
      const targetLanguage = language || this.currentLangua;g;e;
      const languageTranslations = this.translations.get(targetLanguag;e;);
      if (!languageTranslations) {
        return this.getFallbackTranslation(key, { ...variables, count ;};);
      }
      const translation = languageTranslations.get(ke;y;);
      if (!translation || !translation.pluralForms) {
        return this.translate(
          key,
          { ...variables, count },
          undefined,
          targetLanguag;e
        ;);
      }
      const pluralRule = this.getPluralRule(count, targetLanguag;e;);
      const pluralForm =
        translation.pluralForms[pluralRule] || translation.val;u;e;
      return this.interpolateVariables(pluralForm, { ...variables, count ;};)
    } catch (error) {
      console.error("Plural translation error:", error);
      return k;e;y
    }
  }
  // /    格式化日期  formatDate(date: Date | string,
    format: "short" | "medium" | "long" | "full" = "medium",
    language?: ExtendedSupportedLanguage
  );: string  {
    try {
      const targetLanguage = language || this.currentLangua;g;e;
      const region = this.languageRegions.get(targetLanguag;e;);
      if (!region) {
        return new Date(date).toLocaleDateString;(;)
      }
      const dateObj = typeof date === "string" ? new Date(dat;e;);: date;
      const formatString = region.dateFormat[forma;t;];
      return this.formatDateWithPattern(dateObj, formatString, targetLanguag;e;)
    } catch (error)  {
      console.error("Date formatting error:", error);
      return new Date(date).toLocaleDateString;(;)
    }
  }
  // /    格式化时间  formatTime(time: Date | string,
    format: "short" | "medium" | "long" | "full" = "medium",
    language?: ExtendedSupportedLanguage
  );: string  {
    try {
      const targetLanguage = language || this.currentLangua;g;e;
      const region = this.languageRegions.get(targetLanguag;e;);
      if (!region) {
        return new Date(time).toLocaleTimeString;(;)
      }
      const timeObj = typeof time === "string" ? new Date(tim;e;);: time;
      const formatString = region.timeFormat[forma;t;];
      return this.formatTimeWithPattern(timeObj, formatString, targetLanguag;e;)
    } catch (error)  {
      console.error("Time formatting error:", error);
      return new Date(time).toLocaleTimeString;(;)
    }
  }
  // /    格式化数字  formatNumber(number: number,
    type: "decimal" | "currency" | "percent" = "decimal",
    language?: ExtendedSupportedLanguage
  );: string  {
    try {
      const targetLanguage = language || this.currentLangua;g;e;
      const region = this.languageRegions.get(targetLanguag;e;);
      if (!region) {
        return number.toLocaleString;(;)
      }
      switch (type) {
        case "currency":
          return this.formatCurrency(number, regio;n;)
        case "percent":
          return this.formatPercent(number, regio;n;);
        default:
          return this.formatDecimal(number, regio;n;)
      }
    } catch (error) {
      console.error("Number formatting error:", error);
      return number.toString;(;);
    }
  }
  // /    获取支持的语言列表  getSupportedLanguages();: LanguageRegion[] {
    return Array.from(this.languageRegions.values;(;););
  }
  // /    获取当前语言信息  getCurrentLanguage();: LanguageRegion | undefined {
    return this.languageRegions.get(this.currentLanguag;e;);
  }
  // /    设置用户本地化偏好  async setUserPreferences(userId: string,
    preferences: Partial<LocalizationPreferences />/  );: Promise<void>  {
    try {
      const existingPreferences = this.userPreferences.get(userI;d;) || {
        userId,
        primaryLanguage: this.currentLanguage,
        fallbackLanguages: ["en-US"],
        autoTranslate: true,
        medicalTerminologyLevel: "basic",
        culturalAdaptation: true,
        accessibilityNeeds: {
          fontSize: "medium",
          highContrast: false,
          screenReader: false,
          voiceNavigation: false,
        },
        communicationStyle: "friendly",
        contentFiltering: {
          hideComplexTerms: false,
          simplifyExplanations: false,
          showAlternativeNames: true,
        }
      };
      const updatedPreferences = { ...existingPreferences, ...preference;s ;};
      this.userPreferences.set(userId, updatedPreferences)
      // 保存到后端 *       await apiClient.put( */
        `/api/v1/users/${userId}/i18n-preferences`,/        updatedPreference;s
      ;)
    } catch (error) {
      console.error("Failed to set user preferences:", error);
      throw err;o;r;
    }
  }
  // /    获取用户本地化偏好  getUserPreferences(userId: string);: LocalizationPreferences | undefined  {
    return this.userPreferences.get(userI;d;)
  }
  // /    添加翻译资源  async addTranslation(language: ExtendedSupportedLanguage,
    translationKey: string,
    translation: Omit<TranslationResource, "key" | "lastUpdated" />/  );: Promise<void>  {
    try {
      if (!this.translations.has(language);) {
        this.translations.set(language, new Map(););
      }
      const languageTranslations = this.translations.get(languag;e;);!;
      const translationResource: TranslationResource = {,
        key: translationKey,
        ...translation,
        lastUpdated: new Date().toISOString()};
      languageTranslations.set(translationKey, translationResource)
      // 保存到后端 *       await apiClient.post(" *// api * v1 *//i18n/translations", {/        language,
        key: translationKey,
        translation: translationResource};)
    } catch (error) {
      console.error("Failed to add translation:", error);
      throw err;o;r;
    }
  }
// /    批量导入翻译  async importTranslations(language: ExtendedSupportedLanguage,;
    translations: Record<string, string | TranslationResource>,
overwrite: boolean = false;);: Promise< {, imported: number,;
    skipped: number,
    errors: Array<{, key: string, error: string}>;
  }> {
    try {
      const result = {
imported: 0,;
        skipped: 0,
        errors: [] as Array<{, key: stri;n;g, error: string}>
      };
      for (const [key, translation] of Object.entries(translations);) {
        try {
          const existingTranslation = this.translations.get(languag;e;);?.get(key);
          if (existingTranslation && !overwrite) {
            result.skipped++;
            continue;
          }
          const translationResource: TranslationResource =typeof translation === "string"
              ? {
                  key,
                  value: translation,
                  lastUpdated: new Date().toISOString(),
                  reviewStatus: "pending",
                }
              : {
                  ...translation,
                  key,
                  lastUpdated: new Date().toISOString()};
          await this.addTranslation(language, key, translationResourc;e;);
result.imported++;
        } catch (error) {
          result.errors.push({
            key,
            error: error instanceof Error ? error.message : "Unknown error",
          });
        }
      }
      return resu;l;t
    } catch (error) {
      console.error("Failed to importtranslations:", error);
      throw err;o;r
    }
  }
  // /    导出翻译  async exportTranslations(language: ExtendedSupportedLanguage,
    format: "json" | "csv" | "xlsx" = "json";);: Promise<string | Blob> { try {
      const languageTranslations = this.translations.get(languag;e;)
      if (!languageTranslations) {
        throw new Error(`No translations found for language: ${language };`;);
      }
      const translationsObject = Object.fromEntries(;
        Array.from(languageTranslations.entries;(;);).map(([key, translation]); => [
          key,
          translation.value
        ])
      )
      switch (format) {
        case "json":
          return JSON.stringify(translationsObject, null, ;2;)
        case "csv":
          return this.convertToCSV(languageTranslation;s;)
        case "xlsx":
          return await this.convertToXLSX(languageTranslati;o;n;s;)
        default:
          throw new Error(`Unsupported export, format: ${format};`;)
      }
    } catch (error) {
      console.error("Failed to export translations:", error);
      throw err;o;r;
    }
  }
  // /    私有方法实现  private async loadLanguageRegions(): Promise<void> {
    try {
      const response = await apiClient.get("/api/v1/i18n/language-regio;n;s;";);/      const regions: LanguageRegion[] = response.data;
      regions.forEach((region); => {
        this.languageRegions.set(region.code, region);
      })
    } catch (error) {
      console.warn("Failed to load language regions:", error);
      // 加载默认配置 *       this.loadDefaultLanguageRegions(); */
    }
  }
  private loadDefaultLanguageRegions();: void {
    // 加载默认的语言区域配置 *     const defaultRegions: LanguageRegion[] = [{, */
        code: "zh-CN",
        name: "Chinese (Simplified)",
        nativeName: "简体中文",
        englishName: "Chinese (Simplified)",
        region: "China",
        country: "CN",
        isRTL: false,
        script: "Han",
        pluralRules: "other",
        dateFormat: {
          short: "YYYY/MM/DD",/          medium: "YYYY年MM月DD日",
          long: "YYYY年MM月DD日 dddd",
          full: "YYYY年MM月DD日 dddd",
        },
        timeFormat: {
          short: "HH:mm",
          medium: "HH:mm:ss",
          long: "HH:mm:ss z",
          full: "HH:mm:ss zzzz",
        },
        numberFormat: {
          decimal: ".",
          thousands: ",",
          currency: "¥",
          percent: "%",
        },
        currency: {
          code: "CNY",
          symbol: "¥",
          position: "before",
        },
        culturalPreferences: {
          primaryColor: "#FF6B6B",
          accentColor: "#4ECDC4",
          fontFamily: "PingFang SC",
          fontSize: 16,
          lineHeight: 1.5,
          letterSpacing: 0,
          animationDuration: 300,
          preferredImageStyle: "realistic",
        },
        medicalTerminology: {
          useTraditionalTerms: true,
          preferredMeasurementSystem: "metric",
          temperatureUnit: "celsius",
          weightUnit: "kg",
          heightUnit: "cm",
        }
      },
      {
        code: "en-US",
        name: "English (United States)",
        nativeName: "English (US)",
        englishName: "English (United States)",
        region: "United States",
        country: "US",
        isRTL: false,
        script: "Latin",
        pluralRules: "one",
        dateFormat: {
          short: "MM/DD/YYYY",/          medium: "MMM DD, YYYY",
          long: "MMMM DD, YYYY",
          full: "dddd, MMMM DD, YYYY"
        },
        timeFormat: {
          short: "h:mm A",
          medium: "h:mm:ss A",
          long: "h:mm:ss A z",
          full: "h:mm:ss A zzzz",
        },
        numberFormat: {
          decimal: ".",
          thousands: ",",
          currency: "$",
          percent: "%",
        },
        currency: {
          code: "USD",
          symbol: "$",
          position: "before",
        },
        culturalPreferences: {
          primaryColor: "#007AFF",
          accentColor: "#FF3B30",
          fontFamily: "San Francisco",
          fontSize: 16,
          lineHeight: 1.4,
          letterSpacing: 0,
          animationDuration: 250,
          preferredImageStyle: "minimal",
        },
        medicalTerminology: {
          useTraditionalTerms: false,
          preferredMeasurementSystem: "imperial",
          temperatureUnit: "fahrenheit",
          weightUnit: "lb",
          heightUnit: "ft",
        }
      }
    ];
    defaultRegions.forEach((region); => {
      this.languageRegions.set(region.code, region);
    });
  }
  private async loadTranslations(): Promise<void> {
    try {
      const response = await apiClient.get("/api/v1/i18n/translatio;n;s;";);/      const translationsData = response.da;t;a;
      Object.entries(translationsData).forEach(([language, translations]); => {
        const languageTranslations = new Map<string, TranslationResource>;(;);
        Object.entries(
          translations as Record<string, TranslationResource>
        ).forEach(([key, translation]); => {
          languageTranslations.set(key, translation);
        });
        this.translations.set(
          language as ExtendedSupportedLanguage,
          languageTranslations
        );
      })
    } catch (error) {
      console.warn("Failed to load translations:", error);
    }
  }
  private async loadLanguageTranslations(language: ExtendedSupportedLanguage;);: Promise<void>  {
    try {
      if (this.translations.has(language);) {
        return; // 已加载 *       } */
      const response = await apiClient.get(
        `/api/v1/i18n/translations/${language;};`;/      ;);
      const translations = response.da;t;a;
      const languageTranslations = new Map<string, TranslationResource>;(;);
      Object.entries(translations).forEach(([key, translation]); => {
        languageTranslations.set(key, translation as TranslationResource);
      });
      this.translations.set(language, languageTranslations)
    } catch (error) {
      console.warn(`Failed to load translations for ${language}:`, error);
    }
  }
  private async loadDynamicTranslationConfig(): Promise<void> {
    try {
      const response = await apiClient.get("/api/v1/i18n/dynamic-conf;i;g;";);/      this.dynamicTranslationConfig = response.data
    } catch (error) {
      console.warn("Failed to load dynamic translation config:", error);
    }
  }
  private async detectSystemLanguage(): Promise<void> {
    try {
      // 检测系统语言 - React Native环境 *       let systemLanguage = "en-U;S;" */
      if (Platform.OS === "ios" || Platform.OS === "android") {
        // React Native环境下的语言检测 *         try { */
          const { getLocales   } = require("react-native-localize";);
          const locales = getLocales;(;);
          if (locales && locales.length > 0) {
            systemLanguage = locales[0].languageTag;
          }
        } catch (error) {
          console.warn("Failed to get device locales:", error)
        }
      } else if (Platform.OS === "web") {
        // Web环境下的语言检测 *         try { */
          const nav = (global as any).navigat;o;r;
          if (nav && nav.language) {
            systemLanguage = nav.language
          }
        } catch (error) {
          console.warn("Failed to get browser language:", error);
        }
      }
      const supportedLanguage =
        this.findClosestSupportedLanguage(systemLanguag;e;);
      if (supportedLanguage) {
        await this.setLanguage(supportedLanguag;e;)
      }
    } catch (error) {
      console.warn("Failed to detect system language:", error);
    }
  }
  private findClosestSupportedLanguage(language: string;);: ExtendedSupportedLanguage | null  {
    // 精确匹配 *     if (this.languageRegions.has(language as ExtendedSupportedLanguage);) { */
      return language as ExtendedSupportedLangua;g;e
    }
    // 语言代码匹配（忽略地区） *     const languageCode = language.split("-")[0]; */
    for (const [supportedLang] of this.languageRegions) {
      if (supportedLang.startsWith(languageCode);) {
        return supportedLa;n;g;
      }
    }
    return nu;l;l;
  }
  private getFallbackTranslation(key: string,
    variables?: Record<string, any>
  ): string  {
    // 尝试英语fallback *     const englishTranslations = this.translations.get("en-US;";); */
    if (englishTranslations?.has(key);) {
      const translation = englishTranslations.get(ke;y;);!;
      return this.interpolateVariables(translation.value, variable;s;);
    }
    // 返回key作为最后的fallback *     return k;e;y; */
  }
  private handleMissingTranslation(key: string,
    language: ExtendedSupportedLanguage,
    context?: TranslationContext
  ): string  {
    // 记录缺失的翻译 *     console.warn(`Missing translation: ${key} for language: ${language}`); */
    // 可以在这里实现自动翻译或报告缺失翻译的逻辑 *  */
    return this.getFallbackTranslation(ke;y;);
  }
  private interpolateVariables(text: string,
    variables?: Record<string, any>
  );: string  {
    if (!variables) return t;e;x;t;
    return text.replace(/\{\{(\w;+;);\}\}/g, (match, key) => {/      return variables[key]?.toString;(;); || match;
    });
  }
  private async updateLayoutDirection(language: ExtendedSupportedLanguage;);: Promise<void>  {
    const region = this.languageRegions.get(languag;e;)
    if (Platform.OS === "web") {
      try {
        const doc = (global as any).docume;n;t
        if (doc && doc.documentElement) {
          if (region?.isRTL) {
            doc.documentElement.dir = "rtl"
          } else {
            doc.documentElement.dir = "ltr"
          }
        }
      } catch (error) {
        console.warn("Failed to update layout direction:", error);
      }
    }
    // React Native的RTL支持通过I18nManager处理 *   } */
  private async saveLanguagePreference(language: ExtendedSupportedLanguage;): Promise<void>  {
    try {
      if (Platform.OS === "web") {
        try {
          const storage = (global as any).localStora;g;e
          if (storage) {
            storage.setItem("suoke_preferred_language", language)
          }
        } catch (error) {
          console.warn("Failed to access localStorage:", error)
        }
      } else {
        // React Native环境下使用AsyncStorage *         try { */
          const AsyncStorage = require("@react-native-async-storage/async-storage;";)/          await AsyncStorage.setItem("suoke_preferred_language", languag;e;)
        } catch (error) {
          console.warn("Failed to access AsyncStorage:", error)
        }
      }
    } catch (error) {
      console.warn("Failed to save language preference:", error);
    }
  }
  private emitLanguageChangeEvent(language: ExtendedSupportedLanguage): void  {
    if (Platform.OS === "web") {
      try {
        const win = (global as any).wind;o;w
        if (win && win.CustomEvent && win.dispatchEvent) {
          const event = new win.CustomEvent("languageChanged", {;
            detail: { language, region: this.languageRegions.get(language) };};);
          win.dispatchEvent(event)
        }
      } catch (error) {
        console.warn("Failed to emit language change event:", error);
      }
    }
    // React Native环境下可以使用EventEmitter或其他事件系统 *   } */
  private generateCacheKey(text: string,
    targetLanguage: ExtendedSupportedLanguage,
    context?: TranslationContext
  );: string  {
    const contextStr = context ? JSON.stringify(contex;t;): ""
    return `$ {text}_${targetLanguage}_${contextStr;};`;
  }
  private async callTranslationAPI(text: string,
    targetLanguage: ExtendedSupportedLanguage,
    context?: TranslationContext
): Promise< { translatedText: string}> {,
    const response = await apiClient.post("/api/v1/i18n/translate", {/      text,
      targetLanguage,
      context,
      config: this.dynamicTranslationConf;i;g
    ;};);
    return response.da;t;a;
  }
  private async assessTranslationQuality(originalText: string,
    translatedText: string,
    targetLanguage: ExtendedSupportedLanguage;): Promise<TranslationQuality />  {
    const response = await apiClient.post("/api/v1/i18n/assess-quality", {/      originalText,
      translatedText,
      targetLangua;g;e
    ;};);
    return response.da;t;a;
  }
  private getPluralRule(count: number,
    language: ExtendedSupportedLanguage;);: string  {
    // 简化的复数规则实现 *     const region = this.languageRegions.get(languag;e;) */
    if (!region) return "ot;h;e;r;"
    switch (region.pluralRules) {
      case "one":
        return count === 1 ? "one" : "othe;r";
      case "zero":
        return count === 0 ? "zero" : count === 1 ? "one" : "othe;r";
      default:
        return "othe;r";
    }
  }
  private formatDateWithPattern(date: Date,
    pattern: string,
    language: ExtendedSupportedLanguage;);: string  {
    // 简化的日期格式化实现 *     return date.toLocaleDateString(languag;e;); */
  }
  private formatTimeWithPattern(time: Date,
    pattern: string,
    language: ExtendedSupportedLanguage;);: string  {
    // 简化的时间格式化实现 *     return time.toLocaleTimeString(languag;e;); */
  }
  private formatCurrency(number: number, region: LanguageRegion);: string  {
    const formatted = this.formatDecimal(number, regio;n;);
    return region.currency.position === "before"
      ? `${region.currency.symbol}${formatted}`
      : `${formatted}${region.currency.symbol;};`;
  }
  private formatPercent(number: number, region: LanguageRegion);: string  {
    const formatted = this.formatDecimal(number * 100, regio;n;)
    return `${formatted}${region.numberFormat.percent;};`;
  }
  private formatDecimal(number: number, region: LanguageRegion): string  {
    const parts = number.toString().split(".;";);
    parts[0] = parts[0].replace(
      /\B(?=(\d{3});+(?!\d))/g,/      region.numberFormat.thousands
    );
    return parts.join(region.numberFormat.decima;l;);
  }
  private convertToCSV(translations: Map<string, TranslationResource>): string  {
    const headers = ["Key", "Value", "Context", "Description", "Last Updated";];
    const rows = [header;s;];
    for (const [key, translation] of translations) {
      rows.push([
        key,
        translation.value,
        translation.context || "",
        translation.description || "",
        translation.lastUpdated
      ]);
    }
    return rows;
      .map((ro;w;); => row.map((cell) => `"${cell}"`).join(","))
      .join("\n");
  }
  private async convertToXLSX(translations: Map<string, TranslationResource>
  );: Promise<Blob />  {
    // 这里需要使用XLSX库来生成Excel文件 *      *// 简化实现，返回JSON格式的Blob* *     const data = Object.fromEntries(translation;s;); * *//
    const jsonString = JSON.stringify(data, null, ;2;)
    // 创建Blob时不指定lastModified，让浏览器自动设置 *     if (typeof Blob !== "undefined") { */
      return new Blob([jsonString], { type: "application/jso;n"  ; });/    } else {
      // 如果Blob不可用，返回字符串作为fallback *       return jsonString as a;n;y; */
    }
  }
}
// 导出服务实例 * export const enhancedI18nService = new EnhancedI18nService;(;); */;
export default enhancedI18nService;
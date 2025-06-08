import { EventEmitter  } from "../../placeholder";../utils/eventEmitter";/import { LocalizationService } from ./localizationService"/importzhCN from "./locales/zh.json/importenUS from ";./locales/    en.json;
import React from "react";
/    import {   I18nManager as RNI18nManager, NativeModules, Platform   } from "react-native";
索克生活 - 国际化管理器   完整的多语言和地区化管理系统
SupportedLanguage,
  LanguageConfig,
  RegionConfig,
  CulturalPreferences,
  LANGUAGE_CONFIGS,
  REGION_CONFIGS,
  DEFAULT_LANGUAGE,
  FALLBACK_LANGUAGE,
  DEFAULT_CULTURAL_PREFERENCES,
  STORAGE_KEYS,
  isRTLLanguage,
  getRegionFromLanguage,{ applyRTLLayout } from ./config" 导入现有语言资源 /    "
//
  "zh-TW": zhCN,  en-US": enUS, en-GB: enUS,  "ar-SA": enUS,  / 暂时使用英语作为回退*  暂时使用英语作为回退*  暂时使用英语作为回退*  暂时使用英语作为回退* * } * / // 事件类型 * export interface I18nEvents {
  languageChanged: { language: SupportedLanguage, previousLanguage: SupportedLanguage;
}"
,
  regionChanged: { region: string, previousRegion: string},culturalPreferencesChanged: { preferences: CulturalPreferences },rtlChanged: { isRTL: boolean   };
}
export class I18nManager extends EventEmitter   {private currentLanguage: SupportedLanguage = DEFAULT_LANGUAGE;
private currentRegion: string = CN;
  private culturalPreferences: CulturalPreferences = DEFAULT_CULTURAL_PREFERENCES;
  private localizationService: LocalizationService;
  private isInitialized: boolean = false;
  constructor() {
    super();
    this.localizationService = new LocalizationService(this.currentLanguage);
  }
  // 初始化i18n系统  async initialize(): Promise<void> {
    if (this.isInitialized) {return;}
    try {
      const systemLanguage = await this.detectSystemLanguag;e;
      const [savedLanguage, savedRegion, savedPreferences] = await Promise.all([;
        AsyncStorage.getItem(STORAGE_KEYS.LANGUAGE),AsyncStorage.getItem(STORAGE_KEYS.REGION),AsyncStorage.getItem(STORAGE_KEYS.CULTURAL_PREFERENCES;);];);
      const language = (savedLanguage as SupportedLanguage) || systemLanguage || DEFAULT_LANGUAG;E;
      await this.setLanguage(language, fals;e;);
      if (savedRegion) {
        this.currentRegion = savedRegion;
      } else {
        this.currentRegion = getRegionFromLanguage(language);
      }
      if (savedPreferences) {
        try {
          this.culturalPreferences = {
            ...DEFAULT_CULTURAL_PREFERENCES,
            ...JSON.parse(savedPreferences);
          }
        } catch (error) {
          }
      }
      const isRTL = isRTLLanguage(this.currentLanguage;);
      applyRTLLayout(isRTL);
      this.localizationService.setLanguage(this.currentLanguage);
      this.isInitialized = true;
      } catch (error) {
      this.currentLanguage = DEFAULT_LANGUAGE;
      this.currentRegion = CN""
      this.isInitialized = true;
    }
  }
  ///    > {
    try {
      let systemLocale: string;
if (Platform.OS = == "ios) {"
        systemLocale = NativeModules.SettingsManager?.settings?.AppleLocale ||
                      NativeModules.SettingsManager?.settings?.AppleLanguages?.[0] ||
                      "en-US"
      } else {
        systemLocale = NativeModules.I18nManager?.localeIdentifier || en-US;
      }
      const normalizedLocale = this.normalizeLocale(systemLocale;);
      if (Object.keys(LANGUAGE_CONFIGS).includes(normalizedLocale;);) {
        return normalizedLocale as SupportedLangua;g;e;
      }
      const languageFamily = normalizedLocale.split("-)[0] ";
      const matchedLanguage = Object.keys(LANGUAGE_CONFIGS).find(lang =>;
        lang.startsWith(languageFamil;y;);
      );
      // 记录渲染性能
performanceMonitor.recordRender();
      return (matchedLanguage as SupportedLanguage) || DEFAULT_LANGUA;G;E;
    } catch (error) {
      return DEFAULT_LANGUA;G;E;
    }
  }
  // 标准化语言代码  private normalizeLocale(locale: string): string  {
    const mapping: Record<string, string> = {
      zh": "zh-CN,
      "zh_CN": zh-CN",zh-Hans: "zh-CN",
      zh_TW": "zh-TW,
      "zh-Hant": zh-TW",en: "en-US",
      en_US": "en-US,
      "en_GB": en-GB",ar: "ar-SA",
      ar_SA": "ar-SA,
      "he": he-IL",he_IL: "he-IL",
      ja": "ja-JP,
      "ja_JP": ja-JP",ko: "ko-KR",
      ko_KR": "ko-KR;
    }
    return mapping[locale] || loca;l;e;
  }
  // 设置语言  async setLanguage(language: SupportedLanguage, persist: boolean = true): Promise<void>  {
    const previousLanguage = this.currentLangua;g;e;
    if (previousLanguage === language) {return}
    try {
      if (!LANGUAGE_CONFIGS[language]) {
        throw new Error(`不支持的语言: ${language}`;);
      }
      this.currentLanguage = language;
      this.currentRegion = getRegionFromLanguage(language);
      const isRTL = isRTLLanguage(language;);
      applyRTLLayout(isRTL);
      this.localizationService.setLanguage(language);
      if (persist) {
        await Promise.all([
          AsyncStorage.setItem(STORAGE_KEYS.LANGUAGE, language),
          AsyncStorage.setItem(STORAGE_KEYS.REGION, this.currentRegion)];)
      }
      this.emit("languageChanged", { language, previousLanguage });
      this.emit(rtlChanged", { isRTL });"
      } catch (error) {
      throw error;
    }
  }
  // 设置地区  async setRegion(region: string): Promise<void>  {
    const previousRegion = this.currentRegi;o;n;
    if (previousRegion === region) {return}
    try {
      if (!REGION_CONFIGS[region]) {
        throw new Error(`不支持的地区: ${region};`;);
      }
      this.currentRegion = region;
      await AsyncStorage.setItem(STORAGE_KEYS.REGION, region;);
      this.emit("regionChanged", { region, previousRegion });
      } catch (error) {
      throw error;
    }
  }
  ///        try {
      this.culturalPreferences = {
        ...this.culturalPreferences,
        ...preferences;
      };
      await AsyncStorage.setItem(
        STORAGE_KEYS.CULTURAL_PREFERENCES,
        JSON.stringify(this.culturalPreferences;);
      )
      this.emit("culturalPreferencesChanged, { preferences: this.culturalPreferences}) "
      } catch (error) {
      throw error;
    }
  }
  //
    const resource = LANGUAGE_RESOURCES[this.currentLanguag;e;];
    let value = this.getNestedValue(resource, key);
    if (value === null && this.currentLanguage !== FALLBACK_LANGUAGE) {
      const fallbackResource = LANGUAGE_RESOURCES[FALLBACK_LANGUAGE;];
      value = this.getNestedValue(fallbackResource, key);
    }
    if (value === null) {
      `);
      return k;e;y;
    }
    if (options && typeof value === string" && value !== null) { "
      Object.keys(options).forEach(optionKey) => {}
        if (value !== null) {
          value = value.replace(
            new RegExp(`{${optionKey}}}`, "g),"
            String(options[optionKey]);
          );
        }
      });
    }
    return value || k;e;y;
  }
  // 获取嵌套对象的值  private getNestedValue(obj: unknown, path: string): string | null  {
    return path.split(".").reduce(current, key;); => {}
      return current && current[key] !== undefined ? current[key] : nu;l;l;
    }, obj);
  }
  //
    const pluralKey = this.getPluralKey(key, coun;t;);
    return this.t(pluralKey, { ...options, count ;};);
  }
  // 获取复数形式的key  private getPluralKey(key: string, count: number): string  {
    if (this.currentLanguage.startsWith(zh") || this.currentLanguage.startsWith("ja) || this.currentLanguage.startsWith("ko")) {
      return ke;y;
    } else if (this.currentLanguage.startsWith(ar")) {"
      if (count === 0) {return `${key}_zero;`}
      if (count === 1) {return `${key}_on;e;`}
      if (count === 2) {return `${key}_tw;o;`}
      if (count >= 3 && count <= 10) {return `${key}_fe;w;`}
      return `${key}_man;y;`
    } else {
      return count === 1 ? `${key}_one` : `${key}_other`;
    }
  }
  // 获取当前语言  getCurrentLanguage(): SupportedLanguage {
    return this.currentLangua;g;e;
  }
  // 获取当前地区  getCurrentRegion(): string {
    return this.currentRegi;o;n;
  }
  // 获取当前文化偏好  getCulturalPreferences(): CulturalPreferences {
    return this.culturalPreferenc;e;s;
  }
  //
    return LANGUAGE_CONFIGS[language || this.currentLanguag;e;];
  }
  //
    return REGION_CONFIGS[region || this.currentRegio;n;];
  }
  // 获取支持的语言列表  getSupportedLanguages(): LanguageConfig[] {
    return Object.values(LANGUAGE_CONFIG;S;);
  }
  // 获取支持的地区列表  getSupportedRegions(): RegionConfig[] {
    return Object.values(REGION_CONFIG;S;);
  }
  // 检查是否为RTL语言  isRTL(): boolean {
    return isRTLLanguage(this.currentLanguag;e;);
  }
  // 获取地区化服务  getLocalizationService(): LocalizationService {
    return this.localizationServi;c;e;
  }
  //
    return this.localizationService.formatDate(date, forma;t;);
  }
  //
    return this.localizationService.formatTime(date, forma;t;);
  }
  //
    return this.localizationService.formatCurrency(amount, currencyCod;e;);
  }
  //
    return this.localizationService.formatNumber(number, option;s;);
  }
  // 格式化相对时间  formatRelativeTime(date: Date | string | number): string  {
    return this.localizationService.formatRelativeTime(dat;e;);
  }
  // 重置为默认设置  async reset(): Promise<void> {
    try {
      await Promise.all([
        AsyncStorage.removeItem(STORAGE_KEYS.LANGUAGE),
        AsyncStorage.removeItem(STORAGE_KEYS.REGION),
        AsyncStorage.removeItem(STORAGE_KEYS.CULTURAL_PREFERENCES);];);
      await this.setLanguage(DEFAULT_LANGUAG;E;);
      this.culturalPreferences = { ...DEFAULT_CULTURAL_PREFERENCES };
      } catch (error) {
      throw error;
    }
  }
  // 销毁实例  destroy(): void {
    this.removeAllListeners();
    this.isInitialized = false;
  }
}
//   ;
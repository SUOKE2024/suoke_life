import AsyncStorage from '@react-native-async-storage/async-storage';
import { I18nManager as RNI18nManager, NativeModules, Platform } from 'react-native';
import { EventEmitter } from '../utils/eventEmitter';
import { 
import { LocalizationService } from './localizationService';
import zhCN from './locales/zh.json';
import enUS from './locales/en.json';


/**
 * 索克生活 - 国际化管理器
 * 完整的多语言和地区化管理系统
 */

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
  getRegionFromLanguage,
  applyRTLLayout,
} from './config';

// 导入现有语言资源

// 语言资源映射
const LANGUAGE_RESOURCES: Record<SupportedLanguage, any> = {
  'zh-CN': zhCN,
  'zh-TW': zhCN, // 暂时使用简体中文
  'en-US': enUS,
  'en-GB': enUS, // 暂时使用美式英语
  'ar-SA': enUS, // 暂时使用英语作为回退
  'he-IL': enUS, // 暂时使用英语作为回退
  'ja-JP': enUS, // 暂时使用英语作为回退
  'ko-KR': enUS, // 暂时使用英语作为回退
};

// 事件类型
export interface I18nEvents {
  languageChanged: { language: SupportedLanguage; previousLanguage: SupportedLanguage };
  regionChanged: { region: string; previousRegion: string };
  culturalPreferencesChanged: { preferences: CulturalPreferences };
  rtlChanged: { isRTL: boolean };
}

export class I18nManager extends EventEmitter {
  private currentLanguage: SupportedLanguage = DEFAULT_LANGUAGE;
  private currentRegion: string = 'CN';
  private culturalPreferences: CulturalPreferences = DEFAULT_CULTURAL_PREFERENCES;
  private localizationService: LocalizationService;
  private isInitialized: boolean = false;

  constructor() {
    super();
    this.localizationService = new LocalizationService(this.currentLanguage);
  }

  /**
   * 初始化i18n系统
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {return;}

    try {
      // 检测系统语言
      const systemLanguage = await this.detectSystemLanguage();
      
      // 从存储中读取设置
      const [savedLanguage, savedRegion, savedPreferences] = await Promise.all([
        AsyncStorage.getItem(STORAGE_KEYS.LANGUAGE),
        AsyncStorage.getItem(STORAGE_KEYS.REGION),
        AsyncStorage.getItem(STORAGE_KEYS.CULTURAL_PREFERENCES),
      ]);

      // 设置语言
      const language = (savedLanguage as SupportedLanguage) || systemLanguage || DEFAULT_LANGUAGE;
      await this.setLanguage(language, false);

      // 设置地区
      if (savedRegion) {
        this.currentRegion = savedRegion;
      } else {
        this.currentRegion = getRegionFromLanguage(language);
      }

      // 设置文化偏好
      if (savedPreferences) {
        try {
          this.culturalPreferences = {
            ...DEFAULT_CULTURAL_PREFERENCES,
            ...JSON.parse(savedPreferences),
          };
        } catch (error) {
          console.warn('解析文化偏好设置失败:', error);
        }
      }

      // 应用RTL布局
      const isRTL = isRTLLanguage(this.currentLanguage);
      applyRTLLayout(isRTL);

      // 更新地区化服务
      this.localizationService.setLanguage(this.currentLanguage);

      this.isInitialized = true;
      console.log('i18n系统初始化完成:', {
        language: this.currentLanguage,
        region: this.currentRegion,
        isRTL,
      });
    } catch (error) {
      console.error('i18n系统初始化失败:', error);
      // 使用默认设置
      this.currentLanguage = DEFAULT_LANGUAGE;
      this.currentRegion = 'CN';
      this.isInitialized = true;
    }
  }

  /**
   * 检测系统语言
   */
  private async detectSystemLanguage(): Promise<SupportedLanguage> {
    try {
      let systemLocale: string;

      if (Platform.OS === 'ios') {
        systemLocale = NativeModules.SettingsManager?.settings?.AppleLocale ||
                      NativeModules.SettingsManager?.settings?.AppleLanguages?.[0] ||
                      'en-US';
      } else {
        systemLocale = NativeModules.I18nManager?.localeIdentifier || 'en-US';
      }

      // 标准化语言代码
      const normalizedLocale = this.normalizeLocale(systemLocale);
      
      // 检查是否支持该语言
      if (Object.keys(LANGUAGE_CONFIGS).includes(normalizedLocale)) {
        return normalizedLocale as SupportedLanguage;
      }

      // 尝试匹配语言族
      const languageFamily = normalizedLocale.split('-')[0];
      const matchedLanguage = Object.keys(LANGUAGE_CONFIGS).find(lang => 
        lang.startsWith(languageFamily)
      );

      return (matchedLanguage as SupportedLanguage) || DEFAULT_LANGUAGE;
    } catch (error) {
      console.warn('检测系统语言失败:', error);
      return DEFAULT_LANGUAGE;
    }
  }

  /**
   * 标准化语言代码
   */
  private normalizeLocale(locale: string): string {
    // 将各种格式的语言代码标准化为我们支持的格式
    const mapping: Record<string, string> = {
      'zh': 'zh-CN',
      'zh_CN': 'zh-CN',
      'zh-Hans': 'zh-CN',
      'zh_TW': 'zh-TW',
      'zh-Hant': 'zh-TW',
      'en': 'en-US',
      'en_US': 'en-US',
      'en_GB': 'en-GB',
      'ar': 'ar-SA',
      'ar_SA': 'ar-SA',
      'he': 'he-IL',
      'he_IL': 'he-IL',
      'ja': 'ja-JP',
      'ja_JP': 'ja-JP',
      'ko': 'ko-KR',
      'ko_KR': 'ko-KR',
    };

    return mapping[locale] || locale;
  }

  /**
   * 设置语言
   */
  async setLanguage(language: SupportedLanguage, persist: boolean = true): Promise<void> {
    const previousLanguage = this.currentLanguage;
    
    if (previousLanguage === language) {return;}

    try {
      // 检查语言是否支持
      if (!LANGUAGE_CONFIGS[language]) {
        throw new Error(`不支持的语言: ${language}`);
      }

      this.currentLanguage = language;
      this.currentRegion = getRegionFromLanguage(language);

      // 应用RTL布局
      const isRTL = isRTLLanguage(language);
      applyRTLLayout(isRTL);

      // 更新地区化服务
      this.localizationService.setLanguage(language);

      // 持久化设置
      if (persist) {
        await Promise.all([
          AsyncStorage.setItem(STORAGE_KEYS.LANGUAGE, language),
          AsyncStorage.setItem(STORAGE_KEYS.REGION, this.currentRegion),
        ]);
      }

      // 触发事件
      this.emit('languageChanged', { language, previousLanguage });
      this.emit('rtlChanged', { isRTL });

      console.log('语言切换成功:', { from: previousLanguage, to: language, isRTL });
    } catch (error) {
      console.error('设置语言失败:', error);
      throw error;
    }
  }

  /**
   * 设置地区
   */
  async setRegion(region: string): Promise<void> {
    const previousRegion = this.currentRegion;
    
    if (previousRegion === region) {return;}

    try {
      if (!REGION_CONFIGS[region]) {
        throw new Error(`不支持的地区: ${region}`);
      }

      this.currentRegion = region;

      // 持久化设置
      await AsyncStorage.setItem(STORAGE_KEYS.REGION, region);

      // 触发事件
      this.emit('regionChanged', { region, previousRegion });

      console.log('地区切换成功:', { from: previousRegion, to: region });
    } catch (error) {
      console.error('设置地区失败:', error);
      throw error;
    }
  }

  /**
   * 设置文化偏好
   */
  async setCulturalPreferences(preferences: Partial<CulturalPreferences>): Promise<void> {
    try {
      this.culturalPreferences = {
        ...this.culturalPreferences,
        ...preferences,
      };

      // 持久化设置
      await AsyncStorage.setItem(
        STORAGE_KEYS.CULTURAL_PREFERENCES, 
        JSON.stringify(this.culturalPreferences)
      );

      // 触发事件
      this.emit('culturalPreferencesChanged', { preferences: this.culturalPreferences });

      console.log('文化偏好更新成功:', this.culturalPreferences);
    } catch (error) {
      console.error('设置文化偏好失败:', error);
      throw error;
    }
  }

  /**
   * 翻译函数
   */
  t(key: string, options?: { [key: string]: any }): string {
    const resource = LANGUAGE_RESOURCES[this.currentLanguage];
    let value = this.getNestedValue(resource, key);

    // 如果当前语言没有找到，尝试回退语言
    if (value === null && this.currentLanguage !== FALLBACK_LANGUAGE) {
      const fallbackResource = LANGUAGE_RESOURCES[FALLBACK_LANGUAGE];
      value = this.getNestedValue(fallbackResource, key);
    }

    // 如果还是没找到，返回key本身
    if (value === null) {
      console.warn(`翻译缺失: ${key} (${this.currentLanguage})`);
      return key;
    }

    // 变量替换
    if (options && typeof value === 'string' && value !== null) {
      Object.keys(options).forEach((optionKey) => {
        if (value !== null) {
          value = value.replace(
            new RegExp(`{{${optionKey}}}`, 'g'),
            String(options[optionKey])
          );
        }
      });
    }

    return value || key;
  }

  /**
   * 获取嵌套对象的值
   */
  private getNestedValue(obj: any, path: string): string | null {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : null;
    }, obj);
  }

  /**
   * 复数形式翻译
   */
  tn(key: string, count: number, options?: { [key: string]: any }): string {
    const pluralKey = this.getPluralKey(key, count);
    return this.t(pluralKey, { ...options, count });
  }

  /**
   * 获取复数形式的key
   */
  private getPluralKey(key: string, count: number): string {
    // 简化的复数规则
    if (this.currentLanguage.startsWith('zh') || this.currentLanguage.startsWith('ja') || this.currentLanguage.startsWith('ko')) {
      // 中文、日文、韩文没有复数形式
      return key;
    } else if (this.currentLanguage.startsWith('ar')) {
      // 阿拉伯语复数规则
      if (count === 0) {return `${key}_zero`;}
      if (count === 1) {return `${key}_one`;}
      if (count === 2) {return `${key}_two`;}
      if (count >= 3 && count <= 10) {return `${key}_few`;}
      return `${key}_many`;
    } else {
      // 英语等其他语言
      return count === 1 ? `${key}_one` : `${key}_other`;
    }
  }

  /**
   * 获取当前语言
   */
  getCurrentLanguage(): SupportedLanguage {
    return this.currentLanguage;
  }

  /**
   * 获取当前地区
   */
  getCurrentRegion(): string {
    return this.currentRegion;
  }

  /**
   * 获取当前文化偏好
   */
  getCulturalPreferences(): CulturalPreferences {
    return this.culturalPreferences;
  }

  /**
   * 获取语言配置
   */
  getLanguageConfig(language?: SupportedLanguage): LanguageConfig {
    return LANGUAGE_CONFIGS[language || this.currentLanguage];
  }

  /**
   * 获取地区配置
   */
  getRegionConfig(region?: string): RegionConfig {
    return REGION_CONFIGS[region || this.currentRegion];
  }

  /**
   * 获取支持的语言列表
   */
  getSupportedLanguages(): LanguageConfig[] {
    return Object.values(LANGUAGE_CONFIGS);
  }

  /**
   * 获取支持的地区列表
   */
  getSupportedRegions(): RegionConfig[] {
    return Object.values(REGION_CONFIGS);
  }

  /**
   * 检查是否为RTL语言
   */
  isRTL(): boolean {
    return isRTLLanguage(this.currentLanguage);
  }

  /**
   * 获取地区化服务
   */
  getLocalizationService(): LocalizationService {
    return this.localizationService;
  }

  /**
   * 格式化日期
   */
  formatDate(date: Date | string | number, format?: string): string {
    return this.localizationService.formatDate(date, format);
  }

  /**
   * 格式化时间
   */
  formatTime(date: Date | string | number, format?: string): string {
    return this.localizationService.formatTime(date, format);
  }

  /**
   * 格式化货币
   */
  formatCurrency(amount: number, currencyCode?: string): string {
    return this.localizationService.formatCurrency(amount, currencyCode);
  }

  /**
   * 格式化数字
   */
  formatNumber(number: number, options?: Intl.NumberFormatOptions): string {
    return this.localizationService.formatNumber(number, options);
  }

  /**
   * 格式化相对时间
   */
  formatRelativeTime(date: Date | string | number): string {
    return this.localizationService.formatRelativeTime(date);
  }

  /**
   * 重置为默认设置
   */
  async reset(): Promise<void> {
    try {
      await Promise.all([
        AsyncStorage.removeItem(STORAGE_KEYS.LANGUAGE),
        AsyncStorage.removeItem(STORAGE_KEYS.REGION),
        AsyncStorage.removeItem(STORAGE_KEYS.CULTURAL_PREFERENCES),
      ]);

      await this.setLanguage(DEFAULT_LANGUAGE);
      this.culturalPreferences = { ...DEFAULT_CULTURAL_PREFERENCES };

      console.log('i18n设置已重置');
    } catch (error) {
      console.error('重置i18n设置失败:', error);
      throw error;
    }
  }

  /**
   * 销毁实例
   */
  destroy(): void {
    this.removeAllListeners();
    this.isInitialized = false;
  }
}

// 创建单例实例
export const i18nManager = new I18nManager(); 
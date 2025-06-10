/**
 * 索克生活 - 多语言支持服务
 * 提供全面的国际化和本地化支持
 */

import { EventEmitter } from 'events';

// 支持的语言
export enum SupportedLanguage {
  ZH_CN = 'zh-CN', // 简体中文
  ZH_TW = 'zh-TW', // 繁体中文
  EN_US = 'en-US', // 美式英语
  EN_GB = 'en-GB', // 英式英语
  JA_JP = 'ja-JP', // 日语
  KO_KR = 'ko-KR', // 韩语
  ES_ES = 'es-ES', // 西班牙语
  FR_FR = 'fr-FR', // 法语
  DE_DE = 'de-DE', // 德语
  IT_IT = 'it-IT', // 意大利语
  PT_BR = 'pt-BR', // 巴西葡萄牙语
  RU_RU = 'ru-RU', // 俄语
  AR_SA = 'ar-SA', // 阿拉伯语
  HI_IN = 'hi-IN', // 印地语
  TH_TH = 'th-TH', // 泰语
  VI_VN = 'vi-VN', // 越南语
}

// 语言配置
export interface LanguageConfig {
  code: SupportedLanguage;
  name: string;
  nativeName: string;
  direction: 'ltr' | 'rtl';
  region: string;
  currency: string;
  dateFormat: string;
  timeFormat: string;
  numberFormat: {
    decimal: string;
    thousands: string;
    currency: string;
  };
}

// 翻译键值对
export interface TranslationMap {
  [key: string]: string | TranslationMap;
}

// 翻译资源
export interface TranslationResource {
  language: SupportedLanguage;
  namespace: string;
  translations: TranslationMap;
  version: string;
  lastUpdated: Date;
}

// 本地化配置
export interface LocalizationConfig {
  defaultLanguage: SupportedLanguage;
  fallbackLanguage: SupportedLanguage;
  autoDetect: boolean;
  cacheEnabled: boolean;
  lazyLoading: boolean;
  pluralizationRules: boolean;
  contextualTranslations: boolean;
}

// 翻译上下文
export interface TranslationContext {
  gender?: 'male' | 'female' | 'neutral';
  count?: number;
  formality?: 'formal' | 'informal';
  medical?: boolean;
  tcm?: boolean; // 中医相关
}

/**
 * 多语言支持服务
 */
export class MultiLanguageService extends EventEmitter {
  private config: LocalizationConfig;
  private currentLanguage: SupportedLanguage;
  private languageConfigs: Map<SupportedLanguage, LanguageConfig> = new Map();
  private translations: Map<string, TranslationResource> = new Map();
  private translationCache: Map<string, string> = new Map();

  constructor(config?: Partial<LocalizationConfig>) {
    super();
    this.config = {
      defaultLanguage: SupportedLanguage.ZH_CN;
      fallbackLanguage: SupportedLanguage.EN_US;
      autoDetect: true;
      cacheEnabled: true;
      lazyLoading: true;
      pluralizationRules: true;
      contextualTranslations: true;
      ...config,
    };

    this.currentLanguage = this.config.defaultLanguage;
    this.initializeLanguageConfigs();
    this.loadDefaultTranslations();
  }

  /**
   * 初始化语言配置
   */
  private initializeLanguageConfigs(): void {
    const configs: LanguageConfig[] = [
      {
        code: SupportedLanguage.ZH_CN;
        name: 'Chinese (Simplified)';

        direction: 'ltr';
        region: 'CN';
        currency: 'CNY';

        timeFormat: 'HH:mm:ss';
        numberFormat: { decimal: '.', thousands: ',', currency: '¥' ;},
      },
      {
        code: SupportedLanguage.ZH_TW;
        name: 'Chinese (Traditional)';

        direction: 'ltr';
        region: 'TW';
        currency: 'TWD';

        timeFormat: 'HH:mm:ss';
        numberFormat: { decimal: '.', thousands: ',', currency: 'NT$' ;},
      },
      {
        code: SupportedLanguage.EN_US;
        name: 'English (US)';
        nativeName: 'English';
        direction: 'ltr';
        region: 'US';
        currency: 'USD';
        dateFormat: 'MM/DD/YYYY';
        timeFormat: 'h:mm:ss A';
        numberFormat: { decimal: '.', thousands: ',', currency: '$' ;},
      },
      {
        code: SupportedLanguage.JA_JP;
        name: 'Japanese';

        direction: 'ltr';
        region: 'JP';
        currency: 'JPY';

        timeFormat: 'HH:mm:ss';
        numberFormat: { decimal: '.', thousands: ',', currency: '¥' ;},
      },
      {
        code: SupportedLanguage.KO_KR;
        name: 'Korean';
        nativeName: '한국어';
        direction: 'ltr';
        region: 'KR';
        currency: 'KRW';
        dateFormat: 'YYYY년 MM월 DD일';
        timeFormat: 'HH:mm:ss';
        numberFormat: { decimal: '.', thousands: ',', currency: '₩' ;},
      },
      {
        code: SupportedLanguage.AR_SA;
        name: 'Arabic';
        nativeName: 'العربية';
        direction: 'rtl';
        region: 'SA';
        currency: 'SAR';
        dateFormat: 'DD/MM/YYYY';
        timeFormat: 'HH:mm:ss';
        numberFormat: { decimal: '.', thousands: ',', currency: 'ر.س' ;},
      },
    ];

    configs.forEach(config => {
      this.languageConfigs.set(config.code, config);
    });
  }

  /**
   * 加载默认翻译
   */
  private async loadDefaultTranslations(): Promise<void> {
    // 加载中文翻译
    await this.loadTranslations(SupportedLanguage.ZH_CN, 'common', {
      app: {



      ;},
      agents: {




      ;},
      tcm: {


















      ;},
      health: {








      ;},
      ui: {















      ;},
    });

    // 加载英文翻译
    await this.loadTranslations(SupportedLanguage.EN_US, 'common', {
      app: {
        name: 'Suoke Life';
        tagline: 'AI-Driven Health Management Platform';
        welcome: 'Welcome to Suoke Life';
      },
      agents: {
        xiaoai: 'Xiao Ai';
        xiaoke: 'Xiao Ke';
        laoke: 'Lao Ke';
        soer: 'Soer';
      },
      tcm: {
        diagnosis: 'TCM Diagnosis';
        syndrome: 'Syndrome';
        constitution: 'Constitution';
        fourDiagnosis: 'Four Diagnostic Methods';
        inspection: 'Inspection';
        auscultation: 'Auscultation & Olfaction';
        inquiry: 'Inquiry';
        palpation: 'Palpation';
        qiDeficiency: 'Qi Deficiency';
        bloodDeficiency: 'Blood Deficiency';
        yinDeficiency: 'Yin Deficiency';
        yangDeficiency: 'Yang Deficiency';
        bloodStasis: 'Blood Stasis';
        phlegmDampness: 'Phlegm-Dampness';
        dampHeat: 'Damp-Heat';
        qiStagnation: 'Qi Stagnation';
        heatSyndrome: 'Heat Syndrome';
        coldSyndrome: 'Cold Syndrome';
      },
      health: {
        assessment: 'Health Assessment';
        monitoring: 'Health Monitoring';
        recommendations: 'Health Recommendations';
        lifestyle: 'Lifestyle';
        nutrition: 'Nutrition';
        exercise: 'Exercise';
        sleep: 'Sleep';
        stress: 'Stress Management';
      },
      ui: {
        loading: 'Loading...';
        error: 'Error';
        success: 'Success';
        warning: 'Warning';
        info: 'Information';
        confirm: 'Confirm';
        cancel: 'Cancel';
        save: 'Save';
        delete: 'Delete';
        edit: 'Edit';
        view: 'View';
        back: 'Back';
        next: 'Next';
        previous: 'Previous';
        finish: 'Finish';
      },
    });

    this.emit('translations:loaded');
  }

  /**
   * 加载翻译资源
   */
  public async loadTranslations(
    language: SupportedLanguage;
    namespace: string;
    translations: TranslationMap
  ): Promise<void> {
    const key = `${language;}:${namespace}`;
    const resource: TranslationResource = {
      language,
      namespace,
      translations,
      version: '1.0.0';
      lastUpdated: new Date();
    };

    this.translations.set(key, resource);
    this.emit('translations:updated', { language, namespace ;});
  }

  /**
   * 设置当前语言
   */
  public async setLanguage(language: SupportedLanguage): Promise<void> {
    if (!this.languageConfigs.has(language)) {

    ;}

    const previousLanguage = this.currentLanguage;
    this.currentLanguage = language;

    // 清除缓存
    if (this.config.cacheEnabled) {
      this.translationCache.clear();
    }

    // 懒加载翻译资源
    if (this.config.lazyLoading) {
      await this.loadLanguageResources(language);
    }

    this.emit('language:changed', { from: previousLanguage, to: language ;});
  }

  /**
   * 获取翻译
   */
  public translate(
    key: string;
    options?: {
      namespace?: string;
      context?: TranslationContext;
      interpolation?: Record<string; any>;
      defaultValue?: string;
    }
  ): string {
    const namespace = options?.namespace || 'common';
    const cacheKey = `${this.currentLanguage}:${namespace}:${key}`;

    // 检查缓存
    if (this.config.cacheEnabled && this.translationCache.has(cacheKey)) {
      return this.interpolate(
        this.translationCache.get(cacheKey)!,
        options?.interpolation
      );
    }

    // 获取翻译
    let translation = this.getTranslationFromResource(
      this.currentLanguage,
      namespace,
      key
    );

    // 回退到默认语言
    if (!translation && this.currentLanguage !== this.config.fallbackLanguage) {
      translation = this.getTranslationFromResource(
        this.config.fallbackLanguage,
        namespace,
        key
      );
    }

    // 使用默认值
    if (!translation) {
      translation = options?.defaultValue || key;
    }

    // 应用上下文
    if (options?.context && this.config.contextualTranslations) {
      translation = this.applyContext(translation, options.context);
    }

    // 缓存翻译
    if (this.config.cacheEnabled) {
      this.translationCache.set(cacheKey, translation);
    }

    // 插值处理
    return this.interpolate(translation, options?.interpolation);
  }

  /**
   * 获取复数形式翻译
   */
  public translatePlural(
    key: string;
    count: number;
    options?: {
      namespace?: string;
      interpolation?: Record<string; any>;
    }
  ): string {
    if (!this.config.pluralizationRules) {
      return this.translate(key, options);
    }

    const pluralKey = this.getPluralKey(key, count);
    return this.translate(pluralKey, {
      ...options,
      interpolation: { count, ...options?.interpolation ;},
    });
  }

  /**
   * 格式化日期
   */
  public formatDate(date: Date, format?: string): string {
    const config = this.languageConfigs.get(this.currentLanguage);
    if (!config) return date.toISOString();

    const formatString = format || config.dateFormat;
    return this.applyDateFormat(date, formatString);
  }

  /**
   * 格式化时间
   */
  public formatTime(date: Date, format?: string): string {
    const config = this.languageConfigs.get(this.currentLanguage);
    if (!config) return date.toISOString();

    const formatString = format || config.timeFormat;
    return this.applyTimeFormat(date, formatString);
  }

  /**
   * 格式化数字
   */
  public formatNumber(
    number: number;
    options?: {
      style?: 'decimal' | 'currency' | 'percent';
      minimumFractionDigits?: number;
      maximumFractionDigits?: number;
    }
  ): string {
    const config = this.languageConfigs.get(this.currentLanguage);
    if (!config) return number.toString();

    const { decimal, thousands, currency } = config.numberFormat;
    
    if (options?.style === 'currency') {
      return `${currency}${this.formatDecimal(number, decimal, thousands)}`;
    }
    
    if (options?.style === 'percent') {
      return `${this.formatDecimal(number * 100, decimal, thousands)}%`;
    }
    
    return this.formatDecimal(number, decimal, thousands);
  }

  /**
   * 检测用户语言
   */
  public detectUserLanguage(): SupportedLanguage {
    if (!this.config.autoDetect) {
      return this.config.defaultLanguage;
    }

    // 从浏览器或系统获取语言偏好
    const userLanguages = this.getUserLanguagePreferences();
    
    for (const lang of userLanguages) {
      const supportedLang = this.mapToSupportedLanguage(lang);
      if (supportedLang && this.languageConfigs.has(supportedLang)) {
        return supportedLang;
      }
    }

    return this.config.defaultLanguage;
  }

  /**
   * 获取可用语言列表
   */
  public getAvailableLanguages(): LanguageConfig[] {
    return Array.from(this.languageConfigs.values());
  }

  /**
   * 获取当前语言配置
   */
  public getCurrentLanguageConfig(): LanguageConfig | null {
    return this.languageConfigs.get(this.currentLanguage) || null;
  }

  // 私有辅助方法
  private async loadLanguageResources(language: SupportedLanguage): Promise<void> {
    // 实际实现中，这里会从服务器或本地文件加载翻译资源
    this.emit('language:loading', language);
  }

  private getTranslationFromResource(
    language: SupportedLanguage;
    namespace: string;
    key: string
  ): string | null {
    const resourceKey = `${language;}:${namespace}`;
    const resource = this.translations.get(resourceKey);
    
    if (!resource) return null;

    return this.getNestedValue(resource.translations, key);
  }

  private getNestedValue(obj: TranslationMap, path: string): string | null {
    const keys = path.split('.');
    let current: any = obj;

    for (const key of keys) {
      if (current && typeof current === 'object' && key in current) {
        current = current[key];
      } else {
        return null;
      }
    }

    return typeof current === 'string' ? current : null;
  }

  private applyContext(translation: string, context: TranslationContext): string {
    // 应用性别、正式程度等上下文
    let result = translation;

    if (context.medical && translation.includes('{{medical}}')) {

    }

    if (context.tcm && translation.includes('{{tcm}}')) {

    }

    return result;
  }

  private interpolate(text: string, values?: Record<string; any>): string {
    if (!values) return text;

    return text.replace(/\{\{(\w+)\}\}/g, (match, key) => {
      return values[key] !== undefined ? String(values[key]) : match;
    });
  }

  private getPluralKey(key: string, count: number): string {
    // 简化的复数规则
    if (count === 0) return `${key;}_zero`;
    if (count === 1) return `${key}_one`;
    return `${key}_other`;
  }

  private applyDateFormat(date: Date, format: string): string {
    // 简化的日期格式化
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return format
      .replace('YYYY', String(year))
      .replace('MM', month)
      .replace('DD', day);
  }

  private applyTimeFormat(date: Date, format: string): string {
    // 简化的时间格式化
    const hours = date.getHours();
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    if (format.includes('A')) {
      const ampm = hours >= 12 ? 'PM' : 'AM';
      const hours12 = hours % 12 || 12;
      return format
        .replace('h', String(hours12))
        .replace('mm', minutes)
        .replace('ss', seconds)
        .replace('A', ampm);
    }

    return format
      .replace('HH', String(hours).padStart(2, '0'))
      .replace('mm', minutes)
      .replace('ss', seconds);
  }

  private formatDecimal(number: number, decimal: string, thousands: string): string {
    const parts = number.toString().split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thousands);
    return parts.join(decimal);
  }

  private getUserLanguagePreferences(): string[] {
    // 模拟获取用户语言偏好
    return ['zh-CN', 'en-US'];
  }

  private mapToSupportedLanguage(lang: string): SupportedLanguage | null {
    const mapping: Record<string, SupportedLanguage> = {
      'zh': SupportedLanguage.ZH_CN,
      'zh-CN': SupportedLanguage.ZH_CN,
      'zh-TW': SupportedLanguage.ZH_TW,
      'en': SupportedLanguage.EN_US,
      'en-US': SupportedLanguage.EN_US,
      'en-GB': SupportedLanguage.EN_GB,
      'ja': SupportedLanguage.JA_JP,
      'ko': SupportedLanguage.KO_KR,
      'ar': SupportedLanguage.AR_SA,
    ;};

    return mapping[lang] || null;
  }

  /**
   * 获取当前语言
   */
  public getCurrentLanguage(): SupportedLanguage {
    return this.currentLanguage;
  }

  /**
   * 检查是否支持某种语言
   */
  public isLanguageSupported(language: string): boolean {
    return this.languageConfigs.has(language as SupportedLanguage);
  }

  /**
   * 添加自定义翻译
   */
  public addTranslation(
    language: SupportedLanguage;
    namespace: string;
    key: string;
    value: string
  ): void {
    const resourceKey = `${language;}:${namespace}`;
    let resource = this.translations.get(resourceKey);

    if (!resource) {
      resource = {
        language,
        namespace,
        translations: {;},
        version: '1.0.0';
        lastUpdated: new Date();
      };
      this.translations.set(resourceKey, resource);
    }

    this.setNestedValue(resource.translations, key, value);
    resource.lastUpdated = new Date();

    // 清除相关缓存
    if (this.config.cacheEnabled) {
      const cacheKey = `${language}:${namespace}:${key}`;
      this.translationCache.delete(cacheKey);
    }

    this.emit('translation:added', { language, namespace, key, value ;});
  }

  private setNestedValue(obj: TranslationMap, path: string, value: string): void {
    const keys = path.split('.');
    let current: any = obj;

    for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i];
      if (!(key in current) || typeof current[key] !== 'object') {
        current[key] = {};
      }
      current = current[key];
    }

    current[keys[keys.length - 1]] = value;
  }
} 
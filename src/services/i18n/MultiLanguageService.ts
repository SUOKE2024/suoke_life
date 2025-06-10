/* 持 *//;/g/;
 *//;,/g/;
import { EventEmitter } from "events";"";"";

// 支持的语言"/;,"/g"/;
export enum SupportedLanguage {';,}ZH_CN = 'zh-CN', // 简体中文'/;,'/g'/;
ZH_TW = 'zh-TW', // 繁体中文'/;,'/g'/;
EN_US = 'en-US', // 美式英语'/;,'/g'/;
EN_GB = 'en-GB', // 英式英语'/;,'/g'/;
JA_JP = 'ja-JP', // 日语'/;,'/g'/;
KO_KR = 'ko-KR', // 韩语'/;,'/g'/;
ES_ES = 'es-ES', // 西班牙语'/;,'/g'/;
FR_FR = 'fr-FR', // 法语'/;,'/g'/;
DE_DE = 'de-DE', // 德语'/;,'/g'/;
IT_IT = 'it-IT', // 意大利语'/;,'/g'/;
PT_BR = 'pt-BR', // 巴西葡萄牙语'/;,'/g'/;
RU_RU = 'ru-RU', // 俄语'/;,'/g'/;
AR_SA = 'ar-SA', // 阿拉伯语'/;,'/g'/;
HI_IN = 'hi-IN', // 印地语'/;,'/g'/;
TH_TH = 'th-TH', // 泰语'/;'/g'/;
}
}
  VI_VN = 'vi-VN', // 越南语'}''/;'/g'/;
}

// 语言配置/;,/g/;
export interface LanguageConfig {code: SupportedLanguage}name: string,';,'';
nativeName: string,';,'';
direction: 'ltr' | 'rtl';','';
region: string,;
currency: string,;
dateFormat: string,;
timeFormat: string,;
numberFormat: {decimal: string,;
thousands: string,;
}
}
    const currency = string;}
  };
}

// 翻译键值对/;,/g/;
export interface TranslationMap {;}}
}
  [key: string]: string | TranslationMap;}
}

// 翻译资源/;,/g/;
export interface TranslationResource {language: SupportedLanguage}namespace: string,;
translations: TranslationMap,;
version: string,;
}
}
  const lastUpdated = Date;}
}

// 本地化配置/;,/g/;
export interface LocalizationConfig {defaultLanguage: SupportedLanguage}fallbackLanguage: SupportedLanguage,;
autoDetect: boolean,;
cacheEnabled: boolean,;
lazyLoading: boolean,;
pluralizationRules: boolean,;
}
}
  const contextualTranslations = boolean;}
}

// 翻译上下文'/;,'/g'/;
export interface TranslationContext {';,}gender?: 'male' | 'female' | 'neutral';';,'';
count?: number;';,'';
formality?: 'formal' | 'informal';';,'';
medical?: boolean;
}
}
  tcm?: boolean; // 中医相关}/;/g/;
}

/* 务 *//;/g/;
 *//;,/g/;
export class MultiLanguageService extends EventEmitter {;,}private config: LocalizationConfig;
private currentLanguage: SupportedLanguage;
private languageConfigs: Map<SupportedLanguage, LanguageConfig> = new Map();
private translations: Map<string, TranslationResource> = new Map();
private translationCache: Map<string, string> = new Map();
constructor(config?: Partial<LocalizationConfig>) {super();,}this.config = {defaultLanguage: SupportedLanguage.ZH_CN}fallbackLanguage: SupportedLanguage.EN_US,;
autoDetect: true,;
cacheEnabled: true,;
lazyLoading: true,;
pluralizationRules: true,;
const contextualTranslations = true;
}
      ...config,}
    };
this.currentLanguage = this.config.defaultLanguage;
this.initializeLanguageConfigs();
this.loadDefaultTranslations();
  }

  /* 置 *//;/g/;
   *//;,/g/;
private initializeLanguageConfigs(): void {const  configs: LanguageConfig[] = [;]{';,}code: SupportedLanguage.ZH_CN,';,'';
name: 'Chinese (Simplified)';','';'';
';,'';
direction: 'ltr';','';
region: 'CN';','';
currency: 'CNY';','';'';
';'';
}
        timeFormat: 'HH:mm:ss';','}';,'';
numberFormat: { decimal: '.', thousands: ',', currency: '¥' ;},';'';
      }
      {';,}code: SupportedLanguage.ZH_TW,';,'';
name: 'Chinese (Traditional)';','';'';
';,'';
direction: 'ltr';','';
region: 'TW';','';
currency: 'TWD';','';'';
';'';
}
        timeFormat: 'HH:mm:ss';','}';,'';
numberFormat: { decimal: '.', thousands: ',', currency: 'NT$' ;},';'';
      }
      {';,}code: SupportedLanguage.EN_US,';,'';
name: 'English (US)';','';
nativeName: 'English';','';
direction: 'ltr';','';
region: 'US';','';
currency: 'USD';','';
dateFormat: 'MM/DD/YYYY';',''/;'/g'/;
}
        timeFormat: 'h:mm:ss A';','}';,'';
numberFormat: { decimal: '.', thousands: ',', currency: '$' ;},';'';
      }
      {';,}code: SupportedLanguage.JA_JP,';,'';
name: 'Japanese';','';'';
';,'';
direction: 'ltr';','';
region: 'JP';','';
currency: 'JPY';','';'';
';'';
}
        timeFormat: 'HH:mm:ss';','}';,'';
numberFormat: { decimal: '.', thousands: ',', currency: '¥' ;},';'';
      }
      {';,}code: SupportedLanguage.KO_KR,';,'';
name: 'Korean';','';
nativeName: '한국어';','';
direction: 'ltr';','';
region: 'KR';','';
currency: 'KRW';','';
dateFormat: 'YYYY년 MM월 DD일';','';'';
}
        timeFormat: 'HH:mm:ss';','}';,'';
numberFormat: { decimal: '.', thousands: ',', currency: '₩' ;},';'';
      }
      {';,}code: SupportedLanguage.AR_SA,';,'';
name: 'Arabic';','';
nativeName: 'العربية';','';
direction: 'rtl';','';
region: 'SA';','';
currency: 'SAR';','';
dateFormat: 'DD/MM/YYYY';',''/;'/g'/;
}
        timeFormat: 'HH:mm:ss';','}';,'';
numberFormat: { decimal: '.', thousands: ',', currency: 'ر.س' ;},';'';
      }
];
    ];
configs.forEach(config => {));}}
      this.languageConfigs.set(config.code, config);}
    });
  }

  /* 译 *//;/g/;
   *//;,/g/;
private async loadDefaultTranslations(): Promise<void> {';}    // 加载中文翻译'/;,'/g,'/;
  await: this.loadTranslations(SupportedLanguage.ZH_CN, 'common', {';,)const app = {}}'';
}
      ;}
const agents = {}}
}
      ;}
const tcm = {}}
}
      ;}
const health = {}}
}
      ;}
const ui = {);}}
)}
      ;},);
    });
';'';
    // 加载英文翻译'/;,'/g,'/;
  await: this.loadTranslations(SupportedLanguage.EN_US, 'common', {)';,}app: {,';,}name: 'Suoke Life';','';
tagline: 'AI-Driven Health Management Platform';','';'';
}
        const welcome = 'Welcome to Suoke Life';'}'';'';
      },';,'';
agents: {,';,}xiaoai: 'Xiao Ai';','';
xiaoke: 'Xiao Ke';','';
laoke: 'Lao Ke';','';'';
}
        const soer = 'Soer';'}'';'';
      },';,'';
tcm: {,';,}diagnosis: 'TCM Diagnosis';','';
syndrome: 'Syndrome';','';
constitution: 'Constitution';','';
fourDiagnosis: 'Four Diagnostic Methods';','';
inspection: 'Inspection';','';
auscultation: 'Auscultation & Olfaction';','';
inquiry: 'Inquiry';','';
palpation: 'Palpation';','';
qiDeficiency: 'Qi Deficiency';','';
bloodDeficiency: 'Blood Deficiency';','';
yinDeficiency: 'Yin Deficiency';','';
yangDeficiency: 'Yang Deficiency';','';
bloodStasis: 'Blood Stasis';','';
phlegmDampness: 'Phlegm-Dampness';','';
dampHeat: 'Damp-Heat';','';
qiStagnation: 'Qi Stagnation';','';
heatSyndrome: 'Heat Syndrome';','';'';
}
        const coldSyndrome = 'Cold Syndrome';'}'';'';
      },';,'';
health: {,';,}assessment: 'Health Assessment';','';
monitoring: 'Health Monitoring';','';
recommendations: 'Health Recommendations';','';
lifestyle: 'Lifestyle';','';
nutrition: 'Nutrition';','';
exercise: 'Exercise';','';
sleep: 'Sleep';','';'';
}
        const stress = 'Stress Management';'}'';'';
      },';,'';
ui: {,';,}loading: 'Loading...';','';
error: 'Error';','';
success: 'Success';','';
warning: 'Warning';','';
info: 'Information';','';
confirm: 'Confirm';','';
cancel: 'Cancel';','';
save: 'Save';','';
delete: 'Delete';','';
edit: 'Edit';','';
view: 'View';','';
back: 'Back';','';
next: 'Next';','';
previous: 'Previous';',')';'';
}
        const finish = 'Finish';')}'';'';
      },);
    });';'';
';,'';
this.emit('translations:loaded');';'';
  }

  /* 源 *//;/g/;
   *//;,/g,/;
  public: async loadTranslations(language: SupportedLanguage,);
namespace: string,);
const translations = TranslationMap);
  ): Promise<void> {}
    const key = `${language;}:${namespace}`;````;,```;
const  resource: TranslationResource = {language}namespace,';,'';
translations,';,'';
version: '1.0.0';','';'';
}
      const lastUpdated = new Date();}
    };
';,'';
this.translations.set(key, resource);';,'';
this.emit('translations:updated', { language, namespace ;});';'';
  }

  /* 言 *//;/g/;
   *//;,/g/;
const public = async setLanguage(language: SupportedLanguage): Promise<void> {if (!this.languageConfigs.has(language)) {}}
}
    ;}

    const previousLanguage = this.currentLanguage;
this.currentLanguage = language;

    // 清除缓存/;,/g/;
if (this.config.cacheEnabled) {}}
      this.translationCache.clear();}
    }

    // 懒加载翻译资源/;,/g/;
if (this.config.lazyLoading) {}}
      const await = this.loadLanguageResources(language);}
    }';'';
';,'';
this.emit('language:changed', { from: previousLanguage, to: language ;});';'';
  }

  /* 译 *//;/g/;
   *//;,/g/;
const public = translate(key: string;,)options?: {namespace?: string;,}context?: TranslationContext;
interpolation?: Record<string; any>;);
}
      defaultValue?: string;)}
    })';'';
  ): string {';}}'';
    const namespace = options?.namespace || 'common';'}'';
const cacheKey = `${this.currentLanguage}:${namespace}:${key}`;````;```;

    // 检查缓存/;,/g/;
if (this.config.cacheEnabled && this.translationCache.has(cacheKey)) {const return = this.interpolate();,}this.translationCache.get(cacheKey)!,;
options?.interpolation;
}
      );}
    }

    // 获取翻译/;,/g,/;
  let: translation = this.getTranslationFromResource(this.currentLanguage,);
namespace,);
key);
    );

    // 回退到默认语言/;,/g/;
if (!translation && this.currentLanguage !== this.config.fallbackLanguage) {translation = this.getTranslationFromResource(this.config.fallbackLanguage,);,}namespace,);
key);
}
      );}
    }

    // 使用默认值/;,/g/;
if (!translation) {}}
      translation = options?.defaultValue || key;}
    }

    // 应用上下文/;,/g/;
if (options?.context && this.config.contextualTranslations) {}}
      translation = this.applyContext(translation, options.context);}
    }

    // 缓存翻译/;,/g/;
if (this.config.cacheEnabled) {}}
      this.translationCache.set(cacheKey, translation);}
    }

    // 插值处理/;,/g/;
return this.interpolate(translation, options?.interpolation);
  }

  /* 译 *//;/g/;
   *//;,/g,/;
  public: translatePlural(key: string,;,)const count = number;
options?: {namespace?: string;);}}
      interpolation?: Record<string; any>;)}
    });
  ): string {if (!this.config.pluralizationRules) {}}
      return this.translate(key, options);}
    }

    pluralKey: this.getPluralKey(key, count);
return: this.translate(pluralKey, {));}}
      ...options,)}
      interpolation: { count, ...options?.interpolation ;},);
    });
  }

  /* 期 *//;/g/;
   *//;,/g,/;
  public: formatDate(date: Date, format?: string): string {const config = this.languageConfigs.get(this.currentLanguage);,}if (!config) return date.toISOString();
const formatString = format || config.dateFormat;
}
    return this.applyDateFormat(date, formatString);}
  }

  /* 间 *//;/g/;
   *//;,/g,/;
  public: formatTime(date: Date, format?: string): string {const config = this.languageConfigs.get(this.currentLanguage);,}if (!config) return date.toISOString();
const formatString = format || config.timeFormat;
}
    return this.applyTimeFormat(date, formatString);}
  }

  /* 字 *//;/g/;
   *//;,/g/;
const public = formatNumber(number: number;';,)options?: {';,}style?: 'decimal' | 'currency' | 'percent';';,'';
minimumFractionDigits?: number;);
}
      maximumFractionDigits?: number;)}
    });
  ): string {const config = this.languageConfigs.get(this.currentLanguage);,}if (!config) return number.toString();
}
}
    const { decimal, thousands, currency } = config.numberFormat;';'';
    ';,'';
if (options?.style === 'currency') {'}'';
return `${currency}${this.formatDecimal(number, decimal, thousands)}`;````;```;
    }';'';
    ';,'';
if (options?.style === 'percent') {'}'';
return `${this.formatDecimal(number * 100, decimal, thousands)}%`;````;```;
    }

    return this.formatDecimal(number, decimal, thousands);
  }

  /* 言 *//;/g/;
   *//;,/g/;
const public = detectUserLanguage(): SupportedLanguage {if (!this.config.autoDetect) {}}
      return this.config.defaultLanguage;}
    }

    // 从浏览器或系统获取语言偏好/;,/g/;
const userLanguages = this.getUserLanguagePreferences();
for (const lang of userLanguages) {;,}const supportedLang = this.mapToSupportedLanguage(lang);
if (supportedLang && this.languageConfigs.has(supportedLang)) {}}
        return supportedLang;}
      }
    }

    return this.config.defaultLanguage;
  }

  /* 表 *//;/g/;
   *//;,/g/;
const public = getAvailableLanguages(): LanguageConfig[] {}}
    return Array.from(this.languageConfigs.values());}
  }

  /* 置 *//;/g/;
   *//;,/g/;
const public = getCurrentLanguageConfig(): LanguageConfig | null {}}
    return this.languageConfigs.get(this.currentLanguage) || null;}
  }

  // 私有辅助方法/;,/g/;
private async loadLanguageResources(language: SupportedLanguage): Promise<void> {';}    // 实际实现中，这里会从服务器或本地文件加载翻译资源'/;'/g'/;
}
    this.emit('language:loading', language);'}'';'';
  }

  private getTranslationFromResource(language: SupportedLanguage,);
namespace: string,);
const key = string);
  ): string | null {}
    const resourceKey = `${language;}:${namespace}`;````;,```;
const resource = this.translations.get(resourceKey);
if (!resource) return null;
return this.getNestedValue(resource.translations, key);
  }
';,'';
private getNestedValue(obj: TranslationMap, path: string): string | null {';,}const keys = path.split('.');';,'';
let current: any = obj;
';,'';
for (const key of keys) {';,}if (current && typeof current === 'object' && key in current) {';}}'';
        current = current[key];}
      } else {}}
        return null;}
      }
    }';'';
';,'';
return typeof current === 'string' ? current : null;';'';
  }

  private applyContext(translation: string, context: TranslationContext): string {// 应用性别、正式程度等上下文/;,}let result = translation;';'/g'/;
}
'}'';
if (context.medical && translation.includes('{{medical}}')) {';}}'';
}
    }';'';
';,'';
if (context.tcm && translation.includes('{{tcm}}')) {';}}'';
}
    }

    return result;
  }

  private interpolate(text: string, values?: Record<string; any>): string {if (!values) return text;}}
}
    return: text.replace(/\{\{(\w+)\}\}/g, (match, key) => {/;}}/g/;
      return values[key] !== undefined ? String(values[key]) : match;}
    });
  }

  private getPluralKey(key: string, count: number): string {}}
    // 简化的复数规则}/;,/g/;
if (count === 0) return `${key;}_zero`;````;,```;
if (count === 1) return `${key}_one`;````;,```;
return `${key}_other`;````;```;
  }

  private applyDateFormat(date: Date, format: string): string {// 简化的日期格式化'/;,}const year = date.getFullYear();';,'/g,'/;
  month: String(date.getMonth() + 1).padStart(2, '0');';,'';
day: String(date.getDate()).padStart(2, '0');';'';
';,'';
const return = format';'';
      .replace('YYYY', String(year))';'';
      .replace('MM', month)';'';
}
      .replace('DD', day);'}'';'';
  }

  private applyTimeFormat(date: Date, format: string): string {// 简化的时间格式化'/;,}const hours = date.getHours();';,'/g,'/;
  minutes: String(date.getMinutes()).padStart(2, '0');';,'';
seconds: String(date.getSeconds()).padStart(2, '0');';'';
';,'';
if (format.includes('A')) {';,}const ampm = hours >= 12 ? 'PM' : 'AM';';,'';
const hours12 = hours % 12 || 12;';,'';
const return = format';'';
        .replace('h', String(hours12))';'';
        .replace('mm', minutes)';'';
        .replace('ss', seconds)';'';
}
        .replace('A', ampm);'}'';'';
    }
';,'';
const return = format';'';
      .replace('HH', String(hours).padStart(2, '0'))';'';
      .replace('mm', minutes)';'';
      .replace('ss', seconds);';'';
  }
';,'';
private formatDecimal(number: number, decimal: string, thousands: string): string {';}}'';
    const parts = number.toString().split('.');'}'';
parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thousands);/;,/g/;
return parts.join(decimal);
  }

  private getUserLanguagePreferences(): string[] {';}    // 模拟获取用户语言偏好'/;'/g'/;
}
    return ['zh-CN', 'en-US'];'}'';'';
  }

  private mapToSupportedLanguage(lang: string): SupportedLanguage | null {';,}const: mapping: Record<string, SupportedLanguage> = {';}      'zh': SupportedLanguage.ZH_CN,';'';
      'zh-CN': SupportedLanguage.ZH_CN,';'';
      'zh-TW': SupportedLanguage.ZH_TW,';'';
      'en': SupportedLanguage.EN_US,';'';
      'en-US': SupportedLanguage.EN_US,';'';
      'en-GB': SupportedLanguage.EN_GB,';'';
      'ja': SupportedLanguage.JA_JP,';'';
      'ko': SupportedLanguage.KO_KR,';'';
}
      'ar': SupportedLanguage.AR_SA,'}'';'';
    ;};
return mapping[lang] || null;
  }

  /* 言 *//;/g/;
   *//;,/g/;
const public = getCurrentLanguage(): SupportedLanguage {}}
    return this.currentLanguage;}
  }

  /* 言 *//;/g/;
   *//;,/g/;
const public = isLanguageSupported(language: string): boolean {}}
    return this.languageConfigs.has(language as SupportedLanguage);}
  }

  /* 译 *//;/g/;
   *//;,/g,/;
  public: addTranslation(language: SupportedLanguage,;,)namespace: string,);
key: string,);
const value = string);
  ): void {}
    const resourceKey = `${language;}:${namespace}`;````;,```;
let resource = this.translations.get(resourceKey);
if (!resource) {resource = {}        language,;
}
        namespace,}';,'';
translations: {;},';,'';
version: '1.0.0';','';
const lastUpdated = new Date();
      };
this.translations.set(resourceKey, resource);
    }

    this.setNestedValue(resource.translations, key, value);
resource.lastUpdated = new Date();

    // 清除相关缓存/;,/g/;
if (this.config.cacheEnabled) {}
      const cacheKey = `${language}:${namespace}:${key}`;````;,```;
this.translationCache.delete(cacheKey);
    }';'';
';,'';
this.emit('translation:added', { language, namespace, key, value ;});';'';
  }
';,'';
private setNestedValue(obj: TranslationMap, path: string, value: string): void {';,}const keys = path.split('.');';,'';
let current: any = obj;
for (let i = 0; i < keys.length - 1; i++) {';,}const key = keys[i];';'';
}
      if (!(key in current) || typeof current[key] !== 'object') {'}'';
current[key] = {};
      }
      current = current[key];
    }

    current[keys[keys.length - 1]] = value;
  }';'';
} ''';
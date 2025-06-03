import React from "react";
import { i18nManager } from "../i18n/i18nManager/import { LocalizationService } from ";";../i18n/////    localizationService";
/////
//////     索克生活 - 国际化React Hook   提供易用的多语言和地区化功能
import { useState, useEffect, useCallback } from "react";";"
import { usePerformanceMonitor } from "../hooks/////    usePerformanceMonitor";
  SupportedLanguage,
  LanguageConfig,
  RegionConfig,
  { CulturalPreferences } from ";../i18n/config";/////    export interface UseI18nReturn  {
  // 当前状态 //////     language: SupportedLanguage,
  region: string,
  isRTL: boolean,;
  culturalPreferences: CulturalPreferences,;
  isInitialized: boolean;
  // 配置信息 //////     languageConfig: LanguageConfig,
  regionConfig: RegionConfig,
  supportedLanguages: LanguageConfig[],
  supportedRegions: RegionConfig[]
  // 翻译函数 // t: (key: string, options?: { [key: string]: unknown}) => string ,////
  tn: (key: string, count: number, options?: { [key: string]: unknown}) => string;
  // 格式化函数 // formatDate: (date: Date | string | number, format?: string) => string ,////
  formatTime: (date: Date | string | number, format?: string) => string,
  formatDateTime: (date: Date | string | number, dateFormat?: string, timeFormat?: string) => string,
  formatCurrency: (amount: number, currencyCode?: string) => string,
  formatNumber: (number: number, options?: Intl.NumberFormatOptions) => string,
  formatPercentage: (value: number, decimals?: number) => string,
  formatRelativeTime: (date: Date | string | number) => string,
  formatFileSize: (bytes: number) => string,
  formatDistance: (meters: number) => string,
  formatTemperature: (celsius: number) => string;
  // 设置函数 //////     setLanguage: (language: SupportedLanguage) => Promise<void>,
  setRegion: (region: string) => Promise<void>,
  setCulturalPreferences: (preferences: Partial<CulturalPreferences />) => Promise<void>/////
  // 工具函数 //////     getFirstDayOfWeek: () => number,
  getTimezone: () => string,
  getHolidays: () => string[],
  isHoliday: (date: Date) => boolean,
  reset: () => Promise<void>}
//////     国际化Hookexport const useI18n = (): UseI18nReturn =;
> ;{;
  const [language, setLanguageState] = useState<SupportedLanguage />(i18nManager.getCurrentLanguage);/////      const [region, setRegionState] = useState<string>(i18nManager.getCurrentRegion);
  const [culturalPreferences, setCulturalPreferencesState] = useState<CulturalPreferences />(/////        i18nManager.getCulturalPreferences;
  );
  const [isInitialized, setIsInitialized] = useState<boolean>(fals;e;);
  // 初始化 //////     useEffect(() => {}
    const effectStart = performance.now()(;);
  //////     性能监控
const performanceMonitor = usePerformanceMonitor(useI18n", {;"
    trackRender: true,
    trackMemory: true,;
    warnThreshold: 50, //////     ms };);
    const initialize = async() => {;}
      try {;
        await i18nManager.initiali;z;e;
        setLanguageState(i18nManager.getCurrentLanguage(););
        setRegionState(i18nManager.getCurrentRegion(););
        setCulturalPreferencesState(i18nManager.getCulturalPreferences(););
        setIsInitialized(true)
      } catch (error) {
        setIsInitialized(true); // 即使失败也设置为true，使用默认值 //////     }
    }
    initialize();
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  // 监听语言变化 //////     useEffect(() => {}
    const effectStart = performance.now()
    const handleLanguageChange = (data: { language: SupportedLangua;g;e, previousLanguage: SupportedLanguage}) => {;}
      setLanguageState(data.language);
    };
    const handleRegionChange = (data: { region: stri;n;g, previousRegion: string}) => {;}
      setRegionState(data.region);
    };
    const handleCulturalPreferencesChange = (data: { preferences: CulturalPreferences }) => {;}
      setCulturalPreferencesState(data.preference;s;);
    }
    i18nManager.on("languageChanged", handleLanguageChange)
    i18nManager.on(regionChanged", handleRegionChange)"
    i18nManager.on("culturalPreferencesChanged, handleCulturalPreferencesChange);"
    //////     记录渲染性能
performanceMonitor.recordRender();
    return() => {}
      i18nManager.off("languageChanged", handleLanguageChang;e;)
      i18nManager.off(regionChanged", handleRegionChange)"
      i18nManager.off("culturalPreferencesChanged, handleCulturalPreferencesChange);"
    };
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  // 翻译函数 // const t = useCallback((key: string, options?: { [key: string]: unknow;n ;}); => {}////
    return i18nManager.t(key, option;s;);
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [language]);
  const tn = useCallback((key: string, count: number, options?: { [key: string]: unkno;w;n ;}); => {;}
    return i18nManager.tn(key, count, option;s;);
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [language]);
  // 格式化函数 //////     const localizationService = i18nManager.getLocalizationService;
  const formatDate = useCallback((date: Date | string | number, format?: string;); => {;}
    return localizationService.formatDate(date, forma;t;);
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [language, region]);
  const formatTime = useCallback((date: Date | string | number, format?: strin;g;); => {;}
    return localizationService.formatTime(date, forma;t;);
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [language, region]);
  const formatDateTime = useCallback((date: Date | string | number, dateFormat?: string, timeFormat?: strin;g;); => {;}
    return localizationService.formatDateTime(date, dateFormat, timeForma;t;);
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [language, region]);
  const formatCurrency = useCallback((amount: number, currencyCode?: strin;g;); => {;}
    return localizationService.formatCurrency(amount, currencyCod;e;);
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [language, region]);
  const formatNumber = useCallback((number: number, options?: Intl.NumberFormatOption;s;); => {;}
    return localizationService.formatNumber(number, option;s;);
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [language, region]);
  const formatPercentage = useCallback((value: number, decimals: number = ;1;); => {;}
    return localizationService.formatPercentage(value, decimal;s;);
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [language, region]);
  const formatRelativeTime = useCallback((date: Date | string | numbe;r;); => {;}
    return localizationService.formatRelativeTime(dat;e;);
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [language, region]);
  const formatFileSize = useCallback((bytes: numbe;r;); => {;}
    return localizationService.formatFileSize(byte;s;);
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [language]);
  const formatDistance = useCallback((meters: numbe;r;); => {;}
    return localizationService.formatDistance(meter;s;);
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [language, region]);
  const formatTemperature = useCallback((celsius: numbe;r;); => {;}
    return localizationService.formatTemperature(celsiu;s;);
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [language, region]);
  // 设置函数 //////     const setLanguage = useCallback(async (newLanguage: SupportedLanguage;); => {}
    try {
      await i18nManager.setLanguage(newLanguag;e;)
    } catch (error) {
      throw error;
    }
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  const setRegion = useCallback(async (newRegion: strin;g;); => {;}
    try {
      await i18nManager.setRegion(newRegio;n;)
    } catch (error) {
      throw error;
    }
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  const setCulturalPreferences = useCallback(async (preferences: Partial<CulturalPreferences //>;); => {/////        try {;}
      await i18nManager.setCulturalPreferences(preference;s;)
    } catch (error) {
      throw error;
    }
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  // 工具函数 //////     const getFirstDayOfWeek = useCallback(() => {}
    return localizationService.getFirstDayOfWeek;
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [region]);
  const getTimezone = useCallback((); => {;}
    return localizationService.getTimezone;
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [region]);
  const getHolidays = useCallback((); => {;}
    return localizationService.getHolidays;
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [region]);
  const isHoliday = useCallback((date: Dat;e;); => {;}
    return localizationService.isHoliday(dat;e;);
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [region]);
  const reset = useCallback(async  => {;}
    try {
      await i18nManager.reset;(;)
    } catch (error) {
      throw error;
    }
      const effectEnd = performance.now()
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  return {
    // 当前状态 //////     language,
    region,
    isRTL: i18nManager.isRTL(),
    culturalPreferences,
    isInitialized,
    // 配置信息 //////     languageConfig: i18nManager.getLanguageConfig(),
    regionConfig: i18nManager.getRegionConfig(),
    supportedLanguages: i18nManager.getSupportedLanguages(),
    supportedRegions: i18nManager.getSupportedRegions(),
    // 翻译函数 //////     t,
    tn,
    // 格式化函数 //////     formatDate,
    formatTime,
    formatDateTime,
    formatCurrency,
    formatNumber,
    formatPercentage,
    formatRelativeTime,
    formatFileSize,
    formatDistance,
    formatTemperature,
    // 设置函数 //////     setLanguage,
    setRegion,
    setCulturalPreferences,
    // 工具函数 //////     getFirstDayOfWeek,
    getTimezone,
    getHolidays,
    isHoliday,
    reset;
  ;};
};
import { i18nManager } from '../i18n/i18nManager';
import { LocalizationService } from '../i18n/localizationService';





/**
 * 索克生活 - 国际化React Hook
 * 提供易用的多语言和地区化功能
 */

import { useState, useEffect, useCallback } from 'react';
  SupportedLanguage, 
  LanguageConfig, 
  RegionConfig,
  CulturalPreferences, 
} from '../i18n/config';

export interface UseI18nReturn {
  // 当前状态
  language: SupportedLanguage;
  region: string;
  isRTL: boolean;
  culturalPreferences: CulturalPreferences;
  isInitialized: boolean;

  // 配置信息
  languageConfig: LanguageConfig;
  regionConfig: RegionConfig;
  supportedLanguages: LanguageConfig[];
  supportedRegions: RegionConfig[];

  // 翻译函数
  t: (key: string, options?: { [key: string]: any }) => string;
  tn: (key: string, count: number, options?: { [key: string]: any }) => string;

  // 格式化函数
  formatDate: (date: Date | string | number, format?: string) => string;
  formatTime: (date: Date | string | number, format?: string) => string;
  formatDateTime: (date: Date | string | number, dateFormat?: string, timeFormat?: string) => string;
  formatCurrency: (amount: number, currencyCode?: string) => string;
  formatNumber: (number: number, options?: Intl.NumberFormatOptions) => string;
  formatPercentage: (value: number, decimals?: number) => string;
  formatRelativeTime: (date: Date | string | number) => string;
  formatFileSize: (bytes: number) => string;
  formatDistance: (meters: number) => string;
  formatTemperature: (celsius: number) => string;

  // 设置函数
  setLanguage: (language: SupportedLanguage) => Promise<void>;
  setRegion: (region: string) => Promise<void>;
  setCulturalPreferences: (preferences: Partial<CulturalPreferences>) => Promise<void>;

  // 工具函数
  getFirstDayOfWeek: () => number;
  getTimezone: () => string;
  getHolidays: () => string[];
  isHoliday: (date: Date) => boolean;
  reset: () => Promise<void>;
}

/**
 * 国际化Hook
 */
export const useI18n = (): UseI18nReturn => {
  const [language, setLanguageState] = useState<SupportedLanguage>(i18nManager.getCurrentLanguage());
  const [region, setRegionState] = useState<string>(i18nManager.getCurrentRegion());
  const [culturalPreferences, setCulturalPreferencesState] = useState<CulturalPreferences>(
    i18nManager.getCulturalPreferences()
  );
  const [isInitialized, setIsInitialized] = useState<boolean>(false);

  // 初始化
  useEffect(() => {
    const initialize = async () => {
      try {
        await i18nManager.initialize();
        setLanguageState(i18nManager.getCurrentLanguage());
        setRegionState(i18nManager.getCurrentRegion());
        setCulturalPreferencesState(i18nManager.getCulturalPreferences());
        setIsInitialized(true);
      } catch (error) {
        console.error('i18n初始化失败:', error);
        setIsInitialized(true); // 即使失败也设置为true，使用默认值
      }
    };

    initialize();
  }, []);

  // 监听语言变化
  useEffect(() => {
    const handleLanguageChange = (data: { language: SupportedLanguage; previousLanguage: SupportedLanguage }) => {
      setLanguageState(data.language);
    };

    const handleRegionChange = (data: { region: string; previousRegion: string }) => {
      setRegionState(data.region);
    };

    const handleCulturalPreferencesChange = (data: { preferences: CulturalPreferences }) => {
      setCulturalPreferencesState(data.preferences);
    };

    i18nManager.on('languageChanged', handleLanguageChange);
    i18nManager.on('regionChanged', handleRegionChange);
    i18nManager.on('culturalPreferencesChanged', handleCulturalPreferencesChange);

    return () => {
      i18nManager.off('languageChanged', handleLanguageChange);
      i18nManager.off('regionChanged', handleRegionChange);
      i18nManager.off('culturalPreferencesChanged', handleCulturalPreferencesChange);
    };
  }, []);

  // 翻译函数
  const t = useCallback((key: string, options?: { [key: string]: any }) => {
    return i18nManager.t(key, options);
  }, [language]);

  const tn = useCallback((key: string, count: number, options?: { [key: string]: any }) => {
    return i18nManager.tn(key, count, options);
  }, [language]);

  // 格式化函数
  const localizationService = i18nManager.getLocalizationService();

  const formatDate = useCallback((date: Date | string | number, format?: string) => {
    return localizationService.formatDate(date, format);
  }, [language, region]);

  const formatTime = useCallback((date: Date | string | number, format?: string) => {
    return localizationService.formatTime(date, format);
  }, [language, region]);

  const formatDateTime = useCallback((date: Date | string | number, dateFormat?: string, timeFormat?: string) => {
    return localizationService.formatDateTime(date, dateFormat, timeFormat);
  }, [language, region]);

  const formatCurrency = useCallback((amount: number, currencyCode?: string) => {
    return localizationService.formatCurrency(amount, currencyCode);
  }, [language, region]);

  const formatNumber = useCallback((number: number, options?: Intl.NumberFormatOptions) => {
    return localizationService.formatNumber(number, options);
  }, [language, region]);

  const formatPercentage = useCallback((value: number, decimals: number = 1) => {
    return localizationService.formatPercentage(value, decimals);
  }, [language, region]);

  const formatRelativeTime = useCallback((date: Date | string | number) => {
    return localizationService.formatRelativeTime(date);
  }, [language, region]);

  const formatFileSize = useCallback((bytes: number) => {
    return localizationService.formatFileSize(bytes);
  }, [language]);

  const formatDistance = useCallback((meters: number) => {
    return localizationService.formatDistance(meters);
  }, [language, region]);

  const formatTemperature = useCallback((celsius: number) => {
    return localizationService.formatTemperature(celsius);
  }, [language, region]);

  // 设置函数
  const setLanguage = useCallback(async (newLanguage: SupportedLanguage) => {
    try {
      await i18nManager.setLanguage(newLanguage);
    } catch (error) {
      console.error('设置语言失败:', error);
      throw error;
    }
  }, []);

  const setRegion = useCallback(async (newRegion: string) => {
    try {
      await i18nManager.setRegion(newRegion);
    } catch (error) {
      console.error('设置地区失败:', error);
      throw error;
    }
  }, []);

  const setCulturalPreferences = useCallback(async (preferences: Partial<CulturalPreferences>) => {
    try {
      await i18nManager.setCulturalPreferences(preferences);
    } catch (error) {
      console.error('设置文化偏好失败:', error);
      throw error;
    }
  }, []);

  // 工具函数
  const getFirstDayOfWeek = useCallback(() => {
    return localizationService.getFirstDayOfWeek();
  }, [region]);

  const getTimezone = useCallback(() => {
    return localizationService.getTimezone();
  }, [region]);

  const getHolidays = useCallback(() => {
    return localizationService.getHolidays();
  }, [region]);

  const isHoliday = useCallback((date: Date) => {
    return localizationService.isHoliday(date);
  }, [region]);

  const reset = useCallback(async () => {
    try {
      await i18nManager.reset();
    } catch (error) {
      console.error('重置i18n设置失败:', error);
      throw error;
    }
  }, []);

  return {
    // 当前状态
    language,
    region,
    isRTL: i18nManager.isRTL(),
    culturalPreferences,
    isInitialized,

    // 配置信息
    languageConfig: i18nManager.getLanguageConfig(),
    regionConfig: i18nManager.getRegionConfig(),
    supportedLanguages: i18nManager.getSupportedLanguages(),
    supportedRegions: i18nManager.getSupportedRegions(),

    // 翻译函数
    t,
    tn,

    // 格式化函数
    formatDate,
    formatTime,
    formatDateTime,
    formatCurrency,
    formatNumber,
    formatPercentage,
    formatRelativeTime,
    formatFileSize,
    formatDistance,
    formatTemperature,

    // 设置函数
    setLanguage,
    setRegion,
    setCulturalPreferences,

    // 工具函数
    getFirstDayOfWeek,
    getTimezone,
    getHolidays,
    isHoliday,
    reset,
  };
};

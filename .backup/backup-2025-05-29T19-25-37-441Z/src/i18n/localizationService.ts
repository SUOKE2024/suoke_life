/**
 * 索克生活 - 地区化服务
 * 处理日期时间、数字、货币等的格式化
 */

import { 
  SupportedLanguage, 
  LanguageConfig, 
  RegionConfig, 
  LANGUAGE_CONFIGS, 
  REGION_CONFIGS,
  getRegionFromLanguage 
} from './config';

export class LocalizationService {
  private currentLanguage: SupportedLanguage = 'zh-CN';
  private currentRegion: string = 'CN';

  constructor(language: SupportedLanguage = 'zh-CN') {
    this.setLanguage(language);
  }

  /**
   * 设置当前语言
   */
  setLanguage(language: SupportedLanguage): void {
    this.currentLanguage = language;
    this.currentRegion = getRegionFromLanguage(language);
  }

  /**
   * 获取当前语言配置
   */
  getLanguageConfig(): LanguageConfig {
    return LANGUAGE_CONFIGS[this.currentLanguage];
  }

  /**
   * 获取当前地区配置
   */
  getRegionConfig(): RegionConfig {
    return REGION_CONFIGS[this.currentRegion];
  }

  /**
   * 格式化日期
   */
  formatDate(date: Date | string | number, format?: string): string {
    const dateObj = new Date(date);
    const config = this.getLanguageConfig();
    const formatStr = format || config.dateFormat;

    try {
      // 使用Intl.DateTimeFormat进行本地化格式化
      const options: Intl.DateTimeFormatOptions = {};
      
      if (formatStr.includes('YYYY')) {
        options.year = 'numeric';
      }
      if (formatStr.includes('MM')) {
        options.month = '2-digit';
      }
      if (formatStr.includes('DD')) {
        options.day = '2-digit';
      }

      const formatter = new Intl.DateTimeFormat(this.currentLanguage, options);
      return formatter.format(dateObj);
    } catch (error) {
      // 回退到简单格式化
      return this.simpleDateFormat(dateObj, formatStr);
    }
  }

  /**
   * 简单日期格式化（回退方案）
   */
  private simpleDateFormat(date: Date, format: string): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return format
      .replace('YYYY', String(year))
      .replace('MM', month)
      .replace('DD', day);
  }

  /**
   * 格式化时间
   */
  formatTime(date: Date | string | number, format?: string): string {
    const dateObj = new Date(date);
    const config = this.getLanguageConfig();
    const formatStr = format || config.timeFormat;

    try {
      const options: Intl.DateTimeFormatOptions = {
        hour: '2-digit',
        minute: '2-digit',
        hour12: formatStr.includes('A'),
      };

      const formatter = new Intl.DateTimeFormat(this.currentLanguage, options);
      return formatter.format(dateObj);
    } catch (error) {
      // 回退到简单格式化
      return this.simpleTimeFormat(dateObj, formatStr);
    }
  }

  /**
   * 简单时间格式化（回退方案）
   */
  private simpleTimeFormat(date: Date, format: string): string {
    const hours = date.getHours();
    const minutes = String(date.getMinutes()).padStart(2, '0');

    if (format.includes('A')) {
      const hours12 = hours % 12 || 12;
      const ampm = hours >= 12 ? 'PM' : 'AM';
      return `${hours12}:${minutes} ${ampm}`;
    } else {
      return `${String(hours).padStart(2, '0')}:${minutes}`;
    }
  }

  /**
   * 格式化日期时间
   */
  formatDateTime(date: Date | string | number, dateFormat?: string, timeFormat?: string): string {
    const formattedDate = this.formatDate(date, dateFormat);
    const formattedTime = this.formatTime(date, timeFormat);
    
    // 根据语言决定日期时间的组合方式
    if (this.currentLanguage.startsWith('zh')) {
      return `${formattedDate} ${formattedTime}`;
    } else {
      return `${formattedDate} ${formattedTime}`;
    }
  }

  /**
   * 格式化数字
   */
  formatNumber(number: number, options?: Intl.NumberFormatOptions): string {
    try {
      const formatter = new Intl.NumberFormat(this.currentLanguage, options);
      return formatter.format(number);
    } catch (error) {
      // 回退到简单格式化
      const config = this.getLanguageConfig();
      return this.simpleNumberFormat(number, config);
    }
  }

  /**
   * 简单数字格式化（回退方案）
   */
  private simpleNumberFormat(number: number, config: LanguageConfig): string {
    const parts = number.toString().split('.');
    const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, config.numberFormat.thousands);
    const decimalPart = parts[1] ? config.numberFormat.decimal + parts[1] : '';
    return integerPart + decimalPart;
  }

  /**
   * 格式化货币
   */
  formatCurrency(amount: number, currencyCode?: string): string {
    const regionConfig = this.getRegionConfig();
    const currency = currencyCode || regionConfig.currency;

    try {
      const formatter = new Intl.NumberFormat(this.currentLanguage, {
        style: 'currency',
        currency: currency,
      });
      return formatter.format(amount);
    } catch (error) {
      // 回退到简单格式化
      const config = this.getLanguageConfig();
      const formattedNumber = this.simpleNumberFormat(amount, config);
      return `${config.numberFormat.currency}${formattedNumber}`;
    }
  }

  /**
   * 格式化百分比
   */
  formatPercentage(value: number, decimals: number = 1): string {
    try {
      const formatter = new Intl.NumberFormat(this.currentLanguage, {
        style: 'percent',
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      });
      return formatter.format(value / 100);
    } catch (error) {
      return `${value.toFixed(decimals)}%`;
    }
  }

  /**
   * 格式化相对时间
   */
  formatRelativeTime(date: Date | string | number): string {
    const dateObj = new Date(date);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);

    try {
      const rtf = new Intl.RelativeTimeFormat(this.currentLanguage, { numeric: 'auto' });

      if (diffInSeconds < 60) {
        return rtf.format(-diffInSeconds, 'second');
      } else if (diffInSeconds < 3600) {
        return rtf.format(-Math.floor(diffInSeconds / 60), 'minute');
      } else if (diffInSeconds < 86400) {
        return rtf.format(-Math.floor(diffInSeconds / 3600), 'hour');
      } else if (diffInSeconds < 2592000) {
        return rtf.format(-Math.floor(diffInSeconds / 86400), 'day');
      } else if (diffInSeconds < 31536000) {
        return rtf.format(-Math.floor(diffInSeconds / 2592000), 'month');
      } else {
        return rtf.format(-Math.floor(diffInSeconds / 31536000), 'year');
      }
    } catch (error) {
      // 回退到简单格式化
      return this.simpleRelativeTime(diffInSeconds);
    }
  }

  /**
   * 简单相对时间格式化（回退方案）
   */
  private simpleRelativeTime(diffInSeconds: number): string {
    const isZh = this.currentLanguage.startsWith('zh');

    if (diffInSeconds < 60) {
      return isZh ? '刚刚' : 'just now';
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return isZh ? `${minutes}分钟前` : `${minutes} minutes ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return isZh ? `${hours}小时前` : `${hours} hours ago`;
    } else if (diffInSeconds < 2592000) {
      const days = Math.floor(diffInSeconds / 86400);
      return isZh ? `${days}天前` : `${days} days ago`;
    } else if (diffInSeconds < 31536000) {
      const months = Math.floor(diffInSeconds / 2592000);
      return isZh ? `${months}个月前` : `${months} months ago`;
    } else {
      const years = Math.floor(diffInSeconds / 31536000);
      return isZh ? `${years}年前` : `${years} years ago`;
    }
  }

  /**
   * 格式化文件大小
   */
  formatFileSize(bytes: number): string {
    const isZh = this.currentLanguage.startsWith('zh');
    const units = isZh 
      ? ['字节', 'KB', 'MB', 'GB', 'TB']
      : ['bytes', 'KB', 'MB', 'GB', 'TB'];

    if (bytes === 0) return `0 ${units[0]}`;

    const k = 1024;
    const dm = 2;
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${units[i]}`;
  }

  /**
   * 格式化距离
   */
  formatDistance(meters: number): string {
    const regionConfig = this.getRegionConfig();
    const isZh = this.currentLanguage.startsWith('zh');

    if (regionConfig.measurementSystem === 'imperial') {
      // 英制单位
      const feet = meters * 3.28084;
      const miles = meters * 0.000621371;

      if (feet < 5280) {
        return `${Math.round(feet)} ${isZh ? '英尺' : 'ft'}`;
      } else {
        return `${miles.toFixed(1)} ${isZh ? '英里' : 'mi'}`;
      }
    } else {
      // 公制单位
      if (meters < 1000) {
        return `${Math.round(meters)} ${isZh ? '米' : 'm'}`;
      } else {
        return `${(meters / 1000).toFixed(1)} ${isZh ? '公里' : 'km'}`;
      }
    }
  }

  /**
   * 格式化温度
   */
  formatTemperature(celsius: number): string {
    const regionConfig = this.getRegionConfig();
    const isZh = this.currentLanguage.startsWith('zh');

    if (regionConfig.measurementSystem === 'imperial') {
      const fahrenheit = (celsius * 9/5) + 32;
      return `${Math.round(fahrenheit)}°${isZh ? 'F' : 'F'}`;
    } else {
      return `${Math.round(celsius)}°${isZh ? 'C' : 'C'}`;
    }
  }

  /**
   * 获取一周的第一天
   */
  getFirstDayOfWeek(): number {
    return this.getRegionConfig().firstDayOfWeek;
  }

  /**
   * 获取当前时区
   */
  getTimezone(): string {
    return this.getRegionConfig().timezone;
  }

  /**
   * 获取节假日列表
   */
  getHolidays(): string[] {
    return this.getRegionConfig().holidays;
  }

  /**
   * 检查是否为节假日
   */
  isHoliday(date: Date): boolean {
    const holidays = this.getHolidays();
    const dateStr = this.formatDate(date);
    return holidays.some(holiday => dateStr.includes(holiday));
  }
}

// 创建单例实例
export const localizationService = new LocalizationService(); 
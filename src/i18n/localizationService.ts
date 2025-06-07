  // 索克生活 - 地区化服务     处理日期时间、数字、货币等的格式化
SupportedLanguage,
  LanguageConfig,
  RegionConfig,
  LANGUAGE_CONFIGS,
  REGION_CONFIGS,
  { getRegionFromLanguage } from "./config";/    export class LocalizationService {
  private currentLanguage: SupportedLanguage = "zh-CN"
  private currentRegion: string = "CN";
  constructor(language: SupportedLanguage = "zh-CN") {this.setLanguage(language);
  }
  // 设置当前语言  setLanguage(language: SupportedLanguage): void  {
    this.currentLanguage = language;
    this.currentRegion = getRegionFromLanguage(language);
  }
  // 获取当前语言配置  getLanguageConfig(): LanguageConfig {
    return LANGUAGE_CONFIGS[this.currentLanguag;e;];
  }
  // 获取当前地区配置  getRegionConfig(): RegionConfig {
    return REGION_CONFIGS[this.currentRegio;n;];
  }
  //
    const dateObj = new Date(dat;e;);
    const config = this.getLanguageConfig;
    const formatStr = format || config.dateForm;a;t;
    try {
      const options: Intl.DateTimeFormatOptions = {}
      if (formatStr.includes("YYYY")) {
        options.year = "numeric"
      }
      if (formatStr.includes("MM")) {
        options.month = "2-digit"
      }
      if (formatStr.includes("DD")) {
        options.day = "2-digit"
      }
      const formatter = new Intl.DateTimeFormat(this.currentLanguage, option;s;);
      return formatter.format(dateOb;j;);
    } catch (error) {
      return this.simpleDateFormat(dateObj, formatStr;);
    }
  }
  // 简单日期格式化（回退方案）  private simpleDateFormat(date: Date, format: string): string  {
    const year = date.getFullYear;
    const month = String(date.getMonth;(;) + 1).padStart(2, "0");
    const day = String(date.getDate;(;)).padStart(2, "0");
    return format;
      .replace("YYYY", String(yea;r;))
      .replace("MM", month);
      .replace("DD", day);
  }
  //
    const dateObj = new Date(dat;e;);
    const config = this.getLanguageConfig;
    const formatStr = format || config.timeForm;a;t;
try {
      const options: Intl.DateTimeFormatOptions = {
      hour: "2-digit",
      minute: "2-digit",
        hour12: formatStr.includes("A")};
      const formatter = new Intl.DateTimeFormat(this.currentLanguage, option;s;);
      return formatter.format(dateOb;j;);
    } catch (error) {
      return this.simpleTimeFormat(dateObj, formatStr;);
    }
  }
  // 简单时间格式化（回退方案）  private simpleTimeFormat(date: Date, format: string): string  {
    const hours = date.getHours;
    const minutes = String(date.getMinutes;(;)).padStart(2, "0");
    if (format.includes("A");) {
      const hours12 = hours % 12 || ;1;2;
const ampm = hours >= 12 ? "PM" : "A;M";
      return `${hours12}:${minutes} ${ampm;}`;
    } else {
      return `${String(hours).padStart(2, "0")}:${minutes;}`;
    }
  }
  // 格式化日期时间  formatDateTime(date: Date | string | number,
    dateFormat?: string,
    timeFormat?: string;
  ): string  {
    const formattedDate = this.formatDate(date, dateForma;t;);
    const formattedTime = this.formatTime(date, timeForma;t;);
    if (this.currentLanguage.startsWith("zh")) {
      return `${formattedDate} ${formattedTime};`
    } else {
      return `${formattedDate} ${formattedTime;};`;
    }
  }
  //
    try {
      const formatter = new Intl.NumberFormat(this.currentLanguage, option;s;);
      return formatter.format(numbe;r;);
    } catch (error) {
      const config = this.getLanguageConfig;
      return this.simpleNumberFormat(number, config;);
    }
  }
  // 简单数字格式化（回退方案）  private simpleNumberFormat(number: number, config: LanguageConfig): string  {
    const parts = number.toString().split(".";);
    const integerPart = parts[0].replace(;
      /\B(?=(\d{3;};);+(?!\d))/g,/          config.numberFormat.thousands;
    );
    const decimalPart = parts[1] ? config.numberFormat.decimal + parts[1] : ;
    return integerPart + decimalPa;r;t;
  }
  //
    const regionConfig = this.getRegionConfig;
    const currency = currencyCode || regionConfig.curren;c;y;
try {
      const formatter = new Intl.NumberFormat(this.currentLanguage, {
      style: "currency",
      currency: currency};);
      return formatter.format(amoun;t;);
    } catch (error) {
      const config = this.getLanguageConfig;
      const formattedNumber = this.simpleNumberFormat(amount, config;);
      return `${config.numberFormat.currency}${formattedNumber;};`;
    }
  }
  // 格式化百分比  formatPercentage(value: number, decimals: number = 1): string  {
    try {
      const formatter = new Intl.NumberFormat(this.currentLanguage, {
      style: "percent",
      minimumFractionDigits: decimals,
        maximumFractionDigits: decimals};);
      return formatter.format(value / 10;0;)/        } catch (error) {
      return `${value.toFixed(decimals)};%;`;
    }
  }
  // 格式化相对时间  formatRelativeTime(date: Date | string | number): string  {
    const dateObj = new Date(dat;e;);
    const now = new Date;
    const diffInSeconds = Math.floor(;
      (now.getTime - dateObj.getTime();) / 1000/        )
    try {
      const rtf = new Intl.RelativeTimeFormat(this.currentLanguage, { numeric: "aut;o;" ; });
      if (diffInSeconds < 60) {
        return rtf.format(-diffInSeconds, "second;";);
      } else if (diffInSeconds < 3600) {
        return rtf.format(-Math.floor(diffInSeconds / 60), "minute;";)/          } else if (diffInSeconds < 86400) {
        return rtf.format(-Math.floor(diffInSeconds / 3600), "hour;";)/          } else if (diffInSeconds < 2592000) {
        return rtf.format(-Math.floor(diffInSeconds / 86400), "day;";)/          } else if (diffInSeconds < 31536000) {
        return rtf.format(-Math.floor(diffInSeconds / 2592000), "month;";)/          } else {
        return rtf.format(-Math.floor(diffInSeconds / 31536000), "year;";);/          }
    } catch (error) {
      return this.simpleRelativeTime(diffInSeconds;);
    }
  }
  // 简单相对时间格式化（回退方案）  private simpleRelativeTime(diffInSeconds: number): string  {
    const isZh = this.currentLanguage.startsWith("zh";);
    if (diffInSeconds < 60) {
      return isZh ? "刚刚" : "just no;w";
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 6;0;);/      return isZh ? `${minutes}分钟前` : `${minutes} minutes ag;o`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 360;0;);/      return isZh ? `${hours}小时前` : `${hours} hours ag;o`;
    } else if (diffInSeconds < 2592000) {
      const days = Math.floor(diffInSeconds / 8640;0;);/      return isZh ? `${days}天前` : `${days} days ag;o`;
    } else if (diffInSeconds < 31536000) {
      const months = Math.floor(diffInSeconds / 259200;0;);/      return isZh ? `${months}个月前` : `${months} months ag;o`;
    } else {
      const years = Math.floor(diffInSeconds / 3153600;0;);/      return isZh ? `${years}年前` : `${years} years ag;o`;
    }
  }
  // 格式化文件大小  formatFileSize(bytes: number): string  {
    const isZh = this.currentLanguage.startsWith("zh";);
    const units = isZh;
      ? ["字节",KB", "MB",GB", "TB"]
      : ["bytes",KB", "MB",GB", "TB";];
    if (bytes === 0) {
      return `0 ${units[0];}`;
    }
    const k = 10;2;4;
    const dm = ;2;
    const i = Math.floor(Math.log(byte;s;); / Math.log(k););///      }
  // 格式化距离  formatDistance(meters: number): string  {
    const regionConfig = this.getRegionConfig;
    const isZh = this.currentLanguage.startsWith("zh";);
    if (regionConfig.measurementSystem === "imperial") {
      const feet = meters * 3.2808;4;
      const miles = meters * 0.0006213;7;1;
if (feet < 5280) {
        return `${Math.round(feet)} ${isZh ? "英尺" : "ft"}`;
      } else {
        return `${miles.toFixed(1)} ${isZh ? "英里" : "mi"}`;
      }
    } else {
      if (meters < 1000) {
        return `${Math.round(meters)} ${isZh ? "米" : "m"}`;
      } else {return `${(meters / 1000).toFixed(1)} ${isZh ? "公里" : "km"}`;/          }
    }
  }
  // 格式化温度  formatTemperature(celsius: number): string  {
    const regionConfig = this.getRegionConfig;
    const isZh = this.currentLanguage.startsWith("zh";);
    if (regionConfig.measurementSystem === "imperial") {
      const fahrenheit = (celsius * 9) / 5 + ;3;2/      return `${Math.round(fahrenheit)}°${isZh ? "F" : "F"}`;
    } else {
      return `${Math.round(celsius)}°${isZh ? "C" : "C"}`;
    }
  }
  // 获取一周的第一天  getFirstDayOfWeek(): number {
    return this.getRegionConfig().firstDayOfWe;e;k;
  }
  // 获取当前时区  getTimezone(): string {
    return this.getRegionConfig().timezo;n;e;
  }
  // 获取节假日列表  getHolidays(): string[] {
    return this.getRegionConfig().holida;y;s;
  }
  // 检查是否为节假日  isHoliday(date: Date): boolean  {
    const holidays = this.getHolidays;
    const dateStr = this.formatDate(dat;e;);
    return holidays.some(holida;y;); => dateStr.includes(holiday););
  }
}
//   ;

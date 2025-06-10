import {   I18nManager   } from "react-native;";"";"";
";"";
// 索克生活 - 国际化配置   完整的多语言和地区化支持系统/;/g/;
//;"/;,"/g"/;
N;";"";
  | "zh-TW"";"";
  | "en-US"";"";
  | "en-GB"";"";
  | "ar-SA"";"";
  | "he-IL"";"";
  | "ja-JP"";"";
  | "ko-KR"";"";
//   ;/;/g/;
/    ;/;/g/;
// 语言配置接口 * export interface LanguageConfig {/;,}code: SupportedLanguage,;,/g,/;
  name: string,;
nativeName: string,;
isRTL: boolean,;
dateFormat: string,;
timeFormat: string,;
}
}
  numberFormat: {decimal: string,thousands: string,currency: string;}
};
culturalPreferences: {primaryColor: string}accentColor: string,;
}
    preferredFontSize: number,}
    const animationDuration = number;}
}";"";
//"/;,"/g,"/;
  code: "zh-CN";",";
name: "Chinese (Simplified)";",";
isRTL: false,";"";
";,"";
timeFormat: "HH:mm";",";
numberFormat: {,";,}decimal: ".";","";"";
}
      thousands: ";","}";
currency: "¥";},";,"";
culturalPreferences: {,";}}"";
  primaryColor: "#35bb78",  accentColor: "#ff6800",  / 索克橙* ///"}""/;,"/g"/;
const animationDuration = 300;}";"";
  },";"";
  "zh-TW": {";,}code: "zh-TW";",";
name: "Chinese (Traditional)";",";
isRTL: false,";"";
";,"";
timeFormat: "HH:mm";",";
numberFormat: {,";,}decimal: ".";","";"";
}
      thousands: ";","}";
currency: "NT$";},";,"";
culturalPreferences: {,";,}primaryColor: "#35bb78";",";
accentColor: "#ff6800";","";"";
}
      preferredFontSize: 16,}
      const animationDuration = 300;}";"";
  },";"";
  "en-US": {";,}code: "en-US";",";
name: "English (US)";",";
nativeName: "English (US)";",";
isRTL: false,";,"";
dateFormat: "MM/DD/YYYY",/        timeFormat: "h:mm A";",""/;,"/g,"/;
  numberFormat: {,";,}decimal: ".";","";"";
}
      thousands: ";","}";
currency: "$";},";,"";
culturalPreferences: {,";,}primaryColor: "#35bb78";",";
accentColor: "#ff6800";","";"";
}
      preferredFontSize: 16,}
      const animationDuration = 250;}";"";
  },";"";
  "en-GB": {";,}code: "en-GB";",";
name: "English (UK)";",";
nativeName: "English (UK)";",";
isRTL: false,";,"";
dateFormat: "DD/MM/YYYY",/        timeFormat: "HH:mm";",""/;,"/g,"/;
  numberFormat: {,";,}decimal: ".";","";"";
}
      thousands: ";","}";
currency: "£";},";,"";
culturalPreferences: {,";,}primaryColor: "#35bb78";",";
accentColor: "#ff6800";","";"";
}
      preferredFontSize: 16,}
      const animationDuration = 250;}";"";
  },";"";
  "ar-SA": {";,}code: "ar-SA";",";
name: "Arabic (Saudi Arabia)";",";
nativeName: "العربية (السعودية)";",";
isRTL: true,";,"";
dateFormat: "DD/MM/YYYY",/        timeFormat: "HH:mm";",""/;,"/g,"/;
  numberFormat: {,";,}decimal: ".";","";"";
}
      thousands: ";","}";
currency: "ر.س";},";,"";
culturalPreferences: {,";,}primaryColor: "#35bb78";",";
accentColor: "#ff6800";","";"";
}
      preferredFontSize: 18,}
      const animationDuration = 400;}";"";
  },";"";
  "he-IL": {";,}code: "he-IL";",";
name: "Hebrew (Israel)";",";
nativeName: "עברית (ישראל)";",";
isRTL: true,";,"";
dateFormat: "DD/MM/YYYY",/        timeFormat: "HH:mm";",""/;,"/g,"/;
  numberFormat: {,";,}decimal: ".";","";"";
}
      thousands: ";","}";
currency: "₪";},";,"";
culturalPreferences: {,";,}primaryColor: "#35bb78";",";
accentColor: "#ff6800";","";"";
}
      preferredFontSize: 18,}
      const animationDuration = 400;}";"";
  },";"";
  "ja-JP": {";,}code: "ja-JP";",";
name: "Japanese";",";
isRTL: false,";"";
";,"";
timeFormat: "HH:mm";",";
numberFormat: {,";,}decimal: ".";","";"";
}
      thousands: ";","}";
currency: "¥";},";,"";
culturalPreferences: {,";,}primaryColor: "#35bb78";",";
accentColor: "#ff6800";","";"";
}
      preferredFontSize: 15,}
      const animationDuration = 200;}";"";
  },";"";
  "ko-KR": {";,}code: "ko-KR";",";
name: "Korean";",";
nativeName: "한국어";",";
isRTL: false,";,"";
dateFormat: "YYYY년 MM월 DD일";",";
timeFormat: "HH:mm";",";
numberFormat: {,";,}decimal: ".";","";"";
}
      thousands: ";","}";
currency: "₩";},";,"";
culturalPreferences: {,";,}primaryColor: "#35bb78";",";
accentColor: "#ff6800";","";"";
}
      preferredFontSize: 16,}
      const animationDuration = 250;}
  }
}
//  ;/;/g/;
//  ;/;/g/;
/    ;/;/g/;
//   ;"/;"/g"/;
{";,}LANGUAGE: "@suoke_life:language";","";"";
}
      REGION: "@suoke_life:region";","}";,"";
const CULTURAL_PREFERENCES = "@suoke_life: cultural_preferences";};";"";
// 地区配置接口 * export interface RegionConfig {/;,}code: string,;,/g,/;
  name: string,";,"";
timezone: string,";"";
}
}
  currency: string,measurementSystem: "metric" | "imperial",firstDayOfWeek: 0 | 1;  holidays: string[];"}"";"";
}
//"/;,"/g,"/;
  CN: {,";,}code: "CN";","";"";
";,"";
timezone: "Asia/Shanghai",/        currency: "CNY";",""/;,"/g,"/;
  measurementSystem: "metric";",";
const firstDayOfWeek = 1;
}
}
  },";,"";
TW: {,";,}code: "TW";","";"";
";,"";
timezone: "Asia/Taipei",/        currency: "TWD";",""/;,"/g,"/;
  measurementSystem: "metric";",";
const firstDayOfWeek = 1;
}
}
  },";,"";
US: {,";,}code: "US";",";
name: "United States";",";
timezone: "America/New_York",/        currency: "USD";",""/;,"/g,"/;
  measurementSystem: "imperial";",";
firstDayOfWeek: 0,";"";
}
    holidays: ["New Year",Independence Day", "Thanksgiving",Christmas"]"}"";"";
  ;},";,"";
GB: {,";,}code: "GB";",";
name: "United Kingdom";",";
timezone: "Europe/London",/        currency: "GBP";",""/;,"/g,"/;
  measurementSystem: "metric";",";
firstDayOfWeek: 1,";"";
}
    holidays: ["New Year",Easter", "Christmas",Boxing Day"]"}"";"";
  ;},";,"";
SA: {,";,}code: "SA";",";
name: "Saudi Arabia";",";
timezone: "Asia/Riyadh",/        currency: "SAR";",""/;,"/g,"/;
  measurementSystem: "metric";",";
firstDayOfWeek: 0,";"";
}
    holidays: ["Eid al-Fitr",Eid al-Adha", "National Day"]"}"";"";
  ;},";,"";
IL: {,";,}code: "IL";",";
name: "Israel";",";
timezone: "Asia/Jerusalem",/        currency: "ILS";",""/;,"/g,"/;
  measurementSystem: "metric";",";
firstDayOfWeek: 0,";"";
}
    holidays: ["Rosh Hashanah",Yom Kippur", "Passover",Independence Day"]"}"";"";
  ;},";,"";
JP: {,";,}code: "JP";",";
name: "Japan";",";
timezone: "Asia/Tokyo",/        currency: "JPY";",""/;,"/g,"/;
  measurementSystem: "metric";",";
firstDayOfWeek: 0,";"";
}
    holidays: ["New Year",Golden Week", "Obon",Culture Day"]"}"";"";
  ;},";,"";
KR: {,";,}code: "KR";",";
name: "South Korea";",";
timezone: "Asia/Seoul",/        currency: "KRW";",""/;,"/g,"/;
  measurementSystem: "metric";",";
firstDayOfWeek: 0,";"";
}
    holidays: ["New Year",Lunar New Year", "Children"s Day",National Day"]''}'';'';
  ;}
}';'';
// 文化偏好接口 * export interface CulturalPreferences {/;}';,'/g,'/;
  colorScheme: "light" | "dark" | "auto";",";
accentColor: string,";,"";
fontSize: "small" | "medium" | "large";",";
animationSpeed: "slow" | "normal" | "fast";",";
soundEnabled: boolean,;
hapticEnabled: boolean,;
}
}
  const reducedMotion = boolean;}
}";"";
//,"/;,"/g,"/;
  colorScheme: "auto";",";
accentColor: "#35bb78";",";
fontSize: "medium";",";
animationSpeed: "normal";",";
soundEnabled: true,;
hapticEnabled: true,;
const reducedMotion = false;};
//   ;/;/g/;
>  ;{//;}}/g/;
  return RTL_LANGUAGES.includes(languag;e;);}
};";"";
//   ;"/;"/g"/;
>  ;{return language.split("-")[1] || "C;N";"}"";"";
};
//   ;/;/g/;
>  ;{//;,}if (I18nManager.isRTL !== isRTL) {I18nManager.allowRTL(isRTL);}}/g/;
    I18nManager.forceRTL(isRTL);}
  }";"";
};""";
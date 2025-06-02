// 应用配置常量
export const STORAGE_CONFIG = ;{;
    KEYS: {
      AUTH_TOKEN: '@suoke_life:auth_token',
      REFRESH_TOKEN: '@suoke_life:refresh_token',
      USER_ID: '@suoke_life:user_id',
      USER_PREFERENCES: '@suoke_life:user_preferences',
      THEME: '@suoke_life:theme',
      LANGUAGE: '@suoke_life:language'
    }
  };
  export const API_CONFIG = ;{
    BASE_URL: 'https:// api.suokelife.com',
    TIMEOUT: 10000,
    RETRY_ATTEMPTS: 3
  };
  export const APP_CONFIG = ;{
    NAME: '索克生活',
    VERSION: '1.0.0',
    BUILD_NUMBER: '1',
    ENVIRONMENT: process.env.NODE_ENV || 'development'
  };
  export const THEME_CONFIG = ;{
    LIGHT: 'light',
    DARK: 'dark',
    SYSTEM: 'system'
  };
  export const LANGUAGE_CONFIG = ;{
    ZH_CN: 'zh-CN',
    EN_US: 'en-US'
  };
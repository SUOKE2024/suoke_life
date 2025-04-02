/**
 * JWT配置模块
 * 提供JWT相关的配置
 */

/**
 * 默认JWT配置选项
 */
const defaultOptions = {
  // JWT密钥(应从环境变量读取)
  secret: process.env.JWT_SECRET || 'suoke-life-jwt-secret-key-development-only',
  
  // 访问令牌配置
  access: {
    // 访问令牌过期时间(默认30分钟)
    expiresIn: process.env.JWT_ACCESS_EXPIRES || '30m',
    
    // 访问令牌Cookie配置
    cookie: {
      name: 'access_token',
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 30 * 60 * 1000 // 30分钟，对应expiresIn
    }
  },
  
  // 刷新令牌配置
  refresh: {
    // 刷新令牌过期时间(默认7天)
    expiresIn: process.env.JWT_REFRESH_EXPIRES || '7d',
    
    // 刷新令牌Cookie配置
    cookie: {
      name: 'refresh_token',
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/api/auth/refresh', // 限制刷新令牌只能用于刷新端点
      maxAge: 7 * 24 * 60 * 60 * 1000 // 7天，对应expiresIn
    }
  },
  
  // 临时令牌配置(用于邮件验证等)
  temporary: {
    // 临时令牌过期时间(默认1小时)
    expiresIn: process.env.JWT_TEMPORARY_EXPIRES || '1h'
  },
  
  // 验签算法
  algorithm: 'HS256',
  
  // 颁发者
  issuer: 'suoke.life',
  
  // 允许的受众
  audience: 'suoke.life-clients'
};

/**
 * 根据环境获取JWT配置
 * @param {string} env - 环境名称
 * @returns {Object} JWT配置
 */
const getConfig = (env = process.env.NODE_ENV || 'development') => {
  // 生产环境配置
  if (env === 'production') {
    if (!process.env.JWT_SECRET) {
      console.warn('警告: 生产环境中未设置JWT_SECRET环境变量');
    }
    
    return {
      ...defaultOptions,
      // 生产环境特定配置覆盖
      access: {
        ...defaultOptions.access,
        cookie: {
          ...defaultOptions.access.cookie,
          secure: true,
          sameSite: 'strict'
        }
      },
      refresh: {
        ...defaultOptions.refresh,
        cookie: {
          ...defaultOptions.refresh.cookie,
          secure: true,
          sameSite: 'strict'
        }
      }
    };
  }
  
  // 测试环境配置
  if (env === 'test') {
    return {
      ...defaultOptions,
      // 测试环境特定配置覆盖
      access: {
        ...defaultOptions.access,
        expiresIn: '15m' // 更短的过期时间便于测试
      },
      refresh: {
        ...defaultOptions.refresh,
        expiresIn: '1d' // 更短的过期时间便于测试
      }
    };
  }
  
  // 开发环境(默认)配置
  return {
    ...defaultOptions
  };
};

/**
 * 导出当前环境的JWT配置
 */
module.exports = getConfig(); 
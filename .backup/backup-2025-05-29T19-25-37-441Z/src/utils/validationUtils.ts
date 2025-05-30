/**
 * 验证工具函数
 */

/**
 * 邮箱验证
 */
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * 手机号验证（中国大陆）
 */
export const validatePhone = (phone: string): boolean => {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
};

/**
 * 密码验证
 */
export const validatePassword = (
  password: string
): {
  isValid: boolean;
  errors: string[];
} => {
  const errors: string[] = [];

  if (password.length < 6) {
    errors.push('密码长度至少6位');
  }

  if (password.length > 20) {
    errors.push('密码长度不能超过20位');
  }

  if (!/[a-zA-Z]/.test(password)) {
    errors.push('密码必须包含字母');
  }

  if (!/\d/.test(password)) {
    errors.push('密码必须包含数字');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
};

/**
 * 用户名验证
 */
export const validateUsername = (username: string): boolean => {
  // 用户名：3-20位，只能包含字母、数字、下划线
  const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
  return usernameRegex.test(username);
};

/**
 * 身份证号验证（中国大陆）
 */
export const validateIdCard = (idCard: string): boolean => {
  const idCardRegex =
    /(^[1-9]\d{5}(18|19|([23]\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$)|(^[1-9]\d{5}\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{2}$)/;
  return idCardRegex.test(idCard);
};

/**
 * 必填项验证
 */
export const validateRequired = (value: any): boolean => {
  if (value === null || value === undefined) {
    return false;
  }

  if (typeof value === 'string') {
    return value.trim().length > 0;
  }

  if (Array.isArray(value)) {
    return value.length > 0;
  }

  return true;
};

/**
 * 数字范围验证
 */
export const validateNumberRange = (
  value: number,
  min?: number,
  max?: number
): boolean => {
  if (isNaN(value)) {
    return false;
  }

  if (min !== undefined && value < min) {
    return false;
  }

  if (max !== undefined && value > max) {
    return false;
  }

  return true;
};

/**
 * 年龄验证（基于数字）
 */
export const validateAgeNumber = (age: number): boolean => {
  return validateNumberRange(age, 0, 150);
};

/**
 * 年龄验证（基于出生日期）
 */
export const validateAge = (birthDate: string): { isValid: boolean; age?: number; error?: string } => {
  try {
    // 先检查日期格式
    if (!birthDate || typeof birthDate !== 'string') {
      return { isValid: false, error: '无效的日期格式' };
    }
    
    const birth = new Date(birthDate);
    const now = new Date();
    
    // 检查日期格式是否有效
    if (isNaN(birth.getTime())) {
      return {
        isValid: false,
        error: '无效的日期格式',
      };
    }
    
    // 检查是否为未来日期
    if (birth > now) {
      return {
        isValid: false,
        error: '出生日期不能是未来日期',
      };
    }
    
    // 检查年份是否合理（不能早于1850年）
    if (birth.getFullYear() < 1850) {
      return {
        isValid: false,
        error: '出生年份不能早于1850年',
      };
    }
    
    // 计算年龄
    let age = now.getFullYear() - birth.getFullYear();
    const monthDiff = now.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && now.getDate() < birth.getDate())) {
      age--;
    }
    
    // 检查年份是否合理（不能早于1850年）
    if (birth.getFullYear() < 1850) {
      return {
        isValid: false,
        error: '出生年份不能早于1850年',
      };
    }
    
    // 检查年龄范围
    if (age < 0) {
      return {
        isValid: false,
        error: '年龄不能为负数',
      };
    }
    
    if (age > 150) {
      return {
        isValid: false,
        error: '年龄不能超过150岁',
      };
    }
    
    return {
      isValid: true,
      age,
    };
  } catch (error) {
    return {
      isValid: false,
      error: '日期解析错误',
    };
  }
};

/**
 * 身高验证（厘米）
 */
export const validateHeight = (height: number): boolean => {
  return validateNumberRange(height, 50, 300);
};

/**
 * 体重验证（公斤）
 */
export const validateWeight = (weight: number): boolean => {
  return validateNumberRange(weight, 10, 500);
};

/**
 * URL验证
 */
export const validateUrl = (url: string): boolean => {
  try {
    const urlObject = new URL(url);
    return Boolean(urlObject);
  } catch {
    return false;
  }
};

/**
 * 表单验证规则类型
 */
export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => boolean | string;
}

/**
 * 表单字段验证
 */
export const validateField = (
  value: any,
  rules: ValidationRule
): {
  isValid: boolean;
  error?: string;
} => {
  // 必填项验证
  if (rules.required && !validateRequired(value)) {
    return {
      isValid: false,
      error: '此字段为必填项',
    };
  }

  // 如果不是必填且值为空，则验证通过
  if (!rules.required && !validateRequired(value)) {
    return { isValid: true };
  }

  const stringValue = String(value);

  // 最小长度验证
  if (rules.minLength && stringValue.length < rules.minLength) {
    return {
      isValid: false,
      error: `最少需要${rules.minLength}个字符`,
    };
  }

  // 最大长度验证
  if (rules.maxLength && stringValue.length > rules.maxLength) {
    return {
      isValid: false,
      error: `最多允许${rules.maxLength}个字符`,
    };
  }

  // 正则表达式验证
  if (rules.pattern && !rules.pattern.test(stringValue)) {
    return {
      isValid: false,
      error: '格式不正确',
    };
  }

  // 自定义验证
  if (rules.custom) {
    const customResult = rules.custom(value);
    if (typeof customResult === 'string') {
      return {
        isValid: false,
        error: customResult,
      };
    } else if (!customResult) {
      return {
        isValid: false,
        error: '验证失败',
      };
    }
  }

  return { isValid: true };
};

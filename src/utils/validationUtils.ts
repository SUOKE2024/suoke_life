// 简化的验证工具
export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => boolean;
}

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePhone = (phone: string): boolean => {
  const phoneRegex = /^[1][3-9]\d{9}$/;
  return phoneRegex.test(phone);
};

export const validatePassword = (password: string): boolean => {
  return password.length >= 6;
};

export const validateRequired = (value: any): boolean => {
  if (typeof value === 'string') {
    return value.trim().length > 0;
  }
  return value != null && value !== undefined;
};

export const validateLength = (;
  value: string,
  minLength?: number,
  maxLength?: number;
): boolean => {
  if (!value) return false;

  if (minLength && value.length < minLength) return false;
  if (maxLength && value.length > maxLength) return false;

  return true;
};

export const validateNumberRange = (;
  value: number,
  min?: number,
  max?: number;
): boolean => {
  if (min !== undefined && value < min) return false;
  if (max !== undefined && value > max) return false;
  return true;
};

export const validateField = (;
  value: unknown,
  rules: ValidationRule;
): { isValid: boolean; error?: string } => {
  if (rules.required && !validateRequired(value)) {
    return { isValid: false, error: '此字段为必填项' };
  }

  if (typeof value === 'string') {
    if (rules.minLength && value.length < rules.minLength) {
      return { isValid: false, error: `最少需要${rules.minLength}个字符` };
    }

    if (rules.maxLength && value.length > rules.maxLength) {
      return { isValid: false, error: `最多允许${rules.maxLength}个字符` };
    }

    if (rules.pattern && !rules.pattern.test(value)) {
      return { isValid: false, error: '格式不正确' };
    }
  }

  if (rules.custom && !rules.custom(value)) {
    return { isValid: false, error: '自定义验证失败' };
  }

  return { isValid: true };
};

export const validateForm = (;
  data: Record<string, unknown>,
  rules: Record<string, ValidationRule>
): { isValid: boolean; errors: Record<string, string> } => {
  const errors: Record<string, string> = {};

  for (const [field, rule] of Object.entries(rules)) {
    const result = validateField(data[field], rule);
    if (!result.isValid && result.error) {
      errors[field] = result.error;
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

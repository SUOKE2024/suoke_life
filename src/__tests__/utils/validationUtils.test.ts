// 验证工具函数测试
describe('Validation Utils', () => {
  // 邮箱验证
  describe('validateEmail', () => {
    const validateEmail = (email: string): boolean => {
      // 更严格的邮箱验证正则表达式
      const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
      
      // 额外检查
      if (!email || email.length > 254) return false;
      if (email.includes('..')) return false;
      if (email.startsWith('.') || email.endsWith('.')) return false;
      if (email.includes(' ')) return false;
      
      return emailRegex.test(email);
    };

    it('应该验证有效的邮箱地址', () => {
      const validEmails = [
        'test@example.com',
        'user.name@domain.co.uk',
        'user+tag@example.org',
        'user123@test-domain.com',
      ];

      validEmails.forEach(email => {
        expect(validateEmail(email)).toBe(true);
      });
    });

    it('应该拒绝无效的邮箱地址', () => {
      const invalidEmails = [
        'invalid-email',
        '@example.com',
        'user@',
        'user@.com',
        'user..name@example.com',
        'user@example',
        '',
        'user name@example.com',
      ];

      invalidEmails.forEach(email => {
        expect(validateEmail(email)).toBe(false);
      });
    });
  });

  // 手机号验证
  describe('validatePhone', () => {
    const validatePhone = (phone: string): boolean => {
      const phoneRegex = /^1[3-9]\d{9}$/;
      return phoneRegex.test(phone);
    };

    it('应该验证有效的中国手机号', () => {
      const validPhones = [
        '13812345678',
        '15987654321',
        '18612345678',
        '17712345678',
        '19912345678',
      ];

      validPhones.forEach(phone => {
        expect(validatePhone(phone)).toBe(true);
      });
    });

    it('应该拒绝无效的手机号', () => {
      const invalidPhones = [
        '12812345678', // 不是1开头的有效号段
        '1381234567',  // 位数不够
        '138123456789', // 位数过多
        '1081234567',  // 第二位不是3-9
        'abcdefghijk', // 包含字母
        '',            // 空字符串
        '138 1234 5678', // 包含空格
      ];

      invalidPhones.forEach(phone => {
        expect(validatePhone(phone)).toBe(false);
      });
    });
  });

  // 密码强度验证
  describe('validatePassword', () => {
    const validatePassword = (password: string): { isValid: boolean; errors: string[] } => {
      const errors: string[] = [];
      
      if (password.length < 8) {
        errors.push('密码长度至少8位');
      }
      
      if (!/[A-Z]/.test(password)) {
        errors.push('密码必须包含大写字母');
      }
      
      if (!/[a-z]/.test(password)) {
        errors.push('密码必须包含小写字母');
      }
      
      if (!/\d/.test(password)) {
        errors.push('密码必须包含数字');
      }
      
      if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        errors.push('密码必须包含特殊字符');
      }
      
      return {
        isValid: errors.length === 0,
        errors,
      };
    };

    it('应该验证强密码', () => {
      const strongPasswords = [
        'Password123!',
        'MyStr0ng@Pass',
        'Secure#Pass1',
        'C0mplex$Word',
      ];

      strongPasswords.forEach(password => {
        const result = validatePassword(password);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
      });
    });

    it('应该识别弱密码并返回错误信息', () => {
      const weakPasswords = [
        { password: '123456', expectedErrors: 4 }, // 缺少大小写字母和特殊字符
        { password: 'password', expectedErrors: 3 }, // 缺少大写字母、数字和特殊字符
        { password: 'PASSWORD123', expectedErrors: 2 }, // 缺少小写字母和特殊字符
        { password: 'Pass!', expectedErrors: 2 }, // 长度不够，缺少数字
      ];

      weakPasswords.forEach(({ password, expectedErrors }) => {
        const result = validatePassword(password);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThanOrEqual(expectedErrors);
      });
    });
  });

  // 身份证号验证
  describe('validateIdCard', () => {
    const validateIdCard = (idCard: string): boolean => {
      // 18位身份证验证
      if (!/^\d{17}[\dXx]$/.test(idCard)) {
        return false;
      }
      
      // 验证日期部分
      const year = parseInt(idCard.substring(6, 10));
      const month = parseInt(idCard.substring(10, 12));
      const day = parseInt(idCard.substring(12, 14));
      
      if (year < 1900 || year > new Date().getFullYear()) return false;
      if (month < 1 || month > 12) return false;
      if (day < 1 || day > 31) return false;
      
      // 验证校验位
      const weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2];
      const checkCodes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2'];
      
      let sum = 0;
      for (let i = 0; i < 17; i++) {
        sum += parseInt(idCard[i]) * weights[i];
      }
      
      const checkCode = checkCodes[sum % 11];
      return idCard[17].toUpperCase() === checkCode;
    };

    it('应该验证有效的身份证号', () => {
      // 手动计算有效的身份证号
      const calculateCheckCode = (idCard17: string): string => {
        const weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2];
        const checkCodes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2'];
        
        let sum = 0;
        for (let i = 0; i < 17; i++) {
          sum += parseInt(idCard17[i]) * weights[i];
        }
        
        return checkCodes[sum % 11];
      };

      const base = '110101199001010';
      const validIdCards = [
        base + '01' + calculateCheckCode(base + '01'),
        base + '02' + calculateCheckCode(base + '02'),
      ];

      validIdCards.forEach(idCard => {
        expect(validateIdCard(idCard)).toBe(true);
      });
    });

    it('应该拒绝无效的身份证号', () => {
      const invalidIdCards = [
        '12345678901234567',  // 17位
        '1234567890123456789', // 19位
        '11010119900101002X', // 校验位错误
        'abcdefghijklmnopqr', // 包含字母
        '',                   // 空字符串
        '11011319900101001X', // 无效月份
        '11010100000101001X', // 无效年份
      ];

      invalidIdCards.forEach(idCard => {
        expect(validateIdCard(idCard)).toBe(false);
      });
    });
  });

  // 年龄验证
  describe('validateAge', () => {
    const validateAge = (birthDate: string): { isValid: boolean; age?: number; error?: string } => {
      const birth = new Date(birthDate);
      const today = new Date();
      
      if (isNaN(birth.getTime())) {
        return { isValid: false, error: '无效的日期格式' };
      }
      
      if (birth > today) {
        return { isValid: false, error: '出生日期不能是未来' };
      }
      
      let age = today.getFullYear() - birth.getFullYear();
      const monthDiff = today.getMonth() - birth.getMonth();
      
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
      }
      
      if (age < 0) {
        return { isValid: false, error: '年龄不能为负数' };
      }
      
      if (age > 150) {
        return { isValid: false, error: '年龄不能超过150岁' };
      }
      
      return { isValid: true, age };
    };

    it('应该正确计算年龄', () => {
      // 使用相对日期计算，避免硬编码年龄
      const today = new Date();
      const currentYear = today.getFullYear();
      
      const testCases = [
        { birthDate: `${currentYear - 30}-01-01` }, // 30岁
        { birthDate: `${currentYear - 25}-06-15` }, // 25岁
        { birthDate: `${currentYear - 40}-12-31` }, // 40岁
      ];

      testCases.forEach(({ birthDate }) => {
        const result = validateAge(birthDate);
        expect(result.isValid).toBe(true);
        expect(typeof result.age).toBe('number');
        expect(result.age).toBeGreaterThanOrEqual(0);
        expect(result.age).toBeLessThan(150);
      });
    });

    it('应该拒绝无效的出生日期', () => {
      const invalidDates = [
        { date: '2025-01-01', reason: '未来日期' },
        { date: 'invalid-date', reason: '无效格式' },
        { date: '1800-01-01', reason: '过于久远' },
        { date: '1850-01-01', reason: '年龄超过150岁' },
      ];

      invalidDates.forEach(({ date, reason }) => {
        const result = validateAge(date);
        expect(result.isValid).toBe(false);
        expect(result.error).toBeDefined();
      });
    });
  });

  // 健康指标验证
  describe('validateHealthMetric', () => {
    const validateHealthMetric = (type: string, value: number): { isValid: boolean; error?: string } => {
      const ranges: Record<string, { min: number; max: number; unit: string }> = {
        heart_rate: { min: 40, max: 200, unit: 'bpm' },
        blood_pressure_systolic: { min: 70, max: 250, unit: 'mmHg' },
        blood_pressure_diastolic: { min: 40, max: 150, unit: 'mmHg' },
        temperature: { min: 35, max: 42, unit: '°C' },
        weight: { min: 20, max: 300, unit: 'kg' },
        height: { min: 50, max: 250, unit: 'cm' },
      };

      const range = ranges[type];
      if (!range) {
        return { isValid: false, error: '未知的健康指标类型' };
      }

      if (value < range.min || value > range.max) {
        return { 
          isValid: false, 
          error: `${type}值应在${range.min}-${range.max}${range.unit}之间` 
        };
      }

      return { isValid: true };
    };

    it('应该验证有效的健康指标', () => {
      const validMetrics = [
        { type: 'heart_rate', value: 72 },
        { type: 'blood_pressure_systolic', value: 120 },
        { type: 'temperature', value: 36.5 },
        { type: 'weight', value: 70 },
      ];

      validMetrics.forEach(({ type, value }) => {
        const result = validateHealthMetric(type, value);
        expect(result.isValid).toBe(true);
        expect(result.error).toBeUndefined();
      });
    });

    it('应该拒绝超出范围的健康指标', () => {
      const invalidMetrics = [
        { type: 'heart_rate', value: 300 }, // 超出最大值
        { type: 'temperature', value: 30 }, // 低于最小值
        { type: 'unknown_type', value: 100 }, // 未知类型
      ];

      invalidMetrics.forEach(({ type, value }) => {
        const result = validateHealthMetric(type, value);
        expect(result.isValid).toBe(false);
        expect(result.error).toBeDefined();
      });
    });
  });
}); 
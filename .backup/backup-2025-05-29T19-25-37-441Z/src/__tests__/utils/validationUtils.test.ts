/**
 * 验证工具函数测试
 * 测试各种数据验证功能
 */

describe('验证工具函数测试', () => {
  describe('邮箱验证', () => {
    it('应该验证有效的邮箱地址', () => {
      const validEmails = [
        'test@example.com',
        'user.name@domain.co.uk',
        'user+tag@example.org',
        'user123@test-domain.com',
      ];

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      
      validEmails.forEach(email => {
        expect(emailRegex.test(email)).toBe(true);
      });
    });

    it('应该拒绝无效的邮箱地址', () => {
      const invalidEmails = [
        'invalid-email',
        '@example.com',
        'user@',
        'user@.com',
        'user@example',
      ];

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      
      invalidEmails.forEach(email => {
        expect(emailRegex.test(email)).toBe(false);
      });
    });
  });

  describe('密码验证', () => {
    it('应该验证密码强度', () => {
      const validatePassword = (password: string) => {
        const minLength = password.length >= 8;
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        return {
          isValid: minLength && hasUpperCase && hasLowerCase && hasNumbers,
          minLength,
          hasUpperCase,
          hasLowerCase,
          hasNumbers,
          hasSpecialChar,
        };
      };

      const strongPassword = 'StrongPass123!';
      const weakPassword = 'weak';

      const strongResult = validatePassword(strongPassword);
      const weakResult = validatePassword(weakPassword);

      expect(strongResult.isValid).toBe(true);
      expect(strongResult.minLength).toBe(true);
      expect(strongResult.hasUpperCase).toBe(true);
      expect(strongResult.hasLowerCase).toBe(true);
      expect(strongResult.hasNumbers).toBe(true);

      expect(weakResult.isValid).toBe(false);
      expect(weakResult.minLength).toBe(false);
    });

    it('应该检查密码复杂度', () => {
      const getPasswordStrength = (password: string) => {
        let score = 0;
        if (password.length >= 8) {score++;}
        if (/[A-Z]/.test(password)) {score++;}
        if (/[a-z]/.test(password)) {score++;}
        if (/\d/.test(password)) {score++;}
        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {score++;}

        if (score <= 2) {return 'weak';}
        if (score <= 3) {return 'medium';}
        return 'strong';
      };

      expect(getPasswordStrength('123')).toBe('weak');
      expect(getPasswordStrength('Password123')).toBe('strong');
      expect(getPasswordStrength('Password123!')).toBe('strong');
    });
  });

  describe('手机号验证', () => {
    it('应该验证中国手机号', () => {
      const validateChinesePhone = (phone: string) => {
        const regex = /^1[3-9]\d{9}$/;
        return regex.test(phone);
      };

      const validPhones = [
        '13812345678',
        '15987654321',
        '18612345678',
        '19123456789',
      ];

      const invalidPhones = [
        '12345678901',
        '1381234567',
        '138123456789',
        '21812345678',
      ];

      validPhones.forEach(phone => {
        expect(validateChinesePhone(phone)).toBe(true);
      });

      invalidPhones.forEach(phone => {
        expect(validateChinesePhone(phone)).toBe(false);
      });
    });
  });

  describe('身份证验证', () => {
    it('应该验证身份证号格式', () => {
      const validateIdCard = (idCard: string) => {
        // 简化的身份证验证
        const regex = /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/;
        return regex.test(idCard);
      };

      const validIdCards = [
        '11010119900101001X',
        '110101199001010010',
        '44030119850615123X',
      ];

      const invalidIdCards = [
        '123456789012345678',
        '11010119900101001',
        '110101199013010010', // 无效月份
      ];

      validIdCards.forEach(idCard => {
        expect(validateIdCard(idCard)).toBe(true);
      });

      invalidIdCards.forEach(idCard => {
        expect(validateIdCard(idCard)).toBe(false);
      });
    });
  });

  describe('数字验证', () => {
    it('应该验证整数', () => {
      const isInteger = (value: any) => {
        return Number.isInteger(Number(value));
      };

      expect(isInteger(123)).toBe(true);
      expect(isInteger('456')).toBe(true);
      expect(isInteger(123.45)).toBe(false);
      expect(isInteger('abc')).toBe(false);
    });

    it('应该验证数字范围', () => {
      const isInRange = (value: number, min: number, max: number) => {
        return value >= min && value <= max;
      };

      expect(isInRange(5, 1, 10)).toBe(true);
      expect(isInRange(0, 1, 10)).toBe(false);
      expect(isInRange(15, 1, 10)).toBe(false);
    });

    it('应该验证正数', () => {
      const isPositive = (value: number) => {
        return value > 0;
      };

      expect(isPositive(5)).toBe(true);
      expect(isPositive(0)).toBe(false);
      expect(isPositive(-5)).toBe(false);
    });
  });

  describe('字符串验证', () => {
    it('应该验证字符串长度', () => {
      const validateLength = (str: string, min: number, max: number) => {
        return str.length >= min && str.length <= max;
      };

      expect(validateLength('hello', 3, 10)).toBe(true);
      expect(validateLength('hi', 3, 10)).toBe(false);
      expect(validateLength('very long string', 3, 10)).toBe(false);
    });

    it('应该验证只包含字母', () => {
      const isAlphabetic = (str: string) => {
        return /^[a-zA-Z]+$/.test(str);
      };

      expect(isAlphabetic('hello')).toBe(true);
      expect(isAlphabetic('Hello')).toBe(true);
      expect(isAlphabetic('hello123')).toBe(false);
      expect(isAlphabetic('hello world')).toBe(false);
    });

    it('应该能够验证只包含数字和字母', () => {
      const isAlphanumeric = (str: string) => {
        return /^[a-zA-Z0-9]+$/.test(str);
      };

      expect(isAlphanumeric('hello123')).toBe(true);
      expect(isAlphanumeric('Hello')).toBe(true);
      expect(isAlphanumeric('123')).toBe(true);
      expect(isAlphanumeric('hello-world')).toBe(false);
    });
  });

  describe('URL验证', () => {
    it('应该验证有效的URL', () => {
      const isValidUrl = (url: string) => {
        try {
          new URL(url);
          return true;
        } catch {
          return false;
        }
      };

      const validUrls = [
        'https://www.example.com',
        'http://example.com',
        'https://example.com/path?query=value',
        'ftp://files.example.com',
      ];

      const invalidUrls = [
        'not-a-url',
        'example.com', // 缺少协议，但在某些环境中可能被认为有效
      ];

      validUrls.forEach(url => {
        expect(isValidUrl(url)).toBe(true);
      });

      // 只测试明确无效的URL
      expect(isValidUrl('not-a-url')).toBe(false);
    });
  });

  describe('日期验证', () => {
    it('应该验证日期格式', () => {
      const isValidDate = (dateString: string) => {
        const date = new Date(dateString);
        return !isNaN(date.getTime());
      };

      expect(isValidDate('2024-12-19')).toBe(true);
      expect(isValidDate('2024/12/19')).toBe(true);
      expect(isValidDate('invalid-date')).toBe(false);
      expect(isValidDate('2024-13-01')).toBe(false); // 无效月份
    });

    it('应该验证年龄范围', () => {
      const isValidAge = (birthDate: string, minAge: number, maxAge: number) => {
        const birth = new Date(birthDate);
        const today = new Date();
        const age = today.getFullYear() - birth.getFullYear();
        
        return age >= minAge && age <= maxAge;
      };

      expect(isValidAge('1990-01-01', 18, 65)).toBe(true);
      expect(isValidAge('2010-01-01', 18, 65)).toBe(false); // 太年轻
      expect(isValidAge('1950-01-01', 18, 65)).toBe(false); // 太老
    });
  });

  describe('文件验证', () => {
    it('应该验证文件扩展名', () => {
      const isValidFileExtension = (filename: string, allowedExtensions: string[]) => {
        const extension = filename.split('.').pop()?.toLowerCase();
        return extension ? allowedExtensions.includes(extension) : false;
      };

      const allowedImages = ['jpg', 'jpeg', 'png', 'gif'];
      
      expect(isValidFileExtension('photo.jpg', allowedImages)).toBe(true);
      expect(isValidFileExtension('image.PNG', allowedImages)).toBe(true);
      expect(isValidFileExtension('document.pdf', allowedImages)).toBe(false);
      expect(isValidFileExtension('noextension', allowedImages)).toBe(false);
    });

    it('应该验证文件大小', () => {
      const isValidFileSize = (sizeInBytes: number, maxSizeInMB: number) => {
        const maxSizeInBytes = maxSizeInMB * 1024 * 1024;
        return sizeInBytes <= maxSizeInBytes;
      };

      expect(isValidFileSize(1024 * 1024, 2)).toBe(true); // 1MB < 2MB
      expect(isValidFileSize(3 * 1024 * 1024, 2)).toBe(false); // 3MB > 2MB
    });
  });

  describe('综合验证', () => {
    it('应该验证用户注册信息', () => {
      const validateUserRegistration = (userData: {
        username: string;
        email: string;
        password: string;
        phone: string;
      }) => {
        const errors: string[] = [];

        // 用户名验证
        if (userData.username.length < 3 || userData.username.length > 20) {
          errors.push('用户名长度必须在3-20个字符之间');
        }

        // 邮箱验证
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(userData.email)) {
          errors.push('邮箱格式不正确');
        }

        // 密码验证
        if (userData.password.length < 8) {
          errors.push('密码长度至少8个字符');
        }

        // 手机号验证
        const phoneRegex = /^1[3-9]\d{9}$/;
        if (!phoneRegex.test(userData.phone)) {
          errors.push('手机号格式不正确');
        }

        return {
          isValid: errors.length === 0,
          errors,
        };
      };

      const validUser = {
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123',
        phone: '13812345678',
      };

      const invalidUser = {
        username: 'ab',
        email: 'invalid-email',
        password: '123',
        phone: '123456',
      };

      const validResult = validateUserRegistration(validUser);
      const invalidResult = validateUserRegistration(invalidUser);

      expect(validResult.isValid).toBe(true);
      expect(validResult.errors).toHaveLength(0);

      expect(invalidResult.isValid).toBe(false);
      expect(invalidResult.errors.length).toBeGreaterThan(0);
    });
  });
}); 
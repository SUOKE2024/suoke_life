/**
 * 工具函数单元测试
 */
const { validator } = require('../utils');

describe('验证器工具测试', () => {
  describe('isEmail', () => {
    test('有效的邮箱地址应返回true', () => {
      expect(validator.isEmail('test@example.com')).toBe(true);
      expect(validator.isEmail('user.name@domain.co.uk')).toBe(true);
    });

    test('无效的邮箱地址应返回false', () => {
      expect(validator.isEmail('test@')).toBe(false);
      expect(validator.isEmail('test@domain')).toBe(false);
      expect(validator.isEmail('testdomain.com')).toBe(false);
      expect(validator.isEmail('')).toBe(false);
    });
  });

  describe('isStrongPassword', () => {
    test('强密码应返回true', () => {
      expect(validator.isStrongPassword('Test1234!')).toBe(true);
      expect(validator.isStrongPassword('Complex@Pass123')).toBe(true);
    });

    test('弱密码应返回false', () => {
      expect(validator.isStrongPassword('password')).toBe(false);
      expect(validator.isStrongPassword('12345678')).toBe(false);
      expect(validator.isStrongPassword('test')).toBe(false);
    });
  });

  describe('sanitizeInput', () => {
    test('应移除HTML标签', () => {
      expect(validator.sanitizeInput('<script>alert("XSS")</script>')).toBe('alert("XSS")');
      expect(validator.sanitizeInput('<p>普通文本</p>')).toBe('普通文本');
    });

    test('应处理特殊字符', () => {
      expect(validator.sanitizeInput('&lt;div&gt;')).toBe('<div>');
    });
  });
}); 
import {
  validateEmail,
  validatePassword,
  validateUsername,
} from '../utils/authUtils';

describe('认证工具函数测试', () => {
  describe('validateEmail', () => {
    test('应该验证有效的邮箱地址', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name@domain.co.uk')).toBe(true);
      expect(validateEmail('user+tag@example.org')).toBe(true);
    });

    test('应该拒绝无效的邮箱地址', () => {
      expect(validateEmail('invalid-email')).toBe(false);
      expect(validateEmail('test@')).toBe(false);
      expect(validateEmail('@example.com')).toBe(false);
      expect(validateEmail('test.example.com')).toBe(false);
      expect(validateEmail('')).toBe(false);
    });
  });

  describe('validatePassword', () => {
    test('应该验证符合基本要求的密码', () => {
      expect(validatePassword('abc123')).toBe(true);
      expect(validatePassword('password1')).toBe(true);
      expect(validatePassword('Test123')).toBe(true);
    });

    test('应该拒绝不符合要求的密码', () => {
      expect(validatePassword('12345')).toBe(false); // 太短
      expect(validatePassword('abcdef')).toBe(false); // 只有字母
      expect(validatePassword('123456')).toBe(false); // 只有数字
      expect(validatePassword('')).toBe(false); // 空密码
    });

    test('应该验证强密码要求', () => {
      expect(validatePassword('Test123!', 'strong')).toBe(true);
      expect(validatePassword('MyPassword1@', 'strong')).toBe(true);

      expect(validatePassword('test123', 'strong')).toBe(false); // 缺少大写字母和特殊字符
      expect(validatePassword('TEST123!', 'strong')).toBe(false); // 缺少小写字母
    });
  });

  describe('validateUsername', () => {
    test('应该验证有效的用户名', () => {
      expect(validateUsername('user')).toBe(true);
      expect(validateUsername('test_user')).toBe(true);
      expect(validateUsername('用户名')).toBe(true);
      expect(validateUsername('a'.repeat(20))).toBe(true); // 20个字符
    });

    test('应该拒绝无效的用户名', () => {
      expect(validateUsername('a')).toBe(false); // 太短
      expect(validateUsername('a'.repeat(21))).toBe(false); // 太长
      expect(validateUsername('')).toBe(false); // 空用户名
      expect(validateUsername('  ')).toBe(false); // 只有空格
    });
  });
});

/**
 * 工具函数测试
 */

import {
  validateEmail,
  validatePhone,
  validateRequired,
  formatDate,
  calculateAge,
  isSameDay,
  debounce,
  deepClone,
  generateId,
  unique,
  formatNumber,
  isEmpty,
} from '../utils';

describe('Validation Utils', () => {
  describe('validateEmail', () => {
    it('should validate correct email', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name@domain.com')).toBe(true);
    });

    it('should reject invalid email', () => {
      expect(validateEmail('invalid-email')).toBe(false);
      expect(validateEmail('test@')).toBe(false);
      expect(validateEmail('@example.com')).toBe(false);
    });
  });

  describe('validatePhone', () => {
    it('should validate correct Chinese phone number', () => {
      expect(validatePhone('13812345678')).toBe(true);
      expect(validatePhone('15987654321')).toBe(true);
    });

    it('should reject invalid phone number', () => {
      expect(validatePhone('12812345678')).toBe(false);
      expect(validatePhone('1381234567')).toBe(false);
      expect(validatePhone('abc12345678')).toBe(false);
    });
  });

  describe('validateRequired', () => {
    it('should validate required fields', () => {
      expect(validateRequired('test')).toBe(true);
      expect(validateRequired(['item'])).toBe(true);
      expect(validateRequired(0)).toBe(true);
    });

    it('should reject empty values', () => {
      expect(validateRequired('')).toBe(false);
      expect(validateRequired('   ')).toBe(false);
      expect(validateRequired(null)).toBe(false);
      expect(validateRequired(undefined)).toBe(false);
      expect(validateRequired([])).toBe(false);
    });
  });
});

describe('Date Utils', () => {
  describe('formatDate', () => {
    it('should format date correctly', () => {
      const date = new Date('2023-12-25T10:30:00');
      expect(formatDate(date, 'YYYY-MM-DD')).toBe('2023-12-25');
      expect(formatDate(date, 'YYYY-MM-DD HH:mm')).toBe('2023-12-25 10:30');
    });

    it('should handle string dates', () => {
      expect(formatDate('2023-12-25', 'YYYY-MM-DD')).toBe('2023-12-25');
    });
  });

  describe('calculateAge', () => {
    it('should calculate age correctly', () => {
      const birthDate = new Date();
      birthDate.setFullYear(birthDate.getFullYear() - 25);
      expect(calculateAge(birthDate)).toBe(25);
    });
  });

  describe('isSameDay', () => {
    it('should check if dates are same day', () => {
      const date1 = new Date('2023-12-25T10:00:00');
      const date2 = new Date('2023-12-25T15:00:00');
      const date3 = new Date('2023-12-26T10:00:00');

      expect(isSameDay(date1, date2)).toBe(true);
      expect(isSameDay(date1, date3)).toBe(false);
    });
  });
});

describe('Common Utils', () => {
  describe('deepClone', () => {
    it('should deep clone objects', () => {
      const original = { a: 1, b: { c: 2 } };
      const cloned = deepClone(original);

      expect(cloned).toEqual(original);
      expect(cloned).not.toBe(original);
      expect(cloned.b).not.toBe(original.b);
    });

    it('should deep clone arrays', () => {
      const original = [1, { a: 2 }, [3, 4]];
      const cloned = deepClone(original);

      expect(cloned).toEqual(original);
      expect(cloned).not.toBe(original);
      expect(cloned[1]).not.toBe(original[1]);
    });
  });

  describe('generateId', () => {
    it('should generate unique IDs', () => {
      const id1 = generateId();
      const id2 = generateId();

      expect(id1).not.toBe(id2);
      expect(typeof id1).toBe('string');
      expect(id1.length).toBeGreaterThan(0);
    });
  });

  describe('unique', () => {
    it('should remove duplicates from array', () => {
      expect(unique([1, 2, 2, 3, 3, 3])).toEqual([1, 2, 3]);
      expect(unique(['a', 'b', 'a', 'c'])).toEqual(['a', 'b', 'c']);
    });
  });

  describe('formatNumber', () => {
    it('should format numbers correctly', () => {
      expect(formatNumber(123.456)).toBe('123.46');
      expect(formatNumber(123.456, 1)).toBe('123.5');
      expect(formatNumber(NaN)).toBe('0');
    });
  });

  describe('isEmpty', () => {
    it('should check if values are empty', () => {
      expect(isEmpty('')).toBe(true);
      expect(isEmpty('   ')).toBe(true);
      expect(isEmpty(null)).toBe(true);
      expect(isEmpty(undefined)).toBe(true);
      expect(isEmpty([])).toBe(true);
      expect(isEmpty({})).toBe(true);

      expect(isEmpty('test')).toBe(false);
      expect(isEmpty([1])).toBe(false);
      expect(isEmpty({ a: 1 })).toBe(false);
      expect(isEmpty(0)).toBe(false);
    });
  });

  describe('debounce', () => {
    jest.useFakeTimers();

    it('should debounce function calls', () => {
      const func = jest.fn();
      const debouncedFunc = debounce(func, 100);

      debouncedFunc();
      debouncedFunc();
      debouncedFunc();

      expect(func).not.toHaveBeenCalled();

      jest.advanceTimersByTime(100);

      expect(func).toHaveBeenCalledTimes(1);
    });
  });
});

// Mock日期工具函数
const dateUtils = {
    // 格式化日期
    formatDate: (date: Date | string | number, format: string = 'YYYY-MM-DD') => {
      const d = new Date(date);
      if (isNaN(d.getTime())) {
        throw new Error('无效的日期');
      }
  
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      const hours = String(d.getHours()).padStart(2, '0');
      const minutes = String(d.getMinutes()).padStart(2, '0');
      const seconds = String(d.getSeconds()).padStart(2, '0');
  
      return format
        .replace('YYYY', year.toString())
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hours)
        .replace('mm', minutes)
        .replace('ss', seconds);
    },
  
        // 相对时间
    getRelativeTime: (date: Date | string | number, mockNow?: Date) => {
      const d = new Date(date);
      const now = mockNow || new Date();
      const diffMs = now.getTime() - d.getTime();
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

      if (diffMinutes < 1) return '刚刚';
      if (diffMinutes < 60) return `${diffMinutes}分钟前`;
      if (diffHours < 24) return `${diffHours}小时前`;
      if (diffDays < 7) return `${diffDays}天前`;
      if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前`;
      if (diffDays < 365) return `${Math.floor(diffDays / 30)}个月前`;
      return `${Math.floor(diffDays / 365)}年前`;
    },
  
    // 计算年龄
    calculateAge: (birthDate: Date | string) => {
      const birth = new Date(birthDate);
      const today = new Date();
      
      if (birth > today) {
        throw new Error('出生日期不能晚于今天');
      }
  
      let age = today.getFullYear() - birth.getFullYear();
      const monthDiff = today.getMonth() - birth.getMonth();
      
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
      }
      
      return age;
    },
  
    // 添加时间
    addTime: (date: Date | string, amount: number, unit: 'days' | 'hours' | 'minutes' | 'seconds') => {
      const d = new Date(date);
      
      switch (unit) {
        case 'days':
          d.setDate(d.getDate() + amount);
          break;
        case 'hours':
          d.setHours(d.getHours() + amount);
          break;
        case 'minutes':
          d.setMinutes(d.getMinutes() + amount);
          break;
        case 'seconds':
          d.setSeconds(d.getSeconds() + amount);
          break;
        default:
          throw new Error('不支持的时间单位');
      }
      
      return d;
    },
  
    // 获取时间范围
    getTimeRange: (startDate: Date | string, endDate: Date | string) => {
      const start = new Date(startDate);
      const end = new Date(endDate);
      
      if (start > end) {
        throw new Error('开始时间不能晚于结束时间');
      }
  
      const diffMs = end.getTime() - start.getTime();
      const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  
      return { days, hours, minutes, totalMs: diffMs };
    },
  
    // 判断是否为今天
    isToday: (date: Date | string, mockNow?: Date) => {
      const d = new Date(date);
      const today = mockNow || new Date();
      
      return d.getDate() === today.getDate() &&
             d.getMonth() === today.getMonth() &&
             d.getFullYear() === today.getFullYear();
    },
  
    // 判断是否为本周
    isThisWeek: (date: Date | string, mockNow?: Date) => {
      const d = new Date(date);
      const today = mockNow || new Date();
      
      // 获取本周的开始和结束
      const startOfWeek = new Date(today);
      startOfWeek.setDate(today.getDate() - today.getDay());
      startOfWeek.setHours(0, 0, 0, 0);
      
      const endOfWeek = new Date(startOfWeek);
      endOfWeek.setDate(startOfWeek.getDate() + 6);
      endOfWeek.setHours(23, 59, 59, 999);
      
      return d >= startOfWeek && d <= endOfWeek;
    },
  
    // 获取月份天数
    getDaysInMonth: (year: number, month: number) => {
      return new Date(year, month, 0).getDate();
    },
  
    // 判断是否为闰年
    isLeapYear: (year: number) => {
      return (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
    },
  
    // 获取季度
    getQuarter: (date: Date | string) => {
      const d = new Date(date);
      const month = d.getMonth() + 1;
      return Math.ceil(month / 3);
    },
  
    // 时区转换
    convertTimezone: (date: Date | string, fromTz: string, toTz: string) => {
      // 简化的时区转换实现
      const d = new Date(date);
      const timezoneOffsets: Record<string, number> = {
        'UTC': 0,
        'GMT+8': 8,
        'EST': -5,
        'PST': -8,
      };
  
      const fromOffset = timezoneOffsets[fromTz] || 0;
      const toOffset = timezoneOffsets[toTz] || 0;
      const offsetDiff = (toOffset - fromOffset) * 60 * 60 * 1000;
  
      return new Date(d.getTime() + offsetDiff);
    },
  
    // 工作日计算
    getWorkdays: (startDate: Date | string, endDate: Date | string) => {
      const start = new Date(startDate);
      const end = new Date(endDate);
      let workdays = 0;
      
      const current = new Date(start);
      while (current <= end) {
        const dayOfWeek = current.getDay();
        if (dayOfWeek !== 0 && dayOfWeek !== 6) { // 不是周末
          workdays++;
        }
        current.setDate(current.getDate() + 1);
      }
      
      return workdays;
    },
  
    // 解析日期字符串
    parseDate: (dateString: string, format: string = 'YYYY-MM-DD') => {
      if (format === 'YYYY-MM-DD') {
        const match = dateString.match(/^(\d{4})-(\d{2})-(\d{2})$/);
        if (match) {
          const [, year, month, day] = match;
          return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
        }
      }
      
      if (format === 'DD/MM/YYYY') {
        const match = dateString.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
        if (match) {
          const [, day, month, year] = match;
          return new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
        }
      }
      
      throw new Error('无法解析日期字符串');
    },
  };
  
  describe('日期工具函数测试', () => {
    describe('formatDate', () => {
      const currentYear = new Date().getFullYear();
      
      it('应该格式化日期为默认格式', () => {
        const date = new Date(`${currentYear}-01-15T10:30:45`);
        const result = dateUtils.formatDate(date);
        expect(result).toBe(`${currentYear}-01-15`);
      });
  
      it('应该支持自定义格式', () => {
        const date = new Date(`${currentYear}-01-15T10:30:45`);
        const result = dateUtils.formatDate(date, 'YYYY-MM-DD HH:mm:ss');
        expect(result).toBe(`${currentYear}-01-15 10:30:45`);
      });
  
      it('应该处理字符串日期', () => {
        const result = dateUtils.formatDate(`${currentYear}-01-15`);
        expect(result).toBe(`${currentYear}-01-15`);
      });
  
      it('应该处理时间戳', () => {
        const timestamp = new Date(`${currentYear}-01-15`).getTime();
        const result = dateUtils.formatDate(timestamp);
        expect(result).toBe(`${currentYear}-01-15`);
      });
  
      it('应该拒绝无效日期', () => {
        expect(() => dateUtils.formatDate('invalid')).toThrow('无效的日期');
      });
    });
  
        describe('getRelativeTime', () => {
      // 使用固定的测试日期，避免年份变化导致的问题
      const mockNow = new Date('2024-01-15T12:00:00');
      
      beforeEach(() => {
        // Mock当前时间为固定值
        jest.spyOn(Date, 'now').mockReturnValue(mockNow.getTime());
      });

      afterEach(() => {
        jest.restoreAllMocks();
      });

      it('应该返回"刚刚"对于很近的时间', () => {
        const date = new Date('2024-01-15T11:59:30');
        const result = dateUtils.getRelativeTime(date, mockNow);
        expect(result).toBe('刚刚');
      });

      it('应该返回分钟前', () => {
        const date = new Date('2024-01-15T11:45:00');
        const result = dateUtils.getRelativeTime(date, mockNow);
        expect(result).toBe('15分钟前');
      });

      it('应该返回小时前', () => {
        const date = new Date('2024-01-15T10:00:00');
        const result = dateUtils.getRelativeTime(date, mockNow);
        expect(result).toBe('2小时前');
      });

      it('应该返回天前', () => {
        const date = new Date('2024-01-13T12:00:00');
        const result = dateUtils.getRelativeTime(date, mockNow);
        expect(result).toBe('2天前');
      });

      it('应该返回周前', () => {
        const date = new Date('2024-01-01T12:00:00');
        const result = dateUtils.getRelativeTime(date, mockNow);
        expect(result).toBe('2周前');
      });
    });
  
    describe('calculateAge', () => {
      const currentYear = new Date().getFullYear();
      const mockDate = new Date(`${currentYear}-01-15`);
      
      beforeEach(() => {
        // Mock当前时间为当前年份的1月15日
        jest.spyOn(Date, 'now').mockReturnValue(mockDate.getTime());
      });
  
      afterEach(() => {
        jest.restoreAllMocks();
      });
  
      it('应该正确计算年龄', () => {
        const birthDate = '1990-01-15';
        const age = dateUtils.calculateAge(birthDate);
        expect(age).toBe(currentYear - 1990);
      });
  
      it('应该处理生日未到的情况', () => {
        const birthDate = '1990-06-15';
        const age = dateUtils.calculateAge(birthDate);
        expect(age).toBe(currentYear - 1990 - 1);
      });
  
      it('应该拒绝未来的出生日期', () => {
        const futureDate = `${currentYear + 1}-01-15`;
        expect(() => dateUtils.calculateAge(futureDate)).toThrow('出生日期不能晚于今天');
      });
    });
  
    describe('addTime', () => {
      const currentYear = new Date().getFullYear();
      
      it('应该添加天数', () => {
        const date = new Date(`${currentYear}-01-15`);
        const result = dateUtils.addTime(date, 5, 'days');
        expect(dateUtils.formatDate(result)).toBe(`${currentYear}-01-20`);
      });
  
      it('应该添加小时', () => {
        const date = new Date(`${currentYear}-01-15T10:00:00`);
        const result = dateUtils.addTime(date, 3, 'hours');
        expect(result.getHours()).toBe(13);
      });
  
      it('应该添加分钟', () => {
        const date = new Date(`${currentYear}-01-15T10:30:00`);
        const result = dateUtils.addTime(date, 45, 'minutes');
        expect(result.getMinutes()).toBe(15);
        expect(result.getHours()).toBe(11);
      });
  
      it('应该拒绝不支持的时间单位', () => {
        const date = new Date(`${currentYear}-01-15`);
        expect(() => dateUtils.addTime(date, 1, 'years' as any)).toThrow('不支持的时间单位');
      });
    });
  
    describe('getTimeRange', () => {
      const currentYear = new Date().getFullYear();
      
      it('应该计算时间范围', () => {
        const start = `${currentYear}-01-15T10:00:00`;
        const end = `${currentYear}-01-17T14:30:00`;
        const range = dateUtils.getTimeRange(start, end);
        
        expect(range.days).toBe(2);
        expect(range.hours).toBe(4);
        expect(range.minutes).toBe(30);
      });
  
      it('应该拒绝无效的时间范围', () => {
        const start = `${currentYear}-01-17T10:00:00`;
        const end = `${currentYear}-01-15T10:00:00`;
        
        expect(() => dateUtils.getTimeRange(start, end)).toThrow('开始时间不能晚于结束时间');
      });
    });
  
    describe('isToday', () => {
      const mockNow = new Date('2024-01-15T12:00:00');
      
      beforeEach(() => {
        jest.spyOn(Date, 'now').mockReturnValue(mockNow.getTime());
      });
  
      afterEach(() => {
        jest.restoreAllMocks();
      });
  
            it('应该识别今天的日期', () => {
        const today = new Date('2024-01-15T08:30:00');
        expect(dateUtils.isToday(today, mockNow)).toBe(true);
      });

      it('应该识别不是今天的日期', () => {
        const yesterday = new Date('2024-01-14T12:00:00');
        expect(dateUtils.isToday(yesterday, mockNow)).toBe(false);
      });
    });
  
    describe('isThisWeek', () => {
      const mockNow = new Date('2024-01-15T12:00:00'); // 2024-01-15是周一
      
      beforeEach(() => {
        jest.spyOn(Date, 'now').mockReturnValue(mockNow.getTime());
      });
  
      afterEach(() => {
        jest.restoreAllMocks();
      });
  
            it('应该识别本周的日期', () => {
        const thisWeek = new Date('2024-01-17T12:00:00'); // 周三
        expect(dateUtils.isThisWeek(thisWeek, mockNow)).toBe(true);
      });

      it('应该识别不是本周的日期', () => {
        const lastWeek = new Date('2024-01-07T12:00:00');
        expect(dateUtils.isThisWeek(lastWeek, mockNow)).toBe(false);
      });
    });
  
    describe('getDaysInMonth', () => {
      it('应该返回正确的月份天数', () => {
        expect(dateUtils.getDaysInMonth(2024, 1)).toBe(31); // 1月
        expect(dateUtils.getDaysInMonth(2024, 2)).toBe(29); // 2月（闰年）
        expect(dateUtils.getDaysInMonth(2023, 2)).toBe(28); // 2月（平年）
        expect(dateUtils.getDaysInMonth(2024, 4)).toBe(30); // 4月
      });
    });
  
    describe('isLeapYear', () => {
      it('应该识别闰年', () => {
        expect(dateUtils.isLeapYear(2024)).toBe(true);
        expect(dateUtils.isLeapYear(2000)).toBe(true);
        expect(dateUtils.isLeapYear(1600)).toBe(true);
      });
  
      it('应该识别平年', () => {
        expect(dateUtils.isLeapYear(2023)).toBe(false);
        expect(dateUtils.isLeapYear(1900)).toBe(false);
        expect(dateUtils.isLeapYear(2100)).toBe(false);
      });
    });
  
    describe('getQuarter', () => {
      const currentYear = new Date().getFullYear();
      
      it('应该返回正确的季度', () => {
        expect(dateUtils.getQuarter(`${currentYear}-01-15`)).toBe(1);
        expect(dateUtils.getQuarter(`${currentYear}-04-15`)).toBe(2);
        expect(dateUtils.getQuarter(`${currentYear}-07-15`)).toBe(3);
        expect(dateUtils.getQuarter(`${currentYear}-10-15`)).toBe(4);
      });
    });
  
    describe('convertTimezone', () => {
      const currentYear = new Date().getFullYear();
      
      it('应该转换时区', () => {
        const date = new Date(`${currentYear}-01-15T12:00:00`);
        const result = dateUtils.convertTimezone(date, 'UTC', 'GMT+8');
        
        expect(result.getHours()).toBe(20); // UTC 12:00 -> GMT+8 20:00
      });
  
      it('应该处理相同时区', () => {
        const date = new Date(`${currentYear}-01-15T12:00:00`);
        const result = dateUtils.convertTimezone(date, 'UTC', 'UTC');
        
        expect(result.getTime()).toBe(date.getTime());
      });
    });
  
    describe('getWorkdays', () => {
      it('应该计算工作日数量', () => {
        // 2024-01-15是周一，2024-01-19是周五
        const workdays = dateUtils.getWorkdays('2024-01-15', '2024-01-19');
        expect(workdays).toBe(5);
      });
  
      it('应该排除周末', () => {
        // 包含一个完整的周
        const workdays = dateUtils.getWorkdays('2024-01-15', '2024-01-21');
        expect(workdays).toBe(5); // 周一到周五
      });
    });
  
    describe('parseDate', () => {
      const currentYear = new Date().getFullYear();
      
      it('应该解析YYYY-MM-DD格式', () => {
        const result = dateUtils.parseDate(`${currentYear}-01-15`);
        expect(result.getFullYear()).toBe(currentYear);
        expect(result.getMonth()).toBe(0); // 0-based
        expect(result.getDate()).toBe(15);
      });
  
      it('应该解析DD/MM/YYYY格式', () => {
        const result = dateUtils.parseDate(`15/01/${currentYear}`, 'DD/MM/YYYY');
        expect(result.getFullYear()).toBe(currentYear);
        expect(result.getMonth()).toBe(0);
        expect(result.getDate()).toBe(15);
      });
  
      it('应该拒绝无效格式', () => {
        expect(() => dateUtils.parseDate('invalid-date')).toThrow('无法解析日期字符串');
      });
    });
  });
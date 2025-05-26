// Mock格式化工具函数
const formatUtils = {
  formatDate: (date: Date | string, format?: string): string => {
    const d = new Date(date);
    if (format === 'YYYY-MM-DD') {
      return d.toISOString().split('T')[0];
    }
    if (format === 'MM-DD') {
      const month = (d.getMonth() + 1).toString().padStart(2, '0');
      const day = d.getDate().toString().padStart(2, '0');
      return `${month}-${day}`;
    }
    return d.toLocaleDateString('zh-CN');
  },

  formatTime: (date: Date | string): string => {
    const d = new Date(date);
    return d.toLocaleTimeString('zh-CN', { hour12: false });
  },

  formatNumber: (num: number, decimals: number = 0): string => {
    return num.toFixed(decimals);
  },

  formatCurrency: (amount: number): string => {
    return `¥${amount.toFixed(2)}`;
  },

  formatPercentage: (value: number, total: number): string => {
    const percentage = (value / total) * 100;
    return `${percentage.toFixed(1)}%`;
  },

  formatFileSize: (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
  },

  formatPhoneNumber: (phone: string): string => {
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 11) {
      return `${cleaned.slice(0, 3)} ${cleaned.slice(3, 7)} ${cleaned.slice(7)}`;
    }
    if (cleaned.length === 13 && cleaned.startsWith('86')) {
      // 处理+86开头的号码
      const number = cleaned.slice(2);
      return `${number.slice(0, 3)} ${number.slice(3, 7)} ${number.slice(7)}`;
    }
    return phone;
  },

  formatHealthScore: (score: number): string => {
    if (score >= 90) return '优秀';
    if (score >= 80) return '良好';
    if (score >= 70) return '一般';
    if (score >= 60) return '较差';
    return '差';
  },

  formatDuration: (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes}分钟`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    if (remainingMinutes === 0) {
      return `${hours}小时`;
    }
    return `${hours}小时${remainingMinutes}分钟`;
  },

  formatRelativeTime: (date: Date | string): string => {
    const now = Date.now();
    const target = new Date(date).getTime();
    const diffMs = now - target;
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMinutes < 1) return '刚刚';
    if (diffMinutes < 60) return `${diffMinutes}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    if (diffDays < 7) return `${diffDays}天前`;
    return formatUtils.formatDate(date);
  },
};

describe('FormatUtils', () => {
  describe('日期格式化', () => {
    it('应该正确格式化日期为YYYY-MM-DD', () => {
      const date = new Date('2024-01-15T10:30:00');
      const result = formatUtils.formatDate(date, 'YYYY-MM-DD');
      expect(result).toBe('2024-01-15');
    });

    it('应该正确格式化日期为MM-DD', () => {
      const date = new Date('2024-01-15T10:30:00');
      const result = formatUtils.formatDate(date, 'MM-DD');
      expect(result).toBe('01-15');
    });

    it('应该正确格式化为本地日期', () => {
      const date = new Date('2024-01-15T10:30:00');
      const result = formatUtils.formatDate(date);
      expect(result).toMatch(/2024/);
    });

    it('应该处理字符串日期', () => {
      const result = formatUtils.formatDate('2024-01-15', 'YYYY-MM-DD');
      expect(result).toBe('2024-01-15');
    });
  });

  describe('时间格式化', () => {
    it('应该正确格式化时间', () => {
      const date = new Date('2024-01-15T10:30:00');
      const result = formatUtils.formatTime(date);
      expect(result).toMatch(/10:30:00/);
    });
  });

  describe('数字格式化', () => {
    it('应该正确格式化整数', () => {
      const result = formatUtils.formatNumber(123);
      expect(result).toBe('123');
    });

    it('应该正确格式化小数', () => {
      const result = formatUtils.formatNumber(123.456, 2);
      expect(result).toBe('123.46');
    });

    it('应该处理零值', () => {
      const result = formatUtils.formatNumber(0, 2);
      expect(result).toBe('0.00');
    });
  });

  describe('货币格式化', () => {
    it('应该正确格式化货币', () => {
      const result = formatUtils.formatCurrency(123.45);
      expect(result).toBe('¥123.45');
    });

    it('应该处理整数金额', () => {
      const result = formatUtils.formatCurrency(100);
      expect(result).toBe('¥100.00');
    });

    it('应该处理零金额', () => {
      const result = formatUtils.formatCurrency(0);
      expect(result).toBe('¥0.00');
    });
  });

  describe('百分比格式化', () => {
    it('应该正确计算百分比', () => {
      const result = formatUtils.formatPercentage(25, 100);
      expect(result).toBe('25.0%');
    });

    it('应该处理小数百分比', () => {
      const result = formatUtils.formatPercentage(1, 3);
      expect(result).toBe('33.3%');
    });

    it('应该处理零值', () => {
      const result = formatUtils.formatPercentage(0, 100);
      expect(result).toBe('0.0%');
    });

    it('应该处理100%', () => {
      const result = formatUtils.formatPercentage(100, 100);
      expect(result).toBe('100.0%');
    });
  });

  describe('文件大小格式化', () => {
    it('应该格式化字节', () => {
      const result = formatUtils.formatFileSize(512);
      expect(result).toBe('512.0 B');
    });

    it('应该格式化KB', () => {
      const result = formatUtils.formatFileSize(1536);
      expect(result).toBe('1.5 KB');
    });

    it('应该格式化MB', () => {
      const result = formatUtils.formatFileSize(1572864);
      expect(result).toBe('1.5 MB');
    });

    it('应该格式化GB', () => {
      const result = formatUtils.formatFileSize(1610612736);
      expect(result).toBe('1.5 GB');
    });

    it('应该处理零字节', () => {
      const result = formatUtils.formatFileSize(0);
      expect(result).toBe('0 B');
    });
  });

  describe('手机号格式化', () => {
    it('应该正确格式化11位手机号', () => {
      const result = formatUtils.formatPhoneNumber('13800138000');
      expect(result).toBe('138 0013 8000');
    });

    it('应该处理带符号的手机号', () => {
      const result = formatUtils.formatPhoneNumber('+86-138-0013-8000');
      expect(result).toBe('138 0013 8000');
    });

    it('应该保持非11位号码不变', () => {
      const result = formatUtils.formatPhoneNumber('12345');
      expect(result).toBe('12345');
    });
  });

  describe('健康分数格式化', () => {
    it('应该返回优秀', () => {
      expect(formatUtils.formatHealthScore(95)).toBe('优秀');
      expect(formatUtils.formatHealthScore(90)).toBe('优秀');
    });

    it('应该返回良好', () => {
      expect(formatUtils.formatHealthScore(85)).toBe('良好');
      expect(formatUtils.formatHealthScore(80)).toBe('良好');
    });

    it('应该返回一般', () => {
      expect(formatUtils.formatHealthScore(75)).toBe('一般');
      expect(formatUtils.formatHealthScore(70)).toBe('一般');
    });

    it('应该返回较差', () => {
      expect(formatUtils.formatHealthScore(65)).toBe('较差');
      expect(formatUtils.formatHealthScore(60)).toBe('较差');
    });

    it('应该返回差', () => {
      expect(formatUtils.formatHealthScore(55)).toBe('差');
      expect(formatUtils.formatHealthScore(30)).toBe('差');
    });
  });

  describe('时长格式化', () => {
    it('应该格式化分钟', () => {
      expect(formatUtils.formatDuration(30)).toBe('30分钟');
      expect(formatUtils.formatDuration(59)).toBe('59分钟');
    });

    it('应该格式化整小时', () => {
      expect(formatUtils.formatDuration(60)).toBe('1小时');
      expect(formatUtils.formatDuration(120)).toBe('2小时');
    });

    it('应该格式化小时和分钟', () => {
      expect(formatUtils.formatDuration(90)).toBe('1小时30分钟');
      expect(formatUtils.formatDuration(125)).toBe('2小时5分钟');
    });

    it('应该处理零分钟', () => {
      expect(formatUtils.formatDuration(0)).toBe('0分钟');
    });
  });

  describe('相对时间格式化', () => {
    beforeEach(() => {
      // Mock Date.now to return a fixed time
      jest.spyOn(Date, 'now').mockReturnValue(new Date('2024-01-15T12:00:00').getTime());
    });

    afterEach(() => {
      jest.restoreAllMocks();
    });

    it('应该返回刚刚', () => {
      const date = new Date('2024-01-15T11:59:30');
      const result = formatUtils.formatRelativeTime(date);
      expect(result).toBe('刚刚');
    });

    it('应该返回分钟前', () => {
      const date = new Date('2024-01-15T11:55:00');
      const result = formatUtils.formatRelativeTime(date);
      expect(result).toBe('5分钟前');
    });

    it('应该返回小时前', () => {
      const date = new Date('2024-01-15T10:00:00');
      const result = formatUtils.formatRelativeTime(date);
      expect(result).toBe('2小时前');
    });

    it('应该返回天前', () => {
      const date = new Date('2024-01-14T12:00:00');
      const result = formatUtils.formatRelativeTime(date);
      expect(result).toBe('1天前');
    });

    it('应该返回格式化日期（超过7天）', () => {
      const date = new Date('2024-01-01T12:00:00');
      const result = formatUtils.formatRelativeTime(date);
      expect(result).toMatch(/2024/);
    });
  });
}); 
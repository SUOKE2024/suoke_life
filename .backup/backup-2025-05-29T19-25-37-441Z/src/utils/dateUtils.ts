/**
 * 日期和时间处理工具
 */

/**
 * 格式化日期
 */
export const formatDate = (
  date: Date | string | number,
  format: string = 'YYYY-MM-DD'
): string => {
  let d: Date;
  
  if (typeof date === 'string') {
    d = new Date(date);
  } else if (typeof date === 'number') {
    d = new Date(date);
  } else {
    d = date;
  }

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
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
};

/**
 * 格式化时间戳为相对时间
 */
export const formatRelativeTime = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInMs = now.getTime() - d.getTime();
  const diffInSeconds = Math.floor(diffInMs / 1000);
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  const diffInHours = Math.floor(diffInMinutes / 60);
  const diffInDays = Math.floor(diffInHours / 24);

  if (diffInSeconds < 60) {
    return '刚刚';
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}分钟前`;
  } else if (diffInHours < 24) {
    return `${diffInHours}小时前`;
  } else if (diffInDays < 7) {
    return `${diffInDays}天前`;
  } else {
    return formatDate(d, 'MM-DD');
  }
};

/**
 * 获取相对时间（别名）
 */
export const getRelativeTime = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffInMs = now.getTime() - d.getTime();
  const diffInSeconds = Math.floor(diffInMs / 1000);
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  const diffInHours = Math.floor(diffInMinutes / 60);
  const diffInDays = Math.floor(diffInHours / 24);
  const diffInWeeks = Math.floor(diffInDays / 7);

  if (diffInSeconds < 60) {
    return '刚刚';
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}分钟前`;
  } else if (diffInHours < 24) {
    return `${diffInHours}小时前`;
  } else if (diffInDays < 7) {
    return `${diffInDays}天前`;
  } else if (diffInWeeks < 4) {
    return `${diffInWeeks}周前`;
  } else {
    return formatDate(d, 'MM-DD');
  }
};

/**
 * 计算年龄
 */
export const calculateAge = (birthDate: Date | string): number => {
  const birth = typeof birthDate === 'string' ? new Date(birthDate) : birthDate;
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
};

/**
 * 判断是否是同一天
 */
export const isSameDay = (
  date1: Date | string,
  date2: Date | string
): boolean => {
  const d1 = typeof date1 === 'string' ? new Date(date1) : date1;
  const d2 = typeof date2 === 'string' ? new Date(date2) : date2;

  return (
    d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate()
  );
};

/**
 * 判断是否是今天
 */
export const isToday = (date: Date | string): boolean => {
  const d = typeof date === 'string' ? new Date(date) : date;
  const today = new Date();
  return isSameDay(d, today);
};

/**
 * 判断是否是本周
 */
export const isThisWeek = (date: Date | string): boolean => {
  const d = typeof date === 'string' ? new Date(date) : date;
  const today = new Date();
  
  // 获取本周的开始（周一）
  const startOfWeek = new Date(today);
  const dayOfWeek = today.getDay();
  const daysToMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1; // 周日是0，需要特殊处理
  startOfWeek.setDate(today.getDate() - daysToMonday);
  startOfWeek.setHours(0, 0, 0, 0);
  
  // 获取本周的结束（周日）
  const endOfWeek = new Date(startOfWeek);
  endOfWeek.setDate(startOfWeek.getDate() + 6);
  endOfWeek.setHours(23, 59, 59, 999);
  
  return d >= startOfWeek && d <= endOfWeek;
};

/**
 * 添加时间
 */
export const addTime = (
  date: Date,
  amount: number,
  unit: 'days' | 'hours' | 'minutes'
): Date => {
  const result = new Date(date);
  
  switch (unit) {
    case 'days':
      result.setDate(result.getDate() + amount);
      break;
    case 'hours':
      result.setHours(result.getHours() + amount);
      break;
    case 'minutes':
      result.setMinutes(result.getMinutes() + amount);
      break;
    default:
      throw new Error('不支持的时间单位');
  }
  
  return result;
};

/**
 * 获取时间范围
 */
export const getTimeRange = (start: string, end: string) => {
  const startDate = new Date(start);
  const endDate = new Date(end);
  
  if (startDate > endDate) {
    throw new Error('开始时间不能晚于结束时间');
  }
  
  const diffInMs = endDate.getTime() - startDate.getTime();
  const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
  const diffInHours = Math.floor(diffInMinutes / 60);
  const diffInDays = Math.floor(diffInHours / 24);
  
  return {
    days: diffInDays,
    hours: diffInHours % 24,
    minutes: diffInMinutes % 60,
  };
};

/**
 * 获取月份天数
 */
export const getDaysInMonth = (year: number, month: number): number => {
  return new Date(year, month, 0).getDate();
};

/**
 * 判断是否是闰年
 */
export const isLeapYear = (year: number): boolean => {
  return (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
};

/**
 * 获取季度
 */
export const getQuarter = (date: string): number => {
  const d = new Date(date);
  const month = d.getMonth() + 1; // getMonth() 返回 0-11
  return Math.ceil(month / 3);
};

/**
 * 转换时区
 */
export const convertTimezone = (
  date: Date,
  fromTimezone: string,
  toTimezone: string
): Date => {
  // 简化实现，仅处理UTC和GMT+8的转换
  if (fromTimezone === toTimezone) {
    return new Date(date);
  }
  
  const result = new Date(date);
  
  if (fromTimezone === 'UTC' && toTimezone === 'GMT+8') {
    result.setHours(result.getHours() + 8);
  } else if (fromTimezone === 'GMT+8' && toTimezone === 'UTC') {
    result.setHours(result.getHours() - 8);
  }
  
  return result;
};

/**
 * 计算工作日数量
 */
export const getWorkdays = (start: string, end: string): number => {
  const startDate = new Date(start);
  const endDate = new Date(end);
  let workdays = 0;
  
  const current = new Date(startDate);
  while (current <= endDate) {
    const dayOfWeek = current.getDay();
    // 周一到周五是工作日（1-5）
    if (dayOfWeek >= 1 && dayOfWeek <= 5) {
      workdays++;
    }
    current.setDate(current.getDate() + 1);
  }
  
  return workdays;
};

/**
 * 解析日期字符串
 */
export const parseDate = (
  dateString: string,
  format: string = 'YYYY-MM-DD'
): Date => {
  if (format === 'YYYY-MM-DD') {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      throw new Error('无法解析日期字符串');
    }
    return date;
  } else if (format === 'DD/MM/YYYY') {
    const parts = dateString.split('/');
    if (parts.length !== 3) {
      throw new Error('无法解析日期字符串');
    }
    const date = new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));
    if (isNaN(date.getTime())) {
      throw new Error('无法解析日期字符串');
    }
    return date;
  } else {
    throw new Error('无法解析日期字符串');
  }
};

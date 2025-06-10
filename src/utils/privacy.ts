// 隐私保护工具 - 索克生活APP;
export function maskPhone(phone: string): string {
  if (!phone) return '';
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
}
export function maskIdCard(id: string): string {
  if (!id) return '';
  return id.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2');
}
export function maskName(name: string): string {
  if (!name) return '';
  return name[0] + '*'.repeat(name.length - 1);
}
export function maskSensitiveData(data: any): any {
  if (typeof data === 'string') {
    return data;
  }
  if (typeof data === 'object' && data !== null) {
    const masked = { ...data };
    Object.keys(masked).forEach((key) => {
      if (typeof masked[key] === 'string') {
        if (/phone|mobile/i.test(key)) {
          masked[key] = maskPhone(masked[key]);
        } else if (/id(card)?/i.test(key)) {
          masked[key] = maskIdCard(masked[key]);
        } else if (/name/i.test(key)) {
          masked[key] = maskName(masked[key]);
        }
      }
    });
    return masked;
  }
  return data;
}
export function sanitizeLogData(...args: any[]): any[] {
  return args.map((arg) => {
    try {
      return JSON.parse(
        JSON.stringify(arg, (key, value) => {
          return maskSensitiveData(value);
        })
      );
    } catch {
      return arg;
    }
  });
}
export default {
  maskPhone,
  maskIdCard,
  maskName,
  maskSensitiveData,
  sanitizeLogData,
};

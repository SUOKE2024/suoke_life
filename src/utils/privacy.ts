// 敏感信息脱敏工具
export function maskPhone(phone: string): string {
  if (!phone) return "";
  return phone.replace(/(\d{3})\d{4}(\d{4})/, "$1****$2");
}

export function maskIdCard(id: string): string {
  if (!id) return "";
  return id.replace(/(\d{4})\d{10}(\w{4})/, "$1**********$2");
}

export function maskName(name: string): string {
  if (!name) return "";
  if (name.length <= 1) return "*";
  return name[0] + "*".repeat(name.length - 1);
}

// 日志拦截，自动脱敏敏感字段
export function safeLog(...args: any[]) {
  const replacer = (key: string, value: any) => {
    if (typeof value === "string") {
      if (/phone|mobile/i.test(key)) return maskPhone(value);
      if (/id(card)?/i.test(key)) return maskIdCard(value);
      if (/name/i.test(key)) return maskName(value);
    }
    return value;
  };
  const safeArgs = args.map((arg) => {
    if (typeof arg === "object") {
      try {
        return JSON.parse(JSON.stringify(arg, replacer));
      } catch {
        return arg;
      }
    }
    return arg;
  });
  // eslint-disable-next-line no-console
  console.log(...safeArgs);
}

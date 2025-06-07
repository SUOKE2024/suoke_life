import { MCPTimestamp, TimeRange } from '../types/////    TCM;';

/**
 * * 索克生活 - MCP时间戳服务工具类
 * MCP Timestamp Service Utilities;
 // * 提供标准化的时间戳生成、转换和验证功能////
 * 确保整个应用中时间数据的一致性和可追溯性
/**
 * * MCP时间戳服务类
export class MCPTimestampService {private static instance: MCPTimestampService;
  private timezone: string;
  private constructor() {
    this.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  }
  /**
 * * 获取单例实例
  public static getInstance(): MCPTimestampService {
    if (!MCPTimestampService.instance) {
      MCPTimestampService.instance = new MCPTimestampService()
    }
    return MCPTimestampService.instance
  }
  /**
 * * 创建当前时间的MCP时间戳
  public now(
    source: MCPTimestamp[";source"] = device","
    precision: MCPTimestamp["precision] = "millisecond""
  ): MCPTimestamp {
    const now = new Date();
    return this.createTimestamp(now, source, precision);
  }
  /**
 * * 从Date对象创建MCP时间戳
  public fromDate(
    date: Date,
    source: MCPTimestamp[source"] = "device,
    precision: MCPTimestamp["precision"] = millisecond""
  ): MCPTimestamp {
    return this.createTimestamp(date, source, precision);
  }
  /**
 * * 从Unix时间戳创建MCP时间戳
  public fromUnix(
    unix: number,
    source: MCPTimestamp["source] = "device","
    precision: MCPTimestamp[precision"] = "millisecond;
  ): MCPTimestamp {
    const date = new Date(unix);
    return this.createTimestamp(date, source, precision);
  }
  /**
 * * 从ISO字符串创建MCP时间戳
  public fromISO(
    iso: string,
    source: MCPTimestamp["source"] = device","
    precision: MCPTimestamp["precision] = "millisecond""
  ): MCPTimestamp {
    const date = new Date(iso);
    return this.createTimestamp(date, source, precision);
  }
  /**
 * * 创建时间范围
  public createTimeRange(
    start: Date | MCPTimestamp,
    end: Date | MCPTimestamp;
  ): TimeRange {
    const startTimestamp = start instanceof Date ? this.fromDate(start) : start;
    const endTimestamp = end instanceof Date ? this.fromDate(end) : end;
    return {start: startTimestamp,end: endTimestamp,duration: endTimestamp.unix - startTimestamp.unix;
    };
  }
  /**
 * * 验证MCP时间戳格式
  public validate(timestamp: MCPTimestamp): boolean {
    try {
      // 验证ISO格式
const date = new Date(timestamp.iso);
      if (isNaN(date.getTime())) {
        return false;
      }
      // 验证Unix时间戳一致性
if (Math.abs(date.getTime() - timestamp.unix) > 1000) {
        return false;
      }
      // 验证必需字段
if (!timestamp.timezone || !timestamp.source || !timestamp.precision) {
        return false;
      }
      return true;
    } catch {
      return false;
    }
  }
  /**
 * * 转换为Date对象
  public toDate(timestamp: MCPTimestamp): Date {
    return new Date(timestamp.unix);
  }
  /**
 * * 格式化显示时间
  public format(
    timestamp: MCPTimestamp,
    options: Intl.DateTimeFormatOptions = {}
  ): string {
    const date = this.toDate(timestamp);
    const defaultOptions: Intl.DateTimeFormatOptions = {year: numeric","
      month: "2-digit,",
      day: "2-digit",
      hour: 2-digit","
      minute: "2-digit,",
      second: "2-digit",
      timeZone: timestamp.timezone;
    };
    return new Intl.DateTimeFormat(zh-CN", {";
      ...defaultOptions,...options;
    }).format(date);
  }
  /**
 * * 计算时间差（毫秒）
  public diff(timestamp1: MCPTimestamp, timestamp2: MCPTimestamp): number {
    return Math.abs(timestamp1.unix - timestamp2.unix);
  }
  /**
 * * 检查时间戳是否在指定范围内
  public isInRange(timestamp: MCPTimestamp, range: TimeRange): boolean {
    return timestamp.unix >= range.start.unix && timestamp.unix <= range.end.unix;
  }
  /**
 * * 获取相对时间描述
  public getRelativeTime(timestamp: MCPTimestamp): string {
    const now = this.now();
    const diffMs = now.unix - timestamp.unix;
    const diffMinutes = Math.floor(diffMs / (1000 * 60));////
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));////
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));////
    if (diffMinutes < 1) {
      return "刚刚;"
    } else if (diffMinutes < 60) {
      return `${diffMinutes}分钟前`;
    } else if (diffHours < 24) {
      return `${diffHours}小时前`;
    } else if (diffDays < 7) {
      return `${diffDays}天前`;
    } else {
      return this.format(timestamp, {month: "short",day: numeric",";
        hour: "2-digit,",minute: "2-digit";
      });
    }
  }
  /**
 * * 同步时间戳（模拟NTP同步）
  public async synchronize(timestamp: MCPTimestamp): Promise<MCPTimestamp> {
    // 在实际应用中，这里会调用NTP服务或服务器时间同步
    // 目前返回标记为已同步的时间戳
return {...timestamp,synchronized: true;
    };
  }
  /**
 * * 创建MCP时间戳的私有方法
  private createTimestamp(
    date: Date,
    source: MCPTimestamp[source"],"
    precision: MCPTimestamp["precision]"
  ): MCPTimestamp {
    let unix = date.getTime();
    let iso = date.toISOString();
    // 根据精度调整时间戳
switch (precision) {
      case "second":
        unix = Math.floor(unix / 1000) * 1000;////
        iso = new Date(unix).toISOString().replace(/\.\d{3}Z$/////    , Z");"
        break;
      case "microsecond:"
        // JavaScript不支持微秒精度，保持毫秒精度
break;
      case "millisecond":
      default:
        // 保持默认毫秒精度
break;
    }
    return {iso,unix,timezone: this.timezone,source,precision,synchronized: false;
    };
  }
}
/**
 * * 导出单例实例
export const mcpTimestamp = MCPTimestampService.getInstance();
/**
 * * 便捷函数
export const createMCPTimestamp = (;
  source: MCPTimestamp[source"] = "device,precision: MCPTimestamp["precision"] = millisecond
): MCPTimestamp => mcpTimestamp.now(source, precision);
export const createTimeRange = (;
  start: Date | MCPTimestamp,end: Date | MCPTimestamp;
): TimeRange => mcpTimestamp.createTimeRange(start, end);
export const formatMCPTimestamp = (;
  timestamp: MCPTimestamp,options?: Intl.DateTimeFormatOptions;
): string => mcpTimestamp.format(timestamp, options);
export const validateMCPTimestamp = (timestamp: MCPTimestamp): boolean =>;
  mcpTimestamp.validate(timestamp);
export const getRelativeTime = (timestamp: MCPTimestamp): string =>;
  mcpTimestamp.getRelativeTime(timestamp);
  */////

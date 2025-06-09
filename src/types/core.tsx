import React from "react";
// 核心类型定义   索克生活APP - 架构优化
// 基础类型 * export interface BaseEntity {
  //
}
id: string}
  createdAt: Date,updatedAt: Date};
///     > { success: boolean;
* data?: T;
  message?: string;
  error?: string;
  code?: number}
// 分页类型 * export interface PaginationParams {
  //
}
page: number};
  limit: number;
  sortBy?: string;
  sortOrder?: "asc" | "desc"}
export interface PaginatedResponse<T> { items: T[],
  total: number,
  page: number,
  limit: number,
  totalPages: number}
// 智能体类型 * export interface AgentConfig {
  //
}
id: string}
  name: string,enabled: boolean,model: string;
  maxTokens?: number;
  temperature?: number}
// 健康数据类型 * export interface HealthMetric {
  //
}
id: string}
  type: string,
  value: number,
  unit: string,
  timestamp: Date,
  source: string}
// 诊断类型 * export interface DiagnosisResult {
  //
}
id: string}
  type: "looking" | "listening" | "asking" | "touching" | "pulse",
  confidence: number,
  findings: string[],
  recommendations: string[],
  timestamp: Date}
//  ;
  email: string;
  avatar?: string,
  preferences: UserPreferences,
  healthProfile: HealthProfile}
export interface UserPreferences {
}
language: string}
  theme: "light" | "dark" | "auto",
  notifications: boolean,
  accessibility: AccessibilitySettings}
export interface HealthProfile {
}
age: number}
  gender: "male" | "female" | "other",height: number,weight: number;
  bloodType?: string;
  allergies: string[],
  medications: string[],
  conditions: string[]
  }
export interface AccessibilitySettings {
}
fontSize: "small" | "medium" | "large"}
  highContrast: boolean,
  screenReader: boolean,
  voiceControl: boolean}
// 服务类型 * export interface ServiceStatus {
  //
}
name: string};
  status: "online" | "offline" | "error",lastCheck: Date;
  responseTime?: number;
  error?: string}
// 缓存类型 * export interface CacheConfig {
  //
}
ttl: number}
  maxSize: number,
  strategy: "lru" | "fifo" | "lfu"}
// 性能监控类型 * export interface PerformanceMetric {
  //
}
}
/
  name: string,
  value: number,unit: string,timestamp: Date;
  tags?: Record<string, string>;
}
// 错误类型 * export interface ErrorInfo {
  //
}
}
/  ;
  type: string,message: string;
  stack?: string;
  context?: Record<string, any>;
  timestamp: Date}
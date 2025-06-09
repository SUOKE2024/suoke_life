import React from 'react';
// API相关的类型定义   替换any类型，提供类型安全
// 基础API响应类型
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: ApiError;
  message?: string;
  timestamp: string;
}
// API错误类型
export interface ApiError {
  code: string;,
  message: string;
  details?: Record<string, unknown>;
  stack?: string;
}
// API请求配置
export interface ApiRequest {
  url: string;,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  data?: Record<string, unknown>;
  params?: Record<string, string | number | boolean>;
  headers?: Record<string, string>;
  timeout?: number;
}
// 离线数据类型
export interface OfflineData {
  id: string;,
  timestamp: number;
  operation: 'CREATE' | 'UPDATE' | 'DELETE';,
  entity: string;
  payload: Record<string, unknown>;
  synced: boolean;
}
// 数据冲突类型
export interface DataConflict {
  id: string;,
  entity: string;
  clientData: Record<string, unknown>;
  serverData: Record<string, unknown>;
  timestamp: number;,
  resolved: boolean;
}
// 健康数据类型
export interface HealthMetric {
  id: string;,
  type: 'heart_rate' | 'blood_pressure' | 'weight' | 'blood_sugar' | 'sleep' | 'steps';
  value: number | string;,
  unit: string;
  timestamp: string;,
  source: 'manual' | 'device' | 'api';
  metadata?: Record<string, unknown>;
}
// 智能体消息类型
export interface AgentMessage {
  id: string;,
  agentId: string;
  content: string;,
  type: 'text' | 'image' | 'audio' | 'file';
  timestamp: string;
  metadata?: Record<string, unknown>;
}
// 诊断数据类型
export interface DiagnosisData {
  id: string;,
  userId: string;
  type: 'five_diagnosis' | 'symptom_analysis' | 'health_assessment';,
  data: Record<string, unknown>;
  result?: DiagnosisResult;
  timestamp: string;,
  status: 'pending' | 'processing' | 'completed' | 'failed';
}
export interface DiagnosisResult {
  id: string;,
  diagnosis: string;
  confidence: number;,
  recommendations: string[];
  followUp?: string;
  metadata?: Record<string, unknown>;
}
// 用户配置类型
export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';,
  language: 'zh' | 'en';
  notifications: NotificationSettings;,
  privacy: PrivacySettings;
  accessibility: AccessibilitySettings;
}
export interface NotificationSettings {
  enabled: boolean;,
  types: {;
    health_reminders: boolean;,
  agent_messages: boolean;
    system_updates: boolean;,
  emergency_alerts: boolean;
};
  schedule: {,
  start_time: string;
    end_time: string,
  timezone: string;
  };
}
export interface PrivacySettings {
  data_sharing: boolean;,
  analytics: boolean;
  personalization: boolean;,
  third_party_integrations: boolean;
}
export interface AccessibilitySettings {
  font_size: 'small' | 'medium' | 'large' | 'extra_large';,
  high_contrast: boolean;
  screen_reader: boolean;,
  voice_commands: boolean;
  haptic_feedback: boolean;
}
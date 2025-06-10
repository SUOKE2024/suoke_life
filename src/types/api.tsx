';'';
// API相关的类型定义   替换any类型，提供类型安全/;/g/;
// 基础API响应类型/;,/g/;
export interface ApiResponse<T = unknown> {;,}const success = boolean;
data?: T;
error?: ApiError;
message?: string;
}
  const timestamp = string;}
}
// API错误类型/;,/g/;
export interface ApiError {code: string}const message = string;
details?: Record<string; unknown>;
}
}
  stack?: string;}
}
// API请求配置/;,/g/;
export interface ApiRequest {';,}url: string,';,'';
const method = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';';,'';
data?: Record<string; unknown>;
params?: Record<string; string | number | boolean>;
headers?: Record<string; string>;
}
}
  timeout?: number;}
}
// 离线数据类型/;,/g/;
export interface OfflineData {id: string,';,}timestamp: number,';,'';
operation: 'CREATE' | 'UPDATE' | 'DELETE';','';
entity: string,;
payload: Record<string, unknown>;
}
}
  const synced = boolean;}
}
// 数据冲突类型/;,/g/;
export interface DataConflict {id: string}entity: string,;
clientData: Record<string, unknown>;
serverData: Record<string, unknown>;
timestamp: number,;
}
}
  const resolved = boolean;}
}
// 健康数据类型/;,/g/;
export interface HealthMetric {';,}id: string,';,'';
type: 'heart_rate' | 'blood_pressure' | 'weight' | 'blood_sugar' | 'sleep' | 'steps';','';
value: number | string,;
unit: string,';,'';
timestamp: string,';,'';
const source = 'manual' | 'device' | 'api';';'';
}
}
  metadata?: Record<string; unknown>;}
}
// 智能体消息类型/;,/g/;
export interface AgentMessage {id: string}agentId: string,';,'';
content: string,';,'';
type: 'text' | 'image' | 'audio' | 'file';','';
const timestamp = string;
}
}
  metadata?: Record<string; unknown>;}
}
// 诊断数据类型/;,/g/;
export interface DiagnosisData {id: string,';,}userId: string,';,'';
type: 'five_diagnosis' | 'symptom_analysis' | 'health_assessment';','';
data: Record<string, unknown>;
result?: DiagnosisResult;';,'';
timestamp: string,';'';
}
}
  const status = 'pending' | 'processing' | 'completed' | 'failed';'}'';'';
}
export interface DiagnosisResult {id: string}diagnosis: string,;
confidence: number,;
const recommendations = string[];
followUp?: string;
}
}
  metadata?: Record<string; unknown>;}
}
// 用户配置类型'/;,'/g'/;
export interface UserPreferences {';,}theme: 'light' | 'dark' | 'auto';','';
language: 'zh' | 'en';','';
notifications: NotificationSettings,;
privacy: PrivacySettings,;
}
}
  const accessibility = AccessibilitySettings;}
}
export interface NotificationSettings {enabled: boolean}types: {health_reminders: boolean,;
agent_messages: boolean,;
system_updates: boolean,;
}
}
  const emergency_alerts = boolean;}
};
schedule: {start_time: string,;
end_time: string,;
}
  const timezone = string;}
  };
}
export interface PrivacySettings {data_sharing: boolean}analytics: boolean,;
personalization: boolean,;
}
}
  const third_party_integrations = boolean;}
}';,'';
export interface AccessibilitySettings {';,}font_size: 'small' | 'medium' | 'large' | 'extra_large';','';
high_contrast: boolean,;
screen_reader: boolean,;
voice_commands: boolean,;
}
}
  const haptic_feedback = boolean;}';'';
};
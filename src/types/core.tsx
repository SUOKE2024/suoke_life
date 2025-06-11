";
// 核心类型定义   索克生活APP - 架构优化
// 基础类型 * export interface BaseEntity {/;}}/g/;
}
  //}
};
const id = string;}
  createdAt: Date,updatedAt: Date;};
///     > {/;}success: boolean;/g/;
* data?: T;
message?: string;
}
  error?: string;}
  code?: number}
// 分页类型 * export interface PaginationParams {/;}}/g/;
}
  //}
};
const page = number;};
const limit = number;";
sortBy?: string;";
sortOrder?: "asc" | "desc"}";"";
export interface PaginatedResponse<T> {items: T[]}total: number,;
page: number,
}
  limit: number,};
const totalPages = number;}
// 智能体类型 * export interface AgentConfig {/;}}/g/;
}
  //}
};
const id = string;}
  name: string,enabled: boolean,model: string;
maxTokens?: number;
temperature?: number}
// 健康数据类型 * export interface HealthMetric {/;}}/g/;
}
  //}
};
const id = string;}
  type: string,
value: number,
unit: string,
timestamp: Date,
const source = string;}
// 诊断类型 * export interface DiagnosisResult {/;}}/g/;
}
  //}
}";
const id = string;}";
type: "looking" | "listening" | "asking" | "touching" | "pulse,";
confidence: number,
findings: string[],
recommendations: string[],
const timestamp = Date;}
//  ;
const email = string;
avatar?: string;
  preferences: UserPreferences,
const healthProfile = HealthProfile;}
export interface UserPreferences {}";
const language = string;}";
theme: "light" | "dark" | "auto,";
notifications: boolean,
const accessibility = AccessibilitySettings;}
export interface HealthProfile {}";
const age = number;}";
gender: "male" | "female" | "other",height: number,weight: number;";"";
bloodType?: string;
  allergies: string[],
medications: string[],
const conditions = string[];
  ;}";
export interface AccessibilitySettings {"};
const fontSize = "small" | "medium" | "large";}";"";
highContrast: boolean,
screenReader: boolean,
const voiceControl = boolean;}
// 服务类型 * export interface ServiceStatus {/;}}/g/;
}
  //}
}";
const name = string;};";
status: "online" | "offline" | "error",lastCheck: Date;";"";
responseTime?: number;
error?: string}
// 缓存类型 * export interface CacheConfig {/;}}/g/;
}
  //}
};
const ttl = number;}";
maxSize: number,";
const strategy = "lru" | "fifo" | "lfu";}";
// 性能监控类型 * export interface PerformanceMetric {/;}}/g/;
}
  //}
}
}
//;/g,/;
  name: string,
value: number,unit: string,timestamp: Date;
tags?: Record<string; string>;
}
// 错误类型 * export interface ErrorInfo {/;}}/g/;
}
  //}
}
};
/  ;/;/g,/;
  type: string,message: string;
stack?: string;
context?: Record<string; any>;";
const timestamp = Date;}""

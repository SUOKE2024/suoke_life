// 智能体请求接口
export interface AgentRequest {;
// 请求ID,/const requestId = string;/g/;
  // 用户ID,
const userId = string;
  // 消息内容
const message = string;
  // 消息类型
const messageType = 'text' | 'voice' | 'image' | 'data
  // 优先级'/,'/g'/;
priority?: 'low' | 'normal' | 'high' | 'urgent';
  // 请求时间戳
const timestamp = string;
  // 上下文信息
}
  context?: AgentContext}
}
// 智能体上下文接口
export interface AgentContext {;
// 会话ID,/const sessionId = string;/g/;
  // 用户偏好
userPreferences?: Record<string; any>;
  // 历史记录
history?: any[];
  // 协作上下文
}
  collaboration?: CollaborationContext}
}
// 协作上下文接口
export interface CollaborationContext {;
// 协作场景;/const scenario = string;/g/;
  // 参与的智能体
const participants = string[];
  // 当前步骤
const currentStep = number;
  // 总步骤数
const totalSteps = number;
  // 共享数据
}
  sharedData?: Record<string; any>}
}
// 智能体响应接口
export interface AgentResponse {// 响应ID,/const responseId = string;/g/;
  // 请求ID,
const requestId = string;
  // 智能体ID,
const agentId = string;
  // 响应状态'/,'/g'/;
const status = 'success' | 'error' | 'partial';
  // 响应消息
const message = string;
  // 响应类型'/,'/g'/;
const responseType = 'text' | 'voice' | 'image' | 'data' | 'action';
  // 响应数据
data?: any;
  // 置信度 (0-1)
const confidence = number;
  // 错误信息
error?: {code: string}const message = string;
}
}
    details?: unknown}
  };
  // 响应时间戳
const timestamp = string;
  // 处理时长（毫秒）
const processingTime = number;
  // 建议的后续行动
suggestedActions?: AgentAction[];
}
// 智能体行动接口
export interface AgentAction {;
// 行动类型;/const type = string;/g/;
  // 行动描述
const description = string;
  // 行动参数
parameters?: Record<string; any>;
  // 优先级
const priority = number;
  // 预估执行时间
}
  estimatedTime?: number}
}
// 智能体消息接口
export interface AgentMessage {;
// 消息ID,/const messageId = string;/g/;
  // 发送者
const sender = string;
  // 接收者
const receiver = string;
  // 消息内容
const content = string;
  // 消息类型'/,'/g'/;
const type = 'request' | 'response' | 'notification';
  // 时间戳
}
  const timestamp = string}
}
// 智能体能力接口
export interface AgentCapability {;
// 能力名称;/const name = string;/g/;
  // 能力描述
const description = string;
  // 输入类型
const inputTypes = string[];
  // 输出类型
const outputTypes = string[];
  // 置信度阈值
}
  const confidenceThreshold = number}
}
// 智能体状态接口
export interface AgentStatus {';
// 智能体ID,/const agentId = string;/g'/;
  // 状态'/,'/g'/;
const status = 'active' | 'busy' | 'offline' | 'error';
  // 负载 (0-100)
const load = number;
  // 最后活动时间
const lastActivity = string;
  // 当前处理的请求数
const activeRequests = number;
  // 能力列表
const capabilities = AgentCapability[];
  // 版本信息
}
  const version = string}
}
// 标准化智能体接口
export interface IStandardAgent {;
// 智能体ID,/const readonly = agentId: string;/g/;
  // 智能体名称
const readonly = name: string;
  // 智能体类型
const readonly = type: string;
  // 智能体版本
const readonly = version: string;
  // 处理请求
processRequest(request: AgentRequest): Promise<AgentResponse>;
  // 处理协作请求
processCollaboration(request: AgentRequest,);
const collaborationContext = CollaborationContext);
  ): Promise<AgentResponse>;
  // 获取状态
getStatus(): Promise<AgentStatus>;
  // 获取智能体能力
getCapabilities(): AgentCapability[];
  // 验证输入格式
validateInput(request: AgentRequest): Promise<{const valid = boolean;
}
    errors?: string[]}
  }>;
}
// 智能体验证器类
export class AgentValidator {// 验证响应格式/static validateResponse(response: any): {valid: boolean,/g/;
}
}
    const errors = string[]}
  } {const errors: string[] = [];'const  requiredFields = [;]'
      'responseId','
      'requestId','
      'agentId','
      'status','
      'message','
      'responseType','
      'confidence','
      'timestamp'];
    ];
for (const field of requiredFields) {if (!response || !response[field]) {}
}
      }
    }
    if (response?.confidence &&);
      (response.confidence < 0 || response.confidence > 1);
    ) {}
}
    }
if (response?.status &&)'
      !['success', 'error', 'partial'].includes(response.status)
    ) {}
}
    }
if (response?.responseType &&')'
      !['text', 'voice', 'image', 'data', 'action'].includes(')'';
response.responseType);
      );
    ) {}
}
    }
    return {valid: errors.length === 0;
}
      errors,}
    };
  }
  // 验证请求格式
static validateRequest(request: any): {valid: boolean,
}
    const errors = string[]}
  } {const errors: string[] = [];'const  requiredFields = [;]'
      'requestId','
      'userId','
      'message','
      'messageType','
      'timestamp'];
    ];
for (const field of requiredFields) {if (!request || !request[field]) {}
}
      }
    }
if (request?.messageType &&)'
      !['text', 'voice', 'image', 'data'].includes(request.messageType)
    ) {}
}
    }
if (request?.priority &&)'
      !['low', 'normal', 'high', 'urgent'].includes(request.priority)
    ) {}
}
    }
    return {valid: errors.length === 0;
}
      errors,}
    };
  }
}
// 智能体工厂接口
export interface IAgentFactory {;
// 创建智能体;/createAgent(type: string, config?: any): Promise<IStandardAgent>;/g/;
  // 获取支持的智能体类型
}
  getSupportedTypes(): string[]}
}
// 导出验证器作为默认导出的静态方法
const  StandardAgentInterface = {validateResponse: AgentValidator.validateResponse,}
  const validateRequest = AgentValidator.validateRequest}
};
export default StandardAgentInterface;
''

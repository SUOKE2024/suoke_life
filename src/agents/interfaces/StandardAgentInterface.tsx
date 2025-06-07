import React from "react";
text" | "voice" | "image" | "data;
  //
  // 请求时间戳  timestamp: string;
  //
export interface AgentContext {
  // 会话ID  sessionId: string;
  //
  //
  //
  // 协作上下文  collaboration?: CollaborationContext
}
export interface CollaborationContext {
  // 协作场景  scenario: string;
  // 参与的智能体  participants: string[];
  // 当前步骤  currentStep: number;
  // 总步骤数  totalSteps: number;
  //
}
export interface AgentResponse {
  // 响应ID  responseId: string;
  // 请求ID  requestId: string;
  // 智能体ID  agentId: string;
  // 响应状态  status: "success" | "error" | "partial";
  // 响应消息  message: string;
  // 响应类型  responseType: "text" | "voice" | "image" | "data" | "action";
  //
  // 置信度 (0-1)  confidence: number;
  //
  //
  // 响应时间戳  timestamp: string;
  // 处理时长（毫秒）  processingTime: number;
  //
    message: string;
    details?: unknown
};
}
export interface AgentAction {
  // 行动类型  type: string;
  // 行动描述  description: string;
  //
  // 优先级  priority: number;
  // 预估执行时间  estimatedTime?: number
}
export interface AgentMessage {
  // 消息ID  messageId: string;
  // 发送者  sender: string;
  // 接收者  receiver: string;
  // 消息内容  content: string;
  // 消息类型  type: "request" | "response" | "notification";
  // 时间戳  timestamp: string;
}
export interface AgentCapability {
  // 能力名称  name: string;
  // 能力描述  description: string;
  // 输入类型  inputTypes: string[];
  // 输出类型  outputTypes: string[];
  // 置信度阈值  confidenceThreshold: number;
}
export interface AgentStatus {
  // 智能体ID  agentId: string;
  // 状态  status: "active" | "busy" | "offline" | "error";
  0-100 ///     , lastActivity: string;
  // 当前处理的请求数  activeRequests: number;
  // 能力列表  capabilities: AgentCapability[];
  // 版本信息  version: string;
}
// 标准化智能体接口export interface IStandardAgent {
  // 智能体ID  readonly agentId: string;
  // 智能体名称  readonly name: string;
  // 智能体类型  readonly type: string;
  // 智能体版本  readonly version: string;
  ///    >;
  // 处理协作请求  processCollaboration(
    request: AgentRequest;
    collaborationContext: CollaborationContext): Promise<AgentResponse /    >;
  ///    >;
  // 获取智能体能力  getCapabilities(): AgentCapability[];
  // 验证输入格式  validateInput(request: AgentRequest): Promise< { valid: boolean;
    errors?: string[];
}>;
  ///    }
验证响应格式  static validateResponse(response: unknown):   { valid: boolean,errors: string[];
    } {
    const errors: string[] = [];
    const requiredFields = [;
      "responseId",requestId","agentId",status","message",responseType","confidence",timestamp"]
    for (const field of requiredFields) {
      if (!response[field]) {
        errors.push(`缺少必需字段: ${field}`);
      }
    }
    if (
      response.confidence &&
      (response.confidence < 0 || response.confidence > 1)
    ) {
      errors.push("置信度必须在0-1之间");
    }
    if (
      response.status &&
      !["success",error", "partial"].includes(response.status);
    ) {
      errors.push("状态值无效");
    }
    if (
      response.responseType &&
      !["text",voice", "image",data", "action"].includes(
        response.responseType;
      );
    ) {
      errors.push("响应类型无效");
    }
    return {valid: errors.length === 0,
      error;s;
    ;};
  }
  // 验证请求格式  static validateRequest(request: unknown):   { valid: boolean,
    errors: string[];
    } {
    const errors: string[] = [];
    const requiredFields = [;
      "requestId",userId","message",messageType","timestamp"]
    for (const field of requiredFields) {
      if (!request[field]) {
        errors.push(`缺少必需字段: ${field}`);
      }
    }
    if (
      request.messageType &&
      !["text",voice", "image",data"].includes(request.messageType);
    ) {
      errors.push("消息类型无效");
    }
    if (
      request.priority &&
      !["low",normal", "high",urgent"].includes(request.priority);
    ) {
      errors.push("优先级值无效");
    }
    return {valid: errors.length === 0,
      error;s;
    ;};
  }
}
// 智能体工厂接口export interface IAgentFactory {
  ///    >;
  // 获取支持的智能体类型  getSupportedTypes(): string[];
}
export default IStandardAgent;

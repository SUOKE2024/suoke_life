import React from "react";
import { apiClient } from "./apiClient";
import { FourDiagnosisAggregationResult } from "../types/agents";

// 智能体信息接口
export interface AgentInfo {
  id: string;
  name: string;
  status: "online" | "offline" | "busy";
  capabilities: string[];
  description?: string;
  avatar?: string;
}

// 消息接口
export interface Message {
  id: string;
  content: string;
  timestamp: number;
  sender: string;
  type?: "text" | "image" | "audio" | "file";
  metadata?: unknown;
}

// 咨询会话接口
export interface ConsultationSession {
  sessionId: string;
  agentId: string;
  status: "active" | "completed" | "cancelled";
  startTime: number;
  endTime?: number;
}

// 智能体建议接口
export interface AgentSuggestion {
  id: string;
  title: string;
  content: string;
  category: string;
  priority: "high" | "medium" | "low";
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    message: string;
    code?: string;
  };
  code?: string | number;
}

class AgentService {
  // 获取智能体信息
  async getAgentInfo(agentId: string): Promise<AgentInfo> {
    try {
      const response: ApiResponse<AgentInfo> = await apiClient.get(
        `/agents/${agentId}/info`
      );
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || "获取智能体信息失败");
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "获取智能体信息失败");
    }
  }

  // 发送消息给智能体
  async sendMessage(
    agentId: string,
    content: string,
    type: string = "text"
  ): Promise<Message> {
    try {
      const response: ApiResponse<Message> = await apiClient.post(
        `/agents/${agentId}/messages`,
        {
          content,
          type,
          timestamp: Date.now(),
        }
      );
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || "发送消息失败");
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "发送消息失败");
    }
  }

  // 开始咨询会话
  async startConsultation(agentId: string): Promise<ConsultationSession> {
    try {
      const response: ApiResponse<ConsultationSession> = await apiClient.post(
        `/agents/${agentId}/consultation/start`,
        { startTime: Date.now() }
      );
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || "开始咨询失败");
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "开始咨询失败");
    }
  }

  // 结束咨询会话
  async endConsultation(sessionId: string): Promise<void> {
    try {
      const response: ApiResponse<void> = await apiClient.post(
        `/consultation/${sessionId}/end`,
        { endTime: Date.now() }
      );
      if (!response.success) {
        throw new Error(response.error?.message || "结束咨询失败");
      }
    } catch (error: any) {
      throw new Error(error.message || "结束咨询失败");
    }
  }

  // 获取智能体建议
  async getAgentSuggestions(
    agentId: string,
    category?: string
  ): Promise<AgentSuggestion[]> {
    try {
      const queryString = category
        ? `?category=${encodeURIComponent(category)}`
        : "";
      const response: ApiResponse<AgentSuggestion[]> = await apiClient.get(
        `/agents/${agentId}/suggestions${queryString}`
      );
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || "获取建议失败");
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "获取建议失败");
    }
  }

  // 获取所有可用智能体
  async getAvailableAgents(): Promise<AgentInfo[]> {
    try {
      const response: ApiResponse<AgentInfo[]> = await apiClient.get("/agents");
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || "获取智能体列表失败");
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "获取智能体列表失败");
    }
  }

  // 获取聊天历史
  async getChatHistory(
    agentId: string,
    limit: number = 50
  ): Promise<Message[]> {
    try {
      const response: ApiResponse<Message[]> = await apiClient.get(
        `/agents/${agentId}/messages?limit=${limit}`
      );
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || "获取聊天历史失败");
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "获取聊天历史失败");
    }
  }

  // 健康检查
  async healthCheck(): Promise<{ status: string; timestamp: number }> {
    try {
      const response: ApiResponse<{ status: string; timestamp: number }> =
        await apiClient.get("/agents/health");
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || "健康检查失败");
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "健康检查失败");
    }
  }

  // 获取四诊聚合结果
  async getFourDiagnosisAggregation(
    agentId: string,
    diagnosisRequest: unknown
  ): Promise<FourDiagnosisAggregationResult> {
    try {
      const response: ApiResponse<FourDiagnosisAggregationResult> =
        await apiClient.post(
          `/agents/${agentId}/four-diagnosis/aggregation`,
          diagnosisRequest
        );
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || "获取四诊聚合结果失败");
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "获取四诊聚合结果失败");
    }
  }

  // 新增：获取智能体状态
  async getAgentStatus(agentId: string): Promise<{ status: string; load: number }> {
    try {
      const response: ApiResponse<{ status: string; load: number }> = 
        await apiClient.get(`/agents/${agentId}/status`);
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || "获取智能体状态失败");
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "获取智能体状态失败");
    }
  }

  // 新增：更新智能体配置
  async updateAgentConfig(agentId: string, config: unknown): Promise<void> {
    try {
      const response: ApiResponse<void> = await apiClient.put(
        `/agents/${agentId}/config`,
        config
      );
      if (!response.success) {
        throw new Error(response.error?.message || "更新智能体配置失败");
      }
    } catch (error: any) {
      throw new Error(error.message || "更新智能体配置失败");
    }
  }

  // 新增：获取智能体性能指标
  async getAgentMetrics(agentId: string): Promise<{
    responseTime: number;
    successRate: number;
    activeConnections: number;
  }> {
    try {
      const response: ApiResponse<{
        responseTime: number;
        successRate: number;
        activeConnections: number;
      }> = await apiClient.get(`/agents/${agentId}/metrics`);
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || "获取智能体性能指标失败");
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.message || "获取智能体性能指标失败");
    }
  }
}

export const agentService = new AgentService();
export default agentService;
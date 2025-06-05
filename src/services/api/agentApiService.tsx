import React from "react";
import { 
  AgentType,
  AgentMessage,
  AgentResponse,
  MessageType,
  ApiResponse 
} from "../../types/agents";
// import { AGENT_CONFIGS } from "../../agents/config/agents.config";

// 临时配置，直到agents.config文件修复
const AGENT_CONFIGS = {
  [AgentType.XIAOAI]: { apiEndpoint: "http://localhost:50053" },
  [AgentType.XIAOKE]: { apiEndpoint: "http://localhost:50054" },
  [AgentType.LAOKE]: { apiEndpoint: "http://localhost:50055" },
  [AgentType.SOER]: { apiEndpoint: "http://localhost:50056" }
};

/**
 * 索克生活四智能体API服务
 * 基于README.md第1013-1063行的智能体描述实现统一的API调用接口
 */

export interface AgentApiConfig {
  baseUrl: string;
  timeout: number;
  retries: number;
  apiKey?: string;
}

export interface ChatRequest {
  message: string;
  messageType: MessageType;
  userId: string;
  sessionId: string;
  context?: Record<string, any>;
}

export interface DiagnosisRequest {
  userId: string;
  sessionId: string;
  diagnosisType: "looking" | "listening" | "inquiry" | "palpation" | "calculation";
  data: unknown;
  context?: Record<string, any>;
}

export interface ServiceRequest {
  userId: string;
  serviceType: string;
  parameters: Record<string, any>;
  context?: Record<string, any>;
}

export interface HealthDataRequest {
  userId: string;
  dataType: "sensor" | "manual" | "device";
  data: unknown;
  timestamp: number;
  context?: Record<string, any>;
}

export class AgentApiService {
  private config: AgentApiConfig;
  private static instance: AgentApiService;

  private constructor(config: AgentApiConfig) {
    this.config = config;
  }

  public static getInstance(config?: AgentApiConfig): AgentApiService {
    if (!AgentApiService.instance) {
      const defaultConfig: AgentApiConfig = {
        baseUrl: "http://localhost:8000",
        timeout: 30000,
        retries: 3
      };
      AgentApiService.instance = new AgentApiService(config || defaultConfig);
    }
    return AgentApiService.instance;
  }

  // 小艾智能体API - 首页聊天频道版主 & 四诊协调智能体
  public async xiaoaiChat(request: ChatRequest): Promise<ApiResponse<AgentResponse>> {
    const endpoint = `${AGENT_CONFIGS[AgentType.XIAOAI].apiEndpoint}/chat`;
    return this.makeRequest(endpoint, {
      method: "POST",
      body: JSON.stringify({
        ...request,
        agentType: AgentType.XIAOAI,
        capabilities: [
          "voice_interaction",
          "dialect_recognition",
          "face_analysis",
          "tongue_diagnosis",
          "intelligent_inquiry",
          "accessibility_services"
        ]
      })
    });
  }

  // 小艾四诊协调API
  public async xiaoaiFourDiagnosis(request: DiagnosisRequest): Promise<ApiResponse<any>> {
    const endpoint = `${AGENT_CONFIGS[AgentType.XIAOAI].apiEndpoint}/four-diagnosis`;
    return this.makeRequest(endpoint, {
      method: "POST",
      body: JSON.stringify({
        ...request,
        agentType: AgentType.XIAOAI,
        coordinationMode: "four_diagnosis_integration"
      })
    });
  }

  // 小艾无障碍服务API
  public async xiaoaiAccessibilityService(request: ServiceRequest): Promise<ApiResponse<any>> {
    const endpoint = `${AGENT_CONFIGS[AgentType.XIAOAI].apiEndpoint}/accessibility`;
    return this.makeRequest(endpoint, {
      method: "POST",
      body: JSON.stringify({
        ...request,
        agentType: AgentType.XIAOAI,
        services: [
          "guide_services",
          "sign_language_recognition",
          "elderly_friendly_interface"
        ]
      })
    });
  }

  // 小克智能体API - SUOKE频道版主 & 服务管理智能体
  public async xiaokeServiceManagement(request: ServiceRequest): Promise<ApiResponse<AgentResponse>> {
    const endpoint = `${AGENT_CONFIGS[AgentType.XIAOKE].apiEndpoint}/service-management`;
    return this.makeRequest(endpoint, {
      method: "POST",
      body: JSON.stringify({
        ...request,
        agentType: AgentType.XIAOKE,
        capabilities: [
          "doctor_matching",
          "appointment_management",
          "service_subscription",
          "product_traceability",
          "store_management"
        ]
      })
    });
  }

  // 小克农产品溯源API
  public async xiaokeProductTraceability(request: ServiceRequest): Promise<ApiResponse<any>> {
    const endpoint = `${AGENT_CONFIGS[AgentType.XIAOKE].apiEndpoint}/product-traceability`;
    return this.makeRequest(endpoint, {
      method: "POST",
      body: JSON.stringify({
        ...request,
        agentType: AgentType.XIAOKE,
        blockchainEnabled: true
      })
    });
  }

  // 小克第三方API集成
  public async xiaokeThirdPartyIntegration(request: ServiceRequest): Promise<ApiResponse<any>> {
    const endpoint = `${AGENT_CONFIGS[AgentType.XIAOKE].apiEndpoint}/third-party-integration`;
    return this.makeRequest(endpoint, {
      method: "POST",
      body: JSON.stringify({
        ...request,
        agentType: AgentType.XIAOKE,
        integrationTypes: [
          "insurance_integration",
          "payment_integration",
          "logistics_integration"
        ]
      })
    });
  }

  // 老克智能体API - 探索频道版主 & 知识传播智能体
  public async laokeKnowledgeRetrieval(request: ServiceRequest): Promise<ApiResponse<AgentResponse>> {
    const endpoint = `${AGENT_CONFIGS[AgentType.LAOKE].apiEndpoint}/knowledge-retrieval`;
    return this.makeRequest(endpoint, {
      method: "POST",
      body: JSON.stringify({
        ...request,
        agentType: AgentType.LAOKE,
        capabilities: [
          "knowledge_retrieval",
          "personalized_learning",
          "content_management",
          "health_education"
        ]
      })
    });
  }

  // 老克游戏NPC API
  public async laokeGameNPC(request: ServiceRequest): Promise<ApiResponse<any>> {
    const endpoint = `${AGENT_CONFIGS[AgentType.LAOKE].apiEndpoint}/game-npc`;
    return this.makeRequest(endpoint, {
      method: "POST",
      body: JSON.stringify({
        ...request,
        agentType: AgentType.LAOKE,
        gameFeatures: [
          "game_npc_roleplay",
          "game_guidance",
          "arvr_interaction"
        ]
      })
    });
  }

  // 老克内容管理API
  public async laokeContentManagement(request: ServiceRequest): Promise<ApiResponse<any>> {
    const endpoint = `${AGENT_CONFIGS[AgentType.LAOKE].apiEndpoint}/content-management`;
    return this.makeRequest(endpoint, {
      method: "POST",
      body: JSON.stringify({
        ...request,
        agentType: AgentType.LAOKE,
        contentServices: [
          "blog_management",
          "content_quality_assurance",
          "knowledge_contribution"
        ]
      })
    });
  }

  // 索儿智能体API - LIFE频道版主 & 生活健康管理智能体
  public async soerLifestyleManagement(request: HealthDataRequest): Promise<ApiResponse<AgentResponse>> {
    const endpoint = `${AGENT_CONFIGS[AgentType.SOER].apiEndpoint}/lifestyle-management`;
    return this.makeRequest(endpoint, {
      method: "POST",
      body: JSON.stringify({
        ...request,
        agentType: AgentType.SOER,
        capabilities: [
          "habit_cultivation",
          "behavior_intervention",
          "diet_management",
          "exercise_management",
          "sleep_management"
        ]
      })
    });
  }

  // 索儿传感器数据整合API
  public async soerSensorDataIntegration(request: HealthDataRequest): Promise<ApiResponse<any>> {
    const endpoint = `${AGENT_CONFIGS[AgentType.SOER].apiEndpoint}/sensor-data-integration`;
    return this.makeRequest(endpoint, {
      method: "POST",
      body: JSON.stringify({
        ...request,
        agentType: AgentType.SOER,
        dataFusionEnabled: true,
        edgeComputingEnabled: true,
        privacyProtectionEnabled: true
      })
    });
  }

  // 索儿健康数据分析API
  public async soerHealthDataAnalysis(request: HealthDataRequest): Promise<ApiResponse<any>> {
    const endpoint = `${AGENT_CONFIGS[AgentType.SOER].apiEndpoint}/health-data-analysis`;
    return this.makeRequest(endpoint, {
      method: "POST",
      body: JSON.stringify({
        ...request,
        agentType: AgentType.SOER,
        analysisTypes: [
          "biomarker_analysis",
          "trend_analysis",
          "risk_assessment",
          "personalized_recommendations"
        ]
      })
    });
  }

  // 通用API调用方法
  private async makeRequest(url: string, options: RequestInit): Promise<ApiResponse<any>> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
          ...(this.config.apiKey && { "Authorization": `Bearer ${this.config.apiKey}` }),
          ...options.headers
        }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data,
        timestamp: new Date(),
        requestId: `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      };
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof Error) {
        return {
          success: false,
          error: {
            code: "REQUEST_FAILED",
            message: error.message
          },
          timestamp: new Date(),
          requestId: `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        };
      }
      
      return {
        success: false,
        error: {
          code: "UNKNOWN_ERROR",
          message: "Unknown error occurred"
        },
        timestamp: new Date(),
        requestId: `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      };
    }
  }

  // 批量API调用
  public async batchRequest(requests: Array<{
    endpoint: string;
    options: RequestInit;
  }>): Promise<ApiResponse<any>[]> {
    const promises = requests.map(({ endpoint, options }) => 
      this.makeRequest(endpoint, options)
    );
    
    return Promise.all(promises);
  }

  // 健康检查API
  public async healthCheck(): Promise<ApiResponse<{ status: string; timestamp: number }>> {
    const endpoint = `${this.config.baseUrl}/health`;
    return this.makeRequest(endpoint, { method: "GET" });
  }

  // 获取智能体状态
  public async getAgentStatus(agentType: AgentType): Promise<ApiResponse<any>> {
    const endpoint = `${AGENT_CONFIGS[agentType].apiEndpoint}/status`;
    return this.makeRequest(endpoint, { method: "GET" });
  }

  // 更新智能体配置
  public async updateAgentConfig(agentType: AgentType, config: Record<string, any>): Promise<ApiResponse<any>> {
    const endpoint = `${AGENT_CONFIGS[agentType].apiEndpoint}/config`;
    return this.makeRequest(endpoint, {
      method: "PUT",
      body: JSON.stringify(config)
    });
  }
}

// 导出单例实例
export const agentApiService = AgentApiService.getInstance();
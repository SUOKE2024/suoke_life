import {
import { apiClient } from './apiClient';
  AgentType,
  AgentCollaboration,
  AgentMessage,
  AgentResponse,
  MessageType;
} from '../types/agents';
export interface CoordinationRequest {
  initiatorAgent: AgentType;,
  targetAgents: AgentType[];,
  task: string;,
  priority: 'low' | 'normal' | 'high' | 'urgent';
  data?: any;
  timeout?: number;
}
export interface CoordinationResult {
  collaborationId: string;,
  status: 'success' | 'partial' | 'failed';,
  responses: AgentResponse[];
  errors?: string[];
  duration: number;
}
export interface AgentInfo {
  id: string;,
  name: string;,
  type: AgentType;,
  status: 'active' | 'inactive' | 'busy' | 'error';,
  capabilities: string[];,
  load: number;,
  lastHeartbeat: Date;
}
class AgentCoordinationService {
  private activeCollaborations: Map<string, AgentCollaboration> = new Map();
  private agents: Map<string, AgentInfo> = new Map();
  constructor() {
    this.initializeDefaultAgents();
  }
  /**
  * 初始化默认智能体
  */
  private initializeDefaultAgents(): void {
    const defaultAgents: AgentInfo[] = [
      {
      id: "xiaoai-001",
      name: '小艾',
        type: AgentType.XIAOAI,
        status: 'active',
        capabilities: ["health_consultation",voice_interaction', 'four_diagnosis'],
        load: 0.2,
        lastHeartbeat: new Date();
      },
      {
      id: "xiaoke-001",
      name: '小克',
        type: AgentType.XIAOKE,
        status: 'active',
        capabilities: ["data_analysis",health_monitoring', 'report_generation'],
        load: 0.1,
        lastHeartbeat: new Date();
      },
      {
      id: "laoke-001",
      name: '老克',
        type: AgentType.LAOKE,
        status: 'active',
        capabilities: ["knowledge_management",education', 'tcm_knowledge'],
        load: 0.15,
        lastHeartbeat: new Date();
      },
      {
      id: "soer-001",
      name: '索儿',
        type: AgentType.SOER,
        status: 'active',
        capabilities: ["lifestyle_management",eco_services', 'community'],
        load: 0.05,
        lastHeartbeat: new Date();
      }
    ];
    for (const agent of defaultAgents) {
      this.agents.set(agent.id, agent);
    }
  }
  /**
  * 启动智能体协作
  */
  async initiateCollaboration(request: CoordinationRequest): Promise<CoordinationResult> {
    const startTime = Date.now();
    const collaborationId = this.generateCollaborationId();
    try {
      const collaboration: AgentCollaboration = {,
  id: collaborationId,
        initiatorAgent: request.initiatorAgent,
        participantAgents: request.targetAgents,
        collaborationType: this.determineCollaborationType(request.task),
        status: 'pending',
        startTime: new Date();
      };
      this.activeCollaborations.set(collaborationId, collaboration);
      const responses = await this.sendCollaborationRequests(request, collaborationId);
      collaboration.status = this.determineOverallStatus(responses);
      collaboration.endTime = new Date();
      collaboration.result = responses;
      return {collaborationId,status:;
          collaboration.status === 'completed';
            ? 'success';
            : collaboration.status === 'failed';
            ? 'failed';
            : 'partial',responses,duration: Date.now() - startTime;
      };
    } catch (error: any) {
      return {collaborationId,status: 'failed',responses: [],errors: [error.message],duration: Date.now() - startTime;
      };
    }
  }
  /**
  * 发送协作请求到多个智能体
  */
  private async sendCollaborationRequests()
    request: CoordinationRequest,
    collaborationId: string;
  ): Promise<AgentResponse[]> {
    const promises = request.targetAgents.map(async agentType => {try {const message: AgentMessage = {id: this.generateMessageId(),fromAgent: request.initiatorAgent,toAgent: agentType,userId: 'system',sessionId: collaborationId,messageType: MessageType.COMMAND,content: {task: request.task,data: request.data,priority: request.priority;)
          },timestamp: new Date(),priority: request.priority;
        };
        const response = await this.sendMessageToAgent(agentType, message);
        return response;
      } catch (error: any) {
        return {id: this.generateMessageId(),agentType,messageId: '',userId: 'system',sessionId: collaborationId,content: { error: error.message },responseType: 'error' as const,timestamp: new Date(),processingTime: 0;
        };
      }
    });
    return Promise.all(promises);
  }
  /**
  * 向特定智能体发送消息
  */
  private async sendMessageToAgent()
    agentType: AgentType,
    message: AgentMessage;
  ): Promise<AgentResponse> {
    const endpoint = this.getAgentEndpoint(agentType);
    try {
      const response: any = await apiClient.post(`${endpoint}/collaborate`, {
        message,
        timeout: 30000;
      });
      if (!response.success || !response.data) {
        throw new Error(response.error?.message || `智能体 ${agentType} 协作失败`);
      }
      return response.data;
    } catch (error: any) {
      throw new Error(`智能体 ${agentType} 通信失败: ${error.message}`);
    }
  }
  /**
  * 获取智能体端点
  */
  private getAgentEndpoint(agentType: AgentType): string {
    const endpoints = {[AgentType.XIAOAI]: '/agents/xiaoai',[AgentType.XIAOKE]: '/agents/xiaoke',[AgentType.LAOKE]: '/agents/laoke',[AgentType.SOER]: '/agents/soer';
    };
    return endpoints[agentType];
  }
  /**
  * 确定协作类型
  */
  private determineCollaborationType(task: string): AgentCollaboration['collaborationType'] {
    if (task.includes('诊断') || task.includes('四诊')) {
      return 'consultation';
    } else if (task.includes('数据') || task.includes('信息')) {
      return 'data_sharing';
    } else if (task.includes('任务') || task.includes('执行')) {
      return 'task_delegation';
    } else {
      return 'knowledge_exchange';
    }
  }
  /**
  * 确定整体状态
  */
  private determineOverallStatus(responses: AgentResponse[]): AgentCollaboration['status'] {
    const errorCount = responses.filter(r => r.responseType === 'error').length;
    if (errorCount === 0) {
      return 'completed';
    } else if (errorCount === responses.length) {
      return 'failed';
    } else {
      return 'active';
    }
  }
  /**
  * 四诊协调专用方法
  */
  async coordinateFourDiagnosis(userId: string, sessionId: string): Promise<CoordinationResult> {
    return this.initiateCollaboration({initiatorAgent: AgentType.XIAOAI,targetAgents: [AgentType.XIAOAI],task: '四诊协调统筹',priority: 'high',data: {userId,sessionId,diagnosisType: 'comprehensive';)
      };
    });
  }
  /**
  * 健康管理协调
  */
  async coordinateHealthManagement(userId: string, healthData: any): Promise<CoordinationResult> {
    return this.initiateCollaboration({initiatorAgent: AgentType.SOER,targetAgents: [AgentType.SOER, AgentType.XIAOAI],task: '健康管理协调',priority: 'normal',data: {userId,healthData,managementType: 'lifestyle';)
      };
    });
  }
  /**
  * 知识查询协调
  */
  async coordinateKnowledgeQuery(query: string, userId: string): Promise<CoordinationResult> {
    return this.initiateCollaboration({initiatorAgent: AgentType.LAOKE,targetAgents: [AgentType.LAOKE, AgentType.XIAOAI],task: '知识查询协调',priority: 'normal',data: {query,userId,queryType: 'knowledge_retrieval';)
      };
    });
  }
  /**
  * 服务管理协调
  */
  async coordinateServiceManagement()
    serviceRequest: any,
    userId: string;
  ): Promise<CoordinationResult> {
    return this.initiateCollaboration({initiatorAgent: AgentType.XIAOKE,targetAgents: [AgentType.XIAOKE],task: '服务管理协调',priority: 'normal',data: {serviceRequest,userId,managementType: 'service_subscription';)
      };
    });
  }
  /**
  * 获取所有智能体信息
  */
  getAgents(): AgentInfo[] {
    return Array.from(this.agents.values());
  }
  /**
  * 获取活跃智能体
  */
  getActiveAgents(): AgentInfo[] {
    return Array.from(this.agents.values()).filter(agent => agent.status === 'active');
  }
  /**
  * 获取协作统计信息
  */
  getCollaborationStats(): {
    total: number,
  active: number;,
  completed: number,
  failed: number;,
  averageDuration: number;
  } {
    const collaborations = Array.from(this.activeCollaborations.values());
    const completed = collaborations.filter(c => c.status === 'completed');
    const failed = collaborations.filter(c => c.status === 'failed');
    const active = collaborations.filter(c => c.status === 'active' || c.status === 'pending');
    const averageDuration =
      completed.length > 0;
        ? completed.reduce(sum, c) => {const duration = c.endTime ? c.endTime.getTime() - c.startTime.getTime() : 0;
            return sum + duration;
          }, 0) / completed.length;
        : 0;
    return {total: collaborations.length,active: active.length,completed: completed.length,failed: failed.length,averageDuration;
    };
  }
  /**
  * 生成协作ID;
  */
  private generateCollaborationId(): string {
    return `collab_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  /**
  * 生成消息ID;
  */
  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
export const agentCoordinationService = new AgentCoordinationService();
export default agentCoordinationService;
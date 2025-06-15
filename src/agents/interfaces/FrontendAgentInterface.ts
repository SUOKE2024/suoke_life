/**
 * 前端智能体接口层
 * 提供前端组件与 Agentic AI 系统的简化接口
 * 
 * 设计原则：
 * 1. 简化：只暴露前端需要的核心功能
 * 2. 代理：将复杂逻辑委托给 Agentic AI 系统
 * 3. 响应式：支持实时状态更新和事件通知
 * 4. 类型安全：提供完整的 TypeScript 类型支持
 */

import { EventEmitter } from 'events';
import {
  AgentType,
  AgentStatus,
  AgentRequest,
  AgentResponse,
  AgentContext,
  CollaborationRequest,
  CollaborationSession
} from '../../core/agentic/interfaces/UnifiedAgentInterface';

// ============================================================================
// 前端专用类型定义
// ============================================================================

export interface FrontendAgentConfig {
  agentId: string;
  type: AgentType;
  displayName: string;
  avatar?: string;
  description?: string;
  capabilities: string[];
  isAvailable: boolean;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
  agentId?: string;
  agentType?: AgentType;
  metadata?: {
    confidence?: number;
    processingTime?: number;
    requiresFollowUp?: boolean;
    suggestions?: string[];
  };
}

export interface DiagnosisRequest {
  type: 'inquiry' | 'look' | 'listen' | 'palpation' | 'comprehensive';
  content: string;
  context: {
    userId: string;
    sessionId: string;
    hasImages?: boolean;
    hasAudio?: boolean;
    hasPalpationData?: boolean;
  };
  attachments?: DiagnosisAttachment[];
}

export interface DiagnosisAttachment {
  id: string;
  type: 'image' | 'audio' | 'sensor_data';
  name: string;
  data: any;
  metadata?: Record<string, any>;
}

export interface DiagnosisResult {
  id: string;
  type: string;
  summary: string;
  confidence: number;
  recommendations: Recommendation[];
  followUpActions?: FollowUpAction[];
  collaboratingAgents?: AgentType[];
  processingTime: number;
}

export interface Recommendation {
  category: 'lifestyle' | 'treatment' | 'monitoring' | 'consultation';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  timeframe?: string;
  actions?: string[];
}

export interface FollowUpAction {
  type: 'schedule_appointment' | 'additional_test' | 'lifestyle_change' | 'medication';
  description: string;
  urgency: 'low' | 'medium' | 'high';
  estimatedTime?: string;
}

export interface AgentAvailability {
  agentId: string;
  type: AgentType;
  status: AgentStatus;
  currentLoad: number;        // 0-1
  estimatedWaitTime: number;  // minutes
  capabilities: string[];
}

export interface CollaborationStatus {
  sessionId: string;
  participants: AgentType[];
  status: 'planning' | 'active' | 'completed' | 'failed';
  progress: number;           // 0-1
  currentActivity: string;
  estimatedCompletion?: Date;
}

// ============================================================================
// 前端智能体接口
// ============================================================================

export interface FrontendAgentInterface extends EventEmitter {
  // 基本信息
  readonly config: FrontendAgentConfig;
  readonly isConnected: boolean;
  readonly lastActivity: Date;
  
  // 连接管理
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  
  // 聊天功能
  sendMessage(content: string, context: AgentContext): Promise<ChatMessage>;
  sendMessageStream(content: string, context: AgentContext): AsyncGenerator<Partial<ChatMessage>>;
  
  // 诊断功能
  requestDiagnosis(request: DiagnosisRequest): Promise<DiagnosisResult>;
  requestCollaborativeDiagnosis(request: DiagnosisRequest, requiredAgents?: AgentType[]): Promise<DiagnosisResult>;
  
  // 状态查询
  getStatus(): AgentStatus;
  getAvailability(): Promise<AgentAvailability>;
  
  // 协作功能
  requestCollaboration(targetAgents: AgentType[], description: string): Promise<CollaborationSession>;
  getCollaborationStatus(sessionId: string): Promise<CollaborationStatus>;
  
  // 事件监听
  onStatusChanged(callback: (status: AgentStatus) => void): void;
  onMessageReceived(callback: (message: ChatMessage) => void): void;
  onDiagnosisCompleted(callback: (result: DiagnosisResult) => void): void;
  onCollaborationUpdate(callback: (status: CollaborationStatus) => void): void;
}

// ============================================================================
// 智能体管理器接口
// ============================================================================

export interface FrontendAgentManager extends EventEmitter {
  // 智能体管理
  getAvailableAgents(): Promise<FrontendAgentConfig[]>;
  getAgent(agentId: string): Promise<FrontendAgentInterface | null>;
  getAgentByType(type: AgentType): Promise<FrontendAgentInterface | null>;
  
  // 智能选择
  selectBestAgent(request: DiagnosisRequest): Promise<FrontendAgentInterface | null>;
  selectAgentsForCollaboration(request: DiagnosisRequest): Promise<FrontendAgentInterface[]>;
  
  // 系统状态
  getSystemStatus(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    availableAgents: number;
    totalAgents: number;
    averageResponseTime: number;
  }>;
  
  // 批量操作
  broadcastMessage(content: string, context: AgentContext, targetTypes?: AgentType[]): Promise<ChatMessage[]>;
  
  // 事件监听
  onAgentAvailable(callback: (agent: FrontendAgentConfig) => void): void;
  onAgentUnavailable(callback: (agentId: string) => void): void;
  onSystemStatusChanged(callback: (status: string) => void): void;
}

// ============================================================================
// 前端智能体实现基类
// ============================================================================

export abstract class BaseFrontendAgent extends EventEmitter implements FrontendAgentInterface {
  protected _config: FrontendAgentConfig;
  protected _isConnected: boolean = false;
  protected _lastActivity: Date = new Date();
  protected _status: AgentStatus = AgentStatus.OFFLINE;
  
  constructor(config: FrontendAgentConfig) {
    super();
    this._config = config;
  }
  
  get config(): FrontendAgentConfig {
    return { ...this._config };
  }
  
  get isConnected(): boolean {
    return this._isConnected;
  }
  
  get lastActivity(): Date {
    return this._lastActivity;
  }
  
  // 抽象方法，由具体实现类实现
  abstract connect(): Promise<void>;
  abstract disconnect(): Promise<void>;
  abstract sendMessage(content: string, context: AgentContext): Promise<ChatMessage>;
  abstract requestDiagnosis(request: DiagnosisRequest): Promise<DiagnosisResult>;
  
  // 默认实现
  async *sendMessageStream(content: string, context: AgentContext): AsyncGenerator<Partial<ChatMessage>> {
    // 默认实现：将普通消息转换为流式响应
    const message = await this.sendMessage(content, context);
    yield message;
  }
  
  async requestCollaborativeDiagnosis(request: DiagnosisRequest, requiredAgents?: AgentType[]): Promise<DiagnosisResult> {
    // 默认实现：委托给单一诊断
    return await this.requestDiagnosis(request);
  }
  
  getStatus(): AgentStatus {
    return this._status;
  }
  
  async getAvailability(): Promise<AgentAvailability> {
    return {
      agentId: this._config.agentId,
      type: this._config.type,
      status: this._status,
      currentLoad: 0.5, // 默认值
      estimatedWaitTime: 0,
      capabilities: this._config.capabilities
    };
  }
  
  async requestCollaboration(targetAgents: AgentType[], description: string): Promise<CollaborationSession> {
    throw new Error('Collaboration not implemented in base class');
  }
  
  async getCollaborationStatus(sessionId: string): Promise<CollaborationStatus> {
    throw new Error('Collaboration status not implemented in base class');
  }
  
  // 事件监听器设置
  onStatusChanged(callback: (status: AgentStatus) => void): void {
    this.on('statusChanged', callback);
  }
  
  onMessageReceived(callback: (message: ChatMessage) => void): void {
    this.on('messageReceived', callback);
  }
  
  onDiagnosisCompleted(callback: (result: DiagnosisResult) => void): void {
    this.on('diagnosisCompleted', callback);
  }
  
  onCollaborationUpdate(callback: (status: CollaborationStatus) => void): void {
    this.on('collaborationUpdate', callback);
  }
  
  // 受保护的辅助方法
  protected updateStatus(status: AgentStatus): void {
    if (this._status !== status) {
      const oldStatus = this._status;
      this._status = status;
      this.emit('statusChanged', status, oldStatus);
    }
  }
  
  protected updateActivity(): void {
    this._lastActivity = new Date();
  }
  
  protected createChatMessage(content: string, role: 'user' | 'agent' | 'system' = 'agent'): ChatMessage {
    return {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      role,
      content,
      timestamp: new Date(),
      agentId: this._config.agentId,
      agentType: this._config.type
    };
  }
  
  protected createDiagnosisResult(
    type: string,
    summary: string,
    confidence: number,
    recommendations: Recommendation[] = []
  ): DiagnosisResult {
    return {
      id: `diag_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      summary,
      confidence,
      recommendations,
      processingTime: 0
    };
  }
}

// ============================================================================
// 工厂函数和工具
// ============================================================================

export interface FrontendAgentFactory {
  createAgent(config: FrontendAgentConfig): Promise<FrontendAgentInterface>;
  createManager(): Promise<FrontendAgentManager>;
  getSupportedTypes(): AgentType[];
}

export class DefaultFrontendAgentFactory implements FrontendAgentFactory {
  async createAgent(config: FrontendAgentConfig): Promise<FrontendAgentInterface> {
    // 根据智能体类型创建相应的实现
    switch (config.type) {
      case AgentType.XIAOAI:
        return new XiaoaiFrontendAgent(config);
      case AgentType.XIAOKE:
        return new XiaokeFrontendAgent(config);
      case AgentType.LAOKE:
        return new LaokeFrontendAgent(config);
      case AgentType.SOER:
        return new SoerFrontendAgent(config);
      default:
        throw new Error(`Unsupported agent type: ${config.type}`);
    }
  }
  
  async createManager(): Promise<FrontendAgentManager> {
    return new DefaultFrontendAgentManager();
  }
  
  getSupportedTypes(): AgentType[] {
    return [AgentType.XIAOAI, AgentType.XIAOKE, AgentType.LAOKE, AgentType.SOER];
  }
}

// ============================================================================
// 具体智能体实现（占位符）
// ============================================================================

class XiaoaiFrontendAgent extends BaseFrontendAgent {
  async connect(): Promise<void> {
    this._isConnected = true;
    this.updateStatus(AgentStatus.AVAILABLE);
  }
  
  async disconnect(): Promise<void> {
    this._isConnected = false;
    this.updateStatus(AgentStatus.OFFLINE);
  }
  
  async sendMessage(content: string, context: AgentContext): Promise<ChatMessage> {
    this.updateActivity();
    // 这里应该调用 Agentic AI 系统
    return this.createChatMessage(`小艾回复: ${content}`);
  }
  
  async requestDiagnosis(request: DiagnosisRequest): Promise<DiagnosisResult> {
    this.updateActivity();
    // 这里应该调用 Agentic AI 系统的诊断功能
    return this.createDiagnosisResult(
      request.type,
      '基于中医四诊的综合分析结果',
      0.85,
      [
        {
          category: 'lifestyle',
          title: '饮食调理建议',
          description: '建议清淡饮食，多食用温性食物',
          priority: 'medium'
        }
      ]
    );
  }
}

class XiaokeFrontendAgent extends BaseFrontendAgent {
  async connect(): Promise<void> {
    this._isConnected = true;
    this.updateStatus(AgentStatus.AVAILABLE);
  }
  
  async disconnect(): Promise<void> {
    this._isConnected = false;
    this.updateStatus(AgentStatus.OFFLINE);
  }
  
  async sendMessage(content: string, context: AgentContext): Promise<ChatMessage> {
    this.updateActivity();
    return this.createChatMessage(`小克回复: ${content}`);
  }
  
  async requestDiagnosis(request: DiagnosisRequest): Promise<DiagnosisResult> {
    this.updateActivity();
    return this.createDiagnosisResult(
      request.type,
      '名医资源匹配和服务推荐',
      0.90,
      [
        {
          category: 'consultation',
          title: '专家预约建议',
          description: '推荐预约相关领域的专家医生',
          priority: 'high'
        }
      ]
    );
  }
}

class LaokeFrontendAgent extends BaseFrontendAgent {
  async connect(): Promise<void> {
    this._isConnected = true;
    this.updateStatus(AgentStatus.AVAILABLE);
  }
  
  async disconnect(): Promise<void> {
    this._isConnected = false;
    this.updateStatus(AgentStatus.OFFLINE);
  }
  
  async sendMessage(content: string, context: AgentContext): Promise<ChatMessage> {
    this.updateActivity();
    return this.createChatMessage(`老克回复: ${content}`);
  }
  
  async requestDiagnosis(request: DiagnosisRequest): Promise<DiagnosisResult> {
    this.updateActivity();
    return this.createDiagnosisResult(
      request.type,
      '知识库检索和学习建议',
      0.80,
      [
        {
          category: 'monitoring',
          title: '健康知识学习',
          description: '提供相关的健康知识和学习资源',
          priority: 'medium'
        }
      ]
    );
  }
}

class SoerFrontendAgent extends BaseFrontendAgent {
  async connect(): Promise<void> {
    this._isConnected = true;
    this.updateStatus(AgentStatus.AVAILABLE);
  }
  
  async disconnect(): Promise<void> {
    this._isConnected = false;
    this.updateStatus(AgentStatus.OFFLINE);
  }
  
  async sendMessage(content: string, context: AgentContext): Promise<ChatMessage> {
    this.updateActivity();
    return this.createChatMessage(`索儿回复: ${content}`);
  }
  
  async requestDiagnosis(request: DiagnosisRequest): Promise<DiagnosisResult> {
    this.updateActivity();
    return this.createDiagnosisResult(
      request.type,
      '生活数据分析和健康趋势',
      0.88,
      [
        {
          category: 'lifestyle',
          title: '生活方式优化',
          description: '基于数据分析的生活方式改进建议',
          priority: 'medium'
        }
      ]
    );
  }
}

// ============================================================================
// 前端智能体管理器实现
// ============================================================================

class DefaultFrontendAgentManager extends EventEmitter implements FrontendAgentManager {
  private agents: Map<string, FrontendAgentInterface> = new Map();
  private factory: FrontendAgentFactory = new DefaultFrontendAgentFactory();
  
  async getAvailableAgents(): Promise<FrontendAgentConfig[]> {
    const configs: FrontendAgentConfig[] = [];
    for (const agent of this.agents.values()) {
      if (agent.getStatus() === AgentStatus.AVAILABLE) {
        configs.push(agent.config);
      }
    }
    return configs;
  }
  
  async getAgent(agentId: string): Promise<FrontendAgentInterface | null> {
    return this.agents.get(agentId) || null;
  }
  
  async getAgentByType(type: AgentType): Promise<FrontendAgentInterface | null> {
    for (const agent of this.agents.values()) {
      if (agent.config.type === type && agent.getStatus() === AgentStatus.AVAILABLE) {
        return agent;
      }
    }
    return null;
  }
  
  async selectBestAgent(request: DiagnosisRequest): Promise<FrontendAgentInterface | null> {
    // 简单的智能体选择逻辑
    switch (request.type) {
      case 'comprehensive':
        return await this.getAgentByType(AgentType.XIAOAI);
      case 'inquiry':
        return await this.getAgentByType(AgentType.XIAOAI);
      default:
        return await this.getAgentByType(AgentType.XIAOAI);
    }
  }
  
  async selectAgentsForCollaboration(request: DiagnosisRequest): Promise<FrontendAgentInterface[]> {
    const agents: FrontendAgentInterface[] = [];
    
    // 根据请求类型选择合适的智能体组合
    if (request.type === 'comprehensive') {
      const xiaoai = await this.getAgentByType(AgentType.XIAOAI);
      const soer = await this.getAgentByType(AgentType.SOER);
      if (xiaoai) agents.push(xiaoai);
      if (soer) agents.push(soer);
    }
    
    return agents;
  }
  
  async getSystemStatus(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    availableAgents: number;
    totalAgents: number;
    averageResponseTime: number;
  }> {
    const totalAgents = this.agents.size;
    const availableAgents = Array.from(this.agents.values())
      .filter(agent => agent.getStatus() === AgentStatus.AVAILABLE).length;
    
    let status: 'healthy' | 'degraded' | 'unhealthy';
    if (availableAgents === totalAgents) {
      status = 'healthy';
    } else if (availableAgents > totalAgents / 2) {
      status = 'degraded';
    } else {
      status = 'unhealthy';
    }
    
    return {
      status,
      availableAgents,
      totalAgents,
      averageResponseTime: 150 // 默认值
    };
  }
  
  async broadcastMessage(content: string, context: AgentContext, targetTypes?: AgentType[]): Promise<ChatMessage[]> {
    const messages: ChatMessage[] = [];
    
    for (const agent of this.agents.values()) {
      if (!targetTypes || targetTypes.includes(agent.config.type)) {
        try {
          const message = await agent.sendMessage(content, context);
          messages.push(message);
        } catch (error) {
          console.error(`Failed to send message to agent ${agent.config.agentId}:`, error);
        }
      }
    }
    
    return messages;
  }
  
  onAgentAvailable(callback: (agent: FrontendAgentConfig) => void): void {
    this.on('agentAvailable', callback);
  }
  
  onAgentUnavailable(callback: (agentId: string) => void): void {
    this.on('agentUnavailable', callback);
  }
  
  onSystemStatusChanged(callback: (status: string) => void): void {
    this.on('systemStatusChanged', callback);
  }
}

// ============================================================================
// 导出
// ============================================================================

export {
  FrontendAgentInterface,
  FrontendAgentManager,
  BaseFrontendAgent,
  FrontendAgentFactory,
  DefaultFrontendAgentFactory,
  DefaultFrontendAgentManager
};
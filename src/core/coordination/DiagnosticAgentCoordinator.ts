import { EventEmitter } from 'events';
import { Logger } from '../monitoring/Logger';
import { MetricsCollector } from '../monitoring/MetricsCollector';
import { ErrorHandler } from '../error/ErrorHandler';
export interface DiagnosticResult {
  serviceType: 'calculation' | 'look' | 'listen' | 'inquiry' | 'palpation';,
  timestamp: number;,
  data: any;,
  confidence: number;,
  metadata: {;,
  sessionId: string;,
  userId: string;,
  version: string;
};
}
export interface AgentResponse {
  agentType: 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';,
  timestamp: number;,
  analysis: any;,
  recommendations: any[];,
  confidence: number;,
  metadata: {;,
  sessionId: string;,
  userId: string;,
  version: string;
};
}
export interface CoordinationSession {
  sessionId: string;,
  userId: string;,
  startTime: number;,
  diagnosticResults: DiagnosticResult[];,
  agentResponses: AgentResponse[];
  consensusResult?: any;
  status: 'active' | 'completed' | 'failed';
}
export class DiagnosticAgentCoordinator extends EventEmitter {
  private logger: Logger;
  private metrics: MetricsCollector;
  private errorHandler: ErrorHandler;
  private activeSessions: Map<string, CoordinationSession>;
  private consensusThreshold: number;
  constructor() {
    super();
    this.logger = new Logger('DiagnosticAgentCoordinator');
    this.metrics = new MetricsCollector();
    this.errorHandler = new ErrorHandler();
    this.activeSessions = new Map();
    this.consensusThreshold = 0.75; // 75%一致性阈值
  }
  /**
  * 启动诊断-智能体协同会话
  */
  async startCoordinationSession(userId: string, sessionId?: string): Promise<string> {
    try {
      const id = sessionId || this.generateSessionId();
      const session: CoordinationSession = {,
  sessionId: id,
        userId,
        startTime: Date.now(),
        diagnosticResults: [],
        agentResponses: [],
        status: 'active'
      };
      this.activeSessions.set(id, session);
      this.logger.info(`协同会话已启动: ${id}`, { userId });
      this.metrics.incrementCounter('coordination_sessions_started');
      this.emit('sessionStarted', { sessionId: id, userId });
      return id;
    } catch (error) {
      this.errorHandler.handleError(error, 'startCoordinationSession');
      throw error;
    }
  }
  /**
  * 接收诊断服务结果
  */
  async receiveDiagnosticResult(sessionId: string, result: DiagnosticResult): Promise<void> {
    try {
      const session = this.activeSessions.get(sessionId);
      if (!session) {
        throw new Error(`会话不存在: ${sessionId}`);
      }
      session.diagnosticResults.push(result);
      this.logger.info(`收到诊断结果: ${result.serviceType}`, {
        sessionId,
        confidence: result.confidence;
      });
      this.metrics.incrementCounter('diagnostic_results_received', {
        service: result.serviceType;
      });
      this.emit('diagnosticResultReceived', { sessionId, result });
      // 检查是否可以触发智能体分析
      await this.checkForAgentTrigger(sessionId);
    } catch (error) {
      this.errorHandler.handleError(error, 'receiveDiagnosticResult');
      throw error;
    }
  }
  /**
  * 接收智能体响应
  */
  async receiveAgentResponse(sessionId: string, response: AgentResponse): Promise<void> {
    try {
      const session = this.activeSessions.get(sessionId);
      if (!session) {
        throw new Error(`会话不存在: ${sessionId}`);
      }
      session.agentResponses.push(response);
      this.logger.info(`收到智能体响应: ${response.agentType}`, {
        sessionId,
        confidence: response.confidence;
      });
      this.metrics.incrementCounter('agent_responses_received', {
        agent: response.agentType;
      });
      this.emit('agentResponseReceived', { sessionId, response });
      // 检查是否可以生成共识结果
      await this.checkForConsensus(sessionId);
    } catch (error) {
      this.errorHandler.handleError(error, 'receiveAgentResponse');
      throw error;
    }
  }
  /**
  * 检查是否触发智能体分析
  */
  private async checkForAgentTrigger(sessionId: string): Promise<void> {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      return;
    }
    // 当收集到足够的诊断数据时，触发智能体分析
    const diagnosticTypes = new Set(session.diagnosticResults.map(r => r.serviceType));
    if (diagnosticTypes.size >= 3) {
      // 至少3种诊断类型
      this.emit('triggerAgentAnalysis', {
        sessionId,
        diagnosticResults: session.diagnosticResults;
      });
    }
  }
  /**
  * 检查智能体共识
  */
  private async checkForConsensus(sessionId: string): Promise<void> {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      return;
    }
    // 当收集到足够的智能体响应时，计算共识
    if (session.agentResponses.length >= 2) {
      // 至少2个智能体响应
      const consensus = await this.calculateConsensus(session);
      if (consensus.confidence >= this.consensusThreshold) {
        session.consensusResult = consensus;
        session.status = 'completed';
        this.logger.info(`达成共识`, {
          sessionId,
          confidence: consensus.confidence;
        });
        this.metrics.incrementCounter('consensus_reached');
        this.emit('consensusReached', {
          sessionId,
          consensus: consensus.result,
          confidence: consensus.confidence;
        });
      }
    }
  }
  /**
  * 计算智能体共识
  */
  private async calculateConsensus()
    session: CoordinationSession;
  ): Promise<{ result: any; confidence: number }> {
    const responses = session.agentResponses;
    // 简化的共识算法：基于置信度加权平均
    let totalWeight = 0;
    let weightedSum = 0;
    const consensusData: any = {};
    responses.forEach(response => {
      totalWeight += response.confidence;
      weightedSum += response.confidence;
      // 合并分析结果
      if (response.analysis) {
        Object.keys(response.analysis).forEach(key => {
          if (!consensusData[key]) {
            consensusData[key] = [];
          }
          consensusData[key].push({
            value: response.analysis[key],
            weight: response.confidence,
            agent: response.agentType;
          });
        });
      }
    });
    const confidence = totalWeight / responses.length;
    // 生成最终共识结果
    const finalResult: any = {};
    Object.keys(consensusData).forEach(key => {
      const items = consensusData[key];
      const weightedAvg =
        items.reduce(sum: number, item: any) => sum + item.value * item.weight, 0) /;
        items.reduce(sum: number, item: any) => sum + item.weight, 0);
      finalResult[key] = {
        value: weightedAvg,
        sources: items.map(item: any) => item.agent),
        confidence: items.reduce(sum: number, item: any) => sum + item.weight, 0) / items.length;
      };
    });
    return {result: finalResult,confidence;
    };
  }
  /**
  * 获取会话状态
  */
  getSessionStatus(sessionId: string): CoordinationSession | null {
    return this.activeSessions.get(sessionId) || null;
  }
  /**
  * 结束协同会话
  */
  async endSession(sessionId: string): Promise<void> {
    const session = this.activeSessions.get(sessionId);
    if (session) {
      session.status = 'completed';
      this.activeSessions.delete(sessionId);
      this.logger.info(`协同会话已结束: ${sessionId}`);
      this.metrics.incrementCounter('coordination_sessions_ended');
      this.emit('sessionEnded', { sessionId });
    }
  }
  /**
  * 生成会话ID;
  */
  private generateSessionId(): string {
    return `coord_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  /**
  * 获取活跃会话数量
  */
  getActiveSessionCount(): number {
    return this.activeSessions.size;
  }
  /**
  * 清理过期会话
  */
  async cleanupExpiredSessions(maxAge: number = 3600000): Promise<void> {
    const now = Date.now();
    const expiredSessions: string[] = [];
    for (const [sessionId, session] of this.activeSessions.entries()) {
      if (now - session.startTime > maxAge) {
        expiredSessions.push(sessionId);
      }
    }
    for (const sessionId of expiredSessions) {
      await this.endSession(sessionId);
    }
    if (expiredSessions.length > 0) {
      this.logger.info(`清理了${expiredSessions.length}个过期会话`);
    }
  }
}
export default DiagnosticAgentCoordinator;
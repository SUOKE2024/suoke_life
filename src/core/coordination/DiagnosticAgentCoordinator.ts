import { EventEmitter } from 'events';
import { Logger } from '../monitoring/Logger';
import { MetricsCollector } from '../monitoring/MetricsCollector';
import { ErrorHandler } from '../error/ErrorHandler';

export interface DiagnosticResult {
  serviceType: 'calculation' | 'look' | 'listen' | 'inquiry' | 'palpation';
  timestamp: number;
  data: any;
  confidence: number;
  metadata: {
    sessionId: string;
    userId: string;
    version: string;
  };
}

export interface AgentResponse {
  agentType: 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';
  timestamp: number;
  analysis: any;
  recommendations: any[];
  confidence: number;
  metadata: {
    sessionId: string;
    userId: string;
    version: string;
  };
}

export interface CoordinationSession {
  sessionId: string;
  userId: string;
  startTime: number;
  diagnosticResults: DiagnosticResult[];
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
      const session: CoordinationSession = {
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
      this.logger.info(`收到诊断结果: ${result.serviceType}`, { sessionId, confidence: result.confidence });
      this.metrics.incrementCounter('diagnostic_results_received', { service: result.serviceType });

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
      this.logger.info(`收到智能体响应: ${response.agentType}`, { sessionId, confidence: response.confidence });
      this.metrics.incrementCounter('agent_responses_received', { agent: response.agentType });

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
    if (!session) return;

    // 当收集到足够的诊断数据时，触发智能体分析
    const diagnosticTypes = new Set(session.diagnosticResults.map(r => r.serviceType));
    
    if (diagnosticTypes.size >= 3) { // 至少3种诊断类型
      this.emit('triggerAgentAnalysis', {
        sessionId,
        diagnosticResults: session.diagnosticResults
      });
    }
  }

  /**
   * 检查智能体共识
   */
  private async checkForConsensus(sessionId: string): Promise<void> {
    const session = this.activeSessions.get(sessionId);
    if (!session) return;

    // 当收集到足够的智能体响应时，计算共识
    if (session.agentResponses.length >= 2) { // 至少2个智能体响应
      const consensus = await this.calculateConsensus(session);
      
      if (consensus.confidence >= this.consensusThreshold) {
        session.consensusResult = consensus;
        session.status = 'completed';
        
        this.logger.info(`达成共识`, { sessionId, confidence: consensus.confidence });
        this.metrics.incrementCounter('consensus_reached');
        
        this.emit('consensusReached', {
          sessionId,
          consensus: consensus.result,
          confidence: consensus.confidence
        });
      }
    }
  }

  /**
   * 计算智能体共识
   */
  private async calculateConsensus(session: CoordinationSession): Promise<{ result: any; confidence: number }> {
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
            agent: response.agentType
          });
        });
      }
    });

    const confidence = totalWeight / responses.length;

    // 生成最终共识结果
    const finalResult: any = {};
    Object.keys(consensusData).forEach(key => {
      const items = consensusData[key];
      const weightedAvg = items.reduce((sum: number, item: any) => 
        sum + (item.value * item.weight), 0) / items.reduce((sum: number, item: any) => 
        sum + item.weight, 0);
      
      finalResult[key] = {
        value: weightedAvg,
        sources: items.map((item: any) => item.agent),
        confidence: items.reduce((sum: number, item: any) => sum + item.weight, 0) / items.length
      };
    });

    return {
      result: finalResult,
      confidence
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
   * 验证诊断结果一致性
   */
  async validateDiagnosticConsistency(sessionId: string): Promise<{
    isConsistent: boolean;
    inconsistencies: string[];
    confidence: number;
  }> {
    const session = this.activeSessions.get(sessionId);
    if (!session) {
      throw new Error(`会话不存在: ${sessionId}`);
    }

    const inconsistencies: string[] = [];
    let consistencyScore = 1.0;

    // 检查诊断结果之间的一致性
    const results = session.diagnosticResults;
    
    // 时间一致性检查
    const timeSpan = Math.max(...results.map(r => r.timestamp)) - Math.min(...results.map(r => r.timestamp));
    if (timeSpan > 30 * 60 * 1000) { // 超过30分钟
      inconsistencies.push('诊断时间跨度过大');
      consistencyScore *= 0.9;
    }

    // 置信度一致性检查
    const confidences = results.map(r => r.confidence);
    const avgConfidence = confidences.reduce((a, b) => a + b, 0) / confidences.length;
    const confidenceVariance = confidences.reduce((sum, conf) => sum + Math.pow(conf - avgConfidence, 2), 0) / confidences.length;
    
    if (confidenceVariance > 0.1) { // 置信度差异过大
      inconsistencies.push('诊断置信度差异过大');
      consistencyScore *= 0.8;
    }

    return {
      isConsistent: inconsistencies.length === 0,
      inconsistencies,
      confidence: consistencyScore
    };
  }

  /**
   * 生成会话ID
   */
  private generateSessionId(): string {
    return `coord_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * 获取协同统计信息
   */
  getCoordinationStats(): {
    activeSessions: number;
    totalSessions: number;
    averageConsensusTime: number;
    consensusRate: number;
  } {
    return {
      activeSessions: this.activeSessions.size,
      totalSessions: this.metrics.getCounter('coordination_sessions_started') || 0,
      averageConsensusTime: this.metrics.getGauge('average_consensus_time') || 0,
      consensusRate: this.metrics.getGauge('consensus_rate') || 0
    };
  }
}

export default DiagnosticAgentCoordinator; 
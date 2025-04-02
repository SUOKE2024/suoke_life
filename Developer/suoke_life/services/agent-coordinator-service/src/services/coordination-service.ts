/**
 * 代理协调服务
 */
import { AgentService } from './agent-service';
import { SessionService } from './session-service';
import { KnowledgeService } from './knowledge-service';
import { Agent, AgentQueryResponse } from '../models/agent';
import { Session, SessionMessage } from '../models/session';
import { loadConfig } from '../utils/config-loader';
import { domainClassifier } from '../utils/domain-classifier';
import { v4 as uuidv4 } from 'uuid';
import logger from '../utils/logger';

export class CoordinationService {
  private agentService: AgentService;
  private sessionService: SessionService;
  private knowledgeService: KnowledgeService;
  private config = loadConfig();
  
  constructor() {
    this.agentService = new AgentService();
    this.sessionService = new SessionService();
    this.knowledgeService = new KnowledgeService();
  }
  
  /**
   * 智能路由请求
   */
  async routeRequest(
    sessionId: string,
    query: string,
    context?: Record<string, any>
  ): Promise<AgentQueryResponse> {
    try {
      // 获取会话
      const session = await this.sessionService.getSession(sessionId);
      
      if (!session) {
        throw new Error(`未找到会话: ${sessionId}`);
      }
      
      // 域名分类
      const domainClassifications = domainClassifier.classifyQuery(query);
      
      // 增强上下文，添加领域信息
      const enhancedContext = {
        ...context,
        domainClassifications,
        primaryDomain: domainClassifications[0]?.domain || 'general'
      };
      
      // 分析查询，确定最合适的代理
      const targetAgentId = await this.determineTargetAgent(query, session, enhancedContext);
      
      // 如果目标代理与当前代理不同，进行代理交接
      if (targetAgentId !== session.currentAgentId) {
        // 更新会话中的当前代理
        await this.sessionService.updateSession(sessionId, {
          currentAgentId: targetAgentId,
        });
        
        // 记录系统消息：代理交接
        await this.addSystemMessage(
          sessionId,
          `会话已从 ${session.currentAgentId} 交接给 ${targetAgentId}`
        );
      }
      
      // 记录用户消息
      await this.addUserMessage(sessionId, query);
      
      // 使用目标代理处理请求
      const response = await this.agentService.queryAgent(
        targetAgentId,
        sessionId,
        query,
        {
          ...context,
          userId: session.userId,
        }
      );
      
      // 记录代理响应
      await this.addAgentMessage(sessionId, response.content, targetAgentId);
      
      return response;
    } catch (error) {
      logger.error(`路由请求失败`, { error, sessionId });
      throw error;
    }
  }
  
  /**
   * 代理交接会话
   */
  async handoffSession(
    sessionId: string,
    fromAgentId: string,
    toAgentId: string,
    reason: string,
    context?: Record<string, any>
  ): Promise<{
    success: boolean;
    message: string;
    handoffId: string;
  }> {
    try {
      // 获取会话
      const session = await this.sessionService.getSession(sessionId);
      
      if (!session) {
        throw new Error(`未找到会话: ${sessionId}`);
      }
      
      // 检查源代理
      if (session.currentAgentId !== fromAgentId) {
        throw new Error(`当前会话未分配给代理: ${fromAgentId}`);
      }
      
      // 检查目标代理是否存在
      const targetAgent = await this.agentService.getAgentDetails(toAgentId);
      
      if (!targetAgent) {
        throw new Error(`未找到目标代理: ${toAgentId}`);
      }
      
      // 更新会话中的当前代理
      await this.sessionService.updateSession(sessionId, {
        currentAgentId: toAgentId,
      });
      
      // 生成交接ID
      const handoffId = uuidv4();
      
      // 记录系统消息：代理交接
      await this.addSystemMessage(
        sessionId,
        `会话已从 ${fromAgentId} 交接给 ${toAgentId}，原因: ${reason}`
      );
      
      return {
        success: true,
        message: `成功将会话从 ${fromAgentId} 交接给 ${toAgentId}`,
        handoffId,
      };
    } catch (error) {
      logger.error(`代理交接会话失败`, { error, sessionId, fromAgentId, toAgentId });
      throw error;
    }
  }
  
  /**
   * 分析用户查询内容
   */
  async analyzeQuery(
    query: string,
    context?: Record<string, any>
  ): Promise<{
    recommendedAgent: string;
    confidence: number;
    matchedKeywords: string[];
    domainClassifications: Array<{ domain: string; confidence: number; subdomains?: string[] }>;
    alternativeAgents: Array<{
      agentId: string;
      confidence: number;
    }>;
  }> {
    try {
      // 获取所有代理
      const agents = await this.agentService.listAgents();
      
      // 域名分类
      const domainClassifications = domainClassifier.classifyQuery(query);
      
      // 基于关键词匹配进行简单分析
      const results = this.analyzeQueryWithKeywords(query, agents);
      
      return {
        recommendedAgent: results.bestMatch.agentId,
        confidence: results.bestMatch.confidence,
        matchedKeywords: results.bestMatch.matchedKeywords,
        domainClassifications,
        alternativeAgents: results.alternatives,
      };
    } catch (error) {
      logger.error(`分析用户查询失败`, { error, queryLength: query.length });
      throw error;
    }
  }
  
  /**
   * 获取系统总体能力
   */
  async getSystemCapabilities(): Promise<{
    capabilities: string[];
    agentCapabilities: Record<string, string[]>;
  }> {
    try {
      // 获取所有代理
      const agents = await this.agentService.listAgents();
      
      // 提取所有能力
      const allCapabilities = new Set<string>();
      const agentCapabilities: Record<string, string[]> = {};
      
      agents.forEach(agent => {
        agent.capabilities.forEach(capability => {
          allCapabilities.add(capability);
        });
        
        agentCapabilities[agent.id] = agent.capabilities;
      });
      
      return {
        capabilities: Array.from(allCapabilities),
        agentCapabilities,
      };
    } catch (error) {
      logger.error(`获取系统总体能力失败`, { error });
      throw error;
    }
  }
  
  /**
   * 根据查询内容确定目标代理
   */
  private async determineTargetAgent(
    query: string,
    session: Session,
    context?: Record<string, any>
  ): Promise<string> {
    try {
      // 获取所有代理
      const agents = await this.agentService.listAgents();
      
      // 如果使用能力路由
      if (this.config.routing.routingMode === 'capability-based') {
        // 域名分类
        const domainClassifications = context.domainClassifications || 
                                      domainClassifier.classifyQuery(query);
        
        // 针对特定领域的路由逻辑
        const primaryDomain = domainClassifications[0]?.domain;
        if (primaryDomain) {
          // 精准医学和相关领域的查询路由到老克（知识管理智能体）
          if (['precisionMedicine', 'multimodalHealth', 'environmentalHealth', 'mentalHealth'].includes(primaryDomain)) {
            logger.info(`基于领域 ${primaryDomain} 路由到老克智能体`);
            return 'laoke';
          }
          
          // 健康相关查询路由到小艾（健康管理智能体）
          if (['traditionalCulture', 'modernMedicine'].includes(primaryDomain)) {
            logger.info(`基于领域 ${primaryDomain} 路由到小艾智能体`);
            return 'xiaoai';
          }
        }
        
        // 关键词分析作为备选
        const analysis = this.analyzeQueryWithKeywords(query, agents);
        
        // 如果匹配度较高，使用推荐的代理
        if (analysis.bestMatch.confidence > 0.5) {
          return analysis.bestMatch.agentId;
        }
      }
      
      // 如果低匹配度或其他原因，使用当前代理或回退代理
      return session.currentAgentId || this.config.routing.fallbackAgent;
    } catch (error) {
      logger.error(`确定目标代理失败`, { error, sessionId: session.id });
      
      // 出错时使用当前代理或回退代理
      return session.currentAgentId || this.config.routing.fallbackAgent;
    }
  }
  
  /**
   * 使用关键词匹配分析查询
   */
  private analyzeQueryWithKeywords(query: string, agents: Agent[]): {
    bestMatch: {
      agentId: string;
      confidence: number;
      matchedKeywords: string[];
    };
    alternatives: Array<{
      agentId: string;
      confidence: number;
    }>;
  } {
    const queryLower = query.toLowerCase();
    const results: Array<{
      agentId: string;
      confidence: number;
      matchedKeywords: string[];
    }> = [];
    
    // 对每个代理进行关键词匹配
    agents.forEach(agent => {
      const matchedKeywords: string[] = [];
      
      // 查找匹配的路由规则
      this.config.routing.routingRules.forEach(rule => {
        if (rule.route === agent.id) {
          rule.keywords.forEach(keyword => {
            if (queryLower.includes(keyword.toLowerCase())) {
              matchedKeywords.push(keyword);
            }
          });
        }
      });
      
      // 计算匹配度
      let confidence = 0;
      if (matchedKeywords.length > 0) {
        confidence = Math.min(matchedKeywords.length / 3, 1);
      }
      
      results.push({
        agentId: agent.id,
        confidence,
        matchedKeywords,
      });
    });
    
    // 按匹配度排序
    results.sort((a, b) => b.confidence - a.confidence);
    
    return {
      bestMatch: results[0] || {
        agentId: this.config.routing.fallbackAgent,
        confidence: 0,
        matchedKeywords: [],
      },
      alternatives: results.slice(1).map(r => ({
        agentId: r.agentId,
        confidence: r.confidence,
      })),
    };
  }
  
  /**
   * 添加用户消息
   */
  private async addUserMessage(sessionId: string, content: string): Promise<void> {
    const message: SessionMessage = {
      id: uuidv4(),
      sessionId,
      timestamp: new Date().toISOString(),
      role: 'user',
      content,
    };
    
    await this.sessionService.addSessionMessage(message);
  }
  
  /**
   * 添加代理消息
   */
  private async addAgentMessage(
    sessionId: string,
    content: string,
    agentId: string
  ): Promise<void> {
    const message: SessionMessage = {
      id: uuidv4(),
      sessionId,
      timestamp: new Date().toISOString(),
      role: 'agent',
      content,
      agentId,
    };
    
    await this.sessionService.addSessionMessage(message);
  }
  
  /**
   * 添加系统消息
   */
  private async addSystemMessage(sessionId: string, content: string): Promise<void> {
    const message: SessionMessage = {
      id: uuidv4(),
      sessionId,
      timestamp: new Date().toISOString(),
      role: 'system',
      content,
    };
    
    await this.sessionService.addSessionMessage(message);
  }
}
/**
 * 代理服务管理
 */
import axios from 'axios';
import { Agent, AgentQueryRequest, AgentQueryResponse } from '../models/agent';
import { loadConfig } from '../utils/config-loader';
import logger from '../utils/logger';
import { AgentNotFoundError } from '../utils/error-handler';

export class AgentService {
  private config = loadConfig();
  
  /**
   * 获取代理列表
   */
  async listAgents(): Promise<Agent[]> {
    return this.config.agents.map(agent => ({
      id: agent.id,
      name: agent.name,
      capabilities: agent.capabilities,
      description: agent.description,
      serviceUrl: agent.serviceUrl || '',
      status: agent.status || 'active',
      metadata: agent.metadata || {},
      isDefault: agent.isDefault,
    }));
  }
  
  /**
   * 获取所有代理（为了兼容测试用例）
   */
  async getAllAgents(): Promise<Agent[]> {
    return this.listAgents();
  }
  
  /**
   * 获取代理详情
   */
  async getAgentDetails(agentId: string): Promise<Agent | null> {
    // 查找指定代理
    const agent = this.config.agents.find(a => a.id === agentId);
    
    if (!agent) {
      return null;
    }
    
    return {
      id: agent.id,
      name: agent.name,
      serviceUrl: agent.serviceUrl,
      capabilities: agent.capabilities,
      description: agent.description,
      status: agent.status || 'active',
      metadata: agent.metadata || {},
      isDefault: agent.isDefault,
    };
  }
  
  /**
   * 根据ID获取代理（为了兼容测试用例）
   */
  async getAgentById(agentId: string): Promise<Agent> {
    const agent = await this.getAgentDetails(agentId);
    
    if (!agent) {
      throw new AgentNotFoundError(agentId);
    }
    
    return agent;
  }
  
  /**
   * 检查代理是否具有指定能力
   */
  async checkAgentCapability(agentId: string, capability: string): Promise<boolean> {
    const agent = await this.getAgentById(agentId);
    return agent.capabilities.includes(capability);
  }
  
  /**
   * 向代理发送查询请求
   */
  async queryAgent(
    agentId: string,
    sessionId: string,
    query: string,
    context?: Record<string, any>
  ): Promise<AgentQueryResponse> {
    try {
      // 获取代理详情
      const agent = await this.getAgentDetails(agentId);
      
      if (!agent) {
        throw new Error(`未找到代理: ${agentId}`);
      }
      
      // 构建请求参数
      const requestData: AgentQueryRequest = {
        sessionId,
        userId: context?.userId || '',
        message: query,
        context,
        metadata: context?.metadata || {},
      };
      
      // 发送请求到代理服务
      const response = await axios.post(
        `${agent.serviceUrl}/api/query`,
        requestData,
        {
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': process.env.API_KEY || '',
            'X-Agent-Coordinator': 'true',
          },
          timeout: 30000, // 30秒超时
        }
      );
      
      // 返回响应
      return {
        ...response.data.data,
        content: response.data.data.content || '',
      };
    } catch (error) {
      logger.error(`查询代理失败`, { error, agentId, sessionId });
      
      // 构建错误响应
      return {
        content: `很抱歉，连接${agentId}代理服务时出现问题，请稍后再试。`,
        metadata: {
          error: error instanceof Error ? error.message : String(error),
        },
      };
    }
  }
  
  /**
   * 检查代理健康状态
   */
  async checkAgentHealth(agentId: string): Promise<boolean> {
    try {
      // 获取代理详情
      const agent = await this.getAgentDetails(agentId);
      
      if (!agent) {
        return false;
      }
      
      // 发送健康检查请求
      const response = await axios.get(
        `${agent.serviceUrl}/health`,
        {
          timeout: 5000, // 5秒超时
        }
      );
      
      return response.status === 200;
    } catch (error) {
      logger.error(`检查代理健康状态失败`, { error, agentId });
      return false;
    }
  }
}
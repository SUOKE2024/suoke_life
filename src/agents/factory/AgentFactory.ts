import { AgentBase } from '../base/AgentBase';
import { LaokeAgentImpl } from '../laoke/LaokeAgentImpl';
import { SoerAgentImpl } from '../soer/SoerAgentImpl';
import { AgentType } from '../types/agents';
import { XiaoaiAgentImpl } from '../xiaoai/XiaoaiAgentImpl';
import { XiaokeAgentImpl } from '../xiaoke/XiaokeAgentImpl';

/**
 * 智能体工厂配置接口
 */
export interface AgentFactoryConfig {
  enableLogging?: boolean;
  defaultTimeout?: number;
  maxRetries?: number;
  enableMetrics?: boolean;
}

/**
 * 智能体创建选项
 */
export interface AgentCreationOptions {
  id?: string;
  name?: string;
  config?: Record<string, any>;
  timeout?: number;
  retries?: number;
}

/**
 * 智能体工厂类
 * 负责创建和管理四个核心智能体实例
 */
export class AgentFactory {
  private static instance: AgentFactory;
  private agentInstances: Map<string, AgentBase> = new Map();
  private config: AgentFactoryConfig;
  private isInitialized: boolean = false;

  constructor(config: AgentFactoryConfig = {}) {
    this.config = {
      enableLogging: true,
      defaultTimeout: 30000,
      maxRetries: 3,
      enableMetrics: false,
      ...config,
    };
  }

  /**
   * 获取工厂单例实例
   */
  static getInstance(config?: AgentFactoryConfig): AgentFactory {
    if (!AgentFactory.instance) {
      AgentFactory.instance = new AgentFactory(config);
    }
    return AgentFactory.instance;
  }

  /**
   * 初始化工厂
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      this.log('warn', 'AgentFactory已经初始化');
      return;
    }

    try {
      this.log('info', '正在初始化智能体工厂...');

      // 预创建核心智能体实例
      await this.preCreateCoreAgents();

      this.isInitialized = true;
      this.log('info', '智能体工厂初始化完成');
    } catch (error) {
      this.log('error', '智能体工厂初始化失败', error);
      throw error;
    }
  }

  /**
   * 预创建核心智能体实例
   */
  private async preCreateCoreAgents(): Promise<void> {
    const coreAgents: Array<{ type: AgentType; id: string; name: string }> = [
      { type: AgentType.XIAOAI, id: 'xiaoai', name: '小艾' },
      { type: AgentType.XIAOKE, id: 'xiaoke', name: '小克' },
      { type: AgentType.LAOKE, id: 'laoke', name: '老克' },
      { type: AgentType.SOER, id: 'soer', name: '索儿' },
    ];

    for (const agentInfo of coreAgents) {
      try {
        const agent = await this.createAgent(agentInfo.type, {
          id: agentInfo.id,
          name: agentInfo.name,
        });
        this.log('info', `核心智能体 ${agentInfo.name} 创建成功`);
      } catch (error) {
        this.log('error', `创建核心智能体 ${agentInfo.name} 失败`, error);
        throw error;
      }
    }
  }

  /**
   * 创建智能体实例
   */
  async createAgent(
    type: AgentType,
    options: AgentCreationOptions = {}
  ): Promise<AgentBase> {
    try {
      this.log('info', `正在创建智能体: ${type}`);

      // 检查是否已存在实例
      const instanceId = options.id || this.generateAgentId(type);
      if (this.agentInstances.has(instanceId)) {
        this.log('warn', `智能体实例 ${instanceId} 已存在，返回现有实例`);
        return this.agentInstances.get(instanceId)!;
      }

      // 创建智能体实例
      const agent = await this.instantiateAgent(type, options);

      // 初始化智能体
      await this.initializeAgent(agent, options);

      // 注册实例
      this.agentInstances.set(instanceId, agent);

      this.log('info', `智能体 ${type} 创建成功，ID: ${instanceId}`);
      return agent;
    } catch (error) {
      this.log('error', `创建智能体 ${type} 失败`, error);
      throw new Error(
        `Failed to create agent ${type}: ${(error as Error).message}`
      );
    }
  }

  /**
   * 实例化具体的智能体类
   */
  private async instantiateAgent(
    type: AgentType,
    options: AgentCreationOptions
  ): Promise<AgentBase> {
    switch (type) {
      case AgentType.XIAOAI:
        return new XiaoaiAgentImpl();

      case AgentType.XIAOKE:
        return new XiaokeAgentImpl();

      case AgentType.LAOKE:
        return new LaokeAgentImpl();

      case AgentType.SOER:
        return new SoerAgentImpl();

      default:
        throw new Error(`不支持的智能体类型: ${type}`);
    }
  }

  /**
   * 初始化智能体
   */
  private async initializeAgent(
    agent: AgentBase,
    options: AgentCreationOptions
  ): Promise<void> {
    try {
      // 初始化智能体
      await agent.initialize();

      this.log('info', `智能体 ${agent.getName()} 初始化完成`);
    } catch (error) {
      this.log('error', `智能体 ${agent.getName()} 初始化失败`, error);
      throw error;
    }
  }

  /**
   * 获取智能体实例
   */
  getAgent(id: string): AgentBase | undefined {
    return this.agentInstances.get(id);
  }

  /**
   * 获取指定类型的智能体
   */
  getAgentByType(type: AgentType): AgentBase | undefined {
    for (const agent of this.agentInstances.values()) {
      if (agent.getAgentType() === type) {
        return agent;
      }
    }
    return undefined;
  }

  /**
   * 获取所有智能体实例
   */
  getAllAgents(): Map<string, AgentBase> {
    return new Map(this.agentInstances);
  }

  /**
   * 获取核心智能体组合
   */
  getCoreAgents(): {
    xiaoai?: AgentBase;
    xiaoke?: AgentBase;
    laoke?: AgentBase;
    soer?: AgentBase;
  } {
    return {
      xiaoai: this.getAgentByType(AgentType.XIAOAI),
      xiaoke: this.getAgentByType(AgentType.XIAOKE),
      laoke: this.getAgentByType(AgentType.LAOKE),
      soer: this.getAgentByType(AgentType.SOER),
    };
  }

  /**
   * 销毁智能体实例
   */
  async destroyAgent(id: string): Promise<boolean> {
    const agent = this.agentInstances.get(id);
    if (!agent) {
      this.log('warn', `智能体 ${id} 不存在`);
      return false;
    }

    try {
      await agent.shutdown();
      this.agentInstances.delete(id);
      this.log('info', `智能体 ${id} 已销毁`);
      return true;
    } catch (error) {
      this.log('error', `销毁智能体 ${id} 失败`, error);
      return false;
    }
  }

  /**
   * 销毁所有智能体实例
   */
  async destroyAllAgents(): Promise<void> {
    this.log('info', '正在销毁所有智能体实例...');

    const destroyPromises = Array.from(this.agentInstances.keys()).map((id) =>
      this.destroyAgent(id)
    );

    await Promise.allSettled(destroyPromises);
    this.agentInstances.clear();

    this.log('info', '所有智能体实例已销毁');
  }

  /**
   * 重启智能体
   */
  async restartAgent(id: string): Promise<AgentBase | undefined> {
    const agent = this.agentInstances.get(id);
    if (!agent) {
      this.log('warn', `智能体 ${id} 不存在`);
      return undefined;
    }

    try {
      const agentType = agent.getAgentType();

      // 销毁现有实例
      await this.destroyAgent(id);

      // 重新创建
      return await this.createAgent(agentType, { id });
    } catch (error) {
      this.log('error', `重启智能体 ${id} 失败`, error);
      throw error;
    }
  }

  /**
   * 检查智能体健康状态
   */
  async checkAgentHealth(id: string): Promise<boolean> {
    const agent = this.agentInstances.get(id);
    if (!agent) {
      return false;
    }

    try {
      const health = await agent.getHealthStatus();
      return health && health.status === 'healthy';
    } catch (error) {
      this.log('error', `检查智能体 ${id} 健康状态失败`, error);
      return false;
    }
  }

  /**
   * 获取工厂统计信息
   */
  getFactoryStats(): {
    totalAgents: number;
    agentsByType: Record<string, number>;
    healthyAgents: number;
    isInitialized: boolean;
  } {
    const agentsByType: Record<string, number> = {};
    let healthyAgents = 0;

    for (const agent of this.agentInstances.values()) {
      const type = agent.getAgentType();
      agentsByType[type] = (agentsByType[type] || 0) + 1;

      // 简化的健康检查
      try {
        if (agent.isReady()) {
          healthyAgents++;
        }
      } catch {
        // 忽略健康检查错误
      }
    }

    return {
      totalAgents: this.agentInstances.size,
      agentsByType,
      healthyAgents,
      isInitialized: this.isInitialized,
    };
  }

  /**
   * 生成智能体ID
   */
  private generateAgentId(type: AgentType): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 8);
    return `${type.toLowerCase()}_${timestamp}_${random}`;
  }

  /**
   * 获取默认智能体名称
   */
  private getDefaultAgentName(type: AgentType): string {
    const nameMap: Record<AgentType, string> = {
      [AgentType.XIAOAI]: '小艾',
      [AgentType.XIAOKE]: '小克',
      [AgentType.LAOKE]: '老克',
      [AgentType.SOER]: '索儿',
    };
    return nameMap[type] || type;
  }

  /**
   * 关闭工厂
   */
  async shutdown(): Promise<void> {
    this.log('info', '正在关闭智能体工厂...');

    try {
      await this.destroyAllAgents();
      this.isInitialized = false;
      this.log('info', '智能体工厂已关闭');
    } catch (error) {
      this.log('error', '关闭智能体工厂失败', error);
      throw error;
    }
  }

  /**
   * 重置工厂
   */
  async reset(): Promise<void> {
    await this.shutdown();
    await this.initialize();
  }

  /**
   * 日志记录
   */
  private log(
    level: 'info' | 'warn' | 'error',
    message: string,
    data?: any
  ): void {
    if (!this.config.enableLogging) {
      return;
    }

    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [AgentFactory] [${level.toUpperCase()}] ${message}`;

    switch (level) {
      case 'info':
        console.log(logMessage, data || '');
        break;
      case 'warn':
        console.warn(logMessage, data || '');
        break;
      case 'error':
        console.error(logMessage, data || '');
        break;
    }
  }
}

/**
 * 默认工厂实例
 */
export const defaultAgentFactory = AgentFactory.getInstance();

/**
 * 便捷方法：创建小艾智能体
 */
export async function createXiaoaiAgent(
  options?: AgentCreationOptions
): Promise<AgentBase> {
  return defaultAgentFactory.createAgent(AgentType.XIAOAI, options);
}

/**
 * 便捷方法：创建小克智能体
 */
export async function createXiaokeAgent(
  options?: AgentCreationOptions
): Promise<AgentBase> {
  return defaultAgentFactory.createAgent(AgentType.XIAOKE, options);
}

/**
 * 便捷方法：创建老克智能体
 */
export async function createLaokeAgent(
  options?: AgentCreationOptions
): Promise<AgentBase> {
  return defaultAgentFactory.createAgent(AgentType.LAOKE, options);
}

/**
 * 便捷方法：创建索儿智能体
 */
export async function createSoerAgent(
  options?: AgentCreationOptions
): Promise<AgentBase> {
  return defaultAgentFactory.createAgent(AgentType.SOER, options);
}

/**
 * 便捷方法：获取所有核心智能体
 */
export async function createAllCoreAgents(): Promise<{
  xiaoai: AgentBase;
  xiaoke: AgentBase;
  laoke: AgentBase;
  soer: AgentBase;
}> {
  const factory = defaultAgentFactory;

  const [xiaoai, xiaoke, laoke, soer] = await Promise.all([
    factory.createAgent(AgentType.XIAOAI, { id: 'xiaoai', name: '小艾' }),
    factory.createAgent(AgentType.XIAOKE, { id: 'xiaoke', name: '小克' }),
    factory.createAgent(AgentType.LAOKE, { id: 'laoke', name: '老克' }),
    factory.createAgent(AgentType.SOER, { id: 'soer', name: '索儿' }),
  ]);

  return { xiaoai, xiaoke, laoke, soer };
}

export default AgentFactory;

import { AgentType, AgentCapability, AgentContext } from '../types';
import { AgentBase } from '../base/AgentBase';
import { XiaoaiAgentImpl } from '../xiaoai/XiaoaiAgentImpl';
import { XiaokeAgentImpl } from '../xiaoke/XiaokeAgentImpl';
import { LaokeAgentImpl } from '../laoke/LaokeAgentImpl';
import { SoerAgentImpl } from '../soer/SoerAgentImpl';
/**
* 智能体配置接口
*/
export interface AgentConfig {
  agentType: AgentType;
  capabilities?: AgentCapability[];
  customSettings?: Record<string, any>;
  enableLogging?: boolean;
  maxConcurrentTasks?: number;
  timeout?: number;
}
/**
* 智能体实例信息
*/
export interface AgentInstance {
  id: string;,
  type: AgentType;,
  agent: AgentBase;,
  config: AgentConfig;,
  createdAt: Date;,
  lastUsed: Date;,
  isActive: boolean;
}
/**
* 智能体工厂类
* 负责智能体的创建、配置、缓存和生命周期管理
*/
export class AgentFactory {
  private static instance: AgentFactory;
  private agentInstances: Map<string, AgentInstance> = new Map();
  private agentPool: Map<AgentType, AgentBase[]> = new Map();
  private maxPoolSize: number = 5;
  private constructor() {
    this.initializeAgentPools();
  }
  /**
  * 获取工厂单例
  */
  public static getInstance(): AgentFactory {
    if (!AgentFactory.instance) {
      AgentFactory.instance = new AgentFactory();
    }
    return AgentFactory.instance;
  }
  /**
  * 创建智能体实例
  */
  public async createAgent(config: AgentConfig): Promise<AgentInstance> {
    try {
      const agentId = this.generateAgentId(config.agentType);
      // 尝试从池中获取
      const pooledAgent = this.getFromPool(config.agentType);
      let agent: AgentBase;
      if (pooledAgent) {
        agent = pooledAgent;
        this.log('info', `从池中获取智能体: ${config.agentType}`);
      } else {
        agent = await this.instantiateAgent(config.agentType);
        this.log('info', `创建新智能体实例: ${config.agentType}`);
      }
      // 配置智能体
      await this.configureAgent(agent, config);
      // 初始化智能体
      await agent.initialize();
      const instance: AgentInstance = {,
  id: agentId,
        type: config.agentType,
        agent,
        config,
        createdAt: new Date(),
        lastUsed: new Date(),
        isActive: true;
      };
      this.agentInstances.set(agentId, instance);
      this.log('info', `智能体实例创建成功: ${agentId}`);
      return instance;
    } catch (error) {
      this.log("error",智能体创建失败', error);
      throw error;
    }
  }
  /**
  * 获取智能体实例
  */
  public getAgent(agentId: string): AgentInstance | undefined {
    const instance = this.agentInstances.get(agentId);
    if (instance) {
      instance.lastUsed = new Date();
    }
    return instance;
  }
  /**
  * 根据类型创建或获取智能体
  */
  public async getOrCreateAgent()
    agentType: AgentType,
    config?: Partial<AgentConfig>
  ): Promise<AgentInstance> {
    // 查找现有的活跃实例
    const existingInstance = this.findActiveInstance(agentType);
    if (existingInstance) {
      existingInstance.lastUsed = new Date();
      return existingInstance;
    }
    // 创建新实例
    const fullConfig: AgentConfig = {
      agentType,
      enableLogging: true,
      maxConcurrentTasks: 5,
      timeout: 30000,
      ...config;
    };
    return this.createAgent(fullConfig);
  }
  /**
  * 批量创建智能体
  */
  public async createAgentBatch(configs: AgentConfig[]): Promise<AgentInstance[]> {
    const promises = configs.map(config => this.createAgent(config));
    return Promise.all(promises);
  }
  /**
  * 释放智能体实例
  */
  public async releaseAgent(agentId: string, returnToPool: boolean = true): Promise<void> {
    const instance = this.agentInstances.get(agentId);
    if (!instance) {
      this.log('warn', `智能体实例不存在: ${agentId}`);
      return;
    }
    try {
      // 标记为非活跃
      instance.isActive = false;
      // 如果需要返回池中且池未满
      if (returnToPool && this.canReturnToPool(instance.type)) {
        await this.returnToPool(instance.agent, instance.type);
        this.log('info', `智能体返回池中: ${agentId}`);
      } else {
        // 关闭智能体
        await instance.agent.shutdown();
        this.log('info', `智能体已关闭: ${agentId}`);
      }
      // 从实例映射中移除
      this.agentInstances.delete(agentId);
    } catch (error) {
      this.log('error', `释放智能体失败: ${agentId}`, error);
      throw error;
    }
  }
  /**
  * 获取所有活跃实例
  */
  public getActiveInstances(): AgentInstance[] {
    return Array.from(this.agentInstances.values()).filter(instance => instance.isActive);
  }
  /**
  * 获取实例统计信息
  */
  public getStatistics(): any {
    const instances = Array.from(this.agentInstances.values());
    const activeCount = instances.filter(i => i.isActive).length;
    const typeStats = new Map<AgentType, number>();
    instances.forEach(instance => {
      const count = typeStats.get(instance.type) || 0;
      typeStats.set(instance.type, count + 1);
    });
    return {totalInstances: instances.length,activeInstances: activeCount,inactiveInstances: instances.length - activeCount,typeDistribution: Object.fromEntries(typeStats),poolSizes: Object.fromEntries(;)
        Array.from(this.agentPool.entries()).map([type, agents]) => [type, agents.length]);
      );
    };
  }
  /**
  * 清理非活跃实例
  */
  public async cleanupInactiveInstances(maxIdleTime: number = 300000): Promise<void> {
    const now = new Date();
    const instancesToCleanup: string[] = [];
    for (const [id, instance] of this.agentInstances) {
      const idleTime = now.getTime() - instance.lastUsed.getTime();
      if (!instance.isActive || idleTime > maxIdleTime) {
        instancesToCleanup.push(id);
      }
    }
    this.log('info', `清理 ${instancesToCleanup.length} 个非活跃实例`);
    for (const id of instancesToCleanup) {
      await this.releaseAgent(id, false);
    }
  }
  /**
  * 关闭工厂
  */
  public async shutdown(): Promise<void> {
    this.log("info",智能体工厂正在关闭...');
    // 关闭所有实例
    const shutdownPromises = Array.from(this.agentInstances.keys()).map(id =>;)
      this.releaseAgent(id, false);
    );
    await Promise.all(shutdownPromises);
    // 清空池
    for (const [type, agents] of this.agentPool) {
      const poolShutdownPromises = agents.map(agent => agent.shutdown());
      await Promise.all(poolShutdownPromises);
    }
    this.agentPool.clear();
    this.log("info",智能体工厂已关闭');
  }
  /**
  * 初始化智能体池
  */
  private initializeAgentPools(): void {
    const agentTypes = [AgentType.XIAOAI, AgentType.XIAOKE, AgentType.LAOKE, AgentType.SOER];
    agentTypes.forEach(type => {
      this.agentPool.set(type, []);
    });
  }
  /**
  * 实例化智能体
  */
  private async instantiateAgent(agentType: AgentType): Promise<AgentBase> {
    switch (agentType) {
      case AgentType.XIAOAI:
        return new XiaoaiAgentImpl();
      case AgentType.XIAOKE:
        return new XiaokeAgentImpl();
      case AgentType.LAOKE:
        return new LaokeAgentImpl();
      case AgentType.SOER:
        return new SoerAgentImpl(),
  default:
        throw new Error(`不支持的智能体类型: ${agentType}`);
    }
  }
  /**
  * 配置智能体
  */
  private async configureAgent(agent: AgentBase, config: AgentConfig): Promise<void> {
    // 这里可以根据配置设置智能体的各种参数
    // 由于当前AgentBase没有配置方法，这里只是占位
    if (config.customSettings) {
      // 应用自定义设置
    }
  }
  /**
  * 从池中获取智能体
  */
  private getFromPool(agentType: AgentType): AgentBase | null {
    const pool = this.agentPool.get(agentType);
    return pool && pool.length > 0 ? pool.pop()! : null;
  }
  /**
  * 返回智能体到池中
  */
  private async returnToPool(agent: AgentBase, agentType: AgentType): Promise<void> {
    const pool = this.agentPool.get(agentType);
    if (pool && pool.length < this.maxPoolSize) {
      // 重置智能体状态
      如果有重置方法的话
      pool.push(agent);
    } else {
      await agent.shutdown();
    }
  }
  /**
  * 检查是否可以返回池中
  */
  private canReturnToPool(agentType: AgentType): boolean {
    const pool = this.agentPool.get(agentType);
    return pool ? pool.length < this.maxPoolSize : false;
  }
  /**
  * 查找活跃实例
  */
  private findActiveInstance(agentType: AgentType): AgentInstance | undefined {
    for (const instance of this.agentInstances.values()) {
      if (instance.type === agentType && instance.isActive) {
        return instance;
      }
    }
    return undefined;
  }
  /**
  * 生成智能体ID;
  */
  private generateAgentId(agentType: AgentType): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 9);
    return `${agentType}_${timestamp}_${random}`;
  }
  /**
  * 记录日志
  */
  private log(level: 'info' | 'warn' | 'error', message: string, data?: any): void {
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
// 导出工厂单例
export const agentFactory = AgentFactory.getInstance();
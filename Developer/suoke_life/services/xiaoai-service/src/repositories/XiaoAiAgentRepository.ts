/**
 * 小艾智能体存储库
 * 处理智能体状态、配置和日志数据
 */
import { BaseRepository } from './BaseRepository';
import XiaoAiAgent, { IXiaoAiAgent } from '../models/XiaoAiAgent';

export interface IXiaoAiAgentRepository extends BaseRepository<IXiaoAiAgent> {
  findByAgentId(agentId: string): Promise<IXiaoAiAgent | null>;
  findByName(name: string): Promise<IXiaoAiAgent | null>;
  updateStatus(agentId: string, status: string): Promise<IXiaoAiAgent | null>;
  updateConfig(agentId: string, config: any): Promise<IXiaoAiAgent | null>;
  updateCapabilities(agentId: string, capabilities: string[]): Promise<IXiaoAiAgent | null>;
  logActivity(agentId: string, activity: any): Promise<IXiaoAiAgent | null>;
  getActiveAgents(): Promise<IXiaoAiAgent[]>;
  getAgentsByCapability(capability: string): Promise<IXiaoAiAgent[]>;
}

export class XiaoAiAgentRepository extends BaseRepository<IXiaoAiAgent> implements IXiaoAiAgentRepository {
  constructor() {
    super(XiaoAiAgent);
  }

  async findByAgentId(agentId: string): Promise<IXiaoAiAgent | null> {
    return this.findOne({ agentId });
  }

  async findByName(name: string): Promise<IXiaoAiAgent | null> {
    return this.findOne({ name });
  }

  async updateStatus(agentId: string, status: string): Promise<IXiaoAiAgent | null> {
    return this.updateOne(
      { agentId },
      { 
        $set: { 
          status,
          lastStatusUpdate: new Date()
        } 
      }
    );
  }

  async updateConfig(agentId: string, config: any): Promise<IXiaoAiAgent | null> {
    return this.updateOne(
      { agentId },
      { 
        $set: { 
          config,
          lastConfigUpdate: new Date()
        } 
      }
    );
  }

  async updateCapabilities(agentId: string, capabilities: string[]): Promise<IXiaoAiAgent | null> {
    return this.updateOne(
      { agentId },
      { 
        $set: { 
          capabilities,
          lastCapabilitiesUpdate: new Date()
        } 
      }
    );
  }

  async logActivity(agentId: string, activity: any): Promise<IXiaoAiAgent | null> {
    return this.model.findOneAndUpdate(
      { agentId },
      { 
        $push: { 
          activityLog: {
            ...activity,
            timestamp: new Date()
          }
        },
        $set: { lastActivity: new Date() }
      },
      { new: true }
    ).exec();
  }

  async getActiveAgents(): Promise<IXiaoAiAgent[]> {
    return this.find({ status: 'active' });
  }

  async getAgentsByCapability(capability: string): Promise<IXiaoAiAgent[]> {
    return this.find({ capabilities: capability });
  }
} 
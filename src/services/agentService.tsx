import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Alert } from 'react-native';
import { apiClient } from './apiClient';
import { FourDiagnosisAggregationResult } from '../types/agents';
// 智能体信息接口
export interface AgentInfo {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'busy';
  capabilities: string[];
  description?: string;
  avatar?: string;
}
// 消息接口
export interface Message {
  id: string;
  content: string;
  timestamp: number;
  sender: string;
  type?: 'text' | 'image' | 'audio' | 'file';
  metadata?: unknown;
}
// 咨询会话接口
export interface ConsultationSession {
  sessionId: string;
  agentId: string;
  status: 'active' | 'completed' | 'cancelled';
  startTime: number;
  endTime?: number;
}
// 智能体建议接口
export interface AgentSuggestion {
  id: string;
  title: string;
  content: string;
  category: string;
  priority: 'high' | 'medium' | 'low';
}
// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    message: string;
    code?: string;
  };
  code?: string | number;
}
// 智能体状态类型
export interface AgentStatus {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'busy' | 'away';
  lastActive: number;
  capabilities: string[];
  currentTask?: string;
  healthScore?: number;
  responseTime?: number;
}
// 智能体交互类型
export interface AgentInteraction {
  agentId: string;
  userId: string;
  sessionId: string;
  messages: AgentMessage[];
  context: Record<string, any>;
  startTime: number;
  lastUpdate: number;
}
export interface AgentMessage {
  id: string;
  content: string;
  timestamp: number;
  sender: 'user' | 'agent';
  type: 'text' | 'image' | 'audio' | 'data';
  metadata?: Record<string, any>;
}
// 智能体服务类
export class AgentService {
  private agents: Map<string, AgentStatus> = new Map();
  private interactions: Map<string, AgentInteraction> = new Map();
  private listeners: Set<(agentId: string, status: AgentStatus) => void> = new Set();
  constructor() {
    this.initializeAgents();
    this.startHealthCheck();
  }
  // 初始化智能体
  private initializeAgents() {
    const defaultAgents: AgentStatus[] = [
      {
      id: "xiaoai",
      name: '小艾',
        status: 'online',
        lastActive: Date.now(),
        capabilities: ["健康咨询", "数据分析', "个性化建议", "多模态交互'],
        healthScore: 95,
        responseTime: 200;
      },
      {
      id: "xiaoke",
      name: '小克',
        status: 'online',
        lastActive: Date.now(),
        capabilities: ["中医辨证", "四诊合参', "体质分析", "方剂推荐'],
        healthScore: 92,
        responseTime: 300;
      },
      {
      id: "laoke",
      name: '老克',
        status: 'online',
        lastActive: Date.now(),
        capabilities: ["健康管理", "康复指导', "慢病管理", "生活方式干预'],
        healthScore: 88,
        responseTime: 250;
      },
      {
      id: "soer",
      name: '索儿',
        status: 'online',
        lastActive: Date.now(),
        capabilities: ["生活教练", "运动指导', "营养建议",心理健康'],
        healthScore: 90,
        responseTime: 180;
      }
    ];
    defaultAgents.forEach(agent => {
      this.agents.set(agent.id, agent);
    });
  }
  // 启动健康检查
  private startHealthCheck() {
    setInterval() => {
      this.performHealthCheck();
    }, 30000); // 每30秒检查一次
  }
  // 执行健康检查
  private performHealthCheck() {
    this.agents.forEach(((agent, agentId) => {
      // 模拟健康检查
      const healthScore = Math.max(70, Math.min(100, agent.healthScore! + (Math.random() - 0.5) * 10));
      const responseTime = Math.max(100, Math.min(1000, agent.responseTime! + (Math.random() - 0.5) * 100));
            // 根据健康分数调整状态
      let status: AgentStatus['status'] = 'online';
      if (healthScore < 80) {
        status = 'busy';
      } else if (healthScore < 75) {
        status = 'away';
      }
      const updatedAgent: AgentStatus = {
        ...agent,
        status,
        healthScore,
        responseTime,
        lastActive: Date.now()
      };
      this.agents.set(agentId, updatedAgent);
      this.notifyListeners(agentId, updatedAgent);
    });
  }
  // 通知监听器
  private notifyListeners(agentId: string, status: AgentStatus) {
    this.listeners.forEach(listener => {
      try {
        listener(agentId, status);
      } catch (error) {
        console.error('智能体状态监听器错误:', error);
      }
    });
  }
  // 获取智能体状态
  async getAgentStatus(agentId: string): Promise<AgentStatus | null> {
    try {
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 100));
            const agent = this.agents.get(agentId);
      if (!agent) {
        throw new Error(`智能体 ${agentId} 不存在`);
      }
      return { ...agent };
    } catch (error) {
      console.error(`获取智能体 ${agentId} 状态失败:`, error);
      return null;
    }
  }
  // 获取所有智能体状态
  async getAllAgentStatuses(): Promise<Record<string, AgentStatus>> {
    try {
      const statuses: Record<string, AgentStatus> = {};
            for (const [agentId, agent] of this.agents) {
        statuses[agentId] = { ...agent };
      }
      return statuses;
    } catch (error) {
      console.error('获取所有智能体状态失败:', error);
      return {};
    }
  }
  // 启动智能体交互
  async startInteraction(agentId: string, userId: string): Promise<string> {
    try {
      const agent = this.agents.get(agentId);
      if (!agent) {
        throw new Error(`智能体 ${agentId} 不存在`);
      }
      if (agent.status === 'offline') {
        throw new Error(`智能体 ${agentId} 当前离线`);
      }
      const sessionId = `${agentId}_${userId}_${Date.now()}`;
      const interaction: AgentInteraction = {
        agentId,
        userId,
        sessionId,
        messages: [],
        context: {},
        startTime: Date.now(),
        lastUpdate: Date.now()
      };
      this.interactions.set(sessionId, interaction);
      // 更新智能体状态
      const updatedAgent = {
        ...agent,
        currentTask: `与用户 ${userId} 交互`,
        lastActive: Date.now()
      };
      this.agents.set(agentId, updatedAgent);
      this.notifyListeners(agentId, updatedAgent);
      return sessionId;
    } catch (error) {
      console.error('启动智能体交互失败:', error);
      throw error;
    }
  }
  // 发送消息给智能体
  async sendMessage(sessionId: string, content: string, type: 'text' | 'image' | 'audio' = 'text'): Promise<AgentMessage> {
    try {
      const interaction = this.interactions.get(sessionId);
      if (!interaction) {
        throw new Error('交互会话不存在');
      }
      const agent = this.agents.get(interaction.agentId);
      if (!agent) {
        throw new Error('智能体不存在');
      }
      // 创建用户消息
      const userMessage: AgentMessage = {,
  id: `msg_${Date.now()}`,
        content,
        timestamp: Date.now(),
        sender: 'user',
        type;
      };
      // 添加到交互历史
      interaction.messages.push(userMessage);
      interaction.lastUpdate = Date.now();
      // 生成智能体回复
      const agentReply = await this.generateAgentReply(interaction.agentId, content, interaction.context);
            const agentMessage: AgentMessage = {,
  id: `msg_${Date.now() + 1}`,
        content: agentReply,
        timestamp: Date.now(),
        sender: 'agent',
        type: 'text',
        metadata: {,
  agentId: interaction.agentId,
          responseTime: agent.responseTime;
        }
      };
      interaction.messages.push(agentMessage);
      interaction.lastUpdate = Date.now();
      // 更新交互记录
      this.interactions.set(sessionId, interaction);
      // 更新智能体最后活跃时间
      const updatedAgent = {
        ...agent,
        lastActive: Date.now()
      };
      this.agents.set(interaction.agentId, updatedAgent);
      return agentMessage;
    } catch (error) {
      console.error('发送消息失败:', error);
      throw error;
    }
  }
  // 生成智能体回复
  private async generateAgentReply(agentId: string, userMessage: string, context: Record<string, any>): Promise<string> {
    // 模拟AI处理延迟
    await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 1000));
    const agent = this.agents.get(agentId);
    if (!agent) {
      return '抱歉，我现在无法回复您的消息。';
    }
    // 根据智能体类型生成不同的回复
    switch (agentId) {
      case 'xiaoai':
        return this.generateXiaoaiReply(userMessage, context);
      case 'xiaoke':
        return this.generateXiaokeReply(userMessage, context);
      case 'laoke':
        return this.generateLaokeReply(userMessage, context);
      case 'soer':
        return this.generateSoerReply(userMessage, context);
      default:
        return '您好，我是您的健康助手，有什么可以帮助您的吗？';
    }
  }
  // 小艾的回复生成
  private generateXiaoaiReply(message: string, context: Record<string, any>): string {
    const lowerMessage = message.toLowerCase();
        if (lowerMessage.includes('健康') || lowerMessage.includes('体检')) {
      return '我正在分析您的健康数据。根据您的情况，建议您：\n\n1. 保持规律作息\n2. 均衡饮食\n3. 适量运动\n4. 定期体检\n\n需要我为您制定个性化的健康管理方案吗？';
    } else if (lowerMessage.includes('症状') || lowerMessage.includes('不舒服')) {
      return '我理解您的担心。请详细描述您的症状，包括：\n\n• 症状出现的时间\n• 症状的具体表现\n• 是否有诱发因素\n• 之前是否有类似情况\n\n这样我能更好地为您分析和建议。';
    } else if (lowerMessage.includes('数据') || lowerMessage.includes('报告')) {
      return '我可以帮您分析各种健康数据，包括：\n\n📊 体检报告解读\n📈 生理指标趋势\n🔍 异常数据分析\n💡 个性化建议\n\n请上传您的数据或报告，我来为您详细分析。';
    } else {
      return '您好！我是小艾，您的智能健康助手。我可以帮您：\n\n🔍 分析健康数据\n📋 解读体检报告\n💊 提供健康建议\n📱 监测健康指标\n\n有什么健康问题需要咨询吗？';
    }
  }
  // 小克的回复生成
  private generateXiaokeReply(message: string, context: Record<string, any>): string {
    const lowerMessage = message.toLowerCase();
        if (lowerMessage.includes('中医') || lowerMessage.includes('辨证')) {
      return '从中医角度来看，我需要通过四诊合参来了解您的体质：\n\n👁️ 望诊：面色、舌象\n👂 闻诊：声音、气味\n❓ 问诊：症状、病史\n✋ 切诊：脉象、按压\n\n请告诉我您的具体症状，我来为您进行中医辨证分析。';
    } else if (lowerMessage.includes('体质') || lowerMessage.includes('调理')) {
      return '中医体质分为九种类型：\n\n🌿 平和质、气虚质、阳虚质\n🔥 阴虚质、痰湿质、湿热质\n💨 气郁质、血瘀质、特禀质\n\n每种体质都有相应的调理方法。请描述您的身体状况，我来判断您的体质类型并提供调理建议。';
    } else if (lowerMessage.includes('方剂') || lowerMessage.includes('药方')) {
      return '中医方剂需要根据具体证候来配伍：\n\n📜 经典方剂：如四君子汤、六味地黄丸\n🌱 现代应用：结合现代病症特点\n⚖️ 个体化：根据体质和症状调整\n\n请详细描述您的症状，我来为您推荐合适的方剂。注意：具体用药请咨询专业中医师。';
    } else {
      return '您好！我是小克，专注中医辨证论治。我可以帮您：\n\n🔍 中医体质辨识\n📋 四诊合参分析\n🌿 方剂配伍建议\n⚖️ 个性化调理方案\n\n请告诉我您的具体情况，我来为您进行中医分析。';
    }
  }
  // 老克的回复生成
  private generateLaokeReply(message: string, context: Record<string, any>): string {
    const lowerMessage = message.toLowerCase();
        if (lowerMessage.includes('管理') || lowerMessage.includes('计划')) {
      return '健康管理是一个系统工程，我来为您制定个性化方案：\n\n📅 日常管理：作息、饮食、运动\n📊 监测指标：血压、血糖、体重等\n🎯 目标设定：短期和长期健康目标\n📈 效果评估：定期评估和调整\n\n请告诉我您的健康状况和目标，我来制定专属方案。';
    } else if (lowerMessage.includes('康复') || lowerMessage.includes('恢复')) {
      return '康复是一个循序渐进的过程：\n\n🏥 医学康复：遵医嘱，规范治疗\n🏃 运动康复：适量运动，逐步增强\n🧠 心理康复：保持积极心态\n🏠 生活康复：改善生活方式\n\n请描述您的具体情况，我来制定康复指导方案。';
    } else if (lowerMessage.includes('慢病') || lowerMessage.includes('长期')) {
      return '慢性病管理需要长期坚持：\n\n💊 药物管理：按时服药，监测效果\n📊 指标监测：定期检查关键指标\n🍎 生活方式：饮食、运动、作息\n👨‍⚕️ 医患配合：定期复诊，及时调整\n\n我可以帮您建立慢病管理档案，制定个性化管理策略。';
    } else {
      return '您好！我是老克，专注健康管理和康复指导。我可以帮您：\n\n📋 制定健康管理方案\n🎯 设定康复目标\n📊 监测健康指标\n💡 提供专业建议\n\n请告诉我您的健康状况，我来为您提供专业指导。';
    }
  }
  // 索儿的回复生成
  private generateSoerReply(message: string, context: Record<string, any>): string {
    const lowerMessage = message.toLowerCase();
        if (lowerMessage.includes('运动') || lowerMessage.includes('锻炼')) {
      return '运动是健康生活的重要组成部分：\n\n🏃 有氧运动：跑步、游泳、骑行\n💪 力量训练：增强肌肉力量\n🧘 柔韧性：瑜伽、拉伸\n⚖️ 平衡性：太极、平衡训练\n\n请告诉我您的运动基础和目标，我来制定适合的运动计划。';
    } else if (lowerMessage.includes('饮食') || lowerMessage.includes('营养')) {
      return '营养均衡是健康的基础：\n\n🥗 膳食搭配：蛋白质、碳水、脂肪\n🍎 维生素：新鲜蔬果\n💧 水分补充：每天8杯水\n⏰ 进餐时间：规律三餐\n\n请分享您的饮食习惯，我来提供营养建议。';
    } else if (lowerMessage.includes('心理') || lowerMessage.includes('情绪')) {
      return '心理健康同样重要：\n\n😊 情绪管理：识别和调节情绪\n🧘 压力缓解：冥想、深呼吸\n👥 社交支持：与家人朋友交流\n🎯 目标设定：制定可实现的目标\n\n保持积极心态，有什么困扰可以和我分享。';
    } else {
      return '您好！我是索儿，您的生活健康教练。我可以帮您：\n\n🏃 制定运动计划\n🥗 提供营养建议\n😊 关注心理健康\n🎯 设定生活目标\n\n让我们一起打造健康的生活方式！有什么想了解的吗？';
    }
  }
  // 结束交互
  async endInteraction(sessionId: string): Promise<void> {
    try {
      const interaction = this.interactions.get(sessionId);
      if (!interaction) {
        return;
      }
      // 更新智能体状态
      const agent = this.agents.get(interaction.agentId);
      if (agent) {
        const updatedAgent = {
          ...agent,
          currentTask: undefined,
          lastActive: Date.now()
        };
        this.agents.set(interaction.agentId, updatedAgent);
        this.notifyListeners(interaction.agentId, updatedAgent);
      }
      // 删除交互记录
      this.interactions.delete(sessionId);
    } catch (error) {
      console.error('结束交互失败:', error);
    }
  }
  // 添加状态监听器
  addStatusListener(listener: (agentId: string, status: AgentStatus) => void): () => void {
    this.listeners.add(listener);
        // 返回取消监听的函数
    return () => {
      this.listeners.delete(listener);
    };
  }
  // 获取交互历史
  getInteractionHistory(sessionId: string): AgentMessage[] {
    const interaction = this.interactions.get(sessionId);
    return interaction ? [...interaction.messages] : [];
  }
  // 更新智能体配置
  async updateAgentConfig(agentId: string, config: Partial<AgentStatus>): Promise<void> {
    try {
      const agent = this.agents.get(agentId);
      if (!agent) {
        throw new Error(`智能体 ${agentId} 不存在`);
      }
      const updatedAgent = { ...agent, ...config };
      this.agents.set(agentId, updatedAgent);
      this.notifyListeners(agentId, updatedAgent);
    } catch (error) {
      console.error('更新智能体配置失败:', error);
      throw error;
    }
  }
}
// 创建全局智能体服务实例
export const agentService = new AgentService();
// React Context;
interface AgentContextType {
  agentService: AgentService;
  agentStatuses: Record<string, AgentStatus>;
  refreshStatuses: () => Promise<void>;
}
const AgentContext = createContext<AgentContextType | null>(null);
// Provider组件
interface AgentProviderProps {
  children: ReactNode;
}
export const AgentProvider: React.FC<AgentProviderProps> = ({ children }) => {
  const [agentStatuses, setAgentStatuses] = useState<Record<string, AgentStatus>>({});
  const refreshStatuses = async () => {
    try {
      const statuses = await agentService.getAllAgentStatuses();
      setAgentStatuses(statuses);
    } catch (error) {
      console.error('刷新智能体状态失败:', error);
    }
  };
  useEffect(() => {
    // 初始加载
    refreshStatuses();
    // 添加状态监听器
    const unsubscribe = agentService.addStatusListener(agentId, status) => {
      setAgentStatuses(prev => ({
        ...prev,
        [agentId]: status;
      }));
    });
    return unsubscribe;
  }, []);
  const value: AgentContextType = {
    agentService,
    agentStatuses,
    refreshStatuses;
  };
  return (
  <AgentContext.Provider value={value}>
      {children}
    </AgentContext.Provider>
  );
};
// Hook;
export const useAgent = () => {
  const context = useContext(AgentContext);
  if (!context) {
    throw new Error('useAgent must be used within an AgentProvider');
  }
  return context;
};
export default agentService;
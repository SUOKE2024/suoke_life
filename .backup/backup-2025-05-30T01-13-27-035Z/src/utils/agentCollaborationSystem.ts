import { securityManager } from "./securityManager";



// 智能体类型定义
export type AgentType = "xiaoai" | "xiaoke" | "laoke" | "soer";

// 智能体角色定义
export interface AgentRole {
  id: AgentType;
  name: string;
  description: string;
  capabilities: string[];
  specialties: string[];
  personality: {
    communication_style: string;
    empathy_level: number;
    expertise_confidence: number;
  };
}

// 协作任务类型
export interface CollaborationTask {
  id: string;
  type:
    | "health_diagnosis"
    | "treatment_plan"
    | "lifestyle_advice"
    | "emergency_response";
  priority: "low" | "medium" | "high" | "critical";
  requiredAgents: AgentType[];
  currentAgent?: AgentType;
  status: "pending" | "in_progress" | "completed" | "failed";
  data: any;
  timeline: TaskTimeline[];
  result?: CollaborationResult;
}

export interface TaskTimeline {
  timestamp: number;
  agent: AgentType;
  action: string;
  data: any;
}

export interface CollaborationResult {
  consensus: boolean;
  recommendations: AgentRecommendation[];
  confidence: number;
  reasoning: string;
}

export interface AgentRecommendation {
  agent: AgentType;
  recommendation: string;
  confidence: number;
  reasoning: string;
  supporting_data: any;
}

// 智能体状态
export interface AgentStatus {
  agent: AgentType;
  online: boolean;
  busy: boolean;
  currentTasks: string[];
  performance: {
    response_time: number;
    accuracy: number;
    user_satisfaction: number;
  };
  lastUpdate: number;
}

// 协作决策引擎
class CollaborationDecisionEngine {
  private static instance: CollaborationDecisionEngine;

  static getInstance(): CollaborationDecisionEngine {
    if (!CollaborationDecisionEngine.instance) {
      CollaborationDecisionEngine.instance = new CollaborationDecisionEngine();
    }
    return CollaborationDecisionEngine.instance;
  }

  // 分析任务并分配智能体
  analyzeTaskAndAssignAgents(taskData: any): AgentType[] {
    const requiredAgents: AgentType[] = [];

    // 基于任务类型和内容分析需要的智能体
    if (taskData.type === "health_diagnosis") {
      requiredAgents.push("xiaoai"); // 小艾负责初步诊断

      if (taskData.symptoms?.includes("chronic") || taskData.age > 60) {
        requiredAgents.push("laoke"); // 老克负责慢性病和老年健康
      }

      if (taskData.needsMedicalIntervention) {
        requiredAgents.push("xiaoke"); // 小克负责医疗服务
      }

      if (taskData.lifestyle_factors) {
        requiredAgents.push("soer"); // 索儿负责生活方式建议
      }
    }

    return requiredAgents;
  }

  // 协调智能体决策
  async coordinateDecision(
    task: CollaborationTask,
    agentRecommendations: AgentRecommendation[]
  ): Promise<CollaborationResult> {
    // 计算共识度
    const consensus = this.calculateConsensus(agentRecommendations);

    // 综合置信度
    const overallConfidence =
      this.calculateOverallConfidence(agentRecommendations);

    // 生成最终推荐
    const finalRecommendations =
      this.synthesizeRecommendations(agentRecommendations);

    // 生成推理说明
    const reasoning = this.generateReasoning(agentRecommendations, consensus);

    return {
      consensus: consensus > 0.7,
      recommendations: finalRecommendations,
      confidence: overallConfidence,
      reasoning,
    };
  }

  private calculateConsensus(recommendations: AgentRecommendation[]): number {
    if (recommendations.length < 2) {
      return 1.0;
    }

    // 简化的共识计算：基于推荐相似度
    let totalSimilarity = 0;
    let comparisons = 0;

    for (let i = 0; i < recommendations.length; i++) {
      for (let j = i + 1; j < recommendations.length; j++) {
        const similarity = this.calculateRecommendationSimilarity(
          recommendations[i],
          recommendations[j]
        );
        totalSimilarity += similarity;
        comparisons++;
      }
    }

    return comparisons > 0 ? totalSimilarity / comparisons : 1.0;
  }

  private calculateRecommendationSimilarity(
    rec1: AgentRecommendation,
    rec2: AgentRecommendation
  ): number {
    // 简化的相似度计算
    const keywords1 = rec1.recommendation.toLowerCase().split(" ");
    const keywords2 = rec2.recommendation.toLowerCase().split(" ");

    const commonKeywords = keywords1.filter((word) => keywords2.includes(word));
    const totalKeywords = new Set([...keywords1, ...keywords2]).size;

    return commonKeywords.length / totalKeywords;
  }

  private calculateOverallConfidence(
    recommendations: AgentRecommendation[]
  ): number {
    if (recommendations.length === 0) {
      return 0;
    }

    const totalConfidence = recommendations.reduce(
      (sum, rec) => sum + rec.confidence,
      0
    );
    return totalConfidence / recommendations.length;
  }

  private synthesizeRecommendations(
    recommendations: AgentRecommendation[]
  ): AgentRecommendation[] {
    // 按置信度排序并返回最佳推荐
    return recommendations
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, 3); // 返回前3个最佳推荐
  }

  private generateReasoning(
    recommendations: AgentRecommendation[],
    consensus: number
  ): string {
    const agentNames = recommendations
      .map((r) => this.getAgentName(r.agent))
      .join("、");

    if (consensus > 0.8) {
      return `${agentNames}达成高度共识，推荐方案具有很高的可信度。`;
    } else if (consensus > 0.6) {
      return `${agentNames}基本达成共识，推荐方案经过充分讨论。`;
    } else {
      return `${agentNames}存在不同观点，建议综合考虑各方意见。`;
    }
  }

  private getAgentName(agent: AgentType): string {
    const names = {
      xiaoai: "小艾",
      xiaoke: "小克",
      laoke: "老克",
      soer: "索儿",
    };
    return names[agent];
  }
}

// 智能体协作管理器
export class AgentCollaborationSystem {
  private static instance: AgentCollaborationSystem;
  private agents: Map<AgentType, AgentRole> = new Map();
  private agentStatuses: Map<AgentType, AgentStatus> = new Map();
  private activeTasks: Map<string, CollaborationTask> = new Map();
  private decisionEngine: CollaborationDecisionEngine;
  private collaborationHistory: CollaborationTask[] = [];

  private constructor() {
    this.decisionEngine = CollaborationDecisionEngine.getInstance();
    this.initializeAgents();
  }

  static getInstance(): AgentCollaborationSystem {
    if (!AgentCollaborationSystem.instance) {
      AgentCollaborationSystem.instance = new AgentCollaborationSystem();
    }
    return AgentCollaborationSystem.instance;
  }

  // 初始化智能体
  private initializeAgents(): void {
    // 小艾 - AI健康诊断助手
    this.agents.set("xiaoai", {
      id: "xiaoai",
      name: "小艾",
      description: "AI健康诊断助手，专注于症状分析和初步诊断",
      capabilities: [
        "症状分析",
        "健康数据解读",
        "风险评估",
        "预防建议",
        "多模态数据融合",
      ],
      specialties: ["中医四诊", "现代医学诊断", "健康监测", "疾病预测"],
      personality: {
        communication_style: "专业、温和、详细",
        empathy_level: 0.8,
        expertise_confidence: 0.9,
      },
    });

    // 小克 - 医疗服务管理助手
    this.agents.set("xiaoke", {
      id: "xiaoke",
      name: "小克",
      description: "医疗服务管理助手，负责医疗资源协调和服务管理",
      capabilities: [
        "医疗服务预约",
        "资源调度",
        "治疗方案制定",
        "康复指导",
        "紧急响应",
      ],
      specialties: ["医疗服务管理", "治疗计划", "康复医学", "急救处理"],
      personality: {
        communication_style: "高效、准确、负责",
        empathy_level: 0.7,
        expertise_confidence: 0.85,
      },
    });

    // 老克 - 慢性病和老年健康专家
    this.agents.set("laoke", {
      id: "laoke",
      name: "老克",
      description: "慢性病和老年健康专家，专注于长期健康管理",
      capabilities: [
        "慢性病管理",
        "老年健康评估",
        "长期护理规划",
        "并发症预防",
        "家庭护理指导",
      ],
      specialties: ["慢性病", "老年医学", "长期护理", "并发症管理"],
      personality: {
        communication_style: "耐心、细致、经验丰富",
        empathy_level: 0.9,
        expertise_confidence: 0.95,
      },
    });

    // 索儿 - 生活方式和养生顾问
    this.agents.set("soer", {
      id: "soer",
      name: "索儿",
      description: "生活方式和养生顾问，专注于健康生活指导",
      capabilities: [
        "营养指导",
        "运动规划",
        "心理健康",
        "生活习惯优化",
        "环境健康评估",
      ],
      specialties: ["营养学", "运动医学", "心理健康", "环境医学"],
      personality: {
        communication_style: "亲切、鼓励、实用",
        empathy_level: 0.85,
        expertise_confidence: 0.8,
      },
    });

    // 初始化智能体状态
    this.agents.forEach((agent, agentType) => {
      this.agentStatuses.set(agentType, {
        agent: agentType,
        online: true,
        busy: false,
        currentTasks: [],
        performance: {
          response_time: 1000 + Math.random() * 2000,
          accuracy: 0.85 + Math.random() * 0.1,
          user_satisfaction: 0.8 + Math.random() * 0.15,
        },
        lastUpdate: Date.now(),
      });
    });
  }

  // 创建协作任务
  async createCollaborationTask(
    type: CollaborationTask["type"],
    data: any,
    priority: CollaborationTask["priority"] = "medium"
  ): Promise<string> {
    const taskId = this.generateTaskId();

    // 分析任务并确定需要的智能体
    const requiredAgents = this.decisionEngine.analyzeTaskAndAssignAgents({
      type,
      ...data,
    });

    const task: CollaborationTask = {
      id: taskId,
      type,
      priority,
      requiredAgents,
      status: "pending",
      data,
      timeline: [
        {
          timestamp: Date.now(),
          agent: "xiaoai", // 默认由小艾发起
          action: "task_created",
          data: { type, priority },
        },
      ],
    };

    this.activeTasks.set(taskId, task);

    // 记录安全事件
    securityManager.logSecurityEvent({
      type: "data_access",
      details: { action: "collaboration_task_created", taskId, type },
      severity: "low",
    });

    // 开始执行任务
    await this.executeTask(taskId);

    return taskId;
  }

  // 执行协作任务
  private async executeTask(taskId: string): Promise<void> {
    const task = this.activeTasks.get(taskId);
    if (!task) {
      return;
    }

    try {
      task.status = "in_progress";

      // 收集各智能体的推荐
      const recommendations: AgentRecommendation[] = [];

      for (const agentType of task.requiredAgents) {
        const recommendation = await this.getAgentRecommendation(
          agentType,
          task
        );
        if (recommendation) {
          recommendations.push(recommendation);
        }
      }

      // 协调决策
      const result = await this.decisionEngine.coordinateDecision(
        task,
        recommendations
      );

      task.result = result;
      task.status = "completed";
      task.timeline.push({
        timestamp: Date.now(),
        agent: "xiaoai",
        action: "task_completed",
        data: { consensus: result.consensus, confidence: result.confidence },
      });

      // 保存到历史记录
      this.collaborationHistory.push({ ...task });

      // 移除活跃任务
      this.activeTasks.delete(taskId);
    } catch (error) {
      console.error("任务执行失败:", error);
      task.status = "failed";
      task.timeline.push({
        timestamp: Date.now(),
        agent: "xiaoai",
        action: "task_failed",
        data: {
          error: error instanceof Error ? error.message : "Unknown error",
        },
      });
    }
  }

  // 获取智能体推荐
  private async getAgentRecommendation(
    agentType: AgentType,
    task: CollaborationTask
  ): Promise<AgentRecommendation | null> {
    const agent = this.agents.get(agentType);
    if (!agent) {
      return null;
    }

    // 模拟智能体分析和推荐生成
    await this.simulateProcessingTime(agentType);

    const recommendation = this.generateMockRecommendation(agent, task);

    task.timeline.push({
      timestamp: Date.now(),
      agent: agentType,
      action: "recommendation_generated",
      data: { confidence: recommendation.confidence },
    });

    return recommendation;
  }

  // 生成模拟推荐（在实际应用中会调用真实的AI服务）
  private generateMockRecommendation(
    agent: AgentRole,
    task: CollaborationTask
  ): AgentRecommendation {
    const baseConfidence = agent.personality.expertise_confidence;
    const confidence = baseConfidence * (0.8 + Math.random() * 0.2);

    let recommendation = "";
    let reasoning = "";

    switch (agent.id) {
      case "xiaoai":
        recommendation = "基于症状分析，建议进行进一步检查并关注生活方式调整";
        reasoning = "通过多模态数据分析，发现潜在健康风险指标";
        break;
      case "xiaoke":
        recommendation = "建议预约专科医生进行详细检查，制定个性化治疗方案";
        reasoning = "基于医疗服务管理经验，推荐最适合的医疗资源";
        break;
      case "laoke":
        recommendation = "重点关注慢性病预防，建立长期健康监测计划";
        reasoning = "结合年龄和健康历史，制定预防性健康管理策略";
        break;
      case "soer":
        recommendation = "调整饮食结构，增加适量运动，改善睡眠质量";
        reasoning = "从生活方式角度提供全面的健康改善建议";
        break;
    }

    return {
      agent: agent.id,
      recommendation,
      confidence,
      reasoning,
      supporting_data: {
        agent_specialties: agent.specialties,
        analysis_time: Date.now(),
      },
    };
  }

  // 模拟处理时间
  private async simulateProcessingTime(agentType: AgentType): Promise<void> {
    const status = this.agentStatuses.get(agentType);
    const processingTime = status?.performance.response_time || 2000;

    return new Promise((resolve) => {
      setTimeout(resolve, processingTime * (0.5 + Math.random()));
    });
  }

  // 获取任务状态
  getTaskStatus(taskId: string): CollaborationTask | null {
    return (
      this.activeTasks.get(taskId) ||
      this.collaborationHistory.find((task) => task.id === taskId) ||
      null
    );
  }

  // 获取智能体状态
  getAgentStatus(agentType: AgentType): AgentStatus | null {
    return this.agentStatuses.get(agentType) || null;
  }

  // 获取所有智能体状态
  getAllAgentStatuses(): AgentStatus[] {
    return Array.from(this.agentStatuses.values());
  }

  // 获取协作历史
  getCollaborationHistory(limit: number = 10): CollaborationTask[] {
    return this.collaborationHistory
      .sort(
        (a, b) =>
          (b.timeline[0]?.timestamp || 0) - (a.timeline[0]?.timestamp || 0)
      )
      .slice(0, limit);
  }

  // 获取协作统计
  getCollaborationStats(): {
    totalTasks: number;
    completedTasks: number;
    averageConfidence: number;
    consensusRate: number;
  } {
    const completedTasks = this.collaborationHistory.filter(
      (task) => task.status === "completed"
    );
    const totalTasks = this.collaborationHistory.length;

    const averageConfidence =
      completedTasks.length > 0
        ? completedTasks.reduce(
            (sum, task) => sum + (task.result?.confidence || 0),
            0
          ) / completedTasks.length
        : 0;

    const consensusRate =
      completedTasks.length > 0
        ? completedTasks.filter((task) => task.result?.consensus).length /
          completedTasks.length
        : 0;

    return {
      totalTasks,
      completedTasks: completedTasks.length,
      averageConfidence,
      consensusRate,
    };
  }

  // 生成任务ID
  private generateTaskId(): string {
    return `collab_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// 导出单例实例
export const agentCollaborationSystem = AgentCollaborationSystem.getInstance();

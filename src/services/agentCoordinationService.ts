// 智能体协调服务 - 管理多个智能体之间的协作

export interface AgentInfo {
  id: string;
  name: string;
  type: "xiaoai" | "xiaoke" | "laoke" | "soer";
  status: "active" | "inactive" | "busy" | "error";
  capabilities: string[];
  load: number;
  lastHeartbeat: Date;
}

export interface TaskRequest {
  id: string;
  type: string;
  priority: "low" | "medium" | "high" | "urgent";
  data: unknown;
  requiredCapabilities: string[];
  deadline?: Date;
  userId?: string;
}

export interface TaskAssignment {
  taskId: string;
  agentId: string;
  assignedAt: Date;
  estimatedCompletion: Date;
  status: "assigned" | "in_progress" | "completed" | "failed";
}

export interface CoordinationEvent {
  id: string;
  type: "task_assigned" | "task_completed" | "agent_status_changed" | "conflict_detected";
  timestamp: Date;
  data: unknown;
}

/**
 * 智能体协调服务
 * 负责管理多个智能体之间的协作和任务分配
 */
export class AgentCoordinationService {
  private agents: Map<string, AgentInfo> = new Map();
  private tasks: Map<string, TaskRequest> = new Map();
  private assignments: Map<string, TaskAssignment> = new Map();
  private eventHistory: CoordinationEvent[] = [];
  private eventListeners: Array<(event: CoordinationEvent) => void> = [];

  constructor() {
    this.initializeDefaultAgents();
    this.startHeartbeatMonitoring();
  }

  // 初始化默认智能体
  private initializeDefaultAgents(): void {
    const defaultAgents: AgentInfo[] = [
      {
        id: "xiaoai-001",
        name: "小艾",
        type: "xiaoai",
        status: "active",
        capabilities: ["health_consultation", "voice_interaction", "four_diagnosis"],
        load: 0.2,
        lastHeartbeat: new Date()
      },
      {
        id: "xiaoke-001",
        name: "小克",
        type: "xiaoke",
        status: "active",
        capabilities: ["data_analysis", "health_monitoring", "report_generation"],
        load: 0.1,
        lastHeartbeat: new Date()
      },
      {
        id: "laoke-001",
        name: "老克",
        type: "laoke",
        status: "active",
        capabilities: ["knowledge_management", "education", "tcm_knowledge"],
        load: 0.15,
        lastHeartbeat: new Date()
      },
      {
        id: "soer-001",
        name: "索儿",
        type: "soer",
        status: "active",
        capabilities: ["lifestyle_management", "eco_services", "community"],
        load: 0.05,
        lastHeartbeat: new Date()
      }
    ];

    for (const agent of defaultAgents) {
      this.agents.set(agent.id, agent);
    }
  }

  // 注册智能体
  async registerAgent(agent: AgentInfo): Promise<boolean> {
    try {
      this.agents.set(agent.id, agent);
      
      const event: CoordinationEvent = {
        id: `event-${Date.now()}`,
        type: "agent_status_changed",
        timestamp: new Date(),
        data: { agentId: agent.id, status: "registered" }
      };
      
      this.emitEvent(event);
      return true;
    } catch (error) {
      console.error("注册智能体失败:", error);
      return false;
    }
  }

  // 注销智能体
  async unregisterAgent(agentId: string): Promise<boolean> {
    try {
      const agent = this.agents.get(agentId);
      if (!agent) {
        return false;
      }

      this.agents.delete(agentId);
      
      const event: CoordinationEvent = {
        id: `event-${Date.now()}`,
        type: "agent_status_changed",
        timestamp: new Date(),
        data: { agentId, status: "unregistered" }
      };
      
      this.emitEvent(event);
      return true;
    } catch (error) {
      console.error("注销智能体失败:", error);
      return false;
    }
  }

  // 提交任务
  async submitTask(task: TaskRequest): Promise<string> {
    try {
      this.tasks.set(task.id, task);
      
      // 自动分配任务
      const assignment = await this.assignTask(task);
      if (assignment) {
        this.assignments.set(task.id, assignment);
        
        const event: CoordinationEvent = {
          id: `event-${Date.now()}`,
          type: "task_assigned",
          timestamp: new Date(),
          data: { taskId: task.id, agentId: assignment.agentId }
        };
        
        this.emitEvent(event);
      }
      
      return task.id;
    } catch (error) {
      console.error("提交任务失败:", error);
      throw error;
    }
  }

  // 分配任务
  private async assignTask(task: TaskRequest): Promise<TaskAssignment | null> {
    // 找到最适合的智能体
    const suitableAgent = this.findBestAgent(task);
    if (!suitableAgent) {
      console.warn("没有找到合适的智能体处理任务:", task.id);
      return null;
    }

    const assignment: TaskAssignment = {
      taskId: task.id,
      agentId: suitableAgent.id,
      assignedAt: new Date(),
      estimatedCompletion: new Date(Date.now() + 30 * 60 * 1000), // 30分钟后
      status: "assigned"
    };

    // 更新智能体负载
    suitableAgent.load += 0.1;
    this.agents.set(suitableAgent.id, suitableAgent);

    return assignment;
  }

  // 找到最佳智能体
  private findBestAgent(task: TaskRequest): AgentInfo | null {
    let bestAgent: AgentInfo | null = null;
    let bestScore = -1;

    for (const agent of this.agents.values()) {
      if (agent.status !== "active") {
        continue;
      }

      // 检查能力匹配
      const capabilityMatch = task.requiredCapabilities.every(cap =>
        agent.capabilities.includes(cap)
      );

      if (!capabilityMatch) {
        continue;
      }

      // 计算分数（负载越低分数越高）
      const score = 1 - agent.load;
      
      if (score > bestScore) {
        bestScore = score;
        bestAgent = agent;
      }
    }

    return bestAgent;
  }

  // 更新任务状态
  async updateTaskStatus(
    taskId: string, 
    status: TaskAssignment['status'],
    result?: unknown
  ): Promise<boolean> {
    try {
      const assignment = this.assignments.get(taskId);
      if (!assignment) {
        return false;
      }

      assignment.status = status;
      this.assignments.set(taskId, assignment);

      // 如果任务完成，减少智能体负载
      if (status === "completed" || status === "failed") {
        const agent = this.agents.get(assignment.agentId);
        if (agent) {
          agent.load = Math.max(0, agent.load - 0.1);
          this.agents.set(agent.id, agent);
        }

        const event: CoordinationEvent = {
          id: `event-${Date.now()}`,
          type: "task_completed",
          timestamp: new Date(),
          data: { taskId, status, result }
        };
        
        this.emitEvent(event);
      }

      return true;
    } catch (error) {
      console.error("更新任务状态失败:", error);
      return false;
    }
  }

  // 获取智能体列表
  getAgents(): AgentInfo[] {
    return Array.from(this.agents.values());
  }

  // 获取活跃智能体
  getActiveAgents(): AgentInfo[] {
    return this.getAgents().filter(agent => agent.status === "active");
  }

  // 获取任务状态
  getTaskStatus(taskId: string): TaskAssignment | null {
    return this.assignments.get(taskId) || null;
  }

  // 获取智能体负载统计
  getLoadStatistics(): { agentId: string; name: string; load: number; }[] {
    return this.getAgents().map(agent => ({
      agentId: agent.id,
      name: agent.name,
      load: agent.load
    }));
  }

  // 开始心跳监控
  private startHeartbeatMonitoring(): void {
    setInterval(() => {
      const now = new Date();
      for (const [agentId, agent] of this.agents.entries()) {
        const timeSinceHeartbeat = now.getTime() - agent.lastHeartbeat.getTime();
        
        // 如果超过5分钟没有心跳，标记为不活跃
        if (timeSinceHeartbeat > 5 * 60 * 1000 && agent.status === "active") {
          agent.status = "inactive";
          this.agents.set(agentId, agent);
          
          const event: CoordinationEvent = {
            id: `event-${Date.now()}`,
            type: "agent_status_changed",
            timestamp: new Date(),
            data: { agentId, status: "inactive", reason: "heartbeat_timeout" }
          };
          
          this.emitEvent(event);
        }
      }
    }, 60000); // 每分钟检查一次
  }

  // 更新智能体心跳
  async updateHeartbeat(agentId: string): Promise<boolean> {
    const agent = this.agents.get(agentId);
    if (!agent) {
      return false;
    }

    agent.lastHeartbeat = new Date();
    if (agent.status === "inactive") {
      agent.status = "active";
    }
    
    this.agents.set(agentId, agent);
    return true;
  }

  // 添加事件监听器
  addEventListener(listener: (event: CoordinationEvent) => void): void {
    this.eventListeners.push(listener);
  }

  // 移除事件监听器
  removeEventListener(listener: (event: CoordinationEvent) => void): void {
    const index = this.eventListeners.indexOf(listener);
    if (index > -1) {
      this.eventListeners.splice(index, 1);
    }
  }

  // 发出事件
  private emitEvent(event: CoordinationEvent): void {
    this.eventHistory.push(event);
    
    // 保持事件历史在合理范围内
    if (this.eventHistory.length > 1000) {
      this.eventHistory = this.eventHistory.slice(-500);
    }

    // 通知所有监听器
    for (const listener of this.eventListeners) {
      try {
        listener(event);
      } catch (error) {
        console.error("事件监听器执行失败:", error);
      }
    }
  }

  // 获取事件历史
  getEventHistory(limit: number = 100): CoordinationEvent[] {
    return this.eventHistory.slice(-limit);
  }

  // 获取系统状态
  getSystemStatus(): {
    totalAgents: number;
    activeAgents: number;
    totalTasks: number;
    completedTasks: number;
    averageLoad: number;
  } {
    const agents = this.getAgents();
    const activeAgents = this.getActiveAgents();
    const assignments = Array.from(this.assignments.values());
    const completedTasks = assignments.filter(a => a.status === "completed");
    const averageLoad = agents.length > 0 
      ? agents.reduce((sum, agent) => sum + agent.load, 0) / agents.length 
      : 0;

    return {
      totalAgents: agents.length,
      activeAgents: activeAgents.length,
      totalTasks: this.tasks.size,
      completedTasks: completedTasks.length,
      averageLoad
    };
  }
}

// 导出单例实例
export const agentCoordinationService = new AgentCoordinationService();
export default agentCoordinationService; 
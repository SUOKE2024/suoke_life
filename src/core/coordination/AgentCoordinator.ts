/**
 * 索克生活 - 智能体协调系统
 * 实现四个智能体（小艾、小克、老克、索儿）之间的协作和任务分配
 */

import { errorHandler, ErrorType } from '../error/ErrorHandler';
import { performanceMonitor, PerformanceCategory } from '../monitoring/PerformanceMonitor';

export enum AgentType {
  XIAOAI = 'XIAOAI',     // 小艾 - 健康助手 & 首页聊天频道版主
  XIAOKE = 'XIAOKE',     // 小克 - 中医诊断专家
  LAOKE = 'LAOKE',       // 老克 - 资深健康顾问
  SOER = 'SOER'          // 索儿 - 生活方式指导师
}

export enum TaskType {
  HEALTH_CONSULTATION = 'HEALTH_CONSULTATION',
  DIAGNOSIS = 'DIAGNOSIS',
  LIFESTYLE_GUIDANCE = 'LIFESTYLE_GUIDANCE',
  EMERGENCY_RESPONSE = 'EMERGENCY_RESPONSE',
  DATA_ANALYSIS = 'DATA_ANALYSIS',
  USER_INTERACTION = 'USER_INTERACTION',
  KNOWLEDGE_SHARING = 'KNOWLEDGE_SHARING'
}

export enum TaskPriority {
  LOW = 1,
  MEDIUM = 2,
  HIGH = 3,
  URGENT = 4,
  EMERGENCY = 5
}

export enum TaskStatus {
  PENDING = 'PENDING',
  ASSIGNED = 'ASSIGNED',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED'
}

export interface AgentCapability {
  type: TaskType;
  proficiency: number; // 0-1之间，表示熟练度
  maxConcurrentTasks: number;
  averageProcessingTime: number; // 毫秒
  specializations: string[];
}

export interface AgentStatus {
  id: string;
  type: AgentType;
  isOnline: boolean;
  currentLoad: number; // 0-1之间，表示当前负载
  capabilities: AgentCapability[];
  activeTasks: string[];
  lastHeartbeat: number;
  performance: {
    successRate: number;
    averageResponseTime: number;
    totalTasksCompleted: number;
  };
}

export interface Task {
  id: string;
  type: TaskType;
  priority: TaskPriority;
  status: TaskStatus;
  assignedAgent?: AgentType;
  requesterUserId: string;
  data: any;
  metadata: {
    createdAt: number;
    assignedAt?: number;
    startedAt?: number;
    completedAt?: number;
    estimatedDuration?: number;
    actualDuration?: number;
  };
  dependencies?: string[]; // 依赖的其他任务ID
  collaborators?: AgentType[]; // 需要协作的其他智能体
  result?: any;
  error?: any;
}

export interface CoordinationRule {
  id: string;
  name: string;
  condition: (task: Task, agents: Map<AgentType, AgentStatus>) => boolean;
  action: (task: Task, agents: Map<AgentType, AgentStatus>) => AgentType | null;
  priority: number;
}

export interface CollaborationRequest {
  id: string;
  fromAgent: AgentType;
  toAgent: AgentType;
  taskId: string;
  requestType: 'CONSULTATION' | 'HANDOVER' | 'ASSISTANCE' | 'KNOWLEDGE_SHARE';
  data: any;
  timestamp: number;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'COMPLETED';
}

export class AgentCoordinator {
  private static instance: AgentCoordinator;
  private agents: Map<AgentType, AgentStatus> = new Map();
  private tasks: Map<string, Task> = new Map();
  private coordinationRules: CoordinationRule[] = [];
  private collaborationRequests: Map<string, CollaborationRequest> = new Map();
  private taskQueue: Task[] = [];
  private isRunning: boolean = false;
  private coordinationInterval: NodeJS.Timeout | null = null;

  private constructor() {
    this.setupDefaultRules();
    this.initializeAgents();
  }

  public static getInstance(): AgentCoordinator {
    if (!AgentCoordinator.instance) {
      AgentCoordinator.instance = new AgentCoordinator();
    }
    return AgentCoordinator.instance;
  }

  /**
   * 启动协调系统
   */
  public start(): void {
    if (this.isRunning) {
      return;
    }

    this.isRunning = true;
    this.coordinationInterval = setInterval(() => {
      this.processTaskQueue();
      this.monitorAgentHealth();
      this.optimizeTaskDistribution();
    }, 1000);

    console.log('🤝 Agent coordination system started');
  }

  /**
   * 停止协调系统
   */
  public stop(): void {
    if (!this.isRunning) {
      return;
    }

    this.isRunning = false;
    if (this.coordinationInterval) {
      clearInterval(this.coordinationInterval);
      this.coordinationInterval = null;
    }

    console.log('⏹️ Agent coordination system stopped');
  }

  /**
   * 提交任务
   */
  public async submitTask(
    type: TaskType,
    priority: TaskPriority,
    requesterUserId: string,
    data: any,
    options: {
      estimatedDuration?: number;
      dependencies?: string[];
      collaborators?: AgentType[];
    } = {}
  ): Promise<string> {
    const taskId = this.generateTaskId();
    
    const task: Task = {
      id: taskId,
      type,
      priority,
      status: TaskStatus.PENDING,
      requesterUserId,
      data,
      metadata: {
        createdAt: Date.now(),
        estimatedDuration: options.estimatedDuration
      },
      dependencies: options.dependencies,
      collaborators: options.collaborators
    };

    this.tasks.set(taskId, task);
    this.taskQueue.push(task);
    this.sortTaskQueue();

    console.log(`📋 Task submitted: ${taskId} (${type}, priority: ${priority})`);
    
    // 立即尝试分配任务
    await this.processTaskQueue();
    
    return taskId;
  }

  /**
   * 获取任务状态
   */
  public getTaskStatus(taskId: string): Task | null {
    return this.tasks.get(taskId) || null;
  }

  /**
   * 取消任务
   */
  public cancelTask(taskId: string): boolean {
    const task = this.tasks.get(taskId);
    if (!task) {
      return false;
    }

    if (task.status === TaskStatus.IN_PROGRESS) {
      // 通知智能体停止任务
      this.notifyAgentTaskCancellation(task);
    }

    task.status = TaskStatus.CANCELLED;
    this.removeFromQueue(taskId);
    
    console.log(`❌ Task cancelled: ${taskId}`);
    return true;
  }

  /**
   * 注册智能体
   */
  public registerAgent(agentStatus: AgentStatus): void {
    this.agents.set(agentStatus.type, agentStatus);
    console.log(`🤖 Agent registered: ${agentStatus.type}`);
  }

  /**
   * 更新智能体状态
   */
  public updateAgentStatus(agentType: AgentType, updates: Partial<AgentStatus>): void {
    const agent = this.agents.get(agentType);
    if (agent) {
      Object.assign(agent, updates);
      agent.lastHeartbeat = Date.now();
    }
  }

  /**
   * 智能体心跳
   */
  public agentHeartbeat(agentType: AgentType, status: Partial<AgentStatus>): void {
    this.updateAgentStatus(agentType, {
      ...status,
      lastHeartbeat: Date.now(),
      isOnline: true
    });
  }

  /**
   * 任务完成通知
   */
  public notifyTaskCompleted(taskId: string, result: any): void {
    const task = this.tasks.get(taskId);
    if (!task) {
      return;
    }

    task.status = TaskStatus.COMPLETED;
    task.result = result;
    task.metadata.completedAt = Date.now();
    
    if (task.metadata.startedAt) {
      task.metadata.actualDuration = task.metadata.completedAt - task.metadata.startedAt;
    }

    // 更新智能体性能统计
    this.updateAgentPerformance(task.assignedAgent!, true, task.metadata.actualDuration || 0);

    // 检查是否有依赖此任务的其他任务
    this.checkDependentTasks(taskId);

    console.log(`✅ Task completed: ${taskId}`);
  }

  /**
   * 任务失败通知
   */
  public notifyTaskFailed(taskId: string, error: any): void {
    const task = this.tasks.get(taskId);
    if (!task) {
      return;
    }

    task.status = TaskStatus.FAILED;
    task.error = error;
    task.metadata.completedAt = Date.now();

    // 更新智能体性能统计
    this.updateAgentPerformance(task.assignedAgent!, false, 0);

    // 尝试重新分配任务
    if (task.priority >= TaskPriority.HIGH) {
      task.status = TaskStatus.PENDING;
      task.assignedAgent = undefined;
      this.taskQueue.push(task);
      this.sortTaskQueue();
    }

    console.log(`❌ Task failed: ${taskId}`, error);
  }

  /**
   * 请求智能体协作
   */
  public async requestCollaboration(
    fromAgent: AgentType,
    toAgent: AgentType,
    taskId: string,
    requestType: CollaborationRequest['requestType'],
    data: any
  ): Promise<string> {
    const requestId = this.generateRequestId();
    
    const request: CollaborationRequest = {
      id: requestId,
      fromAgent,
      toAgent,
      taskId,
      requestType,
      data,
      timestamp: Date.now(),
      status: 'PENDING'
    };

    this.collaborationRequests.set(requestId, request);
    
    // 通知目标智能体
    await this.notifyAgentCollaborationRequest(request);
    
    console.log(`🤝 Collaboration requested: ${fromAgent} -> ${toAgent} (${requestType})`);
    return requestId;
  }

  /**
   * 响应协作请求
   */
  public respondToCollaboration(
    requestId: string,
    accepted: boolean,
    responseData?: any
  ): void {
    const request = this.collaborationRequests.get(requestId);
    if (!request) {
      return;
    }

    request.status = accepted ? 'ACCEPTED' : 'REJECTED';
    
    if (accepted && responseData) {
      request.data = { ...request.data, response: responseData };
    }

    // 通知发起智能体
    this.notifyAgentCollaborationResponse(request, accepted, responseData);
    
    console.log(`🤝 Collaboration ${accepted ? 'accepted' : 'rejected'}: ${requestId}`);
  }

  /**
   * 获取智能体状态
   */
  public getAgentStatus(agentType: AgentType): AgentStatus | null {
    return this.agents.get(agentType) || null;
  }

  /**
   * 获取所有智能体状态
   */
  public getAllAgentStatuses(): Map<AgentType, AgentStatus> {
    return new Map(this.agents);
  }

  /**
   * 获取任务队列状态
   */
  public getQueueStatus(): {
    pending: number;
    inProgress: number;
    completed: number;
    failed: number;
  } {
    const pending = this.taskQueue.length;
    let inProgress = 0;
    let completed = 0;
    let failed = 0;

    for (const task of this.tasks.values()) {
      switch (task.status) {
        case TaskStatus.IN_PROGRESS:
          inProgress++;
          break;
        case TaskStatus.COMPLETED:
          completed++;
          break;
        case TaskStatus.FAILED:
          failed++;
          break;
      }
    }

    return { pending, inProgress, completed, failed };
  }

  private async processTaskQueue(): Promise<void> {
    if (this.taskQueue.length === 0) {
      return;
    }

    const availableTasks = this.taskQueue.filter(task => 
      task.status === TaskStatus.PENDING && this.areDependenciesMet(task)
    );

    for (const task of availableTasks) {
      const assignedAgent = await this.assignTask(task);
      if (assignedAgent) {
        task.assignedAgent = assignedAgent;
        task.status = TaskStatus.ASSIGNED;
        task.metadata.assignedAt = Date.now();
        
        // 从队列中移除
        this.removeFromQueue(task.id);
        
        // 通知智能体开始任务
        await this.notifyAgentTaskAssignment(task);
      }
    }
  }

  private async assignTask(task: Task): Promise<AgentType | null> {
    return performanceMonitor.measureAsync(
      'task_assignment',
      PerformanceCategory.AGENT,
      async () => {
        // 应用协调规则
        for (const rule of this.coordinationRules) {
          if (rule.condition(task, this.agents)) {
            const assignedAgent = rule.action(task, this.agents);
            if (assignedAgent && this.isAgentAvailable(assignedAgent, task)) {
              return assignedAgent;
            }
          }
        }

        // 默认分配逻辑：基于能力和负载
        return this.findBestAgent(task);
      }
    );
  }

  private findBestAgent(task: Task): AgentType | null {
    let bestAgent: AgentType | null = null;
    let bestScore = -1;

    for (const [agentType, agentStatus] of this.agents.entries()) {
      if (!this.isAgentAvailable(agentType, task)) {
        continue;
      }

      const capability = agentStatus.capabilities.find(cap => cap.type === task.type);
      if (!capability) {
        continue;
      }

      // 计算分配分数：能力熟练度 - 当前负载
      const score = capability.proficiency - agentStatus.currentLoad;
      
      if (score > bestScore) {
        bestScore = score;
        bestAgent = agentType;
      }
    }

    return bestAgent;
  }

  private isAgentAvailable(agentType: AgentType, task: Task): boolean {
    const agent = this.agents.get(agentType);
    if (!agent || !agent.isOnline) {
      return false;
    }

    // 检查负载
    if (agent.currentLoad >= 1.0) {
      return false;
    }

    // 检查并发任务限制
    const capability = agent.capabilities.find(cap => cap.type === task.type);
    if (capability && agent.activeTasks.length >= capability.maxConcurrentTasks) {
      return false;
    }

    return true;
  }

  private areDependenciesMet(task: Task): boolean {
    if (!task.dependencies || task.dependencies.length === 0) {
      return true;
    }

    return task.dependencies.every(depId => {
      const depTask = this.tasks.get(depId);
      return depTask && depTask.status === TaskStatus.COMPLETED;
    });
  }

  private sortTaskQueue(): void {
    this.taskQueue.sort((a, b) => {
      // 首先按优先级排序
      if (a.priority !== b.priority) {
        return b.priority - a.priority;
      }
      // 然后按创建时间排序
      return a.metadata.createdAt - b.metadata.createdAt;
    });
  }

  private removeFromQueue(taskId: string): void {
    const index = this.taskQueue.findIndex(task => task.id === taskId);
    if (index > -1) {
      this.taskQueue.splice(index, 1);
    }
  }

  private checkDependentTasks(completedTaskId: string): void {
    for (const task of this.taskQueue) {
      if (task.dependencies?.includes(completedTaskId)) {
        // 重新检查是否可以分配
        if (this.areDependenciesMet(task)) {
          console.log(`📋 Task ${task.id} dependencies met, ready for assignment`);
        }
      }
    }
  }

  private updateAgentPerformance(agentType: AgentType, success: boolean, duration: number): void {
    const agent = this.agents.get(agentType);
    if (!agent) return;

    const perf = agent.performance;
    const totalTasks = perf.totalTasksCompleted + 1;
    
    // 更新成功率
    perf.successRate = (perf.successRate * perf.totalTasksCompleted + (success ? 1 : 0)) / totalTasks;
    
    // 更新平均响应时间
    if (success && duration > 0) {
      perf.averageResponseTime = (perf.averageResponseTime * perf.totalTasksCompleted + duration) / totalTasks;
    }
    
    perf.totalTasksCompleted = totalTasks;
  }

  private monitorAgentHealth(): void {
    const now = Date.now();
    const healthCheckThreshold = 30000; // 30秒

    for (const [agentType, agent] of this.agents.entries()) {
      if (now - agent.lastHeartbeat > healthCheckThreshold) {
        agent.isOnline = false;
        console.warn(`⚠️ Agent ${agentType} appears to be offline`);
        
        // 重新分配该智能体的任务
        this.reassignAgentTasks(agentType);
      }
    }
  }

  private reassignAgentTasks(agentType: AgentType): void {
    for (const task of this.tasks.values()) {
      if (task.assignedAgent === agentType && task.status === TaskStatus.IN_PROGRESS) {
        task.status = TaskStatus.PENDING;
        task.assignedAgent = undefined;
        this.taskQueue.push(task);
        console.log(`🔄 Reassigning task ${task.id} due to agent ${agentType} being offline`);
      }
    }
    this.sortTaskQueue();
  }

  private optimizeTaskDistribution(): void {
    // 检查负载均衡
    const onlineAgents = Array.from(this.agents.values()).filter(agent => agent.isOnline);
    if (onlineAgents.length === 0) return;

    const avgLoad = onlineAgents.reduce((sum, agent) => sum + agent.currentLoad, 0) / onlineAgents.length;
    const overloadedAgents = onlineAgents.filter(agent => agent.currentLoad > avgLoad + 0.3);
    const underloadedAgents = onlineAgents.filter(agent => agent.currentLoad < avgLoad - 0.3);

    if (overloadedAgents.length > 0 && underloadedAgents.length > 0) {
      console.log('⚖️ Load balancing needed, considering task redistribution');
      // 这里可以实现更复杂的负载均衡逻辑
    }
  }

  private async notifyAgentTaskAssignment(task: Task): Promise<void> {
    try {
      // 这里应该调用具体智能体的API来分配任务
      console.log(`📤 Notifying ${task.assignedAgent} of task assignment: ${task.id}`);
      
      // 更新智能体状态
      const agent = this.agents.get(task.assignedAgent!);
      if (agent) {
        agent.activeTasks.push(task.id);
        agent.currentLoad = Math.min(1.0, agent.currentLoad + 0.1);
      }

      task.status = TaskStatus.IN_PROGRESS;
      task.metadata.startedAt = Date.now();
      
    } catch (error) {
      await errorHandler.handleError(error as Error, {
        agentId: task.assignedAgent,
        requestId: task.id
      });
    }
  }

  private notifyAgentTaskCancellation(task: Task): void {
    console.log(`📤 Notifying ${task.assignedAgent} of task cancellation: ${task.id}`);
    
    // 更新智能体状态
    const agent = this.agents.get(task.assignedAgent!);
    if (agent) {
      const index = agent.activeTasks.indexOf(task.id);
      if (index > -1) {
        agent.activeTasks.splice(index, 1);
        agent.currentLoad = Math.max(0, agent.currentLoad - 0.1);
      }
    }
  }

  private async notifyAgentCollaborationRequest(request: CollaborationRequest): Promise<void> {
    console.log(`📤 Notifying ${request.toAgent} of collaboration request: ${request.id}`);
    // 这里应该调用具体智能体的API来通知协作请求
  }

  private notifyAgentCollaborationResponse(
    request: CollaborationRequest,
    accepted: boolean,
    responseData?: any
  ): void {
    console.log(`📤 Notifying ${request.fromAgent} of collaboration response: ${request.id} (${accepted ? 'accepted' : 'rejected'})`);
    // 这里应该调用具体智能体的API来通知协作响应
  }

  private setupDefaultRules(): void {
    // 紧急任务优先分配给在线的智能体
    this.coordinationRules.push({
      id: 'emergency_priority',
      name: '紧急任务优先处理',
      condition: (task) => task.priority === TaskPriority.EMERGENCY,
      action: (task, agents) => {
        for (const [agentType, agent] of agents.entries()) {
          if (agent.isOnline && agent.currentLoad < 0.8) {
            return agentType;
          }
        }
        return null;
      },
      priority: 1
    });

    // 健康咨询分配给小艾
    this.coordinationRules.push({
      id: 'health_consultation_to_xiaoai',
      name: '健康咨询分配给小艾',
      condition: (task) => task.type === TaskType.HEALTH_CONSULTATION,
      action: (task, agents) => {
        const xiaoai = agents.get(AgentType.XIAOAI);
        return xiaoai?.isOnline ? AgentType.XIAOAI : null;
      },
      priority: 2
    });

    // 诊断任务分配给小克
    this.coordinationRules.push({
      id: 'diagnosis_to_xiaoke',
      name: '诊断任务分配给小克',
      condition: (task) => task.type === TaskType.DIAGNOSIS,
      action: (task, agents) => {
        const xiaoke = agents.get(AgentType.XIAOKE);
        return xiaoke?.isOnline ? AgentType.XIAOKE : null;
      },
      priority: 2
    });

    // 生活方式指导分配给索儿
    this.coordinationRules.push({
      id: 'lifestyle_to_soer',
      name: '生活方式指导分配给索儿',
      condition: (task) => task.type === TaskType.LIFESTYLE_GUIDANCE,
      action: (task, agents) => {
        const soer = agents.get(AgentType.SOER);
        return soer?.isOnline ? AgentType.SOER : null;
      },
      priority: 2
    });
  }

  private initializeAgents(): void {
    // 初始化小艾
    this.registerAgent({
      id: 'xiaoai_001',
      type: AgentType.XIAOAI,
      isOnline: false,
      currentLoad: 0,
      capabilities: [
        {
          type: TaskType.HEALTH_CONSULTATION,
          proficiency: 0.9,
          maxConcurrentTasks: 5,
          averageProcessingTime: 2000,
          specializations: ['健康咨询', '用户交互', '聊天管理']
        },
        {
          type: TaskType.USER_INTERACTION,
          proficiency: 0.95,
          maxConcurrentTasks: 10,
          averageProcessingTime: 1000,
          specializations: ['多语言交互', '情感识别', '个性化服务']
        }
      ],
      activeTasks: [],
      lastHeartbeat: 0,
      performance: {
        successRate: 0.95,
        averageResponseTime: 1500,
        totalTasksCompleted: 0
      }
    });

    // 初始化小克
    this.registerAgent({
      id: 'xiaoke_001',
      type: AgentType.XIAOKE,
      isOnline: false,
      currentLoad: 0,
      capabilities: [
        {
          type: TaskType.DIAGNOSIS,
          proficiency: 0.95,
          maxConcurrentTasks: 3,
          averageProcessingTime: 5000,
          specializations: ['中医诊断', '四诊合参', '辨证论治']
        },
        {
          type: TaskType.DATA_ANALYSIS,
          proficiency: 0.85,
          maxConcurrentTasks: 2,
          averageProcessingTime: 3000,
          specializations: ['健康数据分析', '趋势预测']
        }
      ],
      activeTasks: [],
      lastHeartbeat: 0,
      performance: {
        successRate: 0.92,
        averageResponseTime: 4000,
        totalTasksCompleted: 0
      }
    });

    // 初始化老克
    this.registerAgent({
      id: 'laoke_001',
      type: AgentType.LAOKE,
      isOnline: false,
      currentLoad: 0,
      capabilities: [
        {
          type: TaskType.KNOWLEDGE_SHARING,
          proficiency: 0.98,
          maxConcurrentTasks: 2,
          averageProcessingTime: 3000,
          specializations: ['资深咨询', '复杂病例', '知识传授']
        },
        {
          type: TaskType.EMERGENCY_RESPONSE,
          proficiency: 0.9,
          maxConcurrentTasks: 1,
          averageProcessingTime: 1000,
          specializations: ['紧急处理', '危机干预']
        }
      ],
      activeTasks: [],
      lastHeartbeat: 0,
      performance: {
        successRate: 0.98,
        averageResponseTime: 2500,
        totalTasksCompleted: 0
      }
    });

    // 初始化索儿
    this.registerAgent({
      id: 'soer_001',
      type: AgentType.SOER,
      isOnline: false,
      currentLoad: 0,
      capabilities: [
        {
          type: TaskType.LIFESTYLE_GUIDANCE,
          proficiency: 0.92,
          maxConcurrentTasks: 4,
          averageProcessingTime: 2500,
          specializations: ['生活方式指导', '健康计划', '行为改变']
        },
        {
          type: TaskType.DATA_ANALYSIS,
          proficiency: 0.8,
          maxConcurrentTasks: 2,
          averageProcessingTime: 3500,
          specializations: ['生活数据分析', '习惯追踪']
        }
      ],
      activeTasks: [],
      lastHeartbeat: 0,
      performance: {
        successRate: 0.94,
        averageResponseTime: 2800,
        totalTasksCompleted: 0
      }
    });
  }

  private generateTaskId(): string {
    return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// 导出单例实例
export const agentCoordinator = AgentCoordinator.getInstance();

// 便捷函数
export const submitTask = (
  type: TaskType,
  priority: TaskPriority,
  requesterUserId: string,
  data: any,
  options?: any
) => agentCoordinator.submitTask(type, priority, requesterUserId, data, options);

export const getTaskStatus = (taskId: string) => agentCoordinator.getTaskStatus(taskId);

export const cancelTask = (taskId: string) => agentCoordinator.cancelTask(taskId); 
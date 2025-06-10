import { EventEmitter } from 'events';
import { AgentBase } from '../base/AgentBase';

/**
 * 任务状态枚举
 */
export enum TaskStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

/**
 * 任务优先级枚举
 */
export enum TaskPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

/**
 * 协作任务接口
 */
export interface CollaborationTask {
  id: string;
  healthContext: any;
  requiredCapabilities: string[];
  priority: TaskPriority;
  status: TaskStatus;
  createdAt: Date;
  assignedAgents: string[];
  result: any;
  updatedAt?: Date;
  completedAt?: Date;
}

/**
 * 协作会话接口
 */
export interface CollaborationSession {
  id: string;
  taskId: string;
  participants: string[];
  startTime: Date;
  endTime?: Date;
  status: 'active' | 'completed' | 'failed' | 'cancelled';
  decisions: CollaborationDecision[];
  consensusReached: boolean;
  metadata?: Record<string, any>;
}

/**
 * 协作决策接口
 */
export interface CollaborationDecision {
  id: string;
  sessionId: string;
  agentId: string;
  decision: string;
  confidence: number;
  reasoning: string[];
  timestamp: Date;
  supportingData?: any;
}

/**
 * 智能体信息接口
 */
export interface AgentInfo {
  id: string;
  name: string;
  capabilities: string[];
  priority: TaskPriority;
  status: string;
  load?: number;
  responseTime?: number;
}

/**
 * 智能体协同决策框架
 * 实现小艾、小克、老克、索儿四个智能体的分布式自主协作
 */
export class AgentCollaborationFramework extends EventEmitter {
  private agents: Map<string, AgentInfo> = new Map();
  private agentInstances: Map<string, AgentBase> = new Map();
  private taskQueue: CollaborationTask[] = [];
  private activeCollaborations: Map<string, CollaborationSession> = new Map();
  private isInitialized: boolean = false;

  constructor() {
    super();
    this.setMaxListeners(50); // 增加监听器限制
  }

  /**
   * 初始化协作框架
   */
  async initialize(): Promise<void> {
    try {
      this.log('info', '初始化智能体协作框架...');
      await this.initializeAgents();
      this.isInitialized = true;
      this.log('info', '智能体协作框架初始化完成');
    } catch (error) {
      this.log('error', '智能体协作框架初始化失败', error);
      throw error;
    }
  }

  /**
   * 初始化四个核心智能体
   */
  private async initializeAgents(): Promise<void> {
    // 小艾 - AI健康助手，负责用户交互和初步健康评估
    this.registerAgent('xiaoai', {
      id: 'xiaoai',
      name: '小艾',
      capabilities: [
        'user_interaction',
        'health_assessment',
        'symptom_analysis',
      ],
      priority: TaskPriority.HIGH,
      status: 'active',
    });

    // 小克 - 专业诊断智能体，负责中医辨证和现代医学诊断
    this.registerAgent('xiaoke', {
      id: 'xiaoke',
      name: '小克',
      capabilities: [
        'tcm_diagnosis',
        'modern_diagnosis',
        'syndrome_differentiation',
      ],
      priority: TaskPriority.CRITICAL,
      status: 'active',
    });

    // 老克 - 资深健康顾问，负责治疗方案制定和健康管理
    this.registerAgent('laoke', {
      id: 'laoke',
      name: '老克',
      capabilities: [
        'treatment_planning',
        'health_management',
        'lifestyle_guidance',
      ],
      priority: TaskPriority.HIGH,
      status: 'active',
    });

    // 索儿 - 生活服务智能体，负责食农结合和山水养生服务
    this.registerAgent('soer', {
      id: 'soer',
      name: '索儿',
      capabilities: [
        'lifestyle_services',
        'food_agriculture',
        'wellness_tourism',
      ],
      priority: TaskPriority.MEDIUM,
      status: 'active',
    });
  }

  /**
   * 注册智能体
   */
  registerAgent(id: string, agentInfo: AgentInfo): void {
    this.agents.set(id, agentInfo);
    this.emit('agent_registered', { agentId: id, agentInfo });
    this.log('info', `智能体已注册: ${id} (${agentInfo.name})`);
  }

  /**
   * 注册智能体实例
   */
  registerAgentInstance(id: string, instance: AgentBase): void {
    this.agentInstances.set(id, instance);
    this.log('info', `智能体实例已注册: ${id}`);
  }

  /**
   * 创建协作任务
   */
  async createCollaborationTask(
    healthContext: any,
    requiredCapabilities: string[],
    priority: TaskPriority = TaskPriority.MEDIUM
  ): Promise<string> {
    if (!this.isInitialized) {
      throw new Error('协作框架未初始化');
    }

    const taskId = this.generateTaskId();
    const task: CollaborationTask = {
      id: taskId,
      healthContext,
      requiredCapabilities,
      priority,
      status: TaskStatus.PENDING,
      createdAt: new Date(),
      assignedAgents: [],
      result: null,
    };

    // 根据能力匹配智能体
    const suitableAgents = this.findSuitableAgents(requiredCapabilities);
    if (suitableAgents.length === 0) {
      throw new Error('没有找到合适的智能体来处理此任务');
    }

    task.assignedAgents = suitableAgents;
    this.taskQueue.push(task);

    this.emit('task_created', task);
    this.log(
      'info',
      `协作任务已创建: ${taskId}, 分配给: ${suitableAgents.join(', ')}`
    );

    // 启动协作会话
    await this.startCollaborationSession(task);
    return taskId;
  }

  /**
   * 启动协作会话
   */
  private async startCollaborationSession(
    task: CollaborationTask
  ): Promise<void> {
    const sessionId = `session_${task.id}`;
    const session: CollaborationSession = {
      id: sessionId,
      taskId: task.id,
      participants: task.assignedAgents,
      startTime: new Date(),
      status: 'active',
      decisions: [],
      consensusReached: false,
    };

    this.activeCollaborations.set(sessionId, session);
    this.log('info', `协作会话已启动: ${sessionId}`);

    // 通知参与的智能体开始协作
    for (const agentId of task.assignedAgents) {
      const agentInfo = this.agents.get(agentId);
      if (agentInfo) {
        this.emit('collaboration_started', {
          sessionId,
          agentId,
          task,
          healthContext: task.healthContext,
        });
      }
    }

    // 启动协作决策流程
    try {
      await this.executeCollaborationFlow(session, task);
    } catch (error) {
      this.log('error', `协作流程执行失败: ${sessionId}`, error);
      session.status = 'failed';
      task.status = TaskStatus.FAILED;
    }
  }

  /**
   * 执行协作决策流程
   */
  private async executeCollaborationFlow(
    session: CollaborationSession,
    task: CollaborationTask
  ): Promise<void> {
    try {
      task.status = TaskStatus.IN_PROGRESS;
      task.updatedAt = new Date();

      this.log('info', `开始执行协作流程: ${session.id}`);

      // 阶段1: 信息收集和初步分析（小艾主导）
      const analysisResults = await this.collectAnalysis(session, task);

      // 阶段2: 协同诊断和辨证（小克主导）
      const diagnosisResults = await this.performCollaborativeDiagnosis(
        session,
        analysisResults
      );

      // 阶段3: 治疗方案制定（老克主导）
      const treatmentPlan = await this.createTreatmentPlan(
        session,
        diagnosisResults
      );

      // 阶段4: 生活方式指导（索儿主导）
      const lifestyleGuidance = await this.generateLifestyleGuidance(
        session,
        treatmentPlan
      );

      // 整合最终结果
      task.result = {
        analysis: analysisResults,
        diagnosis: diagnosisResults,
        treatment: treatmentPlan,
        lifestyle: lifestyleGuidance,
        confidence: this.calculateConfidence(session),
        recommendations: this.generateRecommendations(session),
        sessionId: session.id,
        completedAt: new Date(),
      };

      task.status = TaskStatus.COMPLETED;
      task.completedAt = new Date();
      session.status = 'completed';
      session.endTime = new Date();
      session.consensusReached = true;

      this.emit('collaboration_completed', { session, task });
      this.log('info', `协作流程完成: ${session.id}`);
    } catch (error) {
      task.status = TaskStatus.FAILED;
      task.updatedAt = new Date();
      session.status = 'failed';
      session.endTime = new Date();

      this.emit('collaboration_failed', { session, task, error });
      this.log('error', `协作流程失败: ${session.id}`, error);
      throw error;
    }
  }

  /**
   * 信息收集和初步分析（小艾主导）
   */
  private async collectAnalysis(
    session: CollaborationSession,
    task: CollaborationTask
  ): Promise<any> {
    this.log('info', `开始信息收集阶段: ${session.id}`);

    const xiaoaiAgent = this.agents.get('xiaoai');
    if (!xiaoaiAgent) {
      throw new Error('小艾智能体未找到');
    }

    // 模拟小艾进行用户交互和症状收集
    const userInteraction = await this.invokeAgent(
      'xiaoai',
      'collect_symptoms',
      {
        healthContext: task.healthContext,
        sessionId: session.id,
      }
    );

    // 模拟小艾进行初步健康评估
    const healthAssessment = await this.invokeAgent('xiaoai', 'assess_health', {
      symptoms: userInteraction.symptoms,
      vitalSigns: task.healthContext.vitalSigns || {},
    });

    const result = {
      userInteraction,
      healthAssessment,
      timestamp: new Date(),
      stage: 'analysis',
    };

    // 记录决策
    this.recordDecision(
      session,
      'xiaoai',
      '信息收集完成',
      0.9,
      ['收集了用户症状信息', '完成了初步健康评估'],
      result
    );

    return result;
  }

  /**
   * 协同诊断和辨证（小克主导，其他智能体协助）
   */
  private async performCollaborativeDiagnosis(
    session: CollaborationSession,
    analysisResults: any
  ): Promise<any> {
    this.log('info', `开始协同诊断阶段: ${session.id}`);

    // 小克进行中医辨证
    const tcmDiagnosis = await this.invokeAgent('xiaoke', 'tcm_diagnosis', {
      symptoms: analysisResults.userInteraction.symptoms,
      constitution: analysisResults.healthAssessment.constitution,
    });

    // 小克进行现代医学诊断
    const modernDiagnosis = await this.invokeAgent(
      'xiaoke',
      'modern_diagnosis',
      {
        symptoms: analysisResults.userInteraction.symptoms,
        labResults: analysisResults.healthAssessment.labResults,
      }
    );

    // 老克提供诊断建议
    const seniorAdvice = await this.invokeAgent('laoke', 'review_diagnosis', {
      tcmDiagnosis,
      modernDiagnosis,
    });

    const result = {
      tcmDiagnosis,
      modernDiagnosis,
      seniorAdvice,
      confidence: this.calculateDiagnosisConfidence([
        tcmDiagnosis,
        modernDiagnosis,
        seniorAdvice,
      ]),
      timestamp: new Date(),
      stage: 'diagnosis',
    };

    // 记录决策
    this.recordDecision(
      session,
      'xiaoke',
      '协同诊断完成',
      0.85,
      ['完成中医辨证分析', '完成现代医学诊断', '获得资深顾问建议'],
      result
    );

    return result;
  }

  /**
   * 治疗方案制定（老克主导）
   */
  private async createTreatmentPlan(
    session: CollaborationSession,
    diagnosisResults: any
  ): Promise<any> {
    this.log('info', `开始治疗方案制定阶段: ${session.id}`);

    const treatmentPlan = await this.invokeAgent(
      'laoke',
      'create_treatment_plan',
      {
        diagnosis: diagnosisResults,
        patientProfile: session.participants,
      }
    );

    // 小克验证治疗方案的医学合理性
    const medicalValidation = await this.invokeAgent(
      'xiaoke',
      'validate_treatment',
      {
        treatmentPlan,
      }
    );

    const result = {
      plan: treatmentPlan,
      validation: medicalValidation,
      timestamp: new Date(),
      stage: 'treatment',
    };

    // 记录决策
    this.recordDecision(
      session,
      'laoke',
      '治疗方案制定完成',
      0.88,
      ['制定了个性化治疗方案', '通过了医学合理性验证'],
      result
    );

    return result;
  }

  /**
   * 生活方式指导（索儿主导）
   */
  private async generateLifestyleGuidance(
    session: CollaborationSession,
    treatmentPlan: any
  ): Promise<any> {
    this.log('info', `开始生活方式指导阶段: ${session.id}`);

    const lifestyleGuidance = await this.invokeAgent(
      'soer',
      'create_lifestyle_plan',
      {
        treatmentPlan,
        sessionId: session.id,
      }
    );

    const result = {
      guidance: lifestyleGuidance,
      timestamp: new Date(),
      stage: 'lifestyle',
    };

    // 记录决策
    this.recordDecision(
      session,
      'soer',
      '生活方式指导完成',
      0.82,
      ['制定了个性化生活方式指导', '整合了治疗方案要求'],
      result
    );

    return result;
  }

  /**
   * 查找合适的智能体
   */
  private findSuitableAgents(requiredCapabilities: string[]): string[] {
    const suitableAgents: string[] = [];

    for (const [agentId, agentInfo] of this.agents) {
      const hasRequiredCapabilities = requiredCapabilities.some((capability) =>
        agentInfo.capabilities.includes(capability)
      );

      if (hasRequiredCapabilities && agentInfo.status === 'active') {
        suitableAgents.push(agentId);
      }
    }

    // 按优先级排序
    suitableAgents.sort((a, b) => {
      const agentA = this.agents.get(a)!;
      const agentB = this.agents.get(b)!;
      const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
      return priorityOrder[agentB.priority] - priorityOrder[agentA.priority];
    });

    return suitableAgents;
  }

  /**
   * 调用智能体
   */
  private async invokeAgent(
    agentId: string,
    action: string,
    params: any
  ): Promise<any> {
    const agentInfo = this.agents.get(agentId);
    if (!agentInfo) {
      throw new Error(`智能体 ${agentId} 未找到`);
    }

    const agentInstance = this.agentInstances.get(agentId);

    // 如果有实际的智能体实例，调用它
    if (agentInstance) {
      try {
        // 这里应该调用实际的智能体方法
        // 暂时返回模拟结果
        return this.simulateAgentResponse(agentId, action, params);
      } catch (error) {
        this.log('error', `调用智能体 ${agentId} 失败`, error);
        throw error;
      }
    }

    // 模拟智能体调用
    return this.simulateAgentResponse(agentId, action, params);
  }

  /**
   * 模拟智能体响应
   */
  private simulateAgentResponse(
    agentId: string,
    action: string,
    params: any
  ): any {
    const timestamp = new Date();
    const baseResponse = {
      agentId,
      action,
      timestamp,
      params,
      success: true,
    };

    // 根据不同的智能体和动作返回不同的模拟结果
    switch (agentId) {
      case 'xiaoai':
        return {
          ...baseResponse,
          result: this.simulateXiaoaiResponse(action, params),
        };
      case 'xiaoke':
        return {
          ...baseResponse,
          result: this.simulateXiaokeResponse(action, params),
        };
      case 'laoke':
        return {
          ...baseResponse,
          result: this.simulateLaokeResponse(action, params),
        };
      case 'soer':
        return {
          ...baseResponse,
          result: this.simulateSoerResponse(action, params),
        };
      default:
        return {
          ...baseResponse,
          result: `${agentId} 执行 ${action} 的结果`,
        };
    }
  }

  /**
   * 模拟小艾的响应
   */
  private simulateXiaoaiResponse(action: string, params: any): any {
    switch (action) {
      case 'collect_symptoms':
        return {
          symptoms: ['头痛', '疲劳', '睡眠不佳'],
          severity: '中等',
          duration: '3天',
          triggers: ['工作压力', '天气变化'],
        };
      case 'assess_health':
        return {
          overallHealth: '良好',
          riskFactors: ['压力过大', '睡眠不足'],
          constitution: '气虚质',
          recommendations: ['调节作息', '适度运动'],
        };
      default:
        return `小艾执行${action}的结果`;
    }
  }

  /**
   * 模拟小克的响应
   */
  private simulateXiaokeResponse(action: string, params: any): any {
    switch (action) {
      case 'tcm_diagnosis':
        return {
          syndrome: '肝郁气滞',
          pattern: '气血不和',
          treatment: '疏肝理气',
          herbs: ['柴胡', '白芍', '当归'],
        };
      case 'modern_diagnosis':
        return {
          condition: '神经性头痛',
          severity: '轻度',
          treatment: '对症治疗',
          medications: ['布洛芬', '维生素B'],
        };
      case 'validate_treatment':
        return {
          valid: true,
          safety: '安全',
          interactions: '无明显相互作用',
          adjustments: [],
        };
      default:
        return `小克执行${action}的结果`;
    }
  }

  /**
   * 模拟老克的响应
   */
  private simulateLaokeResponse(action: string, params: any): any {
    switch (action) {
      case 'review_diagnosis':
        return {
          agreement: '基本同意',
          suggestions: ['建议进一步观察', '注意情绪调节'],
          confidence: 0.85,
        };
      case 'create_treatment_plan':
        return {
          phases: ['急性期治疗', '恢复期调理', '预防保健'],
          duration: '4-6周',
          monitoring: '每周复查',
          goals: ['缓解症状', '改善体质', '预防复发'],
        };
      default:
        return `老克执行${action}的结果`;
    }
  }

  /**
   * 模拟索儿的响应
   */
  private simulateSoerResponse(action: string, params: any): any {
    switch (action) {
      case 'create_lifestyle_plan':
        return {
          diet: '清淡饮食，多吃蔬菜水果',
          exercise: '每日散步30分钟',
          sleep: '晚上10点前睡觉',
          stress: '练习冥想和深呼吸',
          environment: '保持室内空气流通',
        };
      default:
        return `索儿执行${action}的结果`;
    }
  }

  /**
   * 记录协作决策
   */
  private recordDecision(
    session: CollaborationSession,
    agentId: string,
    decision: string,
    confidence: number,
    reasoning: string[],
    supportingData?: any
  ): void {
    const decisionRecord: CollaborationDecision = {
      id: `decision_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
      sessionId: session.id,
      agentId,
      decision,
      confidence,
      reasoning,
      timestamp: new Date(),
      supportingData,
    };

    session.decisions.push(decisionRecord);
    this.emit('decision_recorded', decisionRecord);
  }

  /**
   * 计算整体置信度
   */
  private calculateConfidence(session: CollaborationSession): number {
    if (session.decisions.length === 0) return 0;

    const totalConfidence = session.decisions.reduce(
      (sum, decision) => sum + decision.confidence,
      0
    );
    return totalConfidence / session.decisions.length;
  }

  /**
   * 计算诊断置信度
   */
  private calculateDiagnosisConfidence(diagnoses: any[]): number {
    // 简化的诊断置信度计算
    return 0.85 + Math.random() * 0.1;
  }

  /**
   * 生成建议
   */
  private generateRecommendations(session: CollaborationSession): string[] {
    const recommendations = [
      '建议定期复查',
      '注意饮食调理',
      '保持适度运动',
      '调节情绪状态',
      '改善睡眠质量',
    ];

    // 根据会话中的决策生成更具体的建议
    const specificRecommendations = session.decisions
      .flatMap((decision) => decision.reasoning)
      .filter((reason, index, array) => array.indexOf(reason) === index)
      .slice(0, 3);

    return [...recommendations, ...specificRecommendations];
  }

  /**
   * 生成任务ID
   */
  private generateTaskId(): string {
    return `task_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;
  }

  /**
   * 获取任务状态
   */
  getTaskStatus(taskId: string): CollaborationTask | undefined {
    return this.taskQueue.find((task) => task.id === taskId);
  }

  /**
   * 获取活跃协作会话
   */
  getActiveCollaborations(): Map<string, CollaborationSession> {
    return new Map(this.activeCollaborations);
  }

  /**
   * 获取任务队列
   */
  getTaskQueue(): CollaborationTask[] {
    return [...this.taskQueue];
  }

  /**
   * 获取智能体状态
   */
  getAgentStatus(): Map<string, AgentInfo> {
    return new Map(this.agents);
  }

  /**
   * 获取协作统计信息
   */
  getCollaborationStats(): any {
    const completedTasks = this.taskQueue.filter(
      (task) => task.status === TaskStatus.COMPLETED
    );
    const failedTasks = this.taskQueue.filter(
      (task) => task.status === TaskStatus.FAILED
    );
    const activeSessions = Array.from(
      this.activeCollaborations.values()
    ).filter((session) => session.status === 'active');

    return {
      totalTasks: this.taskQueue.length,
      completedTasks: completedTasks.length,
      failedTasks: failedTasks.length,
      activeSessions: activeSessions.length,
      successRate:
        this.taskQueue.length > 0
          ? completedTasks.length / this.taskQueue.length
          : 0,
      averageConfidence:
        completedTasks.length > 0
          ? completedTasks.reduce(
              (sum, task) => sum + (task.result?.confidence || 0),
              0
            ) / completedTasks.length
          : 0,
    };
  }

  /**
   * 关闭协作框架
   */
  async shutdown(): Promise<void> {
    this.log('info', '智能体协作框架正在关闭...');

    // 取消所有活跃的协作会话
    for (const [sessionId, session] of this.activeCollaborations) {
      if (session.status === 'active') {
        session.status = 'cancelled';
        session.endTime = new Date();
        this.emit('collaboration_cancelled', { session });
      }
    }

    // 清理资源
    this.agents.clear();
    this.agentInstances.clear();
    this.taskQueue.length = 0;
    this.activeCollaborations.clear();
    this.removeAllListeners();
    this.isInitialized = false;

    this.log('info', '智能体协作框架已关闭');
  }

  /**
   * 日志记录
   */
  private log(
    level: 'info' | 'warn' | 'error',
    message: string,
    data?: any
  ): void {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [AgentCollaborationFramework] [${level.toUpperCase()}] ${message}`;

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

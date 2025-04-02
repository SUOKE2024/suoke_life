/**
 * 认知辅助服务
 * 为认知障碍用户提供辅助功能
 */
import { CognitiveAssistanceConfig } from '../types/accessibility';
import { logger } from '../utils/logger';
import visualImpairedService from './visual-impaired-service';

class CognitiveAssistance {
  private config: CognitiveAssistanceConfig = {
    enabled: true,
    simplificationLevel: 3,
    taskBreakdown: true,
    useGraphicalCues: true,
    repeatInstructions: true,
    textSimplificationLevel: 3
  };
  
  // 当前任务状态
  private currentTask: TaskInfo | null = null;
  // 提醒计时器ID
  private reminderTimerId: NodeJS.Timeout | null = null;
  // 上下文记忆
  private contextMemory: Map<string, any> = new Map();
  
  /**
   * 构造函数
   */
  constructor() {
    logger.info('认知辅助服务初始化');
  }
  
  /**
   * 配置认知辅助
   * @param config 认知辅助配置
   */
  public configure(config: Partial<CognitiveAssistanceConfig>): void {
    this.config = {
      ...this.config,
      ...config
    };
    logger.info('认知辅助配置已更新', this.config);
  }
  
  /**
   * 简化文本
   * @param text 原始文本
   * @param level 简化级别(可选，默认使用配置值)
   * @returns 简化后的文本
   */
  public simplifyText(text: string, level?: number): string {
    if (!this.config.enabled) {
      return text;
    }
    
    const simplificationLevel = level ?? this.config.textSimplificationLevel;
    logger.info(`简化文本，级别: ${simplificationLevel}`, { textLength: text.length });
    
    // 根据简化级别处理文本
    switch (simplificationLevel) {
      case 1: // 轻度简化
        return this.lightSimplification(text);
      case 2: // 中度简化
        return this.moderateSimplification(text);
      case 3: // 较高简化
        return this.highSimplification(text);
      case 4: // 高度简化
        return this.veryHighSimplification(text);
      case 5: // 最高简化
        return this.maximumSimplification(text);
      default:
        return this.moderateSimplification(text);
    }
  }
  
  /**
   * 轻度文本简化
   * @param text 原始文本
   * @returns 简化后的文本
   */
  private lightSimplification(text: string): string {
    // 轻度简化：保留大部分内容，主要简化长句和复杂词汇
    return text
      .replace(/，/g, '，\n') // 在逗号后添加换行
      .replace(/；/g, '；\n') // 在分号后添加换行
      .replace(/。/g, '。\n\n'); // 在句号后添加双换行
  }
  
  /**
   * 中度文本简化
   * @param text 原始文本
   * @returns 简化后的文本
   */
  private moderateSimplification(text: string): string {
    // 中度简化：简化句子结构，拆分长句
    let simplified = this.lightSimplification(text);
    
    // 将长句分割成短句
    simplified = simplified
      .replace(/(\S{20,})(，|。|；|！|？)/g, '$1\n$2')
      .replace(/(\S{30,})/g, '$1\n');
      
    return simplified;
  }
  
  /**
   * 较高文本简化
   * @param text 原始文本
   * @returns 简化后的文本
   */
  private highSimplification(text: string): string {
    // 较高简化：进一步简化，移除修饰性内容
    let simplified = this.moderateSimplification(text);
    
    // 将长句分割成更短的句子
    simplified = simplified
      .replace(/(\S{15,})(，|。|；|！|？)/g, '$1\n$2')
      .replace(/(\S{25,})/g, '$1\n');
      
    return simplified;
  }
  
  /**
   * 高度文本简化
   * @param text 原始文本
   * @returns 简化后的文本
   */
  private veryHighSimplification(text: string): string {
    // 高度简化：只保留核心信息
    let simplified = this.highSimplification(text);
    
    // 将任意长度的内容按更短的长度分割
    simplified = simplified
      .replace(/(\S{10,})(，|。|；|！|？)/g, '$1\n$2')
      .replace(/(\S{20,})/g, '$1\n');
      
    return simplified;
  }
  
  /**
   * 最高文本简化
   * @param text 原始文本
   * @returns 简化后的文本
   */
  private maximumSimplification(text: string): string {
    // 最高简化：极度简化，提取关键词和短语
    let simplified = this.veryHighSimplification(text);
    
    // 任何内容都按极短的长度分割
    simplified = simplified
      .replace(/(\S{8,})(，|。|；|！|？)/g, '$1\n$2')
      .replace(/(\S{15,})/g, '$1\n');
      
    return simplified;
  }
  
  /**
   * 分解任务
   * @param taskName 任务名称
   * @param steps 任务步骤
   * @returns 任务ID
   */
  public breakdownTask(taskName: string, steps: string[]): string {
    if (!this.config.enabled || !this.config.taskBreakdown) {
      return '';
    }
    
    const taskId = `task-${Date.now()}`;
    
    // 简化步骤文本
    const simplifiedSteps = steps.map(step => this.simplifyText(step));
    
    this.currentTask = {
      id: taskId,
      name: taskName,
      steps: simplifiedSteps,
      currentStepIndex: 0,
      completed: false
    };
    
    logger.info(`分解任务: ${taskName}`, {
      taskId,
      stepsCount: simplifiedSteps.length
    });
    
    // 如果启用了重复提醒，设置提醒计时器
    if (this.config.repeatInstructions) {
      this.setupTaskReminder();
    }
    
    return taskId;
  }
  
  /**
   * 设置任务提醒
   */
  private setupTaskReminder(): void {
    // 清除现有计时器
    if (this.reminderTimerId) {
      clearInterval(this.reminderTimerId);
      this.reminderTimerId = null;
    }
    
    // 设置新计时器，每30秒提醒一次当前步骤
    this.reminderTimerId = setInterval(() => {
      this.remindCurrentStep();
    }, 30000);
  }
  
  /**
   * 提醒当前步骤
   */
  private remindCurrentStep(): void {
    if (!this.currentTask || this.currentTask.completed) {
      return;
    }
    
    const currentStep = this.currentTask.steps[this.currentTask.currentStepIndex];
    const stepNumber = this.currentTask.currentStepIndex + 1;
    const totalSteps = this.currentTask.steps.length;
    
    const reminderText = `请继续完成"${this.currentTask.name}"的第${stepNumber}步(共${totalSteps}步): ${currentStep}`;
    
    // 使用语音服务提醒
    visualImpairedService.speak(reminderText, false, 4);
    
    logger.info(`提醒当前步骤`, { 
      taskName: this.currentTask.name,
      stepNumber,
      totalSteps 
    });
  }
  
  /**
   * 进入下一个任务步骤
   * @returns 是否成功进入下一步
   */
  public nextTaskStep(): boolean {
    if (!this.currentTask || this.currentTask.completed) {
      return false;
    }
    
    const nextIndex = this.currentTask.currentStepIndex + 1;
    
    // 检查是否已经是最后一步
    if (nextIndex >= this.currentTask.steps.length) {
      this.completeTask();
      return true;
    }
    
    this.currentTask.currentStepIndex = nextIndex;
    const currentStep = this.currentTask.steps[nextIndex];
    const stepNumber = nextIndex + 1;
    const totalSteps = this.currentTask.steps.length;
    
    // 通知当前步骤
    const stepText = `第${stepNumber}步(共${totalSteps}步): ${currentStep}`;
    visualImpairedService.speak(stepText);
    
    logger.info(`进入下一个任务步骤`, {
      taskName: this.currentTask.name,
      stepNumber,
      totalSteps
    });
    
    return true;
  }
  
  /**
   * 完成当前任务
   */
  private completeTask(): void {
    if (!this.currentTask) {
      return;
    }
    
    this.currentTask.completed = true;
    
    // 清除提醒计时器
    if (this.reminderTimerId) {
      clearInterval(this.reminderTimerId);
      this.reminderTimerId = null;
    }
    
    // 通知任务完成
    const completionText = `恭喜! 您已完成"${this.currentTask.name}"的所有步骤。`;
    visualImpairedService.speak(completionText);
    
    logger.info(`完成任务`, { taskName: this.currentTask.name });
  }
  
  /**
   * 获取当前任务信息
   * @returns 当前任务信息或null
   */
  public getCurrentTask(): TaskInfo | null {
    return this.currentTask;
  }
  
  /**
   * 跳转到特定任务步骤
   * @param stepIndex 步骤索引
   * @returns 是否成功跳转
   */
  public jumpToTaskStep(stepIndex: number): boolean {
    if (!this.currentTask || stepIndex < 0 || stepIndex >= this.currentTask.steps.length) {
      return false;
    }
    
    this.currentTask.currentStepIndex = stepIndex;
    const currentStep = this.currentTask.steps[stepIndex];
    const stepNumber = stepIndex + 1;
    const totalSteps = this.currentTask.steps.length;
    
    // 通知当前步骤
    const stepText = `第${stepNumber}步(共${totalSteps}步): ${currentStep}`;
    visualImpairedService.speak(stepText);
    
    logger.info(`跳转到任务步骤`, {
      taskName: this.currentTask.name,
      stepNumber,
      totalSteps
    });
    
    return true;
  }
  
  /**
   * 记住上下文信息
   * @param key 键
   * @param value 值
   */
  public rememberContext(key: string, value: any): void {
    this.contextMemory.set(key, value);
    logger.info(`记住上下文信息: ${key}`, { value });
  }
  
  /**
   * 获取上下文信息
   * @param key 键
   * @returns 值或undefined
   */
  public getContextMemory(key: string): any {
    return this.contextMemory.get(key);
  }
  
  /**
   * 清除上下文信息
   * @param key 键，如果为空则清除所有上下文
   */
  public clearContextMemory(key?: string): void {
    if (key) {
      this.contextMemory.delete(key);
      logger.info(`清除特定上下文信息: ${key}`);
    } else {
      this.contextMemory.clear();
      logger.info('清除所有上下文信息');
    }
  }
  
  /**
   * 提供提示信息
   * @param message 提示消息
   * @param repeatCount 重复次数
   * @param interval 重复间隔(毫秒)
   */
  public provideReminder(
    message: string,
    repeatCount: number = 1,
    interval: number = 10000
  ): void {
    if (!this.config.enabled) {
      return;
    }
    
    // 简化提示消息
    const simplifiedMessage = this.simplifyText(message);
    
    // 立即显示一次
    visualImpairedService.speak(simplifiedMessage);
    
    logger.info(`提供提示信息`, {
      message: simplifiedMessage,
      repeatCount,
      interval
    });
    
    // 如果需要重复，设置计时器
    if (repeatCount > 1) {
      let count = 1;
      
      const timerId = setInterval(() => {
        visualImpairedService.speak(simplifiedMessage, false, 3);
        count++;
        
        if (count >= repeatCount) {
          clearInterval(timerId);
        }
      }, interval);
    }
  }
}

/**
 * 任务信息接口
 */
interface TaskInfo {
  id: string;
  name: string;
  steps: string[];
  currentStepIndex: number;
  completed: boolean;
}

export default new CognitiveAssistance();
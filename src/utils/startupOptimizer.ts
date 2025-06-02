// 启动任务接口
export interface StartupTask {
  name: string;
  priority: number;
  dependencies: string[];
  execute: () => Promise<void>;
  timeout?: number;
  critical?: boolean;
}

// 启动优化器类
export class StartupOptimizer {
  private static instance: StartupOptimizer;
  private tasks = new Map<string, StartupTask>();
  private completed = new Set<string>();
  private running = new Set<string>();
  private failed = new Set<string>();
  private metrics = new Map<string, number>();

  private constructor() {}

  static getInstance(): StartupOptimizer {
    if (!StartupOptimizer.instance) {
      StartupOptimizer.instance = new StartupOptimizer();
    }
    return StartupOptimizer.instance;
  }

  // 注册启动任务
  registerTask(task: StartupTask): void {
    this.tasks.set(task.name, task);
  }

  // 执行所有任务
  async executeAll(): Promise<void> {
    const criticalTasks = Array.from(this.tasks.values()).filter(task => task.critical);
    const nonCriticalTasks = Array.from(this.tasks.values()).filter(task => !task.critical);

    // 先执行关键任务
    await this.executeBatch(criticalTasks);

    // 延迟执行非关键任务
    if (nonCriticalTasks.length > 0) {
      setTimeout(() => this.executeBatch(nonCriticalTasks), 100);
    }
  }

  private async executeBatch(tasks: StartupTask[]): Promise<void> {
    for (const task of tasks) {
      if (this.canExecuteTask(task)) {
        try {
          await this.executeTask(task);
        } catch (error) {
          console.error(`Task ${task.name} failed:`, error);
          this.failed.add(task.name);
        }
      }
    }
  }

  private canExecuteTask(task: StartupTask): boolean {
    if (this.completed.has(task.name) || this.running.has(task.name)) {
      return false;
    }
    
    if (task.dependencies.length === 0) {
      return true;
    }
    
    return task.dependencies.every((dep) => this.completed.has(dep));
  }

  private async executeTask(task: StartupTask): Promise<void> {
    this.running.add(task.name);
    try {
      const startTime = Date.now();
      await task.execute();
      const duration = Date.now() - startTime;
      
      this.metrics.set(task.name, duration);
      this.completed.add(task.name);
      this.running.delete(task.name);
      
      console.log(`Task ${task.name} completed in ${duration}ms`);
    } catch (error) {
      this.running.delete(task.name);
      this.failed.add(task.name);
      throw error;
    }
  }

  // 获取执行统计
  getMetrics(): Record<string, number> {
    return Object.fromEntries(this.metrics);
  }

  // 重置状态
  reset(): void {
    this.tasks.clear();
    this.completed.clear();
    this.running.clear();
    this.failed.clear();
    this.metrics.clear();
  }
}

// 导出单例实例
export const startupOptimizer = StartupOptimizer.getInstance();
export default startupOptimizer;
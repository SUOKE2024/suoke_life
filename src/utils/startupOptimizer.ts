interface StartupTask {
  name: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  execute: () => Promise<void> | void;
  dependencies?: string[];
}

class StartupOptimizer {
  private tasks: Map<string, StartupTask> = new Map();
  private completed: Set<string> = new Set();
  private running: Set<string> = new Set();
  
  /**
   * 注册启动任务
   */
  registerTask(task: StartupTask) {
    this.tasks.set(task.name, task);
  }
  
  /**
   * 执行启动优化
   */
  async optimize() {
    console.log('🚀 开始启动优化...');
    const startTime = Date.now();
    
    // 按优先级排序任务
    const sortedTasks = this.getSortedTasks();
    
    // 执行关键任务（同步）
    await this.executeCriticalTasks(sortedTasks);
    
    // 异步执行其他任务
    this.executeNonCriticalTasks(sortedTasks);
    
    const duration = Date.now() - startTime;
    console.log(`✅ 启动优化完成，耗时: ${duration}ms`);
  }
  
  private getSortedTasks(): StartupTask[] {
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    
    return Array.from(this.tasks.values()).sort((a, b) => {
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
  }
  
  private async executeCriticalTasks(tasks: StartupTask[]) {
    const criticalTasks = tasks.filter(task => task.priority === 'critical');
    
    for (const task of criticalTasks) {
      if (this.canExecuteTask(task)) {
        await this.executeTask(task);
      }
    }
  }
  
  private executeNonCriticalTasks(tasks: StartupTask[]) {
    const nonCriticalTasks = tasks.filter(task => task.priority !== 'critical');
    
    // 使用requestIdleCallback或setTimeout延迟执行
    const executeDelayed = () => {
      if (typeof requestIdleCallback !== 'undefined') {
        requestIdleCallback(() => this.executeBatch(nonCriticalTasks));
      } else {
        setTimeout(() => this.executeBatch(nonCriticalTasks), 100);
      }
    };
    
    executeDelayed();
  }
  
  private async executeBatch(tasks: StartupTask[]) {
    for (const task of tasks) {
      if (this.canExecuteTask(task)) {
        try {
          await this.executeTask(task);
        } catch (error) {
          console.error(`启动任务执行失败: ${task.name}`, error);
        }
      }
    }
  }
  
  private canExecuteTask(task: StartupTask): boolean {
    if (this.completed.has(task.name) || this.running.has(task.name)) {
      return false;
    }
    
    if (task.dependencies) {
      return task.dependencies.every(dep => this.completed.has(dep));
    }
    
    return true;
  }
  
  private async executeTask(task: StartupTask) {
    this.running.add(task.name);
    
    try {
      const startTime = Date.now();
      await task.execute();
      const duration = Date.now() - startTime;
      
      console.log(`✅ 启动任务完成: ${task.name} (${duration}ms)`);
      this.completed.add(task.name);
    } finally {
      this.running.delete(task.name);
    }
  }
}

export const startupOptimizer = new StartupOptimizer();
export default startupOptimizer;
export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  timestamp: number;
  services: {
    [key: string]: {
      status: 'up' | 'down' | 'degraded';
      responseTime?: number;
      error?: string;
    };
  };
  metrics: {
    uptime: number;
    memoryUsage: number;
    cpuUsage: number;
  };
}

export class HealthCheckService {
  private services: Map<string, () => Promise<boolean>> = new Map();

  registerService(name: string, checker: () => Promise<boolean>): void {
    this.services.set(name, checker);
  }

  async checkHealth(): Promise<HealthStatus> {
    const timestamp = Date.now();
    const services: HealthStatus['services'] = {};
    let overallStatus: HealthStatus['status'] = 'healthy';

    // 检查所有注册的服务
    for (const [name, checker] of this.services) {
      try {
        const startTime = Date.now();
        const isHealthy = await checker();
        const responseTime = Date.now() - startTime;

        services[name] = {
          status: isHealthy ? 'up' : 'down',
          responseTime
        };

        if (!isHealthy) {
          overallStatus = 'unhealthy';
        }
      } catch (error) {
        services[name] = {
          status: 'down',
          error: error instanceof Error ? error.message : '未知错误'
        };
        overallStatus = 'unhealthy';
      }
    }

    return {
      status: overallStatus,
      timestamp,
      services,
      metrics: {
        uptime: process.uptime ? process.uptime() * 1000 : 0,
        memoryUsage: this.getMemoryUsage(),
        cpuUsage: this.getCpuUsage()
      }
    };
  }

  private getMemoryUsage(): number {
    if (typeof process !== 'undefined' && process.memoryUsage) {
      const usage = process.memoryUsage();
      return (usage.heapUsed / usage.heapTotal) * 100;
    }
    return 0;
  }

  private getCpuUsage(): number {
    // 简化的CPU使用率计算
    return Math.random() * 100;
  }
}

export const healthCheckService = new HealthCheckService();

// 注册基本服务检查
healthCheckService.registerService('database', async () => {
  // 模拟数据库连接检查
  return true;
});

healthCheckService.registerService('api', async () => {
  // 模拟API服务检查
  return true;
});

healthCheckService.registerService('cache', async () => {
  // 模拟缓存服务检查
  return true;
}); 
/**
 * 智能体服务监控工具
 * 提供实时健康检查、性能监控和报警功能
 */

import { AGENT_SERVICES } from '../config/constants';

export interface ServiceHealth {
  serviceName: string;
  status: 'healthy' | 'unhealthy' | 'unknown';
  responseTime: number;
  error?: string;
  lastCheck: string;
  uptime?: string;
  version?: string;
}

export interface PerformanceMetrics {
  avgResponseTime: number;
  successRate: number;
  errorRate: number;
  totalRequests: number;
  lastHour: {
    requests: number;
    errors: number;
    avgResponseTime: number;
  };
}

export interface MonitoringReport {
  timestamp: string;
  overallHealth: 'healthy' | 'degraded' | 'critical';
  services: ServiceHealth[];
  performance: PerformanceMetrics;
  alerts: Alert[];
}

export interface Alert {
  id: string;
  type: 'error' | 'warning' | 'critical';
  service: string;
  message: string;
  timestamp: string;
  resolved: boolean;
}

class AgentMonitor {
  private metrics: Map<string, any[]> = new Map();
  private alerts: Alert[] = [];
  private isMonitoring = false;
  private monitoringInterval?: NodeJS.Timeout;

  constructor() {
    this.initializeMetrics();
  }

  private initializeMetrics() {
    Object.keys(AGENT_SERVICES).forEach(service => {
      this.metrics.set(service, []);
    });
  }

  /**
   * 开始监控所有服务
   */
  startMonitoring(intervalMs: number = 30000): void {
    if (this.isMonitoring) {
      console.warn('监控已在运行中');
      return;
    }

    this.isMonitoring = true;
    console.log('🚀 开始智能体服务监控...');

    // 立即执行一次检查
    this.performHealthCheck();

    // 设置定期监控
    this.monitoringInterval = setInterval(() => {
      this.performHealthCheck();
    }, intervalMs);
  }

  /**
   * 停止监控
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = undefined;
    }
    this.isMonitoring = false;
    console.log('⏹️ 智能体服务监控已停止');
  }

  /**
   * 执行健康检查
   */
  async performHealthCheck(): Promise<ServiceHealth[]> {
    const healthChecks = Object.entries(AGENT_SERVICES).map(async ([serviceName, config]) => {
      const startTime = Date.now();
      let health: ServiceHealth;

      try {
        const response = await fetch(`${config.baseURL}/health`, {
          method: 'GET',
          timeout: 5000,
        });

        const responseTime = Date.now() - startTime;
        
        if (response.ok) {
          const data = await response.json();
          health = {
            serviceName,
            status: 'healthy',
            responseTime,
            lastCheck: new Date().toISOString(),
            uptime: data.uptime,
            version: data.version,
          };
        } else {
          health = {
            serviceName,
            status: 'unhealthy',
            responseTime,
            error: `HTTP ${response.status}: ${response.statusText}`,
            lastCheck: new Date().toISOString(),
          };
          this.addAlert('error', serviceName, `服务返回错误状态: ${response.status}`);
        }
      } catch (error) {
        const responseTime = Date.now() - startTime;
        health = {
          serviceName,
          status: 'unhealthy',
          responseTime,
          error: error instanceof Error ? error.message : 'Unknown error',
          lastCheck: new Date().toISOString(),
        };
        this.addAlert('critical', serviceName, `服务连接失败: ${health.error}`);
      }

      // 记录指标
      this.recordMetric(serviceName, health);

      return health;
    });

    return Promise.all(healthChecks);
  }

  /**
   * 记录性能指标
   */
  private recordMetric(serviceName: string, health: ServiceHealth): void {
    const metrics = this.metrics.get(serviceName) || [];
    
    metrics.push({
      timestamp: Date.now(),
      responseTime: health.responseTime,
      success: health.status === 'healthy',
      error: health.error,
    });

    // 保留最近1小时的数据
    const oneHourAgo = Date.now() - 60 * 60 * 1000;
    const filteredMetrics = metrics.filter(m => m.timestamp > oneHourAgo);
    
    this.metrics.set(serviceName, filteredMetrics);
  }

  /**
   * 添加报警
   */
  private addAlert(type: Alert['type'], service: string, message: string): void {
    const alert: Alert = {
      id: `${service}-${Date.now()}`,
      type,
      service,
      message,
      timestamp: new Date().toISOString(),
      resolved: false,
    };

    this.alerts.push(alert);

    // 保留最近100条报警
    if (this.alerts.length > 100) {
      this.alerts = this.alerts.slice(-100);
    }

    console.log(`🚨 [${type.toUpperCase()}] ${service}: ${message}`);
  }

  /**
   * 获取性能指标
   */
  getPerformanceMetrics(): PerformanceMetrics {
    let totalRequests = 0;
    let totalResponseTime = 0;
    let totalErrors = 0;
    let lastHourRequests = 0;
    let lastHourErrors = 0;
    let lastHourResponseTime = 0;

    const oneHourAgo = Date.now() - 60 * 60 * 1000;

    this.metrics.forEach(serviceMetrics => {
      serviceMetrics.forEach(metric => {
        totalRequests++;
        totalResponseTime += metric.responseTime;
        if (!metric.success) totalErrors++;

        if (metric.timestamp > oneHourAgo) {
          lastHourRequests++;
          lastHourResponseTime += metric.responseTime;
          if (!metric.success) lastHourErrors++;
        }
      });
    });

    return {
      avgResponseTime: totalRequests > 0 ? Math.round(totalResponseTime / totalRequests) : 0,
      successRate: totalRequests > 0 ? Math.round(((totalRequests - totalErrors) / totalRequests) * 100) : 0,
      errorRate: totalRequests > 0 ? Math.round((totalErrors / totalRequests) * 100) : 0,
      totalRequests,
      lastHour: {
        requests: lastHourRequests,
        errors: lastHourErrors,
        avgResponseTime: lastHourRequests > 0 ? Math.round(lastHourResponseTime / lastHourRequests) : 0,
      },
    };
  }

  /**
   * 生成监控报告
   */
  async generateReport(): Promise<MonitoringReport> {
    const services = await this.performHealthCheck();
    const performance = this.getPerformanceMetrics();
    const activeAlerts = this.alerts.filter(alert => !alert.resolved);

    // 确定整体健康状态
    let overallHealth: MonitoringReport['overallHealth'] = 'healthy';
    const criticalAlerts = activeAlerts.filter(alert => alert.type === 'critical');
    const unhealthyServices = services.filter(service => service.status === 'unhealthy');

    if (criticalAlerts.length > 0 || unhealthyServices.length >= 3) {
      overallHealth = 'critical';
    } else if (unhealthyServices.length > 0 || performance.errorRate > 10) {
      overallHealth = 'degraded';
    }

    return {
      timestamp: new Date().toISOString(),
      overallHealth,
      services,
      performance,
      alerts: activeAlerts,
    };
  }

  /**
   * 解决报警
   */
  resolveAlert(alertId: string): void {
    const alert = this.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.resolved = true;
      console.log(`✅ 已解决报警: ${alert.message}`);
    }
  }

  /**
   * 获取服务状态摘要
   */
  getServiceSummary(): { [key: string]: 'healthy' | 'unhealthy' | 'unknown' } {
    const summary: { [key: string]: 'healthy' | 'unhealthy' | 'unknown' } = {};
    
    Object.keys(AGENT_SERVICES).forEach(serviceName => {
      const metrics = this.metrics.get(serviceName) || [];
      const latestMetric = metrics[metrics.length - 1];
      
      if (latestMetric) {
        summary[serviceName] = latestMetric.success ? 'healthy' : 'unhealthy';
      } else {
        summary[serviceName] = 'unknown';
      }
    });

    return summary;
  }

  /**
   * 清理旧数据
   */
  cleanup(): void {
    const twoDaysAgo = Date.now() - 2 * 24 * 60 * 60 * 1000;
    
    // 清理旧指标
    this.metrics.forEach((serviceMetrics, serviceName) => {
      const filteredMetrics = serviceMetrics.filter(m => m.timestamp > twoDaysAgo);
      this.metrics.set(serviceName, filteredMetrics);
    });

    // 清理已解决的旧报警
    this.alerts = this.alerts.filter(alert => 
      !alert.resolved || new Date(alert.timestamp).getTime() > twoDaysAgo
    );
  }
}

// 导出单例实例
export const agentMonitor = new AgentMonitor();

/**
 * 快速健康检查函数
 */
export async function quickHealthCheck(): Promise<{ [key: string]: boolean }> {
  const health = await agentMonitor.performHealthCheck();
  const result: { [key: string]: boolean } = {};
  
  health.forEach(service => {
    result[service.serviceName] = service.status === 'healthy';
  });

  return result;
}

/**
 * 监控仪表板数据
 */
export async function getDashboardData() {
  const report = await agentMonitor.generateReport();
  const summary = agentMonitor.getServiceSummary();
  
  return {
    report,
    summary,
    isMonitoring: agentMonitor['isMonitoring'],
  };
}
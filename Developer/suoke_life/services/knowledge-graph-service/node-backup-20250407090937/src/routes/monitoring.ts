import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { getPerformanceMonitor, monitoringUtils } from '../infrastructure/monitoring';
import logger from '../infrastructure/logger';

interface TimeRangeQuery {
  startDate?: string;
  endDate?: string;
}

interface QueryIdParams {
  queryId: string;
}

export async function monitoringRoutes(fastify: FastifyInstance) {
  // 获取查询性能报告
  fastify.get<{
    Params: QueryIdParams;
    Querystring: TimeRangeQuery;
  }>('/reports/:queryId', async (request, reply) => {
    try {
      const { queryId } = request.params;
      const { startDate, endDate } = request.query;

      let timeRange;
      if (startDate && endDate) {
        timeRange = {
          start: new Date(startDate),
          end: new Date(endDate)
        };
      }

      const report = await monitoringUtils.generatePerformanceReport(queryId, timeRange);
      return report;
    } catch (error) {
      logger.error('获取性能报告失败:', error);
      reply.status(500).send({
        error: '获取性能报告失败',
        message: error.message
      });
    }
  });

  // 获取实时性能指标
  fastify.get('/metrics/live', async (request, reply) => {
    try {
      const monitor = getPerformanceMonitor();
      const metrics = {
        timestamp: new Date(),
        activeQueries: monitor.getActiveQueries(),
        systemMetrics: {
          memory: process.memoryUsage(),
          cpu: process.cpuUsage()
        }
      };
      return metrics;
    } catch (error) {
      logger.error('获取实时指标失败:', error);
      reply.status(500).send({
        error: '获取实时指标失败',
        message: error.message
      });
    }
  });

  // 获取性能趋势分析
  fastify.get<{
    Params: QueryIdParams;
    Querystring: TimeRangeQuery;
  }>('/trends/:queryId', async (request, reply) => {
    try {
      const { queryId } = request.params;
      const { startDate, endDate } = request.query;

      if (!startDate || !endDate) {
        reply.status(400).send({
          error: '参数错误',
          message: '必须提供开始和结束时间'
        });
        return;
      }

      const monitor = getPerformanceMonitor();
      const trends = monitor.getPerformanceTrends(queryId, {
        start: new Date(startDate),
        end: new Date(endDate)
      });

      return trends;
    } catch (error) {
      logger.error('获取性能趋势失败:', error);
      reply.status(500).send({
        error: '获取性能趋势失败',
        message: error.message
      });
    }
  });

  // 获取告警历史
  fastify.get('/alerts', async (request, reply) => {
    try {
      const monitor = getPerformanceMonitor();
      const alerts = monitor.getAlertHistory();
      return alerts;
    } catch (error) {
      logger.error('获取告警历史失败:', error);
      reply.status(500).send({
        error: '获取告警历史失败',
        message: error.message
      });
    }
  });

  // 更新监控配置
  fastify.put('/config', async (request, reply) => {
    try {
      const monitor = getPerformanceMonitor();
      const config = request.body as any;
      
      // 更新监控配置
      monitor.updateConfig(config);
      
      return { success: true, message: '监控配置已更新' };
    } catch (error) {
      logger.error('更新监控配置失败:', error);
      reply.status(500).send({
        error: '更新监控配置失败',
        message: error.message
      });
    }
  });

  // 健康检查端点
  fastify.get('/health', async () => {
    const monitor = getPerformanceMonitor();
    return {
      status: 'ok',
      timestamp: new Date(),
      metrics: {
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        monitorStatus: monitor.getStatus()
      }
    };
  });
}
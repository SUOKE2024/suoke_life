import { Router, Request, Response } from 'express';
import mongoose from 'mongoose';
import Redis from 'ioredis';
import os from 'os';
import { getConnectionStatus } from '../database';
import logger from '../utils/logger';

const healthRouter = Router();

/**
 * 系统组件状态接口
 */
interface ComponentStatus {
  status: 'UP' | 'DOWN' | 'DEGRADED';
  details?: Record<string, any>;
}

/**
 * 健康检查响应接口
 */
interface HealthResponse {
  status: 'UP' | 'DOWN' | 'DEGRADED';
  timestamp: string;
  service: string;
  version: string;
  environment: string;
  components: Record<string, ComponentStatus>;
}

/**
 * 获取 Redis 连接状态
 * @param redisClient Redis 客户端实例
 * @returns Redis 连接状态
 */
const getRedisStatus = async (redisClient: Redis | null): Promise<ComponentStatus> => {
  if (!redisClient) {
    return { status: 'DOWN', details: { message: 'Redis客户端未初始化' } };
  }

  try {
    // 执行 PING 命令检查连接状态
    const pingResult = await redisClient.ping();
    
    return {
      status: pingResult === 'PONG' ? 'UP' : 'DEGRADED',
      details: {
        ping: pingResult,
        connected: redisClient.status === 'ready'
      }
    };
  } catch (error) {
    logger.error('Redis健康检查失败:', error);
    return {
      status: 'DOWN',
      details: {
        message: '无法连接到Redis服务器',
        error: error instanceof Error ? error.message : String(error)
      }
    };
  }
};

/**
 * 获取 MongoDB 连接状态
 * @returns MongoDB 连接状态
 */
const getMongoStatus = (): ComponentStatus => {
  try {
    const { state, readyState } = getConnectionStatus();
    
    return {
      status: readyState === 1 ? 'UP' : readyState === 2 ? 'DEGRADED' : 'DOWN',
      details: {
        state,
        readyState,
        isConnected: mongoose.connection.readyState === 1
      }
    };
  } catch (error) {
    logger.error('MongoDB健康检查失败:', error);
    return {
      status: 'DOWN',
      details: {
        message: '无法检查MongoDB连接状态',
        error: error instanceof Error ? error.message : String(error)
      }
    };
  }
};

/**
 * 获取系统资源状态
 * @returns 系统资源状态
 */
const getSystemStatus = (): ComponentStatus => {
  try {
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;
    const memUsagePercent = (usedMem / totalMem) * 100;
    
    // CPU 负载
    const loadAvg = os.loadavg();
    const cpuCount = os.cpus().length;
    const loadPercent = (loadAvg[0] / cpuCount) * 100;
    
    // 存储空间 (这里简化处理，实际应该检查应用相关目录)
    const diskSpace = { available: true };
    
    // 内存或CPU超过阈值时降级
    const status = 
      memUsagePercent > 90 || loadPercent > 90 
        ? 'DEGRADED' 
        : 'UP';
    
    return {
      status,
      details: {
        memory: {
          total: Math.round(totalMem / (1024 * 1024)) + 'MB',
          free: Math.round(freeMem / (1024 * 1024)) + 'MB',
          used: Math.round(usedMem / (1024 * 1024)) + 'MB',
          usagePercent: memUsagePercent.toFixed(2) + '%'
        },
        cpu: {
          count: cpuCount,
          loadAverage: loadAvg,
          loadPercent: loadPercent.toFixed(2) + '%'
        },
        uptime: Math.floor(os.uptime() / 60) + ' minutes',
        hostname: os.hostname(),
        platform: os.platform(),
        diskSpace
      }
    };
  } catch (error) {
    logger.error('系统资源健康检查失败:', error);
    return {
      status: 'DEGRADED',
      details: {
        message: '无法检查系统资源状态',
        error: error instanceof Error ? error.message : String(error)
      }
    };
  }
};

/**
 * 主健康检查函数
 * @param req Express请求对象
 * @param res Express响应对象
 * @param redisClient Redis客户端
 * @param includeDetails 是否包含详细信息
 */
const healthCheck = async (
  req: Request, 
  res: Response,
  redisClient: Redis | null,
  includeDetails = true
): Promise<void> => {
  try {
    // 检查各组件状态
    const mongoStatus = getMongoStatus();
    const redisStatus = await getRedisStatus(redisClient);
    const systemStatus = getSystemStatus();
    
    // 确定整体状态
    let overallStatus: 'UP' | 'DOWN' | 'DEGRADED' = 'UP';
    
    if (mongoStatus.status === 'DOWN' || redisStatus.status === 'DOWN') {
      overallStatus = 'DOWN';
    } else if (mongoStatus.status === 'DEGRADED' || redisStatus.status === 'DEGRADED' || systemStatus.status === 'DEGRADED') {
      overallStatus = 'DEGRADED';
    }
    
    // 构建响应
    const response: HealthResponse = {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      service: process.env.SERVICE_NAME || 'laoke-service',
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.NODE_ENV || 'development',
      components: {
        mongodb: mongoStatus,
        redis: redisStatus,
        system: systemStatus
      }
    };
    
    // 如果不需要详细信息，则移除
    if (!includeDetails) {
      for (const component in response.components) {
        if (response.components[component].details) {
          delete response.components[component].details;
        }
      }
    }
    
    // 设置适当的HTTP状态码
    let statusCode = 200;
    if (overallStatus === 'DOWN') {
      statusCode = 503; // Service Unavailable
    } else if (overallStatus === 'DEGRADED') {
      statusCode = 207; // Multi-Status
    }
    
    res.status(statusCode).json(response);
  } catch (error) {
    logger.error('健康检查执行失败:', error);
    res.status(500).json({
      status: 'DOWN',
      timestamp: new Date().toISOString(),
      service: process.env.SERVICE_NAME || 'laoke-service',
      error: error instanceof Error ? error.message : String(error)
    });
  }
};

/**
 * 设置健康检查路由
 * @param redisClient Redis客户端
 * @returns 健康检查路由
 */
export const setupHealthRoutes = (redisClient: Redis | null): Router => {
  // 存活检查 - 最基本的检查，只确认服务正在运行
  healthRouter.get('/live', (req: Request, res: Response) => {
    res.status(200).json({
      status: 'UP',
      timestamp: new Date().toISOString()
    });
  });
  
  // 就绪检查 - 确认服务可以接受流量
  healthRouter.get('/ready', async (req: Request, res: Response) => {
    await healthCheck(req, res, redisClient, false);
  });
  
  // 完整健康检查 - 包含所有组件的详细信息
  healthRouter.get('/', async (req: Request, res: Response) => {
    await healthCheck(req, res, redisClient, true);
  });
  
  // 启动检查 - 用于k8s启动探针
  healthRouter.get('/startup', (req: Request, res: Response) => {
    res.status(200).json({
      status: 'STARTED',
      timestamp: new Date().toISOString()
    });
  });
  
  return healthRouter;
};

export default setupHealthRoutes; 
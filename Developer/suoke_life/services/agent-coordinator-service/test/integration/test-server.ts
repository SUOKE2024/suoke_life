import express from 'express';
import { json, urlencoded } from 'express';
import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import morgan from 'morgan';
import { agentRoutes } from '../../src/routes/agent-routes';
import { knowledgeRoutes } from '../../src/routes/knowledge-routes';
import { coordinationRoutes } from '../../src/routes/coordination-routes';
import { errorHandler } from '../../src/middleware/error-middleware';

/**
 * 配置Express应用程序用于测试
 * @returns Express应用实例
 */
export function createTestServer() {
  const app = express();
  
  // 基本的中间件配置
  app.use(json());
  app.use(urlencoded({ extended: true }));
  
  // 根据测试需要是否启用安全相关中间件
  if (process.env.ENABLE_SECURITY_MIDDLEWARE === 'true') {
    // 安全相关中间件
    app.use(helmet());
    app.use(cors());
    
    // 速率限制（测试环境中限制更宽松）
    const limiter = rateLimit({
      windowMs: 1 * 60 * 1000, // 1分钟
      max: 100, // 每分钟最多100个请求
      standardHeaders: true,
      legacyHeaders: false,
    });
    app.use(limiter);
  }
  
  // 日志中间件 - 在测试模式下只有在DEBUG=true时才启用
  if (process.env.DEBUG === 'true') {
    app.use(morgan('dev'));
  }
  
  // 健康检查端点
  app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
  });
  
  // API路由
  app.use('/api/agents', agentRoutes);
  app.use('/api/knowledge', knowledgeRoutes);
  app.use('/api/coordination', coordinationRoutes);
  
  // 处理404错误
  app.use((req, res) => {
    res.status(404).json({
      success: false,
      message: `路径 ${req.path} 不存在`
    });
  });
  
  // 错误处理中间件
  app.use(errorHandler);
  
  return app;
}

/**
 * 启动测试服务器
 * @param port 服务器端口
 * @returns HTTP服务器实例
 */
export function startTestServer(port = 0) {
  const app = createTestServer();
  const server = app.listen(port, () => {
    const address = server.address();
    const actualPort = typeof address === 'string' ? port : address?.port;
    console.log(`测试服务器启动在端口 ${actualPort}`);
  });
  return server;
}

/**
 * 关闭服务器及其所有连接
 * @param server HTTP服务器实例
 */
export function stopTestServer(server: any) {
  return new Promise<void>((resolve, reject) => {
    if (!server) {
      resolve();
      return;
    }
    
    server.close((err: Error) => {
      if (err) {
        reject(err);
        return;
      }
      resolve();
    });
  });
}

// 便捷的全局测试服务器对象
export let testServer: any = null;

// 设置全局的beforeAll和afterAll钩子
if (typeof beforeAll !== 'undefined' && typeof afterAll !== 'undefined') {
  beforeAll(() => {
    testServer = startTestServer();
    return new Promise<void>((resolve) => {
      testServer.on('listening', () => {
        resolve();
      });
    });
  });
  
  afterAll(() => {
    return stopTestServer(testServer);
  });
} 
/**
 * 路由定义文件
 */
import { Router } from 'express';
import sessionRoutes from './session-routes';
import agentRoutes from './agent-routes';
import coordinationRoutes from './coordination-routes';
import knowledgeRoutes from './knowledge-routes';
import { authenticateApiKey } from '../middlewares/auth-middleware';
import { loadConfig } from '../utils/config-loader';

const router = Router();
const config = loadConfig();

// API认证中间件
if (config.security.enableApiAuthentication) {
  router.use(authenticateApiKey);
}

// 会话管理路由
router.use('/sessions', sessionRoutes);

// 代理服务路由
router.use('/agents', agentRoutes);

// 协调操作路由
router.use('/coordination', coordinationRoutes);

// 知识服务路由
router.use('/knowledge', knowledgeRoutes);

export default router;
/**
 * 模拟路由 - 用于测试，绕过认证中间件
 */
import { Router } from 'express';
import { SessionController } from '../src/controllers/session-controller';
import { AgentController } from '../src/controllers/agent-controller';
import { CoordinationController } from '../src/controllers/coordination-controller';
import { KnowledgeController } from '../src/controllers/knowledge-controller';
import { validateCreateSession, validateUpdateSession } from '../src/middlewares/validation-middleware';

// 创建路由器
const router = Router();

// 控制器实例
const sessionController = new SessionController();
const agentController = new AgentController();
const coordinationController = new CoordinationController();
const knowledgeController = new KnowledgeController();

// 会话路由
router.post('/sessions', validateCreateSession, sessionController.createSession);
router.get('/sessions/:sessionId', sessionController.getSession);
router.put('/sessions/:sessionId', validateUpdateSession, sessionController.updateSession);
router.delete('/sessions/:sessionId', sessionController.endSession);
router.get('/sessions/:sessionId/messages', sessionController.getSessionMessages);

// 代理路由
router.get('/agents', agentController.listAgents);
router.get('/agents/:agentId', agentController.getAgentDetails);
router.post('/agents/:agentId/query', agentController.queryAgent);
router.get('/agents/:agentId/health', agentController.checkAgentHealth);

// 协调路由
router.post('/coordination/route', coordinationController.routeRequest);
router.post('/coordination/handoff', coordinationController.handoffSession);
router.post('/coordination/analyze', coordinationController.analyzeQuery);
router.get('/coordination/capabilities', coordinationController.getSystemCapabilities);

// 知识路由
router.get('/knowledge/search', knowledgeController.searchKnowledge);
router.get('/knowledge/graph/query', knowledgeController.queryKnowledgeGraph);
router.post('/knowledge/rag/generate', knowledgeController.generateRAGResponse);
router.get('/knowledge/precision-medicine/search', knowledgeController.queryPrecisionMedicine);
router.get('/knowledge/multimodal-health/search', knowledgeController.queryMultimodalHealth);
router.get('/knowledge/environmental-health/search', knowledgeController.queryEnvironmentalHealth);
router.get('/knowledge/mental-health/search', knowledgeController.queryMentalHealth);

export default router; 
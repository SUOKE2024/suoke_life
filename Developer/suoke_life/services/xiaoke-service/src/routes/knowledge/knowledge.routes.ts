/**
 * 知识服务路由
 */
import { Router } from 'express';
import { KnowledgeController } from '../../controllers/knowledge';

/**
 * 创建知识路由
 */
export function createKnowledgeRoutes(knowledgeController: KnowledgeController): Router {
  const router = Router();

  // 健康检查
  router.get('/health', knowledgeController.healthCheck);

  // 知识库路由
  router.post('/search', knowledgeController.searchKnowledge);
  router.get('/items/:id', knowledgeController.getKnowledgeItem);
  router.get('/categories/:category', knowledgeController.getKnowledgeByCategory);
  router.get('/tags/:tag', knowledgeController.getKnowledgeByTag);

  // 知识图谱路由
  router.get('/graph/nodes', knowledgeController.searchGraphNodes);
  router.get('/graph/nodes/:nodeId/relations', knowledgeController.getNodeRelations);
  router.get('/graph/path', knowledgeController.findShortestPath);

  // 知识整合路由
  router.get('/products/:productId/enrich', knowledgeController.enrichProductKnowledge);
  router.post('/agriculture-health', knowledgeController.searchAgricultureHealthKnowledge);
  router.get('/products/:productId/health', knowledgeController.getProductHealthKnowledge);
  router.get('/solar-terms/:solarTerm', knowledgeController.getSolarTermAgricultureKnowledge);

  return router;
}
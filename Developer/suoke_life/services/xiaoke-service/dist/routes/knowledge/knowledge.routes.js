"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createKnowledgeRoutes = createKnowledgeRoutes;
/**
 * 知识服务路由
 */
const express_1 = require("express");
/**
 * 创建知识路由
 */
function createKnowledgeRoutes(knowledgeController) {
    const router = (0, express_1.Router)();
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

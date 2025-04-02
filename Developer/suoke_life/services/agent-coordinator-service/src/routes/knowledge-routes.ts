/**
 * 知识服务路由
 */
import express from 'express';
import { KnowledgeController } from '../controllers/knowledge-controller';
import { authenticate } from '../middlewares/auth';

const router = express.Router();
const knowledgeController = new KnowledgeController();

// 认证中间件
router.use(authenticate);

// 基础知识搜索接口
router.get('/search', async (req, res) => {
  await knowledgeController.searchKnowledge(req, res);
});

// 知识图谱查询接口
router.get('/graph/query', async (req, res) => {
  await knowledgeController.queryKnowledgeGraph(req, res);
});

// RAG服务生成接口
router.post('/rag/generate', async (req, res) => {
  await knowledgeController.generateRAGResponse(req, res);
});

// 精准医学知识查询接口
router.get('/precision-medicine/search', async (req, res) => {
  await knowledgeController.queryPrecisionMedicine(req, res);
});

// 多模态健康数据查询接口
router.get('/multimodal-health/search', async (req, res) => {
  await knowledgeController.queryMultimodalHealth(req, res);
});

// 环境健康数据查询接口
router.get('/environmental-health/search', async (req, res) => {
  await knowledgeController.queryEnvironmentalHealth(req, res);
});

// 心理健康数据查询接口
router.get('/mental-health/search', async (req, res) => {
  await knowledgeController.queryMentalHealth(req, res);
});

export default router;
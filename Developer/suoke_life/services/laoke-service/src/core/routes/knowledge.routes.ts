import express from 'express';
import { authenticate } from '../middleware/auth';
import * as knowledgeController from '../../services/knowledge/knowledge.controller';

const router = express.Router();

/**
 * @route GET /api/v1/knowledge
 * @desc 获取知识内容列表
 * @access Public
 */
router.get('/', knowledgeController.getKnowledgeList);

/**
 * @route GET /api/v1/knowledge/:id
 * @desc 获取知识内容详情
 * @access Public
 */
router.get('/:id', knowledgeController.getKnowledgeById);

/**
 * @route GET /api/v1/knowledge/recommend
 * @desc 获取推荐知识内容
 * @access Public
 */
router.get('/recommend', knowledgeController.getRecommendedKnowledge);

/**
 * @route GET /api/v1/knowledge/categories
 * @desc 获取知识分类
 * @access Public
 */
router.get('/categories', knowledgeController.getKnowledgeCategories);

/**
 * @route POST /api/v1/knowledge
 * @desc 创建知识内容
 * @access Private
 */
router.post('/', authenticate, knowledgeController.createKnowledge);

/**
 * @route PUT /api/v1/knowledge/:id
 * @desc 更新知识内容
 * @access Private
 */
router.put('/:id', authenticate, knowledgeController.updateKnowledge);

/**
 * @route DELETE /api/v1/knowledge/:id
 * @desc 删除知识内容
 * @access Private
 */
router.delete('/:id', authenticate, knowledgeController.deleteKnowledge);

/**
 * @route GET /api/v1/knowledge/search
 * @desc 搜索知识内容
 * @access Public
 */
router.get('/search', knowledgeController.searchKnowledge);

/**
 * @route POST /api/v1/knowledge/:id/rating
 * @desc 为知识内容评分
 * @access Private
 */
router.post('/:id/rating', authenticate, knowledgeController.rateKnowledge);

/**
 * @route GET /api/v1/knowledge/trending
 * @desc 获取热门知识内容
 * @access Public
 */
router.get('/trending', knowledgeController.getTrendingKnowledge);

export default router; 
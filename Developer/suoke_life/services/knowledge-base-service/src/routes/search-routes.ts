/**
 * 知识搜索路由
 * 定义知识搜索相关的API路由
 */

import { Router } from 'express';
import { SearchController } from '../controllers/search-controller';
import { validateRequest } from '../middlewares/validation';
import { searchKnowledgeSchema } from '../validations/search-validation';

const router = Router();
const searchController = new SearchController();

/**
 * @swagger
 * /api/search:
 *   get:
 *     summary: 搜索知识内容
 *     tags: [知识搜索]
 *     parameters:
 *       - in: query
 *         name: q
 *         schema:
 *           type: string
 *         required: true
 *         description: 搜索关键词
 *       - in: query
 *         name: categories
 *         schema:
 *           type: array
 *           items:
 *             type: string
 *         description: 分类过滤
 *       - in: query
 *         name: tags
 *         schema:
 *           type: array
 *           items:
 *             type: string
 *         description: 标签过滤
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           default: 1
 *         description: 页码
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 20
 *         description: 每页数量
 *     responses:
 *       200:
 *         description: 搜索成功
 */
router.get('/', validateRequest(searchKnowledgeSchema), searchController.searchKnowledge.bind(searchController));

/**
 * @swagger
 * /api/search/semantic:
 *   get:
 *     summary: 语义搜索知识内容
 *     tags: [知识搜索]
 *     parameters:
 *       - in: query
 *         name: q
 *         schema:
 *           type: string
 *         required: true
 *         description: 搜索关键词
 *       - in: query
 *         name: categories
 *         schema:
 *           type: array
 *           items:
 *             type: string
 *         description: 分类过滤
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 20
 *         description: 返回数量
 *       - in: query
 *         name: threshold
 *         schema:
 *           type: number
 *           default: 0.7
 *         description: 相似度阈值(0-1)
 *     responses:
 *       200:
 *         description: 搜索成功
 */
router.get('/semantic', searchController.semanticSearch.bind(searchController));

/**
 * @swagger
 * /api/search/suggest:
 *   get:
 *     summary: 获取搜索建议
 *     tags: [知识搜索]
 *     parameters:
 *       - in: query
 *         name: q
 *         schema:
 *           type: string
 *         required: true
 *         description: 搜索前缀
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 10
 *         description: 返回数量
 *     responses:
 *       200:
 *         description: 获取建议成功
 */
router.get('/suggest', searchController.getSuggestions.bind(searchController));

/**
 * @swagger
 * /api/search/related:
 *   get:
 *     summary: 获取相关知识
 *     tags: [知识搜索]
 *     parameters:
 *       - in: query
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 知识ID
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 5
 *         description: 返回数量
 *     responses:
 *       200:
 *         description: 获取相关知识成功
 */
router.get('/related', searchController.getRelatedKnowledge.bind(searchController));

export default router;
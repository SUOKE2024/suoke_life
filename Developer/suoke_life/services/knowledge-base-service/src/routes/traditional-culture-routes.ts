/**
 * 传统文化知识路由
 * 定义传统文化知识相关的API路由
 */

import { Router } from 'express';
import { TraditionalCultureController } from '../controllers/traditional-culture-controller';
import { validateRequest } from '../middlewares/validation';
import { 
  createTraditionalCultureKnowledgeSchema, 
  updateTraditionalCultureKnowledgeSchema 
} from '../validations/traditional-culture-validation';
import { authenticate } from '../middlewares/auth';
import { checkPermission } from '../middlewares/permission';

const router = Router();
const traditionalCultureController = new TraditionalCultureController();

/**
 * @swagger
 * /api/traditional-culture:
 *   get:
 *     summary: 获取传统文化知识列表
 *     tags: [传统文化知识]
 *     parameters:
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
 *       - in: query
 *         name: category
 *         schema:
 *           type: string
 *         description: 分类ID
 *       - in: query
 *         name: culturalSystem
 *         schema:
 *           type: string
 *           enum: [yijing, taoism, buddhism, physiognomy, fengshui, classics, other]
 *         description: 文化体系
 *       - in: query
 *         name: historicalPeriod
 *         schema:
 *           type: string
 *         description: 历史时期
 *     responses:
 *       200:
 *         description: 成功获取传统文化知识列表
 */
router.get('/', traditionalCultureController.getTraditionalCultureKnowledgeList.bind(traditionalCultureController));

/**
 * @swagger
 * /api/traditional-culture/{id}:
 *   get:
 *     summary: 获取传统文化知识详情
 *     tags: [传统文化知识]
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 知识ID
 *     responses:
 *       200:
 *         description: 成功获取传统文化知识详情
 *       404:
 *         description: 知识不存在
 */
router.get('/:id', traditionalCultureController.getTraditionalCultureKnowledgeById.bind(traditionalCultureController));

/**
 * @swagger
 * /api/traditional-culture:
 *   post:
 *     summary: 创建传统文化知识
 *     tags: [传统文化知识]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - title
 *               - content
 *               - categories
 *               - culturalSystem
 *             properties:
 *               title:
 *                 type: string
 *               content:
 *                 type: string
 *               summary:
 *                 type: string
 *               categories:
 *                 type: array
 *                 items:
 *                   type: string
 *               tags:
 *                 type: array
 *                 items:
 *                   type: string
 *               culturalSystem:
 *                 type: string
 *                 enum: [yijing, taoism, buddhism, physiognomy, fengshui, classics, other]
 *               historicalPeriod:
 *                 type: string
 *               originalText:
 *                 type: string
 *               interpretation:
 *                 type: string
 *     responses:
 *       201:
 *         description: 传统文化知识创建成功
 *       400:
 *         description: 请求参数错误
 */
router.post('/', 
  authenticate, 
  checkPermission('knowledge:create'),
  validateRequest(createTraditionalCultureKnowledgeSchema), 
  traditionalCultureController.createTraditionalCultureKnowledge.bind(traditionalCultureController)
);

/**
 * @swagger
 * /api/traditional-culture/{id}:
 *   put:
 *     summary: 更新传统文化知识
 *     tags: [传统文化知识]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 知识ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               title:
 *                 type: string
 *               content:
 *                 type: string
 *               summary:
 *                 type: string
 *               categories:
 *                 type: array
 *                 items:
 *                   type: string
 *               tags:
 *                 type: array
 *                 items:
 *                   type: string
 *               culturalSystem:
 *                 type: string
 *                 enum: [yijing, taoism, buddhism, physiognomy, fengshui, classics, other]
 *               historicalPeriod:
 *                 type: string
 *               originalText:
 *                 type: string
 *               interpretation:
 *                 type: string
 *     responses:
 *       200:
 *         description: 传统文化知识更新成功
 *       400:
 *         description: 请求参数错误
 *       404:
 *         description: 知识不存在
 */
router.put('/:id', 
  authenticate, 
  checkPermission('knowledge:update'),
  validateRequest(updateTraditionalCultureKnowledgeSchema), 
  traditionalCultureController.updateTraditionalCultureKnowledge.bind(traditionalCultureController)
);

/**
 * @swagger
 * /api/traditional-culture/{id}:
 *   delete:
 *     summary: 删除传统文化知识
 *     tags: [传统文化知识]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 知识ID
 *     responses:
 *       200:
 *         description: 传统文化知识删除成功
 *       404:
 *         description: 知识不存在
 */
router.delete('/:id', 
  authenticate, 
  checkPermission('knowledge:delete'),
  traditionalCultureController.deleteTraditionalCultureKnowledge.bind(traditionalCultureController)
);

/**
 * @swagger
 * /api/traditional-culture/systems/{culturalSystem}:
 *   get:
 *     summary: 按文化体系获取传统文化知识
 *     tags: [传统文化知识]
 *     parameters:
 *       - in: path
 *         name: culturalSystem
 *         schema:
 *           type: string
 *           enum: [yijing, taoism, buddhism, physiognomy, fengshui, classics, other]
 *         required: true
 *         description: 文化体系
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
 *         description: 成功获取知识列表
 */
router.get('/systems/:culturalSystem', traditionalCultureController.getKnowledgeByCulturalSystem.bind(traditionalCultureController));

/**
 * @swagger
 * /api/traditional-culture/hexagrams:
 *   get:
 *     summary: 获取易经卦象知识
 *     tags: [传统文化知识]
 *     parameters:
 *       - in: query
 *         name: name
 *         schema:
 *           type: string
 *         description: 卦名
 *     responses:
 *       200:
 *         description: 成功获取卦象知识
 */
router.get('/hexagrams', traditionalCultureController.getHexagramKnowledge.bind(traditionalCultureController));

/**
 * @swagger
 * /api/traditional-culture/periods/{historicalPeriod}:
 *   get:
 *     summary: 按历史时期获取传统文化知识
 *     tags: [传统文化知识]
 *     parameters:
 *       - in: path
 *         name: historicalPeriod
 *         schema:
 *           type: string
 *         required: true
 *         description: 历史时期
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
 *         description: 成功获取知识列表
 */
router.get('/periods/:historicalPeriod', traditionalCultureController.getKnowledgeByHistoricalPeriod.bind(traditionalCultureController));

export default router;
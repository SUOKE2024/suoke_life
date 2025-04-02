/**
 * 知识条目路由
 * 定义知识内容相关的API路由
 */

import { Router } from 'express';
import { KnowledgeController } from '../controllers/knowledge-controller';
import { validateRequest } from '../middlewares/validation';
import { 
  createKnowledgeSchema, 
  updateKnowledgeSchema, 
  getKnowledgeListSchema 
} from '../validations/knowledge-validation';
import { authenticate } from '../middlewares/auth';
import { checkPermission } from '../middlewares/permission';

const router = Router();
const knowledgeController = new KnowledgeController();

/**
 * @swagger
 * /api/knowledge:
 *   get:
 *     summary: 获取知识列表
 *     tags: [知识管理]
 *     parameters:
 *       - in: query
 *         name: category
 *         schema:
 *           type: string
 *         description: 按分类筛选
 *       - in: query
 *         name: tag
 *         schema:
 *           type: string
 *         description: 按标签筛选
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
router.get('/', validateRequest(getKnowledgeListSchema), knowledgeController.getKnowledgeList.bind(knowledgeController));

/**
 * @swagger
 * /api/knowledge/{id}:
 *   get:
 *     summary: 获取知识详情
 *     tags: [知识管理]
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 知识ID
 *     responses:
 *       200:
 *         description: 成功获取知识详情
 *       404:
 *         description: 知识不存在
 */
router.get('/:id', knowledgeController.getKnowledgeById.bind(knowledgeController));

/**
 * @swagger
 * /api/knowledge:
 *   post:
 *     summary: 创建知识条目
 *     tags: [知识管理]
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
 *               source:
 *                 type: string
 *               metadata:
 *                 type: object
 *     responses:
 *       201:
 *         description: 知识创建成功
 *       400:
 *         description: 请求参数错误
 */
router.post('/', 
  authenticate, 
  checkPermission('knowledge:create'),
  validateRequest(createKnowledgeSchema), 
  knowledgeController.createKnowledge.bind(knowledgeController)
);

/**
 * @swagger
 * /api/knowledge/{id}:
 *   put:
 *     summary: 更新知识条目
 *     tags: [知识管理]
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
 *               source:
 *                 type: string
 *               metadata:
 *                 type: object
 *     responses:
 *       200:
 *         description: 知识更新成功
 *       400:
 *         description: 请求参数错误
 *       404:
 *         description: 知识不存在
 */
router.put('/:id', 
  authenticate, 
  checkPermission('knowledge:update'),
  validateRequest(updateKnowledgeSchema), 
  knowledgeController.updateKnowledge.bind(knowledgeController)
);

/**
 * @swagger
 * /api/knowledge/{id}:
 *   delete:
 *     summary: 删除知识条目
 *     tags: [知识管理]
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
 *         description: 知识删除成功
 *       404:
 *         description: 知识不存在
 */
router.delete('/:id', 
  authenticate, 
  checkPermission('knowledge:delete'),
  knowledgeController.deleteKnowledge.bind(knowledgeController)
);

/**
 * @swagger
 * /api/knowledge/{id}/versions:
 *   get:
 *     summary: 获取知识版本历史
 *     tags: [知识管理]
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 知识ID
 *     responses:
 *       200:
 *         description: 成功获取版本历史
 *       404:
 *         description: 知识不存在
 */
router.get('/:id/versions', knowledgeController.getKnowledgeVersions.bind(knowledgeController));

/**
 * @swagger
 * /api/knowledge/{id}/publish:
 *   post:
 *     summary: 发布知识
 *     tags: [知识管理]
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
 *         description: 知识发布成功
 *       404:
 *         description: 知识不存在
 */
router.post('/:id/publish', 
  authenticate, 
  checkPermission('knowledge:publish'),
  knowledgeController.publishKnowledge.bind(knowledgeController)
);

/**
 * @swagger
 * /api/knowledge/{id}/unpublish:
 *   post:
 *     summary: 取消发布知识
 *     tags: [知识管理]
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
 *         description: 知识取消发布成功
 *       404:
 *         description: 知识不存在
 */
router.post('/:id/unpublish', 
  authenticate, 
  checkPermission('knowledge:publish'),
  knowledgeController.unpublishKnowledge.bind(knowledgeController)
);

export default router;
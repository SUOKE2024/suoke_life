/**
 * 知识标签路由
 * 定义知识标签相关的API路由
 */

import { Router } from 'express';
import { TagController } from '../controllers/tag-controller';
import { validateRequest } from '../middlewares/validation';
import { createTagSchema, updateTagSchema } from '../validations/tag-validation';
import { authenticate } from '../middlewares/auth';
import { checkPermission } from '../middlewares/permission';

const router = Router();
const tagController = new TagController();

/**
 * @swagger
 * /api/tags:
 *   get:
 *     summary: 获取所有标签
 *     tags: [标签管理]
 *     parameters:
 *       - in: query
 *         name: sort
 *         schema:
 *           type: string
 *           enum: [name, count, createdAt]
 *         description: 排序字段
 *       - in: query
 *         name: order
 *         schema:
 *           type: string
 *           enum: [asc, desc]
 *         description: 排序方式
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 50
 *         description: 返回数量
 *     responses:
 *       200:
 *         description: 成功获取标签列表
 */
router.get('/', tagController.getAllTags.bind(tagController));

/**
 * @swagger
 * /api/tags/{id}:
 *   get:
 *     summary: 获取标签详情
 *     tags: [标签管理]
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 标签ID
 *     responses:
 *       200:
 *         description: 成功获取标签详情
 *       404:
 *         description: 标签不存在
 */
router.get('/:id', tagController.getTagById.bind(tagController));

/**
 * @swagger
 * /api/tags:
 *   post:
 *     summary: 创建标签
 *     tags: [标签管理]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - name
 *             properties:
 *               name:
 *                 type: string
 *               description:
 *                 type: string
 *               color:
 *                 type: string
 *     responses:
 *       201:
 *         description: 标签创建成功
 *       400:
 *         description: 请求参数错误
 */
router.post('/', 
  authenticate, 
  checkPermission('tag:create'),
  validateRequest(createTagSchema), 
  tagController.createTag.bind(tagController)
);

/**
 * @swagger
 * /api/tags/{id}:
 *   put:
 *     summary: 更新标签
 *     tags: [标签管理]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 标签ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               name:
 *                 type: string
 *               description:
 *                 type: string
 *               color:
 *                 type: string
 *     responses:
 *       200:
 *         description: 标签更新成功
 *       400:
 *         description: 请求参数错误
 *       404:
 *         description: 标签不存在
 */
router.put('/:id', 
  authenticate, 
  checkPermission('tag:update'),
  validateRequest(updateTagSchema), 
  tagController.updateTag.bind(tagController)
);

/**
 * @swagger
 * /api/tags/{id}:
 *   delete:
 *     summary: 删除标签
 *     tags: [标签管理]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 标签ID
 *     responses:
 *       200:
 *         description: 标签删除成功
 *       404:
 *         description: 标签不存在
 */
router.delete('/:id', 
  authenticate, 
  checkPermission('tag:delete'),
  tagController.deleteTag.bind(tagController)
);

/**
 * @swagger
 * /api/tags/popular:
 *   get:
 *     summary: 获取热门标签
 *     tags: [标签管理]
 *     parameters:
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 20
 *         description: 返回数量
 *     responses:
 *       200:
 *         description: 成功获取热门标签
 */
router.get('/popular', tagController.getPopularTags.bind(tagController));

export default router;
/**
 * 知识分类路由
 * 定义知识分类相关的API路由
 */

import { Router } from 'express';
import { CategoryController } from '../controllers/category-controller';
import { validateRequest } from '../middlewares/validation';
import { createCategorySchema, updateCategorySchema } from '../validations/category-validation';
import { authenticate } from '../middlewares/auth';
import { checkPermission } from '../middlewares/permission';

const router = Router();
const categoryController = new CategoryController();

/**
 * @swagger
 * /api/categories:
 *   get:
 *     summary: 获取所有分类
 *     tags: [分类管理]
 *     parameters:
 *       - in: query
 *         name: parent
 *         schema:
 *           type: string
 *         description: 父分类ID
 *     responses:
 *       200:
 *         description: 成功获取分类列表
 */
router.get('/', categoryController.getAllCategories.bind(categoryController));

/**
 * @swagger
 * /api/categories/{id}:
 *   get:
 *     summary: 获取分类详情
 *     tags: [分类管理]
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 分类ID
 *     responses:
 *       200:
 *         description: 成功获取分类详情
 *       404:
 *         description: 分类不存在
 */
router.get('/:id', categoryController.getCategoryById.bind(categoryController));

/**
 * @swagger
 * /api/categories:
 *   post:
 *     summary: 创建分类
 *     tags: [分类管理]
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
 *               parentId:
 *                 type: string
 *               icon:
 *                 type: string
 *               color:
 *                 type: string
 *               order:
 *                 type: number
 *     responses:
 *       201:
 *         description: 分类创建成功
 *       400:
 *         description: 请求参数错误
 */
router.post('/', 
  authenticate, 
  checkPermission('category:create'),
  validateRequest(createCategorySchema), 
  categoryController.createCategory.bind(categoryController)
);

/**
 * @swagger
 * /api/categories/{id}:
 *   put:
 *     summary: 更新分类
 *     tags: [分类管理]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 分类ID
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
 *               parentId:
 *                 type: string
 *               icon:
 *                 type: string
 *               color:
 *                 type: string
 *               order:
 *                 type: number
 *     responses:
 *       200:
 *         description: 分类更新成功
 *       400:
 *         description: 请求参数错误
 *       404:
 *         description: 分类不存在
 */
router.put('/:id', 
  authenticate, 
  checkPermission('category:update'),
  validateRequest(updateCategorySchema), 
  categoryController.updateCategory.bind(categoryController)
);

/**
 * @swagger
 * /api/categories/{id}:
 *   delete:
 *     summary: 删除分类
 *     tags: [分类管理]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 分类ID
 *     responses:
 *       200:
 *         description: 分类删除成功
 *       404:
 *         description: 分类不存在
 *       409:
 *         description: 分类下有子分类或关联知识，无法删除
 */
router.delete('/:id', 
  authenticate, 
  checkPermission('category:delete'),
  categoryController.deleteCategory.bind(categoryController)
);

/**
 * @swagger
 * /api/categories/tree:
 *   get:
 *     summary: 获取分类树结构
 *     tags: [分类管理]
 *     responses:
 *       200:
 *         description: 成功获取分类树
 */
router.get('/tree', categoryController.getCategoryTree.bind(categoryController));

export default router;
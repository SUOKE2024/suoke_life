/**
 * 现代医学知识路由
 * 定义现代医学知识相关的API路由
 */

import { Router } from 'express';
import { ModernMedicineController } from '../controllers/modern-medicine-controller';
import { validateRequest } from '../middlewares/validation';
import { 
  createModernMedicineKnowledgeSchema, 
  updateModernMedicineKnowledgeSchema 
} from '../validations/modern-medicine-validation';
import { authenticate } from '../middlewares/auth';
import { checkPermission } from '../middlewares/permission';

const router = Router();
const modernMedicineController = new ModernMedicineController();

/**
 * @swagger
 * /api/modern-medicine:
 *   get:
 *     summary: 获取现代医学知识列表
 *     tags: [现代医学知识]
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
 *         name: medicalSystem
 *         schema:
 *           type: string
 *           enum: [internal, surgery, gynecology, pediatrics, preventive, nutrition, psychology, other]
 *         description: 医学体系
 *       - in: query
 *         name: researchSupport
 *         schema:
 *           type: string
 *           enum: [high, medium, low, unconfirmed]
 *         description: 研究支持程度
 *     responses:
 *       200:
 *         description: 成功获取现代医学知识列表
 */
router.get('/', modernMedicineController.getModernMedicineKnowledgeList.bind(modernMedicineController));

/**
 * @swagger
 * /api/modern-medicine/{id}:
 *   get:
 *     summary: 获取现代医学知识详情
 *     tags: [现代医学知识]
 *     parameters:
 *       - in: path
 *         name: id
 *         schema:
 *           type: string
 *         required: true
 *         description: 知识ID
 *     responses:
 *       200:
 *         description: 成功获取现代医学知识详情
 *       404:
 *         description: 知识不存在
 */
router.get('/:id', modernMedicineController.getModernMedicineKnowledgeById.bind(modernMedicineController));

/**
 * @swagger
 * /api/modern-medicine:
 *   post:
 *     summary: 创建现代医学知识
 *     tags: [现代医学知识]
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
 *               - medicalSystem
 *               - researchSupport
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
 *               medicalSystem:
 *                 type: string
 *                 enum: [internal, surgery, gynecology, pediatrics, preventive, nutrition, psychology, other]
 *               researchSupport:
 *                 type: string
 *                 enum: [high, medium, low, unconfirmed]
 *               references:
 *                 type: array
 *                 items:
 *                   type: string
 *               clinicalTrials:
 *                 type: array
 *                 items:
 *                   type: object
 *                   properties:
 *                     name:
 *                       type: string
 *                     url:
 *                       type: string
 *                     year:
 *                       type: number
 *                     outcome:
 *                       type: string
 *     responses:
 *       201:
 *         description: 现代医学知识创建成功
 *       400:
 *         description: 请求参数错误
 */
router.post('/', 
  authenticate, 
  checkPermission('knowledge:create'),
  validateRequest(createModernMedicineKnowledgeSchema), 
  modernMedicineController.createModernMedicineKnowledge.bind(modernMedicineController)
);

/**
 * @swagger
 * /api/modern-medicine/{id}:
 *   put:
 *     summary: 更新现代医学知识
 *     tags: [现代医学知识]
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
 *               medicalSystem:
 *                 type: string
 *                 enum: [internal, surgery, gynecology, pediatrics, preventive, nutrition, psychology, other]
 *               researchSupport:
 *                 type: string
 *                 enum: [high, medium, low, unconfirmed]
 *               references:
 *                 type: array
 *                 items:
 *                   type: string
 *               clinicalTrials:
 *                 type: array
 *                 items:
 *                   type: object
 *                   properties:
 *                     name:
 *                       type: string
 *                     url:
 *                       type: string
 *                     year:
 *                       type: number
 *                     outcome:
 *                       type: string
 *     responses:
 *       200:
 *         description: 现代医学知识更新成功
 *       400:
 *         description: 请求参数错误
 *       404:
 *         description: 知识不存在
 */
router.put('/:id', 
  authenticate, 
  checkPermission('knowledge:update'),
  validateRequest(updateModernMedicineKnowledgeSchema), 
  modernMedicineController.updateModernMedicineKnowledge.bind(modernMedicineController)
);

/**
 * @swagger
 * /api/modern-medicine/{id}:
 *   delete:
 *     summary: 删除现代医学知识
 *     tags: [现代医学知识]
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
 *         description: 现代医学知识删除成功
 *       404:
 *         description: 知识不存在
 */
router.delete('/:id', 
  authenticate, 
  checkPermission('knowledge:delete'),
  modernMedicineController.deleteModernMedicineKnowledge.bind(modernMedicineController)
);

/**
 * @swagger
 * /api/modern-medicine/systems/{medicalSystem}:
 *   get:
 *     summary: 按医学体系获取现代医学知识
 *     tags: [现代医学知识]
 *     parameters:
 *       - in: path
 *         name: medicalSystem
 *         schema:
 *           type: string
 *           enum: [internal, surgery, gynecology, pediatrics, preventive, nutrition, psychology, other]
 *         required: true
 *         description: 医学体系
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
router.get('/systems/:medicalSystem', modernMedicineController.getKnowledgeByMedicalSystem.bind(modernMedicineController));

/**
 * @swagger
 * /api/modern-medicine/research-support/{level}:
 *   get:
 *     summary: 按研究支持程度获取现代医学知识
 *     tags: [现代医学知识]
 *     parameters:
 *       - in: path
 *         name: level
 *         schema:
 *           type: string
 *           enum: [high, medium, low, unconfirmed]
 *         required: true
 *         description: 研究支持程度
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
router.get('/research-support/:level', modernMedicineController.getKnowledgeByResearchSupport.bind(modernMedicineController));

export default router;
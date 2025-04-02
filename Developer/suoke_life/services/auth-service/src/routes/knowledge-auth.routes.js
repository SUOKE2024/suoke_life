/**
 * 知识库认证路由
 * 用于处理与知识库和知识图谱访问权限相关的请求
 */
const express = require('express');
const router = express.Router();
const { logger } = require('@suoke/shared').utils;
const knowledgeAuthController = require('../controllers/knowledge-auth.controller');
const { verifyToken, verifyAdmin } = require('../middlewares/auth.middleware');
const { validateCsrfToken } = require('../middlewares/csrf.middleware');

/**
 * @swagger
 * tags:
 *   name: 知识库权限
 *   description: 知识库和知识图谱访问权限API
 */

/**
 * @swagger
 * /auth/knowledge/permissions:
 *   get:
 *     summary: 获取当前用户的知识库权限
 *     tags: [知识库权限]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: 成功返回权限列表
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 permissions:
 *                   type: array
 *                   items:
 *                     type: string
 *                   example: ["knowledge:read", "graph:read"]
 *       401:
 *         description: 未授权
 */
router.get('/permissions', verifyToken, knowledgeAuthController.getCurrentUserPermissions);

/**
 * @swagger
 * /auth/knowledge/check-access:
 *   post:
 *     summary: 检查对特定资源的访问权限
 *     tags: [知识库权限]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - resourceType
 *               - resourceId
 *               - action
 *             properties:
 *               resourceType:
 *                 type: string
 *                 description: 资源类型
 *                 example: knowledge_base
 *               resourceId:
 *                 type: string
 *                 description: 资源ID
 *                 example: kb-123456
 *               action:
 *                 type: string
 *                 description: 操作类型
 *                 example: read
 *     responses:
 *       200:
 *         description: 权限检查结果
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 hasAccess:
 *                   type: boolean
 *                   example: true
 *       401:
 *         description: 未授权
 */
router.post('/check-access', verifyToken, knowledgeAuthController.checkAccess);

/**
 * @swagger
 * /auth/knowledge/batch-check-access:
 *   post:
 *     summary: 批量检查多个资源的访问权限
 *     tags: [知识库权限]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - resources
 *             properties:
 *               resources:
 *                 type: array
 *                 items:
 *                   type: object
 *                   required:
 *                     - resourceType
 *                     - resourceId
 *                     - action
 *                   properties:
 *                     resourceType:
 *                       type: string
 *                       description: 资源类型
 *                       example: knowledge_base
 *                     resourceId:
 *                       type: string
 *                       description: 资源ID
 *                       example: kb-123456
 *                     action:
 *                       type: string
 *                       description: 操作类型
 *                       example: read
 *     responses:
 *       200:
 *         description: 批量权限检查结果
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 results:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       resourceType:
 *                         type: string
 *                         example: knowledge_base
 *                       resourceId:
 *                         type: string
 *                         example: kb-123456
 *                       action:
 *                         type: string
 *                         example: read
 *                       hasAccess:
 *                         type: boolean
 *                         example: true
 *       401:
 *         description: 未授权
 */
router.post('/batch-check-access', verifyToken, knowledgeAuthController.batchCheckAccess);

/**
 * @swagger
 * /auth/knowledge/user/{userId}/permissions:
 *   get:
 *     summary: 获取指定用户的知识库权限
 *     tags: [知识库权限]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: userId
 *         required: true
 *         schema:
 *           type: integer
 *         description: 用户ID
 *     responses:
 *       200:
 *         description: 成功返回权限列表
 *       401:
 *         description: 未授权
 *       403:
 *         description: 权限不足
 */
router.get('/user/:userId/permissions', verifyToken, verifyAdmin, knowledgeAuthController.getUserPermissions);

/**
 * @swagger
 * /auth/knowledge/user/{userId}/permissions:
 *   post:
 *     summary: 分配知识库权限给用户
 *     tags: [知识库权限]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: userId
 *         required: true
 *         schema:
 *           type: integer
 *         description: 用户ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - permissions
 *             properties:
 *               permissions:
 *                 type: array
 *                 items:
 *                   type: string
 *                 example: ["knowledge:read", "graph:read"]
 *     responses:
 *       200:
 *         description: 权限分配成功
 *       401:
 *         description: 未授权
 *       403:
 *         description: 权限不足
 */
router.post('/user/:userId/permissions', verifyToken, verifyAdmin, validateCsrfToken, knowledgeAuthController.assignPermissions);

/**
 * @swagger
 * /auth/knowledge/user/{userId}/permissions:
 *   delete:
 *     summary: 撤销用户的知识库权限
 *     tags: [知识库权限]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: userId
 *         required: true
 *         schema:
 *           type: integer
 *         description: 用户ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - permissions
 *             properties:
 *               permissions:
 *                 type: array
 *                 items:
 *                   type: string
 *                 example: ["knowledge:write", "graph:write"]
 *     responses:
 *       200:
 *         description: 权限撤销成功
 *       401:
 *         description: 未授权
 *       403:
 *         description: 权限不足
 */
router.delete('/user/:userId/permissions', verifyToken, verifyAdmin, validateCsrfToken, knowledgeAuthController.revokePermissions);

/**
 * @swagger
 * /auth/knowledge/access-log:
 *   post:
 *     summary: 记录知识资源访问日志
 *     tags: [知识库权限]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - resourceType
 *               - resourceId
 *               - action
 *             properties:
 *               resourceType:
 *                 type: string
 *                 description: 资源类型
 *                 example: knowledge_base
 *               resourceId:
 *                 type: string
 *                 description: 资源ID
 *                 example: kb-123456
 *               action:
 *                 type: string
 *                 description: 操作类型
 *                 example: read
 *     responses:
 *       200:
 *         description: 日志记录成功
 *       401:
 *         description: 未授权
 */
router.post('/access-log', verifyToken, knowledgeAuthController.logAccess);

/**
 * @swagger
 * /auth/knowledge/access-logs:
 *   get:
 *     summary: 获取知识资源访问日志
 *     tags: [知识库权限]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: userId
 *         schema:
 *           type: integer
 *         description: 用户ID
 *       - in: query
 *         name: resourceType
 *         schema:
 *           type: string
 *         description: 资源类型
 *       - in: query
 *         name: resourceId
 *         schema:
 *           type: string
 *         description: 资源ID
 *       - in: query
 *         name: startDate
 *         schema:
 *           type: string
 *           format: date
 *         description: 开始日期
 *       - in: query
 *         name: endDate
 *         schema:
 *           type: string
 *           format: date
 *         description: 结束日期
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
 *         description: 每页条数
 *     responses:
 *       200:
 *         description: 成功返回日志列表
 *       401:
 *         description: 未授权
 *       403:
 *         description: 权限不足
 */
router.get('/access-logs', verifyToken, verifyAdmin, knowledgeAuthController.getAccessLogs);

module.exports = router;
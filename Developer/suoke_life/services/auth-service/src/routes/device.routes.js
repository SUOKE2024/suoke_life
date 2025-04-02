/**
 * 设备管理路由
 */
const express = require('express');
const router = express.Router();
const deviceController = require('../controllers/device.controller');
const { verifyToken } = require('../middlewares/auth.middleware');

/**
 * @swagger
 * /auth/devices:
 *   get:
 *     summary: 获取用户设备列表
 *     description: 获取当前用户的所有已注册设备
 *     tags: [设备管理]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: 成功获取设备列表
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 data:
 *                   type: object
 *                   properties:
 *                     devices:
 *                       type: array
 *                       items:
 *                         type: object
 *                     currentDeviceId:
 *                       type: string
 *       401:
 *         description: 未授权
 *       500:
 *         description: 服务器错误
 */
router.get('/', verifyToken, deviceController.getUserDevices);

/**
 * @swagger
 * /auth/devices/{deviceId}:
 *   delete:
 *     summary: 删除设备
 *     description: 删除指定的设备
 *     tags: [设备管理]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: deviceId
 *         required: true
 *         schema:
 *           type: string
 *         description: 设备ID
 *     responses:
 *       200:
 *         description: 设备已成功删除
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 message:
 *                   type: string
 *                   example: 设备已删除
 *       400:
 *         description: 请求错误，如无法删除当前设备
 *       401:
 *         description: 未授权
 *       404:
 *         description: 设备不存在
 *       500:
 *         description: 服务器错误
 */
router.delete('/:deviceId', verifyToken, deviceController.removeDevice);

/**
 * @swagger
 * /auth/devices/{deviceId}/trust:
 *   post:
 *     summary: 信任设备
 *     description: 将设备标记为受信任，可能会减少安全验证
 *     tags: [设备管理]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: deviceId
 *         required: true
 *         schema:
 *           type: string
 *         description: 设备ID
 *     responses:
 *       200:
 *         description: 设备已被标记为受信任
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 message:
 *                   type: string
 *                   example: 设备已标记为可信任
 *       401:
 *         description: 未授权
 *       404:
 *         description: 设备不存在
 *       500:
 *         description: 服务器错误
 */
router.post('/:deviceId/trust', verifyToken, deviceController.trustDevice);

/**
 * @swagger
 * /auth/devices/{deviceId}/untrust:
 *   post:
 *     summary: 取消信任设备
 *     description: 将设备标记为不受信任
 *     tags: [设备管理]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: deviceId
 *         required: true
 *         schema:
 *           type: string
 *         description: 设备ID
 *     responses:
 *       200:
 *         description: 设备已被标记为不受信任
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 message:
 *                   type: string
 *                   example: 设备已取消信任
 *       401:
 *         description: 未授权
 *       404:
 *         description: 设备不存在
 *       500:
 *         description: 服务器错误
 */
router.post('/:deviceId/untrust', verifyToken, deviceController.untrustDevice);

module.exports = router;
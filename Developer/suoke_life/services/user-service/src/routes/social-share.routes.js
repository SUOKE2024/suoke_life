/**
 * 社交分享路由
 * 处理社交分享相关的API路由
 */
const express = require('express');
const router = express.Router();
const socialShareController = require('../controllers/social-share.controller');
const { authenticateJWT } = require('../middlewares/auth');
const { validateRequestSchema } = require('../middlewares/validation');
const socialShareModel = require('../models/social-share.model');

/**
 * @route POST /api/social-shares
 * @description 创建分享
 * @access 私有（需要认证）
 */
router.post('/', 
  authenticateJWT,
  validateRequestSchema(socialShareModel.createShareSchema),
  socialShareController.createShare
);

/**
 * @route GET /api/social-shares/:shareId
 * @description 获取分享详情
 * @access 公开
 */
router.get('/:shareId', socialShareController.getShareById);

/**
 * @route PUT /api/social-shares/:shareId
 * @description 更新分享
 * @access 私有（需要认证）
 */
router.put('/:shareId',
  authenticateJWT,
  validateRequestSchema(socialShareModel.updateShareSchema),
  socialShareController.updateShare
);

/**
 * @route DELETE /api/social-shares/:shareId
 * @description 删除分享
 * @access 私有（需要认证）
 */
router.delete('/:shareId',
  authenticateJWT,
  socialShareController.deleteShare
);

/**
 * @route GET /api/social-shares/user/:userId
 * @description 获取用户分享列表
 * @access 公开
 */
router.get('/user/:userId', socialShareController.getUserShares);

/**
 * @route POST /api/social-shares/:shareId/interactions
 * @description 记录分享互动
 * @access 私有（需要认证）
 */
router.post('/:shareId/interactions',
  authenticateJWT,
  validateRequestSchema(socialShareModel.recordInteractionSchema),
  socialShareController.recordShareInteraction
);

/**
 * @route GET /api/social-shares/:shareId/interactions
 * @description 获取分享互动列表
 * @access 公开
 */
router.get('/:shareId/interactions', socialShareController.getShareInteractions);

/**
 * @route POST /api/social-shares/:shareId/link
 * @description 生成分享链接
 * @access 私有（需要认证）
 */
router.post('/:shareId/link',
  authenticateJWT,
  socialShareController.generateShareLink
);

/**
 * @route POST /api/social-shares/view/:shareId
 * @description 记录分享查看（无需认证）
 * @access 公开
 */
router.post('/view/:shareId', socialShareController.recordShareView);

module.exports = router;
/**
 * 用户匹配路由
 * 处理用户兴趣图谱匹配相关的API路由
 */
const express = require('express');
const router = express.Router();
const userMatchController = require('../controllers/user-match.controller');
const { authenticateJWT } = require('../middlewares/auth');
const { validateRequestSchema } = require('../middlewares/validation');
const userMatchModel = require('../models/user-match.model');

/**
 * @route POST /api/user-matches
 * @description 创建用户匹配
 * @access 私有（需要认证）
 */
router.post('/',
  authenticateJWT,
  validateRequestSchema(userMatchModel.createMatchSchema),
  userMatchController.createMatch
);

/**
 * @route GET /api/user-matches/:matchId
 * @description 获取匹配详情
 * @access 私有（需要认证）
 */
router.get('/:matchId',
  authenticateJWT,
  userMatchController.getMatchById
);

/**
 * @route PUT /api/user-matches/:matchId/status
 * @description 更新匹配状态
 * @access 私有（需要认证）
 */
router.put('/:matchId/status',
  authenticateJWT,
  validateRequestSchema(userMatchModel.updateMatchStatusSchema),
  userMatchController.updateMatchStatus
);

/**
 * @route GET /api/user-matches
 * @description 获取用户匹配列表
 * @access 私有（需要认证）
 */
router.get('/',
  authenticateJWT,
  userMatchController.getUserMatches
);

/**
 * @route DELETE /api/user-matches/:matchId
 * @description 删除匹配记录
 * @access 私有（需要认证）
 */
router.delete('/:matchId',
  authenticateJWT,
  userMatchController.deleteMatch
);

/**
 * @route POST /api/user-matches/interest-vector
 * @description 计算用户兴趣向量
 * @access 私有（需要认证）
 */
router.post('/interest-vector',
  authenticateJWT,
  userMatchController.calculateUserInterestVector
);

/**
 * @route GET /api/user-matches/potential
 * @description 查找潜在匹配用户
 * @access 私有（需要认证）
 */
router.get('/potential',
  authenticateJWT,
  userMatchController.findPotentialMatches
);

/**
 * @route POST /api/user-matches/connections
 * @description 创建用户连接请求
 * @access 私有（需要认证）
 */
router.post('/connections',
  authenticateJWT,
  validateRequestSchema(userMatchModel.createConnectionSchema),
  userMatchController.createConnection
);

/**
 * @route PUT /api/user-matches/connections/:connectionId/status
 * @description 更新连接状态
 * @access 私有（需要认证）
 */
router.put('/connections/:connectionId/status',
  authenticateJWT,
  validateRequestSchema(userMatchModel.updateConnectionStatusSchema),
  userMatchController.updateConnectionStatus
);

/**
 * @route GET /api/user-matches/connections
 * @description 获取用户连接列表
 * @access 私有（需要认证）
 */
router.get('/connections',
  authenticateJWT,
  userMatchController.getUserConnections
);

module.exports = router;
/**
 * AR增强路由
 * 处理所有AR相关的请求路由
 */
const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');

// 导入控制器
const arController = require('../controllers/ar.controller');

// 导入中间件
const { auth } = require('../middlewares/auth');
const { validate } = require('../middlewares/validate');
const { uploadLimiter } = require('../middlewares/rateLimiter');

// 配置图像上传
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, path.join(__dirname, '../../uploads/ar-images'));
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, `${file.fieldname}-${uniqueSuffix}${path.extname(file.originalname)}`);
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('文件类型必须是图像'));
    }
  }
});

/**
 * 图像识别路由
 * @route POST /api/ar/scan/image
 * @group AR - AR增强相关操作
 * @param {file} image.formData - 图像文件
 * @param {object} location.body - 位置信息
 * @returns {object} 200 - 包含识别到的宝藏列表
 */
router.post('/scan/image', auth(), upload.single('image'), uploadLimiter, arController.scanImage);

/**
 * 上传AR图像扫描结果
 * @route POST /api/ar/scan/image/result
 * @group AR - AR增强相关操作
 * @param {object} data.body - 扫描结果数据
 * @returns {object} 200 - 处理结果
 */
router.post('/scan/image/result', auth(), validate('arScanResult'), (req, res, next) => {
  // 改由前端处理图像分析，仅发送结果数据
  req.body.imageAnalysisResult = req.body.data;
  arController.scanImage(req, res, next);
});

/**
 * 地理位置发现宝藏
 * @route GET /api/ar/discover/location
 * @group AR - AR增强相关操作
 * @param {number} latitude.query.required - 纬度
 * @param {number} longitude.query.required - 经度
 * @param {number} accuracy.query - 精度（米）
 * @returns {object} 200 - 包含发现的宝藏、消息和NPC信息
 */
router.get('/discover/location', auth(), validate('coordinates'), arController.discoverByLocation);

/**
 * 手势收集宝藏
 * @route POST /api/ar/treasures/:treasureId/collect/gesture
 * @group AR - AR增强相关操作
 * @param {string} treasureId.path.required - 宝藏ID
 * @param {object} gestureData.body.required - 手势数据
 * @returns {object} 200 - 收集结果
 */
router.post('/treasures/:treasureId/collect/gesture', auth(), validate('gestureCollection'), arController.collectWithGesture);

/**
 * 启动团队寻宝
 * @route POST /api/ar/teams/:teamId/hunt/:mazeId
 * @group AR - AR增强相关操作
 * @param {string} teamId.path.required - 团队ID
 * @param {string} mazeId.path.required - 迷宫ID
 * @returns {object} 200 - 寻宝会话信息
 */
router.post('/teams/:teamId/hunt/:mazeId', auth(), validate('teamHunt'), arController.startTeamTreasureHunt);

/**
 * 分享宝藏
 * @route POST /api/ar/treasures/:treasureId/share
 * @group AR - AR增强相关操作
 * @param {string} treasureId.path.required - 宝藏ID
 * @param {string} receiverId.body.required - 接收者ID
 * @returns {object} 200 - 分享结果
 */
router.post('/treasures/:treasureId/share', auth(), validate('shareTreasure'), arController.shareTreasure);

/**
 * 获取附近AR留言
 * @route GET /api/ar/messages
 * @group AR - AR增强相关操作
 * @param {number} latitude.query.required - 纬度
 * @param {number} longitude.query.required - 经度
 * @param {number} radius.query - 搜索半径（米）
 * @returns {object} 200 - 消息列表
 */
router.get('/messages', auth(), validate('coordinates'), arController.getNearbyARMessages);

/**
 * 创建AR留言
 * @route POST /api/ar/messages
 * @group AR - AR增强相关操作
 * @param {string} content.body.required - 消息内容
 * @param {object} location.body.required - 位置信息
 * @returns {object} 201 - 创建的消息
 */
router.post('/messages', auth(), validate('arMessage'), arController.createARMessage);

/**
 * 与NPC交互
 * @route POST /api/ar/npc/interact
 * @group AR - AR增强相关操作
 * @param {string} message.body.required - 消息内容
 * @param {string} npcId.body - NPC ID
 * @returns {object} 200 - NPC回复
 */
router.post('/npc/interact', auth(), validate('npcInteraction'), arController.interactWithNPC);

/**
 * 提交环境扫描数据
 * @route POST /api/ar/environment/scan
 * @group AR - AR增强相关操作
 * @param {object} scanData.body.required - 扫描数据
 * @param {object} location.body.required - 位置信息
 * @returns {object} 200 - 处理结果
 */
router.post('/environment/scan', auth(), validate('environmentScan'), arController.submitEnvironmentScan);

module.exports = router;
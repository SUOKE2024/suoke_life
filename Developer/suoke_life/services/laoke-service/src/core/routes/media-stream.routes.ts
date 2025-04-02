import express from 'express';
import * as mediaStreamController from '../../services/media-stream/media-stream.controller';
import { authenticate } from '../middleware/auth.middleware';
import * as validationMiddleware from '../middleware/validation.middleware';

const router = express.Router();

/**
 * @route POST /api/v1/media-stream
 * @desc 上传并处理媒体文件
 * @access 需要认证
 */
router.post(
  '/',
  authenticate,
  mediaStreamController.uploadAndProcessMedia
);

/**
 * @route GET /api/v1/media-stream
 * @desc 获取用户的媒体流记录
 * @access 需要认证
 */
router.get(
  '/',
  authenticate,
  mediaStreamController.getUserMediaStreams
);

/**
 * @route GET /api/v1/media-stream/:id
 * @desc 获取媒体流详情
 * @access 需要认证
 */
router.get(
  '/:id',
  authenticate,
  mediaStreamController.getMediaStreamById
);

/**
 * @route GET /api/v1/media-stream/:id/download
 * @desc 下载处理结果文件
 * @access 需要认证
 */
router.get(
  '/:id/download',
  authenticate,
  mediaStreamController.downloadProcessingResultFile
);

/**
 * @route DELETE /api/v1/media-stream/cleanup
 * @desc 清理过期媒体文件
 * @access 需要管理员权限
 */
router.delete(
  '/cleanup',
  authenticate,
  mediaStreamController.cleanupExpiredMediaFiles
);

export default router; 
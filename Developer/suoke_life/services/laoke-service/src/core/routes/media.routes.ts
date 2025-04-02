import express from 'express';
import multer from 'multer';
import { authenticate } from '../middleware/auth';
import * as mediaStreamController from '../../services/media/media-stream.controller';

const router = express.Router();
const upload = multer({ storage: multer.memoryStorage() });

/**
 * @route POST /api/v1/media/streams
 * @desc 创建媒体流
 * @access Private
 */
router.post('/streams', authenticate, mediaStreamController.createMediaStream);

/**
 * @route POST /api/v1/media/streams/:id/chunks
 * @desc 上传媒体流块
 * @access Private
 */
router.post('/streams/:id/chunks', authenticate, upload.single('chunk'), mediaStreamController.uploadMediaStreamChunk);

/**
 * @route POST /api/v1/media/streams/:id/complete
 * @desc 完成媒体流
 * @access Private
 */
router.post('/streams/:id/complete', authenticate, mediaStreamController.completeMediaStream);

/**
 * @route GET /api/v1/media/streams
 * @desc 获取媒体流列表
 * @access Private
 */
router.get('/streams', authenticate, mediaStreamController.getMediaStreams);

/**
 * @route GET /api/v1/media/streams/:id
 * @desc 获取媒体流详情
 * @access Private
 */
router.get('/streams/:id', authenticate, mediaStreamController.getMediaStreamById);

export default router; 
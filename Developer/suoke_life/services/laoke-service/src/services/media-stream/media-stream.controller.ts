import { Request, Response, NextFunction } from 'express';
import multer from 'multer';
import os from 'os';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import * as mediaStreamService from './media-stream.service';
import { MediaProcessingType } from '../../models/media-stream.model';
import logger from '../../core/utils/logger';
import { ApiError } from '../../core/utils/errors';
import fs from 'fs';

// 配置临时文件存储
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, os.tmpdir());
  },
  filename: (req, file, cb) => {
    const extension = path.extname(file.originalname);
    cb(null, `media-${uuidv4()}${extension}`);
  },
});

const upload = multer({ 
  storage,
  limits: {
    fileSize: 50 * 1024 * 1024, // 限制50MB
  }
});

/**
 * 上传并处理媒体文件
 */
export const uploadAndProcessMedia = async (req: Request, res: Response, next: NextFunction) => {
  upload.single('media')(req, res, async (err) => {
    if (err) {
      return next(new ApiError(400, err.message));
    }
    
    try {
      if (!req.file) {
        throw new ApiError(400, '未提供媒体文件');
      }
      
      const userId = req.user?.id;
      if (!userId) {
        throw new ApiError(401, '未授权');
      }
      
      const processingType = req.body.processingType as MediaProcessingType;
      if (!processingType || !Object.values(MediaProcessingType).includes(processingType)) {
        throw new ApiError(400, '无效的处理类型');
      }
      
      // 获取附加元数据
      const metadata = req.body.metadata ? JSON.parse(req.body.metadata) : {};
      
      // 创建媒体流记录
      const mediaStream = await mediaStreamService.createMediaStream(
        userId,
        req.file,
        processingType,
        metadata
      );
      
      // 返回创建的媒体流记录
      res.status(201).json(mediaStream);
      
      // 异步启动处理（不阻止响应）
      setTimeout(async () => {
        try {
          switch (processingType) {
            case MediaProcessingType.DIALECT_DETECTION:
              await mediaStreamService.processDialectDetection(mediaStream._id.toString());
              break;
            case MediaProcessingType.DIALECT_TRANSLATION:
              const dialectCode = metadata.dialectCode;
              if (!dialectCode) {
                throw new Error('方言代码缺失');
              }
              await mediaStreamService.processDialectTranslation(mediaStream._id.toString(), dialectCode);
              break;
            case MediaProcessingType.SPEECH_TO_TEXT:
              const languageCode = metadata.languageCode || 'zh-CN';
              await mediaStreamService.processSpeechToText(mediaStream._id.toString(), languageCode);
              break;
            case MediaProcessingType.IMAGE_RECOGNITION:
              await mediaStreamService.processImageRecognition(mediaStream._id.toString());
              break;
            default:
              logger.error(`不支持的处理类型: ${processingType}`);
          }
        } catch (processingError) {
          logger.error('媒体处理失败:', processingError);
        }
      }, 0);
    } catch (error) {
      logger.error('上传媒体文件失败:', error);
      
      // 删除临时文件
      if (req.file && req.file.path) {
        try {
          fs.unlinkSync(req.file.path);
        } catch (unlinkError) {
          logger.error('删除临时文件失败:', unlinkError);
        }
      }
      
      next(error);
    }
  });
};

/**
 * 获取用户媒体流记录
 */
export const getUserMediaStreams = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const userId = req.user?.id;
    if (!userId) {
      throw new ApiError(401, '未授权');
    }
    
    const { limit = 20, skip = 0, streamType, processingType, status } = req.query;
    
    // 构建过滤条件
    const filters: Record<string, any> = {};
    if (streamType) filters.streamType = streamType;
    if (processingType) filters.processingType = processingType;
    if (status) filters.status = status;
    
    const result = await mediaStreamService.getUserMediaStreams(
      userId,
      Number(limit),
      Number(skip),
      filters
    );
    
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取用户媒体流记录失败:', error);
    next(error);
  }
};

/**
 * 获取媒体流详情
 */
export const getMediaStreamById = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    
    const mediaStream = await mediaStreamService.getMediaStreamById(id);
    
    // 权限检查 - 用户只能访问自己的媒体流
    if (mediaStream.userId.toString() !== req.user?.id) {
      throw new ApiError(403, '无权访问此媒体流');
    }
    
    res.status(200).json(mediaStream);
  } catch (error) {
    logger.error(`获取媒体流详情失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 下载处理结果文件
 */
export const downloadProcessingResultFile = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    
    // 获取媒体流记录
    const mediaStream = await mediaStreamService.getMediaStreamById(id);
    
    // 权限检查 - 用户只能访问自己的媒体流
    if (mediaStream.userId.toString() !== req.user?.id) {
      throw new ApiError(403, '无权访问此媒体流');
    }
    
    // 获取处理结果文件信息
    const { filePath, mimeType, fileName } = await mediaStreamService.getProcessingResultFile(id);
    
    // 设置响应头
    res.setHeader('Content-Type', mimeType);
    res.setHeader('Content-Disposition', `attachment; filename="${encodeURIComponent(fileName)}"`);
    
    // 发送文件
    res.sendFile(filePath);
  } catch (error) {
    logger.error(`下载处理结果文件失败 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 清理过期媒体文件
 * 注意: 此API应该受到保护，只有管理员可以访问
 */
export const cleanupExpiredMediaFiles = async (req: Request, res: Response, next: NextFunction) => {
  try {
    // 检查用户是否是管理员
    if (!req.user?.roles?.includes('admin')) {
      throw new ApiError(403, '无权执行此操作');
    }
    
    const { days = 7 } = req.query;
    const expirationDays = Number(days);
    
    if (isNaN(expirationDays) || expirationDays < 1) {
      throw new ApiError(400, '过期天数必须是大于0的数字');
    }
    
    const deletedCount = await mediaStreamService.cleanupExpiredMediaFiles(expirationDays);
    
    res.status(200).json({
      message: `已清理 ${deletedCount} 个过期媒体文件`,
      deletedCount
    });
  } catch (error) {
    logger.error('清理过期媒体文件失败:', error);
    next(error);
  }
}; 
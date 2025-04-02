import { Request, Response, NextFunction } from 'express';
import * as mediaStreamService from './media-stream.service';
import { MediaStreamType, MediaStreamStatus } from '../../models/media-stream.model';
import logger from '../../core/utils/logger';
import { ApiError } from '../../core/utils/errors';

/**
 * 创建媒体流
 */
export const createMediaStream = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { streamType, dialect, metadata, deviceInfo } = req.body;
    const userId = req.user?.id;
    
    if (!userId) {
      throw new ApiError(401, '未授权操作');
    }
    
    // 创建会话ID
    const sessionId = req.body.sessionId || `session_${Date.now()}`;
    
    // 验证流类型
    if (!Object.values(MediaStreamType).includes(streamType)) {
      throw new ApiError(400, '无效的媒体流类型');
    }
    
    const mediaStream = await mediaStreamService.createMediaStream({
      userId,
      sessionId,
      streamType,
      dialect,
      metadata,
      deviceInfo
    });
    
    res.status(201).json(mediaStream);
  } catch (error) {
    logger.error('创建媒体流错误:', error);
    next(error);
  }
};

/**
 * 上传媒体流块
 */
export const uploadMediaStreamChunk = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    const chunkIndex = parseInt(req.query.chunkIndex as string || '0');
    
    if (!req.file && !req.body.chunk) {
      throw new ApiError(400, '未提供媒体块数据');
    }
    
    // 获取块数据
    const chunk = req.file ? req.file.buffer : Buffer.from(req.body.chunk, 'base64');
    
    const result = await mediaStreamService.saveMediaStreamChunk(id, chunk, chunkIndex);
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`上传媒体流块错误 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 完成媒体流
 */
export const completeMediaStream = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = req.params;
    const { metadata } = req.body;
    
    const result = await mediaStreamService.completeMediaStream(id, metadata);
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`完成媒体流错误 [ID: ${req.params.id}]:`, error);
    next(error);
  }
};

/**
 * 获取媒体流列表
 */
export const getMediaStreams = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { page = 1, limit = 10, userId, streamType, status } = req.query;
    
    // 权限检查
    if (userId && userId !== req.user?.id && !req.user?.roles?.includes('admin')) {
      throw new ApiError(403, '无权访问其他用户的媒体流');
    }
    
    const result = await mediaStreamService.getMediaStreams({
      userId: (userId as string) || req.user?.id,
      streamType: streamType as MediaStreamType,
      status: status as MediaStreamStatus,
      page: Number(page),
      limit: Number(limit)
    });
    
    res.status(200).json(result);
  } catch (error) {
    logger.error('获取媒体流列表错误:', error);
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
    
    if (!mediaStream) {
      throw new ApiError(404, '媒体流不存在');
    }
    
    // 权限检查
    if (mediaStream.userId !== req.user?.id && !req.user?.roles?.includes('admin')) {
      throw new ApiError(403, '无权访问此媒体流');
    }
    
    res.status(200).json(mediaStream);
  } catch (error) {
    logger.error(`获取媒体流详情错误 [ID: ${req.params.id}]:`, error);
    next(error);
  }
}; 
import { Request, Response } from 'express';
import { logger } from '../../utils/logger';
import * as audioCapture from '../../services/media-capture/audio-capture';
import * as videoCapture from '../../services/media-capture/video-capture';

/**
 * 更新音频隐私设置
 */
export const updateAudioPrivacySettings = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const settings = req.body;
    
    if (!userId) {
      res.status(400).json({ success: false, message: '必须提供用户ID' });
      return;
    }
    
    const updatedSettings = audioCapture.updateUserPrivacySettings(userId, settings);
    
    res.status(200).json({
      success: true,
      data: updatedSettings
    });
  } catch (error) {
    logger.error('更新音频隐私设置失败:', error);
    res.status(500).json({
      success: false,
      message: '更新音频隐私设置失败',
      error: (error as Error).message
    });
  }
};

/**
 * 获取音频隐私设置
 */
export const getAudioPrivacySettings = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      res.status(400).json({ success: false, message: '必须提供用户ID' });
      return;
    }
    
    const settings = audioCapture.getUserPrivacySettings(userId);
    
    res.status(200).json({
      success: true,
      data: settings
    });
  } catch (error) {
    logger.error('获取音频隐私设置失败:', error);
    res.status(500).json({
      success: false,
      message: '获取音频隐私设置失败',
      error: (error as Error).message
    });
  }
};

/**
 * 捕获音频数据
 */
export const captureAudioData = async (req: Request, res: Response): Promise<void> => {
  try {
    const audioData = req.body;
    
    if (!audioData || !audioData.userId) {
      res.status(400).json({ success: false, message: '音频数据不完整' });
      return;
    }
    
    const result = await audioCapture.captureAudio(audioData);
    
    if (!result) {
      res.status(403).json({
        success: false,
        message: '音频捕获已被用户设置禁止'
      });
      return;
    }
    
    res.status(201).json({
      success: true,
      data: result
    });
  } catch (error) {
    logger.error('音频捕获失败:', error);
    res.status(500).json({
      success: false,
      message: '音频捕获失败',
      error: (error as Error).message
    });
  }
};

/**
 * 获取用户音频历史
 */
export const getUserAudioHistory = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const { limit } = req.query;
    
    if (!userId) {
      res.status(400).json({ success: false, message: '必须提供用户ID' });
      return;
    }
    
    const history = audioCapture.getUserAudioHistory(
      userId,
      limit ? parseInt(limit as string) : undefined
    );
    
    res.status(200).json({
      success: true,
      data: history
    });
  } catch (error) {
    logger.error('获取音频历史失败:', error);
    res.status(500).json({
      success: false,
      message: '获取音频历史失败',
      error: (error as Error).message
    });
  }
};

/**
 * 删除音频数据
 */
export const deleteAudioData = async (req: Request, res: Response): Promise<void> => {
  try {
    const { audioId, userId } = req.params;
    
    if (!audioId || !userId) {
      res.status(400).json({ success: false, message: '必须提供音频ID和用户ID' });
      return;
    }
    
    const deleted = audioCapture.deleteAudio(audioId, userId);
    
    if (!deleted) {
      res.status(404).json({
        success: false,
        message: '音频数据未找到或无权删除'
      });
      return;
    }
    
    res.status(200).json({
      success: true,
      message: '音频数据已删除'
    });
  } catch (error) {
    logger.error('删除音频数据失败:', error);
    res.status(500).json({
      success: false,
      message: '删除音频数据失败',
      error: (error as Error).message
    });
  }
};

/**
 * 更新视频隐私设置
 */
export const updateVideoPrivacySettings = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const settings = req.body;
    
    if (!userId) {
      res.status(400).json({ success: false, message: '必须提供用户ID' });
      return;
    }
    
    const updatedSettings = videoCapture.updateUserPrivacySettings(userId, settings);
    
    res.status(200).json({
      success: true,
      data: updatedSettings
    });
  } catch (error) {
    logger.error('更新视频隐私设置失败:', error);
    res.status(500).json({
      success: false,
      message: '更新视频隐私设置失败',
      error: (error as Error).message
    });
  }
};

/**
 * 获取视频隐私设置
 */
export const getVideoPrivacySettings = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      res.status(400).json({ success: false, message: '必须提供用户ID' });
      return;
    }
    
    const settings = videoCapture.getUserPrivacySettings(userId);
    
    res.status(200).json({
      success: true,
      data: settings
    });
  } catch (error) {
    logger.error('获取视频隐私设置失败:', error);
    res.status(500).json({
      success: false,
      message: '获取视频隐私设置失败',
      error: (error as Error).message
    });
  }
};

/**
 * 捕获视频数据
 */
export const captureVideoData = async (req: Request, res: Response): Promise<void> => {
  try {
    const videoData = req.body;
    
    if (!videoData || !videoData.userId) {
      res.status(400).json({ success: false, message: '视频数据不完整' });
      return;
    }
    
    const result = await videoCapture.captureVideo(videoData);
    
    if (!result) {
      res.status(403).json({
        success: false,
        message: '视频捕获已被用户设置禁止'
      });
      return;
    }
    
    res.status(201).json({
      success: true,
      data: result
    });
  } catch (error) {
    logger.error('视频捕获失败:', error);
    res.status(500).json({
      success: false,
      message: '视频捕获失败',
      error: (error as Error).message
    });
  }
};

/**
 * 获取用户视频历史
 */
export const getUserVideoHistory = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const { limit } = req.query;
    
    if (!userId) {
      res.status(400).json({ success: false, message: '必须提供用户ID' });
      return;
    }
    
    const history = videoCapture.getUserVideoHistory(
      userId,
      limit ? parseInt(limit as string) : undefined
    );
    
    res.status(200).json({
      success: true,
      data: history
    });
  } catch (error) {
    logger.error('获取视频历史失败:', error);
    res.status(500).json({
      success: false,
      message: '获取视频历史失败',
      error: (error as Error).message
    });
  }
};

/**
 * 删除视频数据
 */
export const deleteVideoData = async (req: Request, res: Response): Promise<void> => {
  try {
    const { videoId, userId } = req.params;
    
    if (!videoId || !userId) {
      res.status(400).json({ success: false, message: '必须提供视频ID和用户ID' });
      return;
    }
    
    const deleted = videoCapture.deleteVideo(videoId, userId);
    
    if (!deleted) {
      res.status(404).json({
        success: false,
        message: '视频数据未找到或无权删除'
      });
      return;
    }
    
    res.status(200).json({
      success: true,
      message: '视频数据已删除'
    });
  } catch (error) {
    logger.error('删除视频数据失败:', error);
    res.status(500).json({
      success: false,
      message: '删除视频数据失败',
      error: (error as Error).message
    });
  }
};
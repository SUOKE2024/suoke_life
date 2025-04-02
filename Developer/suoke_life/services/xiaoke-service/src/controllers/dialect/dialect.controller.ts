import { Request, Response } from 'express';
import { logger } from '../../utils/logger';
import * as dialectRecognition from '../../services/dialect/dialect-recognition';
import * as dialectSynthesis from '../../services/dialect/dialect-synthesis';

/**
 * 获取支持的方言列表
 */
export const getSupportedDialects = async (req: Request, res: Response): Promise<void> => {
  try {
    // 将枚举转换为数组
    const dialects = Object.values(dialectRecognition.ChineseDialect);
    
    res.status(200).json({
      success: true,
      data: {
        dialects,
        count: dialects.length
      }
    });
  } catch (error) {
    logger.error('获取方言列表失败:', error);
    res.status(500).json({
      success: false,
      message: '获取方言列表失败',
      error: (error as Error).message
    });
  }
};

/**
 * 获取用户方言偏好
 */
export const getUserDialectPreference = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      res.status(400).json({ success: false, message: '必须提供用户ID' });
      return;
    }
    
    const preferences = dialectRecognition.getUserDialectPreference(userId);
    
    res.status(200).json({
      success: true,
      data: preferences
    });
  } catch (error) {
    logger.error('获取用户方言偏好失败:', error);
    res.status(500).json({
      success: false,
      message: '获取用户方言偏好失败',
      error: (error as Error).message
    });
  }
};

/**
 * 更新用户方言偏好
 */
export const updateUserDialectPreference = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const preferences = req.body;
    
    if (!userId) {
      res.status(400).json({ success: false, message: '必须提供用户ID' });
      return;
    }
    
    const updatedPreferences = dialectRecognition.updateUserDialectPreference(userId, preferences);
    
    res.status(200).json({
      success: true,
      data: updatedPreferences
    });
  } catch (error) {
    logger.error('更新用户方言偏好失败:', error);
    res.status(500).json({
      success: false,
      message: '更新用户方言偏好失败',
      error: (error as Error).message
    });
  }
};

/**
 * 识别文本中的方言
 */
export const recognizeDialect = async (req: Request, res: Response): Promise<void> => {
  try {
    const { text, userId, audioId } = req.body;
    
    if (!text || !userId) {
      res.status(400).json({ success: false, message: '必须提供文本和用户ID' });
      return;
    }
    
    const result = await dialectRecognition.recognizeDialect(text, userId, audioId);
    
    res.status(200).json({
      success: true,
      data: result
    });
  } catch (error) {
    logger.error('方言识别失败:', error);
    res.status(500).json({
      success: false,
      message: '方言识别失败',
      error: (error as Error).message
    });
  }
};

/**
 * 将方言文本转换为标准普通话
 */
export const translateToMandarin = async (req: Request, res: Response): Promise<void> => {
  try {
    const { text, sourceDialect } = req.body;
    
    if (!text || !sourceDialect) {
      res.status(400).json({ success: false, message: '必须提供文本和源方言' });
      return;
    }
    
    const translatedText = await dialectRecognition.translateToMandarin(text, sourceDialect);
    
    res.status(200).json({
      success: true,
      data: {
        originalText: text,
        sourceDialect,
        translatedText
      }
    });
  } catch (error) {
    logger.error('方言转换失败:', error);
    res.status(500).json({
      success: false,
      message: '方言转换失败',
      error: (error as Error).message
    });
  }
};

/**
 * 获取用户的方言识别历史
 */
export const getUserDialectHistory = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const { limit } = req.query;
    
    if (!userId) {
      res.status(400).json({ success: false, message: '必须提供用户ID' });
      return;
    }
    
    const history = dialectRecognition.getUserDialectHistory(
      userId,
      limit ? parseInt(limit as string) : undefined
    );
    
    res.status(200).json({
      success: true,
      data: history
    });
  } catch (error) {
    logger.error('获取方言识别历史失败:', error);
    res.status(500).json({
      success: false,
      message: '获取方言识别历史失败',
      error: (error as Error).message
    });
  }
};

/**
 * 获取所有方言发音人
 */
export const getAllDialectVoices = async (req: Request, res: Response): Promise<void> => {
  try {
    const voices = dialectSynthesis.getAllDialectVoices();
    
    res.status(200).json({
      success: true,
      data: {
        voices,
        count: voices.length
      }
    });
  } catch (error) {
    logger.error('获取方言发音人失败:', error);
    res.status(500).json({
      success: false,
      message: '获取方言发音人失败',
      error: (error as Error).message
    });
  }
};

/**
 * 获取特定方言的发音人
 */
export const getDialectVoices = async (req: Request, res: Response): Promise<void> => {
  try {
    const { dialect } = req.params;
    
    if (!dialect) {
      res.status(400).json({ success: false, message: '必须提供方言' });
      return;
    }
    
    const voices = dialectSynthesis.getDialectVoices(dialect as dialectRecognition.ChineseDialect);
    
    res.status(200).json({
      success: true,
      data: {
        dialect,
        voices,
        count: voices.length
      }
    });
  } catch (error) {
    logger.error('获取方言发音人失败:', error);
    res.status(500).json({
      success: false,
      message: '获取方言发音人失败',
      error: (error as Error).message
    });
  }
};

/**
 * 合成方言语音
 */
export const synthesizeDialectSpeech = async (req: Request, res: Response): Promise<void> => {
  try {
    const request = req.body;
    
    if (!request.text || !request.dialect || !request.userId) {
      res.status(400).json({ success: false, message: '必须提供文本、方言和用户ID' });
      return;
    }
    
    const result = await dialectSynthesis.synthesizeDialectSpeech(request);
    
    res.status(200).json({
      success: true,
      data: result
    });
  } catch (error) {
    logger.error('方言语音合成失败:', error);
    res.status(500).json({
      success: false,
      message: '方言语音合成失败',
      error: (error as Error).message
    });
  }
};

/**
 * 获取用户的语音合成历史
 */
export const getUserSynthesisHistory = async (req: Request, res: Response): Promise<void> => {
  try {
    const { userId } = req.params;
    const { limit } = req.query;
    
    if (!userId) {
      res.status(400).json({ success: false, message: '必须提供用户ID' });
      return;
    }
    
    const history = dialectSynthesis.getUserSynthesisHistory(
      userId,
      limit ? parseInt(limit as string) : undefined
    );
    
    res.status(200).json({
      success: true,
      data: history
    });
  } catch (error) {
    logger.error('获取语音合成历史失败:', error);
    res.status(500).json({
      success: false,
      message: '获取语音合成历史失败',
      error: (error as Error).message
    });
  }
};
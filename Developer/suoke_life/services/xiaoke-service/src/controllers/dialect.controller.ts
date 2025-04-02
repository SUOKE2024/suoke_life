/**
 * 小克服务 - 方言控制器
 */

import { Request, Response } from 'express';
import dialectService from '../services/dialect.service';
import { logger } from '../utils/logger';
import { metrics } from '../core/metrics';

/**
 * 获取所有支持的方言列表
 * @param req 请求对象
 * @param res 响应对象
 */
export const getAllSupportedDialects = async (req: Request, res: Response) => {
  try {
    const result = await dialectService.getAllSupportedDialects();
    
    // 记录指标
    metrics.incrementApiCalls('get_dialects');
    
    return res.json(result);
  } catch (error) {
    logger.error(`获取方言列表失败: ${error.message}`);
    return res.status(500).json({
      success: false,
      error: '获取方言列表失败'
    });
  }
};

/**
 * 检测音频中的方言
 * @param req 请求对象
 * @param res 响应对象
 */
export const detectDialect = async (req: Request, res: Response) => {
  try {
    // 获取上传的音频文件
    const audioFile = req.file;
    
    if (!audioFile) {
      return res.status(400).json({
        success: false,
        error: '未提供音频文件'
      });
    }
    
    // 开始计时
    const startTime = Date.now();
    
    // 执行方言检测
    const result = await dialectService.detectDialect(audioFile);
    
    // 记录指标
    const processingTime = Date.now() - startTime;
    metrics.recordProcessingTime('dialect_detection', processingTime);
    metrics.incrementApiCalls('detect_dialect');
    
    return res.json(result);
  } catch (error) {
    logger.error(`方言检测失败: ${error.message}`);
    return res.status(500).json({
      success: false,
      error: '方言检测失败'
    });
  }
};

/**
 * 将方言音频翻译为标准普通话
 * @param req 请求对象
 * @param res 响应对象
 */
export const translateDialect = async (req: Request, res: Response) => {
  try {
    // 获取上传的音频文件和方言代码
    const audioFile = req.file;
    const { dialectCode } = req.body;
    
    if (!audioFile) {
      return res.status(400).json({
        success: false,
        error: '未提供音频文件'
      });
    }
    
    if (!dialectCode) {
      return res.status(400).json({
        success: false,
        error: '未提供方言代码'
      });
    }
    
    // 开始计时
    const startTime = Date.now();
    
    // 执行方言翻译
    const result = await dialectService.translateDialect(dialectCode, audioFile);
    
    // 记录指标
    const processingTime = Date.now() - startTime;
    metrics.recordProcessingTime('dialect_translation', processingTime);
    metrics.incrementApiCalls('translate_dialect');
    
    return res.json(result);
  } catch (error) {
    logger.error(`方言翻译失败: ${error.message}`);
    return res.status(500).json({
      success: false,
      error: '方言翻译失败'
    });
  }
};

/**
 * 获取方言统计信息
 * @param req 请求对象
 * @param res 响应对象
 */
export const getDialectStats = async (req: Request, res: Response) => {
  try {
    const result = await dialectService.getDialectStats();
    
    // 记录指标
    metrics.incrementApiCalls('get_dialect_stats');
    
    return res.json(result);
  } catch (error) {
    logger.error(`获取方言统计信息失败: ${error.message}`);
    return res.status(500).json({
      success: false,
      error: '获取方言统计信息失败'
    });
  }
};

/**
 * 获取用户的方言学习进度
 * @param req 请求对象
 * @param res 响应对象
 */
export const getUserDialectProgress = async (req: Request, res: Response) => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      return res.status(400).json({
        success: false,
        error: '未提供用户ID'
      });
    }
    
    const result = await dialectService.getUserDialectLearningProgress(userId);
    
    // 记录指标
    metrics.incrementApiCalls('get_user_dialect_progress');
    
    return res.json(result);
  } catch (error) {
    logger.error(`获取用户方言学习进度失败: ${error.message}`);
    return res.status(500).json({
      success: false,
      error: '获取用户方言学习进度失败'
    });
  }
};
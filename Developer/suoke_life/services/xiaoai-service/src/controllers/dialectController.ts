import { Request, Response } from 'express';
import { DialectService } from '../services/DialectService';
import { User } from '../models/User';
import { Logger } from '../utils/logger';
import { DialectType } from '../types';
import { metrics } from '../core/metrics';
import { performanceMonitor } from '../core/performance';

const logger = new Logger('DialectController');
const dialectService = new DialectService();

export const dialectController = {
  /**
   * 获取所有支持的方言列表
   */
  getSupportedDialects: async (req: Request, res: Response) => {
    try {
      const dialects = await dialectService.getSupportedDialects();
      res.status(200).json({
        success: true,
        data: {
          dialects,
          count: dialects.length
        }
      });
    } catch (error) {
      logger.error('获取支持的方言列表失败', { error });
      res.status(500).json({
        success: false,
        message: '获取支持的方言列表时发生错误',
        error: error instanceof Error ? error.message : String(error)
      });
    }
  },

  /**
   * 获取所有活跃的方言列表
   */
  getAllActiveDialects: async (req: Request, res: Response) => {
    try {
      const result = await dialectService.getAllActiveDialects();
      
      // 记录指标
      metrics.incrementApiCalls('get_active_dialects');
      
      return res.json(result);
    } catch (error) {
      logger.error(`获取活跃方言列表失败: ${error.message}`);
      return res.status(500).json({
        success: false,
        error: '获取方言列表失败'
      });
    }
  },

  /**
   * 获取用户的方言偏好设置
   */
  getUserDialectPreferences: async (req: Request, res: Response) => {
    try {
      const { userId } = req.params;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '用户ID不能为空'
        });
      }

      const user = await User.findOne({ userId });
      
      if (!user) {
        return res.status(404).json({
          success: false,
          message: '未找到用户'
        });
      }

      res.status(200).json({
        success: true,
        data: user.dialectPreferences
      });
    } catch (error) {
      logger.error('获取用户方言偏好设置失败', { error, userId: req.params.userId });
      res.status(500).json({
        success: false,
        message: '获取用户方言偏好设置时发生错误',
        error: error instanceof Error ? error.message : String(error)
      });
    }
  },

  /**
   * 更新用户的方言偏好设置
   */
  updateUserDialectPreferences: async (req: Request, res: Response) => {
    try {
      const { userId } = req.params;
      const { primary, secondary, autoDetect } = req.body;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '用户ID不能为空'
        });
      }

      const user = await User.findOne({ userId });
      
      if (!user) {
        return res.status(404).json({
          success: false,
          message: '未找到用户'
        });
      }

      // 验证方言类型
      if (primary && !Object.values(DialectType).includes(primary as DialectType)) {
        return res.status(400).json({
          success: false,
          message: '无效的主要方言类型'
        });
      }

      if (secondary && !Object.values(DialectType).includes(secondary as DialectType)) {
        return res.status(400).json({
          success: false,
          message: '无效的次要方言类型'
        });
      }

      // 更新方言偏好
      if (primary) {
        user.dialectPreferences.primary = primary;
      }
      
      if (secondary !== undefined) {
        user.dialectPreferences.secondary = secondary;
      }
      
      if (autoDetect !== undefined) {
        user.dialectPreferences.autoDetect = autoDetect;
      }

      await user.save();

      res.status(200).json({
        success: true,
        data: user.dialectPreferences,
        message: '用户方言偏好设置已更新'
      });
    } catch (error) {
      logger.error('更新用户方言偏好设置失败', { error, userId: req.params.userId });
      res.status(500).json({
        success: false,
        message: '更新用户方言偏好设置时发生错误',
        error: error instanceof Error ? error.message : String(error)
      });
    }
  },

  /**
   * 检测文本使用的方言
   */
  detectDialect: async (req: Request, res: Response) => {
    try {
      const { text } = req.body;
      
      if (!text || typeof text !== 'string') {
        return res.status(400).json({
          success: false,
          message: '文本不能为空并且必须是字符串'
        });
      }

      const detection = await dialectService.detectDialect(text);
      
      res.status(200).json({
        success: true,
        data: detection
      });
    } catch (error) {
      logger.error('方言检测失败', { error, text: req.body.text });
      res.status(500).json({
        success: false,
        message: '方言检测时发生错误',
        error: error instanceof Error ? error.message : String(error)
      });
    }
  },

  /**
   * 检测音频中的方言
   */
  detectAudioDialect: async (req: Request, res: Response) => {
    // 启动性能监测
    performanceMonitor.mark('dialect_detection_start');
    
    try {
      // 获取上传的音频文件
      const audioFile = req.file;
      
      if (!audioFile) {
        return res.status(400).json({
          success: false,
          error: '未提供音频文件'
        });
      }
      
      // 将文件转换为Buffer
      const audioBuffer = audioFile.buffer;
      
      // 执行方言检测
      const result = await dialectService.detectAudioDialect(audioBuffer);
      
      // 记录指标
      metrics.incrementApiCalls('detect_dialect');
      
      // 完成性能监测
      const processingTime = performanceMonitor.measure('dialect_detection_start');
      metrics.recordProcessingTime('dialect_detection', processingTime);
      
      return res.json(result);
    } catch (error) {
      logger.error(`方言检测失败: ${error.message}`);
      
      // 完成性能监测（即使失败）
      if (performanceMonitor.hasMark('dialect_detection_start')) {
        performanceMonitor.measure('dialect_detection_start');
      }
      
      return res.status(500).json({
        success: false,
        error: '方言检测失败'
      });
    }
  },

  /**
   * 将文本翻译成指定方言
   */
  translateToDialect: async (req: Request, res: Response) => {
    try {
      const { text, targetDialect } = req.body;
      
      if (!text || typeof text !== 'string') {
        return res.status(400).json({
          success: false,
          message: '文本不能为空并且必须是字符串'
        });
      }

      if (!targetDialect || !Object.values(DialectType).includes(targetDialect as DialectType)) {
        return res.status(400).json({
          success: false,
          message: '无效的目标方言类型'
        });
      }

      const translation = await dialectService.translateToDialect(text, targetDialect as DialectType);
      
      res.status(200).json({
        success: true,
        data: translation
      });
    } catch (error) {
      logger.error('方言翻译失败', { error, text: req.body.text, targetDialect: req.body.targetDialect });
      res.status(500).json({
        success: false,
        message: '方言翻译时发生错误',
        error: error instanceof Error ? error.message : String(error)
      });
    }
  },

  /**
   * 将方言文本转换为普通话
   */
  translateToMandarin: async (req: Request, res: Response) => {
    try {
      const { text, sourceDialect } = req.body;
      
      if (!text || typeof text !== 'string') {
        return res.status(400).json({
          success: false,
          message: '文本不能为空并且必须是字符串'
        });
      }

      if (!sourceDialect || !Object.values(DialectType).includes(sourceDialect as DialectType)) {
        return res.status(400).json({
          success: false,
          message: '无效的源方言类型'
        });
      }

      const translation = await dialectService.translateToMandarin(text, sourceDialect as DialectType);
      
      res.status(200).json({
        success: true,
        data: translation
      });
    } catch (error) {
      logger.error('方言转换失败', { error, text: req.body.text, sourceDialect: req.body.sourceDialect });
      res.status(500).json({
        success: false,
        message: '方言转换为普通话时发生错误',
        error: error instanceof Error ? error.message : String(error)
      });
    }
  },

  /**
   * 将方言音频翻译为标准普通话
   */
  translateDialect: async (req: Request, res: Response) => {
    // 启动性能监测
    performanceMonitor.mark('dialect_translation_start');
    
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
      
      // 将文件转换为Buffer
      const audioBuffer = audioFile.buffer;
      
      // 执行方言翻译
      const result = await dialectService.translateDialectAudio(dialectCode, audioBuffer);
      
      // 记录指标
      metrics.incrementApiCalls('translate_dialect');
      
      // 完成性能监测
      const processingTime = performanceMonitor.measure('dialect_translation_start');
      metrics.recordProcessingTime('dialect_translation', processingTime);
      
      return res.json(result);
    } catch (error) {
      logger.error(`方言翻译失败: ${error.message}`);
      
      // 完成性能监测（即使失败）
      if (performanceMonitor.hasMark('dialect_translation_start')) {
        performanceMonitor.measure('dialect_translation_start');
      }
      
      return res.status(500).json({
        success: false,
        error: '方言翻译失败'
      });
    }
  },

  /**
   * 根据地区获取推荐方言
   */
  getDialectsByRegion: async (req: Request, res: Response) => {
    try {
      const { region } = req.params;
      
      if (!region) {
        return res.status(400).json({
          success: false,
          message: '地区名称不能为空'
        });
      }

      const dialects = await dialectService.getDialectsByRegion(region);
      
      res.status(200).json({
        success: true,
        data: dialects
      });
    } catch (error) {
      logger.error('获取地区方言失败', { error, region: req.params.region });
      res.status(500).json({
        success: false,
        message: '获取地区方言时发生错误',
        error: error instanceof Error ? error.message : String(error)
      });
    }
  },

  /**
   * 获取方言的文化背景信息
   */
  getDialectCulturalInfo: async (req: Request, res: Response) => {
    try {
      const { dialectCode } = req.params;
      
      if (!dialectCode) {
        return res.status(400).json({
          success: false,
          error: '未提供方言代码'
        });
      }
      
      const result = await dialectService.getDialectCulturalInfo(dialectCode);
      
      // 记录指标
      metrics.incrementApiCalls('get_dialect_cultural_info');
      
      return res.json(result);
    } catch (error) {
      logger.error(`获取方言文化信息失败: ${error.message}`);
      return res.status(500).json({
        success: false,
        error: '获取方言文化信息失败'
      });
    }
  },

  /**
   * 创建方言学习计划
   */
  createDialectLearningPlan: async (req: Request, res: Response) => {
    try {
      const { userId, dialectCode } = req.body;
      
      if (!userId || !dialectCode) {
        return res.status(400).json({
          success: false,
          error: '缺少必要参数'
        });
      }
      
      const result = await dialectService.createDialectLearningPlan(userId, dialectCode);
      
      // 记录指标
      metrics.incrementApiCalls('create_dialect_learning_plan');
      
      return res.json(result);
    } catch (error) {
      logger.error(`创建方言学习计划失败: ${error.message}`);
      return res.status(500).json({
        success: false,
        error: '创建方言学习计划失败'
      });
    }
  }
};
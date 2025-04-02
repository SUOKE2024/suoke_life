/**
 * 小克服务 - 方言服务集成
 * 
 * 该服务封装了共享方言服务的功能，提供方言识别、翻译和样本管理能力
 */

import { Request, Response, NextFunction } from 'express';
import * as path from 'path';
import * as fs from 'fs';
import axios from 'axios';
import { logger } from '../utils/logger';

// 导入共享服务
const sharedServices = require('../../../shared/services');
const dialectService = sharedServices.dialect;

// 配置
const DIALECT_SUPPORT_ENABLED = process.env.DIALECT_SUPPORT_ENABLED === 'true';
const DEFAULT_DIALECT = process.env.DEFAULT_DIALECT || 'mandarin';
const DIALECT_DETECTION_THRESHOLD = parseFloat(process.env.DIALECT_DETECTION_THRESHOLD || '0.7');

/**
 * 方言服务类 - 集成共享方言功能
 */
class DialectService {
  /**
   * 获取所有支持的方言列表
   * @returns 方言列表
   */
  async getAllSupportedDialects() {
    try {
      if (!DIALECT_SUPPORT_ENABLED) {
        return { success: true, dialects: [] };
      }
      
      // 使用Mongoose模型
      const { Dialect } = require('../../../shared/models/dialect.model');
      
      // 获取所有活跃且支持级别大于0的方言
      const dialects = await Dialect.find({
        status: 'active',
        supportLevel: { $gt: 0 }
      }).select('code name region supportLevel sampleStats').lean();
      
      return {
        success: true,
        count: dialects.length,
        dialects
      };
    } catch (error) {
      logger.error(`获取支持的方言列表失败: ${error.message}`);
      return {
        success: false,
        error: `获取方言列表失败: ${error.message}`
      };
    }
  }

  /**
   * 检测音频中的方言
   * @param audioFile 音频文件
   * @returns 检测结果
   */
  async detectDialect(audioFile: Express.Multer.File) {
    try {
      if (!DIALECT_SUPPORT_ENABLED) {
        return { 
          success: true, 
          detected: false,
          dialectCode: DEFAULT_DIALECT,
          confidence: 1.0,
          message: '方言支持未启用，使用默认方言' 
        };
      }
      
      // 验证文件
      if (!audioFile) {
        throw new Error('未提供音频文件');
      }
      
      // 支持的格式
      const supportedFormats = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/ogg'];
      if (!supportedFormats.includes(audioFile.mimetype)) {
        throw new Error(`不支持的音频格式: ${audioFile.mimetype}`);
      }
      
      // 音频处理
      logger.info(`开始检测音频文件中的方言: ${audioFile.originalname}`);
      
      // TODO: 实现实际的方言检测逻辑
      // 这里应该调用实际的方言检测模型
      // 为演示目的，返回模拟结果
      
      const mockDetection = {
        dialectCode: Math.random() > 0.3 ? 'sichuanese' : DEFAULT_DIALECT,
        confidence: 0.75 + Math.random() * 0.2
      };
      
      // 记录方言样本（如果允许）
      if (mockDetection.confidence > DIALECT_DETECTION_THRESHOLD) {
        try {
          // 使用共享服务记录样本来源
          await dialectService.sample.recordSampleSource(mockDetection.dialectCode, {
            method: 'user-upload',
            location: {
              province: '四川省',
              city: '成都市'
            }
          });
          
          logger.debug(`已记录方言样本来源: ${mockDetection.dialectCode}`);
        } catch (sampleError) {
          logger.warn(`记录方言样本失败: ${sampleError.message}`);
        }
      }
      
      return {
        success: true,
        detected: mockDetection.confidence > DIALECT_DETECTION_THRESHOLD,
        dialectCode: mockDetection.dialectCode,
        confidence: mockDetection.confidence,
        message: mockDetection.confidence > DIALECT_DETECTION_THRESHOLD 
          ? `检测到 ${mockDetection.dialectCode} 方言` 
          : '未能确定方言，使用默认方言'
      };
    } catch (error) {
      logger.error(`方言检测失败: ${error.message}`);
      return {
        success: false,
        error: `方言检测失败: ${error.message}`,
        dialectCode: DEFAULT_DIALECT
      };
    }
  }

  /**
   * 将方言音频翻译为标准普通话
   * @param dialectCode 方言代码
   * @param audioFile 音频文件
   * @returns 翻译结果
   */
  async translateDialect(dialectCode: string, audioFile: Express.Multer.File) {
    try {
      if (!DIALECT_SUPPORT_ENABLED) {
        return { 
          success: false, 
          error: '方言支持未启用',
          message: '方言翻译功能未启用'
        };
      }
      
      // 验证文件和方言代码
      if (!audioFile) {
        throw new Error('未提供音频文件');
      }
      
      if (!dialectCode) {
        throw new Error('未指定方言代码');
      }
      
      // 验证方言是否支持
      const { Dialect } = require('../../../shared/models/dialect.model');
      const dialectInfo = await Dialect.findOne({ 
        code: dialectCode,
        status: 'active',
        supportLevel: { $gt: 1 } // 至少支持级别为2才能翻译
      });
      
      if (!dialectInfo) {
        throw new Error(`不支持翻译 ${dialectCode} 方言或该方言不存在`);
      }
      
      // 模拟翻译过程
      logger.info(`翻译 ${dialectCode} 方言音频: ${audioFile.originalname}`);
      
      // TODO: 调用实际的翻译模型
      // 这里应该使用实际训练好的方言翻译模型
      
      // 模拟延迟和结果
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockResult = {
        original: '我今天去街上买东西，碰到老友了。',
        translated: '我今天去商店购物，遇到了老朋友。',
        confidence: 0.85
      };
      
      // 使用共享服务记录样本质量
      try {
        // 这里应该是实际的样本ID，为演示创建一个模拟ID
        const mockSampleId = `sample_${Date.now()}`;
        
        await dialectService.sample.evaluateSampleQuality(mockSampleId, {
          snr: 25 + Math.random() * 10,
          duration: 5 + Math.random() * 10,
          volume: 0.65 + Math.random() * 0.2,
          speechClarity: 0.8 + Math.random() * 0.15
        });
      } catch (evalError) {
        logger.warn(`评估样本质量失败: ${evalError.message}`);
      }
      
      return {
        success: true,
        dialectCode,
        original: mockResult.original,
        translated: mockResult.translated,
        confidence: mockResult.confidence
      };
    } catch (error) {
      logger.error(`方言翻译失败: ${error.message}`);
      return {
        success: false,
        error: `方言翻译失败: ${error.message}`
      };
    }
  }

  /**
   * 获取方言相关统计信息
   * @returns 统计信息
   */
  async getDialectStats() {
    try {
      if (!DIALECT_SUPPORT_ENABLED) {
        return { success: true, stats: {} };
      }
      
      // 使用共享服务获取统计信息
      const { Dialect } = require('../../../shared/models/dialect.model');
      
      // 获取方言总数和支持分布
      const totalCount = await Dialect.countDocuments();
      const activeCount = await Dialect.countDocuments({ status: 'active' });
      
      // 按支持级别分组
      const supportLevelStats = await Dialect.aggregate([
        { $group: { 
          _id: '$supportLevel', 
          count: { $sum: 1 } 
        }},
        { $sort: { _id: 1 } }
      ]);
      
      // 获取样本最多的5种方言
      const topDialects = await Dialect.find()
        .sort({ 'sampleStats.total': -1 })
        .limit(5)
        .select('code name sampleStats')
        .lean();
      
      return {
        success: true,
        stats: {
          totalDialects: totalCount,
          activeDialects: activeCount,
          supportLevels: supportLevelStats.reduce((acc, curr) => {
            acc[`level${curr._id}`] = curr.count;
            return acc;
          }, {}),
          topDialects
        }
      };
    } catch (error) {
      logger.error(`获取方言统计信息失败: ${error.message}`);
      return {
        success: false,
        error: `获取统计信息失败: ${error.message}`
      };
    }
  }

  /**
   * 小克专属：获取用户的方言学习进度
   * @param userId 用户ID
   */
  async getUserDialectLearningProgress(userId: string) {
    try {
      if (!userId) {
        throw new Error('未提供用户ID');
      }
      
      if (!DIALECT_SUPPORT_ENABLED) {
        return { success: true, progress: [] };
      }
      
      // 这里应实现实际的用户方言学习进度查询
      // 为演示目的，返回模拟数据
      
      return {
        success: true,
        userId,
        progress: [
          {
            dialectCode: 'cantonese',
            dialectName: '粤语',
            level: 3,
            lessonsCompleted: 12,
            totalLessons: 25,
            lastPracticeDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
          },
          {
            dialectCode: 'sichuanese',
            dialectName: '四川话',
            level: 2,
            lessonsCompleted: 8,
            totalLessons: 20,
            lastPracticeDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000)
          }
        ]
      };
    } catch (error) {
      logger.error(`获取用户方言学习进度失败: ${error.message}`);
      return {
        success: false,
        error: `获取学习进度失败: ${error.message}`
      };
    }
  }
}

export default new DialectService();
/**
 * 小艾服务 - 方言服务集成
 * 
 * 该服务封装了共享方言服务的功能，提供方言识别和翻译能力，
 * 并增加了小艾特有的方言文化解析功能
 */

import { logger } from '../utils/logger';
import { DialectDetectionResult, DialectTranslationResult, DialectInfo } from '../types/dialect.types';

// 导入共享服务
const sharedServices = require('../../../shared/services');
const dialectService = sharedServices.dialect;

// 配置
const DIALECT_SUPPORT_ENABLED = process.env.DIALECT_SUPPORT_ENABLED === 'true';
const DEFAULT_DIALECT = process.env.DEFAULT_DIALECT || 'mandarin';
const DIALECT_DETECTION_THRESHOLD = parseFloat(process.env.DIALECT_DETECTION_THRESHOLD || '0.7');

/**
 * 方言文化信息接口
 */
interface DialectCulturalInfo {
  dialectCode: string;
  culturalNotes: string[];
  historicalBackground: string;
  famousLiterature: {
    title: string;
    author: string;
    excerpt: string;
  }[];
  localCustoms: string[];
}

/**
 * 方言服务类 - 集成共享方言功能并增强方言文化分析
 */
class DialectService {
  /**
   * 获取所有活跃的方言列表
   * @returns 方言列表
   */
  async getAllActiveDialects(): Promise<{ success: boolean; dialects?: DialectInfo[]; error?: string }> {
    try {
      if (!DIALECT_SUPPORT_ENABLED) {
        return { success: true, dialects: [] };
      }
      
      // 使用Mongoose模型
      const { Dialect } = require('../../../shared/models/dialect.model');
      
      // 获取所有活跃的方言
      const dialects = await Dialect.find({ status: 'active' })
        .select('code name region supportLevel sampleStats metadata')
        .lean();
      
      return {
        success: true,
        dialects: dialects.map(d => ({
          code: d.code,
          name: d.name,
          region: d.region,
          supportLevel: d.supportLevel,
          sampleStats: d.sampleStats,
          description: d.metadata?.description || '',
          culturalBackground: d.metadata?.culturalNotes?.join('. ') || ''
        }))
      };
    } catch (error) {
      logger.error(`获取活跃方言列表失败: ${error.message}`);
      return {
        success: false,
        error: `获取方言列表失败: ${error.message}`
      };
    }
  }

  /**
   * 检测音频中的方言
   * @param audioBuffer 音频缓冲区
   * @returns 检测结果
   */
  async detectDialect(audioBuffer: Buffer): Promise<DialectDetectionResult> {
    try {
      if (!DIALECT_SUPPORT_ENABLED) {
        return { 
          success: true, 
          detected: false,
          dialectCode: DEFAULT_DIALECT,
          dialectName: '普通话',
          confidence: 1.0,
          message: '方言支持未启用，使用默认方言' 
        };
      }
      
      // 验证音频数据
      if (!audioBuffer || audioBuffer.length === 0) {
        throw new Error('无效的音频数据');
      }
      
      logger.info(`开始检测音频中的方言，数据大小: ${audioBuffer.length} 字节`);
      
      // TODO: 实现实际的方言检测逻辑
      // 这里应该调用实际的方言检测模型
      // 为演示目的，返回模拟结果
      
      const mockDetection = {
        dialectCode: Math.random() > 0.3 ? 'hakka' : DEFAULT_DIALECT,
        confidence: 0.75 + Math.random() * 0.2
      };
      
      // 获取方言名称
      let dialectName = '普通话';
      if (mockDetection.dialectCode !== DEFAULT_DIALECT) {
        try {
          const { Dialect } = require('../../../shared/models/dialect.model');
          const dialectInfo = await Dialect.findOne({ code: mockDetection.dialectCode })
            .select('name')
            .lean();
          
          if (dialectInfo) {
            dialectName = dialectInfo.name;
          }
        } catch (nameError) {
          logger.warn(`获取方言名称失败: ${nameError.message}`);
        }
      }
      
      // 记录方言样本（如果允许）
      if (mockDetection.confidence > DIALECT_DETECTION_THRESHOLD) {
        try {
          // 使用共享服务记录样本来源
          await dialectService.sample.recordSampleSource(mockDetection.dialectCode, {
            method: 'user-upload',
            location: {
              province: '广东省',
              city: '梅州市'
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
        dialectName,
        confidence: mockDetection.confidence,
        message: mockDetection.confidence > DIALECT_DETECTION_THRESHOLD 
          ? `检测到${dialectName}(${mockDetection.dialectCode})方言` 
          : '未能确定方言，使用默认方言'
      };
    } catch (error) {
      logger.error(`方言检测失败: ${error.message}`);
      return {
        success: false,
        detected: false,
        dialectCode: DEFAULT_DIALECT,
        dialectName: '普通话',
        confidence: 0,
        error: `方言检测失败: ${error.message}`
      };
    }
  }

  /**
   * 将方言音频翻译为标准普通话
   * @param dialectCode 方言代码
   * @param audioBuffer 音频缓冲区
   * @returns 翻译结果
   */
  async translateDialect(dialectCode: string, audioBuffer: Buffer): Promise<DialectTranslationResult> {
    try {
      if (!DIALECT_SUPPORT_ENABLED) {
        return { 
          success: false, 
          error: '方言支持未启用',
          message: '方言翻译功能未启用'
        };
      }
      
      // 验证数据
      if (!audioBuffer || audioBuffer.length === 0) {
        throw new Error('无效的音频数据');
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
      logger.info(`翻译 ${dialectCode} 方言音频，数据大小: ${audioBuffer.length} 字节`);
      
      // 模拟延迟和结果
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockResult = {
        original: '我哋今日去街市买嘢，遇到旧朋友。',
        translated: '我们今天去市场买东西，遇到了老朋友。',
        confidence: 0.85,
        culturalNotes: ['在客家话中，"哋"是复数人称代词的标志']
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
        dialectName: dialectInfo.name,
        original: mockResult.original,
        translated: mockResult.translated,
        confidence: mockResult.confidence,
        culturalNotes: mockResult.culturalNotes
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
   * 小艾特色功能：获取方言的文化背景信息
   * @param dialectCode 方言代码
   * @returns 文化背景信息
   */
  async getDialectCulturalInfo(dialectCode: string): Promise<{ 
    success: boolean; 
    info?: DialectCulturalInfo; 
    error?: string 
  }> {
    try {
      if (!dialectCode) {
        throw new Error('未指定方言代码');
      }
      
      if (!DIALECT_SUPPORT_ENABLED) {
        return { 
          success: false, 
          error: '方言支持未启用'
        };
      }
      
      // 验证方言是否存在
      const { Dialect } = require('../../../shared/models/dialect.model');
      const dialectInfo = await Dialect.findOne({ code: dialectCode })
        .select('name metadata region features')
        .lean();
      
      if (!dialectInfo) {
        throw new Error(`方言 ${dialectCode} 不存在`);
      }
      
      // 获取更详细的文化信息
      // 这里实际应该从知识库或其他来源获取更丰富的信息
      // 为演示目的，返回模拟数据
      
      const culturalInfo: DialectCulturalInfo = {
        dialectCode,
        culturalNotes: dialectInfo.metadata?.culturalNotes || [
          `${dialectInfo.name}是中国${dialectInfo.region.province}地区的主要方言`,
          '具有悠久的历史和独特的语音系统',
          '是当地非物质文化遗产的重要组成部分'
        ],
        historicalBackground: dialectInfo.metadata?.history || 
          `${dialectInfo.name}的形成可以追溯到唐宋时期，经历了几个世纪的演变和发展，形成了如今独特的语音和词汇系统。`,
        famousLiterature: [
          {
            title: `${dialectInfo.name}民间故事集`,
            author: '民间文学',
            excerpt: '这是一段示例文本，展示该方言的文学作品摘录。'
          }
        ],
        localCustoms: [
          '传统节日庆祝方式',
          '特色礼仪习俗',
          '当地饮食文化'
        ]
      };
      
      logger.info(`获取 ${dialectCode} 方言文化信息成功`);
      
      return {
        success: true,
        info: culturalInfo
      };
    } catch (error) {
      logger.error(`获取方言文化信息失败: ${error.message}`);
      return {
        success: false,
        error: `获取文化信息失败: ${error.message}`
      };
    }
  }

  /**
   * 小艾特色功能：创建方言学习计划
   * @param userId 用户ID
   * @param dialectCode 方言代码
   * @returns 学习计划
   */
  async createDialectLearningPlan(userId: string, dialectCode: string) {
    try {
      if (!userId || !dialectCode) {
        throw new Error('缺少必要参数');
      }
      
      if (!DIALECT_SUPPORT_ENABLED) {
        return { 
          success: false, 
          error: '方言支持未启用'
        };
      }
      
      // 验证方言是否存在
      const { Dialect } = require('../../../shared/models/dialect.model');
      const dialectInfo = await Dialect.findOne({ code: dialectCode })
        .select('name supportLevel features')
        .lean();
      
      if (!dialectInfo) {
        throw new Error(`方言 ${dialectCode} 不存在`);
      }
      
      // 创建学习计划
      // 实际应该基于用户水平和方言特点生成定制计划
      // 为演示目的，返回模拟数据
      
      logger.info(`为用户 ${userId} 创建 ${dialectCode} 方言学习计划`);
      
      return {
        success: true,
        plan: {
          userId,
          dialectCode,
          dialectName: dialectInfo.name,
          createdAt: new Date(),
          duration: '8周',
          difficulty: '中级',
          weeklyGoals: [
            {
              week: 1,
              focus: '基础语音',
              lessons: ['声调识别', '基本问候语', '数字和时间表达'],
              practiceMinutes: 120
            },
            {
              week: 2,
              focus: '常用词汇',
              lessons: ['家庭称谓', '日常物品', '食物名称'],
              practiceMinutes: 150
            }
          ],
          resources: [
            {
              type: '音频',
              title: `${dialectInfo.name}入门课程`,
              url: `https://example.com/resources/${dialectCode}/intro`
            },
            {
              type: '练习册',
              title: '日常对话练习',
              url: `https://example.com/resources/${dialectCode}/practice`
            }
          ]
        }
      };
    } catch (error) {
      logger.error(`创建方言学习计划失败: ${error.message}`);
      return {
        success: false,
        error: `创建学习计划失败: ${error.message}`
      };
    }
  }
}

export default new DialectService();
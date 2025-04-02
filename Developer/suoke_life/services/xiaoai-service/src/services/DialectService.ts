import axios from 'axios';
import { Logger } from '../utils/logger';
import { DialectType, DialectDetection, DialectTranslation, RegionalDialect, TTSDialectParams } from '../types';

const logger = new Logger('DialectService');

export class DialectService {
  private apiUrl: string;
  private modelUrl: string;
  private detectionEnabled: boolean;
  private defaultDialect: DialectType;

  constructor() {
    this.apiUrl = process.env.DIALECT_API_URL || 'http://dialect-service:3070';
    this.modelUrl = process.env.DIALECT_MODEL_URL || 'http://model-service:3100/dialect';
    this.detectionEnabled = process.env.DIALECT_DETECTION_ENABLED === 'true';
    this.defaultDialect = (process.env.DIALECT_DEFAULT as DialectType) || DialectType.MANDARIN;
  }

  /**
   * 获取支持的方言列表
   */
  public async getSupportedDialects(): Promise<DialectType[]> {
    try {
      const response = await axios.get(`${this.apiUrl}/supported`);
      return response.data.dialects;
    } catch (error) {
      logger.error('获取支持的方言列表失败', { error });
      // 返回硬编码的基本方言列表作为备用
      return [
        DialectType.MANDARIN,
        DialectType.CANTONESE,
        DialectType.SHANGHAINESE,
        DialectType.SICHUANESE,
        DialectType.NORTHEASTERN
      ];
    }
  }

  /**
   * 检测文本使用的方言
   * @param text 需要检测的文本
   */
  public async detectDialect(text: string): Promise<DialectDetection> {
    if (!this.detectionEnabled) {
      return {
        text,
        detectedDialect: this.defaultDialect,
        confidence: 1.0
      };
    }

    try {
      const response = await axios.post(`${this.modelUrl}/detect`, { text });
      return response.data;
    } catch (error) {
      logger.error('方言检测失败', { error, text });
      return {
        text,
        detectedDialect: this.defaultDialect,
        confidence: 0.5
      };
    }
  }

  /**
   * 将文本翻译成指定方言
   * @param text 原始文本
   * @param targetDialect 目标方言
   */
  public async translateToDialect(
    text: string,
    targetDialect: DialectType
  ): Promise<DialectTranslation> {
    // 如果已经是目标方言，直接返回
    if (targetDialect === DialectType.MANDARIN) {
      return {
        original: text,
        translated: text,
        targetDialect,
        confidence: 1.0
      };
    }

    try {
      const response = await axios.post(`${this.modelUrl}/translate`, {
        text,
        targetDialect
      });
      return response.data;
    } catch (error) {
      logger.error('方言翻译失败', { error, text, targetDialect });
      return {
        original: text,
        translated: text, // 出错时返回原文
        targetDialect,
        confidence: 0
      };
    }
  }

  /**
   * 将方言文本转换为普通话
   * @param text 方言文本
   * @param sourceDialect 源方言类型
   */
  public async translateToMandarin(
    text: string,
    sourceDialect: DialectType
  ): Promise<DialectTranslation> {
    // 如果已经是普通话，直接返回
    if (sourceDialect === DialectType.MANDARIN) {
      return {
        original: text,
        translated: text,
        targetDialect: DialectType.MANDARIN,
        confidence: 1.0
      };
    }

    try {
      const response = await axios.post(`${this.modelUrl}/to-mandarin`, {
        text,
        sourceDialect
      });
      return response.data;
    } catch (error) {
      logger.error('方言转普通话失败', { error, text, sourceDialect });
      return {
        original: text,
        translated: text, // 出错时返回原文
        targetDialect: DialectType.MANDARIN,
        confidence: 0
      };
    }
  }

  /**
   * 根据地区获取推荐方言
   * @param region 地区名称
   */
  public async getDialectsByRegion(region: string): Promise<RegionalDialect[]> {
    try {
      const response = await axios.get(`${this.apiUrl}/region/${region}`);
      return response.data.dialects;
    } catch (error) {
      logger.error('获取地区方言推荐失败', { error, region });
      // 返回一个基于区域的简单推荐
      const defaultRecommendation: RegionalDialect = {
        region,
        primaryDialect: this.getDefaultDialectForRegion(region),
        secondaryDialects: [DialectType.MANDARIN],
        description: `${region}地区常用方言`,
        popularityRank: 1
      };
      return [defaultRecommendation];
    }
  }

  /**
   * 获取方言对应的TTS参数
   * @param dialect 方言类型
   */
  public getTTSParamsForDialect(dialect: DialectType): TTSDialectParams {
    switch (dialect) {
      case DialectType.CANTONESE:
        return {
          voice: 'cantonese-female-1',
          rate: 1.0,
          pitch: 1.0
        };
      case DialectType.SHANGHAINESE:
        return {
          voice: 'shanghai-female-1',
          rate: 1.1,
          pitch: 1.0
        };
      case DialectType.SICHUANESE:
        return {
          voice: 'sichuan-female-1',
          rate: 0.9,
          pitch: 1.0
        };
      case DialectType.NORTHEASTERN:
        return {
          voice: 'dongbei-male-1',
          rate: 1.0,
          pitch: 0.9
        };
      case DialectType.HAKKA:
        return {
          voice: 'hakka-female-1',
          rate: 1.0,
          pitch: 1.0
        };
      case DialectType.MIN:
        return {
          voice: 'minnan-male-1',
          rate: 1.0,
          pitch: 1.0
        };
      case DialectType.XIANG:
        return {
          voice: 'hunan-female-1',
          rate: 1.0,
          pitch: 1.0
        };
      case DialectType.GAN:
        return {
          voice: 'jiangxi-male-1',
          rate: 1.0,
          pitch: 1.0
        };
      default:
        return {
          voice: 'mandarin-female-1',
          rate: 1.0,
          pitch: 1.0
        };
    }
  }

  /**
   * 根据地区获取默认方言
   * @param region 地区名称
   */
  private getDefaultDialectForRegion(region: string): DialectType {
    const regionMap: Record<string, DialectType> = {
      '广东': DialectType.CANTONESE,
      '广州': DialectType.CANTONESE,
      '深圳': DialectType.CANTONESE,
      '香港': DialectType.CANTONESE,
      '澳门': DialectType.CANTONESE,
      '上海': DialectType.SHANGHAINESE,
      '江苏': DialectType.SHANGHAINESE,
      '浙江': DialectType.SHANGHAINESE,
      '四川': DialectType.SICHUANESE,
      '重庆': DialectType.SICHUANESE,
      '东北': DialectType.NORTHEASTERN,
      '黑龙江': DialectType.NORTHEASTERN,
      '吉林': DialectType.NORTHEASTERN,
      '辽宁': DialectType.NORTHEASTERN,
      '福建': DialectType.MIN,
      '厦门': DialectType.MIN,
      '台湾': DialectType.MIN,
      '湖南': DialectType.XIANG,
      '长沙': DialectType.XIANG,
      '江西': DialectType.GAN,
      '南昌': DialectType.GAN,
      '客家': DialectType.HAKKA
    };

    return regionMap[region] || this.defaultDialect;
  }
}
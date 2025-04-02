import axios from 'axios';
import { Logger } from '../utils/logger';
import { DialectService } from './DialectService';
import { DialectType } from '../types';

const logger = new Logger('VoiceGuidanceService');

// 引入方言服务
const dialectService = new DialectService();

/**
 * 语音引导接口
 */
interface VoiceGuidanceOptions {
  text: string;
  speed: number;
  language: string;
  dialect?: DialectType;
  voiceType?: 'female' | 'male';
  emphasis?: 'normal' | 'strong';
  format?: 'mp3' | 'wav' | 'ogg';
}

/**
 * 语音引导服务 - 为特殊需求用户提供语音引导
 */
export class VoiceGuidanceService {
  private ttsServiceUrl: string;
  private dialectService: DialectService;
  
  constructor() {
    this.ttsServiceUrl = process.env.TTS_SERVICE_URL || 'http://tts-service:3060';
    this.dialectService = new DialectService();
    logger.info('语音引导服务已初始化');
  }
  
  /**
   * 生成语音引导
   * @param text 需要转换为语音的文本
   * @param speed 语音速度
   * @param volume 音量大小(0-100)
   * @param dialect 方言类型
   * @returns 语音文件URL
   */
  public async generateVoiceGuidance(
    text: string,
    speed: number = 1.0,
    volume: number = 80,
    dialect: DialectType = DialectType.MANDARIN
  ): Promise<string> {
    try {
      // 获取方言对应的TTS参数
      const dialectParams = this.dialectService.getTTSParamsForDialect(dialect);
      
      // 如果不是普通话，需要先翻译成方言
      let guidanceText = text;
      if (dialect !== DialectType.MANDARIN) {
        try {
          const translation = await this.dialectService.translateToDialect(text, dialect);
          if (translation.confidence > 0.6) {
            guidanceText = translation.translated;
          }
        } catch (error) {
          logger.warn('方言翻译失败，将使用原始文本', { error, text, dialect });
        }
      }

      const response = await axios.post(`${this.ttsServiceUrl}/generate`, {
        text: guidanceText,
        speed: speed,
        volume: volume,
        voice: dialectParams.voice,
        style: dialectParams.style,
        pitch: dialectParams.pitch
      });

      return response.data.audioUrl;
    } catch (error) {
      logger.error('生成语音引导失败', { error, text });
      throw new Error(`语音生成失败: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  /**
   * 为导盲用户生成特殊引导
   */
  public async generateBlindGuidance(
    text: string,
    speed: number = 0.9,
    volume: number = 90,
    dialect: DialectType = DialectType.MANDARIN
  ): Promise<string> {
    // 为盲人用户优化的文本
    const optimizedText = this.optimizeForBlindUsers(text);
    return this.generateVoiceGuidance(optimizedText, speed, volume, dialect);
  }
  
  /**
   * 生成分步骤引导语音
   * @param steps 步骤文本数组
   * @param speed 语音速度
   * @param volume 音量大小(0-100)
   * @param dialect 方言类型
   * @returns 语音文件URL数组
   */
  public async generateStepByStepGuidance(
    steps: string[],
    speed: number = 0.9,
    volume: number = 80,
    dialect: DialectType = DialectType.MANDARIN
  ): Promise<string[]> {
    const audioUrls: string[] = [];

    for (let i = 0; i < steps.length; i++) {
      const stepText = `第${i + 1}步：${steps[i]}`;
      try {
        const audioUrl = await this.generateVoiceGuidance(stepText, speed, volume, dialect);
        audioUrls.push(audioUrl);
      } catch (error) {
        logger.error(`生成第${i + 1}步语音引导失败`, { error, step: stepText });
        // 继续生成其他步骤，不中断整个过程
      }
    }

    return audioUrls;
  }
  
  /**
   * 为盲人用户优化文本
   * @param text 原始文本
   * @returns 优化后的文本
   */
  private optimizeForBlindUsers(text: string): string {
    // 为盲人用户添加更详细的描述
    let optimized = text;

    // 替换可能不清晰的指向性词语
    optimized = optimized.replace(/点击这里/g, '点击屏幕下方按钮');
    optimized = optimized.replace(/点此/g, '点击屏幕中央按钮');
    optimized = optimized.replace(/如图所示/g, '');

    // 添加更明确的方向指示
    optimized = optimized.replace(/向左/g, '向屏幕左侧');
    optimized = optimized.replace(/向右/g, '向屏幕右侧');

    // 添加语音引导前缀
    if (!optimized.startsWith('语音引导：')) {
      optimized = `语音引导：${optimized}`;
    }

    return optimized;
  }
  
  /**
   * 优化文本使其更适合语音播报
   */
  private optimizeTextForSpeech(text: string): string {
    let optimizedText = text;
    
    // 替换常见缩写和特殊符号
    const replacements: Record<string, string> = {
      'AI': '人工智能',
      'APP': '应用',
      'TCM': '中医',
      '...': '，等等',
      '——': '，',
      '/': '或',
      '&': '和',
      '+': '加',
      '%': '百分之',
      '<=': '小于等于',
      '>=': '大于等于',
      '<': '小于',
      '>': '大于',
      '=': '等于',
      '#': '号',
    };
    
    Object.entries(replacements).forEach(([symbol, replacement]) => {
      optimizedText = optimizedText.replace(new RegExp(symbol, 'g'), replacement);
    });
    
    // 处理数字，使其更易于理解
    optimizedText = optimizedText.replace(/(\d+)\.(\d+)/g, '$1点$2'); // 小数点
    optimizedText = optimizedText.replace(/(\d{4})(\d{4})/g, '$1，$2'); // 分隔长数字
    
    // 增加逗号，使语音更自然
    optimizedText = optimizedText.replace(/([，。！？；])\s*/g, '$1');
    optimizedText = optimizedText.replace(/([^，。！？；]){15,}([，。！？；])/g, '$1，$2');
    
    return optimizedText;
  }
  
  /**
   * 获取特定操作的引导说明
   */
  private getActionGuidance(action: string, context: any): string {
    // 针对特定操作提供详细引导
    switch (action) {
      case '拍照':
        return '双击屏幕中央，相机将自动拍摄照片';
        
      case '语音输入':
        return '长按屏幕底部中央的麦克风按钮，开始说话，松开结束输入';
        
      case '返回':
        return '向右滑动屏幕边缘或双击屏幕左上角';
        
      case '滚动':
        return '用两个手指在屏幕上向上或向下滑动';
        
      default:
        // 根据上下文提供默认引导
        if (context.elements && context.elements.length > 0) {
          // 查找与操作相关的元素
          const relevantElement = context.elements.find((e: any) => 
            e.action && e.action.toLowerCase() === action.toLowerCase()
          );
          
          if (relevantElement) {
            return `找到位于屏幕${relevantElement.position}的${relevantElement.type}，并点击它`;
          }
        }
        
        return '按照语音提示完成操作';
    }
  }
}
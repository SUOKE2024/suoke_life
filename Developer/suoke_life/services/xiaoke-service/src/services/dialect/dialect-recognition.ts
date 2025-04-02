import { v4 as uuidv4 } from 'uuid';
import { logger } from '../../utils/logger';

// 支持的方言列表
export enum ChineseDialect {
  MANDARIN = 'mandarin',   // 普通话
  CANTONESE = 'cantonese', // 粤语
  SHANGHAINESE = 'shanghainese', // 上海话
  HAKKA = 'hakka',         // 客家话
  HOKKIEN = 'hokkien',     // 闽南语
  SICHUANESE = 'sichuanese', // 四川话
  NORTHEASTERN = 'northeastern', // 东北话
  HENAN = 'henan',         // 河南话
  HUBEI = 'hubei',         // 湖北话
  XIANG = 'xiang',         // 湘语
  GAN = 'gan',             // 赣语
  JINYU = 'jinyu',         // 晋语
  OTHER = 'other'          // 其他方言
}

// 方言识别结果
export interface DialectRecognitionResult {
  id: string;
  userId: string;
  timestamp: string;
  audioId?: string;
  text: string;
  detectedDialect: ChineseDialect;
  confidence: number;
  standardMandarinText?: string;
  alternativeDialects?: {
    dialect: ChineseDialect;
    confidence: number;
  }[];
  metadata?: Record<string, any>;
}

// 方言识别历史
const dialectRecognitionStore: DialectRecognitionResult[] = [];

// 用户方言偏好
const userDialectPreferences: Record<string, {
  preferredDialect: ChineseDialect;
  enableTranslation: boolean;
}> = {};

/**
 * 获取用户方言偏好
 */
export const getUserDialectPreference = (userId: string): { preferredDialect: ChineseDialect, enableTranslation: boolean } => {
  return userDialectPreferences[userId] || {
    preferredDialect: ChineseDialect.MANDARIN,
    enableTranslation: true
  };
};

/**
 * 更新用户方言偏好
 */
export const updateUserDialectPreference = (
  userId: string, 
  preferences: { preferredDialect?: ChineseDialect, enableTranslation?: boolean }
): { preferredDialect: ChineseDialect, enableTranslation: boolean } => {
  const currentPreferences = getUserDialectPreference(userId);
  
  userDialectPreferences[userId] = {
    ...currentPreferences,
    ...preferences
  };
  
  logger.info(`用户方言偏好已更新: ${userId}`);
  return userDialectPreferences[userId];
};

/**
 * 识别文本中的方言
 * 此函数模拟方言识别过程，实际应用中应该调用专业的NLP服务
 */
export const recognizeDialect = async (
  text: string, 
  userId: string,
  audioId?: string
): Promise<DialectRecognitionResult> => {
  try {
    logger.info(`识别方言: "${text.substring(0, 20)}..."`);
    
    // 这里是模拟实现，实际应用中应该调用专业的NLP服务
    const detectedDialect = simulateDialectDetection(text);
    
    // 转换为标准普通话（模拟）
    const standardText = await translateToMandarin(text, detectedDialect.dialect);
    
    const result: DialectRecognitionResult = {
      id: uuidv4(),
      userId,
      timestamp: new Date().toISOString(),
      audioId,
      text,
      detectedDialect: detectedDialect.dialect,
      confidence: detectedDialect.confidence,
      standardMandarinText: standardText,
      alternativeDialects: detectedDialect.alternatives
    };
    
    // 保存识别结果
    dialectRecognitionStore.push(result);
    
    logger.info(`方言识别完成: ${result.detectedDialect}, 置信度: ${result.confidence}`);
    return result;
  } catch (error) {
    logger.error('方言识别失败:', error);
    throw new Error(`方言识别失败: ${(error as Error).message}`);
  }
};

/**
 * 将方言文本转换为标准普通话
 * 此函数模拟转换过程，实际应用中应该调用专业的NLP服务
 */
export const translateToMandarin = async (
  text: string,
  sourceDialect: ChineseDialect
): Promise<string> => {
  try {
    if (sourceDialect === ChineseDialect.MANDARIN) {
      return text; // 已经是普通话
    }
    
    // 这里是模拟实现，实际应用中应该调用专业的NLP服务
    // 简单替换一些常见方言词汇（示例）
    let translatedText = text;
    
    switch (sourceDialect) {
      case ChineseDialect.CANTONESE:
        translatedText = text
          .replace(/冇/g, "没有")
          .replace(/嘅/g, "的")
          .replace(/咩/g, "什么")
          .replace(/點解/g, "为什么");
        break;
      case ChineseDialect.SICHUANESE:
        translatedText = text
          .replace(/安逸/g, "舒服")
          .replace(/巴适/g, "好")
          .replace(/造孽/g, "糟糕");
        break;
      case ChineseDialect.NORTHEASTERN:
        translatedText = text
          .replace(/咋整/g, "怎么办")
          .replace(/杠啥/g, "干什么")
          .replace(/嘎哈/g, "干什么");
        break;
      // 其他方言转换规则...
    }
    
    logger.info(`方言转换完成: ${sourceDialect} -> 普通话`);
    return translatedText;
  } catch (error) {
    logger.error('方言转换失败:', error);
    throw new Error(`方言转换失败: ${(error as Error).message}`);
  }
};

/**
 * 获取用户的方言识别历史
 */
export const getUserDialectHistory = (userId: string, limit: number = 20): DialectRecognitionResult[] => {
  return dialectRecognitionStore
    .filter(result => result.userId === userId)
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, limit);
};

/**
 * 模拟方言检测过程
 * 实际应用中应该调用专业的NLP服务
 */
const simulateDialectDetection = (text: string): {
  dialect: ChineseDialect;
  confidence: number;
  alternatives: { dialect: ChineseDialect; confidence: number }[];
} => {
  // 粤语特征词
  const cantonesePatterns = /冇|嘅|咩|點解|唔|睇|乜|喺|嘢|係|啲|嗰|喇|咁|咗|俾|嚟|嘥|攞|畀/;
  
  // 四川话特征词
  const sichuanesePatterns = /安逸|巴适|造孽|倒霉|要得|莫得|晓得|咋|龙门阵|害怕/;
  
  // 东北话特征词
  const northeasternPatterns = /啥|咋整|杠啥|嘎哈|咋地|得劲|玩儿|整一个|老幺|嘞/;
  
  // 上海话特征词
  const shanghainesePatterns = /勿|伐|垃|辣|宁|么|何|来|去|好/;
  
  // 检测文本中的方言特征
  let detectedDialect: ChineseDialect = ChineseDialect.MANDARIN;
  let confidence = 0.6; // 默认置信度
  let alternatives: { dialect: ChineseDialect; confidence: number }[] = [];
  
  if (cantonesePatterns.test(text)) {
    detectedDialect = ChineseDialect.CANTONESE;
    confidence = 0.8 + Math.random() * 0.2;
    alternatives.push({ 
      dialect: ChineseDialect.MANDARIN, 
      confidence: 1 - confidence 
    });
  } else if (sichuanesePatterns.test(text)) {
    detectedDialect = ChineseDialect.SICHUANESE;
    confidence = 0.75 + Math.random() * 0.2;
    alternatives.push({ 
      dialect: ChineseDialect.MANDARIN, 
      confidence: 1 - confidence 
    });
  } else if (northeasternPatterns.test(text)) {
    detectedDialect = ChineseDialect.NORTHEASTERN;
    confidence = 0.7 + Math.random() * 0.2;
    alternatives.push({ 
      dialect: ChineseDialect.MANDARIN, 
      confidence: 1 - confidence 
    });
  } else if (shanghainesePatterns.test(text)) {
    detectedDialect = ChineseDialect.SHANGHAINESE;
    confidence = 0.65 + Math.random() * 0.2;
    alternatives.push({ 
      dialect: ChineseDialect.MANDARIN, 
      confidence: 1 - confidence 
    });
  } else {
    // 默认为普通话
    alternatives.push({ 
      dialect: ChineseDialect.NORTHEASTERN, 
      confidence: 0.15 
    }, { 
      dialect: ChineseDialect.SICHUANESE, 
      confidence: 0.10 
    });
  }
  
  return {
    dialect: detectedDialect,
    confidence,
    alternatives
  };
};
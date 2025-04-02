import { DialectModel, IDialect } from '../../models/dialect.model';
import logger from '../../core/utils/logger';
import { ApiError } from '../../core/utils/errors';
import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import os from 'os';

/**
 * 获取所有方言
 */
export const getAllDialects = async (activeOnly = true) => {
  try {
    const query = activeOnly ? { isActive: true } : {};
    const dialects = await DialectModel.find(query).sort({ region: 1, name: 1 }).lean();
    return dialects;
  } catch (error) {
    logger.error('获取方言列表失败:', error);
    throw new ApiError(500, '获取方言列表失败');
  }
};

/**
 * 按地区分组获取方言
 */
export const getDialectsByRegion = async (activeOnly = true) => {
  try {
    const query = activeOnly ? { isActive: true } : {};
    const dialects = await DialectModel.find(query).sort({ region: 1, name: 1 }).lean();
    
    // 按地区分组
    const dialectsByRegion: Record<string, IDialect[]> = {};
    
    dialects.forEach(dialect => {
      if (!dialectsByRegion[dialect.region]) {
        dialectsByRegion[dialect.region] = [];
      }
      dialectsByRegion[dialect.region].push(dialect);
    });
    
    return dialectsByRegion;
  } catch (error) {
    logger.error('按地区获取方言列表失败:', error);
    throw new ApiError(500, '按地区获取方言列表失败');
  }
};

/**
 * 获取方言详情
 */
export const getDialectByCode = async (code: string) => {
  try {
    const dialect = await DialectModel.findOne({ code }).lean();
    if (!dialect) {
      throw new ApiError(404, `未找到代码为 ${code} 的方言`);
    }
    return dialect;
  } catch (error) {
    logger.error(`获取方言详情失败 [代码: ${code}]:`, error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '获取方言详情失败');
  }
};

/**
 * 创建方言
 */
export const createDialect = async (dialectData: Partial<IDialect>) => {
  try {
    // 检查方言代码是否已存在
    const existingDialect = await DialectModel.findOne({ code: dialectData.code });
    if (existingDialect) {
      throw new ApiError(400, `方言代码 ${dialectData.code} 已存在`);
    }
    
    const dialect = new DialectModel({
      ...dialectData,
      createdAt: new Date(),
      updatedAt: new Date()
    });
    
    await dialect.save();
    return dialect.toObject();
  } catch (error) {
    logger.error('创建方言失败:', error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '创建方言失败');
  }
};

/**
 * 更新方言
 */
export const updateDialect = async (code: string, dialectData: Partial<IDialect>) => {
  try {
    const dialect = await DialectModel.findOne({ code });
    if (!dialect) {
      throw new ApiError(404, `未找到代码为 ${code} 的方言`);
    }
    
    // 更新字段
    Object.assign(dialect, {
      ...dialectData,
      updatedAt: new Date()
    });
    
    await dialect.save();
    return dialect.toObject();
  } catch (error) {
    logger.error(`更新方言失败 [代码: ${code}]:`, error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '更新方言失败');
  }
};

/**
 * 删除方言
 */
export const deleteDialect = async (code: string) => {
  try {
    const result = await DialectModel.deleteOne({ code });
    if (result.deletedCount === 0) {
      throw new ApiError(404, `未找到代码为 ${code} 的方言`);
    }
    return { success: true, message: `已删除代码为 ${code} 的方言` };
  } catch (error) {
    logger.error(`删除方言失败 [代码: ${code}]:`, error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '删除方言失败');
  }
};

/**
 * 检测音频中的方言
 */
export const detectDialect = async (audioBuffer: Buffer, mimeType: string) => {
  try {
    // 保存临时文件
    const tempDir = os.tmpdir();
    const tempFilePath = path.join(tempDir, `dialect-detect-${uuidv4()}.audio`);
    
    try {
      fs.writeFileSync(tempFilePath, audioBuffer);
      
      // 调用方言识别服务
      const formData = new FormData();
      formData.append('audio', new Blob([audioBuffer], { type: mimeType }));
      
      const response = await axios.post(
        `${process.env.DIALECT_SERVICE_URL}/detect`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      // 清理临时文件
      fs.unlinkSync(tempFilePath);
      
      if (!response.data || !response.data.detected) {
        return {
          success: false,
          message: '无法识别方言',
          confidence: 0,
        };
      }
      
      // 获取检测到的方言详情
      const detectedDialect = await DialectModel.findOne({
        code: response.data.dialectCode,
      }).lean();
      
      return {
        success: true,
        detected: true,
        dialect: detectedDialect || { code: response.data.dialectCode },
        confidence: response.data.confidence,
        alternatives: response.data.alternatives || [],
      };
    } finally {
      // 确保临时文件被删除
      if (fs.existsSync(tempFilePath)) {
        fs.unlinkSync(tempFilePath);
      }
    }
  } catch (error) {
    logger.error('检测方言失败:', error);
    throw new ApiError(500, '检测方言失败');
  }
};

/**
 * 转换方言到标准普通话
 */
export const translateDialectToStandard = async (
  audioBuffer: Buffer,
  mimeType: string,
  sourceDialectCode?: string
) => {
  try {
    // 保存临时文件
    const tempDir = os.tmpdir();
    const tempFilePath = path.join(tempDir, `dialect-translate-${uuidv4()}.audio`);
    
    try {
      fs.writeFileSync(tempFilePath, audioBuffer);
      
      // 调用方言转换服务
      const formData = new FormData();
      formData.append('audio', new Blob([audioBuffer], { type: mimeType }));
      
      if (sourceDialectCode) {
        formData.append('dialectCode', sourceDialectCode);
      }
      
      const response = await axios.post(
        `${process.env.DIALECT_SERVICE_URL}/translate`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          responseType: 'arraybuffer',
        }
      );
      
      // 清理临时文件
      fs.unlinkSync(tempFilePath);
      
      // 提取结果和元数据
      const resultBuffer = Buffer.from(response.data);
      const metadataHeader = response.headers['x-translation-metadata'];
      let metadata = {};
      
      if (metadataHeader) {
        try {
          metadata = JSON.parse(metadataHeader);
        } catch (error) {
          logger.warn('解析转换元数据失败:', error);
        }
      }
      
      return {
        success: true,
        audio: resultBuffer,
        mimeType: response.headers['content-type'] || 'audio/wav',
        metadata,
      };
    } finally {
      // 确保临时文件被删除
      if (fs.existsSync(tempFilePath)) {
        fs.unlinkSync(tempFilePath);
      }
    }
  } catch (error) {
    logger.error('转换方言失败:', error);
    throw new ApiError(500, '转换方言失败');
  }
};

/**
 * 初始化默认方言数据
 */
export const initializeDefaultDialects = async () => {
  try {
    // 检查是否已有方言数据
    const count = await DialectModel.countDocuments();
    if (count > 0) {
      return { 
        success: true, 
        message: '方言数据已存在，跳过初始化', 
        count 
      };
    }
    
    // 默认方言数据
    const defaultDialects = [
      {
        code: 'mandarin',
        name: '普通话',
        region: '全国通用',
        description: '中国大陆官方语言，基于北京方言',
        isActive: true,
        supportLevel: 'full',
        features: ['recognition', 'synthesis', 'translation'],
        accuracy: 98
      },
      {
        code: 'cantonese',
        name: '粤语',
        region: '广东、香港、澳门',
        description: '广东地区使用的汉语方言，是汉藏语系汉语族粤语支的一种',
        isActive: true,
        supportLevel: 'full',
        features: ['recognition', 'synthesis', 'translation'],
        accuracy: 92
      },
      {
        code: 'shanghainese',
        name: '上海话',
        region: '上海',
        description: '上海地区使用的汉语方言，属于吴语',
        isActive: true,
        supportLevel: 'partial',
        features: ['recognition', 'translation'],
        accuracy: 85
      },
      {
        code: 'sichuanese',
        name: '四川话',
        region: '四川、重庆',
        description: '四川、重庆地区使用的汉语方言，属于西南官话',
        isActive: true,
        supportLevel: 'partial',
        features: ['recognition', 'translation'],
        accuracy: 82
      },
      {
        code: 'northeast',
        name: '东北话',
        region: '黑龙江、吉林、辽宁',
        description: '中国东北地区使用的汉语方言，属于北方方言',
        isActive: true,
        supportLevel: 'partial',
        features: ['recognition', 'translation'],
        accuracy: 90
      },
      {
        code: 'hakka',
        name: '客家话',
        region: '广东、福建、江西等',
        description: '分布于中国南方多个省份的汉语方言',
        isActive: true,
        supportLevel: 'basic',
        features: ['recognition'],
        accuracy: 75
      },
      {
        code: 'xiang',
        name: '湘语',
        region: '湖南',
        description: '湖南省使用的汉语方言',
        isActive: true,
        supportLevel: 'basic',
        features: ['recognition'],
        accuracy: 70
      },
      {
        code: 'min',
        name: '闽语',
        region: '福建、台湾',
        description: '福建、台湾等地使用的汉语方言',
        isActive: true,
        supportLevel: 'basic',
        features: ['recognition'],
        accuracy: 72
      }
    ];
    
    // 批量插入
    await DialectModel.insertMany(defaultDialects);
    
    return { 
      success: true, 
      message: '方言数据初始化成功', 
      count: defaultDialects.length 
    };
  } catch (error) {
    logger.error('初始化默认方言数据失败:', error);
    throw new ApiError(500, '初始化默认方言数据失败');
  }
}; 
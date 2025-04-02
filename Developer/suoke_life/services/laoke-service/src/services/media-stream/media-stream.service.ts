import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import { 
  MediaStreamModel, 
  IMediaStream, 
  MediaStreamType, 
  MediaStreamStatus,
  MediaProcessingType
} from '../../models/media-stream.model';
import logger from '../../core/utils/logger';
import { ApiError } from '../../core/utils/errors';
import config from '../../core/config';
import mongoose from 'mongoose';

// 媒体文件存储路径
const MEDIA_STORAGE_PATH = path.join(process.cwd(), 'uploads', 'media');

// 确保媒体存储目录存在
if (!fs.existsSync(MEDIA_STORAGE_PATH)) {
  fs.mkdirSync(MEDIA_STORAGE_PATH, { recursive: true });
}

/**
 * 创建媒体流记录
 */
export const createMediaStream = async (
  userId: string,
  file: Express.Multer.File,
  processingType: MediaProcessingType,
  metadata: Record<string, any> = {}
): Promise<IMediaStream> => {
  try {
    // 确定媒体类型
    let streamType: MediaStreamType;
    if (file.mimetype.startsWith('audio/')) {
      streamType = MediaStreamType.AUDIO;
    } else if (file.mimetype.startsWith('video/')) {
      streamType = MediaStreamType.VIDEO;
    } else if (file.mimetype.startsWith('image/')) {
      streamType = MediaStreamType.IMAGE;
    } else {
      throw new ApiError(400, '不支持的媒体类型');
    }

    // 保存媒体文件到永久存储位置
    const fileExtension = path.extname(file.originalname);
    const fileName = `${uuidv4()}${fileExtension}`;
    const filePath = path.join(MEDIA_STORAGE_PATH, fileName);
    
    fs.copyFileSync(file.path, filePath);
    
    // 创建媒体流记录
    const mediaStream = new MediaStreamModel({
      userId: new mongoose.Types.ObjectId(userId),
      streamType,
      processingType,
      originalName: file.originalname,
      fileSize: file.size,
      mimeType: file.mimetype,
      filePath: filePath,
      status: MediaStreamStatus.PENDING,
      processingMetadata: metadata
    });

    await mediaStream.save();
    return mediaStream;
  } catch (error) {
    logger.error('创建媒体流记录失败:', error);
    throw error;
  }
};

/**
 * 获取用户的媒体流记录
 */
export const getUserMediaStreams = async (
  userId: string,
  limit: number = 20,
  skip: number = 0,
  filters: Record<string, any> = {}
): Promise<{ total: number; records: IMediaStream[] }> => {
  try {
    const query = { userId: new mongoose.Types.ObjectId(userId), ...filters };
    
    const total = await MediaStreamModel.countDocuments(query);
    const records = await MediaStreamModel.find(query)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);
    
    return { total, records };
  } catch (error) {
    logger.error('获取用户媒体流记录失败:', error);
    throw error;
  }
};

/**
 * 获取媒体流详情
 */
export const getMediaStreamById = async (
  mediaStreamId: string
): Promise<IMediaStream> => {
  try {
    const mediaStream = await MediaStreamModel.findById(mediaStreamId);
    
    if (!mediaStream) {
      throw new ApiError(404, '未找到媒体流记录');
    }
    
    return mediaStream;
  } catch (error) {
    logger.error(`获取媒体流详情失败 [ID: ${mediaStreamId}]:`, error);
    throw error;
  }
};

/**
 * 更新媒体流处理状态
 */
export const updateMediaStreamStatus = async (
  mediaStreamId: string,
  status: MediaStreamStatus,
  result?: Record<string, any>,
  errorMessage?: string
): Promise<IMediaStream> => {
  try {
    const mediaStream = await MediaStreamModel.findById(mediaStreamId);
    
    if (!mediaStream) {
      throw new ApiError(404, '未找到媒体流记录');
    }
    
    // 更新状态
    mediaStream.status = status;
    
    // 如果是开始处理状态
    if (status === MediaStreamStatus.PROCESSING && !mediaStream.processingStartTime) {
      mediaStream.processingStartTime = new Date();
    }
    
    // 如果是完成或失败状态
    if (status === MediaStreamStatus.COMPLETED || status === MediaStreamStatus.FAILED) {
      mediaStream.processingEndTime = new Date();
      
      if (mediaStream.processingStartTime) {
        const processingDuration = mediaStream.processingEndTime.getTime() - 
          mediaStream.processingStartTime.getTime();
        mediaStream.processingDuration = processingDuration;
      }
      
      if (result) {
        mediaStream.processingResult = result;
      }
      
      if (errorMessage) {
        mediaStream.errorMessage = errorMessage;
      }
    }
    
    await mediaStream.save();
    return mediaStream;
  } catch (error) {
    logger.error(`更新媒体流状态失败 [ID: ${mediaStreamId}]:`, error);
    throw error;
  }
};

/**
 * 处理音频文件 - 方言检测
 */
export const processDialectDetection = async (
  mediaStreamId: string
): Promise<IMediaStream> => {
  try {
    const mediaStream = await getMediaStreamById(mediaStreamId);
    
    if (mediaStream.streamType !== MediaStreamType.AUDIO) {
      throw new ApiError(400, '方言检测仅支持音频文件');
    }
    
    if (mediaStream.processingType !== MediaProcessingType.DIALECT_DETECTION) {
      throw new ApiError(400, '媒体流处理类型不匹配');
    }
    
    // 更新为处理中状态
    await updateMediaStreamStatus(mediaStreamId, MediaStreamStatus.PROCESSING);
    
    try {
      // 读取音频文件
      const audioBuffer = fs.readFileSync(mediaStream.filePath);
      
      // 调用方言检测AI服务
      const response = await axios.post(
        `${config.aiServices.dialectDetection}/detect`,
        audioBuffer,
        {
          headers: {
            'Content-Type': mediaStream.mimeType,
            'X-API-Key': config.aiServices.apiKey
          },
          maxBodyLength: Infinity,
          timeout: 30000 // 30秒超时
        }
      );
      
      // 更新为完成状态并保存结果
      return await updateMediaStreamStatus(
        mediaStreamId, 
        MediaStreamStatus.COMPLETED,
        response.data
      );
    } catch (processingError) {
      logger.error('方言检测处理失败:', processingError);
      
      // 更新为失败状态
      return await updateMediaStreamStatus(
        mediaStreamId,
        MediaStreamStatus.FAILED,
        undefined,
        processingError.message || '方言检测处理失败'
      );
    }
  } catch (error) {
    logger.error(`方言检测处理失败 [ID: ${mediaStreamId}]:`, error);
    throw error;
  }
};

/**
 * 处理音频文件 - 方言翻译
 */
export const processDialectTranslation = async (
  mediaStreamId: string,
  dialectCode: string
): Promise<IMediaStream> => {
  try {
    const mediaStream = await getMediaStreamById(mediaStreamId);
    
    if (mediaStream.streamType !== MediaStreamType.AUDIO) {
      throw new ApiError(400, '方言翻译仅支持音频文件');
    }
    
    if (mediaStream.processingType !== MediaProcessingType.DIALECT_TRANSLATION) {
      throw new ApiError(400, '媒体流处理类型不匹配');
    }
    
    // 更新为处理中状态
    await updateMediaStreamStatus(mediaStreamId, MediaStreamStatus.PROCESSING);
    
    try {
      // 读取音频文件
      const audioBuffer = fs.readFileSync(mediaStream.filePath);
      
      // 调用方言翻译AI服务
      const response = await axios.post(
        `${config.aiServices.dialectTranslation}/translate`,
        {
          audio: audioBuffer.toString('base64'),
          dialectCode: dialectCode
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': config.aiServices.apiKey
          },
          maxBodyLength: Infinity,
          timeout: 60000 // 60秒超时
        }
      );
      
      // 解析响应中的音频数据（Base64）
      const translatedAudioBuffer = Buffer.from(response.data.translatedAudio, 'base64');
      
      // 保存翻译后的音频文件
      const translatedFileName = `translated_${uuidv4()}.wav`;
      const translatedFilePath = path.join(MEDIA_STORAGE_PATH, translatedFileName);
      fs.writeFileSync(translatedFilePath, translatedAudioBuffer);
      
      // 更新结果
      const result = {
        ...response.data,
        translatedAudio: undefined, // 不存储Base64音频数据
        translatedFilePath: translatedFilePath
      };
      
      // 更新为完成状态并保存结果
      return await updateMediaStreamStatus(
        mediaStreamId, 
        MediaStreamStatus.COMPLETED,
        result
      );
    } catch (processingError) {
      logger.error('方言翻译处理失败:', processingError);
      
      // 更新为失败状态
      return await updateMediaStreamStatus(
        mediaStreamId,
        MediaStreamStatus.FAILED,
        undefined,
        processingError.message || '方言翻译处理失败'
      );
    }
  } catch (error) {
    logger.error(`方言翻译处理失败 [ID: ${mediaStreamId}]:`, error);
    throw error;
  }
};

/**
 * 处理音频文件 - 语音转文本
 */
export const processSpeechToText = async (
  mediaStreamId: string,
  languageCode: string = 'zh-CN'
): Promise<IMediaStream> => {
  try {
    const mediaStream = await getMediaStreamById(mediaStreamId);
    
    if (mediaStream.streamType !== MediaStreamType.AUDIO) {
      throw new ApiError(400, '语音转文本仅支持音频文件');
    }
    
    if (mediaStream.processingType !== MediaProcessingType.SPEECH_TO_TEXT) {
      throw new ApiError(400, '媒体流处理类型不匹配');
    }
    
    // 更新为处理中状态
    await updateMediaStreamStatus(mediaStreamId, MediaStreamStatus.PROCESSING);
    
    try {
      // 读取音频文件
      const audioBuffer = fs.readFileSync(mediaStream.filePath);
      
      // 调用语音转文本AI服务
      const response = await axios.post(
        `${config.aiServices.speechToText}/transcribe`,
        {
          audio: audioBuffer.toString('base64'),
          languageCode: languageCode
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': config.aiServices.apiKey
          },
          timeout: 30000 // 30秒超时
        }
      );
      
      // 更新为完成状态并保存结果
      return await updateMediaStreamStatus(
        mediaStreamId, 
        MediaStreamStatus.COMPLETED,
        response.data
      );
    } catch (processingError) {
      logger.error('语音转文本处理失败:', processingError);
      
      // 更新为失败状态
      return await updateMediaStreamStatus(
        mediaStreamId,
        MediaStreamStatus.FAILED,
        undefined,
        processingError.message || '语音转文本处理失败'
      );
    }
  } catch (error) {
    logger.error(`语音转文本处理失败 [ID: ${mediaStreamId}]:`, error);
    throw error;
  }
};

/**
 * 处理图像文件 - 图像识别
 */
export const processImageRecognition = async (
  mediaStreamId: string
): Promise<IMediaStream> => {
  try {
    const mediaStream = await getMediaStreamById(mediaStreamId);
    
    if (mediaStream.streamType !== MediaStreamType.IMAGE) {
      throw new ApiError(400, '图像识别仅支持图片文件');
    }
    
    if (mediaStream.processingType !== MediaProcessingType.IMAGE_RECOGNITION) {
      throw new ApiError(400, '媒体流处理类型不匹配');
    }
    
    // 更新为处理中状态
    await updateMediaStreamStatus(mediaStreamId, MediaStreamStatus.PROCESSING);
    
    try {
      // 读取图像文件
      const imageBuffer = fs.readFileSync(mediaStream.filePath);
      
      // 调用图像识别AI服务
      const response = await axios.post(
        `${config.aiServices.imageRecognition}/analyze`,
        imageBuffer,
        {
          headers: {
            'Content-Type': mediaStream.mimeType,
            'X-API-Key': config.aiServices.apiKey
          },
          maxBodyLength: Infinity,
          timeout: 30000 // 30秒超时
        }
      );
      
      // 更新为完成状态并保存结果
      return await updateMediaStreamStatus(
        mediaStreamId, 
        MediaStreamStatus.COMPLETED,
        response.data
      );
    } catch (processingError) {
      logger.error('图像识别处理失败:', processingError);
      
      // 更新为失败状态
      return await updateMediaStreamStatus(
        mediaStreamId,
        MediaStreamStatus.FAILED,
        undefined,
        processingError.message || '图像识别处理失败'
      );
    }
  } catch (error) {
    logger.error(`图像识别处理失败 [ID: ${mediaStreamId}]:`, error);
    throw error;
  }
};

/**
 * 获取处理结果文件
 */
export const getProcessingResultFile = async (
  mediaStreamId: string
): Promise<{ filePath: string; mimeType: string; fileName: string }> => {
  try {
    const mediaStream = await getMediaStreamById(mediaStreamId);
    
    if (mediaStream.status !== MediaStreamStatus.COMPLETED) {
      throw new ApiError(400, '媒体处理尚未完成');
    }
    
    let filePath: string;
    let fileName: string;
    
    // 根据处理类型确定结果文件
    if (mediaStream.processingType === MediaProcessingType.DIALECT_TRANSLATION) {
      // 对于方言翻译，返回翻译后的音频文件
      filePath = mediaStream.processingResult?.translatedFilePath;
      if (!filePath) {
        throw new ApiError(404, '找不到翻译后的音频文件');
      }
      fileName = `translated_${path.basename(mediaStream.originalName)}`;
    } else {
      // 对于其他类型，返回原始文件
      filePath = mediaStream.filePath;
      fileName = mediaStream.originalName;
    }
    
    // 检查文件是否存在
    if (!fs.existsSync(filePath)) {
      throw new ApiError(404, '文件不存在');
    }
    
    return { 
      filePath, 
      mimeType: mediaStream.mimeType,
      fileName
    };
  } catch (error) {
    logger.error(`获取处理结果文件失败 [ID: ${mediaStreamId}]:`, error);
    throw error;
  }
};

/**
 * 清理过期媒体文件
 */
export const cleanupExpiredMediaFiles = async (
  expirationDays: number = 7
): Promise<number> => {
  try {
    const expirationDate = new Date();
    expirationDate.setDate(expirationDate.getDate() - expirationDays);
    
    // 查找过期的媒体流记录
    const expiredStreams = await MediaStreamModel.find({
      createdAt: { $lt: expirationDate },
      status: { $in: [MediaStreamStatus.COMPLETED, MediaStreamStatus.FAILED] }
    });
    
    let deletedCount = 0;
    
    // 删除文件和记录
    for (const stream of expiredStreams) {
      try {
        // 删除原始文件
        if (stream.filePath && fs.existsSync(stream.filePath)) {
          fs.unlinkSync(stream.filePath);
        }
        
        // 删除处理结果文件 (如果有)
        if (stream.processingResult?.translatedFilePath && 
            fs.existsSync(stream.processingResult.translatedFilePath)) {
          fs.unlinkSync(stream.processingResult.translatedFilePath);
        }
        
        // 从数据库中删除记录
        await MediaStreamModel.findByIdAndDelete(stream._id);
        
        deletedCount++;
      } catch (deleteError) {
        logger.error(`删除过期媒体文件失败 [ID: ${stream._id}]:`, deleteError);
      }
    }
    
    return deletedCount;
  } catch (error) {
    logger.error('清理过期媒体文件失败:', error);
    throw error;
  }
}; 
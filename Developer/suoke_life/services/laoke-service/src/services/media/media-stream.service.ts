import { MediaStreamModel, MediaStreamType, MediaStreamStatus, IMediaStream } from '../../models/media-stream.model';
import { DialectModel } from '../../models/dialect.model';
import logger from '../../core/utils/logger';
import { ApiError } from '../../core/utils/errors';
import * as metrics from '../../core/metrics';
import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { promisify } from 'util';
import { v4 as uuidv4 } from 'uuid';

// AWS SDK用于S3存储
import AWS from 'aws-sdk';

const writeFile = promisify(fs.writeFile);
const mkdir = promisify(fs.mkdir);

// 配置S3
const s3 = new AWS.S3({
  accessKeyId: process.env.S3_ACCESS_KEY_ID || '',
  secretAccessKey: process.env.S3_SECRET_ACCESS_KEY || '',
  region: process.env.S3_REGION || 'us-west-2',
  // 为本地开发环境提供S3兼容服务端点
  ...(process.env.NODE_ENV === 'development' && process.env.S3_ENDPOINT 
    ? { endpoint: process.env.S3_ENDPOINT } 
    : {})
});

// 临时存储路径
const TEMP_STORAGE_PATH = process.env.TEMP_STORAGE_PATH || './temp';

// 确保临时目录存在
const ensureTempDirExists = async (): Promise<void> => {
  try {
    await mkdir(TEMP_STORAGE_PATH, { recursive: true });
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== 'EEXIST') {
      throw error;
    }
  }
};

/**
 * 创建新的媒体流记录
 */
export const createMediaStream = async (data: {
  userId: string;
  sessionId: string;
  streamType: MediaStreamType;
  deviceInfo?: Record<string, any>;
  dialect?: string;
  metadata?: Record<string, any>;
}): Promise<any> => {
  try {
    const mediaStream = new MediaStreamModel({
      ...data,
      status: MediaStreamStatus.ACTIVE,
      startTime: new Date(),
      metadata: data.metadata || {}
    });

    await mediaStream.save();
    
    // 更新指标
    await updateStreamMetrics();
    
    return mediaStream.toObject();
  } catch (error) {
    logger.error('创建媒体流记录错误:', error);
    throw new ApiError(500, '创建媒体流记录失败');
  }
};

/**
 * 接收并保存媒体流块
 */
export const saveMediaStreamChunk = async (
  streamId: string,
  chunk: Buffer,
  chunkIndex: number
): Promise<{ success: boolean; chunkIndex: number }> => {
  try {
    // 查找媒体流记录
    const mediaStream = await MediaStreamModel.findById(streamId);
    if (!mediaStream) {
      throw new ApiError(404, '媒体流不存在');
    }
    
    if (mediaStream.status !== MediaStreamStatus.ACTIVE) {
      throw new ApiError(400, '媒体流已完成或失败');
    }
    
    // 确保临时目录存在
    await ensureTempDirExists();
    
    // 保存块到临时文件
    const tempDir = path.join(TEMP_STORAGE_PATH, streamId);
    await mkdir(tempDir, { recursive: true });
    
    const chunkPath = path.join(tempDir, `chunk_${chunkIndex}.data`);
    await writeFile(chunkPath, chunk);
    
    // 更新媒体流记录
    mediaStream.updatedAt = new Date();
    await mediaStream.save();
    
    return { success: true, chunkIndex };
  } catch (error) {
    logger.error(`保存媒体流块错误 [ID: ${streamId}, 块索引: ${chunkIndex}]:`, error);
    throw error;
  }
};

/**
 * 完成媒体流并处理
 */
export const completeMediaStream = async (
  streamId: string,
  metadata?: Record<string, any>
): Promise<{
  success: boolean;
  streamId: string;
  status: MediaStreamStatus;
  fileUrl: string;
}> => {
  try {
    // 查找媒体流记录
    const mediaStream = await MediaStreamModel.findById(streamId);
    if (!mediaStream) {
      throw new ApiError(404, '媒体流不存在');
    }
    
    // 更新状态为处理中
    mediaStream.status = MediaStreamStatus.PROCESSING;
    if (metadata) {
      mediaStream.metadata = { ...mediaStream.metadata, ...metadata };
    }
    mediaStream.updatedAt = new Date();
    await mediaStream.save();
    
    // 处理临时文件：合并块并上传
    const processingStartTime = Date.now();
    try {
      const fileUrl = await processMediaStream(streamId, mediaStream.streamType);
      
      // 计算处理时间
      const processingTime = Date.now() - processingStartTime;
      
      // 记录AI处理指标
      metrics.recordAiProcessing(
        `media_stream_${mediaStream.streamType}`, 
        'success',
        processingTime
      );
      
      // 更新媒体流记录
      mediaStream.status = MediaStreamStatus.COMPLETED;
      mediaStream.endTime = new Date();
      const duration = (mediaStream.endTime.getTime() - mediaStream.startTime.getTime()) / 1000;
      mediaStream.duration = duration;
      mediaStream.fileUrl = fileUrl;
      await mediaStream.save();
      
      // 进行进一步处理（如识别方言、转写等）
      processMediaContent(mediaStream.toObject()).catch(err => {
        logger.error(`后处理媒体内容错误 [ID: ${streamId}]:`, err);
      });
      
      return {
        success: true,
        streamId: mediaStream._id.toString(),
        status: mediaStream.status,
        fileUrl
      };
    } catch (error) {
      // 处理失败
      mediaStream.status = MediaStreamStatus.FAILED;
      mediaStream.metadata = { 
        ...mediaStream.metadata, 
        error: (error as Error).message || '处理失败'
      };
      await mediaStream.save();
      
      // 记录失败指标
      metrics.recordAiProcessing(
        `media_stream_${mediaStream.streamType}`, 
        'failure',
        Date.now() - processingStartTime
      );
      
      throw error;
    }
  } catch (error) {
    logger.error(`完成媒体流错误 [ID: ${streamId}]:`, error);
    throw error;
  }
};

/**
 * 处理媒体流：合并块并上传到存储
 */
const processMediaStream = async (
  streamId: string,
  streamType: MediaStreamType
): Promise<string> => {
  try {
    const tempDir = path.join(TEMP_STORAGE_PATH, streamId);
    
    // 获取所有块文件
    const files = fs.readdirSync(tempDir)
      .filter(file => file.startsWith('chunk_'))
      .sort((a, b) => {
        const indexA = parseInt(a.split('_')[1]);
        const indexB = parseInt(b.split('_')[1]);
        return indexA - indexB;
      });
    
    if (files.length === 0) {
      throw new Error('没有找到媒体块文件');
    }
    
    // 合并文件
    const outputPath = path.join(tempDir, 'output');
    const outputStream = fs.createWriteStream(outputPath);
    
    for (const file of files) {
      const filePath = path.join(tempDir, file);
      const chunk = fs.readFileSync(filePath);
      outputStream.write(chunk);
    }
    
    outputStream.end();
    
    // 等待写入完成
    await new Promise<void>((resolve, reject) => {
      outputStream.on('finish', resolve);
      outputStream.on('error', reject);
    });
    
    // 确定文件类型和扩展名
    let contentType: string;
    let extension: string;
    
    if (streamType === MediaStreamType.AUDIO) {
      contentType = 'audio/webm';
      extension = 'webm';
    } else if (streamType === MediaStreamType.VIDEO) {
      contentType = 'video/webm';
      extension = 'webm';
    } else {
      contentType = 'application/octet-stream';
      extension = 'bin';
    }
    
    // 上传到S3或其他存储
    const bucketName = process.env.S3_BUCKET || 'laoke-service';
    const fileKey = `media-streams/${streamType}/${new Date().toISOString().slice(0, 10)}/${streamId}.${extension}`;
    
    // 确保存储桶存在
    try {
      await s3.headBucket({ Bucket: bucketName }).promise();
    } catch (error) {
      if ((error as AWS.AWSError).statusCode === 404) {
        // 创建存储桶
        await s3.createBucket({ 
          Bucket: bucketName,
          ...(process.env.S3_REGION && process.env.S3_REGION !== 'us-east-1' 
            ? { CreateBucketConfiguration: { LocationConstraint: process.env.S3_REGION } } 
            : {})
        }).promise();
      } else {
        throw error;
      }
    }
    
    const uploadParams = {
      Bucket: bucketName,
      Key: fileKey,
      Body: fs.createReadStream(outputPath),
      ContentType: contentType
    };
    
    // 上传文件
    const uploadResult = await s3.upload(uploadParams).promise();
    
    // 清理临时文件
    fs.rmSync(tempDir, { recursive: true, force: true });
    
    return uploadResult.Location;
  } catch (error) {
    logger.error(`处理媒体流错误 [ID: ${streamId}]:`, error);
    throw new ApiError(500, '处理媒体流失败');
  }
};

/**
 * 对媒体内容进行进一步处理（异步）
 */
const processMediaContent = async (mediaStream: IMediaStream): Promise<boolean> => {
  try {
    const processingStartTime = Date.now();
    
    // 根据媒体类型进行不同处理
    if (mediaStream.streamType === MediaStreamType.AUDIO) {
      // 语音识别和方言检测
      await processAudioContent(mediaStream);
    } else if (mediaStream.streamType === MediaStreamType.VIDEO) {
      // 视频处理
      await processVideoContent(mediaStream);
    }
    
    // 记录处理时间
    const processingTime = Date.now() - processingStartTime;
    
    // 更新指标
    metrics.recordAiProcessing(
      `process_${mediaStream.streamType}_content`,
      'success',
      processingTime
    );
    
    return true;
  } catch (error) {
    logger.error(`处理媒体内容错误 [ID: ${mediaStream._id}]:`, error);
    
    // 更新指标
    metrics.recordAiProcessing(
      `process_${mediaStream.streamType}_content`,
      'failure',
      Date.now() - processingStartTime
    );
    
    // 不抛出错误，因为这是异步后处理
    return false;
  }
};

/**
 * 处理音频内容
 */
const processAudioContent = async (mediaStream: IMediaStream): Promise<any> => {
  try {
    // 如果指定了方言，进行方言特定处理
    if (mediaStream.dialect) {
      const dialect = await DialectModel.findOne({ code: mediaStream.dialect });
      if (dialect) {
        // 使用特定方言模型
        logger.info(`使用方言模型处理 [方言: ${dialect.name}]`);
      }
    }
    
    // 调用语音识别服务
    const recognitionResult = await recognizeAudio(
      mediaStream.fileUrl || '', 
      mediaStream.dialect
    );
    
    // 更新处理结果
    await MediaStreamModel.findByIdAndUpdate(mediaStream._id, {
      processingResults: recognitionResult,
      updatedAt: new Date()
    });
    
    return recognitionResult;
  } catch (error) {
    logger.error(`处理音频内容错误 [ID: ${mediaStream._id}]:`, error);
    throw error;
  }
};

/**
 * 处理视频内容
 */
const processVideoContent = async (mediaStream: IMediaStream): Promise<any> => {
  try {
    // 提取视频帧
    const videoAnalysisResults = await analyzeVideo(mediaStream.fileUrl || '');
    
    // 提取音频并进行语音识别
    const audioRecognitionResults = await extractAndRecognizeAudio(
      mediaStream.fileUrl || '', 
      mediaStream.dialect
    );
    
    // 结合结果
    const processingResults = {
      videoAnalysis: videoAnalysisResults,
      audioRecognition: audioRecognitionResults
    };
    
    // 更新处理结果
    await MediaStreamModel.findByIdAndUpdate(mediaStream._id, {
      processingResults,
      updatedAt: new Date()
    });
    
    return processingResults;
  } catch (error) {
    logger.error(`处理视频内容错误 [ID: ${mediaStream._id}]:`, error);
    throw error;
  }
};

/**
 * 识别音频内容
 */
const recognizeAudio = async (audioUrl: string, dialect?: string): Promise<any> => {
  try {
    const startTime = Date.now();
    
    // 检查OpenAI API密钥是否配置
    const openaiApiKey = process.env.OPENAI_API_KEY;
    if (!openaiApiKey) {
      logger.warn('未配置OpenAI API密钥，使用模拟的语音识别结果');
      
      // 返回模拟结果
      return {
        text: "这是一段模拟的文本转写结果。由于未配置实际的语音识别服务，所以返回此模拟数据。",
        language: dialect?.split('-')[0] || 'zh',
        segments: [
          {
            id: 0,
            start: 0,
            end: 5.2,
            text: "这是一段模拟的文本转写结果。"
          },
          {
            id: 1,
            start: 5.2,
            end: 10.4,
            text: "由于未配置实际的语音识别服务，所以返回此模拟数据。"
          }
        ],
        words: [],
        _processingType: "simulation"
      };
    }
    
    // 实际的Whisper API调用
    // 这里调用实际的语音识别服务，如OpenAI Whisper API
    const whisperEndpoint = process.env.WHISPER_API_ENDPOINT || 'https://api.openai.com/v1/audio/transcriptions';
    
    // 调用语音识别API
    const response = await axios.post(whisperEndpoint, {
      audio: audioUrl,
      model: 'whisper-1',
      language: dialect ? dialect.split('-')[0] : undefined,
      response_format: 'verbose_json',
      timestamp_granularities: ['segment', 'word']
    }, {
      headers: {
        'Authorization': `Bearer ${openaiApiKey}`,
        'Content-Type': 'application/json'
      }
    });
    
    // 记录处理时间
    metrics.recordAiProcessing(
      'audio_recognition',
      'success',
      Date.now() - startTime
    );
    
    return response.data;
  } catch (error) {
    logger.error(`音频识别错误 [URL: ${audioUrl}]:`, error);
    throw new ApiError(500, '音频识别失败');
  }
};

/**
 * 分析视频内容
 */
const analyzeVideo = async (videoUrl: string): Promise<any> => {
  // 实际视频分析实现
  // 此处为示例代码，实际项目中需要集成实际的视频分析服务
  return {
    frames: [
      // 视频帧分析结果
    ],
    scenes: [
      // 场景分析
    ],
    summary: "这是视频内容的摘要描述",
    _processingType: "simulation"
  };
};

/**
 * 从视频中提取音频并进行识别
 */
const extractAndRecognizeAudio = async (videoUrl: string, dialect?: string): Promise<any> => {
  // 实际实现需要使用FFmpeg等工具提取音频
  // 此处为示例代码，实际项目中需要集成FFmpeg
  const audioUrl = videoUrl.replace('.webm', '.audio.webm');
  return await recognizeAudio(audioUrl, dialect);
};

/**
 * 获取媒体流列表
 */
export const getMediaStreams = async (params: {
  userId?: string;
  streamType?: MediaStreamType;
  status?: MediaStreamStatus;
  page: number;
  limit: number;
}): Promise<{
  items: any[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}> => {
  try {
    const { userId, streamType, status, page, limit } = params;
    const skip = (page - 1) * limit;
    
    // 构建查询条件
    const query: Record<string, any> = {};
    if (userId) {
      query.userId = userId;
    }
    if (streamType) {
      query.streamType = streamType;
    }
    if (status) {
      query.status = status;
    }
    
    // 查询数据
    const [items, total] = await Promise.all([
      MediaStreamModel.find(query)
        .skip(skip)
        .limit(limit)
        .sort({ startTime: -1 })
        .lean(),
      MediaStreamModel.countDocuments(query)
    ]);
    
    return {
      items,
      total,
      page,
      limit,
      pages: Math.ceil(total / limit)
    };
  } catch (error) {
    logger.error('获取媒体流列表错误:', error);
    throw new ApiError(500, '获取媒体流列表失败');
  }
};

/**
 * 获取媒体流详情
 */
export const getMediaStreamById = async (id: string): Promise<any | null> => {
  try {
    const mediaStream = await MediaStreamModel.findById(id).lean();
    
    if (!mediaStream) {
      return null;
    }
    
    return mediaStream;
  } catch (error) {
    logger.error(`获取媒体流详情错误 [ID: ${id}]:`, error);
    throw new ApiError(500, '获取媒体流详情失败');
  }
};

/**
 * 更新媒体流指标
 */
const updateStreamMetrics = async (): Promise<void> => {
  try {
    // 获取活动媒体流数量
    const activeAudioStreams = await MediaStreamModel.countDocuments({
      streamType: MediaStreamType.AUDIO,
      status: MediaStreamStatus.ACTIVE
    });
    
    const activeVideoStreams = await MediaStreamModel.countDocuments({
      streamType: MediaStreamType.VIDEO,
      status: MediaStreamStatus.ACTIVE
    });
    
    // 更新指标
    metrics.updateGauge('active_audio_streams', activeAudioStreams);
    metrics.updateGauge('active_video_streams', activeVideoStreams);
  } catch (error) {
    logger.error('更新媒体流指标错误:', error);
  }
}; 
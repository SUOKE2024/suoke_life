import mongoose, { Document, Schema } from 'mongoose';

/**
 * 媒体流类型枚举
 */
export enum MediaStreamType {
  AUDIO = 'audio',
  VIDEO = 'video',
  IMAGE = 'image'
}

/**
 * 媒体流处理状态枚举
 */
export enum MediaStreamStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

/**
 * 媒体流处理类型枚举
 */
export enum MediaProcessingType {
  DIALECT_DETECTION = 'dialect_detection',
  DIALECT_TRANSLATION = 'dialect_translation',
  SPEECH_TO_TEXT = 'speech_to_text',
  TEXT_TO_SPEECH = 'text_to_speech',
  IMAGE_RECOGNITION = 'image_recognition',
  FACE_DETECTION = 'face_detection',
  OBJECT_DETECTION = 'object_detection',
  EMOTION_DETECTION = 'emotion_detection'
}

/**
 * 媒体流接口
 */
export interface IMediaStream extends Document {
  userId: mongoose.Types.ObjectId;
  streamType: MediaStreamType;
  processingType: MediaProcessingType;
  originalName: string;
  fileSize: number;
  mimeType: string;
  duration?: number;
  filePath: string;
  publicUrl?: string;
  status: MediaStreamStatus;
  processingStartTime?: Date;
  processingEndTime?: Date;
  processingDuration?: number;
  processingMetadata?: Record<string, any>;
  processingResult?: Record<string, any>;
  errorMessage?: string;
  tags?: string[];
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 媒体流Schema
 */
const MediaStreamSchema = new Schema<IMediaStream>(
  {
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      index: true
    },
    streamType: {
      type: String,
      enum: Object.values(MediaStreamType),
      required: true,
      index: true
    },
    processingType: {
      type: String,
      enum: Object.values(MediaProcessingType),
      required: true,
      index: true
    },
    originalName: {
      type: String,
      required: true
    },
    fileSize: {
      type: Number,
      required: true
    },
    mimeType: {
      type: String,
      required: true
    },
    duration: {
      type: Number
    },
    filePath: {
      type: String,
      required: true
    },
    publicUrl: {
      type: String
    },
    status: {
      type: String,
      enum: Object.values(MediaStreamStatus),
      default: MediaStreamStatus.PENDING,
      index: true
    },
    processingStartTime: {
      type: Date
    },
    processingEndTime: {
      type: Date
    },
    processingDuration: {
      type: Number
    },
    processingMetadata: {
      type: Object
    },
    processingResult: {
      type: Object
    },
    errorMessage: {
      type: String
    },
    tags: {
      type: [String],
      index: true
    }
  },
  {
    timestamps: true
  }
);

// 添加索引以优化查询性能
MediaStreamSchema.index({ userId: 1, createdAt: -1 });
MediaStreamSchema.index({ streamType: 1, status: 1 });
MediaStreamSchema.index({ processingType: 1, status: 1 });

/**
 * 创建媒体流处理模型
 */
export const MediaStreamModel = mongoose.model<IMediaStream>('MediaStream', MediaStreamSchema); 
import mongoose, { Schema, Document } from 'mongoose';
import { DialectType } from '../types';

export interface IMessageEntry {
  timestamp: Date;
  sender: string; // 'user' | 'agent' | 'system'
  messageType: 'text' | 'voice' | 'image' | 'video' | 'system';
  content: string;
  originalDialect?: DialectType;
  translatedContent?: string;
  targetDialect?: DialectType;
  metadata?: Record<string, any>;
}

export interface IConversation extends Document {
  conversationId: string;
  userId: string;
  agentId: string;
  title: string;
  messages: IMessageEntry[];
  dialectDetection?: {
    enabled: boolean;
    userDialect: DialectType;
    confidence: number;
  };
  summary?: string;
  tags?: string[];
  isActive: boolean;
  lastMessageAt: Date;
  createdAt: Date;
  updatedAt: Date;
}

const MessageEntrySchema = new Schema({
  timestamp: {
    type: Date,
    default: Date.now,
  },
  sender: {
    type: String,
    required: true,
    enum: ['user', 'agent', 'system'],
  },
  messageType: {
    type: String,
    required: true,
    enum: ['text', 'voice', 'image', 'video', 'system'],
    default: 'text',
  },
  content: {
    type: String,
    required: true,
  },
  originalDialect: {
    type: String,
    enum: Object.values(DialectType),
  },
  translatedContent: {
    type: String,
  },
  targetDialect: {
    type: String,
    enum: Object.values(DialectType),
  },
  metadata: {
    type: Schema.Types.Mixed,
    default: {},
  },
});

const ConversationSchema: Schema = new Schema(
  {
    conversationId: {
      type: String,
      required: true,
      unique: true,
    },
    userId: {
      type: String,
      required: true,
    },
    agentId: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    messages: [MessageEntrySchema],
    dialectDetection: {
      enabled: {
        type: Boolean,
        default: true,
      },
      userDialect: {
        type: String,
        enum: Object.values(DialectType),
        default: DialectType.MANDARIN,
      },
      confidence: {
        type: Number,
        default: 1.0,
      },
    },
    summary: {
      type: String,
    },
    tags: {
      type: [String],
    },
    isActive: {
      type: Boolean,
      default: true,
    },
    lastMessageAt: {
      type: Date,
      default: Date.now,
    },
  },
  {
    timestamps: true,
  }
);

// 索引优化
ConversationSchema.index({ conversationId: 1 });
ConversationSchema.index({ userId: 1 });
ConversationSchema.index({ agentId: 1 });
ConversationSchema.index({ isActive: 1 });
ConversationSchema.index({ lastMessageAt: -1 });
ConversationSchema.index({ 'dialectDetection.userDialect': 1 });

export const Conversation = mongoose.model<IConversation>('Conversation', ConversationSchema);
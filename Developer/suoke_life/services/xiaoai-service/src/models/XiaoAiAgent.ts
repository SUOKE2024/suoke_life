import mongoose, { Document, Schema } from 'mongoose';
import { DialectType } from '../services/DialectService';

// 小艾会话记录接口
export interface IConversationEntry {
  timestamp: Date;
  userId: string;
  messageType: 'text' | 'voice' | 'image' | 'system';
  content: string;
  metadata?: {
    accessibility?: {
      needsVoiceGuidance: boolean;
      preferredVoiceSpeed?: number;
      visuallyImpaired?: boolean;
      hearingImpaired?: boolean;
    };
    dialect?: {
      detected?: DialectType;
      confidence?: number;
      originalText?: string;
    };
    diagnosticContext?: {
      activeDiagnostics?: string[];  // 当前活跃的诊断服务
      diagnosisStage?: string;       // 诊断阶段
      diagnosisResults?: Record<string, any>; // 诊断结果
    };
  };
}

// 小艾智能体状态接口
export interface IXiaoAiState {
  mode: 'normal' | 'accessibility' | 'diagnosis-coordination';
  currentTask?: string;
  userPreferences: {
    voiceEnabled: boolean;
    voiceSpeed: number;
    preferredLanguage: string;
    notificationEnabled: boolean;
  };
  activeDiagnosticServices: string[];
  accessibilitySettings: {
    visualAssistance: boolean;
    audioAssistance: boolean;
    textSize: 'normal' | 'large' | 'extra-large';
    highContrast: boolean;
  };
  dialectSettings: {
    supportedDialects: DialectType[];
    activeDialect: DialectType;
    dialectDetectionEnabled: boolean;
  };
}

// 小艾智能体接口
export interface IXiaoAiAgent extends Document {
  agentId: string;
  name: string;
  description: string;
  userId: string;
  avatarUrl?: string;
  capabilities: string[]; // 支持的能力
  settings: {
    voiceEnabled: boolean;
    voiceVolume: number; // 0-100
    voiceSpeed: number; // 0.5-2.0
    arVrEnabled: boolean;
    accessibilityMode: boolean;
    dialectSupport: boolean; // 方言支持开关
    diagnosticServices: {
      looking: boolean;
      inquiry: boolean;
      smell: boolean;
      touch: boolean;
    };
  };
  lastActive: Date;
  createdAt: Date;
  updatedAt: Date;
}

// 小艾智能体Schema
const XiaoAiAgentSchema = new Schema<IXiaoAiAgent>(
  {
    agentId: {
      type: String,
      required: true,
      unique: true,
    },
    name: {
      type: String,
      required: true,
    },
    description: {
      type: String,
      required: true,
    },
    userId: {
      type: String,
      required: true,
    },
    avatarUrl: {
      type: String,
    },
    capabilities: {
      type: [String],
      default: ['基础对话', '语音交互', '无障碍支持', '方言支持'],
    },
    settings: {
      voiceEnabled: {
        type: Boolean,
        default: true,
      },
      voiceVolume: {
        type: Number,
        default: 80,
        min: 0,
        max: 100,
      },
      voiceSpeed: {
        type: Number,
        default: 1.0,
        min: 0.5,
        max: 2.0,
      },
      arVrEnabled: {
        type: Boolean,
        default: false,
      },
      accessibilityMode: {
        type: Boolean,
        default: false,
      },
      dialectSupport: {
        type: Boolean,
        default: true,
      },
      diagnosticServices: {
        looking: {
          type: Boolean,
          default: true,
        },
        inquiry: {
          type: Boolean,
          default: true,
        },
        smell: {
          type: Boolean,
          default: true,
        },
        touch: {
          type: Boolean,
          default: true,
        },
      },
    },
    lastActive: {
      type: Date,
      default: Date.now,
    },
  },
  {
    timestamps: true,
  }
);

// 索引优化
XiaoAiAgentSchema.index({ agentId: 1 });
XiaoAiAgentSchema.index({ userId: 1 });
XiaoAiAgentSchema.index({ lastActive: -1 });

// 创建并导出模型
const XiaoAiAgent = mongoose.model<IXiaoAiAgent>('XiaoAiAgent', XiaoAiAgentSchema);

export default XiaoAiAgent;
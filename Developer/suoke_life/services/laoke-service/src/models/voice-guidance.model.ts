import mongoose, { Document, Schema } from 'mongoose';

/**
 * 引导类型枚举
 */
export enum GuidanceType {
  NAVIGATION = 'navigation',
  INSTRUCTION = 'instruction',
  INFORMATION = 'information',
  ALERT = 'alert',
  TUTORIAL = 'tutorial',
  FEEDBACK = 'feedback'
}

/**
 * 场景类型枚举
 */
export enum SceneType {
  HOME = 'home',
  MAP = 'map',
  HEALTH = 'health',
  SHOPPING = 'shopping',
  ENTERTAINMENT = 'entertainment',
  EDUCATION = 'education',
  COMMUNICATION = 'communication',
  UTILITY = 'utility',
  GLOBAL = 'global'
}

/**
 * 指令优先级枚举
 */
export enum CommandPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

/**
 * 语音指令接口
 */
export interface IVoiceCommand extends Document {
  trigger: string;
  aliases: string[];
  description: string;
  sceneType: SceneType;
  isEnabled: boolean;
  priority: CommandPriority;
  action: {
    type: string;
    payload: Record<string, any>;
  };
  requiredParams?: string[];
  optionalParams?: string[];
  examples: string[];
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 语音引导内容接口
 */
export interface IGuidanceContent extends Document {
  guidanceType: GuidanceType;
  sceneType: SceneType;
  sceneId?: string;
  title: string;
  content: string;
  audioUrl?: string;
  duration?: number;
  contextualTriggers: {
    event: string;
    conditions: Record<string, any>;
  }[];
  priority: CommandPriority;
  isEnabled: boolean;
  dialects: {
    dialectCode: string;
    content: string;
    audioUrl?: string;
  }[];
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 用户语音会话接口
 */
export interface IVoiceSession extends Document {
  userId: mongoose.Types.ObjectId;
  sessionId: string;
  startTime: Date;
  endTime?: Date;
  duration?: number;
  deviceInfo: {
    deviceId: string;
    deviceType: string;
    platform: string;
    osVersion: string;
    appVersion: string;
  };
  interactionCount: number;
  dialectCode?: string;
  recognitionAccuracy?: number;
  location?: {
    latitude: number;
    longitude: number;
    accuracy: number;
    address?: string;
  };
  context: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 语音交互记录接口
 */
export interface IVoiceInteraction extends Document {
  userId: mongoose.Types.ObjectId;
  sessionId: string;
  timestamp: Date;
  inputType: 'voice' | 'text';
  rawInput: string;
  processedInput: string;
  matchedCommand?: string;
  matchConfidence?: number;
  response: {
    type: string;
    content: string;
    audioUrl?: string;
    visualElements?: Record<string, any>;
  };
  actionTaken?: Record<string, any>;
  successful: boolean;
  errorMessage?: string;
  contextBefore: Record<string, any>;
  contextAfter: Record<string, any>;
  location?: {
    latitude: number;
    longitude: number;
    accuracy: number;
  };
  processingTime: number;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 语音偏好设置接口
 */
export interface IVoicePreference extends Document {
  userId: mongoose.Types.ObjectId;
  voiceType: string;
  pitch: number;
  speed: number;
  volume: number;
  dialectCode: string;
  useDialectForCommand: boolean;
  useDialectForResponse: boolean;
  enableBackgroundListening: boolean;
  enableWakeWord: boolean;
  wakeWord: string;
  enableProactiveSuggestions: boolean;
  enableVoiceFeedback: boolean;
  customCommands: {
    trigger: string;
    action: Record<string, any>;
  }[];
  createdAt: Date;
  updatedAt: Date;
}

/**
 * 语音指令Schema
 */
const VoiceCommandSchema = new Schema<IVoiceCommand>(
  {
    trigger: {
      type: String,
      required: true,
      unique: true,
      index: true
    },
    aliases: {
      type: [String],
      default: [],
      index: true
    },
    description: {
      type: String,
      required: true
    },
    sceneType: {
      type: String,
      enum: Object.values(SceneType),
      required: true,
      index: true
    },
    isEnabled: {
      type: Boolean,
      default: true,
      index: true
    },
    priority: {
      type: String,
      enum: Object.values(CommandPriority),
      default: CommandPriority.MEDIUM,
      index: true
    },
    action: {
      type: {
        type: String,
        required: true
      },
      payload: {
        type: Schema.Types.Mixed,
        default: {}
      }
    },
    requiredParams: {
      type: [String]
    },
    optionalParams: {
      type: [String]
    },
    examples: {
      type: [String],
      required: true
    }
  },
  {
    timestamps: true
  }
);

/**
 * 语音引导内容Schema
 */
const GuidanceContentSchema = new Schema<IGuidanceContent>(
  {
    guidanceType: {
      type: String,
      enum: Object.values(GuidanceType),
      required: true,
      index: true
    },
    sceneType: {
      type: String,
      enum: Object.values(SceneType),
      required: true,
      index: true
    },
    sceneId: {
      type: String,
      index: true
    },
    title: {
      type: String,
      required: true
    },
    content: {
      type: String,
      required: true
    },
    audioUrl: {
      type: String
    },
    duration: {
      type: Number
    },
    contextualTriggers: [
      {
        event: {
          type: String,
          required: true
        },
        conditions: {
          type: Schema.Types.Mixed,
          default: {}
        }
      }
    ],
    priority: {
      type: String,
      enum: Object.values(CommandPriority),
      default: CommandPriority.MEDIUM,
      index: true
    },
    isEnabled: {
      type: Boolean,
      default: true,
      index: true
    },
    dialects: [
      {
        dialectCode: {
          type: String,
          required: true
        },
        content: {
          type: String,
          required: true
        },
        audioUrl: {
          type: String
        }
      }
    ]
  },
  {
    timestamps: true
  }
);

/**
 * 语音会话Schema
 */
const VoiceSessionSchema = new Schema<IVoiceSession>(
  {
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      index: true
    },
    sessionId: {
      type: String,
      required: true,
      unique: true,
      index: true
    },
    startTime: {
      type: Date,
      required: true,
      default: Date.now
    },
    endTime: {
      type: Date
    },
    duration: {
      type: Number
    },
    deviceInfo: {
      deviceId: {
        type: String,
        required: true
      },
      deviceType: {
        type: String,
        required: true
      },
      platform: {
        type: String,
        required: true
      },
      osVersion: {
        type: String
      },
      appVersion: {
        type: String
      }
    },
    interactionCount: {
      type: Number,
      default: 0
    },
    dialectCode: {
      type: String,
      index: true
    },
    recognitionAccuracy: {
      type: Number
    },
    location: {
      latitude: {
        type: Number
      },
      longitude: {
        type: Number
      },
      accuracy: {
        type: Number
      },
      address: {
        type: String
      }
    },
    context: {
      type: Schema.Types.Mixed,
      default: {}
    }
  },
  {
    timestamps: true
  }
);

/**
 * 语音交互记录Schema
 */
const VoiceInteractionSchema = new Schema<IVoiceInteraction>(
  {
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      index: true
    },
    sessionId: {
      type: String,
      required: true,
      index: true
    },
    timestamp: {
      type: Date,
      required: true,
      default: Date.now
    },
    inputType: {
      type: String,
      enum: ['voice', 'text'],
      required: true
    },
    rawInput: {
      type: String,
      required: true
    },
    processedInput: {
      type: String,
      required: true
    },
    matchedCommand: {
      type: String,
      index: true
    },
    matchConfidence: {
      type: Number
    },
    response: {
      type: {
        type: String,
        required: true
      },
      content: {
        type: String,
        required: true
      },
      audioUrl: {
        type: String
      },
      visualElements: {
        type: Schema.Types.Mixed
      }
    },
    actionTaken: {
      type: Schema.Types.Mixed
    },
    successful: {
      type: Boolean,
      required: true,
      index: true
    },
    errorMessage: {
      type: String
    },
    contextBefore: {
      type: Schema.Types.Mixed,
      default: {}
    },
    contextAfter: {
      type: Schema.Types.Mixed,
      default: {}
    },
    location: {
      latitude: {
        type: Number
      },
      longitude: {
        type: Number
      },
      accuracy: {
        type: Number
      }
    },
    processingTime: {
      type: Number,
      required: true
    }
  },
  {
    timestamps: true
  }
);

/**
 * 语音偏好设置Schema
 */
const VoicePreferenceSchema = new Schema<IVoicePreference>(
  {
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
      unique: true,
      index: true
    },
    voiceType: {
      type: String,
      default: 'female'
    },
    pitch: {
      type: Number,
      default: 1.0,
      min: 0.1,
      max: 2.0
    },
    speed: {
      type: Number,
      default: 1.0,
      min: 0.1,
      max: 2.0
    },
    volume: {
      type: Number,
      default: 1.0,
      min: 0.0,
      max: 1.0
    },
    dialectCode: {
      type: String,
      default: 'zh-CN'
    },
    useDialectForCommand: {
      type: Boolean,
      default: false
    },
    useDialectForResponse: {
      type: Boolean,
      default: false
    },
    enableBackgroundListening: {
      type: Boolean,
      default: false
    },
    enableWakeWord: {
      type: Boolean,
      default: true
    },
    wakeWord: {
      type: String,
      default: '老克'
    },
    enableProactiveSuggestions: {
      type: Boolean,
      default: true
    },
    enableVoiceFeedback: {
      type: Boolean,
      default: true
    },
    customCommands: [
      {
        trigger: {
          type: String,
          required: true
        },
        action: {
          type: Schema.Types.Mixed,
          required: true
        }
      }
    ]
  },
  {
    timestamps: true
  }
);

// 创建索引
VoiceCommandSchema.index({ 'action.type': 1 });
GuidanceContentSchema.index({ guidanceType: 1, sceneType: 1, isEnabled: 1 });
VoiceInteractionSchema.index({ userId: 1, sessionId: 1, timestamp: -1 });
VoiceSessionSchema.index({ userId: 1, startTime: -1 });

// 创建模型
export const VoiceCommandModel = mongoose.model<IVoiceCommand>('VoiceCommand', VoiceCommandSchema);
export const GuidanceContentModel = mongoose.model<IGuidanceContent>('GuidanceContent', GuidanceContentSchema);
export const VoiceSessionModel = mongoose.model<IVoiceSession>('VoiceSession', VoiceSessionSchema);
export const VoiceInteractionModel = mongoose.model<IVoiceInteraction>('VoiceInteraction', VoiceInteractionSchema);
export const VoicePreferenceModel = mongoose.model<IVoicePreference>('VoicePreference', VoicePreferenceSchema); 
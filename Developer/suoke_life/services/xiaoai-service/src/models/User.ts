import mongoose, { Document, Schema } from 'mongoose';
import { DialectType } from '../types';

// 用户无障碍需求接口
export interface IAccessibilityNeeds {
  visuallyImpaired: boolean;
  hearingImpaired: boolean;
  mobilityImpaired: boolean;
  cognitiveImpaired: boolean;
  needsVoiceGuidance: boolean;
  preferredVoiceSpeed: number;
  highContrastMode: boolean;
  largeTextMode: boolean;
  otherNeeds?: string;
}

// 用户接口
export interface IUser extends Document {
  userId: string;
  username: string;
  avatarUrl?: string;
  region?: string;
  email?: string;
  phoneNumber?: string;
  accessibilityPreferences: {
    needsVoiceGuidance: boolean;
    needsSimplifiedContent: boolean;
    needsHighContrast: boolean;
    needsScreenReader: boolean;
    hasVisualImpairment: boolean;
    hasHearingImpairment: boolean;
    hasCognitiveImpairment: boolean;
    hasMotorImpairment: boolean;
    guidanceSpeed: 'slow' | 'normal' | 'fast';
    voiceGuidanceVolume: number;
    textSize: 'small' | 'medium' | 'large' | 'x-large';
  };
  dialectPreferences: {
    primary: string; // 主要方言
    secondary?: string; // 次要方言（备选）
    autoDetect: boolean; // 是否自动检测方言
  };
  medicalProfile?: {
    bodyType?: string;
    allergies?: string[];
    medicalConditions?: string[];
    medications?: string[];
  };
  lastLogin?: Date;
  createdAt: Date;
  updatedAt: Date;
}

// 用户Schema
const UserSchema = new Schema<IUser>(
  {
    userId: {
      type: String,
      required: true,
      unique: true,
    },
    username: {
      type: String,
      required: true,
    },
    avatarUrl: {
      type: String,
    },
    region: {
      type: String,
    },
    email: {
      type: String,
      sparse: true,
    },
    phoneNumber: {
      type: String,
      sparse: true,
    },
    accessibilityPreferences: {
      needsVoiceGuidance: {
        type: Boolean,
        default: false,
      },
      needsSimplifiedContent: {
        type: Boolean,
        default: false,
      },
      needsHighContrast: {
        type: Boolean,
        default: false,
      },
      needsScreenReader: {
        type: Boolean,
        default: false,
      },
      hasVisualImpairment: {
        type: Boolean,
        default: false,
      },
      hasHearingImpairment: {
        type: Boolean,
        default: false,
      },
      hasCognitiveImpairment: {
        type: Boolean,
        default: false,
      },
      hasMotorImpairment: {
        type: Boolean,
        default: false,
      },
      guidanceSpeed: {
        type: String,
        enum: ['slow', 'normal', 'fast'],
        default: 'normal',
      },
      voiceGuidanceVolume: {
        type: Number,
        default: 80,
        min: 0,
        max: 100,
      },
      textSize: {
        type: String,
        enum: ['small', 'medium', 'large', 'x-large'],
        default: 'medium',
      },
    },
    dialectPreferences: {
      primary: {
        type: String,
        enum: Object.values(DialectType),
        default: DialectType.MANDARIN,
      },
      secondary: {
        type: String,
        enum: Object.values(DialectType),
      },
      autoDetect: {
        type: Boolean,
        default: true,
      },
    },
    medicalProfile: {
      bodyType: {
        type: String,
      },
      allergies: {
        type: [String],
      },
      medicalConditions: {
        type: [String],
      },
      medications: {
        type: [String],
      },
    },
    lastLogin: {
      type: Date,
    },
  },
  {
    timestamps: true,
  }
);

// 索引优化
UserSchema.index({ userId: 1 });
UserSchema.index({ 'accessibilityPreferences.needsVoiceGuidance': 1 });
UserSchema.index({ 'dialectPreferences.primary': 1 });
UserSchema.index({ lastLogin: -1 });

// 创建并导出模型
const User = mongoose.model<IUser>('User', UserSchema);

export default User;
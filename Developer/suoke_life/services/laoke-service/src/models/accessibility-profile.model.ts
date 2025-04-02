import mongoose, { Schema, Document } from 'mongoose';

export interface IAccessibilityProfile extends Document {
  userId: string;
  visualSettings: {
    textSize: 'small' | 'medium' | 'large' | 'x-large';
    highContrast: boolean;
    reduceMotion: boolean;
    colorBlindMode: 'none' | 'protanopia' | 'deuteranopia' | 'tritanopia' | 'achromatopsia';
    screenReader: boolean;
    invertColors: boolean;
    fontType: 'default' | 'dyslexic' | 'sans-serif' | 'serif';
  };
  audioSettings: {
    voiceFeedback: boolean;
    soundEffects: boolean;
    hapticFeedback: boolean;
    voiceRecognition: boolean;
    voiceSpeed: number; // 0.5-2.0
    voicePitch: number; // 0.5-2.0
  };
  interactionSettings: {
    autoCompleteEnabled: boolean;
    extendedTouch: boolean;
    singleTapMode: boolean;
    keyboardNavigation: boolean;
    gestureControl: boolean;
    mouseDwell: boolean;
    mouseSpeed: number; // 0.5-2.0
  };
  navigationSettings: {
    simplifiedNavigation: boolean;
    shortcutsEnabled: boolean;
    breadcrumbsEnabled: boolean;
    pageStructure: 'standard' | 'simplified' | 'minimal';
  };
  dialectPreference: string; // 方言偏好
  createdAt: Date;
  updatedAt: Date;
}

const AccessibilityProfileSchema: Schema = new Schema({
  userId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    unique: true
  },
  visualSettings: {
    textSize: {
      type: String,
      enum: ['small', 'medium', 'large', 'x-large'],
      default: 'medium'
    },
    highContrast: {
      type: Boolean,
      default: false
    },
    reduceMotion: {
      type: Boolean,
      default: false
    },
    colorBlindMode: {
      type: String,
      enum: ['none', 'protanopia', 'deuteranopia', 'tritanopia', 'achromatopsia'],
      default: 'none'
    },
    screenReader: {
      type: Boolean,
      default: false
    },
    invertColors: {
      type: Boolean,
      default: false
    },
    fontType: {
      type: String,
      enum: ['default', 'dyslexic', 'sans-serif', 'serif'],
      default: 'default'
    }
  },
  audioSettings: {
    voiceFeedback: {
      type: Boolean,
      default: false
    },
    soundEffects: {
      type: Boolean,
      default: true
    },
    hapticFeedback: {
      type: Boolean,
      default: true
    },
    voiceRecognition: {
      type: Boolean,
      default: false
    },
    voiceSpeed: {
      type: Number,
      default: 1.0,
      min: 0.5,
      max: 2.0
    },
    voicePitch: {
      type: Number,
      default: 1.0,
      min: 0.5,
      max: 2.0
    }
  },
  interactionSettings: {
    autoCompleteEnabled: {
      type: Boolean,
      default: true
    },
    extendedTouch: {
      type: Boolean,
      default: false
    },
    singleTapMode: {
      type: Boolean,
      default: false
    },
    keyboardNavigation: {
      type: Boolean,
      default: false
    },
    gestureControl: {
      type: Boolean,
      default: false
    },
    mouseDwell: {
      type: Boolean,
      default: false
    },
    mouseSpeed: {
      type: Number,
      default: 1.0,
      min: 0.5,
      max: 2.0
    }
  },
  navigationSettings: {
    simplifiedNavigation: {
      type: Boolean,
      default: false
    },
    shortcutsEnabled: {
      type: Boolean,
      default: true
    },
    breadcrumbsEnabled: {
      type: Boolean,
      default: true
    },
    pageStructure: {
      type: String,
      enum: ['standard', 'simplified', 'minimal'],
      default: 'standard'
    }
  },
  dialectPreference: {
    type: String,
    default: 'standard'
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// 创建索引
AccessibilityProfileSchema.index({ userId: 1 }, { unique: true });

export const AccessibilityProfileModel = mongoose.model<IAccessibilityProfile>('AccessibilityProfile', AccessibilityProfileSchema); 
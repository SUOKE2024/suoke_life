import mongoose, { Schema, Document } from 'mongoose';

export interface IGameUserProgress extends Document {
  userId: string;
  quests: Array<{
    questId: string;
    status: 'not_started' | 'in_progress' | 'completed' | 'failed';
    startedAt: Date;
    completedAt?: Date;
    steps: Array<{
      stepIndex: number;
      completed: boolean;
      data?: any;
      completedAt?: Date;
    }>;
  }>;
  level: number;
  experience: number;
  points: number;
  achievements: Array<{
    achievementId: string;
    unlockedAt: Date;
  }>;
  inventory: Array<{
    itemId: string;
    quantity: number;
    acquiredAt: Date;
  }>;
  lastPlayedAt: Date;
  createdAt: Date;
  updatedAt: Date;
}

const GameUserProgressSchema: Schema = new Schema({
  userId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  quests: [{
    questId: {
      type: Schema.Types.ObjectId,
      ref: 'GameQuest',
      required: true
    },
    status: {
      type: String,
      enum: ['not_started', 'in_progress', 'completed', 'failed'],
      default: 'not_started'
    },
    startedAt: {
      type: Date
    },
    completedAt: {
      type: Date
    },
    steps: [{
      stepIndex: {
        type: Number,
        required: true
      },
      completed: {
        type: Boolean,
        default: false
      },
      data: {
        type: Schema.Types.Mixed
      },
      completedAt: {
        type: Date
      }
    }]
  }],
  level: {
    type: Number,
    default: 1
  },
  experience: {
    type: Number,
    default: 0
  },
  points: {
    type: Number,
    default: 0
  },
  achievements: [{
    achievementId: {
      type: Schema.Types.ObjectId,
      ref: 'GameAchievement'
    },
    unlockedAt: {
      type: Date,
      default: Date.now
    }
  }],
  inventory: [{
    itemId: {
      type: Schema.Types.ObjectId,
      ref: 'GameItem'
    },
    quantity: {
      type: Number,
      default: 1
    },
    acquiredAt: {
      type: Date,
      default: Date.now
    }
  }],
  lastPlayedAt: {
    type: Date,
    default: Date.now
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

// 创建索引以提高查询性能
GameUserProgressSchema.index({ userId: 1 }, { unique: true });
GameUserProgressSchema.index({ 'quests.questId': 1, userId: 1 });
GameUserProgressSchema.index({ level: 1 });
GameUserProgressSchema.index({ lastPlayedAt: -1 });

export const GameUserProgressModel = mongoose.model<IGameUserProgress>('GameUserProgress', GameUserProgressSchema); 
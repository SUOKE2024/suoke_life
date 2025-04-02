import mongoose, { Schema, Document } from 'mongoose';

export interface IGameQuest extends Document {
  title: string;
  description: string;
  type: 'main' | 'side' | 'daily' | 'event' | 'challenge';
  difficulty: 'easy' | 'medium' | 'hard' | 'expert';
  reward: {
    points: number;
    experience: number;
    items?: Array<{
      itemId: string;
      quantity: number;
    }>;
  };
  requirements?: {
    level?: number;
    quests?: string[];
    items?: Array<{
      itemId: string;
      quantity: number;
    }>;
  };
  steps: Array<{
    order: number;
    description: string;
    location?: {
      latitude: number;
      longitude: number;
      radius: number;
    };
    actionType?: 'collect' | 'interact' | 'photo' | 'scan' | 'answer';
    target?: string;
    quantity?: number;
    completed: boolean;
  }>;
  duration?: number; // 单位：秒，0表示永久
  startDate?: Date;
  endDate?: Date;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

const GameQuestSchema: Schema = new Schema({
  title: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    required: true
  },
  type: {
    type: String,
    enum: ['main', 'side', 'daily', 'event', 'challenge'],
    required: true
  },
  difficulty: {
    type: String,
    enum: ['easy', 'medium', 'hard', 'expert'],
    required: true
  },
  reward: {
    points: {
      type: Number,
      required: true
    },
    experience: {
      type: Number,
      required: true
    },
    items: [{
      itemId: {
        type: Schema.Types.ObjectId,
        ref: 'GameItem'
      },
      quantity: {
        type: Number,
        default: 1
      }
    }]
  },
  requirements: {
    level: {
      type: Number
    },
    quests: [{
      type: Schema.Types.ObjectId,
      ref: 'GameQuest'
    }],
    items: [{
      itemId: {
        type: Schema.Types.ObjectId,
        ref: 'GameItem'
      },
      quantity: {
        type: Number,
        default: 1
      }
    }]
  },
  steps: [{
    order: {
      type: Number,
      required: true
    },
    description: {
      type: String,
      required: true
    },
    location: {
      latitude: Number,
      longitude: Number,
      radius: Number
    },
    actionType: {
      type: String,
      enum: ['collect', 'interact', 'photo', 'scan', 'answer']
    },
    target: String,
    quantity: Number,
    completed: {
      type: Boolean,
      default: false
    }
  }],
  duration: {
    type: Number
  },
  startDate: {
    type: Date
  },
  endDate: {
    type: Date
  },
  isActive: {
    type: Boolean,
    default: true
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
GameQuestSchema.index({ title: 1 });
GameQuestSchema.index({ type: 1 });
GameQuestSchema.index({ difficulty: 1 });
GameQuestSchema.index({ isActive: 1 });
GameQuestSchema.index({ startDate: 1, endDate: 1 });

export const GameQuestModel = mongoose.model<IGameQuest>('GameQuest', GameQuestSchema); 
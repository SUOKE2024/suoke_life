import mongoose, { Document, Schema } from 'mongoose';
import { ActivityReview } from '../core/agent/types';

/**
 * 活动类别枚举
 */
export enum ActivityCategory {
  PLANTING = 'planting',      // 种植体验
  HARVESTING = 'harvesting',  // 收获采摘
  WORKSHOP = 'workshop',      // 农艺工坊
  TOUR = 'tour',              // 农场参观
  WELLNESS = 'wellness',      // 康养活动
  SEASONAL = 'seasonal',      // 节气活动
  CHILDREN = 'children',      // 亲子活动
  OTHER = 'other'             // 其他
}

/**
 * 活动状态枚举
 */
export enum ActivityStatus {
  UPCOMING = 'upcoming',     // 即将开始
  ONGOING = 'ongoing',       // 进行中
  COMPLETED = 'completed',   // 已结束
  CANCELLED = 'cancelled'    // 已取消
}

/**
 * 预约状态枚举
 */
export enum RegistrationStatus {
  PENDING = 'pending',       // 等待确认
  CONFIRMED = 'confirmed',   // 已确认
  CANCELLED = 'cancelled',   // 已取消
  COMPLETED = 'completed',   // 已完成
  NO_SHOW = 'no_show'        // 未出席
}

/**
 * 活动文档接口
 */
export interface ActivityDocument extends Document {
  name: string;                 // 活动名称
  description: string;          // 活动描述
  location: string;             // 活动地点
  startDate: string;            // 开始日期 (ISO字符串)
  endDate: string;              // 结束日期 (ISO字符串)
  status: ActivityStatus;       // 活动状态
  capacity: number;             // 最大容量
  currentRegistrations: number; // 当前注册人数
  price: number;                // 价格 (CNY)
  category: ActivityCategory;   // 活动类别
  organizer: string;            // 组织者
  contactInfo: string;          // 联系信息
  images: string[];             // 图片链接
  requirements?: string;        // 参与要求
  included?: string;            // 包含项目
  reviews: ActivityReview[];    // 活动评价
  metadata?: Record<string, any>; // 元数据
  createdAt?: Date;             // 创建时间
  updatedAt?: Date;             // 更新时间
}

/**
 * 活动注册文档接口
 */
export interface ActivityRegistrationDocument extends Document {
  activityId: string;           // 活动ID
  userId: string;               // 用户ID
  participants: number;         // 参与人数
  registrationDate: string;     // 注册日期 (ISO字符串)
  status: RegistrationStatus;   // 注册状态
  paymentId?: string;           // 支付ID (可选)
  notes?: string;               // 备注
  metadata?: Record<string, any>; // 元数据
  createdAt?: Date;             // 创建时间
  updatedAt?: Date;             // 更新时间
}

// 活动评价子文档Schema
const reviewSchema = new Schema({
  userId: { type: String, required: true },
  rating: { type: Number, required: true, min: 1, max: 5 },
  comment: { type: String, required: true },
  date: { type: String, required: true }, // ISO格式日期字符串
  photoUrls: [String]
}, { _id: false });

// 活动Schema
const activitySchema = new Schema<ActivityDocument>({
  name: { 
    type: String, 
    required: true, 
    trim: true,
    index: true 
  },
  description: { 
    type: String, 
    required: true 
  },
  location: { 
    type: String, 
    required: true,
    index: true 
  },
  startDate: { 
    type: String, 
    required: true,
    index: true 
  },
  endDate: { 
    type: String, 
    required: true 
  },
  status: { 
    type: String, 
    enum: Object.values(ActivityStatus),
    default: ActivityStatus.UPCOMING,
    index: true 
  },
  capacity: { 
    type: Number, 
    required: true, 
    min: 1 
  },
  currentRegistrations: { 
    type: Number, 
    default: 0 
  },
  price: { 
    type: Number, 
    required: true, 
    min: 0 
  },
  category: { 
    type: String, 
    enum: Object.values(ActivityCategory),
    required: true,
    index: true 
  },
  organizer: { 
    type: String, 
    required: true 
  },
  contactInfo: { 
    type: String, 
    required: true 
  },
  images: [{ 
    type: String 
  }],
  requirements: { 
    type: String 
  },
  included: { 
    type: String 
  },
  reviews: [reviewSchema],
  metadata: { 
    type: Schema.Types.Mixed 
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// 虚拟字段：剩余容量
activitySchema.virtual('remainingCapacity').get(function(this: ActivityDocument) {
  return this.capacity - this.currentRegistrations;
});

// 虚拟字段：当前状态自动更新
activitySchema.pre('save', function(this: ActivityDocument, next) {
  const now = new Date().toISOString();
  
  if (now < this.startDate) {
    this.status = ActivityStatus.UPCOMING;
  } else if (now >= this.startDate && now <= this.endDate) {
    this.status = ActivityStatus.ONGOING;
  } else if (now > this.endDate) {
    this.status = ActivityStatus.COMPLETED;
  }
  
  next();
});

// 活动注册Schema
const activityRegistrationSchema = new Schema<ActivityRegistrationDocument>({
  activityId: { 
    type: String, 
    required: true,
    index: true 
  },
  userId: { 
    type: String, 
    required: true,
    index: true 
  },
  participants: { 
    type: Number, 
    required: true, 
    min: 1 
  },
  registrationDate: { 
    type: String, 
    required: true 
  },
  status: { 
    type: String, 
    enum: Object.values(RegistrationStatus),
    default: RegistrationStatus.PENDING,
    index: true 
  },
  paymentId: { 
    type: String 
  },
  notes: { 
    type: String 
  },
  metadata: { 
    type: Schema.Types.Mixed 
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// 创建复合索引
activityRegistrationSchema.index({ userId: 1, activityId: 1 }, { unique: true });

// 创建模型
export const ActivityModel = mongoose.model<ActivityDocument>('Activity', activitySchema);
export const ActivityRegistrationModel = mongoose.model<ActivityRegistrationDocument>('ActivityRegistration', activityRegistrationSchema); 
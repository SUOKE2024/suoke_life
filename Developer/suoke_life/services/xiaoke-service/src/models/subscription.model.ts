import mongoose, { Document, Schema } from 'mongoose';

// 订阅文档类型
export interface SubscriptionDocument extends Document {
  userId: string;
  serviceName: string;
  serviceType: string;
  status: string;
  startDate: string;
  endDate: string;
  price: number;
  billingCycle: string;
  autoRenew: boolean;
  details: any;
  metadata?: any;
  createdAt: Date;
  updatedAt: Date;
}

// 订阅状态枚举
export enum SubscriptionStatus {
  ACTIVE = 'active',
  PENDING = 'pending',
  CANCELED = 'canceled',
  EXPIRED = 'expired',
  SUSPENDED = 'suspended',
  TRIAL = 'trial'
}

// 计费周期枚举
export enum BillingCycle {
  MONTHLY = 'monthly',
  QUARTERLY = 'quarterly',
  SEMI_ANNUALLY = 'semi-annually',
  ANNUALLY = 'annually',
  ONE_TIME = 'one-time'
}

// 服务类型枚举
export enum ServiceType {
  PREMIUM = 'premium',
  BASIC = 'basic',
  STANDARD = 'standard',
  PROFESSIONAL = 'professional',
  ENTERPRISE = 'enterprise',
  FARM_ACTIVITY = 'farm-activity',
  FOOD_DELIVERY = 'food-delivery',
  HEALTH_CONSULTATION = 'health-consultation'
}

// 订阅模式
const subscriptionSchema = new Schema({
  userId: { type: String, required: true, index: true },
  serviceName: { type: String, required: true },
  serviceType: { 
    type: String, 
    required: true,
    enum: Object.values(ServiceType)
  },
  status: { 
    type: String, 
    required: true,
    enum: Object.values(SubscriptionStatus),
    default: SubscriptionStatus.PENDING
  },
  startDate: { type: String, required: true },
  endDate: { type: String, required: true },
  price: { type: Number, required: true },
  billingCycle: { 
    type: String, 
    required: true,
    enum: Object.values(BillingCycle)
  },
  autoRenew: { type: Boolean, default: false },
  details: { type: Schema.Types.Mixed, required: true },
  metadata: { type: Schema.Types.Mixed }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// 索引
subscriptionSchema.index({ userId: 1, status: 1 });
subscriptionSchema.index({ serviceType: 1 });
subscriptionSchema.index({ endDate: 1, status: 1, autoRenew: 1 });

// 虚拟字段
subscriptionSchema.virtual('isActive').get(function() {
  return this.status === SubscriptionStatus.ACTIVE;
});

subscriptionSchema.virtual('daysLeft').get(function() {
  const endDate = new Date(this.endDate);
  const now = new Date();
  const diffTime = endDate.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays > 0 ? diffDays : 0;
});

subscriptionSchema.virtual('formattedPrice').get(function() {
  return `¥${this.price.toFixed(2)}`;
});

// 创建模型
export const SubscriptionModel = mongoose.model<SubscriptionDocument>('Subscription', subscriptionSchema);

export default SubscriptionModel; 
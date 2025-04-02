import mongoose, { Document, Schema } from 'mongoose';

/**
 * 可穿戴设备数据模型接口
 */
export interface IWearableData extends Document {
  userId: mongoose.Types.ObjectId;
  deviceType: string;
  deviceId: string;
  dataType: 'heart_rate' | 'blood_pressure' | 'sleep' | 'activity' | 'stress' | 'oxygen' | 'temperature' | 'other';
  measurements: Array<{
    timestamp: Date;
    value: any;
    unit: string;
    metadata?: Record<string, any>;
  }>;
  analysisResults: {
    trends: Array<{
      type: string;
      description: string;
      severity: 'normal' | 'attention' | 'warning' | 'critical';
      startDate: Date;
      endDate: Date;
    }>;
    anomalies: Array<{
      type: string;
      description: string;
      timestamp: Date;
      value: any;
      threshold: any;
      severity: 'low' | 'medium' | 'high';
    }>;
    healthScore?: number;
    recommendations: string[];
  };
  integrationSource: string;
  createdAt: Date;
  updatedAt: Date;
  lastSyncTime: Date;
}

const measurementSchema = new Schema({
  timestamp: { type: Date, required: true },
  value: { type: Schema.Types.Mixed, required: true },
  unit: { type: String, required: true },
  metadata: { type: Map, of: Schema.Types.Mixed }
});

const trendSchema = new Schema({
  type: { type: String, required: true },
  description: { type: String, required: true },
  severity: { 
    type: String, 
    enum: ['normal', 'attention', 'warning', 'critical'],
    required: true 
  },
  startDate: { type: Date, required: true },
  endDate: { type: Date, required: true }
});

const anomalySchema = new Schema({
  type: { type: String, required: true },
  description: { type: String, required: true },
  timestamp: { type: Date, required: true },
  value: { type: Schema.Types.Mixed, required: true },
  threshold: { type: Schema.Types.Mixed, required: true },
  severity: { 
    type: String, 
    enum: ['low', 'medium', 'high'],
    required: true 
  }
});

const analysisResultsSchema = new Schema({
  trends: [trendSchema],
  anomalies: [anomalySchema],
  healthScore: { type: Number, min: 0, max: 100 },
  recommendations: [{ type: String }]
});

const wearableDataSchema = new Schema({
  userId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  deviceType: { type: String, required: true },
  deviceId: { type: String, required: true },
  dataType: { 
    type: String, 
    enum: ['heart_rate', 'blood_pressure', 'sleep', 'activity', 'stress', 'oxygen', 'temperature', 'other'],
    required: true 
  },
  measurements: [measurementSchema],
  analysisResults: analysisResultsSchema,
  integrationSource: { type: String, required: true },
  lastSyncTime: { type: Date, default: Date.now },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// 创建复合索引支持用户和设备类型的高效查询
wearableDataSchema.index({ userId: 1, deviceType: 1, dataType: 1 });
// 创建时间范围索引以支持时间序列查询
wearableDataSchema.index({ userId: 1, 'measurements.timestamp': 1 });

// 更新时自动更新updatedAt字段
wearableDataSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

export default mongoose.model<IWearableData>('WearableData', wearableDataSchema);
import mongoose, { Document, Schema } from 'mongoose';

// 产品来源信息
interface ProductOrigin {
  farmName: string;
  farmerId: string;
  farmerName: string;
  location: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  farmingType: string;
  certifications: string[];
}

// 生产环节信息
interface ProductionStage {
  stageName: string;
  startDate: Date;
  endDate?: Date;
  location: string;
  operators: string[];
  processes: string[];
  inputs?: any[];
  qualityTests?: any[];
  notes?: string;
  media?: string[];
  metadata?: any;
}

// 区块链记录
interface BlockchainRecord {
  blockchainType: string;
  transactionId: string;
  blockNumber?: number;
  timestamp: Date;
  dataHash: string;
  verificationUrl?: string;
}

// 溯源文档接口
export interface TraceabilityDocument extends Document {
  traceabilityId: string;
  productId: string;
  productName: string;
  productCategory: string;
  batchId: string;
  origin: ProductOrigin;
  harvestDate: Date;
  processingDate?: Date;
  expiryDate?: Date;
  productionStages: ProductionStage[];
  logisticRecords: any[];
  blockchainRecord?: BlockchainRecord;
  verificationStatus: string;
  qualityCertificates: string[];
  scanCount: number;
  metadata?: any;
  createdAt: Date;
  updatedAt: Date;
}

// 产品来源模式
const productOriginSchema = new Schema({
  farmName: { type: String, required: true },
  farmerId: { type: String, required: true },
  farmerName: { type: String, required: true },
  location: { type: String, required: true },
  coordinates: {
    latitude: { type: Number },
    longitude: { type: Number }
  },
  farmingType: { type: String, required: true },
  certifications: [{ type: String }]
});

// 生产环节模式
const productionStageSchema = new Schema({
  stageName: { type: String, required: true },
  startDate: { type: Date, required: true },
  endDate: { type: Date },
  location: { type: String, required: true },
  operators: [{ type: String, required: true }],
  processes: [{ type: String, required: true }],
  inputs: [{ type: Schema.Types.Mixed }],
  qualityTests: [{ type: Schema.Types.Mixed }],
  notes: { type: String },
  media: [{ type: String }],
  metadata: { type: Schema.Types.Mixed }
});

// 物流记录模式
const logisticRecordSchema = new Schema({
  transportType: { type: String, required: true },
  departureLocation: { type: String, required: true },
  departureTime: { type: Date, required: true },
  arrivalLocation: { type: String, required: true },
  arrivalTime: { type: Date },
  carrier: { type: String, required: true },
  temperature: { type: Number },
  humidity: { type: Number },
  trackingNumber: { type: String },
  status: { type: String, required: true },
  notes: { type: String },
  metadata: { type: Schema.Types.Mixed }
});

// 区块链记录模式
const blockchainRecordSchema = new Schema({
  blockchainType: { type: String, required: true },
  transactionId: { type: String, required: true, index: true },
  blockNumber: { type: Number },
  timestamp: { type: Date, required: true },
  dataHash: { type: String, required: true },
  verificationUrl: { type: String }
});

// 溯源模式
const traceabilitySchema = new Schema({
  traceabilityId: { 
    type: String, 
    required: true, 
    unique: true,
    index: true
  },
  productId: { 
    type: String, 
    required: true,
    index: true
  },
  productName: { type: String, required: true },
  productCategory: { type: String, required: true },
  batchId: { type: String, required: true, index: true },
  origin: { type: productOriginSchema, required: true },
  harvestDate: { type: Date, required: true },
  processingDate: { type: Date },
  expiryDate: { type: Date },
  productionStages: [{ type: productionStageSchema, required: true }],
  logisticRecords: [{ type: logisticRecordSchema }],
  blockchainRecord: { type: blockchainRecordSchema },
  verificationStatus: { 
    type: String, 
    required: true,
    enum: ['verified', 'pending', 'failed'],
    default: 'pending',
    index: true
  },
  qualityCertificates: [{ type: String }],
  scanCount: { type: Number, default: 0 },
  metadata: { type: Schema.Types.Mixed }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// 生成溯源ID
traceabilitySchema.pre('save', async function(next) {
  if (this.isNew && !this.traceabilityId) {
    // 生成格式为 TR-{产品类别首字母}-{年月日}-{随机数} 的溯源ID
    const date = new Date();
    const dateStr = `${date.getFullYear()}${(date.getMonth() + 1).toString().padStart(2, '0')}${date.getDate().toString().padStart(2, '0')}`;
    const categoryPrefix = this.productCategory.substring(0, 2).toUpperCase();
    const randomPart = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
    
    this.traceabilityId = `TR-${categoryPrefix}-${dateStr}-${randomPart}`;
  }
  next();
});

// 虚拟字段
traceabilitySchema.virtual('isExpired').get(function() {
  if (!this.expiryDate) return false;
  return new Date() > this.expiryDate;
});

traceabilitySchema.virtual('productionDuration').get(function() {
  if (!this.productionStages || this.productionStages.length === 0) return null;
  
  const firstStage = this.productionStages[0];
  const lastStage = this.productionStages[this.productionStages.length - 1];
  
  if (!firstStage.startDate || !lastStage.endDate) return null;
  
  const startDate = new Date(firstStage.startDate);
  const endDate = new Date(lastStage.endDate);
  
  return (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24); // 返回天数
});

// 索引
traceabilitySchema.index({ harvestDate: -1 });
traceabilitySchema.index({ expiryDate: 1 });
traceabilitySchema.index({ 'origin.farmName': 1 });
traceabilitySchema.index({ 'origin.location': 1 });

// 创建模型
export const TraceabilityModel = mongoose.model<TraceabilityDocument>('Traceability', traceabilitySchema);

export default TraceabilityModel; 
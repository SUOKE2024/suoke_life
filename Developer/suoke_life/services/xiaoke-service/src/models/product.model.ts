import mongoose, { Document, Schema } from 'mongoose';

// 生产者信息
interface Producer {
  id: string;
  name: string;
  location: string;
  contact: string;
}

// TCM特性
interface TcmProperties {
  nature?: string;
  taste?: string[];
  meridians?: string[];
  effects?: string[];
}

// 季节性信息
interface Seasonality {
  peak: string[];
  available: string[];
}

// 产品文档类型
export interface ProductDocument extends Document {
  name: string;
  description: string;
  category: string;
  price: number;
  unit: string;
  stock: number;
  images: string[];
  producer: Producer;
  certifications: string[];
  nutritionFacts: any;
  tcmProperties?: TcmProperties;
  harvestDate?: Date;
  expiryDate?: Date;
  storageConditions?: string;
  seasonality?: Seasonality;
  traceabilityId?: string;
  blockchainVerified?: boolean;
  metadata?: any;
  createdAt: Date;
  updatedAt: Date;
}

// 生产者信息模式
const producerSchema = new Schema({
  id: { type: String, required: true },
  name: { type: String, required: true },
  location: { type: String, required: true },
  contact: { type: String, required: true }
});

// TCM特性模式
const tcmPropertiesSchema = new Schema({
  nature: { type: String, enum: ['寒', '凉', '平', '温', '热'] },
  taste: [{ type: String, enum: ['酸', '苦', '甘', '辛', '咸'] }],
  meridians: [{ type: String }],
  effects: [{ type: String }]
});

// 季节性信息模式
const seasonalitySchema = new Schema({
  peak: [{ type: String }],
  available: [{ type: String }]
});

// 产品模式
const productSchema = new Schema({
  name: { type: String, required: true, index: true },
  description: { type: String, required: true },
  category: { type: String, required: true, index: true },
  price: { type: Number, required: true },
  unit: { type: String, required: true },
  stock: { type: Number, default: 0 },
  images: [{ type: String }],
  producer: { type: producerSchema, required: true },
  certifications: [{ type: String }],
  nutritionFacts: { type: Schema.Types.Mixed },
  tcmProperties: { type: tcmPropertiesSchema },
  harvestDate: { type: Date },
  expiryDate: { type: Date },
  storageConditions: { type: String },
  seasonality: { type: seasonalitySchema },
  traceabilityId: { type: String, index: true },
  blockchainVerified: { type: Boolean, default: false },
  metadata: { type: Schema.Types.Mixed }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// 索引
productSchema.index({ name: 'text', description: 'text' });
productSchema.index({ category: 1, 'tcmProperties.nature': 1 });
productSchema.index({ category: 1, 'tcmProperties.taste': 1 });
productSchema.index({ 'metadata.solarTerms': 1 });
productSchema.index({ 'producer.location': 1 });

// 虚拟字段
productSchema.virtual('isInStock').get(function() {
  return this.stock > 0;
});

productSchema.virtual('priceFormatted').get(function() {
  return `¥${this.price.toFixed(2)}`;
});

// 创建模型
export const ProductModel = mongoose.model<ProductDocument>('Product', productSchema);

export default ProductModel; 
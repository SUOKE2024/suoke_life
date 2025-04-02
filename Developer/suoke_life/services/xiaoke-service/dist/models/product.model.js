"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProductModel = void 0;
const mongoose_1 = __importStar(require("mongoose"));
// 生产者信息模式
const producerSchema = new mongoose_1.Schema({
    id: { type: String, required: true },
    name: { type: String, required: true },
    location: { type: String, required: true },
    contact: { type: String, required: true }
});
// TCM特性模式
const tcmPropertiesSchema = new mongoose_1.Schema({
    nature: { type: String, enum: ['寒', '凉', '平', '温', '热'] },
    taste: [{ type: String, enum: ['酸', '苦', '甘', '辛', '咸'] }],
    meridians: [{ type: String }],
    effects: [{ type: String }]
});
// 季节性信息模式
const seasonalitySchema = new mongoose_1.Schema({
    peak: [{ type: String }],
    available: [{ type: String }]
});
// 产品模式
const productSchema = new mongoose_1.Schema({
    name: { type: String, required: true, index: true },
    description: { type: String, required: true },
    category: { type: String, required: true, index: true },
    price: { type: Number, required: true },
    unit: { type: String, required: true },
    stock: { type: Number, default: 0 },
    images: [{ type: String }],
    producer: { type: producerSchema, required: true },
    certifications: [{ type: String }],
    nutritionFacts: { type: mongoose_1.Schema.Types.Mixed },
    tcmProperties: { type: tcmPropertiesSchema },
    harvestDate: { type: Date },
    expiryDate: { type: Date },
    storageConditions: { type: String },
    seasonality: { type: seasonalitySchema },
    traceabilityId: { type: String, index: true },
    blockchainVerified: { type: Boolean, default: false },
    metadata: { type: mongoose_1.Schema.Types.Mixed }
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
productSchema.virtual('isInStock').get(function () {
    return this.stock > 0;
});
productSchema.virtual('priceFormatted').get(function () {
    return `¥${this.price.toFixed(2)}`;
});
// 创建模型
exports.ProductModel = mongoose_1.default.model('Product', productSchema);
exports.default = exports.ProductModel;

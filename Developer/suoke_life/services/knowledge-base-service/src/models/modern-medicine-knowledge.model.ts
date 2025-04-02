/**
 * 现代医学知识模型
 */
import mongoose, { Document, Schema } from 'mongoose';
import { KnowledgeEntry } from './knowledge-entry.model';

// 医学体系枚举
export enum MedicalSystem {
  INTERNAL = 'internal',
  SURGERY = 'surgery',
  GYNECOLOGY = 'gynecology',
  PEDIATRICS = 'pediatrics',
  PREVENTIVE = 'preventive',
  NUTRITION = 'nutrition',
  PSYCHOLOGY = 'psychology',
  OTHER = 'other'
}

// 研究支持程度枚举
export enum ResearchSupportLevel {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
  UNCONFIRMED = 'unconfirmed'
}

// 临床试验接口
export interface ClinicalTrial {
  name: string;
  url: string;
  year: number;
  outcome: string;
}

// 现代医学知识接口
export interface ModernMedicineKnowledge extends KnowledgeEntry {
  medicalSystem: MedicalSystem;
  researchSupport: ResearchSupportLevel;
  references?: string[];
  clinicalTrials?: ClinicalTrial[];
}

// 现代医学知识文档接口
export interface ModernMedicineKnowledgeDocument extends ModernMedicineKnowledge, Document {}

// 临床试验模式
const clinicalTrialSchema = new Schema<ClinicalTrial>(
  {
    name: { type: String, required: true },
    url: { type: String, required: true },
    year: { type: Number, required: true },
    outcome: { type: String, required: true }
  },
  { _id: false }
);

// 现代医学知识模式
const modernMedicineKnowledgeSchema = new Schema<ModernMedicineKnowledgeDocument>(
  {
    title: { type: String, required: true, index: true },
    content: { type: String, required: true },
    summary: { type: String },
    categories: [{ type: Schema.Types.ObjectId, ref: 'Category', required: true }],
    tags: [{ type: Schema.Types.ObjectId, ref: 'Tag' }],
    medicalSystem: { 
      type: String, 
      required: true, 
      enum: Object.values(MedicalSystem),
      index: true
    },
    researchSupport: { 
      type: String, 
      required: true, 
      enum: Object.values(ResearchSupportLevel),
      index: true
    },
    references: [{ type: String }],
    clinicalTrials: [clinicalTrialSchema],
    vectorized: { type: Boolean, default: false },
    source: { type: String },
    attributes: { type: Map, of: Schema.Types.Mixed },
    createdBy: { type: Schema.Types.ObjectId, ref: 'User' },
    updatedBy: { type: Schema.Types.ObjectId, ref: 'User' }
  },
  {
    timestamps: true,
    collection: 'modern_medicine_knowledge'
  }
);

// 创建全文搜索索引
modernMedicineKnowledgeSchema.index(
  { title: 'text', content: 'text', summary: 'text', 'references': 'text', 'clinicalTrials.name': 'text', 'clinicalTrials.outcome': 'text' },
  { 
    weights: {
      title: 10,
      summary: 5,
      content: 3,
      'references': 1,
      'clinicalTrials.name': 1,
      'clinicalTrials.outcome': 1
    },
    name: 'modern_medicine_text_index'
  }
);

// 导出模型
export const ModernMedicineKnowledgeModel = (mongoose.models.ModernMedicineKnowledge as mongoose.Model<ModernMedicineKnowledgeDocument>) || 
  mongoose.model<ModernMedicineKnowledgeDocument>('ModernMedicineKnowledge', modernMedicineKnowledgeSchema);
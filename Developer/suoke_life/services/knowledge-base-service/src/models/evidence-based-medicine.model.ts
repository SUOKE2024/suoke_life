import mongoose, { Document, Schema } from 'mongoose';

/**
 * 循证医学知识模型接口
 */
export interface IEvidenceBasedMedicine extends Document {
  title: string;
  description: string;
  content: string;
  clinicalQuestion: {
    population: string;
    intervention: string;
    comparison?: string;
    outcome: string;
    timeframe?: string;
  };
  evidenceLevel: 'systematic_review' | 'rct' | 'cohort_study' | 'case_control' | 'case_series' | 'expert_opinion' | 'guideline';
  evidenceQuality: 'high' | 'moderate' | 'low' | 'very_low';
  recommendationStrength: 'strong' | 'conditional' | 'weak' | 'against' | 'insufficient';
  clinicalImplications: string[];
  patientValues: string[];
  researchGaps: string[];
  studySummaries: Array<{
    studyType: string;
    sampleSize: number;
    population: string;
    methods: string;
    results: string;
    limitations: string[];
    citation: string;
  }>;
  guidelineRecommendations: Array<{
    organization: string;
    year: number;
    recommendation: string;
    evidenceBasis: string;
  }>;
  categories: mongoose.Types.ObjectId[];
  tags: mongoose.Types.ObjectId[];
  lastUpdated: Date;
  createdAt: Date;
  updatedAt: Date;
  confidenceInterval?: {
    lower: number;
    upper: number;
    unit: string;
  };
  metaAnalysisResults?: {
    effectSize: number;
    pValue: number;
    heterogeneity: string;
  };
}

const clinicalQuestionSchema = new Schema({
  population: { type: String, required: true },
  intervention: { type: String, required: true },
  comparison: { type: String },
  outcome: { type: String, required: true },
  timeframe: { type: String }
});

const confidenceIntervalSchema = new Schema({
  lower: { type: Number, required: true },
  upper: { type: Number, required: true },
  unit: { type: String, required: true }
});

const metaAnalysisResultsSchema = new Schema({
  effectSize: { type: Number, required: true },
  pValue: { type: Number, required: true },
  heterogeneity: { type: String, required: true }
});

const studySummarySchema = new Schema({
  studyType: { type: String, required: true },
  sampleSize: { type: Number, required: true },
  population: { type: String, required: true },
  methods: { type: String, required: true },
  results: { type: String, required: true },
  limitations: [{ type: String }],
  citation: { type: String, required: true }
});

const guidelineRecommendationSchema = new Schema({
  organization: { type: String, required: true },
  year: { type: Number, required: true },
  recommendation: { type: String, required: true },
  evidenceBasis: { type: String, required: true }
});

const evidenceBasedMedicineSchema = new Schema({
  title: { type: String, required: true, index: true },
  description: { type: String, required: true },
  content: { type: String, required: true },
  clinicalQuestion: clinicalQuestionSchema,
  evidenceLevel: { 
    type: String, 
    enum: ['systematic_review', 'rct', 'cohort_study', 'case_control', 'case_series', 'expert_opinion', 'guideline'],
    required: true 
  },
  evidenceQuality: { 
    type: String, 
    enum: ['high', 'moderate', 'low', 'very_low'],
    required: true 
  },
  recommendationStrength: { 
    type: String, 
    enum: ['strong', 'conditional', 'weak', 'against', 'insufficient'],
    required: true 
  },
  clinicalImplications: [{ type: String, required: true }],
  patientValues: [{ type: String }],
  researchGaps: [{ type: String }],
  studySummaries: [studySummarySchema],
  guidelineRecommendations: [guidelineRecommendationSchema],
  confidenceInterval: confidenceIntervalSchema,
  metaAnalysisResults: metaAnalysisResultsSchema,
  categories: [{ type: Schema.Types.ObjectId, ref: 'Category' }],
  tags: [{ type: Schema.Types.ObjectId, ref: 'Tag' }],
  lastUpdated: { type: Date, required: true },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// 添加文本索引以支持全文搜索
evidenceBasedMedicineSchema.index({
  title: 'text',
  description: 'text',
  content: 'text',
  'clinicalQuestion.population': 'text',
  'clinicalQuestion.intervention': 'text',
  'clinicalQuestion.outcome': 'text'
});

// 添加索引以支持按证据级别和推荐强度查询
evidenceBasedMedicineSchema.index({ evidenceLevel: 1, evidenceQuality: 1, recommendationStrength: 1 });

// 更新时自动更新updatedAt字段
evidenceBasedMedicineSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

export default mongoose.model<IEvidenceBasedMedicine>('EvidenceBasedMedicine', evidenceBasedMedicineSchema);
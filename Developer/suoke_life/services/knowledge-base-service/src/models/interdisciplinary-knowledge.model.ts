import mongoose, { Document, Schema } from 'mongoose';

/**
 * 跨学科健康知识模型接口
 */
export interface IInterdisciplinaryKnowledge extends Document {
  title: string;
  description: string;
  content: string;
  primaryDiscipline: string;
  relatedDisciplines: string[];
  knowledgeNetwork: Array<{
    conceptName: string;
    relatedConcepts: Array<{
      name: string;
      relationship: string;
      disciplineOrigin: string;
      strengthOfAssociation: 'strong' | 'moderate' | 'weak';
    }>;
  }>;
  integratedPrinciples: Array<{
    principle: string;
    description: string;
    disciplinaryBasis: string[];
    applications: string[];
  }>;
  researchEvidence: Array<{
    finding: string;
    supportingStudies: Array<{
      citation: string;
      evidenceStrength: 'high' | 'moderate' | 'low';
      methodology: string;
    }>;
    practicalImplications: string[];
  }>;
  clinicalApplications: Array<{
    scenario: string;
    interdisciplinaryApproach: string;
    outcomes: string[];
    challenges: string[];
  }>;
  categories: mongoose.Types.ObjectId[];
  tags: mongoose.Types.ObjectId[];
  createdAt: Date;
  updatedAt: Date;
  reviewStatus: 'peer_reviewed' | 'expert_reviewed' | 'pending_review';
}

const relatedConceptSchema = new Schema({
  name: { type: String, required: true },
  relationship: { type: String, required: true },
  disciplineOrigin: { type: String, required: true },
  strengthOfAssociation: { 
    type: String, 
    enum: ['strong', 'moderate', 'weak'],
    required: true 
  }
});

const knowledgeNetworkSchema = new Schema({
  conceptName: { type: String, required: true },
  relatedConcepts: [relatedConceptSchema]
});

const integratedPrincipleSchema = new Schema({
  principle: { type: String, required: true },
  description: { type: String, required: true },
  disciplinaryBasis: [{ type: String, required: true }],
  applications: [{ type: String }]
});

const supportingStudySchema = new Schema({
  citation: { type: String, required: true },
  evidenceStrength: { 
    type: String, 
    enum: ['high', 'moderate', 'low'],
    required: true 
  },
  methodology: { type: String, required: true }
});

const researchEvidenceSchema = new Schema({
  finding: { type: String, required: true },
  supportingStudies: [supportingStudySchema],
  practicalImplications: [{ type: String }]
});

const clinicalApplicationSchema = new Schema({
  scenario: { type: String, required: true },
  interdisciplinaryApproach: { type: String, required: true },
  outcomes: [{ type: String }],
  challenges: [{ type: String }]
});

const interdisciplinaryKnowledgeSchema = new Schema({
  title: { type: String, required: true, index: true },
  description: { type: String, required: true },
  content: { type: String, required: true },
  primaryDiscipline: { type: String, required: true },
  relatedDisciplines: [{ type: String, required: true }],
  knowledgeNetwork: [knowledgeNetworkSchema],
  integratedPrinciples: [integratedPrincipleSchema],
  researchEvidence: [researchEvidenceSchema],
  clinicalApplications: [clinicalApplicationSchema],
  categories: [{ type: Schema.Types.ObjectId, ref: 'Category' }],
  tags: [{ type: Schema.Types.ObjectId, ref: 'Tag' }],
  reviewStatus: { 
    type: String, 
    enum: ['peer_reviewed', 'expert_reviewed', 'pending_review'],
    default: 'pending_review'
  },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// 添加文本索引以支持全文搜索
interdisciplinaryKnowledgeSchema.index({
  title: 'text',
  description: 'text',
  content: 'text',
  primaryDiscipline: 'text',
  relatedDisciplines: 'text',
  'knowledgeNetwork.conceptName': 'text',
  'integratedPrinciples.principle': 'text',
  'researchEvidence.finding': 'text'
});

// 添加索引以支持按学科查询
interdisciplinaryKnowledgeSchema.index({ primaryDiscipline: 1, relatedDisciplines: 1 });

// 更新时自动更新updatedAt字段
interdisciplinaryKnowledgeSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

export default mongoose.model<IInterdisciplinaryKnowledge>('InterdisciplinaryKnowledge', interdisciplinaryKnowledgeSchema);
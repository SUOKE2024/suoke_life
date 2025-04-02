/**
 * 迁移脚本：添加知识审核表
 */
import mongoose from 'mongoose';
import logger from '../utils/logger';

/**
 * 知识审核模型定义
 */
const CommentSchema = new mongoose.Schema({
  content: { type: String, required: true },
  position: { type: String },
  createdBy: { type: String, required: true },
  createdAt: { type: Date, default: Date.now }
}, { _id: false });

const SuggestionSchema = new mongoose.Schema({
  field: { type: String, required: true },
  currentValue: { type: mongoose.Schema.Types.Mixed },
  suggestedValue: { type: mongoose.Schema.Types.Mixed },
  reason: { type: String, required: true },
  status: { 
    type: String, 
    enum: ['pending', 'accepted', 'rejected'],
    default: 'pending'
  }
}, { _id: false });

const KnowledgeReviewSchema = new mongoose.Schema({
  knowledgeId: { 
    type: mongoose.Schema.Types.ObjectId, 
    required: true,
    index: true
  },
  knowledgeType: { 
    type: String, 
    required: true,
    enum: ['nutrition', 'lifestyle', 'medical', 'tcm', 'environmentalHealth', 'psychologicalHealth'],
    index: true
  },
  versionId: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'KnowledgeVersion',
    required: true,
    index: true
  },
  versionNumber: { 
    type: Number, 
    required: true
  },
  title: { 
    type: String, 
    required: true 
  },
  reviewType: { 
    type: String,
    enum: ['initial', 'update', 'regular', 'expert'],
    default: 'initial',
    index: true
  },
  status: { 
    type: String,
    enum: ['pending', 'inProgress', 'completed', 'canceled'],
    default: 'pending',
    index: true
  },
  result: { 
    type: String,
    enum: ['approved', 'approvedWithChanges', 'rejected', 'needsRevision', 'pending'],
    default: 'pending',
    index: true
  },
  reviewerIds: [{ 
    type: String,
    index: true
  }],
  assignedAt: { 
    type: Date, 
    default: Date.now 
  },
  deadline: { 
    type: Date 
  },
  completedAt: { 
    type: Date 
  },
  comments: [CommentSchema],
  suggestions: [SuggestionSchema],
  overallComment: { 
    type: String 
  },
  accuracy: { 
    type: Number, 
    min: 0, 
    max: 5 
  },
  relevance: { 
    type: Number, 
    min: 0, 
    max: 5 
  },
  clarity: { 
    type: Number, 
    min: 0, 
    max: 5 
  },
  completeness: { 
    type: Number, 
    min: 0, 
    max: 5 
  },
  createdBy: { 
    type: String, 
    required: true 
  },
  createdAt: { 
    type: Date, 
    default: Date.now,
    index: true
  },
  updatedAt: { 
    type: Date, 
    default: Date.now 
  }
}, { 
  timestamps: true,
  versionKey: false
});

// 创建复合索引
KnowledgeReviewSchema.index({ knowledgeId: 1, versionNumber: 1 });

const migration = {
  version: 4,
  name: 'add_knowledge_review',
  
  /**
   * 创建知识审核表
   */
  up: async (): Promise<void> => {
    try {
      logger.info('开始创建知识审核表');
      
      // 检查集合是否存在
      const collections = await mongoose.connection.db.listCollections({ name: 'knowledgereviews' }).toArray();
      
      if (collections.length > 0) {
        logger.info('知识审核表已存在，跳过创建');
        return;
      }
      
      // 创建模型
      const KnowledgeReview = mongoose.model('KnowledgeReview', KnowledgeReviewSchema);
      
      // 创建索引
      await KnowledgeReview.createIndexes();
      
      logger.info('知识审核表创建成功');
    } catch (error) {
      logger.error('创建知识审核表失败', { error: (error as Error).message });
      throw error;
    }
  },
  
  /**
   * 删除知识审核表
   */
  down: async (): Promise<void> => {
    try {
      logger.info('开始删除知识审核表');
      
      // 检查集合是否存在
      const collections = await mongoose.connection.db.listCollections({ name: 'knowledgereviews' }).toArray();
      
      if (collections.length === 0) {
        logger.info('知识审核表不存在，跳过删除');
        return;
      }
      
      // 删除集合
      await mongoose.connection.db.dropCollection('knowledgereviews');
      
      logger.info('知识审核表删除成功');
    } catch (error) {
      logger.error('删除知识审核表失败', { error: (error as Error).message });
      throw error;
    }
  }
};

export default migration;
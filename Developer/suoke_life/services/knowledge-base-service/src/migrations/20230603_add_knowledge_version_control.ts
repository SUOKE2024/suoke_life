/**
 * 迁移脚本：添加知识版本控制表
 */
import mongoose from 'mongoose';
import logger from '../utils/logger';

/**
 * 知识版本控制模型定义
 */
const ChangeLogItemSchema = new mongoose.Schema({
  field: { type: String, required: true },
  oldValue: { type: mongoose.Schema.Types.Mixed },
  newValue: { type: mongoose.Schema.Types.Mixed },
  description: { type: String }
}, { _id: false });

const KnowledgeVersionSchema = new mongoose.Schema({
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
  versionNumber: { 
    type: Number, 
    required: true,
    index: true
  },
  title: { 
    type: String, 
    required: true 
  },
  description: { 
    type: String 
  },
  changeLog: { 
    type: [ChangeLogItemSchema], 
    default: []
  },
  content: { 
    type: mongoose.Schema.Types.Mixed, 
    required: true 
  },
  status: { 
    type: String, 
    required: true,
    enum: ['draft', 'published', 'archived', 'deprecated'],
    default: 'draft',
    index: true
  },
  publishedAt: { 
    type: Date 
  },
  createdAt: { 
    type: Date, 
    default: Date.now,
    index: true
  },
  updatedAt: { 
    type: Date, 
    default: Date.now 
  },
  createdBy: { 
    type: String, 
    required: true 
  },
  reviewStatus: { 
    type: String,
    enum: ['pending', 'approved', 'rejected', 'none'],
    default: 'none',
    index: true
  },
  reviewedBy: { 
    type: String 
  },
  reviewedAt: { 
    type: Date 
  },
  reviewComments: { 
    type: String 
  },
  isCurrentVersion: { 
    type: Boolean, 
    default: false,
    index: true
  }
}, { 
  timestamps: true,
  versionKey: false
});

// 创建复合索引
KnowledgeVersionSchema.index({ knowledgeId: 1, versionNumber: 1 }, { unique: true });

const migration = {
  version: 3,
  name: 'add_knowledge_version_control',
  
  /**
   * 创建知识版本控制表
   */
  up: async (): Promise<void> => {
    try {
      logger.info('开始创建知识版本控制表');
      
      // 检查集合是否存在
      const collections = await mongoose.connection.db.listCollections({ name: 'knowledgeversions' }).toArray();
      
      if (collections.length > 0) {
        logger.info('知识版本控制表已存在，跳过创建');
        return;
      }
      
      // 创建模型
      const KnowledgeVersion = mongoose.model('KnowledgeVersion', KnowledgeVersionSchema);
      
      // 创建索引
      await KnowledgeVersion.createIndexes();
      
      logger.info('知识版本控制表创建成功');
    } catch (error) {
      logger.error('创建知识版本控制表失败', { error: (error as Error).message });
      throw error;
    }
  },
  
  /**
   * 删除知识版本控制表
   */
  down: async (): Promise<void> => {
    try {
      logger.info('开始删除知识版本控制表');
      
      // 检查集合是否存在
      const collections = await mongoose.connection.db.listCollections({ name: 'knowledgeversions' }).toArray();
      
      if (collections.length === 0) {
        logger.info('知识版本控制表不存在，跳过删除');
        return;
      }
      
      // 删除集合
      await mongoose.connection.db.dropCollection('knowledgeversions');
      
      logger.info('知识版本控制表删除成功');
    } catch (error) {
      logger.error('删除知识版本控制表失败', { error: (error as Error).message });
      throw error;
    }
  }
};

export default migration;
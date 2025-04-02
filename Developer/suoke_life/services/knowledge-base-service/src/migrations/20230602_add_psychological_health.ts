/**
 * 迁移脚本：添加心理健康知识表
 */
import mongoose from 'mongoose';
import logger from '../utils/logger';

/**
 * 心理健康知识模型定义
 */
const ResourceSchema = new mongoose.Schema({
  type: { type: String, required: true },
  name: { type: String, required: true },
  description: { type: String, required: true },
  url: { type: String }
}, { _id: false });

const ReferenceSchema = new mongoose.Schema({
  author: { type: String, required: true },
  title: { type: String, required: true },
  source: { type: String, required: true },
  year: { type: Number, required: true },
  url: { type: String }
}, { _id: false });

const PsychologicalHealthSchema = new mongoose.Schema({
  title: { 
    type: String, 
    required: true, 
    trim: true,
    index: true
  },
  description: { 
    type: String, 
    required: true 
  },
  content: { 
    type: String, 
    required: true 
  },
  issueType: { 
    type: String, 
    required: true,
    index: true
  },
  symptoms: { 
    type: [String], 
    default: [] 
  },
  possibleCauses: { 
    type: [String], 
    default: [] 
  },
  interventionMethods: { 
    type: [String], 
    default: [],
    index: true
  },
  treatmentMethods: { 
    type: [String], 
    default: [] 
  },
  selfHelpMeasures: { 
    type: [String], 
    default: [] 
  },
  targetAgeGroups: { 
    type: [String], 
    default: [],
    index: true
  },
  resources: { 
    type: [ResourceSchema], 
    default: [] 
  },
  applicableScenarios: { 
    type: [String], 
    default: [] 
  },
  expectedOutcomes: { 
    type: [String], 
    default: [] 
  },
  expertAdvice: { 
    type: String 
  },
  keywords: { 
    type: [String], 
    default: [],
    index: true
  },
  references: { 
    type: [ReferenceSchema], 
    default: [] 
  },
  relatedKnowledge: [{ 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Knowledge' 
  }],
  tags: [{ 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Tag' 
  }],
  categories: [{ 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Category' 
  }],
  createdAt: { 
    type: Date, 
    default: Date.now,
    index: true
  },
  updatedAt: { 
    type: Date, 
    default: Date.now,
    index: true
  },
  createdBy: { 
    type: String 
  },
  version: { 
    type: Number, 
    default: 1,
    required: true
  }
}, { 
  timestamps: true,
  versionKey: false
});

// 创建全文搜索索引
PsychologicalHealthSchema.index({ 
  title: 'text', 
  description: 'text', 
  content: 'text',
  keywords: 'text',
  symptoms: 'text',
  treatmentMethods: 'text'
});

const migration = {
  version: 2,
  name: 'add_psychological_health',
  
  /**
   * 创建心理健康知识表
   */
  up: async (): Promise<void> => {
    try {
      logger.info('开始创建心理健康知识表');
      
      // 检查集合是否存在
      const collections = await mongoose.connection.db.listCollections({ name: 'psychologicalhealths' }).toArray();
      
      if (collections.length > 0) {
        logger.info('心理健康知识表已存在，跳过创建');
        return;
      }
      
      // 创建模型
      const PsychologicalHealth = mongoose.model('PsychologicalHealth', PsychologicalHealthSchema);
      
      // 创建索引
      await PsychologicalHealth.createIndexes();
      
      logger.info('心理健康知识表创建成功');
    } catch (error) {
      logger.error('创建心理健康知识表失败', { error: (error as Error).message });
      throw error;
    }
  },
  
  /**
   * 删除心理健康知识表
   */
  down: async (): Promise<void> => {
    try {
      logger.info('开始删除心理健康知识表');
      
      // 检查集合是否存在
      const collections = await mongoose.connection.db.listCollections({ name: 'psychologicalhealths' }).toArray();
      
      if (collections.length === 0) {
        logger.info('心理健康知识表不存在，跳过删除');
        return;
      }
      
      // 删除集合
      await mongoose.connection.db.dropCollection('psychologicalhealths');
      
      logger.info('心理健康知识表删除成功');
    } catch (error) {
      logger.error('删除心理健康知识表失败', { error: (error as Error).message });
      throw error;
    }
  }
};

export default migration;
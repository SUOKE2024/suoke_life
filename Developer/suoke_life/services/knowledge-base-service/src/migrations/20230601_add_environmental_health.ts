/**
 * 迁移脚本：添加环境健康知识表
 */
import mongoose from 'mongoose';
import logger from '../utils/logger';

/**
 * 环境健康知识模型定义
 */
const MonitoringIndicatorSchema = new mongoose.Schema({
  name: { type: String, required: true },
  unit: { type: String, required: true },
  safeRange: { type: String, required: true },
  description: { type: String, required: true }
}, { _id: false });

const ReferenceSchema = new mongoose.Schema({
  author: { type: String, required: true },
  title: { type: String, required: true },
  source: { type: String, required: true },
  year: { type: Number, required: true },
  url: { type: String }
}, { _id: false });

const PolicySchema = new mongoose.Schema({
  name: { type: String, required: true },
  issuer: { type: String, required: true },
  year: { type: Number, required: true },
  description: { type: String, required: true },
  url: { type: String }
}, { _id: false });

const EnvironmentalHealthSchema = new mongoose.Schema({
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
  environmentType: { 
    type: String, 
    required: true,
    index: true
  },
  pollutantType: { 
    type: [String], 
    default: [],
    index: true
  },
  healthImpacts: { 
    type: [String], 
    default: [] 
  },
  riskLevel: { 
    type: Number, 
    required: true,
    min: 1,
    max: 5,
    index: true
  },
  vulnerableGroups: { 
    type: [String], 
    default: [] 
  },
  protectiveMeasures: { 
    type: [String], 
    default: [] 
  },
  preventiveAdvice: { 
    type: [String], 
    default: [] 
  },
  relatedDiseases: { 
    type: [String], 
    default: [] 
  },
  regionSpecific: { 
    type: [String], 
    default: [],
    index: true
  },
  seasonalEffects: { 
    type: [String], 
    default: [] 
  },
  monitoringIndicators: { 
    type: [MonitoringIndicatorSchema], 
    default: [] 
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
  relatedPolicies: {
    type: [PolicySchema],
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
EnvironmentalHealthSchema.index({ 
  title: 'text', 
  description: 'text', 
  content: 'text',
  keywords: 'text',
  healthImpacts: 'text',
  pollutantType: 'text'
});

const migration = {
  version: 1,
  name: 'add_environmental_health',
  
  /**
   * 创建环境健康知识表
   */
  up: async (): Promise<void> => {
    try {
      logger.info('开始创建环境健康知识表');
      
      // 检查集合是否存在
      const collections = await mongoose.connection.db.listCollections({ name: 'environmentalhealths' }).toArray();
      
      if (collections.length > 0) {
        logger.info('环境健康知识表已存在，跳过创建');
        return;
      }
      
      // 创建模型
      const EnvironmentalHealth = mongoose.model('EnvironmentalHealth', EnvironmentalHealthSchema);
      
      // 创建索引
      await EnvironmentalHealth.createIndexes();
      
      logger.info('环境健康知识表创建成功');
    } catch (error) {
      logger.error('创建环境健康知识表失败', { error: (error as Error).message });
      throw error;
    }
  },
  
  /**
   * 删除环境健康知识表
   */
  down: async (): Promise<void> => {
    try {
      logger.info('开始删除环境健康知识表');
      
      // 检查集合是否存在
      const collections = await mongoose.connection.db.listCollections({ name: 'environmentalhealths' }).toArray();
      
      if (collections.length === 0) {
        logger.info('环境健康知识表不存在，跳过删除');
        return;
      }
      
      // 删除集合
      await mongoose.connection.db.dropCollection('environmentalhealths');
      
      logger.info('环境健康知识表删除成功');
    } catch (error) {
      logger.error('删除环境健康知识表失败', { error: (error as Error).message });
      throw error;
    }
  }
};

export default migration;
/**
 * 版本管理模型
 * 用于存储知识条目的历史版本
 */
import mongoose, { Schema } from 'mongoose';

// 版本记录模式定义
const VersionSchema = new Schema({
  // 知识类型（如knowledge, nutrition, tcm等）
  knowledgeType: { 
    type: String, 
    required: true,
    index: true
  },
  
  // 知识条目ID
  documentId: { 
    type: String, 
    required: true,
    index: true
  },
  
  // 版本号
  version: { 
    type: Number, 
    required: true 
  },
  
  // 版本的完整数据
  data: { 
    type: Schema.Types.Mixed, 
    required: true 
  },
  
  // 版本创建者
  createdBy: { 
    type: String 
  },
  
  // 创建时间
  createdAt: { 
    type: Date, 
    default: Date.now,
    index: true
  }
}, { 
  versionKey: false
});

// 创建联合索引确保版本号唯一性
VersionSchema.index({ 
  knowledgeType: 1, 
  documentId: 1, 
  version: 1 
}, { 
  unique: true 
});

const VersionModel = mongoose.model('Version', VersionSchema);

export default VersionModel;
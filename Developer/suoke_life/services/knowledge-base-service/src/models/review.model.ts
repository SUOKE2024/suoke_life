/**
 * 知识审核模型
 * 用于存储知识条目的审核记录
 */
import mongoose, { Schema } from 'mongoose';

// 审核记录模式定义
const ReviewSchema = new Schema({
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
  
  // 知识条目版本
  documentVersion: { 
    type: Number, 
    required: true 
  },
  
  // 审核状态: pending(待审核), approved(已通过), rejected(已拒绝)
  status: { 
    type: String, 
    enum: ['pending', 'approved', 'rejected'],
    default: 'pending',
    index: true
  },
  
  // 提交审核的用户ID
  submittedBy: { 
    type: String, 
    required: true 
  },
  
  // 提交审核时间
  submittedAt: { 
    type: Date, 
    default: Date.now,
    index: true
  },
  
  // 提交者备注
  submitterComments: { 
    type: String 
  },
  
  // 审核者ID
  reviewedBy: { 
    type: String 
  },
  
  // 审核时间
  reviewedAt: { 
    type: Date 
  },
  
  // 审核者备注
  reviewerComments: { 
    type: String 
  },
  
  // 审核内容（知识条目的完整数据）
  content: { 
    type: Schema.Types.Mixed, 
    required: true 
  }
}, { 
  timestamps: true,
  versionKey: false
});

const ReviewModel = mongoose.model('Review', ReviewSchema);

export default ReviewModel;
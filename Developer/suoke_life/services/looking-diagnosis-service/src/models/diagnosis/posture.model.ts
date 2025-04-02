import mongoose, { Schema, Document } from 'mongoose';

/**
 * 体态分析特征接口
 * 描述体态分析中提取的关键特征
 */
export interface PostureFeatures {
  // 基本姿态评估
  overallPosture: string;          // 整体姿态评价 (如"正常"、"前倾"、"后仰"等)
  shoulderAlignment: string;       // 肩部对称性 (如"对称"、"左高"、"右高"等)
  spineAlignment: string;          // 脊柱弯曲状态 (如"正常"、"左侧弯曲"、"右侧弯曲"等)
  hipAlignment: string;            // 骨盆对称性 (如"对称"、"左高"、"右高"等)
  
  // 特定姿态问题
  hasForwardHeadPosture: boolean;  // 是否存在前倾头
  hasRoundedShoulders: boolean;    // 是否存在圆肩
  hasSwaybBack: boolean;           // 是否存在腰椎过度前弯
  hasFlatBack: boolean;            // 是否存在脊柱平直
  
  // 偏差程度
  posturalDeviation: number;       // 姿态偏离度 (0-10分，0为正常)
  
  // 附加信息
  comments: string;                // 额外观察和评注
}

/**
 * 中医体质相关性接口
 * 描述体态与中医体质类型的关联情况
 */
export interface TCMImplication {
  concept: string;                 // 中医概念或体质类型
  confidence: number;              // 关联可信度 (0-1)
  explanation: string;             // 解释说明
}

/**
 * 体态分析结果接口
 * 定义体态分析的结果数据结构
 */
export interface PostureDiagnosis extends Document {
  diagnosisId: string;             // 诊断ID
  sessionId: string;               // 会话ID
  userId?: string;                 // 用户ID (可选)
  timestamp: Date;                 // 诊断时间戳
  
  // 图像信息
  imageUrl?: string;               // 图像URL (如果存储)
  imagePath?: string;              // 图像本地路径 (如果存储)
  
  // 分析结果
  features: PostureFeatures;       // 体态特征
  tcmImplications: TCMImplication[]; // 中医体质关联
  
  // 健康建议
  recommendations: string[];       // 建议列表
  
  // 元数据
  metadata: {
    captureTime?: Date;            // 图像捕获时间
    lightingCondition?: string;    // 光照条件
    processingSteps?: string[];    // 处理步骤记录
    dataVersion?: string;          // 数据版本
  };
  
  // 时间戳
  createdAt: Date;                 // 创建时间
  updatedAt: Date;                 // 更新时间
}

// 体态特征Schema
const PostureFeaturesSchema: Schema = new Schema({
  overallPosture: { type: String, required: true },
  shoulderAlignment: { type: String, required: true },
  spineAlignment: { type: String, required: true },
  hipAlignment: { type: String, required: true },
  
  hasForwardHeadPosture: { type: Boolean, default: false },
  hasRoundedShoulders: { type: Boolean, default: false },
  hasSwaybBack: { type: Boolean, default: false },
  hasFlatBack: { type: Boolean, default: false },
  
  posturalDeviation: { type: Number, default: 0 },
  comments: { type: String, default: '' }
});

// TCM含义Schema
const TCMImplicationSchema: Schema = new Schema({
  concept: { type: String, required: true },
  confidence: { type: Number, required: true },
  explanation: { type: String, required: true }
});

// 体态分析Schema
const PostureDiagnosisSchema: Schema = new Schema({
  diagnosisId: { type: String, required: true, unique: true },
  sessionId: { type: String, required: true },
  userId: { type: String },
  timestamp: { type: Date, default: Date.now },
  
  imageUrl: { type: String },
  imagePath: { type: String },
  
  features: { type: PostureFeaturesSchema, required: true },
  tcmImplications: { type: [TCMImplicationSchema], default: [] },
  
  recommendations: { type: [String], default: [] },
  
  metadata: {
    captureTime: { type: Date },
    lightingCondition: { type: String },
    processingSteps: { type: [String] },
    dataVersion: { type: String }
  }
}, {
  timestamps: true // 自动添加createdAt和updatedAt
});

// 创建并导出模型
export default mongoose.model<PostureDiagnosis>('PostureDiagnosis', PostureDiagnosisSchema); 
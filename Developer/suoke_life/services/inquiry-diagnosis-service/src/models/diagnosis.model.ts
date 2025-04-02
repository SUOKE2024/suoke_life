/**
 * 诊断结果模型
 * 表示对用户症状的完整诊断结果
 */
export interface Diagnosis {
  id: string;               // 诊断ID
  sessionId: string;        // 关联的会话ID
  userId: string;           // 用户ID
  patterns: DiagnosisPattern[]; // 辨别的证型
  recommendations: Recommendation[]; // 建议
  createdAt: Date;          // 创建时间
  updatedAt: Date;          // 更新时间
}

/**
 * 证型模型
 * 表示中医诊断中的一种证型
 */
export interface DiagnosisPattern {
  id: string;               // 证型ID
  name: string;             // 证型名称
  description: string;      // 证型描述
  confidence: number;       // 可信度(0-1)
  matchingSymptoms: string[]; // 匹配的症状
  references?: Reference[]; // 参考文献
}

/**
 * 推荐建议模型
 */
export interface Recommendation {
  id: string;               // 建议ID
  type: RecommendationType; // 建议类型
  content: string;          // 建议内容
  explanation?: string;     // 解释说明
  priority: number;         // 优先级(1-5)
  references?: Reference[]; // 参考文献
}

/**
 * 建议类型枚举
 */
export enum RecommendationType {
  LIFESTYLE = 'lifestyle',   // 生活方式
  DIET = 'diet',             // 饮食建议
  EXERCISE = 'exercise',     // 运动建议
  MEDICATION = 'medication', // 用药建议
  FURTHER_EXAMINATION = 'further_examination', // 进一步检查
  CONSULT_DOCTOR = 'consult_doctor', // 建议就医
  OTHER = 'other'            // 其他
}

/**
 * 参考文献接口
 */
export interface Reference {
  id: string;             // 参考文献ID
  title: string;          // 标题
  source: string;         // 来源
  link?: string;          // 链接
  confidence: number;     // 可信度(0-1)
}

/**
 * 健康记录模型
 */
export interface HealthRecord {
  id: string;                // 记录ID
  userId: string;            // 用户ID
  sessionId?: string;        // 关联的问诊会话ID
  diagnosisId?: string;      // 关联的诊断ID
  recordType: RecordType;    // 记录类型
  symptoms: string[];        // 症状列表
  patterns?: DiagnosisPattern[]; // 诊断的证型
  recommendations?: Recommendation[]; // 建议
  recordDate: Date;          // 记录日期
  notes?: string;            // 备注
  createdAt: Date;           // 创建时间
  updatedAt: Date;           // 更新时间
}

/**
 * 记录类型枚举
 */
export enum RecordType {
  INQUIRY = 'inquiry',       // 问诊记录
  SELF_REPORT = 'self_report', // 自我报告
  MEDICAL_EXAM = 'medical_exam', // 医疗检查
  FOLLOW_UP = 'follow_up'    // 随访记录
}
/**
 * 问诊会话模型
 * 表示用户和系统之间的一次问诊交互过程
 */
export interface InquirySession {
  id: string;               // 会话ID
  userId: string;           // 用户ID
  startTime: Date;          // 会话开始时间
  endTime?: Date;           // 会话结束时间
  status: SessionStatus;    // 会话状态
  patientInfo?: PatientInfo; // 患者信息
  preferences: SessionPreferences; // 会话偏好设置
  extractedSymptoms: string[]; // 从对话中提取的症状
  questions: InquiryQuestion[]; //, // 会话中的所有问题
  createdAt: Date;          // 创建时间
  updatedAt: Date;          // 更新时间
}

/**
 * 会话状态枚举
 */
export enum SessionStatus {
  ACTIVE = 'active',       // 活跃状态
  PAUSED = 'paused',       // 暂停状态
  COMPLETED = 'completed', // 已完成
  ABANDONED = 'abandoned'  // 已放弃
}

/**
 * 患者信息接口
 */
export interface PatientInfo {
  name?: string;           // 患者姓名
  age?: number;            // 患者年龄
  gender?: '男' | '女' | '其他'; // 患者性别
  medicalHistory?: string[]; // 病史
}

/**
 * 会话偏好设置接口
 */
export interface SessionPreferences {
  language: '中文' | '英文';  // 语言偏好
  responseType: '简洁' | '详细'; // 回答类型
  includeReferences: boolean; // 是否包含参考文献
}

/**
 * 问诊问题接口
 */
export interface InquiryQuestion {
  id: string;             // 问题ID
  sessionId: string;      // 所属会话ID
  question: string;       // 问题内容
  answer?: string;        // 回答内容
  extractedSymptoms?: string[]; // 从该问题中提取的症状
  references?: Reference[]; // 参考文献
  timestamp: Date;        // 提问时间
  answerTimestamp?: Date; // 回答时间
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
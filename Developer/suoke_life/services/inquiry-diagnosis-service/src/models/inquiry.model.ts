/**
 * 问诊相关数据模型定义
 */

/**
 * 问诊会话模型
 * 表示一次完整的问诊交互过程
 */
export interface InquirySession {
  /**
   * 会话唯一标识符
   */
  sessionId: string;
  
  /**
   * 用户ID
   */
  userId: string;
  
  /**
   * 会话创建时间
   */
  createdAt: string;
  
  /**
   * 会话更新时间
   */
  updatedAt: string;
  
  /**
   * 会话状态
   * - active: 进行中
   * - completed: 已完成
   * - abandoned: 已放弃
   */
  status: 'active' | 'completed' | 'abandoned';
  
  /**
   * 患者基本信息
   */
  patientInfo?: {
    /**
     * 姓名
     */
    name?: string;
    
    /**
     * 年龄
     */
    age?: number;
    
    /**
     * 性别
     */
    gender?: '男' | '女' | '其他';
    
    /**
     * 身高(cm)
     */
    height?: number;
    
    /**
     * 体重(kg)
     */
    weight?: number;
  };
  
  /**
   * 会话偏好设置
   */
  preferences?: {
    /**
     * 是否使用传统中医术语
     */
    useTCMTerminology?: boolean;
    
    /**
     * 回复详细程度 (1-5)
     */
    detailLevel?: number;
    
    /**
     * 语言
     */
    language?: string;
  };
  
  /**
   * 会话中的问答列表
   */
  exchanges: InquiryExchange[];
  
  /**
   * 诊断结果
   */
  diagnosis?: InquiryDiagnosis;
  
  /**
   * 元数据
   */
  metadata?: Record<string, any>;
}

/**
 * 问诊单次交互模型
 * 表示一问一答的交互
 */
export interface InquiryExchange {
  /**
   * 交互ID
   */
  exchangeId: string;
  
  /**
   * 时间戳
   */
  timestamp: string;
  
  /**
   * 用户提问
   */
  question: string;
  
  /**
   * 系统回答
   */
  answer: string;
  
  /**
   * 提取的症状
   */
  extractedSymptoms?: ExtractedSymptom[];
  
  /**
   * 提问意图分类
   */
  intentType?: string;
  
  /**
   * 置信度
   */
  confidence?: number;
}

/**
 * 提取的症状信息
 */
export interface ExtractedSymptom {
  /**
   * 症状名称
   */
  name: string;
  
  /**
   * 症状部位
   */
  location?: string;
  
  /**
   * 症状程度 (1-5)
   */
  severity?: number;
  
  /**
   * 症状持续时间
   */
  duration?: string;
  
  /**
   * 症状频率
   */
  frequency?: string;
  
  /**
   * 症状特征描述
   */
  characteristics?: string[];
  
  /**
   * 加重因素
   */
  aggravatingFactors?: string[];
  
  /**
   * 缓解因素
   */
  relievingFactors?: string[];
  
  /**
   * 相关症状
   */
  associatedSymptoms?: string[];
  
  /**
   * 置信度 (0-1)
   */
  confidence: number;
}

/**
 * 问诊结果诊断
 */
export interface InquiryDiagnosis {
  /**
   * 诊断ID
   */
  diagnosisId: string;
  
  /**
   * 时间戳
   */
  timestamp: string;
  
  /**
   * 中医辨证分型
   */
  tcmPatterns: Array<{
    /**
     * 证型名称
     */
    pattern: string;
    
    /**
     * 置信度
     */
    confidence: number;
    
    /**
     * 相关症状
     */
    relatedSymptoms?: string[];
  }>;
  
  /**
   * 主要症状列表
   */
  mainSymptoms: string[];
  
  /**
   * 次要症状列表
   */
  secondarySymptoms: string[];
  
  /**
   * 体质分析
   */
  constitution?: {
    /**
     * 主要体质
     */
    primary: string;
    
    /**
     * 次要体质
     */
    secondary?: string[];
    
    /**
     * 偏颇程度 (1-5)
     */
    deviationLevel?: number;
  };
  
  /**
   * 健康建议
   */
  recommendations: {
    /**
     * 饮食建议
     */
    diet?: string[];
    
    /**
     * 生活方式建议
     */
    lifestyle?: string[];
    
    /**
     * 调理建议
     */
    remedies?: string[];
    
    /**
     * 其他建议
     */
    others?: string[];
  };
  
  /**
   * 注意事项
   */
  precautions?: string[];
  
  /**
   * 需要进一步确认的问题
   */
  followUpQuestions?: string[];
}

/**
 * 问诊请求
 */
export interface InquiryRequest {
  /**
   * 会话ID
   */
  sessionId: string;
  
  /**
   * 用户ID
   */
  userId: string;
  
  /**
   * 问题内容
   */
  question: string;
  
  /**
   * 附加上下文
   */
  context?: Record<string, any>;
}

/**
 * 问诊响应
 */
export interface InquiryResponse {
  /**
   * 交互ID
   */
  exchangeId: string;
  
  /**
   * 回答内容
   */
  answer: string;
  
  /**
   * 提取的症状
   */
  extractedSymptoms?: ExtractedSymptom[];
  
  /**
   * 是否需要更多信息
   */
  needMoreInfo: boolean;
  
  /**
   * 建议的后续问题
   */
  suggestedFollowUps?: string[];
  
  /**
   * 如果有一个初步诊断，则包含在这里
   */
  preliminaryDiagnosis?: Partial<InquiryDiagnosis>;
  
  /**
   * 元数据
   */
  metadata?: Record<string, any>;
}
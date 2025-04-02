/**
 * 问诊相关接口定义
 */

export interface IInquiryQuestion {
  content: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

export interface IInquiryResponse {
  content: string;
  timestamp: Date;
  extractedSymptoms?: string[];
  suggestedFollowUp?: string[];
  metadata?: Record<string, any>;
}

export interface IInquiryExchange {
  question: IInquiryQuestion;
  response: IInquiryResponse;
  exchangeId: string;
}

export interface IInquirySession {
  sessionId: string;
  userId: string;
  status: 'active' | 'completed' | 'abandoned';
  createdAt: Date;
  updatedAt: Date;
  patientInfo?: Record<string, any>;
  preferences?: Record<string, any>;
  exchanges: IInquiryExchange[];
  metadata?: Record<string, any>;
}

export interface IInquirySessionCreate {
  userId: string;
  patientInfo?: Record<string, any>;
  preferences?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface IInquiryProcess {
  content: string;
  metadata?: Record<string, any>;
}

export interface IInquiryResponse {
  sessionId: string;
  exchangeId: string;
  response: {
    content: string;
    extractedSymptoms?: string[];
    suggestedFollowUp?: string[];
  };
  sessionStatus: 'active' | 'completed' | 'abandoned';
  metadata?: Record<string, any>;
}

/**
 * @swagger
 * components:
 *   schemas:
 *     InquirySession:
 *       type: object
 *       required:
 *         - id
 *         - userId
 *         - status
 *         - createdAt
 *       properties:
 *         id:
 *           type: string
 *           description: 会话ID
 *         userId:
 *           type: string
 *           description: 用户ID
 *         patientInfo:
 *           type: object
 *           properties:
 *             name:
 *               type: string
 *             age:
 *               type: number
 *             gender:
 *               type: string
 *               enum: [male, female, other]
 *           description: 患者信息
 *         status:
 *           type: string
 *           enum: [active, completed, archived]
 *           description: 会话状态
 *         preferences:
 *           type: object
 *           description: 会话偏好设置
 *         lastInteractionAt:
 *           type: string
 *           format: date-time
 *           description: 最后交互时间
 *         createdAt:
 *           type: string
 *           format: date-time
 *           description: 创建时间
 *         updatedAt:
 *           type: string
 *           format: date-time
 *           description: 更新时间
 *
 *     InquiryMessage:
 *       type: object
 *       required:
 *         - id
 *         - sessionId
 *         - content
 *         - role
 *         - createdAt
 *       properties:
 *         id:
 *           type: string
 *           description: 消息ID
 *         sessionId:
 *           type: string
 *           description: 会话ID
 *         content:
 *           type: string
 *           description: 消息内容
 *         role:
 *           type: string
 *           enum: [user, assistant, system]
 *           description: 角色
 *         metadata:
 *           type: object
 *           description: 元数据(可能包含提取的症状、情绪等)
 *         createdAt:
 *           type: string
 *           format: date-time
 *           description: 创建时间
 *
 *     InquiryResponse:
 *       type: object
 *       required:
 *         - success
 *         - message
 *       properties:
 *         success:
 *           type: boolean
 *           description: 是否成功
 *         message:
 *           type: string
 *           description: 响应消息
 *         data:
 *           type: object
 *           description: 响应数据
 */

// 问诊会话接口
export interface InquirySession {
  id: string;
  userId: string;
  patientInfo?: PatientInfo;
  status: SessionStatus;
  preferences?: Record<string, any>;
  lastInteractionAt?: Date;
  createdAt: Date;
  updatedAt?: Date;
}

// 会话状态枚举
export enum SessionStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  ARCHIVED = 'archived'
}

// 患者信息接口
export interface PatientInfo {
  name?: string;
  age?: number;
  gender?: 'male' | 'female' | 'other';
  medicalHistory?: string[];
  allergies?: string[];
  currentMedications?: string[];
}

// 问诊消息接口
export interface InquiryMessage {
  id: string;
  sessionId: string;
  content: string;
  role: MessageRole;
  metadata?: Record<string, any>;
  createdAt: Date;
}

// 消息角色枚举
export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

// 问诊处理请求
export interface ProcessInquiryRequest {
  sessionId: string;
  content: string;
  metadata?: Record<string, any>;
}

// 问诊处理响应
export interface ProcessInquiryResponse {
  message: InquiryMessage;
  extractedSymptoms?: string[];
  suggestedActions?: SuggestedAction[];
}

// 建议操作
export interface SuggestedAction {
  type: ActionType;
  description: string;
  data?: Record<string, any>;
}

// 操作类型枚举
export enum ActionType {
  GENERATE_DIAGNOSIS = 'generate_diagnosis',
  REQUEST_ADDITIONAL_INFO = 'request_additional_info',
  RECOMMEND_EXAMINATION = 'recommend_examination',
  REFER_TO_SPECIALIST = 'refer_to_specialist'
} 
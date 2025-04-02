import { z } from 'zod';

/**
 * 诊断请求验证模式
 */
export const DiagnosisRequestSchema = z.object({
  userId: z.string().uuid({ message: '用户ID必须是有效的UUID' }),
  sessionId: z.string().uuid({ message: '会话ID必须是有效的UUID' }),
  symptoms: z.array(z.string()).min(1, { message: '至少需要一个症状' }),
  patientInfo: z.object({
    age: z.number().int().min(0).max(120).optional(),
    gender: z.enum(['男', '女', '其他']).optional(),
    medicalHistory: z.array(z.string()).optional(),
  }).optional(),
});

/**
 * 问诊请求验证模式
 */
export const InquiryRequestSchema = z.object({
  userId: z.string().uuid({ message: '用户ID必须是有效的UUID' }),
  sessionId: z.string().uuid({ message: '会话ID必须是有效的UUID' }),
  question: z.string().min(1, { message: '问题不能为空' }),
  context: z.object({
    previousQuestions: z.array(z.string()).optional(),
    previousAnswers: z.array(z.string()).optional(),
    extractedSymptoms: z.array(z.string()).optional(),
  }).optional(),
});

/**
 * 会话创建验证模式
 */
export const SessionCreateSchema = z.object({
  userId: z.string().uuid({ message: '用户ID必须是有效的UUID' }),
  patientInfo: z.object({
    name: z.string().optional(),
    age: z.number().int().min(0).max(120).optional(),
    gender: z.enum(['男', '女', '其他']).optional(),
    medicalHistory: z.array(z.string()).optional(),
  }).optional(),
  preferences: z.object({
    language: z.enum(['中文', '英文']).default('中文'),
    responseType: z.enum(['简洁', '详细']).default('详细'),
    includeReferences: z.boolean().default(true),
  }).optional(),
});

/**
 * 会话偏好更新验证模式
 */
export const SessionPreferencesUpdateSchema = z.object({
  language: z.enum(['中文', '英文']).optional(),
  responseType: z.enum(['简洁', '详细']).optional(),
  includeReferences: z.boolean().optional(),
});
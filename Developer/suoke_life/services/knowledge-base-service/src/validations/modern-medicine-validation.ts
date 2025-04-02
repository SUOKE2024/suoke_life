/**
 * 现代医学知识验证模式
 */
import { z } from 'zod';

// 临床试验架构
const clinicalTrialSchema = z.object({
  name: z.string(),
  url: z.string().url('请输入有效的URL'),
  year: z.number().int().min(1900).max(new Date().getFullYear()),
  outcome: z.string()
});

// 创建现代医学知识验证模式
export const createModernMedicineKnowledgeSchema = z.object({
  title: z.string().min(1, '标题不能为空').max(200, '标题不能超过200个字符'),
  content: z.string().min(1, '内容不能为空').max(50000, '内容不能超过50000个字符'),
  summary: z.string().max(1000, '摘要不能超过1000个字符').optional(),
  categories: z.array(z.string()).min(1, '至少选择一个分类'),
  tags: z.array(z.string()).optional(),
  medicalSystem: z.enum([
    'internal', 'surgery', 'gynecology', 'pediatrics', 
    'preventive', 'nutrition', 'psychology', 'other'
  ], {
    errorMap: () => ({ message: '无效的医学体系' })
  }),
  researchSupport: z.enum(['high', 'medium', 'low', 'unconfirmed'], {
    errorMap: () => ({ message: '无效的研究支持程度' })
  }),
  references: z.array(z.string()).optional(),
  clinicalTrials: z.array(clinicalTrialSchema).optional(),
  vectorized: z.boolean().optional(),
  source: z.string().optional(),
  attributes: z.record(z.string(), z.any()).optional()
});

// 更新现代医学知识验证模式
export const updateModernMedicineKnowledgeSchema = createModernMedicineKnowledgeSchema.partial({
  title: true,
  content: true,
  categories: true,
  medicalSystem: true,
  researchSupport: true
});
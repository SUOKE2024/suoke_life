/**
 * 传统文化知识验证模式
 */
import { z } from 'zod';

// 创建传统文化知识验证模式
export const createTraditionalCultureKnowledgeSchema = z.object({
  title: z.string().min(1, '标题不能为空').max(200, '标题不能超过200个字符'),
  content: z.string().min(1, '内容不能为空').max(50000, '内容不能超过50000个字符'),
  summary: z.string().max(1000, '摘要不能超过1000个字符').optional(),
  categories: z.array(z.string()).min(1, '至少选择一个分类'),
  tags: z.array(z.string()).optional(),
  culturalSystem: z.enum([
    'yijing', 'taoism', 'buddhism', 'physiognomy', 
    'fengshui', 'classics', 'other'
  ], {
    errorMap: () => ({ message: '无效的文化体系' })
  }),
  historicalPeriod: z.string().optional(),
  originalText: z.string().optional(),
  interpretation: z.string().optional(),
  vectorized: z.boolean().optional(),
  source: z.string().optional(),
  attributes: z.record(z.string(), z.any()).optional()
});

// 更新传统文化知识验证模式
export const updateTraditionalCultureKnowledgeSchema = createTraditionalCultureKnowledgeSchema.partial({
  title: true,
  content: true,
  categories: true,
  culturalSystem: true
});
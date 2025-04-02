/**
 * 知识相关验证模式
 */

import { z } from 'zod';

// 创建知识验证模式
export const createKnowledgeSchema = z.object({
  title: z.string({
    required_error: '标题不能为空',
    invalid_type_error: '标题必须为字符串',
  }).min(2, '标题至少需要2个字符').max(200, '标题不能超过200个字符'),
  
  content: z.string({
    required_error: '内容不能为空',
    invalid_type_error: '内容必须为字符串',
  }).min(10, '内容至少需要10个字符'),
  
  summary: z.string().max(500, '摘要不能超过500个字符').optional(),
  
  categories: z.array(z.string(), {
    required_error: '分类不能为空',
    invalid_type_error: '分类必须为数组',
  }).min(1, '至少需要选择一个分类').max(5, '最多只能选择5个分类'),
  
  tags: z.array(z.string()).max(20, '最多只能设置20个标签').optional(),
  
  source: z.string().max(200, '来源不能超过200个字符').optional(),
  
  metadata: z.record(z.any()).optional(),
});

// 更新知识验证模式
export const updateKnowledgeSchema = z.object({
  title: z.string().min(2, '标题至少需要2个字符').max(200, '标题不能超过200个字符').optional(),
  
  content: z.string().min(10, '内容至少需要10个字符').optional(),
  
  summary: z.string().max(500, '摘要不能超过500个字符').optional(),
  
  categories: z.array(z.string()).min(1, '至少需要选择一个分类').max(5, '最多只能选择5个分类').optional(),
  
  tags: z.array(z.string()).max(20, '最多只能设置20个标签').optional(),
  
  source: z.string().max(200, '来源不能超过200个字符').optional(),
  
  metadata: z.record(z.any()).optional(),
});

// 获取知识列表验证模式
export const getKnowledgeListSchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(20),
  category: z.string().optional(),
  tag: z.string().optional(),
  status: z.enum(['draft', 'published', 'archived']).optional(),
  sort: z.string().optional(),
  order: z.enum(['asc', 'desc']).default('desc'),
});

// 获取知识版本历史验证模式
export const getKnowledgeVersionsSchema = z.object({
  id: z.string({
    required_error: '知识ID不能为空',
    invalid_type_error: '知识ID必须为字符串',
  }),
});
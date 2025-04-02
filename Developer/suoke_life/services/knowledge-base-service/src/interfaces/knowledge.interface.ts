/**
 * 知识相关接口定义
 */

import { Document } from 'mongoose';

/**
 * 知识条目接口
 */
export interface IKnowledge extends Document {
  title: string;
  content: string;
  summary?: string;
  categories: string[];
  tags?: string[];
  source?: string;
  author?: string;
  createdAt: Date;
  updatedAt: Date;
  publishedAt?: Date;
  status: 'draft' | 'published' | 'archived';
  version: number;
  metadata?: Record<string, any>;
  vectorId?: string;
  keywords?: string[];
  viewCount: number;
  relations?: {
    relatedKnowledge?: string[];
    prerequisites?: string[];
    nextSteps?: string[];
  };
}

/**
 * 知识版本接口
 */
export interface IKnowledgeVersion extends Document {
  knowledgeId: string;
  version: number;
  title: string;
  content: string;
  summary?: string;
  categories: string[];
  tags?: string[];
  createdAt: Date;
  createdBy?: string;
  comment?: string;
}

/**
 * 知识分类接口
 */
export interface ICategory extends Document {
  name: string;
  description?: string;
  parentId?: string;
  path?: string[];
  level: number;
  icon?: string;
  color?: string;
  order?: number;
  createdAt: Date;
  updatedAt: Date;
  knowledgeCount: number;
}

/**
 * 知识标签接口
 */
export interface ITag extends Document {
  name: string;
  description?: string;
  color?: string;
  createdAt: Date;
  updatedAt: Date;
  knowledgeCount: number;
}

/**
 * 知识创建请求
 */
export interface CreateKnowledgeRequest {
  title: string;
  content: string;
  summary?: string;
  categories: string[];
  tags?: string[];
  source?: string;
  metadata?: Record<string, any>;
}

/**
 * 知识更新请求
 */
export interface UpdateKnowledgeRequest {
  title?: string;
  content?: string;
  summary?: string;
  categories?: string[];
  tags?: string[];
  source?: string;
  metadata?: Record<string, any>;
}

/**
 * 知识列表查询选项
 */
export interface KnowledgeListOptions {
  page?: number;
  limit?: number;
  category?: string;
  tag?: string;
  status?: 'draft' | 'published' | 'archived';
  sort?: string;
  order?: 'asc' | 'desc';
}

/**
 * 分页结果接口
 */
export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

/**
 * 分类树节点
 */
export interface CategoryTreeNode {
  _id: string;
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  order?: number;
  level: number;
  knowledgeCount: number;
  children?: CategoryTreeNode[];
}

/**
 * 搜索选项接口
 */
export interface SearchOptions {
  query: string;
  categories?: string[];
  tags?: string[];
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

/**
 * 语义搜索选项接口
 */
export interface SemanticSearchOptions {
  query: string;
  categories?: string[];
  limit?: number;
  threshold?: number;
}

/**
 * 搜索结果项
 */
export interface SearchResultItem {
  id: string;
  title: string;
  summary?: string;
  content: string;
  categories: string[];
  tags?: string[];
  score: number;
  highlights?: {
    title?: string;
    content?: string;
    summary?: string;
  };
}

/**
 * 相关知识结果
 */
export interface RelatedKnowledgeResult {
  id: string;
  title: string;
  summary?: string;
  similarity: number;
}

/**
 * 知识统计接口
 */
export interface KnowledgeStats {
  total: number;
  published: number;
  draft: number;
  archived: number;
  categoryDistribution: Array<{
    category: string;
    count: number;
  }>;
  creationTrend: Array<{
    date: string;
    count: number;
  }>;
}

/**
 * 知识导出格式
 */
export type KnowledgeExportFormat = 'json' | 'markdown' | 'html' | 'pdf';
/**
 * 知识服务
 * 处理基础知识的创建、查询、更新和删除
 */

import mongoose from 'mongoose';
import KnowledgeModel from '../models/knowledge.model';
import KnowledgeVersionModel from '../models/knowledge-version.model';
import CategoryModel from '../models/category.model';
import TagModel from '../models/tag.model';
import {
  IKnowledge,
  CreateKnowledgeRequest,
  UpdateKnowledgeRequest,
  KnowledgeListOptions,
  PaginatedResult
} from '../interfaces/knowledge.interface';
import logger from '../utils/logger';
import { getRedisClient } from '../utils/redis';

export class KnowledgeService {
  /**
   * 创建知识条目
   * @param data 知识数据
   * @param createdBy 创建者
   */
  async createKnowledge(data: CreateKnowledgeRequest, createdBy?: string): Promise<IKnowledge> {
    try {
      // 创建知识条目
      const knowledge = new KnowledgeModel({
        ...data,
        author: createdBy,
        status: 'draft',
        version: 1,
        viewCount: 0,
      });
      
      await knowledge.save();
      
      // 更新分类计数
      if (data.categories && data.categories.length > 0) {
        await CategoryModel.updateMany(
          { _id: { $in: data.categories } },
          { $inc: { knowledgeCount: 1 } }
        );
      }
      
      // 更新标签计数
      if (data.tags && data.tags.length > 0) {
        await TagModel.updateMany(
          { _id: { $in: data.tags } },
          { $inc: { knowledgeCount: 1 } }
        );
      }
      
      // 创建版本历史
      await KnowledgeVersionModel.create({
        knowledgeId: knowledge._id,
        version: 1,
        title: knowledge.title,
        content: knowledge.content,
        summary: knowledge.summary,
        categories: knowledge.categories,
        tags: knowledge.tags,
        createdBy: createdBy,
        comment: '初始版本',
      });
      
      return knowledge;
    } catch (error) {
      logger.error('创建知识条目失败', { error });
      throw error;
    }
  }
  
  /**
   * 更新知识条目
   * @param id 知识ID
   * @param data 更新数据
   * @param updatedBy 更新者
   */
  async updateKnowledge(id: string, data: UpdateKnowledgeRequest, updatedBy?: string): Promise<IKnowledge | null> {
    try {
      // 获取当前知识条目
      const knowledge = await KnowledgeModel.findById(id);
      
      if (!knowledge) {
        return null;
      }
      
      // 记录旧分类和标签，用于更新计数
      const oldCategories = [...knowledge.categories].map(id => id.toString());
      const oldTags = knowledge.tags ? [...knowledge.tags].map(id => id.toString()) : [];
      
      // 更新知识条目
      const updateData: Record<string, any> = { ...data };
      
      // 增加版本号
      updateData.version = knowledge.version + 1;
      
      // 更新知识条目
      Object.assign(knowledge, updateData);
      await knowledge.save();
      
      // 更新分类计数
      if (data.categories && JSON.stringify(oldCategories) !== JSON.stringify(data.categories)) {
        // 减少旧分类计数
        if (oldCategories.length > 0) {
          await CategoryModel.updateMany(
            { _id: { $in: oldCategories } },
            { $inc: { knowledgeCount: -1 } }
          );
        }
        
        // 增加新分类计数
        await CategoryModel.updateMany(
          { _id: { $in: data.categories } },
          { $inc: { knowledgeCount: 1 } }
        );
      }
      
      // 更新标签计数
      if (data.tags && JSON.stringify(oldTags) !== JSON.stringify(data.tags)) {
        // 减少旧标签计数
        if (oldTags.length > 0) {
          await TagModel.updateMany(
            { _id: { $in: oldTags } },
            { $inc: { knowledgeCount: -1 } }
          );
        }
        
        // 增加新标签计数
        if (data.tags.length > 0) {
          await TagModel.updateMany(
            { _id: { $in: data.tags } },
            { $inc: { knowledgeCount: 1 } }
          );
        }
      }
      
      // 创建版本历史
      await KnowledgeVersionModel.create({
        knowledgeId: knowledge._id,
        version: knowledge.version,
        title: knowledge.title,
        content: knowledge.content,
        summary: knowledge.summary,
        categories: knowledge.categories,
        tags: knowledge.tags,
        createdBy: updatedBy,
        comment: '更新版本',
      });
      
      return knowledge;
    } catch (error) {
      logger.error(`更新知识条目失败: ${id}`, { error });
      throw error;
    }
  }
  
  /**
   * 删除知识条目
   * @param id 知识ID
   */
  async deleteKnowledge(id: string): Promise<boolean> {
    try {
      // 获取当前知识条目
      const knowledge = await KnowledgeModel.findById(id);
      
      if (!knowledge) {
        return false;
      }
      
      // 获取分类和标签，用于更新计数
      const categories = [...knowledge.categories].map(id => id.toString());
      const tags = knowledge.tags ? [...knowledge.tags].map(id => id.toString()) : [];
      
      // 删除知识条目
      await knowledge.deleteOne();
      
      // 删除版本历史
      await KnowledgeVersionModel.deleteMany({ knowledgeId: id });
      
      // 更新分类计数
      if (categories.length > 0) {
        await CategoryModel.updateMany(
          { _id: { $in: categories } },
          { $inc: { knowledgeCount: -1 } }
        );
      }
      
      // 更新标签计数
      if (tags.length > 0) {
        await TagModel.updateMany(
          { _id: { $in: tags } },
          { $inc: { knowledgeCount: -1 } }
        );
      }
      
      return true;
    } catch (error) {
      logger.error(`删除知识条目失败: ${id}`, { error });
      throw error;
    }
  }
  
  /**
   * 获取知识条目
   * @param id 知识ID
   */
  async getKnowledgeById(id: string): Promise<IKnowledge | null> {
    try {
      // 尝试从缓存获取
      const redisClient = getRedisClient();
      const cacheKey = `knowledge:${id}`;
      const cachedData = await redisClient.get(cacheKey);
      
      if (cachedData) {
        return JSON.parse(cachedData);
      }
      
      // 从数据库获取
      const knowledge = await KnowledgeModel.findById(id)
        .populate('categories')
        .populate('tags');
      
      if (!knowledge) {
        return null;
      }
      
      // 增加浏览次数
      knowledge.viewCount += 1;
      await knowledge.save();
      
      // 缓存知识条目
      const cacheTtl = parseInt(process.env.CACHE_TTL || '3600');
      await redisClient.set(cacheKey, JSON.stringify(knowledge), {
        EX: cacheTtl,
      });
      
      return knowledge;
    } catch (error) {
      logger.error(`获取知识条目失败: ${id}`, { error });
      throw error;
    }
  }
  
  /**
   * 获取知识版本历史
   * @param id 知识ID
   */
  async getKnowledgeVersions(id: string): Promise<any[]> {
    try {
      return await KnowledgeVersionModel.find({ knowledgeId: id })
        .sort({ version: -1 })
        .select('-content') // 不返回内容，减少数据量
        .lean();
    } catch (error) {
      logger.error(`获取知识版本历史失败: ${id}`, { error });
      throw error;
    }
  }
  
  /**
   * 获取知识列表
   * @param options 查询选项
   */
  async getKnowledgeList(options: KnowledgeListOptions): Promise<PaginatedResult<IKnowledge>> {
    try {
      const {
        page = 1,
        limit = 20,
        category,
        tag,
        status = 'published',
        sort = 'createdAt',
        order = 'desc',
      } = options;
      
      // 构建查询条件
      const query: any = {};
      
      if (status) {
        query.status = status;
      }
      
      if (category) {
        query.categories = category;
      }
      
      if (tag) {
        query.tags = tag;
      }
      
      // 构建排序选项
      const sortOption: any = {};
      sortOption[sort] = order === 'asc' ? 1 : -1;
      
      // 执行分页查询
      const knowledgeQuery = KnowledgeModel.paginate(query, {
        page,
        limit,
        sort: sortOption,
        populate: ['categories', 'tags'],
      });
      
      const result = await knowledgeQuery;
      
      return {
        items: result.docs,
        total: result.totalDocs,
        page: result.page,
        limit: result.limit,
        pages: result.totalPages,
      };
    } catch (error) {
      logger.error('获取知识列表失败', { error });
      throw error;
    }
  }
  
  /**
   * 发布知识
   * @param id 知识ID
   */
  async publishKnowledge(id: string): Promise<IKnowledge | null> {
    try {
      const knowledge = await KnowledgeModel.findById(id);
      
      if (!knowledge) {
        return null;
      }
      
      knowledge.status = 'published';
      knowledge.publishedAt = new Date();
      
      await knowledge.save();
      
      return knowledge;
    } catch (error) {
      logger.error(`发布知识失败: ${id}`, { error });
      throw error;
    }
  }
  
  /**
   * 取消发布知识
   * @param id 知识ID
   */
  async unpublishKnowledge(id: string): Promise<IKnowledge | null> {
    try {
      const knowledge = await KnowledgeModel.findById(id);
      
      if (!knowledge) {
        return null;
      }
      
      knowledge.status = 'draft';
      
      await knowledge.save();
      
      return knowledge;
    } catch (error) {
      logger.error(`取消发布知识失败: ${id}`, { error });
      throw error;
    }
  }
}
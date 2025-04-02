import logger from '../../core/utils/logger';
import { KnowledgeModel } from '../../models/knowledge.model';
import { KnowledgeCategoryModel } from '../../models/knowledge-category.model';
import { KnowledgeRatingModel } from '../../models/knowledge-rating.model';
import { ApiError } from '../../core/utils/errors';
import axios from 'axios';

/**
 * 知识查询参数
 */
interface KnowledgeQueryParams {
  page: number;
  limit: number;
  category?: string;
  tags?: string[];
}

/**
 * 推荐参数
 */
interface RecommendationParams {
  limit: number;
  userId?: string;
}

/**
 * 搜索参数
 */
interface SearchParams {
  query: string;
  page: number;
  limit: number;
}

/**
 * 趋势参数
 */
interface TrendingParams {
  period: 'day' | 'week' | 'month';
  limit: number;
}

/**
 * 评分参数
 */
interface RatingParams {
  knowledgeId: string;
  userId: string;
  rating: number;
  feedback?: string;
}

/**
 * 获取知识内容列表
 */
export const getKnowledgeList = async (params: KnowledgeQueryParams) => {
  try {
    const { page, limit, category, tags } = params;
    const skip = (page - 1) * limit;
    
    // 构建查询条件
    const query: any = {};
    if (category) {
      query.category = category;
    }
    if (tags && tags.length > 0) {
      query.tags = { $in: tags };
    }
    
    // 查询数据
    const [items, total] = await Promise.all([
      KnowledgeModel.find(query)
        .skip(skip)
        .limit(limit)
        .sort({ createdAt: -1 })
        .lean(),
      KnowledgeModel.countDocuments(query)
    ]);
    
    return {
      items,
      total,
      page,
      limit,
      pages: Math.ceil(total / limit)
    };
  } catch (error) {
    logger.error('获取知识内容列表错误:', error);
    throw new ApiError(500, '获取知识内容列表失败');
  }
};

/**
 * 获取知识内容详情
 */
export const getKnowledgeById = async (id: string) => {
  try {
    const knowledge = await KnowledgeModel.findById(id).lean();
    
    if (!knowledge) {
      return null;
    }
    
    // 增加浏览次数
    await KnowledgeModel.findByIdAndUpdate(id, { $inc: { viewCount: 1 } });
    
    // 获取相关评分
    const ratings = await KnowledgeRatingModel.find({ knowledgeId: id }).lean();
    
    // 计算平均评分
    let averageRating = 0;
    if (ratings.length > 0) {
      averageRating = ratings.reduce((sum, item) => sum + item.rating, 0) / ratings.length;
    }
    
    return {
      ...knowledge,
      ratings: {
        average: averageRating,
        count: ratings.length
      }
    };
  } catch (error) {
    logger.error(`获取知识内容详情错误 [ID: ${id}]:`, error);
    throw new ApiError(500, '获取知识内容详情失败');
  }
};

/**
 * 获取推荐知识内容
 */
export const getRecommendedKnowledge = async (params: RecommendationParams) => {
  try {
    const { limit, userId } = params;
    
    // 如果有用户ID，尝试获取个性化推荐
    if (userId) {
      try {
        // 调用RAG服务获取个性化推荐
        const response = await axios.get(`${process.env.RAG_SERVICE_URL}/recommendations/knowledge`, {
          params: { userId, limit }
        });
        
        if (response.data && response.data.items) {
          return response.data;
        }
      } catch (error) {
        logger.warn(`从RAG服务获取个性化推荐失败，回退到通用推荐 [用户ID: ${userId}]:`, error);
      }
    }
    
    // 通用推荐：基于热门内容
    const items = await KnowledgeModel.find()
      .sort({ viewCount: -1, createdAt: -1 })
      .limit(limit)
      .lean();
    
    return { items };
  } catch (error) {
    logger.error('获取推荐知识内容错误:', error);
    throw new ApiError(500, '获取推荐知识内容失败');
  }
};

/**
 * 获取知识分类
 */
export const getKnowledgeCategories = async () => {
  try {
    const categories = await KnowledgeCategoryModel.find().sort({ order: 1 }).lean();
    
    // 对每个分类，添加对应内容数量
    const categoriesWithCount = await Promise.all(
      categories.map(async (category) => {
        const count = await KnowledgeModel.countDocuments({ category: category._id });
        return { ...category, count };
      })
    );
    
    return categoriesWithCount;
  } catch (error) {
    logger.error('获取知识分类错误:', error);
    throw new ApiError(500, '获取知识分类失败');
  }
};

/**
 * 创建知识内容
 */
export const createKnowledge = async (data: any) => {
  try {
    // 验证分类是否存在
    if (data.category) {
      const categoryExists = await KnowledgeCategoryModel.exists({ _id: data.category });
      if (!categoryExists) {
        throw new ApiError(400, '指定的分类不存在');
      }
    }
    
    // 创建知识内容
    const knowledge = new KnowledgeModel({
      ...data,
      viewCount: 0,
      createdAt: new Date(),
      updatedAt: new Date()
    });
    
    await knowledge.save();
    
    return knowledge.toObject();
  } catch (error) {
    logger.error('创建知识内容错误:', error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '创建知识内容失败');
  }
};

/**
 * 更新知识内容
 */
export const updateKnowledge = async (id: string, data: any, userId: string) => {
  try {
    // 检查知识内容是否存在并且用户有权限更新
    const knowledge = await KnowledgeModel.findOne({ 
      _id: id,
      $or: [
        { createdBy: userId },
        { collaborators: userId }
      ]
    });
    
    if (!knowledge) {
      return null;
    }
    
    // 验证分类是否存在
    if (data.category) {
      const categoryExists = await KnowledgeCategoryModel.exists({ _id: data.category });
      if (!categoryExists) {
        throw new ApiError(400, '指定的分类不存在');
      }
    }
    
    // 更新知识内容
    Object.assign(knowledge, {
      ...data,
      updatedAt: new Date()
    });
    
    await knowledge.save();
    
    return knowledge.toObject();
  } catch (error) {
    logger.error(`更新知识内容错误 [ID: ${id}]:`, error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '更新知识内容失败');
  }
};

/**
 * 删除知识内容
 */
export const deleteKnowledge = async (id: string, userId: string) => {
  try {
    // 检查知识内容是否存在并且用户有权限删除
    const result = await KnowledgeModel.findOneAndDelete({ 
      _id: id,
      $or: [
        { createdBy: userId },
        { collaborators: userId }
      ]
    });
    
    if (!result) {
      return false;
    }
    
    // 删除相关的评分
    await KnowledgeRatingModel.deleteMany({ knowledgeId: id });
    
    return true;
  } catch (error) {
    logger.error(`删除知识内容错误 [ID: ${id}]:`, error);
    throw new ApiError(500, '删除知识内容失败');
  }
};

/**
 * 搜索知识内容
 */
export const searchKnowledge = async (params: SearchParams) => {
  try {
    const { query, page, limit } = params;
    const skip = (page - 1) * limit;
    
    // 使用RAG服务进行语义搜索
    try {
      const response = await axios.get(`${process.env.RAG_SERVICE_URL}/search/knowledge`, {
        params: { query, limit, offset: skip }
      });
      
      if (response.data) {
        return response.data;
      }
    } catch (error) {
      logger.warn(`RAG服务搜索失败，回退到本地搜索 [查询: ${query}]:`, error);
    }
    
    // 本地搜索回退
    const searchRegex = new RegExp(query, 'i');
    const searchCondition = {
      $or: [
        { title: searchRegex },
        { summary: searchRegex },
        { content: searchRegex },
        { tags: searchRegex }
      ]
    };
    
    const [items, total] = await Promise.all([
      KnowledgeModel.find(searchCondition)
        .skip(skip)
        .limit(limit)
        .sort({ createdAt: -1 })
        .lean(),
      KnowledgeModel.countDocuments(searchCondition)
    ]);
    
    return {
      items,
      total,
      page,
      limit,
      pages: Math.ceil(total / limit)
    };
  } catch (error) {
    logger.error(`搜索知识内容错误 [查询: ${params.query}]:`, error);
    throw new ApiError(500, '搜索知识内容失败');
  }
};

/**
 * 为知识内容评分
 */
export const rateKnowledge = async (params: RatingParams) => {
  try {
    const { knowledgeId, userId, rating, feedback } = params;
    
    // 检查知识内容是否存在
    const knowledge = await KnowledgeModel.findById(knowledgeId);
    if (!knowledge) {
      throw new ApiError(404, '知识内容不存在');
    }
    
    // 检查用户是否已经评过分
    let ratingDoc = await KnowledgeRatingModel.findOne({ knowledgeId, userId });
    
    if (ratingDoc) {
      // 更新现有评分
      ratingDoc.rating = rating;
      if (feedback) {
        ratingDoc.feedback = feedback;
      }
      ratingDoc.updatedAt = new Date();
    } else {
      // 创建新评分
      ratingDoc = new KnowledgeRatingModel({
        knowledgeId,
        userId,
        rating,
        feedback,
        createdAt: new Date(),
        updatedAt: new Date()
      });
    }
    
    await ratingDoc.save();
    
    // 计算平均评分
    const ratings = await KnowledgeRatingModel.find({ knowledgeId });
    const averageRating = ratings.reduce((sum, item) => sum + item.rating, 0) / ratings.length;
    
    return {
      rating: ratingDoc.toObject(),
      averageRating,
      ratingsCount: ratings.length
    };
  } catch (error) {
    logger.error(`为知识内容评分错误 [ID: ${params.knowledgeId}]:`, error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '为知识内容评分失败');
  }
};

/**
 * 获取热门知识内容
 */
export const getTrendingKnowledge = async (params: TrendingParams) => {
  try {
    const { period, limit } = params;
    
    // 计算时间范围
    const now = new Date();
    let startDate: Date;
    
    switch (period) {
      case 'day':
        startDate = new Date(now.setDate(now.getDate() - 1));
        break;
      case 'week':
        startDate = new Date(now.setDate(now.getDate() - 7));
        break;
      case 'month':
        startDate = new Date(now.setMonth(now.getMonth() - 1));
        break;
      default:
        startDate = new Date(now.setDate(now.getDate() - 7));
    }
    
    // 获取指定时间范围内最热门的内容
    const items = await KnowledgeModel.find({ 
      createdAt: { $gte: startDate } 
    })
      .sort({ viewCount: -1, createdAt: -1 })
      .limit(limit)
      .lean();
    
    return { items, period };
  } catch (error) {
    logger.error(`获取热门知识内容错误 [周期: ${params.period}]:`, error);
    throw new ApiError(500, '获取热门知识内容失败');
  }
};
import logger from '../../core/utils/logger';
import { BlogModel } from '../../models/blog.model';
import { BlogCommentModel } from '../../models/blog-comment.model';
import { ApiError } from '../../core/utils/errors';

/**
 * 博客查询参数
 */
interface BlogQueryParams {
  page: number;
  limit: number;
  author?: string;
  tags?: string[];
  status?: 'draft' | 'published' | 'archived';
}

/**
 * 评论查询参数
 */
interface CommentQueryParams {
  page: number;
  limit: number;
  blog: string;
  parentComment?: string;
}

/**
 * 获取博客列表
 */
export const getBlogList = async (params: BlogQueryParams) => {
  try {
    const { page, limit, author, tags, status } = params;
    const skip = (page - 1) * limit;
    
    // 构建查询条件
    const query: any = {};
    if (author) {
      query.author = author;
    }
    if (tags && tags.length > 0) {
      query.tags = { $in: tags };
    }
    if (status) {
      query.status = status;
    } else {
      // 默认只查询已发布的博客
      query.status = 'published';
    }
    
    // 查询数据
    const [items, total] = await Promise.all([
      BlogModel.find(query)
        .skip(skip)
        .limit(limit)
        .sort({ createdAt: -1 })
        .lean(),
      BlogModel.countDocuments(query)
    ]);
    
    return {
      items,
      total,
      page,
      limit,
      pages: Math.ceil(total / limit)
    };
  } catch (error) {
    logger.error('获取博客列表错误:', error);
    throw new ApiError(500, '获取博客列表失败');
  }
};

/**
 * 获取博客详情
 */
export const getBlogById = async (id: string) => {
  try {
    const blog = await BlogModel.findById(id).lean();
    
    if (!blog) {
      return null;
    }
    
    // 只有已发布的博客可以被公开查看
    if (blog.status !== 'published') {
      return null;
    }
    
    // 增加浏览次数
    await BlogModel.findByIdAndUpdate(id, { $inc: { viewCount: 1 } });
    
    return blog;
  } catch (error) {
    logger.error(`获取博客详情错误 [ID: ${id}]:`, error);
    throw new ApiError(500, '获取博客详情失败');
  }
};

/**
 * 获取我的博客（作者本人可查看所有状态的博客）
 */
export const getMyBlogs = async (authorId: string, params: BlogQueryParams) => {
  try {
    params.author = authorId;
    return await getBlogList(params);
  } catch (error) {
    logger.error(`获取作者博客列表错误 [作者ID: ${authorId}]:`, error);
    throw new ApiError(500, '获取我的博客列表失败');
  }
};

/**
 * 创建博客
 */
export const createBlog = async (data: any) => {
  try {
    const blog = new BlogModel({
      ...data,
      viewCount: 0,
      likeCount: 0,
      commentCount: 0,
      createdAt: new Date(),
      updatedAt: new Date()
    });
    
    if (data.status === 'published') {
      blog.publishedAt = new Date();
    }
    
    await blog.save();
    
    return blog.toObject();
  } catch (error) {
    logger.error('创建博客错误:', error);
    throw new ApiError(500, '创建博客失败');
  }
};

/**
 * 更新博客
 */
export const updateBlog = async (id: string, data: any, userId: string) => {
  try {
    // 检查博客是否存在并且用户有权限更新
    const blog = await BlogModel.findOne({ 
      _id: id,
      author: userId
    });
    
    if (!blog) {
      return null;
    }
    
    // 如果状态从非published变为published，设置publishedAt
    if (blog.status !== 'published' && data.status === 'published') {
      data.publishedAt = new Date();
    }
    
    // 更新博客
    Object.assign(blog, {
      ...data,
      updatedAt: new Date()
    });
    
    await blog.save();
    
    return blog.toObject();
  } catch (error) {
    logger.error(`更新博客错误 [ID: ${id}]:`, error);
    throw new ApiError(500, '更新博客失败');
  }
};

/**
 * 删除博客
 */
export const deleteBlog = async (id: string, userId: string) => {
  try {
    // 检查博客是否存在并且用户有权限删除
    const blog = await BlogModel.findOne({ 
      _id: id,
      author: userId
    });
    
    if (!blog) {
      return false;
    }
    
    // 删除博客及其相关评论
    await Promise.all([
      BlogModel.deleteOne({ _id: id }),
      BlogCommentModel.deleteMany({ blog: id })
    ]);
    
    return true;
  } catch (error) {
    logger.error(`删除博客错误 [ID: ${id}]:`, error);
    throw new ApiError(500, '删除博客失败');
  }
};

/**
 * 获取博客评论
 */
export const getBlogComments = async (params: CommentQueryParams) => {
  try {
    const { page, limit, blog, parentComment } = params;
    const skip = (page - 1) * limit;
    
    // 构建查询条件
    const query: any = { blog, isApproved: true };
    if (parentComment) {
      query.parentComment = parentComment;
    } else {
      query.parentComment = { $exists: false };
    }
    
    // 查询评论
    const [items, total] = await Promise.all([
      BlogCommentModel.find(query)
        .skip(skip)
        .limit(limit)
        .sort({ createdAt: -1 })
        .lean(),
      BlogCommentModel.countDocuments(query)
    ]);
    
    return {
      items,
      total,
      page,
      limit,
      pages: Math.ceil(total / limit)
    };
  } catch (error) {
    logger.error(`获取博客评论错误 [博客ID: ${params.blog}]:`, error);
    throw new ApiError(500, '获取博客评论失败');
  }
};

/**
 * 添加博客评论
 */
export const addBlogComment = async (data: any) => {
  try {
    // 检查博客是否存在
    const blogExists = await BlogModel.exists({ _id: data.blog, status: 'published' });
    if (!blogExists) {
      throw new ApiError(404, '博客不存在或未发布');
    }
    
    // 如果是回复评论，检查父评论是否存在
    if (data.parentComment) {
      const parentCommentExists = await BlogCommentModel.exists({ 
        _id: data.parentComment,
        blog: data.blog,
        isApproved: true
      });
      
      if (!parentCommentExists) {
        throw new ApiError(404, '父评论不存在');
      }
    }
    
    // 创建评论
    const comment = new BlogCommentModel({
      ...data,
      createdAt: new Date(),
      updatedAt: new Date()
    });
    
    await comment.save();
    
    // 更新博客评论计数
    await BlogModel.findByIdAndUpdate(data.blog, { $inc: { commentCount: 1 } });
    
    return comment.toObject();
  } catch (error) {
    logger.error('添加博客评论错误:', error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '添加博客评论失败');
  }
};

/**
 * 点赞博客
 */
export const likeBlog = async (blogId: string) => {
  try {
    const blog = await BlogModel.findOneAndUpdate(
      { _id: blogId, status: 'published' },
      { $inc: { likeCount: 1 } },
      { new: true }
    );
    
    if (!blog) {
      throw new ApiError(404, '博客不存在或未发布');
    }
    
    return { likeCount: blog.likeCount };
  } catch (error) {
    logger.error(`点赞博客错误 [ID: ${blogId}]:`, error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '点赞博客失败');
  }
};

/**
 * 点赞评论
 */
export const likeComment = async (commentId: string) => {
  try {
    const comment = await BlogCommentModel.findOneAndUpdate(
      { _id: commentId, isApproved: true },
      { $inc: { likeCount: 1 } },
      { new: true }
    );
    
    if (!comment) {
      throw new ApiError(404, '评论不存在或未批准');
    }
    
    return { likeCount: comment.likeCount };
  } catch (error) {
    logger.error(`点赞评论错误 [ID: ${commentId}]:`, error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '点赞评论失败');
  }
}; 
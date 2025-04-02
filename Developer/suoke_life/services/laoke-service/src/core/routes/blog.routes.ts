import express from 'express';
import * as blogController from '../../services/blog/blog.controller';
import { authenticate } from '../middleware/auth';
import { validateRequest } from '../middleware/validation';
import { blogSchema, commentSchema } from '../validation/blog.schema';

const router = express.Router();

// 获取博客列表
router.get('/', blogController.getBlogList);

// 获取我的博客列表
router.get('/my-blogs', authenticate, blogController.getMyBlogs);

// 创建博客
router.post('/', authenticate, validateRequest(blogSchema), blogController.createBlog);

// 获取博客详情
router.get('/:id', blogController.getBlogById);

// 更新博客
router.put('/:id', authenticate, validateRequest(blogSchema), blogController.updateBlog);

// 删除博客
router.delete('/:id', authenticate, blogController.deleteBlog);

// 点赞博客
router.post('/:id/like', blogController.likeBlog);

// 获取博客评论
router.get('/:id/comments', blogController.getBlogComments);

// 添加博客评论
router.post('/:id/comments', authenticate, validateRequest(commentSchema), blogController.addBlogComment);

// 点赞评论
router.post('/:id/comments/:commentId/like', blogController.likeComment);

export default router; 
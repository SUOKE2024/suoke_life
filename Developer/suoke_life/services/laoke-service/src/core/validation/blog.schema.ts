import Joi from 'joi';

export const blogSchema = Joi.object({
  title: Joi.string().required().max(200).messages({
    'string.empty': '标题不能为空',
    'string.max': '标题不能超过200个字符',
    'any.required': '标题是必填项'
  }),
  content: Joi.string().required().messages({
    'string.empty': '内容不能为空',
    'any.required': '内容是必填项'
  }),
  summary: Joi.string().required().max(500).messages({
    'string.empty': '摘要不能为空',
    'string.max': '摘要不能超过500个字符',
    'any.required': '摘要是必填项'
  }),
  tags: Joi.array().items(Joi.string().trim()).messages({
    'array.base': '标签必须是数组'
  }),
  status: Joi.string().valid('draft', 'published', 'archived').default('draft').messages({
    'any.only': '状态必须是draft、published或archived之一'
  }),
  featuredImage: Joi.string().uri().allow('').optional().messages({
    'string.uri': '特色图片必须是有效的URL'
  })
});

export const commentSchema = Joi.object({
  content: Joi.string().required().max(1000).messages({
    'string.empty': '评论内容不能为空',
    'string.max': '评论内容不能超过1000个字符',
    'any.required': '评论内容是必填项'
  }),
  parentComment: Joi.string().optional().messages({
    'string.base': '父评论ID必须是字符串'
  })
}); 
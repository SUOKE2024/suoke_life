import { Request, Response, NextFunction } from 'express';
import Joi from 'joi';
import { AppError } from './errorHandler';

// 文本消息请求验证模式
const textMessageSchema = Joi.object({
  userId: Joi.string().required(),
  message: Joi.string().required(),
});

// 语音消息请求验证模式
const voiceMessageSchema = Joi.object({
  userId: Joi.string().required(),
  audioBase64: Joi.string(),
  transcription: Joi.string(),
}).xor('audioBase64', 'transcription'); // 必须提供其中一个

// 图像消息请求验证模式
const imageMessageSchema = Joi.object({
  userId: Joi.string().required(),
  imageBase64: Joi.string().required(),
  caption: Joi.string(),
});

// 无障碍需求更新验证模式
const accessibilityUpdateSchema = Joi.object({
  visuallyImpaired: Joi.boolean(),
  hearingImpaired: Joi.boolean(),
  mobilityImpaired: Joi.boolean(),
  cognitiveImpaired: Joi.boolean(),
  needsVoiceGuidance: Joi.boolean(),
  preferredVoiceSpeed: Joi.number().min(0.5).max(2.0),
  highContrastMode: Joi.boolean(),
  largeTextMode: Joi.boolean(),
  otherNeeds: Joi.string(),
});

/**
 * 验证文本消息请求
 */
export const validateMessageRequest = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const { error } = textMessageSchema.validate(req.body);
  
  if (error) {
    next(new AppError(`请求验证失败: ${error.message}`, 400));
    return;
  }
  
  next();
};

/**
 * 验证语音消息请求
 */
export const validateVoiceMessageRequest = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const { error } = voiceMessageSchema.validate(req.body);
  
  if (error) {
    next(new AppError(`请求验证失败: ${error.message}`, 400));
    return;
  }
  
  next();
};

/**
 * 验证图像消息请求
 */
export const validateImageMessageRequest = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const { error } = imageMessageSchema.validate(req.body);
  
  if (error) {
    next(new AppError(`请求验证失败: ${error.message}`, 400));
    return;
  }
  
  next();
};

/**
 * 验证无障碍需求更新请求
 */
export const validateAccessibilityUpdateRequest = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const { error } = accessibilityUpdateSchema.validate(req.body.accessibilityNeeds);
  
  if (error) {
    next(new AppError(`无障碍需求验证失败: ${error.message}`, 400));
    return;
  }
  
  next();
};
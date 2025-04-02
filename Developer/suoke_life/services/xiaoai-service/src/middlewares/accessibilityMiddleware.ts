import { Request, Response, NextFunction } from 'express';
import User from '../models/User';
import { logger } from '../index';

/**
 * 无障碍中间件 - 为请求添加无障碍支持信息
 */
export const accessibilityMiddleware = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    // 从请求中获取用户ID
    const userId = req.headers['x-user-id'] as string || 
                  req.body.userId ||
                  req.query.userId;
    
    // 如果有用户ID，获取用户的无障碍需求
    if (userId) {
      // 查找用户
      const user = await User.findOne({ userId });
      
      // 如果找到用户，添加无障碍信息到请求对象
      if (user) {
        (req as any).accessibilityNeeds = user.accessibilityNeeds;
        (req as any).voicePreferences = {
          voiceAssistantEnabled: user.preferences.voiceAssistantEnabled,
          voiceAssistantVolume: user.preferences.voiceAssistantVolume,
          preferredLanguage: user.preferences.language,
        };
        
        // 为有无障碍需求的用户设置较长的超时时间
        if (
          user.accessibilityNeeds.visuallyImpaired ||
          user.accessibilityNeeds.hearingImpaired ||
          user.accessibilityNeeds.mobilityImpaired ||
          user.accessibilityNeeds.cognitiveImpaired
        ) {
          // 设置更长的响应超时，以适应特殊需求用户
          res.setTimeout(30000); // 30秒
        }
      }
    }
    
    next();
  } catch (error) {
    logger.error('无障碍中间件错误:', error);
    next(); // 继续处理请求，不阻止
  }
};
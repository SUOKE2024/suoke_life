import { Request, Response } from 'express';
import * as voiceGuidanceService from '../services/voice-guidance/voice-guidance.service';
import { SceneType } from '../models/voice-guidance.model';
import { ApiError } from '../core/utils/errors';
import logger from '../core/utils/logger';
import multer from 'multer';
import path from 'path';
import fs from 'fs';

// 配置音频上传
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(process.cwd(), 'uploads', 'temp');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

export const upload = multer({ 
  storage: storage,
  fileFilter: (req, file, cb) => {
    // 仅接受音频文件
    if (file.mimetype.startsWith('audio/')) {
      cb(null, true);
    } else {
      cb(new Error('只允许上传音频文件') as any);
    }
  },
  limits: {
    fileSize: 10 * 1024 * 1024 // 限制10MB
  }
});

/**
 * 创建语音命令
 */
export const createVoiceCommand = async (req: Request, res: Response) => {
  try {
    const commandData = req.body;
    
    const command = await voiceGuidanceService.createVoiceCommand(commandData);
    
    res.status(201).json({
      success: true,
      data: command
    });
  } catch (error) {
    logger.error('创建语音命令控制器错误:', error);
    handleError(error, res);
  }
};

/**
 * 更新语音命令
 */
export const updateVoiceCommand = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const updateData = req.body;
    
    const command = await voiceGuidanceService.updateVoiceCommand(id, updateData);
    
    res.status(200).json({
      success: true,
      data: command
    });
  } catch (error) {
    logger.error(`更新语音命令控制器错误 [ID: ${req.params.id}]:`, error);
    handleError(error, res);
  }
};

/**
 * 删除语音命令
 */
export const deleteVoiceCommand = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    
    const result = await voiceGuidanceService.deleteVoiceCommand(id);
    
    res.status(200).json({
      success: true,
      data: result
    });
  } catch (error) {
    logger.error(`删除语音命令控制器错误 [ID: ${req.params.id}]:`, error);
    handleError(error, res);
  }
};

/**
 * 获取所有语音命令
 */
export const getAllVoiceCommands = async (req: Request, res: Response) => {
  try {
    const { limit = '100', skip = '0', isEnabled, sceneType } = req.query;
    
    let query: Record<string, any> = {};
    
    if (isEnabled !== undefined) {
      query.isEnabled = isEnabled === 'true';
    }
    
    if (sceneType) {
      query.sceneType = sceneType;
    }
    
    const result = await voiceGuidanceService.getAllVoiceCommands(
      query,
      parseInt(limit as string, 10),
      parseInt(skip as string, 10)
    );
    
    res.status(200).json({
      success: true,
      data: result
    });
  } catch (error) {
    logger.error('获取语音命令列表控制器错误:', error);
    handleError(error, res);
  }
};

/**
 * 获取特定场景的语音命令
 */
export const getVoiceCommandsByScene = async (req: Request, res: Response) => {
  try {
    const { scene } = req.params;
    
    if (!Object.values(SceneType).includes(scene as SceneType)) {
      throw new ApiError(400, `无效的场景类型: ${scene}`);
    }
    
    const commands = await voiceGuidanceService.getVoiceCommandsByScene(scene as SceneType);
    
    res.status(200).json({
      success: true,
      data: commands
    });
  } catch (error) {
    logger.error(`获取场景语音命令控制器错误 [场景: ${req.params.scene}]:`, error);
    handleError(error, res);
  }
};

/**
 * 匹配语音命令
 */
export const matchVoiceCommand = async (req: Request, res: Response) => {
  try {
    const { input, sceneType } = req.body;
    
    if (!input) {
      throw new ApiError(400, '缺少输入文本');
    }
    
    if (!sceneType || !Object.values(SceneType).includes(sceneType)) {
      throw new ApiError(400, `无效的场景类型: ${sceneType}`);
    }
    
    const result = await voiceGuidanceService.matchVoiceCommand(input, sceneType);
    
    res.status(200).json({
      success: true,
      data: result
    });
  } catch (error) {
    logger.error('匹配语音命令控制器错误:', error);
    handleError(error, res);
  }
};

/**
 * 创建语音引导内容
 */
export const createGuidanceContent = async (req: Request, res: Response) => {
  try {
    const contentData = req.body;
    
    const content = await voiceGuidanceService.createGuidanceContent(contentData);
    
    res.status(201).json({
      success: true,
      data: content
    });
  } catch (error) {
    logger.error('创建语音引导内容控制器错误:', error);
    handleError(error, res);
  }
};

/**
 * 更新语音引导内容
 */
export const updateGuidanceContent = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const updateData = req.body;
    
    const content = await voiceGuidanceService.updateGuidanceContent(id, updateData);
    
    res.status(200).json({
      success: true,
      data: content
    });
  } catch (error) {
    logger.error(`更新语音引导内容控制器错误 [ID: ${req.params.id}]:`, error);
    handleError(error, res);
  }
};

/**
 * 删除语音引导内容
 */
export const deleteGuidanceContent = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    
    const result = await voiceGuidanceService.deleteGuidanceContent(id);
    
    res.status(200).json({
      success: true,
      data: result
    });
  } catch (error) {
    logger.error(`删除语音引导内容控制器错误 [ID: ${req.params.id}]:`, error);
    handleError(error, res);
  }
};

/**
 * 获取语音引导内容
 */
export const getGuidanceContents = async (req: Request, res: Response) => {
  try {
    const { limit = '50', skip = '0', isEnabled, sceneType, guidanceType } = req.query;
    
    let query: Record<string, any> = {};
    
    if (isEnabled !== undefined) {
      query.isEnabled = isEnabled === 'true';
    }
    
    if (sceneType) {
      query.sceneType = sceneType;
    }
    
    if (guidanceType) {
      query.guidanceType = guidanceType;
    }
    
    const result = await voiceGuidanceService.getGuidanceContents(
      query,
      parseInt(limit as string, 10),
      parseInt(skip as string, 10)
    );
    
    res.status(200).json({
      success: true,
      data: result
    });
  } catch (error) {
    logger.error('获取语音引导内容列表控制器错误:', error);
    handleError(error, res);
  }
};

/**
 * 根据场景和事件获取匹配的引导内容
 */
export const getContextualGuidance = async (req: Request, res: Response) => {
  try {
    const { sceneType, sceneId, event } = req.params;
    const { context = {} } = req.body;
    
    if (!sceneType || !Object.values(SceneType).includes(sceneType as SceneType)) {
      throw new ApiError(400, `无效的场景类型: ${sceneType}`);
    }
    
    if (!event) {
      throw new ApiError(400, '缺少事件名称');
    }
    
    const guidanceContents = await voiceGuidanceService.getContextualGuidance(
      sceneType as SceneType,
      sceneId,
      event,
      context
    );
    
    res.status(200).json({
      success: true,
      data: guidanceContents
    });
  } catch (error) {
    logger.error(`获取情境引导内容控制器错误 [场景: ${req.params.sceneType}, 事件: ${req.params.event}]:`, error);
    handleError(error, res);
  }
};

/**
 * 生成引导音频
 */
export const generateGuidanceAudio = async (req: Request, res: Response) => {
  try {
    const { guidanceId } = req.params;
    const { dialectCode } = req.query;
    
    const result = await voiceGuidanceService.generateGuidanceAudio(
      guidanceId,
      dialectCode as string | undefined
    );
    
    res.status(200).json({
      success: true,
      data: result
    });
  } catch (error) {
    logger.error(`生成引导音频控制器错误 [引导ID: ${req.params.guidanceId}]:`, error);
    handleError(error, res);
  }
};

/**
 * 获取音频文件
 */
export const getAudioFile = async (req: Request, res: Response) => {
  try {
    const { fileName } = req.params;
    const audioFilePath = path.join(process.cwd(), 'uploads', 'audio', fileName);
    
    if (!fs.existsSync(audioFilePath)) {
      throw new ApiError(404, '音频文件不存在');
    }
    
    res.setHeader('Content-Type', 'audio/mpeg');
    res.setHeader('Content-Disposition', `attachment; filename=${fileName}`);
    
    fs.createReadStream(audioFilePath).pipe(res);
  } catch (error) {
    logger.error(`获取音频文件控制器错误 [文件名: ${req.params.fileName}]:`, error);
    handleError(error, res);
  }
};

/**
 * 创建语音会话
 */
export const createVoiceSession = async (req: Request, res: Response) => {
  try {
    const userData = req.body;
    
    if (!userData.userId) {
      throw new ApiError(400, '缺少用户ID');
    }
    
    if (!userData.deviceInfo || !userData.deviceInfo.deviceId) {
      throw new ApiError(400, '缺少设备信息');
    }
    
    const session = await voiceGuidanceService.createVoiceSession(userData);
    
    res.status(201).json({
      success: true,
      data: {
        sessionId: session.sessionId,
        startTime: session.startTime
      }
    });
  } catch (error) {
    logger.error('创建语音会话控制器错误:', error);
    handleError(error, res);
  }
};

/**
 * 结束语音会话
 */
export const endVoiceSession = async (req: Request, res: Response) => {
  try {
    const { sessionId } = req.params;
    
    const session = await voiceGuidanceService.endVoiceSession(sessionId);
    
    res.status(200).json({
      success: true,
      data: {
        sessionId: session.sessionId,
        startTime: session.startTime,
        endTime: session.endTime,
        duration: session.duration
      }
    });
  } catch (error) {
    logger.error(`结束语音会话控制器错误 [会话ID: ${req.params.sessionId}]:`, error);
    handleError(error, res);
  }
};

/**
 * 更新会话上下文
 */
export const updateSessionContext = async (req: Request, res: Response) => {
  try {
    const { sessionId } = req.params;
    const contextUpdates = req.body;
    
    if (!contextUpdates || Object.keys(contextUpdates).length === 0) {
      throw new ApiError(400, '缺少上下文更新数据');
    }
    
    const session = await voiceGuidanceService.updateSessionContext(sessionId, contextUpdates);
    
    res.status(200).json({
      success: true,
      data: {
        sessionId: session.sessionId,
        context: session.context
      }
    });
  } catch (error) {
    logger.error(`更新会话上下文控制器错误 [会话ID: ${req.params.sessionId}]:`, error);
    handleError(error, res);
  }
};

/**
 * 处理语音输入
 */
export const processVoiceInput = async (req: Request, res: Response) => {
  try {
    if (!req.file) {
      throw new ApiError(400, '缺少音频文件');
    }
    
    const { userId, sessionId, sceneType, dialectCode } = req.body;
    let context = {};
    
    try {
      if (req.body.context) {
        context = JSON.parse(req.body.context);
      }
    } catch (error) {
      logger.warn('解析上下文JSON失败，使用空对象替代');
    }
    
    if (!userId) {
      throw new ApiError(400, '缺少用户ID');
    }
    
    if (!sessionId) {
      throw new ApiError(400, '缺少会话ID');
    }
    
    if (!sceneType || !Object.values(SceneType).includes(sceneType)) {
      throw new ApiError(400, `无效的场景类型: ${sceneType}`);
    }
    
    // 读取上传的音频文件
    const audioBuffer = fs.readFileSync(req.file.path);
    const mimeType = req.file.mimetype;
    
    // 处理语音输入
    const result = await voiceGuidanceService.processVoiceInput(
      audioBuffer,
      mimeType,
      userId,
      sessionId,
      sceneType,
      dialectCode,
      context
    );
    
    // 删除临时文件
    fs.unlinkSync(req.file.path);
    
    res.status(200).json({
      success: true,
      data: result
    });
  } catch (error) {
    // 清理临时文件
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }
    
    logger.error('处理语音输入控制器错误:', error);
    handleError(error, res);
  }
};

/**
 * 处理文本输入
 */
export const processTextInput = async (req: Request, res: Response) => {
  try {
    const { text, userId, sessionId, sceneType, context = {} } = req.body;
    
    if (!text) {
      throw new ApiError(400, '缺少输入文本');
    }
    
    if (!userId) {
      throw new ApiError(400, '缺少用户ID');
    }
    
    if (!sessionId) {
      throw new ApiError(400, '缺少会话ID');
    }
    
    if (!sceneType || !Object.values(SceneType).includes(sceneType)) {
      throw new ApiError(400, `无效的场景类型: ${sceneType}`);
    }
    
    const result = await voiceGuidanceService.processTextInput(
      text,
      userId,
      sessionId,
      sceneType,
      context
    );
    
    res.status(200).json({
      success: true,
      data: result
    });
  } catch (error) {
    logger.error('处理文本输入控制器错误:', error);
    handleError(error, res);
  }
};

/**
 * 获取用户语音偏好设置
 */
export const getVoicePreference = async (req: Request, res: Response) => {
  try {
    const { userId } = req.params;
    
    const preference = await voiceGuidanceService.getVoicePreference(userId);
    
    res.status(200).json({
      success: true,
      data: preference
    });
  } catch (error) {
    logger.error(`获取用户语音偏好设置控制器错误 [用户ID: ${req.params.userId}]:`, error);
    handleError(error, res);
  }
};

/**
 * 更新用户语音偏好设置
 */
export const updateVoicePreference = async (req: Request, res: Response) => {
  try {
    const { userId } = req.params;
    const updateData = req.body;
    
    const preference = await voiceGuidanceService.updateVoicePreference(userId, updateData);
    
    res.status(200).json({
      success: true,
      data: preference
    });
  } catch (error) {
    logger.error(`更新用户语音偏好设置控制器错误 [用户ID: ${req.params.userId}]:`, error);
    handleError(error, res);
  }
};

/**
 * 错误处理函数
 */
const handleError = (error: any, res: Response) => {
  if (error instanceof ApiError) {
    res.status(error.statusCode).json({
      success: false,
      error: {
        message: error.message,
        statusCode: error.statusCode
      }
    });
  } else {
    res.status(500).json({
      success: false,
      error: {
        message: '服务器内部错误',
        statusCode: 500
      }
    });
  }
}; 
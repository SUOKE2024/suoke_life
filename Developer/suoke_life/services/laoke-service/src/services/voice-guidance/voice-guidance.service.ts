import mongoose from 'mongoose';
import { 
  VoiceCommandModel, 
  IVoiceCommand,
  GuidanceContentModel, 
  IGuidanceContent,
  VoiceSessionModel,
  IVoiceSession,
  VoiceInteractionModel,
  IVoiceInteraction,
  VoicePreferenceModel,
  IVoicePreference,
  SceneType,
  GuidanceType,
  CommandPriority
} from '../../models/voice-guidance.model';
import logger from '../../core/utils/logger';
import { ApiError } from '../../core/utils/errors';
import axios from 'axios';
import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import config from '../../core/config';

// 临时音频文件存储路径
const TEMP_AUDIO_PATH = path.join(process.cwd(), 'uploads', 'temp');

// 确保目录存在
if (!fs.existsSync(TEMP_AUDIO_PATH)) {
  fs.mkdirSync(TEMP_AUDIO_PATH, { recursive: true });
}

/**
 * 创建语音命令
 */
export const createVoiceCommand = async (commandData: Partial<IVoiceCommand>): Promise<IVoiceCommand> => {
  try {
    // 检查触发词是否已存在
    const existingCommand = await VoiceCommandModel.findOne({ trigger: commandData.trigger });
    if (existingCommand) {
      throw new ApiError(400, `触发词 "${commandData.trigger}" 已存在`);
    }
    
    const voiceCommand = new VoiceCommandModel(commandData);
    await voiceCommand.save();
    
    return voiceCommand;
  } catch (error) {
    logger.error('创建语音命令失败:', error);
    throw error;
  }
};

/**
 * 更新语音命令
 */
export const updateVoiceCommand = async (
  commandId: string,
  updateData: Partial<IVoiceCommand>
): Promise<IVoiceCommand> => {
  try {
    // 如果更新了触发词，检查新触发词是否已存在
    if (updateData.trigger) {
      const existingCommand = await VoiceCommandModel.findOne({
        trigger: updateData.trigger,
        _id: { $ne: commandId }
      });
      
      if (existingCommand) {
        throw new ApiError(400, `触发词 "${updateData.trigger}" 已存在`);
      }
    }
    
    const command = await VoiceCommandModel.findByIdAndUpdate(
      commandId,
      { $set: updateData },
      { new: true, runValidators: true }
    );
    
    if (!command) {
      throw new ApiError(404, `未找到ID为 ${commandId} 的语音命令`);
    }
    
    return command;
  } catch (error) {
    logger.error(`更新语音命令失败 [ID: ${commandId}]:`, error);
    throw error;
  }
};

/**
 * 删除语音命令
 */
export const deleteVoiceCommand = async (commandId: string): Promise<{ success: boolean }> => {
  try {
    const result = await VoiceCommandModel.findByIdAndDelete(commandId);
    
    if (!result) {
      throw new ApiError(404, `未找到ID为 ${commandId} 的语音命令`);
    }
    
    return { success: true };
  } catch (error) {
    logger.error(`删除语音命令失败 [ID: ${commandId}]:`, error);
    throw error;
  }
};

/**
 * 获取所有语音命令
 */
export const getAllVoiceCommands = async (
  query: Record<string, any> = {},
  limit: number = 100,
  skip: number = 0
): Promise<{ total: number; commands: IVoiceCommand[] }> => {
  try {
    const total = await VoiceCommandModel.countDocuments(query);
    const commands = await VoiceCommandModel.find(query)
      .sort({ priority: -1, trigger: 1 })
      .skip(skip)
      .limit(limit);
    
    return { total, commands };
  } catch (error) {
    logger.error('获取语音命令列表失败:', error);
    throw error;
  }
};

/**
 * 获取特定场景的语音命令
 */
export const getVoiceCommandsByScene = async (
  sceneType: SceneType
): Promise<IVoiceCommand[]> => {
  try {
    // 查询特定场景和全局场景的命令
    const commands = await VoiceCommandModel.find({
      $or: [
        { sceneType: sceneType },
        { sceneType: SceneType.GLOBAL }
      ],
      isEnabled: true
    }).sort({ priority: -1, trigger: 1 });
    
    return commands;
  } catch (error) {
    logger.error(`获取场景语音命令失败 [场景: ${sceneType}]:`, error);
    throw error;
  }
};

/**
 * 匹配语音命令
 */
export const matchVoiceCommand = async (
  inputText: string,
  sceneType: SceneType
): Promise<{ 
  command: IVoiceCommand | null; 
  confidence: number;
  extractedParams?: Record<string, string>;
}> => {
  try {
    // 获取当前场景的所有命令
    const commands = await getVoiceCommandsByScene(sceneType);
    
    if (commands.length === 0) {
      return { command: null, confidence: 0 };
    }
    
    // 准备用于调用AI命令匹配服务的数据
    const commandData = commands.map(cmd => ({
      id: cmd._id.toString(),
      trigger: cmd.trigger,
      aliases: cmd.aliases,
      requiredParams: cmd.requiredParams || [],
      optionalParams: cmd.optionalParams || [],
      examples: cmd.examples
    }));
    
    // 调用AI命令匹配服务
    const response = await axios.post(
      `${config.aiServices.commandMatching}/match`,
      {
        input: inputText,
        commands: commandData,
        language: 'zh-CN'
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': config.aiServices.apiKey
        }
      }
    );
    
    const { matchedCommandId, confidence, extractedParams } = response.data;
    
    if (!matchedCommandId || confidence < 0.6) {
      return { command: null, confidence };
    }
    
    // 查找匹配的命令
    const matchedCommand = commands.find(cmd => cmd._id.toString() === matchedCommandId);
    
    if (!matchedCommand) {
      return { command: null, confidence };
    }
    
    return { 
      command: matchedCommand, 
      confidence,
      extractedParams 
    };
  } catch (error) {
    logger.error(`匹配语音命令失败 [输入: ${inputText}, 场景: ${sceneType}]:`, error);
    throw error;
  }
};

/**
 * 执行语音命令
 */
export const executeVoiceCommand = async (
  userId: string,
  sessionId: string,
  commandId: string,
  params: Record<string, any> = {},
  context: Record<string, any> = {}
): Promise<{
  response: {
    type: string;
    content: string;
    audioUrl?: string;
    visualElements?: Record<string, any>;
  };
  actionResult?: any;
}> => {
  try {
    // 获取命令
    const command = await VoiceCommandModel.findById(commandId);
    
    if (!command) {
      throw new ApiError(404, `未找到ID为 ${commandId} 的语音命令`);
    }
    
    // 检查必填参数
    if (command.requiredParams && command.requiredParams.length > 0) {
      for (const param of command.requiredParams) {
        if (params[param] === undefined) {
          throw new ApiError(400, `缺少必填参数: ${param}`);
        }
      }
    }
    
    // 准备用于调用命令执行服务的数据
    const commandData = {
      action: command.action,
      params,
      context
    };
    
    // 调用命令执行服务
    const response = await axios.post(
      `${config.aiServices.commandExecution}/execute`,
      commandData,
      {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': config.aiServices.apiKey,
          'X-User-ID': userId
        }
      }
    );
    
    const { response: commandResponse, actionResult } = response.data;
    
    // 记录交互
    await recordVoiceInteraction({
      userId,
      sessionId,
      inputType: 'text', // 这里假设是文本输入，实际应该根据情况而定
      rawInput: JSON.stringify(params),
      processedInput: command.trigger,
      matchedCommand: command.trigger,
      matchConfidence: 1.0,
      response: commandResponse,
      actionTaken: actionResult,
      successful: true,
      contextBefore: context,
      contextAfter: response.data.updatedContext || context,
      processingTime: 0 // 实际应该计算处理时间
    });
    
    return {
      response: commandResponse,
      actionResult
    };
  } catch (error) {
    logger.error(`执行语音命令失败 [命令ID: ${commandId}]:`, error);
    
    // 创建错误响应
    const errorResponse = {
      type: 'error',
      content: error instanceof ApiError ? error.message : '命令执行失败'
    };
    
    // 记录失败的交互
    try {
      await recordVoiceInteraction({
        userId,
        sessionId,
        inputType: 'text',
        rawInput: JSON.stringify(params),
        processedInput: '',
        matchedCommand: commandId,
        matchConfidence: 1.0,
        response: errorResponse,
        successful: false,
        errorMessage: error instanceof Error ? error.message : '未知错误',
        contextBefore: context,
        contextAfter: context,
        processingTime: 0
      });
    } catch (logError) {
      logger.error('记录失败交互时出错:', logError);
    }
    
    throw error;
  }
};

/**
 * 创建语音引导内容
 */
export const createGuidanceContent = async (contentData: Partial<IGuidanceContent>): Promise<IGuidanceContent> => {
  try {
    const guidanceContent = new GuidanceContentModel(contentData);
    await guidanceContent.save();
    
    return guidanceContent;
  } catch (error) {
    logger.error('创建语音引导内容失败:', error);
    throw error;
  }
};

/**
 * 更新语音引导内容
 */
export const updateGuidanceContent = async (
  contentId: string,
  updateData: Partial<IGuidanceContent>
): Promise<IGuidanceContent> => {
  try {
    const content = await GuidanceContentModel.findByIdAndUpdate(
      contentId,
      { $set: updateData },
      { new: true, runValidators: true }
    );
    
    if (!content) {
      throw new ApiError(404, `未找到ID为 ${contentId} 的语音引导内容`);
    }
    
    return content;
  } catch (error) {
    logger.error(`更新语音引导内容失败 [ID: ${contentId}]:`, error);
    throw error;
  }
};

/**
 * 删除语音引导内容
 */
export const deleteGuidanceContent = async (contentId: string): Promise<{ success: boolean }> => {
  try {
    const result = await GuidanceContentModel.findByIdAndDelete(contentId);
    
    if (!result) {
      throw new ApiError(404, `未找到ID为 ${contentId} 的语音引导内容`);
    }
    
    return { success: true };
  } catch (error) {
    logger.error(`删除语音引导内容失败 [ID: ${contentId}]:`, error);
    throw error;
  }
};

/**
 * 获取语音引导内容
 */
export const getGuidanceContents = async (
  query: Record<string, any> = {},
  limit: number = 50,
  skip: number = 0
): Promise<{ total: number; contents: IGuidanceContent[] }> => {
  try {
    const total = await GuidanceContentModel.countDocuments(query);
    const contents = await GuidanceContentModel.find(query)
      .sort({ priority: -1, createdAt: -1 })
      .skip(skip)
      .limit(limit);
    
    return { total, contents };
  } catch (error) {
    logger.error('获取语音引导内容列表失败:', error);
    throw error;
  }
};

/**
 * 根据场景和事件获取匹配的引导内容
 */
export const getContextualGuidance = async (
  sceneType: SceneType,
  sceneId: string | undefined,
  event: string,
  context: Record<string, any> = {}
): Promise<IGuidanceContent[]> => {
  try {
    // 查询特定场景和全局场景中启用的引导内容
    const baseQuery = {
      $or: [
        { sceneType },
        { sceneType: SceneType.GLOBAL }
      ],
      isEnabled: true,
      'contextualTriggers.event': event
    };
    
    // 如果提供了场景ID，增加对应的查询条件
    if (sceneId) {
      baseQuery.$or = [
        { sceneType, sceneId },
        { sceneType, sceneId: { $exists: false } },
        { sceneType: SceneType.GLOBAL }
      ];
    }
    
    const guidanceContents = await GuidanceContentModel.find(baseQuery)
      .sort({ priority: -1 });
    
    // 使用AI服务评估上下文条件是否满足
    if (guidanceContents.length > 0 && Object.keys(context).length > 0) {
      // 准备引导内容数据
      const guidanceData = guidanceContents.map(content => ({
        id: content._id.toString(),
        triggers: content.contextualTriggers.filter(trigger => trigger.event === event)
      }));
      
      // 调用AI条件评估服务
      const response = await axios.post(
        `${config.aiServices.contextEvaluation}/evaluate`,
        {
          context,
          guidanceData
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': config.aiServices.apiKey
          }
        }
      );
      
      const { matchedIds } = response.data;
      
      // 过滤出匹配的引导内容
      if (matchedIds && matchedIds.length > 0) {
        return guidanceContents.filter(content => 
          matchedIds.includes(content._id.toString())
        );
      }
      
      return [];
    }
    
    return guidanceContents;
  } catch (error) {
    logger.error(`获取情境引导内容失败 [场景: ${sceneType}, 事件: ${event}]:`, error);
    throw error;
  }
};

/**
 * 生成引导音频
 */
export const generateGuidanceAudio = async (
  guidanceId: string,
  dialectCode?: string
): Promise<{ audioUrl: string }> => {
  try {
    // 获取引导内容
    const guidance = await GuidanceContentModel.findById(guidanceId);
    
    if (!guidance) {
      throw new ApiError(404, `未找到ID为 ${guidanceId} 的语音引导内容`);
    }
    
    let contentText = guidance.content;
    
    // 如果指定了方言代码且内容中有对应方言版本，使用方言版本
    if (dialectCode) {
      const dialectVersion = guidance.dialects.find(d => d.dialectCode === dialectCode);
      if (dialectVersion) {
        // 如果方言版本已有音频URL，直接返回
        if (dialectVersion.audioUrl) {
          return { audioUrl: dialectVersion.audioUrl };
        }
        contentText = dialectVersion.content;
      }
    }
    
    // 如果标准版本已有音频URL且没有指定方言，直接返回
    if (guidance.audioUrl && !dialectCode) {
      return { audioUrl: guidance.audioUrl };
    }
    
    // 调用文本转语音服务
    const response = await axios.post(
      `${config.aiServices.textToSpeech}/synthesize`,
      {
        text: contentText,
        language: dialectCode || 'zh-CN',
        voice: dialectCode ? 'dialect' : 'standard'
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': config.aiServices.apiKey
        },
        responseType: 'arraybuffer'
      }
    );
    
    // 保存音频文件
    const audioFileName = `guidance_${guidanceId}_${dialectCode || 'standard'}_${Date.now()}.mp3`;
    const audioFilePath = path.join(process.cwd(), 'uploads', 'audio', audioFileName);
    
    // 确保目录存在
    const audioDir = path.dirname(audioFilePath);
    if (!fs.existsSync(audioDir)) {
      fs.mkdirSync(audioDir, { recursive: true });
    }
    
    fs.writeFileSync(audioFilePath, response.data);
    
    // 构建音频URL
    const audioUrl = `/api/v1/voice-guidance/audio/${audioFileName}`;
    
    // 更新引导内容的音频URL
    if (dialectCode) {
      // 更新方言版本的音频URL
      await GuidanceContentModel.updateOne(
        { 
          _id: guidanceId,
          'dialects.dialectCode': dialectCode
        },
        {
          $set: {
            'dialects.$.audioUrl': audioUrl
          }
        }
      );
    } else {
      // 更新标准版本的音频URL
      await GuidanceContentModel.findByIdAndUpdate(
        guidanceId,
        {
          $set: {
            audioUrl: audioUrl
          }
        }
      );
    }
    
    return { audioUrl };
  } catch (error) {
    logger.error(`生成引导音频失败 [引导ID: ${guidanceId}]:`, error);
    throw error;
  }
};

/**
 * 创建语音会话
 */
export const createVoiceSession = async (
  userData: {
    userId: string;
    deviceInfo: {
      deviceId: string;
      deviceType: string;
      platform: string;
      osVersion?: string;
      appVersion?: string;
    };
    dialectCode?: string;
    location?: {
      latitude: number;
      longitude: number;
      accuracy: number;
      address?: string;
    };
  }
): Promise<IVoiceSession> => {
  try {
    const sessionId = uuidv4();
    
    const session = new VoiceSessionModel({
      userId: new mongoose.Types.ObjectId(userData.userId),
      sessionId,
      startTime: new Date(),
      deviceInfo: userData.deviceInfo,
      dialectCode: userData.dialectCode,
      location: userData.location,
      interactionCount: 0,
      context: {}
    });
    
    await session.save();
    return session;
  } catch (error) {
    logger.error('创建语音会话失败:', error);
    throw error;
  }
};

/**
 * 结束语音会话
 */
export const endVoiceSession = async (sessionId: string): Promise<IVoiceSession> => {
  try {
    const session = await VoiceSessionModel.findOne({ sessionId });
    
    if (!session) {
      throw new ApiError(404, `未找到ID为 ${sessionId} 的语音会话`);
    }
    
    const now = new Date();
    session.endTime = now;
    
    if (session.startTime) {
      session.duration = (now.getTime() - session.startTime.getTime()) / 1000; // 转换为秒
    }
    
    await session.save();
    return session;
  } catch (error) {
    logger.error(`结束语音会话失败 [会话ID: ${sessionId}]:`, error);
    throw error;
  }
};

/**
 * 更新会话上下文
 */
export const updateSessionContext = async (
  sessionId: string,
  contextUpdates: Record<string, any>
): Promise<IVoiceSession> => {
  try {
    const session = await VoiceSessionModel.findOne({ sessionId });
    
    if (!session) {
      throw new ApiError(404, `未找到ID为 ${sessionId} 的语音会话`);
    }
    
    // 合并上下文
    session.context = {
      ...session.context,
      ...contextUpdates
    };
    
    await session.save();
    return session;
  } catch (error) {
    logger.error(`更新会话上下文失败 [会话ID: ${sessionId}]:`, error);
    throw error;
  }
};

/**
 * 记录语音交互
 */
export const recordVoiceInteraction = async (
  interactionData: {
    userId: string;
    sessionId: string;
    inputType: 'voice' | 'text';
    rawInput: string;
    processedInput: string;
    matchedCommand?: string;
    matchConfidence?: number;
    response: {
      type: string;
      content: string;
      audioUrl?: string;
      visualElements?: Record<string, any>;
    };
    actionTaken?: Record<string, any>;
    successful: boolean;
    errorMessage?: string;
    contextBefore: Record<string, any>;
    contextAfter: Record<string, any>;
    location?: {
      latitude: number;
      longitude: number;
      accuracy: number;
    };
    processingTime: number;
  }
): Promise<IVoiceInteraction> => {
  try {
    // 创建交互记录
    const interaction = new VoiceInteractionModel({
      userId: new mongoose.Types.ObjectId(interactionData.userId),
      sessionId: interactionData.sessionId,
      timestamp: new Date(),
      ...interactionData
    });
    
    await interaction.save();
    
    // 更新会话的交互计数
    await VoiceSessionModel.updateOne(
      { sessionId: interactionData.sessionId },
      {
        $inc: { interactionCount: 1 },
        $set: { 
          lastAccessedAt: new Date(),
          context: interactionData.contextAfter
        }
      }
    );
    
    return interaction;
  } catch (error) {
    logger.error('记录语音交互失败:', error);
    throw error;
  }
};

/**
 * 获取用户语音偏好设置
 */
export const getVoicePreference = async (userId: string): Promise<IVoicePreference> => {
  try {
    let preference = await VoicePreferenceModel.findOne({
      userId: new mongoose.Types.ObjectId(userId)
    });
    
    // 如果没有找到，创建默认设置
    if (!preference) {
      preference = new VoicePreferenceModel({
        userId: new mongoose.Types.ObjectId(userId)
      });
      
      await preference.save();
    }
    
    return preference;
  } catch (error) {
    logger.error(`获取用户语音偏好设置失败 [用户ID: ${userId}]:`, error);
    throw error;
  }
};

/**
 * 更新用户语音偏好设置
 */
export const updateVoicePreference = async (
  userId: string,
  updateData: Partial<IVoicePreference>
): Promise<IVoicePreference> => {
  try {
    let preference = await VoicePreferenceModel.findOne({
      userId: new mongoose.Types.ObjectId(userId)
    });
    
    // 如果没有找到，创建新设置
    if (!preference) {
      preference = new VoicePreferenceModel({
        userId: new mongoose.Types.ObjectId(userId),
        ...updateData
      });
    } else {
      // 更新现有设置
      Object.assign(preference, updateData);
    }
    
    await preference.save();
    return preference;
  } catch (error) {
    logger.error(`更新用户语音偏好设置失败 [用户ID: ${userId}]:`, error);
    throw error;
  }
};

/**
 * 处理语音输入
 */
export const processVoiceInput = async (
  audioBuffer: Buffer,
  mimeType: string,
  userId: string,
  sessionId: string,
  sceneType: SceneType,
  dialectCode?: string,
  context: Record<string, any> = {}
): Promise<{
  text: string;
  command?: IVoiceCommand;
  confidence: number;
  response: {
    type: string;
    content: string;
    audioUrl?: string;
    visualElements?: Record<string, any>;
  };
  actionResult?: any;
}> => {
  try {
    // 保存临时音频文件
    const tempFileName = `voice_input_${uuidv4()}${
      mimeType === 'audio/wav' ? '.wav' : 
      mimeType === 'audio/mp3' ? '.mp3' : 
      mimeType === 'audio/ogg' ? '.ogg' : '.audio'
    }`;
    const tempFilePath = path.join(TEMP_AUDIO_PATH, tempFileName);
    
    fs.writeFileSync(tempFilePath, audioBuffer);
    
    // 开始计时
    const startTime = Date.now();
    
    try {
      // 获取用户偏好设置
      const preferences = await getVoicePreference(userId);
      
      // 调用语音识别服务
      const recognitionResponse = await axios.post(
        `${config.aiServices.speechRecognition}/recognize`,
        fs.readFileSync(tempFilePath),
        {
          headers: {
            'Content-Type': mimeType,
            'X-API-Key': config.aiServices.apiKey,
            'X-Dialect-Code': dialectCode || preferences.dialectCode
          },
          maxBodyLength: Infinity
        }
      );
      
      const { text, confidence: recognitionConfidence } = recognitionResponse.data;
      
      if (!text) {
        throw new ApiError(400, '无法识别语音输入');
      }
      
      // 匹配语音命令
      const { command, confidence, extractedParams } = await matchVoiceCommand(text, sceneType);
      
      let response;
      let actionResult;
      
      // 如果匹配到命令，执行命令
      if (command && confidence >= 0.6) {
        const result = await executeVoiceCommand(
          userId,
          sessionId,
          command._id.toString(),
          extractedParams || {},
          context
        );
        
        response = result.response;
        actionResult = result.actionResult;
      } else {
        // 如果没有匹配到命令，使用AI生成回复
        const aiResponse = await axios.post(
          `${config.aiServices.conversationalAI}/respond`,
          {
            input: text,
            context,
            userId,
            sessionId
          },
          {
            headers: {
              'Content-Type': 'application/json',
              'X-API-Key': config.aiServices.apiKey
            }
          }
        );
        
        response = aiResponse.data.response;
        
        // 更新会话上下文
        await updateSessionContext(sessionId, aiResponse.data.updatedContext || {});
      }
      
      // 计算处理时间
      const processingTime = Date.now() - startTime;
      
      // 记录语音交互
      await recordVoiceInteraction({
        userId,
        sessionId,
        inputType: 'voice',
        rawInput: `[Voice Audio: ${tempFileName}]`,
        processedInput: text,
        matchedCommand: command?.trigger,
        matchConfidence: confidence,
        response,
        actionTaken: actionResult,
        successful: true,
        contextBefore: context,
        contextAfter: context, // 实际应该是更新后的上下文
        processingTime
      });
      
      return {
        text,
        command: command || undefined,
        confidence,
        response,
        actionResult
      };
    } finally {
      // 清理临时文件
      if (fs.existsSync(tempFilePath)) {
        fs.unlinkSync(tempFilePath);
      }
    }
  } catch (error) {
    logger.error('处理语音输入失败:', error);
    
    // 创建错误响应
    const errorResponse = {
      type: 'error',
      content: error instanceof ApiError ? error.message : '处理语音输入失败'
    };
    
    // 记录失败的交互
    try {
      await recordVoiceInteraction({
        userId,
        sessionId,
        inputType: 'voice',
        rawInput: '[Voice Audio]',
        processedInput: '',
        successful: false,
        errorMessage: error instanceof Error ? error.message : '未知错误',
        response: errorResponse,
        contextBefore: context,
        contextAfter: context,
        processingTime: 0
      });
    } catch (logError) {
      logger.error('记录失败交互时出错:', logError);
    }
    
    throw error;
  }
};

/**
 * 处理文本输入
 */
export const processTextInput = async (
  text: string,
  userId: string,
  sessionId: string,
  sceneType: SceneType,
  context: Record<string, any> = {}
): Promise<{
  command?: IVoiceCommand;
  confidence: number;
  response: {
    type: string;
    content: string;
    audioUrl?: string;
    visualElements?: Record<string, any>;
  };
  actionResult?: any;
}> => {
  try {
    // 开始计时
    const startTime = Date.now();
    
    // 匹配语音命令
    const { command, confidence, extractedParams } = await matchVoiceCommand(text, sceneType);
    
    let response;
    let actionResult;
    
    // 如果匹配到命令，执行命令
    if (command && confidence >= 0.6) {
      const result = await executeVoiceCommand(
        userId,
        sessionId,
        command._id.toString(),
        extractedParams || {},
        context
      );
      
      response = result.response;
      actionResult = result.actionResult;
    } else {
      // 如果没有匹配到命令，使用AI生成回复
      const aiResponse = await axios.post(
        `${config.aiServices.conversationalAI}/respond`,
        {
          input: text,
          context,
          userId,
          sessionId
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': config.aiServices.apiKey
          }
        }
      );
      
      response = aiResponse.data.response;
      
      // 更新会话上下文
      await updateSessionContext(sessionId, aiResponse.data.updatedContext || {});
    }
    
    // 计算处理时间
    const processingTime = Date.now() - startTime;
    
    // 记录文本交互
    await recordVoiceInteraction({
      userId,
      sessionId,
      inputType: 'text',
      rawInput: text,
      processedInput: text,
      matchedCommand: command?.trigger,
      matchConfidence: confidence,
      response,
      actionTaken: actionResult,
      successful: true,
      contextBefore: context,
      contextAfter: context, // 实际应该是更新后的上下文
      processingTime
    });
    
    return {
      command: command || undefined,
      confidence,
      response,
      actionResult
    };
  } catch (error) {
    logger.error(`处理文本输入失败 [输入: ${text}]:`, error);
    
    // 创建错误响应
    const errorResponse = {
      type: 'error',
      content: error instanceof ApiError ? error.message : '处理文本输入失败'
    };
    
    // 记录失败的交互
    try {
      await recordVoiceInteraction({
        userId,
        sessionId,
        inputType: 'text',
        rawInput: text,
        processedInput: text,
        successful: false,
        errorMessage: error instanceof Error ? error.message : '未知错误',
        response: errorResponse,
        contextBefore: context,
        contextAfter: context,
        processingTime: 0
      });
    } catch (logError) {
      logger.error('记录失败交互时出错:', logError);
    }
    
    throw error;
  }
}; 
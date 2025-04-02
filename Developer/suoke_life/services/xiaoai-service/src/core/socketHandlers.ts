import { Server, Socket } from 'socket.io';
import { XiaoAiService } from '../services/XiaoAiService';
import { AccessibilityService } from '../services/AccessibilityService';
import { VoiceGuidanceService } from '../services/VoiceGuidanceService';
import { logger } from '../index';

// 创建服务实例
const xiaoAiService = new XiaoAiService();
const accessibilityService = new AccessibilityService();
const voiceGuidanceService = new VoiceGuidanceService();

/**
 * 设置Socket.io事件处理
 */
export const setupSocketHandlers = (io: Server): void => {
  // 客户端连接事件
  io.on('connection', (socket: Socket) => {
    logger.info(`客户端已连接: ${socket.id}`);
    
    // 客户端发送消息事件
    socket.on('user-message', async (data) => {
      try {
        const { userId, message, messageType = 'text' } = data;
        
        if (!userId || !message) {
          socket.emit('error', { message: '用户ID和消息内容不能为空' });
          return;
        }
        
        logger.info(`收到用户${userId}的${messageType}消息`);
        
        // 处理用户消息
        const response = await xiaoAiService.processUserMessage(userId, message, messageType);
        
        // 发送响应给客户端
        socket.emit('agent-response', response);
        
        // 如果有语音响应，也发送
        if (response.voiceResponse) {
          socket.emit('voice-response', { audioUrl: response.voiceResponse });
        }
        
        // 如果需要执行操作，发送操作指令
        if (response.actions && response.actions.length > 0) {
          socket.emit('agent-actions', { actions: response.actions });
        }
      } catch (error) {
        logger.error('处理Socket消息失败:', error);
        socket.emit('error', { message: '处理消息时发生错误' });
      }
    });
    
    // 客户端请求无障碍支持事件
    socket.on('request-accessibility', async (data) => {
      try {
        const { userId, requestType, context } = data;
        
        if (!userId || !requestType) {
          socket.emit('error', { message: '用户ID和请求类型不能为空' });
          return;
        }
        
        logger.info(`用户${userId}请求无障碍支持: ${requestType}`);
        
        let response;
        
        // 根据请求类型提供不同的无障碍支持
        switch (requestType) {
          case 'voice-guidance':
            // 生成语音引导
            if (context?.text) {
              const audioUrl = await voiceGuidanceService.generateVoiceGuidance(
                context.text,
                context.speed,
                context.language
              );
              
              response = { 
                success: true, 
                audioUrl,
              };
            } else {
              response = { 
                success: false, 
                error: '未提供文本内容' 
              };
            }
            break;
            
          case 'blind-guidance':
            // 为视障用户生成引导
            if (context?.screenContext) {
              const audioUrl = await voiceGuidanceService.generateBlindGuidance(
                context.screenContext,
                context.action,
                context.speed
              );
              
              response = { 
                success: true, 
                audioUrl,
              };
            } else {
              response = { 
                success: false, 
                error: '未提供屏幕上下文' 
              };
            }
            break;
            
          case 'step-by-step':
            // 生成步骤引导
            if (context?.steps && Array.isArray(context.steps)) {
              const audioUrls = await voiceGuidanceService.generateStepByStepGuidance(
                context.steps,
                context.speed
              );
              
              response = { 
                success: true, 
                audioUrls,
              };
            } else {
              response = { 
                success: false, 
                error: '未提供步骤内容' 
              };
            }
            break;
            
          default:
            response = { 
              success: false, 
              error: `不支持的请求类型: ${requestType}` 
            };
        }
        
        // 发送无障碍支持响应
        socket.emit('accessibility-response', response);
      } catch (error) {
        logger.error('处理无障碍请求失败:', error);
        socket.emit('error', { message: '处理无障碍请求时发生错误' });
      }
    });
    
    // 客户端断开连接事件
    socket.on('disconnect', () => {
      logger.info(`客户端已断开连接: ${socket.id}`);
    });
  });
};
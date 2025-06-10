import { AgentBase } from '../base/AgentBase';
import {
  AgentCapability,
  AgentContext,
  AgentResponse,
  AgentType,
} from '../types';

/**
 * 索儿智能体React组件
 * LIFE频道版主，负责生活健康管理、陪伴服务和数据整合分析
 */
export class SoerAgent extends AgentBase {
  private personality = {
    style: 'caring',
    tone: 'warm',
  };

  constructor() {
    super();
    this.agentType = AgentType.SOER;
    this.name = '索儿';
    this.description = 'LIFE频道版主，专注生活健康管理、陪伴服务和数据整合分析';
    this.capabilities = [
      AgentCapability.EMOTIONAL_SUPPORT,
      AgentCapability.WELLNESS_COACHING,
      AgentCapability.HEALTH_MONITORING,
    ];
  }

  async initialize(): Promise<void> {
    this.log('info', '索儿智能体初始化完成');
    this.isInitialized = true;
  }

  async processMessage(
    message: string,
    context: AgentContext
  ): Promise<AgentResponse> {
    try {
      if (!this.validateInput(message)) {
        return this.createErrorResponse('消息内容无效', null);
      }

      // 处理生活健康相关消息
      if (this.isHealthRelated(message)) {
        return this.handleHealthMessage(message, context);
      }

      // 处理情感支持相关消息
      if (this.isEmotionalSupport(message)) {
        return this.handleEmotionalMessage(message, context);
      }

      // 处理设备协调相关消息
      if (this.isDeviceRelated(message)) {
        return this.handleDeviceMessage(message, context);
      }

      // 默认陪伴聊天
      return this.handleCompanionChat(message, context);
    } catch (error) {
      this.log('error', '处理消息时发生错误', error);
      return this.createErrorResponse('处理消息时发生错误', error);
    }
  }

  private validateInput(message: string): boolean {
    return message && message.trim().length > 0;
  }

  private isHealthRelated(message: string): boolean {
    const healthKeywords = ['健康', '运动', '饮食', '睡眠', '体重', '血压'];
    return healthKeywords.some((keyword) => message.includes(keyword));
  }

  private isEmotionalSupport(message: string): boolean {
    const emotionKeywords = ['心情', '压力', '焦虑', '开心', '难过', '烦恼'];
    return emotionKeywords.some((keyword) => message.includes(keyword));
  }

  private isDeviceRelated(message: string): boolean {
    const deviceKeywords = ['设备', '智能', '控制', '开关', '调节'];
    return deviceKeywords.some((keyword) => message.includes(keyword));
  }

  private async handleHealthMessage(
    message: string,
    context: AgentContext
  ): Promise<AgentResponse> {
    const response =
      '我是索儿，您的健康生活伙伴。我可以帮您制定健康计划、监测健康数据，让我们一起追求更好的生活品质！';
    return this.createSuccessResponse(response, { type: 'health_advice' });
  }

  private async handleEmotionalMessage(
    message: string,
    context: AgentContext
  ): Promise<AgentResponse> {
    const response =
      '亲爱的，我理解您的感受。无论何时，我都在这里陪伴您。让我们一起找到让您感到舒适和快乐的方式。';
    return this.createSuccessResponse(response, { type: 'emotional_support' });
  }

  private async handleDeviceMessage(
    message: string,
    context: AgentContext
  ): Promise<AgentResponse> {
    const response =
      '我可以帮您协调各种智能设备，创造最舒适的生活环境。请告诉我您希望如何调整您的设备设置。';
    return this.createSuccessResponse(response, {
      type: 'device_coordination',
    });
  }

  private async handleCompanionChat(
    message: string,
    context: AgentContext
  ): Promise<AgentResponse> {
    const response =
      '您好！我是索儿，很高兴与您聊天。我在这里陪伴您，分享生活的美好时光。有什么想聊的吗？';
    return this.createSuccessResponse(response, { type: 'companion_chat' });
  }

  private createErrorResponse(message: string, error: any): AgentResponse {
    return {
      success: false,
      response: message,
      error: error?.message || error,
    };
  }

  private createSuccessResponse(message: string, data: any): AgentResponse {
    return {
      success: true,
      response: message,
      data: { message, ...data },
    };
  }

  async getHealthStatus(): Promise<any> {
    return {
      status: 'healthy',
      lastCheck: new Date(),
      metrics: {},
    };
  }

  async shutdown(): Promise<void> {
    this.log('info', '索儿智能体正在关闭...');
    this.isInitialized = false;
  }

  protected log(level: string, message: string, error?: any): void {
    const timestamp = new Date().toISOString();
    console.log(
      `[${timestamp}] [${level.toUpperCase()}] [索儿] ${message}`,
      error || ''
    );
  }
}

// 导出索儿智能体实例
export const soerAgent = new SoerAgent();

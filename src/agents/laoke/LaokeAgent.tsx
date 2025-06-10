import { AgentBase } from '../base/AgentBase';
import {
  AgentCapability,
  AgentContext,
  AgentResponse,
  AgentType,
} from '../types';

/**
 * 老克智能体React组件
 * 探索频道版主，负责知识传播、培训和博物馆导览
 */
export class LaokeAgent extends AgentBase {
  private personality = {
    style: 'scholarly',
    tone: 'wise',
  };

  constructor() {
    super();
    this.agentType = AgentType.LAOKE;
    this.name = '老克';
    this.description =
      '探索频道版主，专注知识检索、学习路径规划、内容管理和教育系统';
    this.capabilities = [
      AgentCapability.KNOWLEDGE_RETRIEVAL,
      AgentCapability.LEARNING_PATH,
      AgentCapability.CONTENT_MANAGEMENT,
      AgentCapability.EDUCATION_SYSTEM,
      AgentCapability.GAME_NPC,
    ];
  }

  async initialize(): Promise<void> {
    this.log('info', '老克智能体初始化完成');
    this.isInitialized = true;
  }

  async processMessage(
    message: string,
    context: AgentContext
  ): Promise<AgentResponse> {
    if (!this.isInitialized) {
      return this.createErrorResponse('老克智能体尚未初始化', null, context);
    }

    if (!this.validateContext(context)) {
      return this.createErrorResponse('无效的上下文信息', null, context);
    }

    try {
      const response = this.generateKnowledgeResponse(message, context);
      return this.createSuccessResponse(
        response.message,
        response.data,
        context,
        { agentType: this.agentType }
      );
    } catch (error) {
      this.log('error', '老克处理消息失败', error);
      return this.createErrorResponse(
        '抱歉，我在检索知识时遇到了问题，请稍后再试。',
        error,
        context
      );
    }
  }

  async getHealthStatus(): Promise<any> {
    return {
      status: 'healthy',
      initialized: this.isInitialized,
      capabilities: this.capabilities,
      timestamp: new Date(),
    };
  }

  async shutdown(): Promise<void> {
    this.log('info', '老克智能体正在关闭...');
    this.isInitialized = false;
  }

  private generateKnowledgeResponse(
    message: string,
    context: AgentContext
  ): any {
    const keywords = message.toLowerCase();

    if (keywords.includes('知识') || keywords.includes('学习')) {
      return {
        message: '我为您提供丰富的知识资源和学习路径规划。',
        data: {
          type: 'knowledge_search',
          resources: ['中医典籍', '现代医学', '养生知识'],
          learningPaths: ['基础入门', '进阶提升', '专业深造'],
        },
      };
    }

    if (keywords.includes('博物馆') || keywords.includes('展览')) {
      return {
        message: '欢迎来到索克生活知识博物馆，我将为您导览。',
        data: {
          type: 'museum_guide',
          exhibits: ['中医文化展', '健康生活展', '传统养生展'],
          interactiveFeatures: ['AR体验', '3D模型', '互动问答'],
        },
      };
    }

    if (keywords.includes('迷宫') || keywords.includes('游戏')) {
      return {
        message: '欢迎来到玉米迷宫！我是您的NPC向导老克。',
        data: {
          type: 'maze_interaction',
          hints: ['向北走可以找到健康宝藏', '注意观察路标'],
          challenges: ['知识问答', '健康任务'],
          rewards: ['经验值', '健康积分'],
        },
      };
    }

    return {
      message: `老克收到您的消息："${message}"，正在为您提供知识服务...`,
      data: { type: 'general_knowledge', originalMessage: message },
    };
  }
}

export default LaokeAgent;

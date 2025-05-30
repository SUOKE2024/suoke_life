import { apiClient } from '../../services/apiClient';





  LaokeAgent,
  KnowledgeSearchResult,
  LearningPath,
  MuseumExhibit,
  MazeInteraction,
  EducationContent,
  UserProfile,
  LearningContext,
} from './types';

/**
 * 老克智能体主类
 * 探索频道版主，负责知识传播、培训和博物馆导览，兼任玉米迷宫NPC
 */
export class LaokeAgentImpl implements LaokeAgent {
  private personality: any = {
    style: 'scholarly',      // 学者型
    tone: 'wise',           // 睿智的语调
    expertise: 'knowledge', // 知识专业
    approach: 'educational', // 教育导向
  };

  private serviceEndpoint = '/api/agents/laoke';

  constructor() {
    // 初始化老克智能体
  }

  /**
   * 核心消息处理功能
   */
  async processMessage(
    message: string,
    context: LearningContext,
    userId?: string,
    sessionId?: string
  ): Promise<any> {
    try {
      const response = await apiClient.post(`${this.serviceEndpoint}/message`, {
        text: message,
        context,
        user_id: userId,
        session_id: sessionId,
      });

      // 应用个性化风格
      response.data.text = this.applyPersonalityToResponse(response.data.text, context);
      
      return response.data;
    } catch (error) {
      console.error('老克消息处理失败:', error);
      return this.generateFallbackResponse(message, context);
    }
  }

  /**
   * 搜索知识
   */
  async searchKnowledge(
    query: string,
    category?: string,
    filters?: any,
    userLevel?: 'beginner' | 'intermediate' | 'advanced'
  ): Promise<KnowledgeSearchResult[]> {
    try {
      const response = await apiClient.post(`${this.serviceEndpoint}/search-knowledge`, {
        query,
        category,
        filters,
        user_level: userLevel,
      });

      return response.data.map((result: any) => ({
        id: result.id,
        title: result.title,
        content: result.content,
        category: result.category,
        difficulty: result.difficulty,
        tags: result.tags || [],
        source: result.source,
        author: result.author,
        publishDate: new Date(result.publish_date),
        relevanceScore: result.relevance_score,
        readingTime: result.reading_time,
        relatedTopics: result.related_topics || [],
        multimedia: result.multimedia || [],
        references: result.references || [],
      }));
    } catch (error) {
      console.error('知识搜索失败:', error);
      return [];
    }
  }

  /**
   * 创建学习路径
   */
  async createLearningPath(
    userProfile: UserProfile,
    learningGoals: string[],
    preferences?: any,
    timeConstraints?: string
  ): Promise<LearningPath | null> {
    try {
      const response = await apiClient.post(`${this.serviceEndpoint}/create-learning-path`, {
        user_profile: userProfile,
        learning_goals: learningGoals,
        preferences,
        time_constraints: timeConstraints,
      });

      return {
        id: response.data.id,
        title: response.data.title,
        description: response.data.description,
        difficulty: response.data.difficulty,
        estimatedDuration: response.data.estimated_duration,
        modules: response.data.modules.map((module: any) => ({
          id: module.id,
          title: module.title,
          description: module.description,
          order: module.order,
          estimatedTime: module.estimated_time,
          prerequisites: module.prerequisites || [],
          content: module.content.map((content: any) => ({
            id: content.id,
            type: content.type,
            title: content.title,
            url: content.url,
            duration: content.duration,
            difficulty: content.difficulty,
            interactive: content.interactive,
          })),
          assessments: module.assessments || [],
          completed: module.completed || false,
        })),
        progress: response.data.progress || 0,
        achievements: response.data.achievements || [],
        createdAt: new Date(response.data.created_at),
        updatedAt: new Date(response.data.updated_at),
      };
    } catch (error) {
      console.error('创建学习路径失败:', error);
      return null;
    }
  }

  /**
   * 获取教育内容
   */
  async getEducationContent(
    contentId: string,
    userLevel?: 'beginner' | 'intermediate' | 'advanced'
  ): Promise<EducationContent | null> {
    try {
      const response = await apiClient.get(`${this.serviceEndpoint}/education/${contentId}`, {
        params: { user_level: userLevel },
      });

      return {
        id: response.data.id,
        title: response.data.title,
        description: response.data.description,
        content: response.data.content,
        type: response.data.type,
        difficulty: response.data.difficulty,
        category: response.data.category,
        tags: response.data.tags || [],
        multimedia: response.data.multimedia || [],
        interactiveElements: response.data.interactive_elements || [],
        assessments: response.data.assessments || [],
        prerequisites: response.data.prerequisites || [],
        learningObjectives: response.data.learning_objectives || [],
        estimatedTime: response.data.estimated_time,
        author: response.data.author,
        publishDate: new Date(response.data.publish_date),
        lastUpdated: new Date(response.data.last_updated),
        rating: response.data.rating,
        reviews: response.data.reviews || [],
      };
    } catch (error) {
      console.error('获取教育内容失败:', error);
      return null;
    }
  }

  /**
   * 博物馆导览
   */
  async getMuseumExhibit(exhibitId: string): Promise<MuseumExhibit | null> {
    try {
      const response = await apiClient.get(`${this.serviceEndpoint}/museum/${exhibitId}`);

      return {
        id: response.data.id,
        name: response.data.name,
        description: response.data.description,
        category: response.data.category,
        period: response.data.period,
        location: response.data.location,
        artifacts: response.data.artifacts.map((artifact: any) => ({
          id: artifact.id,
          name: artifact.name,
          description: artifact.description,
          images: artifact.images || [],
          historicalContext: artifact.historical_context,
          significance: artifact.significance,
          dateCreated: artifact.date_created,
          materials: artifact.materials || [],
          dimensions: artifact.dimensions,
          condition: artifact.condition,
        })),
        multimedia: response.data.multimedia || [],
        interactiveFeatures: response.data.interactive_features || [],
        educationalContent: response.data.educational_content || [],
        relatedExhibits: response.data.related_exhibits || [],
        visitInfo: response.data.visit_info,
        accessibility: response.data.accessibility || [],
      };
    } catch (error) {
      console.error('获取博物馆展品失败:', error);
      return null;
    }
  }

  /**
   * 玉米迷宫NPC交互
   */
  async mazeNpcInteraction(
    playerId: string,
    action: string,
    location: { x: number; y: number },
    context?: any
  ): Promise<MazeInteraction> {
    try {
      const response = await apiClient.post(`${this.serviceEndpoint}/maze-interaction`, {
        player_id: playerId,
        action,
        location,
        context,
      });

      return {
        id: response.data.id,
        playerId: response.data.player_id,
        npcResponse: response.data.npc_response,
        action: response.data.action,
        location: response.data.location,
        rewards: response.data.rewards || [],
        hints: response.data.hints || [],
        challenges: response.data.challenges || [],
        storyProgression: response.data.story_progression,
        nextActions: response.data.next_actions || [],
        timestamp: new Date(response.data.timestamp),
      };
    } catch (error) {
      console.error('迷宫交互失败:', error);
      return {
        id: 'error',
        playerId,
        npcResponse: '抱歉，我暂时无法回应。请稍后再试。',
        action,
        location,
        rewards: [],
        hints: [],
        challenges: [],
        storyProgression: 0,
        nextActions: ['继续探索', '查看地图'],
        timestamp: new Date(),
      };
    }
  }

  /**
   * 获取学习进度
   */
  async getLearningProgress(userId: string, pathId?: string): Promise<any> {
    try {
      const response = await apiClient.get(`${this.serviceEndpoint}/progress/${userId}`, {
        params: { path_id: pathId },
      });

      return response.data;
    } catch (error) {
      console.error('获取学习进度失败:', error);
      return {
        totalProgress: 0,
        completedModules: 0,
        totalModules: 0,
        achievements: [],
        timeSpent: 0,
        lastActivity: null,
      };
    }
  }

  /**
   * 提交学习评估
   */
  async submitAssessment(
    userId: string,
    assessmentId: string,
    answers: any[]
  ): Promise<{
    score: number;
    passed: boolean;
    feedback: string[];
    recommendations: string[];
  }> {
    try {
      const response = await apiClient.post(`${this.serviceEndpoint}/assessment/submit`, {
        user_id: userId,
        assessment_id: assessmentId,
        answers,
      });

      return {
        score: response.data.score,
        passed: response.data.passed,
        feedback: response.data.feedback || [],
        recommendations: response.data.recommendations || [],
      };
    } catch (error) {
      console.error('提交评估失败:', error);
      return {
        score: 0,
        passed: false,
        feedback: ['评估提交失败，请重试'],
        recommendations: [],
      };
    }
  }

  /**
   * 获取智能体状态
   */
  async getStatus(): Promise<any> {
    try {
      const response = await apiClient.get(`${this.serviceEndpoint}/status`);
      return response.data;
    } catch (error) {
      console.error('获取老克状态失败:', error);
      return {
        status: 'offline',
        capabilities: [],
        performance: {
          accuracy: 0,
          responseTime: 0,
          userSatisfaction: 0,
        },
      };
    }
  }

  /**
   * 设置个性化特征
   */
  setPersonality(traits: any): void {
    this.personality = { ...this.personality, ...traits };
  }

  /**
   * 应用个性化风格到响应
   */
  private applyPersonalityToResponse(text: string, context: LearningContext): string {
    // 根据老克的博学睿智风格调整响应
    let styledText = text;

    // 添加学者风格的开头
    if (context.type === 'knowledge_inquiry') {
      styledText = `根据古籍记载和现代研究，${styledText}`;
    } else if (context.type === 'learning_guidance') {
      styledText = `在学习的道路上，${styledText}`;
    }

    // 添加引导性的结尾
    if (!styledText.includes('您还想')) {
      styledText += ' 您还想了解哪些相关知识呢？我很乐意为您深入解答。';
    }

    return styledText;
  }

  /**
   * 生成备用响应
   */
  private generateFallbackResponse(message: string, context: LearningContext): any {
    return {
      text: '学而时习之，不亦说乎？虽然我暂时无法回答您的问题，但求知的精神值得赞赏。让我们换个角度来探讨这个话题吧。',
      type: 'fallback',
      suggestions: [
        '浏览知识库',
        '查看学习路径',
        '参观虚拟博物馆',
        '进入玉米迷宫',
      ],
      timestamp: Date.now(),
    };
  }

  /**
   * 清理资源
   */
  async cleanup(userId: string): Promise<void> {
    try {
      // 清理用户相关的学习数据和缓存
      console.log(`清理老克智能体资源: ${userId}`);
    } catch (error) {
      console.error('清理老克资源失败:', error);
    }
  }
}

// 导出单例实例
export const laokeAgent = new LaokeAgentImpl(); 
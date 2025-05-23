import axios from 'axios';
import { AGENT_SERVICE_PORTS } from '../../config/constants';

// 创建专门的老克服务客户端
const laokeClient = axios.create({
  baseURL: `http://localhost:${AGENT_SERVICE_PORTS.LAOKE}`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 知识文章类型
export interface KnowledgeArticle {
  id: string;
  title: string;
  content: string;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
  author: string;
  publishDate: string;
  readTime: number;
  likes: number;
  views: number;
}

// 学习路径类型
export interface LearningPath {
  id: string;
  title: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime: string;
  topics: string[];
  prerequisites: string[];
  modules: Array<{
    id: string;
    title: string;
    description: string;
    articles: string[];
    exercises: string[];
  }>;
}

// 社区帖子类型
export interface CommunityPost {
  id: string;
  title: string;
  content: string;
  author: string;
  category: string;
  tags: string[];
  likes: number;
  replies: number;
  createdAt: string;
  updatedAt: string;
}

// 智能体交互请求类型
export interface AgentInteractionRequest {
  userId: string;
  sessionId: string;
  message: string;
  context?: {
    currentTopic?: string;
    learningProgress?: any;
    userPreferences?: any;
  };
}

// 学习进度类型
export interface LearningProgress {
  userId: string;
  pathId: string;
  completedModules: string[];
  currentModule: string;
  progressPercentage: number;
  timeSpent: number;
  achievements: string[];
  nextRecommendations: string[];
}

// 老克智能体API服务
const laokeApi = {
  /**
   * 获取知识文章列表
   * @param category 分类
   * @param difficulty 难度
   * @param limit 限制数量
   * @param offset 偏移量
   * @returns 知识文章列表
   */
  getKnowledgeArticles: async (
    category?: string, 
    difficulty?: string, 
    limit: number = 20, 
    offset: number = 0
  ): Promise<KnowledgeArticle[]> => {
    try {
      const response = await laokeClient.get('/api/v1/knowledge/articles', {
        params: {
          category,
          difficulty,
          limit,
          offset
        }
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '获取知识文章失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取指定文章详情
   * @param articleId 文章ID
   * @returns 文章详情
   */
  getArticleById: async (articleId: string): Promise<KnowledgeArticle> => {
    try {
      const response = await laokeClient.get(`/api/v1/knowledge/articles/${articleId}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '获取文章详情失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 搜索知识内容
   * @param query 搜索关键词
   * @param filters 过滤条件
   * @returns 搜索结果
   */
  searchKnowledge: async (query: string, filters?: Record<string, any>) => {
    try {
      const response = await laokeClient.post('/api/v1/knowledge/search', {
        query,
        filters: filters || {}
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '知识搜索失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取学习路径列表
   * @param difficulty 难度
   * @param topic 主题
   * @returns 学习路径列表
   */
  getLearningPaths: async (difficulty?: string, topic?: string): Promise<LearningPath[]> => {
    try {
      const response = await laokeClient.get('/api/v1/learning/paths', {
        params: {
          difficulty,
          topic
        }
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '获取学习路径失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取个性化学习路径推荐
   * @param userId 用户ID
   * @param preferences 用户偏好
   * @returns 推荐的学习路径
   */
  getPersonalizedLearningPaths: async (userId: string, preferences?: any) => {
    try {
      const response = await laokeClient.post('/api/v1/learning/personalized', {
        user_id: userId,
        preferences: preferences || {}
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '获取个性化学习路径失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 报名学习路径
   * @param userId 用户ID
   * @param pathId 学习路径ID
   * @returns 报名结果
   */
  enrollLearningPath: async (userId: string, pathId: string) => {
    try {
      const response = await laokeClient.post('/api/v1/learning/enroll', {
        user_id: userId,
        path_id: pathId
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '学习路径报名失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取学习进度
   * @param userId 用户ID
   * @param pathId 学习路径ID
   * @returns 学习进度
   */
  getLearningProgress: async (userId: string, pathId: string): Promise<LearningProgress> => {
    try {
      const response = await laokeClient.get(`/api/v1/learning/progress/${userId}/${pathId}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '获取学习进度失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 更新学习进度
   * @param userId 用户ID
   * @param pathId 学习路径ID
   * @param moduleId 模块ID
   * @param completed 是否完成
   * @returns 更新结果
   */
  updateLearningProgress: async (userId: string, pathId: string, moduleId: string, completed: boolean) => {
    try {
      const response = await laokeClient.post('/api/v1/learning/progress/update', {
        user_id: userId,
        path_id: pathId,
        module_id: moduleId,
        completed: completed
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '更新学习进度失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取社区帖子列表
   * @param category 分类
   * @param limit 限制数量
   * @param offset 偏移量
   * @returns 社区帖子列表
   */
  getCommunityPosts: async (
    category?: string, 
    limit: number = 20, 
    offset: number = 0
  ): Promise<CommunityPost[]> => {
    try {
      const response = await laokeClient.get('/api/v1/community/posts', {
        params: {
          category,
          limit,
          offset
        }
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '获取社区帖子失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 创建社区帖子
   * @param postData 帖子数据
   * @returns 创建结果
   */
  createCommunityPost: async (postData: Partial<CommunityPost>) => {
    try {
      const response = await laokeClient.post('/api/v1/community/posts', postData);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '创建社区帖子失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 与老克智能体交互
   * @param data 交互请求数据
   * @returns 智能体响应
   */
  agentInteraction: async (data: AgentInteractionRequest) => {
    try {
      const response = await laokeClient.post('/api/v1/agent/interact', {
        user_id: data.userId,
        session_id: data.sessionId,
        message: data.message,
        context: data.context || {}
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '智能体交互失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取知识问答
   * @param question 问题
   * @param context 上下文
   * @returns 问答结果
   */
  askQuestion: async (question: string, context?: any) => {
    try {
      const response = await laokeClient.post('/api/v1/knowledge/qa', {
        question,
        context: context || {}
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '知识问答失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取游戏NPC交互
   * @param userId 用户ID
   * @param gameContext 游戏上下文
   * @param action 用户动作
   * @returns NPC响应
   */
  npcInteraction: async (userId: string, gameContext: any, action: string) => {
    try {
      const response = await laokeClient.post('/api/v1/game/npc/interact', {
        user_id: userId,
        game_context: gameContext,
        action: action
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || 'NPC交互失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取用户学习统计
   * @param userId 用户ID
   * @returns 学习统计数据
   */
  getUserLearningStats: async (userId: string) => {
    try {
      const response = await laokeClient.get(`/api/v1/learning/stats/${userId}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '获取学习统计失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取推荐内容
   * @param userId 用户ID
   * @param type 推荐类型
   * @returns 推荐内容
   */
  getRecommendations: async (userId: string, type: 'articles' | 'paths' | 'posts') => {
    try {
      const response = await laokeClient.get(`/api/v1/recommendations/${type}`, {
        params: { user_id: userId }
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '获取推荐内容失败';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 健康检查
   * @returns 健康状态
   */
  healthCheck: async () => {
    try {
      const response = await laokeClient.get('/health/status');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || '健康检查失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },
};

export default laokeApi;
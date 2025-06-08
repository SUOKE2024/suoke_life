import { apiClient } from './apiClient';
import {/**
* 玉米迷宫服务客户端
* Corn Maze Service Client;
*/
  Maze,
  MazeProgress,
  MazeTemplate,
  KnowledgeNode,
  Challenge,
  MazeStats,
  LeaderboardEntry,
  GameSettings,
  MazeInteraction,
  CreateMazeRequest,
  UpdateMazeRequest,
  StartMazeRequest,
  MoveRequest,
  ListMazesRequest,
  MazeResponse,
  MoveResponse,
  UserProgressResponse,
  ListMazesResponse,
  ListTemplatesResponse,
  Direction,
  Position,
  MazeTheme,
  MazeDifficulty,
  GameReward;
} from '../types/maze';
/**
* 玉米迷宫服务配置
*/
interface CornMazeServiceConfig {
  baseURL: string;
  timeout: number;
  retryAttempts: number;
  enableCache: boolean;
}
/**
* 默认配置
*/
const DEFAULT_CONFIG: CornMazeServiceConfig = {,
  baseURL: process.env.CORN_MAZE_SERVICE_URL || 'http://localhost:51057',
  timeout: 10000,
  retryAttempts: 3,
  enableCache: true;
};
/**
* 玉米迷宫服务客户端类
*/
export class CornMazeService {
  private config: CornMazeServiceConfig;
  private cache: Map<string, any> = new Map();
  private cacheTimeout: number = 5 * 60 * 1000; // 5分钟缓存
  constructor(config?: Partial<CornMazeServiceConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }
  /**
  * 健康检查
  */
  async healthCheck(): Promise<{ status: string; version: string; timestamp: string }> {
    try {
      const response = await apiClient.get(`${this.config.baseURL}/health`);
      return response.data;
    } catch (error) {
      console.error('Corn Maze Service health check failed:', error);
      throw new Error('服务健康检查失败');
    }
  }
  /**
  * 创建迷宫
  */
  async createMaze(request: CreateMazeRequest): Promise<Maze> {
    try {
      const response = await apiClient.post<MazeResponse>(;)
        `${this.config.baseURL}/api/v1/mazes`,request;
      );
      return response.data.maze;
    } catch (error) {
      console.error('Failed to create maze:', error);
      throw new Error('创建迷宫失败');
    }
  }
  /**
  * 获取迷宫信息
  */
  async getMaze(mazeId: string, userId?: string): Promise<MazeResponse> {
    const cacheKey = `maze_${mazeId}_${userId || 'anonymous'}`;
    // 检查缓存
    if (this.config.enableCache && this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }
    try {
      const params = userId ? { user_id: userId } : {};
      const response = await apiClient.get<MazeResponse>(;)
        `${this.config.baseURL}/api/v1/mazes/${mazeId}`,{ params };
      );
      // 缓存结果
      if (this.config.enableCache) {
        this.cache.set(cacheKey, {
          data: response.data,
          timestamp: Date.now();
        });
      }
      return response.data;
    } catch (error) {
      console.error('Failed to get maze:', error);
      throw new Error('获取迷宫信息失败');
    }
  }
  /**
  * 更新迷宫
  */
  async updateMaze(mazeId: string, request: UpdateMazeRequest): Promise<Maze> {
    try {
      const response = await apiClient.put<MazeResponse>(;)
        `${this.config.baseURL}/api/v1/mazes/${mazeId}`,request;
      );
      // 清除相关缓存
      this.clearMazeCache(mazeId);
      return response.data.maze;
    } catch (error) {
      console.error('Failed to update maze:', error);
      throw new Error('更新迷宫失败');
    }
  }
  /**
  * 删除迷宫
  */
  async deleteMaze(mazeId: string): Promise<void> {
    try {
      await apiClient.delete(`${this.config.baseURL}/api/v1/mazes/${mazeId}`);
      // 清除相关缓存
      this.clearMazeCache(mazeId);
    } catch (error) {
      console.error('Failed to delete maze:', error);
      throw new Error('删除迷宫失败');
    }
  }
  /**
  * 获取迷宫列表
  */
  async listMazes(request?: ListMazesRequest): Promise<ListMazesResponse> {
    try {
      const response = await apiClient.get<ListMazesResponse>(;)
        `${this.config.baseURL}/api/v1/mazes`,{ params: request };
      );
      return response.data;
    } catch (error) {
      console.error('Failed to list mazes:', error);
      throw new Error('获取迷宫列表失败');
    }
  }
  /**
  * 开始迷宫游戏
  */
  async startMaze(request: StartMazeRequest): Promise<MazeProgress> {
    try {
      const response = await apiClient.post<{ progress: MazeProgress }>(;)
        `${this.config.baseURL}/api/v1/mazes/${request.mazeId}/start`,{ user_id: request.userId };
      );
      return response.data.progress;
    } catch (error) {
      console.error('Failed to start maze:', error);
      throw new Error('开始迷宫游戏失败');
    }
  }
  /**
  * 在迷宫中移动
  */
  async moveInMaze(request: MoveRequest): Promise<MoveResponse> {
    try {
      const response = await apiClient.post<MoveResponse>(;)
        `${this.config.baseURL}/api/v1/mazes/${request.mazeId}/move`,{user_id: request.userId,direction: request.direction;
        };
      );
      // 清除进度缓存
      this.clearProgressCache(request.userId, request.mazeId);
      return response.data;
    } catch (error) {
      console.error('Failed to move in maze:', error);
      throw new Error('迷宫移动失败');
    }
  }
  /**
  * 获取用户进度
  */
  async getUserProgress(mazeId: string, userId: string): Promise<UserProgressResponse> {
    const cacheKey = `progress_${userId}_${mazeId}`;
    // 检查缓存
    if (this.config.enableCache && this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }
    try {
      const response = await apiClient.get<UserProgressResponse>(;)
        `${this.config.baseURL}/api/v1/mazes/${mazeId}/progress/${userId}`;
      );
      // 缓存结果
      if (this.config.enableCache) {
        this.cache.set(cacheKey, {
          data: response.data,
          timestamp: Date.now();
        });
      }
      return response.data;
    } catch (error) {
      console.error('Failed to get user progress:', error);
      throw new Error('获取用户进度失败');
    }
  }
  /**
  * 获取迷宫模板列表
  */
  async listMazeTemplates()
    mazeType?: MazeTheme,
    difficulty?: MazeDifficulty,
    page: number = 1,
    pageSize: number = 20;
  ): Promise<ListTemplatesResponse> {
    try {
      const params: any = { page, page_size: pageSize };
      if (mazeType) params.maze_type = mazeType;
      if (difficulty) params.difficulty = difficulty;
      const response = await apiClient.get<ListTemplatesResponse>(;)
        `${this.config.baseURL}/api/v1/templates`,{ params };
      );
      return response.data;
    } catch (error) {
      console.error('Failed to list maze templates:', error);
      throw new Error('获取迷宫模板失败');
    }
  }
  /**
  * 记录迷宫完成
  */
  async recordMazeCompletion()
    userId: string,
    mazeId: string,
    stepsTaken: number,
    completionTime: number,
    score: number;
  ): Promise<{ rewards: GameReward[]; achievements: string[] }> {
    try {
      const response = await apiClient.post(;)
        `${this.config.baseURL}/api/v1/mazes/${mazeId}/complete`,{user_id: userId,steps_taken: stepsTaken,completion_time: completionTime,score: score;
        };
      );
      // 清除相关缓存
      this.clearProgressCache(userId, mazeId);
      return response.data;
    } catch (error) {
      console.error('Failed to record maze completion:', error);
      throw new Error('记录迷宫完成失败');
    }
  }
  /**
  * 获取知识节点详情
  */
  async getKnowledgeNode(nodeId: string): Promise<KnowledgeNode> {
    const cacheKey = `knowledge_${nodeId}`;
    // 检查缓存
    if (this.config.enableCache && this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }
    try {
      const response = await apiClient.get<{ node: KnowledgeNode }>(;)
        `${this.config.baseURL}/api/v1/knowledge/${nodeId}`;
      );
      // 缓存结果
      if (this.config.enableCache) {
        this.cache.set(cacheKey, {
          data: response.data.node,
          timestamp: Date.now();
        });
      }
      return response.data.node;
    } catch (error) {
      console.error('Failed to get knowledge node:', error);
      throw new Error('获取知识节点失败');
    }
  }
  /**
  * 获取挑战详情
  */
  async getChallenge(challengeId: string): Promise<Challenge> {
    const cacheKey = `challenge_${challengeId}`;
    // 检查缓存
    if (this.config.enableCache && this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }
    try {
      const response = await apiClient.get<{ challenge: Challenge }>(;)
        `${this.config.baseURL}/api/v1/challenges/${challengeId}`;
      );
      // 缓存结果
      if (this.config.enableCache) {
        this.cache.set(cacheKey, {
          data: response.data.challenge,
          timestamp: Date.now();
        });
      }
      return response.data.challenge;
    } catch (error) {
      console.error('Failed to get challenge:', error);
      throw new Error('获取挑战详情失败');
    }
  }
  /**
  * 提交挑战答案
  */
  async submitChallengeAnswer()
    challengeId: string,
    userId: string,
    answers: string[]
  ): Promise<{ correct: boolean; score: number; explanation?: string }> {
    try {
      const response = await apiClient.post(;)
        `${this.config.baseURL}/api/v1/challenges/${challengeId}/submit`,{user_id: userId,answers: answers;
        };
      );
      return response.data;
    } catch (error) {
      console.error('Failed to submit challenge answer:', error);
      throw new Error('提交挑战答案失败');
    }
  }
  /**
  * 获取用户统计信息
  */
  async getUserStats(userId: string): Promise<MazeStats> {
    try {
      const response = await apiClient.get<MazeStats>(;)
        `${this.config.baseURL}/api/v1/users/${userId}/stats`;
      );
      return response.data;
    } catch (error) {
      console.error('Failed to get user stats:', error);
      throw new Error('获取用户统计失败');
    }
  }
  /**
  * 获取排行榜
  */
  async getLeaderboard()
    mazeId?: string,
    limit: number = 10;
  ): Promise<LeaderboardEntry[]> {
    try {
      const params: any = { limit };
      if (mazeId) params.maze_id = mazeId;
      const response = await apiClient.get<{ entries: LeaderboardEntry[] }>(;)
        `${this.config.baseURL}/api/v1/leaderboard`,{ params };
      );
      return response.data.entries;
    } catch (error) {
      console.error('Failed to get leaderboard:', error);
      throw new Error('获取排行榜失败');
    }
  }
  /**
  * 智能体迷宫交互
  */
  async mazeNpcInteraction()
    playerId: string,
    action: string,
    location: Position,
    context?: any;
  ): Promise<MazeInteraction> {
    try {
      const response = await apiClient.post<MazeInteraction>(;)
        `${this.config.baseURL}/api/v1/maze-interaction`,{player_id: playerId,action,location,context;
        };
      );
      return response.data;
    } catch (error) {
      console.error('Failed to interact with maze NPC:', error);
      // 返回默认响应而不是抛出错误
      return {id: 'error',playerId,npcResponse: '抱歉，我暂时无法回应。请稍后再试。',action,location,rewards: [],hints: [],challenges: [],storyProgression: 0,nextActions: ["继续探索",查看地图'],timestamp: new Date();
      };
    }
  }
  /**
  * 获取游戏设置
  */
  async getGameSettings(userId: string): Promise<GameSettings> {
    try {
      const response = await apiClient.get<GameSettings>(;)
        `${this.config.baseURL}/api/v1/users/${userId}/settings`;
      );
      return response.data;
    } catch (error) {
      console.error('Failed to get game settings:', error);
      // 返回默认设置
      return {soundEnabled: true,musicEnabled: true,vibrationEnabled: true,autoSave: true,difficulty: MazeDifficulty.NORMAL,showHints: true,animationSpeed: 'normal',colorScheme: 'auto';
      };
    }
  }
  /**
  * 更新游戏设置
  */
  async updateGameSettings(userId: string, settings: Partial<GameSettings>): Promise<GameSettings> {
    try {
      const response = await apiClient.put<GameSettings>(;)
        `${this.config.baseURL}/api/v1/users/${userId}/settings`,settings;
      );
      return response.data;
    } catch (error) {
      console.error('Failed to update game settings:', error);
      throw new Error('更新游戏设置失败');
    }
  }
  /**
  * 清除迷宫相关缓存
  */
  private clearMazeCache(mazeId: string): void {
    const keysToDelete: string[] = [];
    for (const key of this.cache.keys()) {
      if (key.includes(`maze_${mazeId}`)) {
        keysToDelete.push(key);
      }
    }
    keysToDelete.forEach(key => this.cache.delete(key));
  }
  /**
  * 清除进度相关缓存
  */
  private clearProgressCache(userId: string, mazeId: string): void {
    const progressKey = `progress_${userId}_${mazeId}`;
    this.cache.delete(progressKey);
  }
  /**
  * 清除所有缓存
  */
  clearCache(): void {
    this.cache.clear();
  }
  /**
  * 获取缓存统计
  */
  getCacheStats(): { size: number; keys: string[] } {
    return {size: this.cache.size,keys: Array.from(this.cache.keys());
    };
  }
}
/**
* 默认的玉米迷宫服务实例
*/
export const cornMazeService = new CornMazeService();
/**
* 创建自定义配置的服务实例
*/
export const createCornMazeService = (config?: Partial<CornMazeServiceConfig>) => {return new CornMazeService(config);
};
export default cornMazeService;
/**
 * 玉米迷宫服务类型定义
 * Corn Maze Service Type Definitions
 */

// 基础枚举类型
export enum MazeTheme {
  HEALTH_PATH = 'health_path',           // 健康之路
  NUTRITION_GARDEN = 'nutrition_garden', // 营养花园
  TCM_JOURNEY = 'tcm_journey',          // 中医之旅
  BALANCED_LIFE = 'balanced_life'        // 平衡生活
}

export enum MazeDifficulty {
  EASY = 'easy',       // 简单
  NORMAL = 'normal',   // 普通
  HARD = 'hard',       // 困难
  EXPERT = 'expert'    // 专家
}

export enum NodeType {
  EMPTY = 'empty',         // 空地
  PATH = 'path',           // 路径
  WALL = 'wall',           // 墙壁
  START = 'start',         // 起点
  END = 'end',             // 终点
  KNOWLEDGE = 'knowledge', // 知识节点
  CHALLENGE = 'challenge', // 挑战节点
  REWARD = 'reward'        // 奖励节点
}

export enum Direction {
  NORTH = 'north',  // 北
  EAST = 'east',    // 东
  SOUTH = 'south',  // 南
  WEST = 'west'     // 西
}

export enum ProgressStatus {
  NOT_STARTED = 'not_started', // 未开始
  IN_PROGRESS = 'in_progress', // 进行中
  COMPLETED = 'completed',     // 已完成
  PAUSED = 'paused'           // 暂停
}

export enum GameEventType {
  NONE = 'none',               // 无事件
  KNOWLEDGE = 'knowledge',     // 知识事件
  CHALLENGE = 'challenge',     // 挑战事件
  REWARD = 'reward',          // 奖励事件
  GOAL = 'goal',              // 到达终点
  WALL_HIT = 'wall_hit'       // 撞墙
}

// 位置坐标
export interface Position {
  x: number;
  y: number;
}

// 迷宫节点
export interface MazeNode {
  x: number;
  y: number;
  nodeType: NodeType;
  content?: string;           // 节点内容
  knowledgeId?: string;       // 知识点ID
  challengeId?: string;       // 挑战ID
  visited?: boolean;          // 是否已访问
  accessible?: boolean;       // 是否可访问
}

// 知识节点详情
export interface KnowledgeNode {
  nodeId: string;
  title: string;
  content: string;
  category: string;           // 分类：四季养生、五行平衡等
  difficultyLevel: string;
  relatedTags: string[];
  multimedia?: {
    images?: string[];
    videos?: string[];
    audio?: string[];
  };
  interactiveElements?: any[];
  estimatedReadTime?: number; // 预计阅读时间（分钟）
}

// 挑战任务
export interface Challenge {
  challengeId: string;
  title: string;
  description: string;
  type: 'multiple_choice' | 'matching' | 'sorting' | 'fill_blank'; // 题型
  difficultyLevel: string;
  questions: ChallengeQuestion[];
  rewardDescription: string;
  timeLimit?: number;         // 时间限制（秒）
  maxAttempts?: number;       // 最大尝试次数
}

// 挑战题目
export interface ChallengeQuestion {
  questionId: string;
  question: string;
  options?: string[];         // 选择题选项
  correctAnswer: string | string[];
  explanation?: string;       // 答案解释
  hints?: string[];          // 提示
}

// 迷宫基本信息
export interface Maze {
  id: string;
  name: string;
  description?: string;
  size: number;               // 迷宫大小 (size x size)
  theme: MazeTheme;
  difficulty: MazeDifficulty;
  creatorId: string;
  nodes: MazeNode[][];        // 二维节点数组
  startPosition: Position;
  endPosition: Position;
  knowledgeNodes: KnowledgeNode[];
  challenges: Challenge[];
  createdAt: Date;
  updatedAt: Date;
  isPublic?: boolean;         // 是否公开
  tags?: string[];           // 标签
  estimatedTime?: number;     // 预计完成时间（分钟）
}

// 用户迷宫进度
export interface MazeProgress {
  userId: string;
  mazeId: string;
  status: ProgressStatus;
  currentPosition: Position;
  visitedNodes: Position[];   // 已访问的节点位置
  collectedItems: string[];   // 收集的物品ID
  completedChallenges: string[]; // 完成的挑战ID
  acquiredKnowledge: string[];   // 获得的知识点ID
  score: number;
  stepsCount: number;         // 步数统计
  startTime: Date;
  lastActiveTime: Date;
  completionTime?: Date;
  achievements?: string[];    // 获得的成就
  hints?: number;            // 使用的提示次数
}

// 迷宫模板
export interface MazeTemplate {
  templateId: string;
  name: string;
  description: string;
  mazeType: MazeTheme;
  difficulty: MazeDifficulty;
  previewImageUrl?: string;
  sizeX: number;
  sizeY: number;
  knowledgeNodeCount: number;
  challengeCount: number;
  isPopular?: boolean;
  rating?: number;
  usageCount?: number;
}

// API请求类型
export interface CreateMazeRequest {
  name: string;
  description?: string;
  size?: number;
  theme: MazeTheme;
  difficulty: MazeDifficulty;
  useTemplate?: boolean;
  templateId?: string;
  customNodes?: MazeNode[][];
}

export interface UpdateMazeRequest {
  name?: string;
  description?: string;
  difficulty?: MazeDifficulty;
  isPublic?: boolean;
  tags?: string[];
}

export interface StartMazeRequest {
  userId: string;
  mazeId: string;
}

export interface MoveRequest {
  userId: string;
  mazeId: string;
  direction: Direction;
}

export interface ListMazesRequest {
  page?: number;
  size?: number;
  theme?: MazeTheme;
  difficulty?: MazeDifficulty;
  isPublic?: boolean;
  creatorId?: string;
  tags?: string[];
}

// API响应类型
export interface MazeResponse {
  maze: Maze;
  userProgress?: MazeProgress;
}

export interface MoveResponse {
  success: boolean;
  newPosition: Position;
  eventType: GameEventType;
  eventId?: string;
  message?: string;
  knowledgeNode?: KnowledgeNode;
  challenge?: Challenge;
  reward?: GameReward;
  gameCompleted?: boolean;
  score?: number;
}

export interface UserProgressResponse {
  progress: MazeProgress;
  maze: Maze;
  nextRecommendations?: string[];
}

export interface ListMazesResponse {
  mazes: Maze[];
  total: number;
  page: number;
  size: number;
  hasNext: boolean;
}

export interface ListTemplatesResponse {
  templates: MazeTemplate[];
  total: number;
  page: number;
  size: number;
}

// 游戏奖励
export interface GameReward {
  rewardId: string;
  type: 'points' | 'badge' | 'item' | 'knowledge';
  name: string;
  description: string;
  value: number;
  icon?: string;
  rarity?: 'common' | 'rare' | 'epic' | 'legendary';
}

// 智能体迷宫交互
export interface MazeInteraction {
  id: string;
  playerId: string;
  npcResponse: string;
  action: string;
  location: Position;
  rewards: GameReward[];
  hints: string[];
  challenges: Challenge[];
  storyProgression: number;   // 故事进度 0-100
  nextActions: string[];
  timestamp: Date;
  agentType?: 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';
  contextualAdvice?: string;  // 上下文建议
}

// 迷宫统计信息
export interface MazeStats {
  totalMazes: number;
  completedMazes: number;
  averageScore: number;
  totalPlayTime: number;      // 总游戏时间（分钟）
  favoriteTheme: MazeTheme;
  achievements: string[];
  rank?: number;              // 排名
  level?: number;             // 等级
}

// 排行榜条目
export interface LeaderboardEntry {
  userId: string;
  username: string;
  avatar?: string;
  score: number;
  completionTime: number;     // 完成时间（秒）
  rank: number;
  mazeId: string;
  mazeName: string;
  achievedAt: Date;
}

// 游戏设置
export interface GameSettings {
  soundEnabled: boolean;
  musicEnabled: boolean;
  vibrationEnabled: boolean;
  autoSave: boolean;
  difficulty: MazeDifficulty;
  showHints: boolean;
  animationSpeed: 'slow' | 'normal' | 'fast';
  colorScheme: 'light' | 'dark' | 'auto';
}

// 错误类型
export interface MazeError {
  code: string;
  message: string;
  details?: any;
  timestamp: Date;
}

// 事件监听器类型
export type MazeEventListener = (event: MazeGameEvent) => void;

export interface MazeGameEvent {
  type: GameEventType;
  data: any;
  timestamp: Date;
}

// 所有类型已通过interface和enum关键字导出，无需重复导出 
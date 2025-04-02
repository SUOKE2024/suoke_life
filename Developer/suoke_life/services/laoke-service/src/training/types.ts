/**
 * 知识培训模块类型定义
 */
import { 
  ContentType,
  KnowledgeDomain,
  DifficultyLevel,
  ContentStatus
} from '../knowledge/types';

/**
 * 学习路径类型
 */
export enum LearningPathType {
  // 技能提升
  SKILL_IMPROVEMENT = 'skill_improvement',
  // 知识探索
  KNOWLEDGE_EXPLORATION = 'knowledge_exploration',
  // 系统学习
  SYSTEMATIC_LEARNING = 'systematic_learning',
  // 认证课程
  CERTIFICATION = 'certification',
  // 快速入门
  QUICK_START = 'quick_start'
}

/**
 * 学习方式枚举
 */
export enum LearningMode {
  // 自主学习
  SELF_PACED = 'self_paced',
  // 指导学习
  GUIDED = 'guided',
  // 社群学习
  COMMUNITY = 'community',
  // 混合模式
  BLENDED = 'blended'
}

/**
 * 学习资源类型枚举
 */
export enum LearningResourceType {
  // 文章
  ARTICLE = 'article',
  // 视频
  VIDEO = 'video',
  // 音频
  AUDIO = 'audio',
  // 测验
  QUIZ = 'quiz',
  // 练习
  EXERCISE = 'exercise',
  // 案例分析
  CASE_STUDY = 'case_study',
  // 实践项目
  PROJECT = 'project',
  // 交互式模拟
  SIMULATION = 'simulation',
  // 参考资料
  REFERENCE = 'reference'
}

/**
 * 问题类型枚举
 */
export enum QuestionType {
  // 单选题
  SINGLE_CHOICE = 'single_choice',
  // 多选题
  MULTIPLE_CHOICE = 'multiple_choice',
  // 判断题
  TRUE_FALSE = 'true_false',
  // 填空题
  FILL_BLANK = 'fill_blank',
  // 匹配题
  MATCHING = 'matching',
  // 排序题
  ORDERING = 'ordering',
  // 简答题
  SHORT_ANSWER = 'short_answer',
  // 论述题
  ESSAY = 'essay'
}

/**
 * 认证类型枚举
 */
export enum CertificationType {
  // 完成证书
  COMPLETION = 'completion',
  // 能力证书
  COMPETENCY = 'competency',
  // 专业认证
  PROFESSIONAL = 'professional',
  // 参与证明
  PARTICIPATION = 'participation'
}

/**
 * 学习状态枚举
 */
export enum LearningStatus {
  // 未开始
  NOT_STARTED = 'not_started',
  // 进行中
  IN_PROGRESS = 'in_progress',
  // 已完成
  COMPLETED = 'completed',
  // 已暂停
  PAUSED = 'paused',
  // 已放弃
  ABANDONED = 'abandoned'
}

/**
 * 学习路径接口
 */
export interface LearningPath {
  // 路径ID
  id: string;
  // 标题
  title: string;
  // 路径类型
  type: LearningPathType;
  // 描述
  description: string;
  // 学习领域
  domain: KnowledgeDomain;
  // 难度级别
  difficulty: DifficultyLevel;
  // 预计完成时间(小时)
  estimatedDuration: number;
  // 学习节点
  nodes: LearningNode[];
  // 创建者ID
  creatorId: string;
  // 创建时间
  createdAt: Date;
  // 更新时间
  updatedAt: Date;
  // 标签
  tags: string[];
  // 路径状态
  status: ContentStatus;
  // 学习模式
  learningMode: LearningMode;
  // 先修路径ID
  prerequisites?: string[];
  // 后续推荐路径ID
  nextPathIds?: string[];
  // 认证类型
  certificationType?: CertificationType;
  // 完成条件描述
  completionCriteria: string;
  // 学习人数
  enrollmentCount: number;
  // 完成人数
  completionCount: number;
  // 评分(0-5)
  rating: number;
  // 评分人数
  ratingCount: number;
}

/**
 * 学习节点接口
 */
export interface LearningNode {
  // 节点ID
  id: string;
  // 标题
  title: string;
  // 描述
  description?: string;
  // 序号
  order: number;
  // 是否必修
  required: boolean;
  // 预计时长(分钟)
  duration: number;
  // 学习资源
  resources: LearningResource[];
  // 完成条件
  completionRequirements: CompletionRequirement[];
  // 后续节点ID
  nextNodeIds?: string[];
  // 依赖节点ID
  dependsOnNodeIds?: string[];
}

/**
 * 学习资源接口
 */
export interface LearningResource {
  // 资源ID
  id: string;
  // 标题
  title: string;
  // 资源类型
  type: LearningResourceType;
  // 内容ID
  contentId: string;
  // 描述
  description?: string;
  // 序号
  order: number;
  // 是否必修
  required: boolean;
  // 预计时长(分钟)
  duration: number;
  // 自定义元数据
  metadata?: Record<string, any>;
}

/**
 * 完成要求接口
 */
export interface CompletionRequirement {
  // 要求ID
  id: string;
  // 要求类型
  type: 'view' | 'quiz' | 'exercise' | 'project' | 'time' | 'custom';
  // 要求目标ID
  targetId?: string;
  // 最低分数(百分比)
  minimumScore?: number;
  // 最低时长(分钟)
  minimumTime?: number;
  // 要求描述
  description: string;
  // 自定义验证函数ID
  validatorId?: string;
}

/**
 * 测验接口
 */
export interface Quiz {
  // 测验ID
  id: string;
  // 标题
  title: string;
  // 描述
  description: string;
  // 知识领域
  domain: KnowledgeDomain;
  // 难度级别
  difficulty: DifficultyLevel;
  // 问题列表
  questions: Question[];
  // 及格分数(百分比)
  passingScore: number;
  // 时间限制(分钟)，0表示无限制
  timeLimit: number;
  // 允许重试次数，-1表示无限制
  allowedAttempts: number;
  // 是否随机顺序
  randomOrder: boolean;
  // 创建者ID
  creatorId: string;
  // 创建时间
  createdAt: Date;
  // 更新时间
  updatedAt: Date;
  // 标签
  tags: string[];
}

/**
 * 问题接口
 */
export interface Question {
  // 问题ID
  id: string;
  // 问题文本
  text: string;
  // 问题类型
  type: QuestionType;
  // 难度级别
  difficulty: DifficultyLevel;
  // 分值
  points: number;
  // 选项列表(对于选择题)
  options?: QuestionOption[];
  // 正确答案
  answer: string | string[];
  // 解释
  explanation?: string;
  // 知识点
  knowledgePoints?: string[];
  // 提示
  hints?: string[];
  // 标签
  tags?: string[];
}

/**
 * 问题选项接口
 */
export interface QuestionOption {
  // 选项ID
  id: string;
  // 选项文本
  text: string;
  // 是否正确
  isCorrect: boolean;
  // 选择该选项时的反馈
  feedback?: string;
}

/**
 * 用户学习记录接口
 */
export interface UserLearningRecord {
  // 记录ID
  id: string;
  // 用户ID
  userId: string;
  // 学习路径ID
  pathId: string;
  // 学习状态
  status: LearningStatus;
  // 开始时间
  startedAt: Date;
  // 最后活动时间
  lastActivityAt: Date;
  // 完成时间
  completedAt?: Date;
  // 总学习时长(分钟)
  totalLearningTime: number;
  // 节点进度
  nodeProgress: NodeProgress[];
  // 测验尝试
  quizAttempts: QuizAttempt[];
  // 获得的徽章ID
  earnedBadgeIds: string[];
  // 认证ID
  certificationId?: string;
  // 笔记
  notes: LearningNote[];
  // 自定义进度数据
  customProgressData?: Record<string, any>;
}

/**
 * 节点进度接口
 */
export interface NodeProgress {
  // 节点ID
  nodeId: string;
  // 进度状态
  status: LearningStatus;
  // 完成百分比
  completionPercentage: number;
  // 学习时长(分钟)
  learningTime: number;
  // 资源进度
  resourceProgress: ResourceProgress[];
  // 最后活动时间
  lastActivityAt: Date;
}

/**
 * 资源进度接口
 */
export interface ResourceProgress {
  // 资源ID
  resourceId: string;
  // 进度状态
  status: LearningStatus;
  // 完成百分比
  completionPercentage: number;
  // 学习时长(分钟)
  learningTime: number;
  // 位置标记(如视频时间点，文章滚动位置)
  position?: number;
  // 最后活动时间
  lastActivityAt: Date;
}

/**
 * 测验尝试接口
 */
export interface QuizAttempt {
  // 尝试ID
  id: string;
  // 测验ID
  quizId: string;
  // 开始时间
  startedAt: Date;
  // 提交时间
  submittedAt?: Date;
  // 分数
  score: number;
  // 总分
  totalPoints: number;
  // 得分百分比
  percentage: number;
  // 是否通过
  passed: boolean;
  // 用时(秒)
  timeTaken: number;
  // 答案
  answers: QuestionAnswer[];
}

/**
 * 问题答案接口
 */
export interface QuestionAnswer {
  // 问题ID
  questionId: string;
  // 用户答案
  userAnswer: string | string[];
  // 是否正确
  isCorrect: boolean;
  // 得分
  score: number;
  // 总分
  totalPoints: number;
  // 反馈
  feedback?: string;
}

/**
 * 学习笔记接口
 */
export interface LearningNote {
  // 笔记ID
  id: string;
  // 相关资源ID
  resourceId?: string;
  // 相关节点ID
  nodeId?: string;
  // 内容
  content: string;
  // 创建时间
  createdAt: Date;
  // 更新时间
  updatedAt: Date;
  // 标签
  tags?: string[];
  // 位置标记(如视频时间点，文章段落)
  position?: number | string;
}

/**
 * 认证接口
 */
export interface Certification {
  // 认证ID
  id: string;
  // 用户ID
  userId: string;
  // 学习路径ID
  pathId: string;
  // 认证类型
  type: CertificationType;
  // 认证名称
  name: string;
  // 发布日期
  issuedAt: Date;
  // 有效期至
  validUntil?: Date;
  // 证书编号
  certificateNumber: string;
  // 颁发机构
  issuingAuthority: string;
  // 认证详情
  details: string;
  // 验证URL
  verificationUrl?: string;
  // 证书图像URL
  imageUrl?: string;
  // 是否已验证
  verified: boolean;
  // 成绩
  grade?: string;
}

/**
 * 徽章接口
 */
export interface Badge {
  // 徽章ID
  id: string;
  // 名称
  name: string;
  // 描述
  description: string;
  // 图标URL
  iconUrl: string;
  // 获取条件
  criteria: string;
  // 徽章级别
  level: 'bronze' | 'silver' | 'gold' | 'platinum';
  // 徽章类别
  category: string;
  // 是否为隐藏徽章
  hidden: boolean;
  // 获得人数
  earnedCount: number;
  // 创建时间
  createdAt: Date;
}
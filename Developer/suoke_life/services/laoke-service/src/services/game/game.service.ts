import logger from '../../core/utils/logger';
import { GameQuestModel } from '../../models/game-quest.model';
import { GameUserProgressModel } from '../../models/game-user-progress.model';
import { ApiError } from '../../core/utils/errors';

/**
 * 任务查询参数
 */
interface QuestQueryParams {
  page: number;
  limit: number;
  type?: 'main' | 'side' | 'daily' | 'event' | 'challenge';
  difficulty?: 'easy' | 'medium' | 'hard' | 'expert';
  isActive?: boolean;
}

/**
 * 获取游戏任务列表
 */
export const getQuestList = async (params: QuestQueryParams) => {
  try {
    const { page, limit, type, difficulty, isActive = true } = params;
    const skip = (page - 1) * limit;
    
    // 构建查询条件
    const query: any = { isActive };
    if (type) {
      query.type = type;
    }
    if (difficulty) {
      query.difficulty = difficulty;
    }
    
    // 只返回当前可用的任务（未过期）
    const now = new Date();
    query.$or = [
      { endDate: { $exists: false } },
      { endDate: null },
      { endDate: { $gt: now } }
    ];
    query.$and = [
      { $or: [
        { startDate: { $exists: false } },
        { startDate: null },
        { startDate: { $lte: now } }
      ]}
    ];
    
    // 查询数据
    const [items, total] = await Promise.all([
      GameQuestModel.find(query)
        .skip(skip)
        .limit(limit)
        .sort({ createdAt: -1 })
        .lean(),
      GameQuestModel.countDocuments(query)
    ]);
    
    return {
      items,
      total,
      page,
      limit,
      pages: Math.ceil(total / limit)
    };
  } catch (error) {
    logger.error('获取游戏任务列表错误:', error);
    throw new ApiError(500, '获取游戏任务列表失败');
  }
};

/**
 * 获取任务详情
 */
export const getQuestById = async (id: string, userId?: string) => {
  try {
    const quest = await GameQuestModel.findOne({ 
      _id: id, 
      isActive: true 
    }).lean();
    
    if (!quest) {
      return null;
    }
    
    // 如果提供了用户ID，获取任务进度
    let progress = null;
    if (userId) {
      const userProgress = await GameUserProgressModel.findOne({
        userId,
        'quests.questId': id
      }).lean();
      
      if (userProgress) {
        progress = userProgress.quests.find(q => q.questId.toString() === id);
      }
    }
    
    return {
      ...quest,
      progress
    };
  } catch (error) {
    logger.error(`获取任务详情错误 [ID: ${id}]:`, error);
    throw new ApiError(500, '获取任务详情失败');
  }
};

/**
 * 接受任务
 */
export const acceptQuest = async (questId: string, userId: string) => {
  try {
    // 检查任务是否存在且可接受
    const quest = await GameQuestModel.findOne({ 
      _id: questId, 
      isActive: true 
    });
    
    if (!quest) {
      throw new ApiError(404, '任务不存在或不可用');
    }
    
    // 检查任务是否在有效期内
    const now = new Date();
    if (quest.startDate && quest.startDate > now) {
      throw new ApiError(400, '任务尚未开始');
    }
    if (quest.endDate && quest.endDate < now) {
      throw new ApiError(400, '任务已结束');
    }
    
    // 查找用户进度
    let userProgress = await GameUserProgressModel.findOne({ userId });
    
    // 如果用户没有进度记录，创建一个新的
    if (!userProgress) {
      userProgress = new GameUserProgressModel({
        userId,
        quests: [],
        level: 1,
        experience: 0,
        points: 0,
        achievements: [],
        inventory: [],
        lastPlayedAt: now,
        createdAt: now,
        updatedAt: now
      });
    }
    
    // 检查用户是否已接受此任务
    const existingQuestIndex = userProgress.quests.findIndex(
      q => q.questId.toString() === questId
    );
    
    if (existingQuestIndex >= 0) {
      const existingQuest = userProgress.quests[existingQuestIndex];
      if (existingQuest.status === 'completed') {
        throw new ApiError(400, '您已完成此任务');
      }
      if (existingQuest.status === 'in_progress') {
        throw new ApiError(400, '您已接受此任务');
      }
      
      // 如果任务状态是failed或not_started，重新开始任务
      userProgress.quests[existingQuestIndex] = {
        questId,
        status: 'in_progress',
        startedAt: now,
        steps: quest.steps.map((step, index) => ({
          stepIndex: index,
          completed: false
        }))
      };
    } else {
      // 添加新任务
      userProgress.quests.push({
        questId,
        status: 'in_progress',
        startedAt: now,
        steps: quest.steps.map((step, index) => ({
          stepIndex: index,
          completed: false
        }))
      });
    }
    
    userProgress.lastPlayedAt = now;
    userProgress.updatedAt = now;
    
    await userProgress.save();
    
    // 返回更新后的任务进度
    const updatedQuest = userProgress.quests.find(
      q => q.questId.toString() === questId
    );
    
    return {
      quest: {
        ...quest.toObject(),
        progress: updatedQuest
      }
    };
  } catch (error) {
    logger.error(`接受任务错误 [任务ID: ${questId}, 用户ID: ${userId}]:`, error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '接受任务失败');
  }
};

/**
 * 更新任务步骤
 */
export const updateQuestStep = async (questId: string, stepIndex: number, data: any, userId: string) => {
  try {
    // 检查任务是否存在
    const quest = await GameQuestModel.findOne({ _id: questId, isActive: true });
    
    if (!quest) {
      throw new ApiError(404, '任务不存在或不可用');
    }
    
    // 检查步骤是否存在
    if (!quest.steps[stepIndex]) {
      throw new ApiError(404, '任务步骤不存在');
    }
    
    // 查找用户进度
    const userProgress = await GameUserProgressModel.findOne({ userId });
    
    if (!userProgress) {
      throw new ApiError(404, '用户进度不存在');
    }
    
    // 查找任务进度
    const questProgressIndex = userProgress.quests.findIndex(
      q => q.questId.toString() === questId
    );
    
    if (questProgressIndex === -1) {
      throw new ApiError(404, '用户未接受此任务');
    }
    
    const questProgress = userProgress.quests[questProgressIndex];
    
    if (questProgress.status !== 'in_progress') {
      throw new ApiError(400, `任务当前状态为 ${questProgress.status}，无法更新步骤`);
    }
    
    // 查找步骤进度
    const stepProgressIndex = questProgress.steps.findIndex(
      s => s.stepIndex === stepIndex
    );
    
    if (stepProgressIndex === -1) {
      throw new ApiError(404, '步骤进度不存在');
    }
    
    // 更新步骤数据和完成状态
    const now = new Date();
    const step = questProgress.steps[stepProgressIndex];
    step.completed = true;
    step.data = data;
    step.completedAt = now;
    
    // 检查所有步骤是否完成
    const allStepsCompleted = questProgress.steps.every(s => s.completed);
    
    // 如果所有步骤都完成，更新任务状态为完成
    if (allStepsCompleted) {
      questProgress.status = 'completed';
      questProgress.completedAt = now;
      
      // 添加奖励
      userProgress.experience += quest.reward.experience;
      userProgress.points += quest.reward.points;
      
      // 更新等级
      const newLevel = calculateLevel(userProgress.experience);
      if (newLevel > userProgress.level) {
        userProgress.level = newLevel;
      }
    }
    
    userProgress.lastPlayedAt = now;
    userProgress.updatedAt = now;
    
    await userProgress.save();
    
    return {
      step: questProgress.steps[stepProgressIndex],
      questStatus: questProgress.status,
      isCompleted: questProgress.status === 'completed'
    };
  } catch (error) {
    logger.error(`更新任务步骤错误 [任务ID: ${questId}, 步骤: ${stepIndex}, 用户ID: ${userId}]:`, error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '更新任务步骤失败');
  }
};

/**
 * 完成任务
 */
export const completeQuest = async (questId: string, userId: string) => {
  try {
    // 查找用户进度
    const userProgress = await GameUserProgressModel.findOne({ userId });
    
    if (!userProgress) {
      throw new ApiError(404, '用户进度不存在');
    }
    
    // 查找任务进度
    const questProgressIndex = userProgress.quests.findIndex(
      q => q.questId.toString() === questId
    );
    
    if (questProgressIndex === -1) {
      throw new ApiError(404, '用户未接受此任务');
    }
    
    const questProgress = userProgress.quests[questProgressIndex];
    
    // 检查所有步骤是否完成
    const allStepsCompleted = questProgress.steps.every(s => s.completed);
    
    if (!allStepsCompleted) {
      throw new ApiError(400, '任务尚未完成所有步骤');
    }
    
    if (questProgress.status === 'completed') {
      throw new ApiError(400, '任务已完成');
    }
    
    // 更新任务状态为完成
    const now = new Date();
    questProgress.status = 'completed';
    questProgress.completedAt = now;
    
    // 获取任务信息以应用奖励
    const quest = await GameQuestModel.findById(questId);
    
    if (!quest) {
      throw new ApiError(404, '任务不存在');
    }
    
    // 添加奖励
    userProgress.experience += quest.reward.experience;
    userProgress.points += quest.reward.points;
    
    // 更新等级
    const newLevel = calculateLevel(userProgress.experience);
    if (newLevel > userProgress.level) {
      userProgress.level = newLevel;
    }
    
    userProgress.lastPlayedAt = now;
    userProgress.updatedAt = now;
    
    await userProgress.save();
    
    return {
      status: 'completed',
      rewards: {
        experience: quest.reward.experience,
        points: quest.reward.points,
        level: userProgress.level,
        levelUp: newLevel > userProgress.level
      }
    };
  } catch (error) {
    logger.error(`完成任务错误 [任务ID: ${questId}, 用户ID: ${userId}]:`, error);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, '完成任务失败');
  }
};

/**
 * 获取用户进度
 */
export const getUserProgress = async (userId: string) => {
  try {
    const userProgress = await GameUserProgressModel.findOne({ userId }).lean();
    
    if (!userProgress) {
      // 返回默认进度
      return {
        level: 1,
        experience: 0,
        points: 0,
        questsCount: {
          total: 0,
          completed: 0,
          inProgress: 0
        }
      };
    }
    
    // 计算任务统计
    const questsCount = {
      total: userProgress.quests.length,
      completed: userProgress.quests.filter(q => q.status === 'completed').length,
      inProgress: userProgress.quests.filter(q => q.status === 'in_progress').length
    };
    
    return {
      level: userProgress.level,
      experience: userProgress.experience,
      points: userProgress.points,
      questsCount,
      lastPlayedAt: userProgress.lastPlayedAt
    };
  } catch (error) {
    logger.error(`获取用户进度错误 [用户ID: ${userId}]:`, error);
    throw new ApiError(500, '获取用户进度失败');
  }
};

/**
 * 根据经验值计算等级
 * 使用简单的对数增长公式: level = 1 + log(experience/100 + 1) / log(1.5)
 */
function calculateLevel(experience: number): number {
  if (experience <= 0) return 1;
  const level = 1 + Math.floor(Math.log(experience / 100 + 1) / Math.log(1.5));
  return level;
} 
/**
 * 老克游戏NPC服务
 * 负责游戏中NPC角色的交互、对话和任务系统
 */
import { logger } from '../utils/logger';

// NPC任务状态
enum TaskStatus {
  AVAILABLE = 'available',   // 可接取
  ACCEPTED = 'accepted',     // 已接取
  COMPLETED = 'completed',   // 已完成
  FAILED = 'failed',         // 已失败
  EXPIRED = 'expired'        // 已过期
}

// NPC对话选项
interface DialogOption {
  id: string;              // 选项ID
  text: string;            // 选项文本
  nextDialogId?: string;   // 下一对话ID
  condition?: {            // 显示条件
    type: 'task' | 'item' | 'level' | 'reputation';
    value: string;
    operation: '=' | '>' | '<' | '>=' | '<=' | '!=';
    target: any;
  };
  action?: {               // 选择后触发动作
    type: 'giveTask' | 'completeTask' | 'giveItem' | 'takeItem' | 'giveExperience' | 'teleport';
    value: string;
    amount?: number;
  };
}

// NPC对话
interface Dialog {
  id: string;              // 对话ID
  text: string;            // 对话文本
  options: DialogOption[]; // 对话选项
  animation?: string;      // 对话时的动画
  audio?: string;          // 对话语音
}

// NPC任务
interface NPCTask {
  id: string;              // 任务ID
  title: string;           // 任务标题
  description: string;     // 任务描述
  type: 'collect' | 'visit' | 'defeat' | 'escort' | 'craft' | 'quiz'; // 任务类型
  objective: {             // 任务目标
    type: string;
    target: string;
    amount: number;
    current: number;
  };
  rewards: {               // 任务奖励
    experience?: number;   // 经验值
    items?: Array<{ id: string; amount: number }>; // 物品奖励
    currency?: number;     // 货币奖励
    reputation?: number;   // 声望奖励
  };
  prerequisite?: {         // 任务前置条件
    tasks?: string[];      // 需要完成的任务
    level?: number;        // 需要达到的等级
    reputation?: number;   // 需要达到的声望
  };
  timeLimit?: number;      // 时间限制(分钟)
  status: TaskStatus;      // 任务状态
  assignedTo?: string;     // 分配给的玩家ID
  assignedAt?: Date;       // 分配时间
  completedAt?: Date;      // 完成时间
}

// NPC行为动画
interface NPCAnimation {
  id: string;              // 动画ID
  name: string;            // 动画名称
  frames: string[];        // 动画帧
  duration: number;        // 动画持续时间
}

// NPC路径点
interface PathPoint {
  x: number;               // X坐标
  y: number;               // Y坐标
  z: number;               // Z坐标
  waitTime?: number;       // 等待时间(秒)
  animation?: string;      // 在该点执行的动画
  dialog?: string;         // 在该点触发的对话
}

// NPC定义
interface NPCDefinition {
  id: string;              // NPC ID
  name: string;            // NPC 名称
  description: string;     // NPC 描述
  role: string;            // NPC 角色
  appearance: {            // NPC 外观
    model: string;         // 模型
    scale: number;         // 缩放
    color?: string;        // 颜色
    accessories?: string[]; // 配饰
  };
  animations: NPCAnimation[]; // NPC 动画列表
  dialogs: Dialog[];       // NPC 对话列表
  initialDialog: string;   // 初始对话ID
  tasks: NPCTask[];        // NPC 任务列表
  patrolPath?: PathPoint[]; // NPC 巡逻路径
  schedule?: {             // NPC 日程安排
    [key: string]: {       // 时间段
      location: PathPoint;
      activity: string;
      animation?: string;
      dialog?: string;
    };
  };
}

class GameNPCService {
  // 老克NPC定义
  private laoke: NPCDefinition;
  // 用户任务状态记录 Map<用户ID, Map<任务ID, 任务状态>>
  private userTasksMap: Map<string, Map<string, NPCTask>> = new Map();
  // 用户对话状态记录 Map<用户ID, 当前对话ID>
  private userDialogMap: Map<string, string> = new Map();
  
  constructor() {
    logger.info('游戏NPC服务初始化');
    
    // 初始化老克NPC
    this.laoke = this.initLaoKeNPC();
  }
  
  /**
   * 初始化老克NPC
   * @returns 老克NPC定义
   */
  private initLaoKeNPC(): NPCDefinition {
    return {
      id: 'laoke',
      name: '老克',
      description: '索克生活APP探索频道版主，负责知识传播、知识培训、用户博客管理工作',
      role: '探索频道版主',
      appearance: {
        model: 'laoke_model_01',
        scale: 1.0,
        accessories: ['glasses', 'notebook']
      },
      animations: [
        {
          id: 'idle',
          name: '待机',
          frames: ['laoke_idle_01', 'laoke_idle_02', 'laoke_idle_03'],
          duration: 3.0
        },
        {
          id: 'talk',
          name: '对话',
          frames: ['laoke_talk_01', 'laoke_talk_02', 'laoke_talk_03'],
          duration: 2.0
        },
        {
          id: 'think',
          name: '思考',
          frames: ['laoke_think_01', 'laoke_think_02', 'laoke_think_03'],
          duration: 4.0
        },
        {
          id: 'walk',
          name: '行走',
          frames: ['laoke_walk_01', 'laoke_walk_02', 'laoke_walk_03', 'laoke_walk_04'],
          duration: 1.0
        },
        {
          id: 'write',
          name: '书写',
          frames: ['laoke_write_01', 'laoke_write_02', 'laoke_write_03'],
          duration: 2.5
        }
      ],
      dialogs: [
        {
          id: 'greeting',
          text: '你好啊，游客。我是老克，负责索克生活APP探索频道，主要任务是传播知识和培训。有什么我能帮助你的吗？',
          options: [
            {
              id: 'learn_about_city',
              text: '我想了解更多关于索克城的知识',
              nextDialogId: 'about_city'
            },
            {
              id: 'learn_about_tcm',
              text: '我对中医知识感兴趣',
              nextDialogId: 'about_tcm'
            },
            {
              id: 'start_task',
              text: '我想接受一个任务',
              nextDialogId: 'task_selection'
            },
            {
              id: 'goodbye',
              text: '再见',
              nextDialogId: 'farewell'
            }
          ],
          animation: 'talk'
        },
        {
          id: 'about_city',
          text: '索克城是一个充满智慧和创新的虚拟空间，由AI代理自主运营管理。这里融合了传统文化与现代科技，为居民提供健康、快乐的生活环境。',
          options: [
            {
              id: 'city_districts',
              text: '索克城有哪些区域？',
              nextDialogId: 'city_districts'
            },
            {
              id: 'city_activities',
              text: '这里有什么活动？',
              nextDialogId: 'city_activities'
            },
            {
              id: 'back_to_main',
              text: '我想问点别的',
              nextDialogId: 'greeting'
            }
          ],
          animation: 'talk'
        },
        {
          id: 'city_districts',
          text: '索克城主要分为五个区域：知识园区、健康谷、农耕园、游乐场和冥想湖。每个区域都有特色功能和服务。',
          options: [
            {
              id: 'knowledge_park',
              text: '请告诉我更多关于知识园区的信息',
              nextDialogId: 'knowledge_park'
            },
            {
              id: 'back_to_city',
              text: '返回上一级',
              nextDialogId: 'about_city'
            },
            {
              id: 'back_to_main',
              text: '我想问点别的',
              nextDialogId: 'greeting'
            }
          ],
          animation: 'talk'
        },
        {
          id: 'knowledge_park',
          text: '知识园区是索克城的文化中心，这里有图书馆、博物馆和学习中心。我就在这里工作，负责传播各种知识和组织培训活动。',
          options: [
            {
              id: 'take_tour',
              text: '我想参观知识园区',
              nextDialogId: 'knowledge_park_tour',
              action: {
                type: 'giveTask',
                value: 'tour_knowledge_park'
              }
            },
            {
              id: 'back_to_districts',
              text: '返回上一级',
              nextDialogId: 'city_districts'
            },
            {
              id: 'back_to_main',
              text: '我想问点别的',
              nextDialogId: 'greeting'
            }
          ],
          animation: 'talk'
        },
        {
          id: 'knowledge_park_tour',
          text: '太好了！我已经为你创建了一个参观任务。完成后别忘了来找我领取奖励。祝你游览愉快！',
          options: [
            {
              id: 'task_details',
              text: '查看任务详情',
              nextDialogId: 'tour_task_details'
            },
            {
              id: 'back_to_main',
              text: '我稍后再来',
              nextDialogId: 'greeting'
            }
          ],
          animation: 'talk'
        },
        {
          id: 'about_tcm',
          text: '中医是中国传统医学的简称，有着几千年的历史。它基于阴阳五行理论，通过四诊(望闻问切)来判断健康状况，并使用草药、针灸等方法调理健康。',
          options: [
            {
              id: 'learn_constitution',
              text: '什么是中医体质？',
              nextDialogId: 'tcm_constitution'
            },
            {
              id: 'learn_herbs',
              text: '我想了解中药',
              nextDialogId: 'tcm_herbs'
            },
            {
              id: 'tcm_quiz',
              text: '参加中医知识小测验',
              nextDialogId: 'tcm_quiz_intro',
              action: {
                type: 'giveTask',
                value: 'tcm_knowledge_quiz'
              }
            },
            {
              id: 'back_to_main',
              text: '我想问点别的',
              nextDialogId: 'greeting'
            }
          ],
          animation: 'talk'
        },
        {
          id: 'tcm_constitution',
          text: '中医体质理论认为每个人都有独特的体质类型，主要分为九种：平和质、气虚质、阳虚质、阴虚质、痰湿质、湿热质、血瘀质、气郁质和特禀质。',
          options: [
            {
              id: 'constitution_test',
              text: '我想做体质测试',
              nextDialogId: 'constitution_test_intro',
              action: {
                type: 'giveTask',
                value: 'constitution_test'
              }
            },
            {
              id: 'back_to_tcm',
              text: '返回上一级',
              nextDialogId: 'about_tcm'
            },
            {
              id: 'back_to_main',
              text: '我想问点别的',
              nextDialogId: 'greeting'
            }
          ],
          animation: 'talk'
        },
        {
          id: 'task_selection',
          text: '我这里有几个任务可以提供给你，完成后会有相应奖励。你想尝试哪一个？',
          options: [
            {
              id: 'knowledge_task',
              text: '知识收集任务',
              nextDialogId: 'knowledge_collection_task',
              action: {
                type: 'giveTask',
                value: 'knowledge_collection'
              }
            },
            {
              id: 'blog_task',
              text: '撰写博客任务',
              nextDialogId: 'blog_writing_task',
              action: {
                type: 'giveTask',
                value: 'blog_writing'
              }
            },
            {
              id: 'guide_task',
              text: '新手引导任务',
              nextDialogId: 'newbie_guide_task',
              action: {
                type: 'giveTask',
                value: 'newbie_guide'
              }
            },
            {
              id: 'back_to_main',
              text: '我再想想',
              nextDialogId: 'greeting'
            }
          ],
          animation: 'think'
        },
        {
          id: 'farewell',
          text: '再见！如果你有任何问题，随时欢迎回来找我。祝你在索克城玩得愉快！',
          options: [
            {
              id: 'restart',
              text: '重新开始对话',
              nextDialogId: 'greeting'
            }
          ],
          animation: 'talk'
        }
      ],
      initialDialog: 'greeting',
      tasks: [
        {
          id: 'tour_knowledge_park',
          title: '知识园区参观之旅',
          description: '参观索克城知识园区的主要景点，了解这里的文化和知识资源。',
          type: 'visit',
          objective: {
            type: 'locations',
            target: 'knowledge_park',
            amount: 5,
            current: 0
          },
          rewards: {
            experience: 100,
            items: [
              { id: 'knowledge_token', amount: 5 },
              { id: 'park_map', amount: 1 }
            ]
          },
          status: TaskStatus.AVAILABLE
        },
        {
          id: 'tcm_knowledge_quiz',
          title: '中医知识小测验',
          description: '回答与中医相关的问题，测试你对中医基础知识的了解程度。',
          type: 'quiz',
          objective: {
            type: 'questions',
            target: 'tcm_quiz',
            amount: 10,
            current: 0
          },
          rewards: {
            experience: 150,
            items: [
              { id: 'tcm_handbook', amount: 1 },
              { id: 'knowledge_token', amount: 10 }
            ]
          },
          status: TaskStatus.AVAILABLE
        },
        {
          id: 'constitution_test',
          title: '中医体质测试',
          description: '完成中医体质测试问卷，了解自己的体质类型。',
          type: 'quiz',
          objective: {
            type: 'questions',
            target: 'constitution_quiz',
            amount: 20,
            current: 0
          },
          rewards: {
            experience: 200,
            items: [
              { id: 'constitution_report', amount: 1 },
              { id: 'health_token', amount: 15 }
            ]
          },
          status: TaskStatus.AVAILABLE
        },
        {
          id: 'knowledge_collection',
          title: '知识收集任务',
          description: '在知识园区收集特定的知识碎片，帮助完善索克城的知识库。',
          type: 'collect',
          objective: {
            type: 'items',
            target: 'knowledge_fragment',
            amount: 10,
            current: 0
          },
          rewards: {
            experience: 120,
            currency: 50,
            reputation: 5
          },
          status: TaskStatus.AVAILABLE
        },
        {
          id: 'blog_writing',
          title: '撰写博客任务',
          description: '撰写一篇关于索克城或健康养生的博客文章，分享你的见解和体验。',
          type: 'craft',
          objective: {
            type: 'blog',
            target: 'create_blog',
            amount: 1,
            current: 0
          },
          rewards: {
            experience: 250,
            currency: 100,
            reputation: 15,
            items: [
              { id: 'blogger_badge', amount: 1 }
            ]
          },
          prerequisite: {
            level: 5
          },
          status: TaskStatus.AVAILABLE
        },
        {
          id: 'newbie_guide',
          title: '新手引导任务',
          description: '完成索克城的新手引导，熟悉主要功能和服务。',
          type: 'collect',
          objective: {
            type: 'checkpoints',
            target: 'guide_checkpoints',
            amount: 7,
            current: 0
          },
          rewards: {
            experience: 200,
            items: [
              { id: 'welcome_pack', amount: 1 },
              { id: 'newbie_hat', amount: 1 }
            ]
          },
          status: TaskStatus.AVAILABLE
        }
      ],
      patrolPath: [
        { x: 100, y: 0, z: 100, waitTime: 10, animation: 'think' },
        { x: 120, y: 0, z: 100, waitTime: 5 },
        { x: 120, y: 0, z: 120, waitTime: 15, animation: 'write' },
        { x: 100, y: 0, z: 120, waitTime: 5 },
        { x: 100, y: 0, z: 100, waitTime: 10, dialog: 'greeting' }
      ],
      schedule: {
        '08:00-10:00': {
          location: { x: 105, y: 0, z: 105 },
          activity: '晨间阅读',
          animation: 'think'
        },
        '10:00-12:00': {
          location: { x: 120, y: 0, z: 120 },
          activity: '教学授课',
          animation: 'talk'
        },
        '12:00-14:00': {
          location: { x: 110, y: 0, z: 110 },
          activity: '午休',
          animation: 'idle'
        },
        '14:00-18:00': {
          location: { x: 115, y: 0, z: 115 },
          activity: '任务管理',
          animation: 'write'
        },
        '18:00-20:00': {
          location: { x: 100, y: 0, z: 100 },
          activity: '巡逻',
          animation: 'walk'
        }
      }
    };
  }
  
  /**
   * 获取NPC定义
   * @returns NPC定义
   */
  public getNPCDefinition(): NPCDefinition {
    return this.laoke;
  }
  
  /**
   * 开始对话
   * @param userId 用户ID
   * @returns 初始对话内容
   */
  public startDialog(userId: string): Dialog {
    const dialogId = this.laoke.initialDialog;
    
    // 保存用户当前对话状态
    this.userDialogMap.set(userId, dialogId);
    
    logger.info(`用户 ${userId} 开始对话`, { dialogId });
    
    const dialog = this.getDialogById(dialogId);
    if (!dialog) {
      throw new Error(`对话不存在: ${dialogId}`);
    }
    
    return dialog;
  }
  
  /**
   * 用户选择对话选项
   * @param userId 用户ID
   * @param optionId 选项ID
   * @returns 新的对话内容或null
   */
  public chooseOption(userId: string, optionId: string): Dialog | null {
    // 获取用户当前对话
    const currentDialogId = this.userDialogMap.get(userId);
    if (!currentDialogId) {
      logger.warn(`用户 ${userId} 没有进行中的对话`);
      return null;
    }
    
    const currentDialog = this.getDialogById(currentDialogId);
    if (!currentDialog) {
      logger.warn(`对话不存在: ${currentDialogId}`);
      return null;
    }
    
    // 查找选项
    const option = currentDialog.options.find(opt => opt.id === optionId);
    if (!option) {
      logger.warn(`选项不存在: ${optionId}`, {
        userId,
        dialogId: currentDialogId
      });
      return null;
    }
    
    logger.info(`用户 ${userId} 选择选项: ${optionId}`, {
      dialogId: currentDialogId,
      nextDialogId: option.nextDialogId
    });
    
    // 处理选项动作
    if (option.action) {
      this.processOptionAction(userId, option.action);
    }
    
    // 转到下一个对话
    if (option.nextDialogId) {
      const nextDialog = this.getDialogById(option.nextDialogId);
      if (!nextDialog) {
        logger.warn(`下一对话不存在: ${option.nextDialogId}`);
        return null;
      }
      
      // 更新用户当前对话
      this.userDialogMap.set(userId, option.nextDialogId);
      
      return nextDialog;
    }
    
    return null;
  }
  
  /**
   * 分配任务给用户
   * @param userId 用户ID
   * @param taskId 任务ID
   * @returns 任务详情或null
   */
  public assignTask(userId: string, taskId: string): NPCTask | null {
    // 查找任务
    const taskTemplate = this.laoke.tasks.find(task => task.id === taskId);
    if (!taskTemplate) {
      logger.warn(`任务不存在: ${taskId}`);
      return null;
    }
    
    // 检查用户任务状态
    if (!this.userTasksMap.has(userId)) {
      this.userTasksMap.set(userId, new Map());
    }
    
    const userTasks = this.userTasksMap.get(userId)!;
    
    // 检查用户是否已有此任务
    if (userTasks.has(taskId)) {
      const existingTask = userTasks.get(taskId)!;
      
      // 如果任务已失败或过期，可以重新接取
      if (
        existingTask.status === TaskStatus.FAILED ||
        existingTask.status === TaskStatus.EXPIRED
      ) {
        logger.info(`用户 ${userId} 重新接取任务: ${taskId}`);
      } else {
        logger.warn(`用户 ${userId} 已有任务: ${taskId}`, {
          status: existingTask.status
        });
        return existingTask;
      }
    }
    
    // 克隆任务模板
    const newTask: NPCTask = JSON.parse(JSON.stringify(taskTemplate));
    newTask.status = TaskStatus.ACCEPTED;
    newTask.assignedTo = userId;
    newTask.assignedAt = new Date();
    
    // 如果有时间限制，计算过期时间
    if (newTask.timeLimit) {
      const expiryDate = new Date();
      expiryDate.setMinutes(expiryDate.getMinutes() + newTask.timeLimit);
      // 可以在这里保存过期时间，例如 newTask.expiryDate = expiryDate;
    }
    
    // 保存任务状态
    userTasks.set(taskId, newTask);
    
    logger.info(`分配任务给用户 ${userId}: ${taskId}`, {
      taskTitle: newTask.title,
      assignedAt: newTask.assignedAt
    });
    
    return newTask;
  }
  
  /**
   * 更新任务进度
   * @param userId 用户ID
   * @param taskId 任务ID
   * @param progress 进度值
   * @returns 更新后的任务或null
   */
  public updateTaskProgress(
    userId: string,
    taskId: string,
    progress: number
  ): NPCTask | null {
    // 检查用户任务状态
    if (!this.userTasksMap.has(userId)) {
      logger.warn(`用户 ${userId} 没有任务记录`);
      return null;
    }
    
    const userTasks = this.userTasksMap.get(userId)!;
    
    // 检查用户是否已有此任务
    if (!userTasks.has(taskId)) {
      logger.warn(`用户 ${userId} 没有任务: ${taskId}`);
      return null;
    }
    
    const task = userTasks.get(taskId)!;
    
    // 检查任务状态
    if (task.status !== TaskStatus.ACCEPTED) {
      logger.warn(`任务 ${taskId} 状态不为进行中`, {
        userId,
        status: task.status
      });
      return task;
    }
    
    // 更新任务进度
    const oldProgress = task.objective.current;
    task.objective.current = Math.min(progress, task.objective.amount);
    
    logger.info(`更新任务进度: ${taskId}`, {
      userId,
      oldProgress,
      newProgress: task.objective.current
    });
    
    // 检查任务是否完成
    if (task.objective.current >= task.objective.amount) {
      task.status = TaskStatus.COMPLETED;
      task.completedAt = new Date();
      
      logger.info(`任务完成: ${taskId}`, {
        userId,
        completedAt: task.completedAt
      });
    }
    
    // 保存更新后的任务
    userTasks.set(taskId, task);
    
    return task;
  }
  
  /**
   * 完成任务
   * @param userId 用户ID
   * @param taskId 任务ID
   * @returns 任务奖励或null
   */
  public completeTask(
    userId: string,
    taskId: string
  ): NPCTask['rewards'] | null {
    // 检查用户任务状态
    if (!this.userTasksMap.has(userId)) {
      logger.warn(`用户 ${userId} 没有任务记录`);
      return null;
    }
    
    const userTasks = this.userTasksMap.get(userId)!;
    
    // 检查用户是否已有此任务
    if (!userTasks.has(taskId)) {
      logger.warn(`用户 ${userId} 没有任务: ${taskId}`);
      return null;
    }
    
    const task = userTasks.get(taskId)!;
    
    // 检查任务状态
    if (task.status !== TaskStatus.COMPLETED) {
      logger.warn(`任务 ${taskId} 未完成`, {
        userId,
        status: task.status
      });
      return null;
    }
    
    logger.info(`发放任务奖励: ${taskId}`, {
      userId,
      rewards: task.rewards
    });
    
    return task.rewards;
  }
  
  /**
   * 获取用户所有任务
   * @param userId 用户ID
   * @param status 任务状态过滤
   * @returns 任务列表
   */
  public getUserTasks(
    userId: string,
    status?: TaskStatus[]
  ): NPCTask[] {
    // 检查用户任务状态
    if (!this.userTasksMap.has(userId)) {
      return [];
    }
    
    const userTasks = Array.from(this.userTasksMap.get(userId)!.values());
    
    // 按状态过滤
    if (status && status.length > 0) {
      return userTasks.filter(task => 
        status.includes(task.status)
      );
    }
    
    return userTasks;
  }
  
  /**
   * 获取可用任务列表
   * @returns 可用任务列表
   */
  public getAvailableTasks(): NPCTask[] {
    return this.laoke.tasks.filter(task => 
      task.status === TaskStatus.AVAILABLE
    );
  }
  
  /**
   * 根据ID获取对话
   * @param dialogId 对话ID
   * @returns 对话或null
   */
  private getDialogById(dialogId: string): Dialog | null {
    const dialog = this.laoke.dialogs.find(d => d.id === dialogId);
    return dialog || null;
  }
  
  /**
   * 处理对话选项动作
   * @param userId 用户ID
   * @param action 动作
   */
  private processOptionAction(
    userId: string,
    action: DialogOption['action']
  ): void {
    if (!action) return;
    
    logger.info(`处理对话选项动作`, {
      userId,
      actionType: action.type,
      actionValue: action.value
    });
    
    switch (action.type) {
      case 'giveTask':
        this.assignTask(userId, action.value);
        break;
      
      case 'completeTask':
        this.completeTask(userId, action.value);
        break;
      
      case 'giveItem':
        // 这里应该实现给予物品的逻辑
        logger.info(`为用户 ${userId} 添加物品: ${action.value}`, {
          amount: action.amount || 1
        });
        break;
      
      case 'takeItem':
        // 这里应该实现收取物品的逻辑
        logger.info(`从用户 ${userId} 收取物品: ${action.value}`, {
          amount: action.amount || 1
        });
        break;
      
      case 'giveExperience':
        // 这里应该实现给予经验的逻辑
        logger.info(`为用户 ${userId} 添加经验: ${action.amount || 0}`);
        break;
      
      case 'teleport':
        // 这里应该实现传送的逻辑
        logger.info(`将用户 ${userId} 传送到: ${action.value}`);
        break;
      
      default:
        logger.warn(`未知动作类型: ${action.type}`);
        break;
    }
  }
}

export default new GameNPCService();
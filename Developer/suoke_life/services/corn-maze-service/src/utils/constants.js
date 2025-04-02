/**
 * 系统常量定义
 */

// 玉米生长阶段
const CORN_GROWTH_STAGES = {
  SEED: 1,         // 种子阶段
  SEEDLING: 2,     // 幼苗阶段
  VEGETATIVE: 3,   // 营养生长阶段
  FLOWERING: 4,    // 开花阶段
  MATURITY: 5      // 成熟阶段
};

// 奖励类型
const REWARD_TYPES = {
  COIN: 'coin',           // 金币
  ITEM: 'item',           // 道具
  EXPERIENCE: 'exp',      // 经验值
  PLANT_BOOST: 'boost',   // 植物成长加速
  ACHIEVEMENT: 'achieve', // 成就
  RARE_SEED: 'seed',      // 稀有种子
  KNOWLEDGE: 'knowledge', // 知识卡片
  REAL_PRODUCT: 'product' // 实物商品
};

// 奖励稀有度
const REWARD_RARITY = {
  COMMON: 1,      // 普通
  UNCOMMON: 2,    // 少见
  RARE: 3,        // 稀有
  VERY_RARE: 4,   // 非常稀有
  LEGENDARY: 5    // 传说
};

// 迷宫难度
const MAZE_DIFFICULTY = {
  EASY: 'easy',           // 简单
  MEDIUM: 'medium',       // 中等
  HARD: 'hard',           // 困难
  EXPERT: 'expert'        // 专家
};

// 迷宫尺寸
const MAZE_SIZE = {
  SMALL: 'small',         // 小型 (10x10)
  MEDIUM: 'medium',       // 中型 (20x20)
  LARGE: 'large',         // 大型 (30x30)
  HUGE: 'huge'            // 超大型 (50x50)
};

// AR标记类型
const AR_MARKER_TYPES = {
  TREASURE: 'treasure',   // 宝藏
  PLANT: 'plant',         // 植物
  INFO: 'info',           // 信息点
  PORTAL: 'portal',       // 传送门
  PUZZLE: 'puzzle',       // 解谜
  CHARACTER: 'character'  // 角色
};

// 团队规模
const TEAM_SIZES = {
  SMALL: 2,        // 小队(2人)
  MEDIUM: 3,       // 中队(3人)
  LARGE: 5         // 大队(5人)
};

// 系统角色
const USER_ROLES = {
  PLAYER: 'player',            // 普通玩家
  TEAM_LEADER: 'team_leader',  // 队长
  ADMIN: 'admin'               // 管理员
};

// 活动阶段
const GAME_PHASES = {
  PLANTING: 'planting',        // 种植阶段
  GROWING: 'growing',          // 生长阶段
  MAZE: 'maze',                // 迷宫阶段
  HARVEST: 'harvest'           // 收获阶段
};

// 植物生长阶段
const PLANT_GROWTH_STAGES = {
  SEED: 'seed',           // 种子
  SPROUT: 'sprout',       // 幼苗
  GROWING: 'growing',     // 生长期
  MATURE: 'mature',       // 成熟期
  FLOWERING: 'flowering', // 开花期
  HARVESTING: 'harvest'   // 收获期
};

// 植物健康状态
const PLANT_HEALTH_STATUS = {
  EXCELLENT: 'excellent', // 状态极佳
  GOOD: 'good',           // 状态良好
  NORMAL: 'normal',       // 状态正常
  POOR: 'poor',           // 状态不佳
  CRITICAL: 'critical'    // 危急状态
};

// 团队角色
const TEAM_ROLES = {
  LEADER: 'leader',       // 队长
  MEMBER: 'member',       // 成员
  INVITED: 'invited'      // 已邀请
};

// 新增常量：AR交互类型
const AR_INTERACTION_TYPES = {
  SIMPLE: 'simple',       // 简单点击
  GESTURE: 'gesture',     // 手势识别
  PUZZLE: 'puzzle',       // 解谜类
  AR_ANIMATION: 'ar_animation' // AR动画
};

// 新增常量：手势类型
const GESTURE_TYPES = {
  TAP: 'tap',             // 点击
  DOUBLE_TAP: 'double_tap', // 双击
  LONG_PRESS: 'long_press', // 长按
  SWIPE_UP: 'swipe_up',   // 向上滑动
  SWIPE_DOWN: 'swipe_down', // 向下滑动
  SWIPE_LEFT: 'swipe_left', // 向左滑动
  SWIPE_RIGHT: 'swipe_right', // 向右滑动
  ROTATE: 'rotate',       // 旋转
  PINCH: 'pinch',         // 捏合
  SPREAD: 'spread',       // 展开
  SHAKE: 'shake',         // 摇晃
  WAVE: 'wave'            // 挥手
};

// 新增常量：图像识别类型
const IMAGE_RECOGNITION_TYPES = {
  MARKER: 'marker',       // 标记识别
  OBJECT: 'object',       // 物体识别
  SCENE: 'scene',         // 场景识别
  FACE: 'face',           // 人脸识别
  TEXT: 'text',           // 文字识别
  LANDMARK: 'landmark'    // 地标识别
};

// 新增常量：位置精度
const LOCATION_ACCURACY = {
  LOW: 'low',             // 低精度 (>100m)
  MEDIUM: 'medium',       // 中等精度 (10-100m)
  HIGH: 'high',           // 高精度 (2-10m)
  VERY_HIGH: 'very_high'  // 极高精度 (<2m)
};

// 新增常量：社交互动类型
const SOCIAL_INTERACTION_TYPES = {
  SHARE: 'share',         // 分享
  GIFT: 'gift',           // 赠送
  INVITE: 'invite',       // 邀请
  COLLABORATE: 'collaborate', // 协作
  COMPETE: 'compete',     // 竞争
  MESSAGE: 'message'      // 留言
};

module.exports = {
  CORN_GROWTH_STAGES,
  REWARD_TYPES,
  REWARD_RARITY,
  MAZE_DIFFICULTY,
  MAZE_SIZE,
  AR_MARKER_TYPES,
  TEAM_SIZES,
  USER_ROLES,
  GAME_PHASES,
  PLANT_GROWTH_STAGES,
  PLANT_HEALTH_STATUS,
  TEAM_ROLES,
  AR_INTERACTION_TYPES,
  GESTURE_TYPES,
  IMAGE_RECOGNITION_TYPES,
  LOCATION_ACCURACY,
  SOCIAL_INTERACTION_TYPES
};

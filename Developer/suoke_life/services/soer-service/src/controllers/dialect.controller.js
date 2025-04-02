/**
 * 索儿服务 - 方言控制器
 * 
 * 专为儿童用户设计的方言学习和互动功能
 */

const dialectService = require('../services/dialect.service');
const logger = require('../utils/logger');
const { incrementApiCalls, recordProcessingTime } = require('../metrics');

/**
 * 获取适合儿童的方言列表
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getChildFriendlyDialects = async (req, res) => {
  try {
    const result = await dialectService.getChildFriendlyDialects();
    
    // 记录指标
    incrementApiCalls('get_child_friendly_dialects');
    
    return res.json(result);
  } catch (error) {
    logger.error(`获取儿童友好方言列表失败: ${error.message}`);
    return res.status(500).json({
      success: false,
      error: '获取方言列表失败，请稍后再试',
      friendlyMessage: '哎呀，方言列表暂时找不到了，请稍后再试哦'
    });
  }
};

/**
 * 儿童版方言检测
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const detectDialectForChildren = async (req, res) => {
  try {
    // 获取上传的音频文件
    const audioFile = req.file;
    
    if (!audioFile) {
      return res.status(400).json({
        success: false,
        error: '没有收到声音哦，请再试一次',
        friendlyMessage: '小朋友，我没有听到你的声音，请再说一次好吗？'
      });
    }
    
    // 开始计时
    const startTime = Date.now();
    
    // 将文件内容转为Buffer
    const audioBuffer = audioFile.buffer;
    
    // 执行方言检测
    const result = await dialectService.detectDialectForChildren(audioBuffer);
    
    // 记录指标
    const processingTime = Date.now() - startTime;
    recordProcessingTime('dialect_detection_children', processingTime);
    incrementApiCalls('detect_dialect_children');
    
    return res.json(result);
  } catch (error) {
    logger.error(`儿童方言检测失败: ${error.message}`);
    return res.status(500).json({
      success: false,
      error: '听不清楚呢，我们再试一次好吗？',
      friendlyMessage: '小朋友，我听不清楚你说的话，可以再说一次吗？'
    });
  }
};

/**
 * 获取方言学习游戏
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getDialectLearningGames = async (req, res) => {
  try {
    const { dialectCode, ageGroup } = req.params;
    
    if (!dialectCode) {
      return res.status(400).json({
        success: false,
        error: '请选择一种方言',
        friendlyMessage: '小朋友，请先选择一种方言再继续哦'
      });
    }
    
    const result = await dialectService.getDialectLearningGames(dialectCode, ageGroup);
    
    // 记录指标
    incrementApiCalls('get_dialect_learning_games');
    
    return res.json(result);
  } catch (error) {
    logger.error(`获取方言学习游戏失败: ${error.message}`);
    return res.status(500).json({
      success: false,
      error: '获取游戏失败',
      friendlyMessage: '哎呀，游戏暂时找不到了，请稍后再试哦'
    });
  }
};

/**
 * 创建儿童方言探险任务
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const createDialectAdventure = async (req, res) => {
  try {
    const { userId, dialectCodes } = req.body;
    
    if (!userId) {
      return res.status(400).json({
        success: false,
        error: '需要用户ID',
        friendlyMessage: '请先登录再开始探险哦'
      });
    }
    
    const result = await dialectService.createDialectAdventure(userId, dialectCodes);
    
    // 记录指标
    incrementApiCalls('create_dialect_adventure');
    
    return res.json(result);
  } catch (error) {
    logger.error(`创建方言探险任务失败: ${error.message}`);
    return res.status(500).json({
      success: false,
      error: '创建探险任务失败',
      friendlyMessage: '哎呀，探险地图暂时无法准备好，请稍后再试哦'
    });
  }
};

/**
 * 获取探险任务详情
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const getDialectAdventure = async (req, res) => {
  try {
    const { adventureId } = req.params;
    const { userId } = req.query;
    
    if (!adventureId || !userId) {
      return res.status(400).json({
        success: false,
        error: '缺少必要参数',
        friendlyMessage: '探险地图不见了，请重新开始探险'
      });
    }
    
    // 这里需要实现实际的方法
    // 暂时返回模拟数据
    
    // 记录指标
    incrementApiCalls('get_dialect_adventure');
    
    return res.json({
      success: true,
      adventure: {
        id: adventureId,
        userId,
        title: '中国方言大冒险',
        progress: {
          currentPosition: 2,
          treasuresFound: 1
        },
        // 更多探险信息...
      }
    });
  } catch (error) {
    logger.error(`获取方言探险任务失败: ${error.message}`);
    return res.status(500).json({
      success: false,
      error: '获取探险任务失败',
      friendlyMessage: '探险地图暂时看不清楚，请稍后再试哦'
    });
  }
};

/**
 * 更新探险任务进度
 * @param {Object} req 请求对象
 * @param {Object} res 响应对象
 */
const updateAdventureProgress = async (req, res) => {
  try {
    const { adventureId } = req.params;
    const { userId, progress, completedTasks, treasureFound } = req.body;
    
    if (!adventureId || !userId || !progress) {
      return res.status(400).json({
        success: false,
        error: '缺少必要参数',
        friendlyMessage: '无法更新探险进度，请重试'
      });
    }
    
    // 这里需要实现实际的方法
    // 暂时返回模拟数据
    
    // 记录指标
    incrementApiCalls('update_adventure_progress');
    
    return res.json({
      success: true,
      message: '探险进度已更新',
      friendlyMessage: treasureFound ? '恭喜你找到了宝藏！' : '你的探险进度已保存',
      updatedProgress: {
        currentPosition: progress.currentPosition,
        treasuresFound: treasureFound ? (progress.treasuresFound + 1) : progress.treasuresFound
      },
      rewards: treasureFound ? {
        points: 10,
        badge: '探险家徽章'
      } : null
    });
  } catch (error) {
    logger.error(`更新方言探险进度失败: ${error.message}`);
    return res.status(500).json({
      success: false,
      error: '更新探险进度失败',
      friendlyMessage: '哎呀，进度保存失败了，请再试一次哦'
    });
  }
};

module.exports = {
  getChildFriendlyDialects,
  detectDialectForChildren,
  getDialectLearningGames,
  createDialectAdventure,
  getDialectAdventure,
  updateAdventureProgress
};
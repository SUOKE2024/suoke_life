const MazeService = require('../services/mazeService');
const { handleError } = require('../utils/errorHandler');

/**
 * 迷宫控制器
 * 实现玉米迷宫的所有管理与交互功能
 */
class MazeController {
  /**
   * 创建新迷宫
   */
  async createMaze(req, res) {
    try {
      const { 
        name, 
        seasonId, 
        difficulty, 
        width, 
        height, 
        teamId,
        seed
      } = req.body;
      
      if (!name || !seasonId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数'
        });
      }
      
      const mazeService = new MazeService();
      const newMaze = await mazeService.createMaze({
        name,
        seasonId,
        difficulty: difficulty || 'medium',
        width: width || 20,
        height: height || 20,
        teamId,
        seed: seed || Math.floor(Math.random() * 1000000)
      });
      
      return res.status(201).json({
        success: true,
        data: newMaze,
        message: '迷宫创建成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取所有迷宫
   */
  async getAllMazes(req, res) {
    try {
      const filters = {};
      
      // 应用过滤条件
      if (req.query.seasonId) filters.seasonId = req.query.seasonId;
      if (req.query.teamId) filters.teamId = req.query.teamId;
      if (req.query.difficulty) filters.difficulty = req.query.difficulty;
      if (req.query.isActive !== undefined) filters.isActive = req.query.isActive === 'true';
      
      const mazeService = new MazeService();
      const mazes = await mazeService.getMazes(filters);
      
      return res.status(200).json({
        success: true,
        count: mazes.length,
        data: mazes
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取单个迷宫
   */
  async getMazeById(req, res) {
    try {
      const { id } = req.params;
      const mazeService = new MazeService();
      const maze = await mazeService.getMazeById(id);
      
      if (!maze) {
        return res.status(404).json({
          success: false,
          message: '未找到指定迷宫'
        });
      }
      
      return res.status(200).json({
        success: true,
        data: maze
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取迷宫结构
   */
  async getMazeStructure(req, res) {
    try {
      const { id } = req.params;
      const { userId, includeHidden = false } = req.query;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId'
        });
      }
      
      const mazeService = new MazeService();
      const result = await mazeService.getMazeStructure(id, userId, includeHidden === 'true');
      
      if (!result.success) {
        return res.status(result.code || 404).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.structure
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 移动玩家
   */
  async movePlayer(req, res) {
    try {
      const { id } = req.params;
      const { userId, direction } = req.body;
      
      if (!userId || !direction) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId 或 direction'
        });
      }
      
      const validDirections = ['north', 'south', 'east', 'west'];
      if (!validDirections.includes(direction)) {
        return res.status(400).json({
          success: false,
          message: '无效的方向，有效值为: north, south, east, west'
        });
      }
      
      const mazeService = new MazeService();
      const result = await mazeService.movePlayer(id, userId, direction);
      
      if (!result.success) {
        return res.status(result.code || 400).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.moveResult
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 交互迷宫元素
   */
  async interactWithElement(req, res) {
    try {
      const { id } = req.params;
      const { userId, elementId, action } = req.body;
      
      if (!userId || !elementId || !action) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId, elementId 或 action'
        });
      }
      
      const mazeService = new MazeService();
      const result = await mazeService.interactWithElement(id, userId, elementId, action);
      
      if (!result.success) {
        return res.status(result.code || 400).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.interactionResult
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取宝藏
   */
  async collectTreasure(req, res) {
    try {
      const { id, treasureId } = req.params;
      const { userId } = req.body;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId'
        });
      }
      
      const mazeService = new MazeService();
      const result = await mazeService.collectTreasure(id, userId, treasureId);
      
      if (!result.success) {
        return res.status(result.code || 400).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.treasure,
        message: result.message
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取探索进度
   */
  async getExplorationProgress(req, res) {
    try {
      const { id } = req.params;
      const { userId } = req.query;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId'
        });
      }
      
      const mazeService = new MazeService();
      const result = await mazeService.getExplorationProgress(id, userId);
      
      if (!result.success) {
        return res.status(result.code || 404).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.progress
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取迷宫环境状态
   */
  async getMazeEnvironment(req, res) {
    try {
      const { id } = req.params;
      
      const mazeService = new MazeService();
      const result = await mazeService.getMazeEnvironment(id);
      
      if (!result.success) {
        return res.status(result.code || 404).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.environment
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取队友位置
   */
  async getTeammatesLocations(req, res) {
    try {
      const { id } = req.params;
      const { userId } = req.query;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId'
        });
      }
      
      const mazeService = new MazeService();
      const result = await mazeService.getTeammatesLocations(id, userId);
      
      if (!result.success) {
        return res.status(result.code || 404).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.locations
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取迷宫排行榜
   */
  async getMazeLeaderboard(req, res) {
    try {
      const { id } = req.params;
      const { type = 'exploration', limit = 10 } = req.query;
      
      const mazeService = new MazeService();
      const result = await mazeService.getMazeLeaderboard(id, type, parseInt(limit));
      
      if (!result.success) {
        return res.status(result.code || 404).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.leaderboard
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 重置迷宫
   */
  async resetMaze(req, res) {
    try {
      const { id } = req.params;
      const { adminId, keepProgress = false } = req.body;
      
      if (!adminId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: adminId'
        });
      }
      
      const mazeService = new MazeService();
      const result = await mazeService.resetMaze(id, adminId, keepProgress === true);
      
      if (!result.success) {
        return res.status(result.code || 400).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.maze,
        message: '迷宫已重置'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
}

module.exports = new MazeController();

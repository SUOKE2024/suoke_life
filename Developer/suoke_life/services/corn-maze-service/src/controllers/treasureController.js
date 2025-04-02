const TreasureService = require('../services/treasureService');
const { handleError } = require('../utils/errorHandler');

/**
 * 宝藏控制器
 * 实现玉米迷宫的宝藏管理与交互功能
 */
class TreasureController {
  /**
   * 创建新宝藏
   */
  async createTreasure(req, res) {
    try {
      const { 
        name,
        description,
        type,
        rarity,
        points,
        mazeId,
        position,
        requirements,
        seasonId
      } = req.body;
      
      if (!name || !type || !mazeId || !position) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数'
        });
      }
      
      const treasureService = new TreasureService();
      const newTreasure = await treasureService.createTreasure({
        name,
        description,
        type,
        rarity: rarity || 'common',
        points: points || 10,
        mazeId,
        position,
        requirements,
        seasonId
      });
      
      return res.status(201).json({
        success: true,
        data: newTreasure,
        message: '宝藏创建成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取所有宝藏
   */
  async getAllTreasures(req, res) {
    try {
      const filters = {};
      
      // 应用过滤条件
      if (req.query.mazeId) filters.mazeId = req.query.mazeId;
      if (req.query.seasonId) filters.seasonId = req.query.seasonId;
      if (req.query.type) filters.type = req.query.type;
      if (req.query.rarity) filters.rarity = req.query.rarity;
      if (req.query.isCollected !== undefined) {
        filters.isCollected = req.query.isCollected === 'true';
      }
      
      const treasureService = new TreasureService();
      const treasures = await treasureService.getTreasures(filters);
      
      return res.status(200).json({
        success: true,
        count: treasures.length,
        data: treasures
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取单个宝藏
   */
  async getTreasureById(req, res) {
    try {
      const { id } = req.params;
      const treasureService = new TreasureService();
      const treasure = await treasureService.getTreasureById(id);
      
      if (!treasure) {
        return res.status(404).json({
          success: false,
          message: '未找到指定宝藏'
        });
      }
      
      return res.status(200).json({
        success: true,
        data: treasure
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 更新宝藏
   */
  async updateTreasure(req, res) {
    try {
      const { id } = req.params;
      const treasureService = new TreasureService();
      const treasure = await treasureService.updateTreasure(id, req.body);
      
      if (!treasure) {
        return res.status(404).json({
          success: false,
          message: '未找到指定宝藏'
        });
      }
      
      return res.status(200).json({
        success: true,
        data: treasure,
        message: '宝藏更新成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 删除宝藏
   */
  async deleteTreasure(req, res) {
    try {
      const { id } = req.params;
      const { adminId } = req.body;
      
      if (!adminId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: adminId'
        });
      }
      
      const treasureService = new TreasureService();
      const result = await treasureService.deleteTreasure(id, adminId);
      
      if (!result.success) {
        return res.status(result.code || 400).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        message: '宝藏删除成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 收集宝藏
   */
  async collectTreasure(req, res) {
    try {
      const { id } = req.params;
      const { userId, teamId } = req.body;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId'
        });
      }
      
      const treasureService = new TreasureService();
      const result = await treasureService.collectTreasure(id, userId, teamId);
      
      if (!result.success) {
        return res.status(result.code || 400).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.treasure,
        message: result.message,
        rewards: result.rewards
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取用户收集的宝藏
   */
  async getUserTreasures(req, res) {
    try {
      const { userId } = req.params;
      const { seasonId, mazeId } = req.query;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId'
        });
      }
      
      const filters = { collectedBy: userId };
      
      if (seasonId) filters.seasonId = seasonId;
      if (mazeId) filters.mazeId = mazeId;
      
      const treasureService = new TreasureService();
      const treasures = await treasureService.getUserTreasures(userId, filters);
      
      return res.status(200).json({
        success: true,
        count: treasures.length,
        data: treasures
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取团队收集的宝藏
   */
  async getTeamTreasures(req, res) {
    try {
      const { teamId } = req.params;
      const { seasonId, mazeId } = req.query;
      
      if (!teamId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: teamId'
        });
      }
      
      const filters = {};
      
      if (seasonId) filters.seasonId = seasonId;
      if (mazeId) filters.mazeId = mazeId;
      
      const treasureService = new TreasureService();
      const treasures = await treasureService.getTeamTreasures(teamId, filters);
      
      return res.status(200).json({
        success: true,
        count: treasures.length,
        totalPoints: treasures.reduce((sum, t) => sum + (t.points || 0), 0),
        data: treasures
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取附近的宝藏
   */
  async getNearbyTreasures(req, res) {
    try {
      const { mazeId } = req.params;
      const { x, y, radius = 5, userId } = req.query;
      
      if (!mazeId || x === undefined || y === undefined || !userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: mazeId, x, y, 或 userId'
        });
      }
      
      const position = {
        x: parseInt(x),
        y: parseInt(y)
      };
      
      const treasureService = new TreasureService();
      const treasures = await treasureService.getNearbyTreasures(
        mazeId, 
        position, 
        parseInt(radius), 
        userId
      );
      
      return res.status(200).json({
        success: true,
        count: treasures.length,
        data: treasures
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取宝藏收集排行榜
   */
  async getTreasureLeaderboard(req, res) {
    try {
      const { mazeId } = req.params;
      const { type = 'individual', limit = 10 } = req.query;
      
      const treasureService = new TreasureService();
      const result = await treasureService.getTreasureLeaderboard(
        mazeId, 
        type, 
        parseInt(limit)
      );
      
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
   * 生成迷宫宝藏
   */
  async generateMazeTreasures(req, res) {
    try {
      const { mazeId } = req.params;
      const { 
        count = 10, 
        adminId,
        rarityDistribution,
        typeDistribution
      } = req.body;
      
      if (!mazeId || !adminId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: mazeId 或 adminId'
        });
      }
      
      const treasureService = new TreasureService();
      const result = await treasureService.generateTreasuresForMaze(
        mazeId, 
        adminId, 
        parseInt(count),
        rarityDistribution,
        typeDistribution
      );
      
      if (!result.success) {
        return res.status(result.code || 400).json({
          success: false,
          message: result.message
        });
      }
      
      return res.status(200).json({
        success: true,
        count: result.treasures.length,
        data: result.treasures,
        message: `成功为迷宫生成了${result.treasures.length}个宝藏`
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
}

module.exports = new TreasureController();

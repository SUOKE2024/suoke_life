const Plant = require('../models/plant.model');
const PlantService = require('../services/plantService');
const { handleError } = require('../utils/errorHandler');
const { CORN_GROWTH_STAGES, GAME_PHASES } = require('../utils/constants');

/**
 * 植物控制器
 * 实现玉米植物的所有管理功能
 */
class PlantController {
  /**
   * 创建新植物
   */
  async createPlant(req, res) {
    try {
      const { name, userId, location, seasonId } = req.body;
      
      if (!name || !userId || !location || !seasonId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数'
        });
      }
      
      const plantService = new PlantService();
      const newPlant = await plantService.createPlant({
        name,
        userId,
        nickname: req.body.nickname,
        location,
        seasonId,
        gamePhase: req.body.gamePhase || GAME_PHASES.PLANTING
      });
      
      return res.status(201).json({
        success: true,
        data: newPlant,
        message: '植物创建成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取所有植物
   */
  async getAllPlants(req, res) {
    try {
      const filters = {};
      
      // 应用过滤条件
      if (req.query.userId) filters.userId = req.query.userId;
      if (req.query.seasonId) filters.seasonId = req.query.seasonId;
      if (req.query.growthStage) filters.growthStage = parseInt(req.query.growthStage);
      if (req.query.gamePhase) filters.gamePhase = req.query.gamePhase;
      if (req.query.isActive) filters.isActive = req.query.isActive === 'true';
      
      const plantService = new PlantService();
      const plants = await plantService.getPlants(filters);
      
      return res.status(200).json({
        success: true,
        count: plants.length,
        data: plants
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取单个植物
   */
  async getPlantById(req, res) {
    try {
      const { id } = req.params;
      const plantService = new PlantService();
      const plant = await plantService.getPlantById(id);
      
      if (!plant) {
        return res.status(404).json({
          success: false,
          message: '未找到指定植物'
        });
      }
      
      return res.status(200).json({
        success: true,
        data: plant
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 更新植物
   */
  async updatePlant(req, res) {
    try {
      const { id } = req.params;
      const plantService = new PlantService();
      const plant = await plantService.updatePlant(id, req.body);
      
      if (!plant) {
        return res.status(404).json({
          success: false,
          message: '未找到指定植物'
        });
      }
      
      return res.status(200).json({
        success: true,
        data: plant,
        message: '植物更新成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 删除植物
   */
  async deletePlant(req, res) {
    try {
      const { id } = req.params;
      const plantService = new PlantService();
      const result = await plantService.deletePlant(id);
      
      if (!result) {
        return res.status(404).json({
          success: false,
          message: '未找到指定植物'
        });
      }
      
      return res.status(200).json({
        success: true,
        message: '植物删除成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 浇水
   */
  async waterPlant(req, res) {
    try {
      const { id } = req.params;
      const { userId, details } = req.body;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId'
        });
      }
      
      const plantService = new PlantService();
      const result = await plantService.waterPlant(id, userId, details);
      
      if (!result.success) {
        return res.status(400).json({
          success: false,
          message: result.message || '浇水失败'
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.plant,
        message: '浇水成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 施肥
   */
  async fertilizePlant(req, res) {
    try {
      const { id } = req.params;
      const { userId, details } = req.body;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId'
        });
      }
      
      const plantService = new PlantService();
      const result = await plantService.fertilizePlant(id, userId, details);
      
      if (!result.success) {
        return res.status(400).json({
          success: false,
          message: result.message || '施肥失败'
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.plant,
        message: '施肥成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 收获植物
   */
  async harvestPlant(req, res) {
    try {
      const { id } = req.params;
      const { userId, yield } = req.body;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId'
        });
      }
      
      const plantService = new PlantService();
      const result = await plantService.harvestPlant(id, userId, yield);
      
      if (!result.success) {
        return res.status(400).json({
          success: false,
          message: result.message || '收获失败'
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.plant,
        message: '收获成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 强制生长
   */
  async forcePlantGrowth(req, res) {
    try {
      const { id } = req.params;
      const { stages } = req.body;
      
      const plantService = new PlantService();
      const result = await plantService.forceGrowth(id, stages || 1);
      
      if (!result.success) {
        return res.status(400).json({
          success: false,
          message: result.message || '促进生长失败'
        });
      }
      
      return res.status(200).json({
        success: true,
        data: result.plant,
        message: '促进生长成功'
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
  
  /**
   * 获取用户的植物统计
   */
  async getUserPlantStats(req, res) {
    try {
      const { userId } = req.params;
      
      if (!userId) {
        return res.status(400).json({
          success: false,
          message: '缺少必要参数: userId'
        });
      }
      
      const plantService = new PlantService();
      const stats = await plantService.getUserPlantStats(userId);
      
      return res.status(200).json({
        success: true,
        data: stats
      });
    } catch (error) {
      return handleError(error, res);
    }
  }
}

module.exports = new PlantController();

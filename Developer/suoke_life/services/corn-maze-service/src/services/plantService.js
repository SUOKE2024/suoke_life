const Plant = require('../models/plant.model');
const { CORN_GROWTH_STAGES, GAME_PHASES } = require('../utils/constants');
const { AppError } = require('../utils/errorHandler');

/**
 * 植物服务类
 * 实现与玉米植物相关的所有业务逻辑
 */
class PlantService {
  /**
   * 创建新植物
   * @param {Object} plantData - 植物数据
   * @returns {Object} 创建的植物
   */
  async createPlant(plantData) {
    try {
      // 验证位置是否已有植物
      const existingPlant = await Plant.findOne({
        'location.plotId': plantData.location.plotId,
        isActive: true
      });

      if (existingPlant) {
        throw new AppError('该地块已有植物', 'CONFLICT', 409);
      }

      // 创建新植物
      const newPlant = new Plant({
        name: plantData.name,
        userId: plantData.userId,
        nickname: plantData.nickname,
        location: {
          x: plantData.location.x,
          y: plantData.location.y,
          plotId: plantData.location.plotId
        },
        seasonId: plantData.seasonId,
        gamePhase: plantData.gamePhase || GAME_PHASES.PLANTING,
        growthStage: CORN_GROWTH_STAGES.SEED
      });

      await newPlant.save();
      return newPlant;
    } catch (error) {
      throw error;
    }
  }

  /**
   * 获取植物列表
   * @param {Object} filters - 过滤条件
   * @returns {Array} 植物列表
   */
  async getPlants(filters = {}) {
    try {
      const query = { ...filters };
      return await Plant.find(query).sort({ createdAt: -1 });
    } catch (error) {
      throw error;
    }
  }

  /**
   * 获取单个植物
   * @param {String} id - 植物ID
   * @returns {Object} 植物
   */
  async getPlantById(id) {
    try {
      return await Plant.findById(id);
    } catch (error) {
      throw error;
    }
  }

  /**
   * 更新植物
   * @param {String} id - 植物ID
   * @param {Object} updateData - 更新数据
   * @returns {Object} 更新后的植物
   */
  async updatePlant(id, updateData) {
    try {
      // 不允许直接更新的字段
      const protectedFields = ['_id', 'userId', 'createdAt', 'plantedAt', 'careHistory'];
      
      // 过滤掉受保护的字段
      const filteredData = Object.keys(updateData)
        .filter(key => !protectedFields.includes(key))
        .reduce((obj, key) => {
          obj[key] = updateData[key];
          return obj;
        }, {});
      
      // 添加更新时间
      filteredData.updatedAt = new Date();
      
      return await Plant.findByIdAndUpdate(
        id,
        { $set: filteredData },
        { new: true, runValidators: true }
      );
    } catch (error) {
      throw error;
    }
  }

  /**
   * 删除植物
   * @param {String} id - 植物ID
   * @returns {Boolean} 是否成功
   */
  async deletePlant(id) {
    try {
      const result = await Plant.findByIdAndUpdate(
        id,
        { isActive: false, updatedAt: new Date() },
        { new: true }
      );
      return !!result;
    } catch (error) {
      throw error;
    }
  }

  /**
   * 浇水
   * @param {String} id - 植物ID
   * @param {String} userId - 用户ID
   * @param {String} details - 详细信息
   * @returns {Object} 结果
   */
  async waterPlant(id, userId, details = '') {
    try {
      const plant = await Plant.findById(id);
      
      if (!plant) {
        return { success: false, message: '未找到指定植物' };
      }
      
      if (plant.harvested) {
        return { success: false, message: '植物已收获，无法浇水' };
      }
      
      if (!plant.isActive) {
        return { success: false, message: '植物已停用，无法浇水' };
      }
      
      // 检查是否可以浇水（24小时内只能浇水一次）
      const lastWatered = plant.lastWateredAt || plant.plantedAt;
      const hoursSinceLastWatered = (Date.now() - lastWatered) / (1000 * 60 * 60);
      
      if (hoursSinceLastWatered < 24 && userId !== 'SYSTEM') {
        return { 
          success: false, 
          message: `植物刚刚浇过水，需要等待${Math.ceil(24 - hoursSinceLastWatered)}小时后才能再次浇水`
        };
      }
      
      // 执行浇水
      const waterSuccess = plant.water(userId, details);
      
      if (!waterSuccess) {
        return { success: false, message: '浇水操作失败' };
      }
      
      await plant.save();
      
      return { success: true, plant };
    } catch (error) {
      throw error;
    }
  }

  /**
   * 施肥
   * @param {String} id - 植物ID
   * @param {String} userId - 用户ID
   * @param {String} details - 详细信息
   * @returns {Object} 结果
   */
  async fertilizePlant(id, userId, details = '') {
    try {
      const plant = await Plant.findById(id);
      
      if (!plant) {
        return { success: false, message: '未找到指定植物' };
      }
      
      if (plant.harvested) {
        return { success: false, message: '植物已收获，无法施肥' };
      }
      
      if (!plant.isActive) {
        return { success: false, message: '植物已停用，无法施肥' };
      }
      
      // 检查是否可以施肥（48小时内只能施肥一次）
      const lastFertilized = plant.lastFertilizedAt || plant.plantedAt;
      const hoursSinceLastFertilized = (Date.now() - lastFertilized) / (1000 * 60 * 60);
      
      if (hoursSinceLastFertilized < 48 && userId !== 'SYSTEM') {
        return { 
          success: false, 
          message: `植物刚刚施过肥，需要等待${Math.ceil(48 - hoursSinceLastFertilized)}小时后才能再次施肥`
        };
      }
      
      // 执行施肥
      const fertilizeSuccess = plant.fertilize(userId, details);
      
      if (!fertilizeSuccess) {
        return { success: false, message: '施肥操作失败' };
      }
      
      await plant.save();
      
      return { success: true, plant };
    } catch (error) {
      throw error;
    }
  }

  /**
   * 收获植物
   * @param {String} id - 植物ID
   * @param {String} userId - 用户ID
   * @param {Number} yield - 产量
   * @returns {Object} 结果
   */
  async harvestPlant(id, userId, yield = 1) {
    try {
      const plant = await Plant.findById(id);
      
      if (!plant) {
        return { success: false, message: '未找到指定植物' };
      }
      
      if (plant.harvested) {
        return { success: false, message: '植物已收获' };
      }
      
      if (!plant.isActive) {
        return { success: false, message: '植物已停用，无法收获' };
      }
      
      if (plant.growthStage !== CORN_GROWTH_STAGES.MATURITY) {
        return { success: false, message: '植物尚未成熟，无法收获' };
      }
      
      // 执行收获
      const harvestSuccess = plant.harvest(userId, yield);
      
      if (!harvestSuccess) {
        return { success: false, message: '收获操作失败' };
      }
      
      await plant.save();
      
      return { success: true, plant };
    } catch (error) {
      throw error;
    }
  }

  /**
   * 强制植物生长
   * @param {String} id - 植物ID
   * @param {Number} stages - 增加的生长阶段数
   * @returns {Object} 结果
   */
  async forceGrowth(id, stages = 1) {
    try {
      const plant = await Plant.findById(id);
      
      if (!plant) {
        return { success: false, message: '未找到指定植物' };
      }
      
      if (plant.harvested) {
        return { success: false, message: '植物已收获，无法生长' };
      }
      
      if (!plant.isActive) {
        return { success: false, message: '植物已停用，无法生长' };
      }
      
      if (plant.growthStage === CORN_GROWTH_STAGES.MATURITY) {
        return { success: false, message: '植物已完全成熟' };
      }
      
      // 计算新的生长阶段
      const newStage = Math.min(
        CORN_GROWTH_STAGES.MATURITY,
        plant.growthStage + Math.max(1, stages)
      );
      
      // 更新生长阶段
      plant.growthStage = newStage;
      
      // 添加系统生长记录
      plant.careHistory.push({
        action: 'grow',
        performedBy: 'SYSTEM',
        timestamp: new Date(),
        details: `系统促进生长，从阶段${plant.growthStage}到阶段${newStage}`
      });
      
      await plant.save();
      
      return { success: true, plant };
    } catch (error) {
      throw error;
    }
  }

  /**
   * 系统定时更新植物状态
   * @returns {Object} 更新结果
   */
  async updateAllPlantStatus() {
    try {
      // 查找所有活跃且未收获的植物
      const plants = await Plant.find({
        isActive: true,
        harvested: false
      });
      
      const updateResults = {
        total: plants.length,
        updated: 0,
        grown: 0,
        wilted: 0,
        errors: []
      };
      
      // 更新每个植物的状态
      for (const plant of plants) {
        try {
          plant.updateStatus();
          
          // 自然生长的机会
          const growthChance = Math.random();
          
          // 如果植物健康且水分和营养充足，有机会自然生长
          if (plant.health > 70 && plant.waterLevel > 50 && plant.nutrientLevel > 50 && growthChance > 0.7) {
            const didGrow = plant.grow();
            if (didGrow) {
              updateResults.grown++;
            }
          }
          
          await plant.save();
          updateResults.updated++;
        } catch (error) {
          updateResults.errors.push({
            plantId: plant._id,
            error: error.message
          });
        }
      }
      
      return updateResults;
    } catch (error) {
      throw error;
    }
  }

  /**
   * 获取用户的植物统计
   * @param {String} userId - 用户ID
   * @returns {Object} 统计数据
   */
  async getUserPlantStats(userId) {
    try {
      // 获取用户的所有植物
      const plants = await Plant.find({ userId });
      
      // 计算植物数量
      const totalPlants = plants.length;
      const activePlants = plants.filter(p => p.isActive).length;
      const harvestedPlants = plants.filter(p => p.harvested).length;
      
      // 计算总产量
      const totalYield = plants.reduce((sum, plant) => sum + (plant.yield || 0), 0);
      
      // 计算各生长阶段的植物数量
      const plantsByStage = Object.values(CORN_GROWTH_STAGES).reduce((acc, stage) => {
        acc[stage] = plants.filter(p => p.growthStage === stage && p.isActive && !p.harvested).length;
        return acc;
      }, {});
      
      // 计算健康状况
      const healthyPlants = plants.filter(p => p.health > 70 && p.isActive && !p.harvested).length;
      const averageHealth = plants.length ? 
        plants.reduce((sum, plant) => sum + plant.health, 0) / plants.length : 0;
      
      return {
        totalPlants,
        activePlants,
        harvestedPlants,
        totalYield,
        plantsByStage,
        healthStats: {
          healthyPlants,
          averageHealth
        },
        lastHarvest: plants.filter(p => p.harvested)
          .sort((a, b) => b.harvestedAt - a.harvestedAt)[0]?.harvestedAt || null
      };
    } catch (error) {
      throw error;
    }
  }
  
  /**
   * 批量更新植物游戏阶段
   * @param {String} seasonId - 赛季ID
   * @param {String} newPhase - 新游戏阶段
   * @returns {Object} 更新结果
   */
  async updateGamePhase(seasonId, newPhase) {
    try {
      if (!Object.values(GAME_PHASES).includes(newPhase)) {
        throw new AppError('无效的游戏阶段', 'VALIDATION_ERROR', 400);
      }
      
      const result = await Plant.updateMany(
        { seasonId, isActive: true },
        { $set: { gamePhase: newPhase, updatedAt: new Date() } }
      );
      
      return {
        success: true,
        message: `成功更新${result.modifiedCount}个植物的游戏阶段为${newPhase}`,
        modifiedCount: result.modifiedCount
      };
    } catch (error) {
      throw error;
    }
  }
}

module.exports = PlantService;

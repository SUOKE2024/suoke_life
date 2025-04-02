/**
 * NPC生成器工具
 * 用于生成测试用的NPC数据
 */
const mongoose = require('mongoose');
const NPCLocation = require('../models/npcLocation.model');
const logger = require('./logger');

/**
 * NPC生成器类
 */
class NPCGenerator {
  /**
   * 在迷宫中创建老克NPC
   * @param {string} mazeId - 迷宫ID
   * @param {Array} baseCoordinates - 基础坐标 [longitude, latitude]
   * @returns {Promise<Object>} - 返回创建的NPC位置
   */
  async createLaokeInMaze(mazeId, baseCoordinates) {
    try {
      // 创建老克NPC位置
      const npcLocation = new NPCLocation({
        npcId: 'laoke',
        name: '老克',
        description: '索克生活的智慧引导者，玉米迷宫的守护者',
        location: {
          type: 'Point',
          coordinates: baseCoordinates,
          altitude: 0
        },
        mazeId,
        radius: 50,
        isActive: true,
        startTime: new Date(),
        properties: {
          hasCornKnowledge: true,
          offersQuests: true,
          sharesSecrets: true,
          sellsItems: true
        },
        visuals: {
          avatarUrl: '/public/images/npcs/laoke-avatar.png',
          markerUrl: '/public/images/npcs/laoke-marker.png',
          markerColor: '#35BB78',
          scaleSize: 1.2
        }
      });
      
      // 设置活动时间为每天上午9点到下午6点
      npcLocation.interactionConditions = {
        timeRestricted: true,
        timeWindows: [
          { dayOfWeek: 0, startHour: 9, endHour: 18 },
          { dayOfWeek: 1, startHour: 9, endHour: 18 },
          { dayOfWeek: 2, startHour: 9, endHour: 18 },
          { dayOfWeek: 3, startHour: 9, endHour: 18 },
          { dayOfWeek: 4, startHour: 9, endHour: 18 },
          { dayOfWeek: 5, startHour: 9, endHour: 18 },
          { dayOfWeek: 6, startHour: 9, endHour: 18 }
        ],
        weatherDependent: false
      };
      
      // 添加移动路径（在迷宫中的几个关键点）
      const now = new Date();
      npcLocation.movementPath = this.generateMovementPath(baseCoordinates, 5, now);
      
      await npcLocation.save();
      logger.info(`已在迷宫[${mazeId}]中创建老克NPC位置`);
      
      return npcLocation;
    } catch (error) {
      logger.error('创建老克NPC失败', error);
      throw error;
    }
  }
  
  /**
   * 生成移动路径
   * @param {Array} baseCoordinates - 基础坐标 [longitude, latitude]
   * @param {number} pointCount - 路径点数量
   * @param {Date} startTime - 开始时间
   * @returns {Array} - 返回移动路径
   */
  generateMovementPath(baseCoordinates, pointCount = 5, startTime = new Date()) {
    const path = [];
    const baseTime = new Date(startTime);
    
    // 生成围绕基础坐标的随机路径点
    for (let i = 0; i < pointCount; i++) {
      // 在基础坐标附近生成随机偏移
      const offsetLon = (Math.random() - 0.5) * 0.002; // 约100-200米的经度偏移
      const offsetLat = (Math.random() - 0.5) * 0.002; // 约100-200米的纬度偏移
      
      const point = {
        coordinates: [
          baseCoordinates[0] + offsetLon,
          baseCoordinates[1] + offsetLat
        ],
        stayDuration: 30 + Math.floor(Math.random() * 60), // 30-90分钟的停留时间
        arrivalTime: new Date(baseTime)
      };
      
      path.push(point);
      
      // 增加时间，为下一个点做准备
      baseTime.setMinutes(baseTime.getMinutes() + 90 + Math.floor(Math.random() * 60)); // 90-150分钟后到达下一个点
    }
    
    return path;
  }
  
  /**
   * 生成测试数据
   * @param {string} mazeId - 迷宫ID
   * @param {number} count - NPC数量
   * @returns {Promise<Array>} - 返回创建的NPC位置列表
   */
  async generateTestData(mazeId, count = 3) {
    try {
      const locations = [];
      
      // 生成一个老克NPC
      const centerLocation = await this.createLaokeInMaze(
        mazeId,
        [116.3972282409668, 39.90960456049752] // 示例坐标，实际使用时需要替换为迷宫中心坐标
      );
      locations.push(centerLocation);
      
      // 生成其他NPC
      const npcTypes = ['farmer', 'scientist', 'guide'];
      const baseCoordinates = centerLocation.location.coordinates;
      
      for (let i = 0; i < count - 1 && i < npcTypes.length; i++) {
        const npcType = npcTypes[i];
        
        // 在基础坐标附近生成随机偏移
        const offsetLon = (Math.random() - 0.5) * 0.005; // 约250-500米的经度偏移
        const offsetLat = (Math.random() - 0.5) * 0.005; // 约250-500米的纬度偏移
        
        const coordinates = [
          baseCoordinates[0] + offsetLon,
          baseCoordinates[1] + offsetLat
        ];
        
        const npcLocation = new NPCLocation({
          npcId: npcType,
          name: this.getNPCName(npcType),
          description: this.getNPCDescription(npcType),
          location: {
            type: 'Point',
            coordinates,
            altitude: 0
          },
          mazeId,
          radius: 30,
          isActive: true,
          startTime: new Date(),
          properties: this.getNPCProperties(npcType),
          visuals: {
            avatarUrl: `/public/images/npcs/${npcType}-avatar.png`,
            markerUrl: `/public/images/npcs/${npcType}-marker.png`,
            markerColor: this.getNPCColor(npcType),
            scaleSize: 1.0
          }
        });
        
        // 设置简单的活动时间
        npcLocation.interactionConditions = {
          timeRestricted: true,
          timeWindows: [
            { dayOfWeek: 0, startHour: 9, endHour: 18 },
            { dayOfWeek: 1, startHour: 9, endHour: 18 },
            { dayOfWeek: 2, startHour: 9, endHour: 18 },
            { dayOfWeek: 3, startHour: 9, endHour: 18 },
            { dayOfWeek: 4, startHour: 9, endHour: 18 },
            { dayOfWeek: 5, startHour: 9, endHour: 18 },
            { dayOfWeek: 6, startHour: 9, endHour: 18 }
          ],
          weatherDependent: false
        };
        
        await npcLocation.save();
        locations.push(npcLocation);
      }
      
      logger.info(`已在迷宫[${mazeId}]中创建${locations.length}个NPC位置`);
      return locations;
    } catch (error) {
      logger.error('生成测试数据失败', error);
      throw error;
    }
  }
  
  /**
   * 获取NPC名称
   * @param {string} type - NPC类型
   * @returns {string} - 返回NPC名称
   */
  getNPCName(type) {
    const names = {
      farmer: '老农',
      scientist: '研究员',
      guide: '向导',
      merchant: '商人',
      wizard: '玉米巫师'
    };
    
    return names[type] || `未知NPC-${type}`;
  }
  
  /**
   * 获取NPC描述
   * @param {string} type - NPC类型
   * @returns {string} - 返回NPC描述
   */
  getNPCDescription(type) {
    const descriptions = {
      farmer: '世代种植玉米的老农，熟悉每一片土地的脾气。',
      scientist: '研究玉米育种的科学家，掌握着提高作物产量的秘密。',
      guide: '迷宫中的向导，能帮助迷路的人找到出口。',
      merchant: '收购农作物并提供各种工具的商人。',
      wizard: '掌握古老玉米知识的奇人，能预测天气变化。'
    };
    
    return descriptions[type] || `神秘的${this.getNPCName(type)}`;
  }
  
  /**
   * 获取NPC属性
   * @param {string} type - NPC类型
   * @returns {Object} - 返回NPC属性
   */
  getNPCProperties(type) {
    const properties = {
      farmer: {
        hasCornKnowledge: true,
        offersQuests: true,
        sharesSecrets: false,
        sellsItems: false
      },
      scientist: {
        hasCornKnowledge: true,
        offersQuests: true,
        sharesSecrets: true,
        sellsItems: false
      },
      guide: {
        hasCornKnowledge: false,
        offersQuests: true,
        sharesSecrets: true,
        sellsItems: false
      },
      merchant: {
        hasCornKnowledge: false,
        offersQuests: false,
        sharesSecrets: false,
        sellsItems: true
      },
      wizard: {
        hasCornKnowledge: true,
        offersQuests: true,
        sharesSecrets: true,
        sellsItems: false
      }
    };
    
    return properties[type] || {
      hasCornKnowledge: false,
      offersQuests: false,
      sharesSecrets: false,
      sellsItems: false
    };
  }
  
  /**
   * 获取NPC标记颜色
   * @param {string} type - NPC类型
   * @returns {string} - 返回颜色代码
   */
  getNPCColor(type) {
    const colors = {
      farmer: '#8B4513', // 棕色
      scientist: '#4169E1', // 蓝色
      guide: '#FF6800', // 索克橙
      merchant: '#FFD700', // 金色
      wizard: '#800080' // 紫色
    };
    
    return colors[type] || '#CCCCCC';
  }
}

module.exports = new NPCGenerator(); 
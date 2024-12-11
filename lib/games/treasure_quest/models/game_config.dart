import 'package:flutter/material.dart';

class GameConfig {
  static const String gameName = "索克寻宝记";
  static const String gameVersion = "1.0.0";
  
  // 游戏难度设置
  static const Map<String, Map<String, dynamic>> difficultyLevels = {
    'easy': {
      'name': '休闲探索',
      'treasureCount': 5,
      'timeLimit': 3600, // 1小时
      'hintInterval': 300, // 5分钟一次提示
    },
    'medium': {
      'name': '达人挑战',
      'treasureCount': 8,
      'timeLimit': 7200, // 2小时
      'hintInterval': 600, // 10分钟一次提示
    },
    'hard': {
      'name': '专家探险',
      'treasureCount': 12,
      'timeLimit': 10800, // 3小时
      'hintInterval': 900, // 15分钟一次提示
    },
  };

  // 当前赛季信息
  static const Map<String, dynamic> currentSeason = {
    'id': 'season_2024_spring',
    'name': '春日寻宝季',
    'theme': '云南早春野生菌探索',
    'startDate': '2024-02-01',
    'endDate': '2024-04-30',
    'specialRewards': [
      '限量版保温杯',
      '定制野餐垫',
      '索克NFT徽章',
      '野生菌鉴定手册',
    ],
  };

  // AR 功能配置
  static const Map<String, dynamic> arConfig = {
    'enableAR': true,
    'features': {
      'compass': true,
      'treasureDetector': true,
      'environmentInfo': true,
      'playerStats': true,
    },
    'effects': {
      'discovery': ['光芒四射', '金币飞舞', '烟花绽放'],
      'guidance': ['路径指引', '区域提示', '方向标记'],
      'ambient': ['自然音效', '氛围光效', '天气特效'],
    },
    'minAccuracy': 10.0, // 米
    'updateInterval': 1000, // 毫秒
  };

  // 奖励系统配置
  static const Map<String, dynamic> rewardSystem = {
    'experience': {
      'treasureFound': 100,
      'questCompleted': 200,
      'photoShared': 50,
      'helpOthers': 80,
    },
    'points': {
      'treasureFound': 50,
      'questCompleted': 100,
      'photoShared': 25,
      'helpOthers': 40,
    },
    'specialItems': {
      'rare': ['神秘菌篮', '探宝者勋章', '达人认证'],
      'epic': ['定制装备', '限定皮肤', '特效光环'],
      'legendary': ['索克大使称号', '独家NFT', '实物周边'],
    },
  };

  // 游戏内置物品
  static const Map<String, Map<String, dynamic>> gameItems = {
    'tools': {
      'basic_compass': {
        'name': '基础指南针',
        'description': '指引大致方向',
        'durability': 100,
        'accuracy': 0.8,
      },
      'advanced_detector': {
        'name': '高级探测器',
        'description': '提供精确距离',
        'durability': 80,
        'accuracy': 0.95,
      },
      'master_radar': {
        'name': '大师雷达',
        'description': '全方位探测',
        'durability': 50,
        'accuracy': 0.99,
      },
    },
    'consumables': {
      'hint_scroll': {
        'name': '提示卷轴',
        'description': '获得一次额外提示',
        'duration': 300,
      },
      'time_potion': {
        'name': '时间药水',
        'description': '延长游戏时间',
        'duration': 600,
      },
      'luck_charm': {
        'name': '幸运符咒',
        'description': '提高稀有物品出现概率',
        'duration': 1800,
      },
    },
  };

  // 天气效果
  static const Map<String, Map<String, dynamic>> weatherEffects = {
    'sunny': {
      'visibility': 1.0,
      'treasureSpawnRate': 1.0,
      'energyCost': 1.0,
    },
    'rainy': {
      'visibility': 0.7,
      'treasureSpawnRate': 1.2,
      'energyCost': 1.3,
    },
    'foggy': {
      'visibility': 0.5,
      'treasureSpawnRate': 1.5,
      'energyCost': 1.1,
    },
    'stormy': {
      'visibility': 0.3,
      'treasureSpawnRate': 2.0,
      'energyCost': 1.5,
    },
  };
} 
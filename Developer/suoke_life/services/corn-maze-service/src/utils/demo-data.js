/**
 * 演示数据生成器
 * 用于生成测试和演示用的数据
 */
const { 
  REWARD_TYPES, 
  REWARD_RARITY, 
  AR_MARKER_TYPES,
  AR_INTERACTION_TYPES,
  GESTURE_TYPES,
  IMAGE_RECOGNITION_TYPES
} = require('./constants');

/**
 * 生成AR图像识别测试数据
 * @returns {Object} 测试数据
 */
const generateARImageData = () => {
  return {
    signatures: [
      'img_sig_corn_plant_01',
      'img_sig_corn_field_wide',
      'img_sig_corn_maze_entrance',
      'img_sig_corn_maze_center',
      'img_sig_corn_special_var',
      'img_sig_corn_cob_gold',
      'img_sig_scarecrow_basic',
      'img_sig_scarecrow_special',
      'img_sig_farmer_character',
      'img_sig_maze_map_marker'
    ],
    objects: [
      {
        name: '玉米植物',
        signatures: ['img_sig_corn_plant_01', 'img_sig_corn_plant_02'],
        treasureIds: ['treasure123', 'treasure456'],
        confidenceThreshold: 0.75
      },
      {
        name: '金色玉米棒',
        signatures: ['img_sig_corn_cob_gold'],
        treasureIds: ['treasure789'],
        confidenceThreshold: 0.85
      },
      {
        name: '稻草人',
        signatures: ['img_sig_scarecrow_basic', 'img_sig_scarecrow_special'],
        treasureIds: ['treasure321', 'treasure654'],
        confidenceThreshold: 0.8
      }
    ]
  };
};

/**
 * 生成AR手势互动测试数据
 * @returns {Object} 测试数据
 */
const generateGestureData = () => {
  return [
    {
      name: GESTURE_TYPES.SWIPE_UP,
      treasureIds: ['treasure001', 'treasure002'],
      description: '向上滑动解锁宝箱'
    },
    {
      name: GESTURE_TYPES.ROTATE,
      treasureIds: ['treasure003'],
      description: '旋转手势开启旋转锁'
    },
    {
      name: GESTURE_TYPES.PINCH,
      treasureIds: ['treasure004', 'treasure005'],
      description: '捏合手势收集能量'
    },
    {
      name: GESTURE_TYPES.WAVE,
      treasureIds: ['treasure006'],
      description: '挥手呼唤精灵'
    },
    {
      name: GESTURE_TYPES.SHAKE,
      treasureIds: ['treasure007', 'treasure008'],
      description: '摇晃解开封印'
    }
  ];
};

/**
 * 生成地理位置宝藏测试数据
 * @returns {Object} 测试数据
 */
const generateLocationTreasures = () => {
  // 这些坐标仅用于测试，需要替换为实际坐标
  return [
    {
      name: '迷宫入口宝箱',
      description: '位于迷宫入口的基础宝箱',
      coordinates: [121.12345, 31.54321], // 经度，纬度
      radius: 5, // 触发半径(米)
      treasureIds: ['location_treasure_001']
    },
    {
      name: '迷宫中心宝藏',
      description: '位于迷宫中心的稀有宝藏',
      coordinates: [121.12355, 31.54331],
      radius: 3,
      treasureIds: ['location_treasure_002']
    },
    {
      name: '玉米田休息区',
      description: '隐藏在休息区的知识卡片',
      coordinates: [121.12375, 31.54311],
      radius: 8,
      treasureIds: ['location_treasure_003', 'location_treasure_004']
    },
    {
      name: '向导小屋',
      description: '向导小屋附近的任务提示',
      coordinates: [121.12395, 31.54341],
      radius: 10,
      treasureIds: ['location_treasure_005']
    }
  ];
};

/**
 * 生成社交互动测试数据
 * @returns {Object} 测试数据
 */
const generateSocialInteractionData = () => {
  return {
    teams: [
      {
        id: 'team001',
        name: '黄金探索者',
        members: ['user123', 'user456', 'user789'],
        leader: 'user123'
      },
      {
        id: 'team002',
        name: '玉米守护者',
        members: ['user321', 'user654', 'user987'],
        leader: 'user321'
      }
    ],
    teamHunts: [
      {
        id: 'hunt001',
        teamId: 'team001',
        mazeId: 'maze123',
        startedAt: new Date(Date.now() - 3600000), // 1小时前
        status: 'active'
      }
    ],
    sharedTreasures: [
      {
        fromUser: 'user123',
        toUser: 'user456',
        treasureId: 'treasure789',
        message: '这是我找到的稀有宝藏，送给你！',
        sharedAt: new Date(Date.now() - 1800000) // 30分钟前
      }
    ]
  };
};

/**
 * 生成增强现实的宝藏测试数据
 */
const generateARTreasures = () => {
  return [
    {
      name: '金色玉米棒',
      description: '传说中的金色玉米棒，带来好运和财富',
      rewardType: REWARD_TYPES.COIN,
      rarity: REWARD_RARITY.LEGENDARY,
      value: 1000,
      arMarker: {
        type: AR_MARKER_TYPES.TREASURE,
        markerId: 'AR_MARKER_001',
        modelUrl: '/models/golden_corn.glb'
      },
      interactionType: AR_INTERACTION_TYPES.GESTURE,
      gestureName: GESTURE_TYPES.SWIPE_UP,
      effectsEnabled: {
        sound: true,
        particles: true,
        haptic: true
      },
      location: {
        type: 'Point',
        coordinates: [121.12345, 31.54321]
      },
      recognitionData: {
        imageSignatures: ['img_sig_corn_cob_gold']
      },
      seasonId: 'season1',
      isLimited: true,
      limitedQuantity: 10,
      remainingQuantity: 5,
      sharable: true
    },
    {
      name: '知识宝典',
      description: '记载了玉米种植的古老知识',
      rewardType: REWARD_TYPES.KNOWLEDGE,
      rarity: REWARD_RARITY.RARE,
      value: 50,
      arMarker: {
        type: AR_MARKER_TYPES.INFO,
        markerId: 'AR_MARKER_002',
        modelUrl: '/models/knowledge_book.glb'
      },
      interactionType: AR_INTERACTION_TYPES.SIMPLE,
      effectsEnabled: {
        sound: true,
        particles: false,
        haptic: false
      },
      location: {
        type: 'Point',
        coordinates: [121.12355, 31.54331]
      },
      recognitionData: {
        imageSignatures: ['img_sig_ancient_book']
      },
      seasonId: 'season1',
      isLimited: false,
      sharable: true
    },
    {
      name: '神秘宝箱',
      description: '需要特殊手势才能打开的神秘宝箱',
      rewardType: REWARD_TYPES.ITEM,
      rarity: REWARD_RARITY.VERY_RARE,
      value: 200,
      arMarker: {
        type: AR_MARKER_TYPES.PUZZLE,
        markerId: 'AR_MARKER_003',
        modelUrl: '/models/mystery_chest.glb'
      },
      interactionType: AR_INTERACTION_TYPES.PUZZLE,
      puzzleData: {
        type: 'sequence',
        solution: [1, 3, 2, 4],
        hintText: '观察箱子上的符号，按正确顺序点击'
      },
      effectsEnabled: {
        sound: true,
        particles: true,
        haptic: true
      },
      location: {
        type: 'Point',
        coordinates: [121.12375, 31.54311]
      },
      recognitionData: {
        imageSignatures: ['img_sig_mystery_chest']
      },
      seasonId: 'season1',
      isLimited: true,
      limitedQuantity: 20,
      remainingQuantity: 15,
      sharable: false
    },
    {
      name: '稀有种子包',
      description: '包含稀有玉米品种的种子',
      rewardType: REWARD_TYPES.RARE_SEED,
      rarity: REWARD_RARITY.UNCOMMON,
      value: 100,
      arMarker: {
        type: AR_MARKER_TYPES.TREASURE,
        markerId: 'AR_MARKER_004',
        modelUrl: '/models/seed_pack.glb'
      },
      interactionType: AR_INTERACTION_TYPES.AR_ANIMATION,
      animationAsset: '/animations/seed_growing.glb',
      effectsEnabled: {
        sound: true,
        particles: true,
        haptic: false
      },
      location: {
        type: 'Point',
        coordinates: [121.12395, 31.54341]
      },
      recognitionData: {
        imageSignatures: ['img_sig_seed_pack']
      },
      seasonId: 'season1',
      isLimited: false,
      sharable: true
    }
  ];
};

module.exports = {
  generateARImageData,
  generateGestureData,
  generateLocationTreasures,
  generateSocialInteractionData,
  generateARTreasures
}; 
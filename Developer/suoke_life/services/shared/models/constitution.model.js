/**
 * 体质模型
 * 描述中医九种体质分类及相关属性
 */
const Joi = require('joi');
const { v4: uuidv4 } = require('uuid');

/**
 * 体质类型枚举
 * 基于中医传统九种体质分类
 * @type {Object}
 */
const ConstitutionType = {
  BALANCED: 'balanced',              // 平和质
  QI_DEFICIENCY: 'qi_deficiency',    // 气虚质
  YANG_DEFICIENCY: 'yang_deficiency', // 阳虚质
  YIN_DEFICIENCY: 'yin_deficiency',  // 阴虚质
  PHLEGM_DAMPNESS: 'phlegm_dampness', // 痰湿质
  DAMP_HEAT: 'damp_heat',            // 湿热质
  BLOOD_STASIS: 'blood_stasis',      // 血瘀质
  QI_STAGNATION: 'qi_stagnation',    // 气郁质
  SPECIAL: 'special'                 // 特禀质
};

/**
 * 体质特征类别
 * @type {Object}
 */
const TraitCategory = {
  PHYSICAL: 'physical',       // 体形特征
  PSYCHOLOGICAL: 'psychological', // 心理特征
  DISEASE: 'disease',         // 发病倾向
  RESPONSE: 'response',       // 对外界环境的反应
  ADAPTATION: 'adaptation'    // 适应能力
};

/**
 * 体质模型验证模式
 * @type {Object}
 */
const constitutionSchema = Joi.object({
  id: Joi.string().uuid().default(() => uuidv4()),
  type: Joi.string().valid(...Object.values(ConstitutionType)).required(),
  name: Joi.string().required(),
  nameEn: Joi.string(),
  description: Joi.string().required(),
  characteristics: Joi.array().items(
    Joi.object({
      category: Joi.string().valid(...Object.values(TraitCategory)).required(),
      traits: Joi.array().items(Joi.string()).required()
    })
  ).required(),
  symptoms: Joi.array().items(Joi.string()),
  tendencies: Joi.array().items(Joi.string()),
  causes: Joi.array().items(Joi.string()),
  recommendations: Joi.object({
    diet: Joi.array().items(Joi.string()),
    lifestyle: Joi.array().items(Joi.string()),
    exercise: Joi.array().items(Joi.string()),
    environment: Joi.array().items(Joi.string()),
    avoid: Joi.array().items(Joi.string())
  }).required(),
  associatedDiseases: Joi.array().items(Joi.string()),
  createdAt: Joi.date().default(() => new Date()),
  updatedAt: Joi.date().default(() => new Date())
});

/**
 * 体质评估问卷验证模式
 * @type {Object}
 */
const constitutionQuestionnaireSchema = Joi.object({
  id: Joi.string().uuid().default(() => uuidv4()),
  name: Joi.string().required(),
  description: Joi.string(),
  version: Joi.string().required(),
  questions: Joi.array().items(
    Joi.object({
      id: Joi.string().required(),
      text: Joi.string().required(),
      constitutionType: Joi.string().valid(...Object.values(ConstitutionType)),
      options: Joi.array().items(
        Joi.object({
          id: Joi.string().required(),
          text: Joi.string().required(),
          score: Joi.number().required()
        })
      ).required(),
      category: Joi.string().valid(...Object.values(TraitCategory)),
      required: Joi.boolean().default(true)
    })
  ).required(),
  scoringMethod: Joi.string().valid('sum', 'average', 'weighted').required(),
  thresholds: Joi.object().pattern(
    Joi.string().valid(...Object.values(ConstitutionType)),
    Joi.object({
      min: Joi.number().required(),
      max: Joi.number().required(),
      level: Joi.object({
        mild: Joi.number(),
        moderate: Joi.number(),
        severe: Joi.number()
      })
    })
  ).required(),
  createdAt: Joi.date().default(() => new Date()),
  updatedAt: Joi.date().default(() => new Date())
});

/**
 * 体质评估结果验证模式
 * @type {Object}
 */
const constitutionAssessmentResultSchema = Joi.object({
  id: Joi.string().uuid().default(() => uuidv4()),
  userId: Joi.string().uuid().required(),
  questionnaireId: Joi.string().uuid().required(),
  questionnaireVersion: Joi.string().required(),
  answers: Joi.array().items(
    Joi.object({
      questionId: Joi.string().required(),
      optionId: Joi.string().required(),
      score: Joi.number().required()
    })
  ).required(),
  scores: Joi.object().pattern(
    Joi.string().valid(...Object.values(ConstitutionType)),
    Joi.number()
  ).required(),
  primaryConstitution: Joi.string().valid(...Object.values(ConstitutionType)).required(),
  secondaryConstitutions: Joi.array().items(
    Joi.string().valid(...Object.values(ConstitutionType))
  ),
  severity: Joi.string().valid('mild', 'moderate', 'severe'),
  assessmentDate: Joi.date().default(() => new Date()),
  recommendations: Joi.object({
    diet: Joi.array().items(Joi.string()),
    lifestyle: Joi.array().items(Joi.string()),
    exercise: Joi.array().items(Joi.string()),
    environment: Joi.array().items(Joi.string()),
    avoid: Joi.array().items(Joi.string())
  }),
  practitioner: Joi.string(),
  notes: Joi.string(),
  createdAt: Joi.date().default(() => new Date()),
  updatedAt: Joi.date().default(() => new Date())
});

/**
 * 预定义的体质特征
 * @type {Object}
 */
const constitutionTraits = {
  // 平和质特征
  balanced: {
    physical: [
      '体形匀称',
      '面色红润',
      '目光有神',
      '唇色红润',
      '头发稠密有光泽',
      '肌肉结实有弹性',
      '食欲良好',
      '二便正常'
    ],
    psychological: [
      '性格随和开朗',
      '乐观豁达',
      '适应能力强',
      '精力充沛',
      '情绪稳定',
      '不易疲劳'
    ],
    disease: [
      '抗病能力强',
      '很少生病',
      '病后恢复快'
    ],
    response: [
      '对外界环境适应性强',
      '不易受气候变化影响',
      '耐寒耐热'
    ]
  },
  
  // 气虚质特征
  qi_deficiency: {
    physical: [
      '体形偏瘦或肥胖',
      '面色淡白或萎黄',
      '语声低弱',
      '气短懒言',
      '易出汗',
      '舌淡胖',
      '脉弱'
    ],
    psychological: [
      '性格内向',
      '不爱言语',
      '做事缺乏毅力',
      '易疲劳',
      '精神不振'
    ],
    disease: [
      '易患感冒',
      '肺系疾病',
      '消化不良',
      '慢性疾病'
    ],
    response: [
      '对气候环境变化敏感',
      '不耐受劳累',
      '容易出汗'
    ]
  },
  
  // 阳虚质特征
  yang_deficiency: {
    physical: [
      '体形偏胖',
      '皮肤白而冷',
      '手足不温',
      '面色苍白',
      '喜热怕冷',
      '口淡不渴',
      '舌淡胖苔白',
      '脉沉迟'
    ],
    psychological: [
      '性格安静',
      '稳重',
      '不活泼',
      '喜静不喜动',
      '怕冷'
    ],
    disease: [
      '易感寒邪',
      '关节疼痛',
      '腹泻',
      '水肿',
      '甲状腺功能减退'
    ],
    response: [
      '冬季症状加重',
      '遇冷加重',
      '遇热减轻'
    ]
  },
  
  // 阴虚质特征
  yin_deficiency: {
    physical: [
      '体形偏瘦',
      '面色潮红或偏黑',
      '口燥咽干',
      '手足心热',
      '皮肤干燥',
      '大便干结',
      '舌红少苔',
      '脉细数'
    ],
    psychological: [
      '性格急躁',
      '容易激动',
      '不耐烦',
      '易失眠',
      '健忘'
    ],
    disease: [
      '易患热性病',
      '口腔溃疡',
      '干眼症',
      '便秘',
      '潮热盗汗'
    ],
    response: [
      '夏季症状加重',
      '遇热加重',
      '遇凉减轻'
    ]
  },
  
  // 痰湿质特征
  phlegm_dampness: {
    physical: [
      '体形肥胖',
      '腹部肥满松软',
      '面部皮肤油腻',
      '多痰',
      '口粘腻',
      '舌苔厚腻',
      '脉滑'
    ],
    psychological: [
      '性格温和',
      '不易激动',
      '嗜睡',
      '反应迟钝',
      '思维迟缓'
    ],
    disease: [
      '易患代谢综合征',
      '痰多',
      '胸闷',
      '水肿',
      '消化不良'
    ],
    response: [
      '梅雨季节症状加重',
      '湿度大时不适'
    ]
  },
  
  // 湿热质特征
  damp_heat: {
    physical: [
      '面垢油光',
      '易生痤疮',
      '口苦口臭',
      '身重困倦',
      '大便粘滞不爽',
      '小便短黄',
      '舌红苔黄腻',
      '脉滑数'
    ],
    psychological: [
      '性格急躁',
      '外向',
      '容易烦闷',
      '抑郁',
      '情绪不稳'
    ],
    disease: [
      '易患皮肤病',
      '肝胆疾病',
      '泌尿系感染',
      '痔疮'
    ],
    response: [
      '夏季和梅雨季节症状加重',
      '湿热环境中不适'
    ]
  },
  
  // 血瘀质特征
  blood_stasis: {
    physical: [
      '肤色晦暗',
      '唇色偏暗',
      '易出现皮下瘀斑',
      '舌质紫暗或有瘀点',
      '舌下静脉曲张',
      '脉涩'
    ],
    psychological: [
      '性格内向',
      '抑郁',
      '烦闷',
      '健忘',
      '多愁善感'
    ],
    disease: [
      '易患心脑血管疾病',
      '静脉曲张',
      '痛经',
      '月经不调',
      '瘤样病变'
    ],
    response: [
      '寒冷加重',
      '气候变化时症状明显'
    ]
  },
  
  // 气郁质特征
  qi_stagnation: {
    physical: [
      '体形偏瘦',
      '常太息',
      '胸胁胀痛',
      '咽喉异物感',
      '舌边有齿痕',
      '脉弦'
    ],
    psychological: [
      '性格内向',
      '抑郁',
      '敏感多虑',
      '情绪不稳',
      '容易紧张',
      '焦虑'
    ],
    disease: [
      '易患抑郁症',
      '焦虑症',
      '失眠',
      '植物神经功能紊乱',
      '消化不良'
    ],
    response: [
      '精神压力大时症状加重',
      '情绪波动明显时不适'
    ]
  },
  
  // 特禀质特征
  special: {
    physical: [
      '过敏体质',
      '反应性强',
      '特定食物或药物过敏',
      '皮肤过敏',
      '过敏性鼻炎',
      '哮喘',
      '湿疹'
    ],
    psychological: [
      '性格谨慎',
      '敏感',
      '警惕性高'
    ],
    disease: [
      '易患过敏性疾病',
      '自身免疫性疾病',
      '遗传性疾病'
    ],
    response: [
      '对特定环境或物质反应强烈',
      '季节变换时症状明显'
    ]
  }
};

/**
 * 获取体质类型的详细信息
 * @param {string} constitutionType - 体质类型
 * @returns {Object} 体质类型详细信息
 */
function getConstitutionInfo(constitutionType) {
  if (!Object.values(ConstitutionType).includes(constitutionType)) {
    throw new Error(`无效的体质类型: ${constitutionType}`);
  }
  
  // 基本体质信息
  const constitutionInfo = {
    type: constitutionType,
    name: getConstitutionName(constitutionType),
    nameEn: getConstitutionNameEn(constitutionType),
    description: getConstitutionDescription(constitutionType),
    characteristics: [],
    recommendations: {
      diet: [],
      lifestyle: [],
      exercise: [],
      environment: [],
      avoid: []
    }
  };
  
  // 添加体质特征
  if (constitutionTraits[constitutionType]) {
    Object.entries(constitutionTraits[constitutionType]).forEach(([category, traits]) => {
      constitutionInfo.characteristics.push({
        category,
        traits
      });
    });
  }
  
  // 添加体质推荐
  const recommendations = getConstitutionRecommendations(constitutionType);
  if (recommendations) {
    constitutionInfo.recommendations = recommendations;
  }
  
  return constitutionInfo;
}

/**
 * 获取体质名称
 * @param {string} constitutionType - 体质类型
 * @returns {string} 体质名称
 */
function getConstitutionName(constitutionType) {
  const names = {
    [ConstitutionType.BALANCED]: '平和质',
    [ConstitutionType.QI_DEFICIENCY]: '气虚质',
    [ConstitutionType.YANG_DEFICIENCY]: '阳虚质',
    [ConstitutionType.YIN_DEFICIENCY]: '阴虚质',
    [ConstitutionType.PHLEGM_DAMPNESS]: '痰湿质',
    [ConstitutionType.DAMP_HEAT]: '湿热质',
    [ConstitutionType.BLOOD_STASIS]: '血瘀质',
    [ConstitutionType.QI_STAGNATION]: '气郁质',
    [ConstitutionType.SPECIAL]: '特禀质'
  };
  
  return names[constitutionType] || '未知体质';
}

/**
 * 获取体质英文名称
 * @param {string} constitutionType - 体质类型
 * @returns {string} 体质英文名称
 */
function getConstitutionNameEn(constitutionType) {
  const names = {
    [ConstitutionType.BALANCED]: 'Balanced Constitution',
    [ConstitutionType.QI_DEFICIENCY]: 'Qi Deficiency Constitution',
    [ConstitutionType.YANG_DEFICIENCY]: 'Yang Deficiency Constitution',
    [ConstitutionType.YIN_DEFICIENCY]: 'Yin Deficiency Constitution',
    [ConstitutionType.PHLEGM_DAMPNESS]: 'Phlegm-Dampness Constitution',
    [ConstitutionType.DAMP_HEAT]: 'Damp-Heat Constitution',
    [ConstitutionType.BLOOD_STASIS]: 'Blood Stasis Constitution',
    [ConstitutionType.QI_STAGNATION]: 'Qi Stagnation Constitution',
    [ConstitutionType.SPECIAL]: 'Allergic Constitution'
  };
  
  return names[constitutionType] || 'Unknown Constitution';
}

/**
 * 获取体质描述
 * @param {string} constitutionType - 体质类型
 * @returns {string} 体质描述
 */
function getConstitutionDescription(constitutionType) {
  const descriptions = {
    [ConstitutionType.BALANCED]: '平和质是九种体质中最为理想的状态，阴阳气血调和，脏腑功能正常，体形匀称，面色红润，精力充沛，对外界环境适应能力强，抗病能力强。',
    [ConstitutionType.QI_DEFICIENCY]: '气虚质主要表现为气虚，常见疲乏无力，气短懒言，自汗，舌淡，脉弱等，对环境适应能力差，抵抗力低下，易感冒。',
    [ConstitutionType.YANG_DEFICIENCY]: '阳虚质主要表现为阳气不足，畏寒肢冷，面色苍白，喜热饮食，大便溏薄，舌淡胖，脉沉迟。冬季症状加重，夏季减轻。',
    [ConstitutionType.YIN_DEFICIENCY]: '阴虚质主要表现为阴液亏少，口燥咽干，手足心热，潮热盗汗，舌红少苔，脉细数。夏季症状加重，冬季减轻。',
    [ConstitutionType.PHLEGM_DAMPNESS]: '痰湿质主要表现为痰湿内蕴，形体肥胖，腹部松软，面部皮肤油腻，多痰，口粘腻，舌苔厚腻，脉滑。雨季症状加重。',
    [ConstitutionType.DAMP_HEAT]: '湿热质主要表现为湿热内蕴，面垢油光，易生痤疮，口苦口臭，身重困倦，小便短黄，大便粘滞不爽，舌红苔黄腻，脉滑数。',
    [ConstitutionType.BLOOD_STASIS]: '血瘀质主要表现为血行不畅，肤色晦暗，唇色偏暗，舌质紫暗或有瘀点，舌下静脉曲张，脉涩。寒冷时症状加重。',
    [ConstitutionType.QI_STAGNATION]: '气郁质主要表现为气机郁滞，情绪不稳，抑郁，胸胁胀痛，咽喉异物感，舌边有齿痕，脉弦。精神压力大时症状加重。',
    [ConstitutionType.SPECIAL]: '特禀质主要表现为特殊体质，对某些物质或环境过敏，如食物、药物、花粉、季节变化等，易患过敏性疾病。'
  };
  
  return descriptions[constitutionType] || '无详细描述';
}

/**
 * 获取体质调理建议
 * @param {string} constitutionType - 体质类型
 * @returns {Object} 体质调理建议
 */
function getConstitutionRecommendations(constitutionType) {
  const recommendations = {
    [ConstitutionType.BALANCED]: {
      diet: [
        '饮食均衡多样',
        '定时定量',
        '粗细搭配',
        '七分饱为宜'
      ],
      lifestyle: [
        '作息规律',
        '保持乐观心态',
        '适度劳逸结合'
      ],
      exercise: [
        '适量运动',
        '太极拳',
        '八段锦',
        '散步',
        '游泳'
      ],
      environment: [
        '保持居室通风',
        '避免污染环境'
      ],
      avoid: [
        '避免过度劳累',
        '避免情绪剧烈波动',
        '避免过度饮食'
      ]
    },
    [ConstitutionType.QI_DEFICIENCY]: {
      diet: [
        '多食补气食物如大枣、山药、黄芪、人参、莲子等',
        '少食生冷食物',
        '适量增加优质蛋白质',
        '小量多餐'
      ],
      lifestyle: [
        '保证充足睡眠',
        '避免过度劳累',
        '适当午休'
      ],
      exercise: [
        '温和锻炼',
        '气功',
        '太极',
        '缓步行走',
        '避免剧烈运动'
      ],
      environment: [
        '保持环境温暖',
        '避免风寒'
      ],
      avoid: [
        '避免过度劳累',
        '避免大量出汗',
        '避免情绪低落'
      ]
    },
    [ConstitutionType.YANG_DEFICIENCY]: {
      diet: [
        '多食温阳食物如羊肉、狗肉、韭菜、生姜、桂圆等',
        '避免生冷食物',
        '食物宜温热',
        '可适量饮用红茶'
      ],
      lifestyle: [
        '保暖',
        '早睡早起',
        '适当日光浴'
      ],
      exercise: [
        '八段锦',
        '六字诀',
        '温和锻炼',
        '避免出大汗'
      ],
      environment: [
        '保持环境温暖干燥',
        '避免寒冷潮湿'
      ],
      avoid: [
        '避免受寒',
        '避免游泳',
        '避免在寒冷环境长时间停留'
      ]
    },
    [ConstitutionType.YIN_DEFICIENCY]: {
      diet: [
        '多食滋阴食物如银耳、百合、梨、芝麻、蜂蜜、豆腐等',
        '少食辛辣刺激性食物',
        '避免过热食物',
        '少饮酒和咖啡'
      ],
      lifestyle: [
        '保证充足睡眠',
        '保持情绪平静',
        '避免熬夜'
      ],
      exercise: [
        '温和锻炼',
        '太极',
        '游泳',
        '避免剧烈运动和大量出汗'
      ],
      environment: [
        '保持环境湿润',
        '避免干燥炎热'
      ],
      avoid: [
        '避免长时间暴露在高温环境',
        '避免情绪激动',
        '避免熬夜'
      ]
    },
    [ConstitutionType.PHLEGM_DAMPNESS]: {
      diet: [
        '清淡饮食',
        '多食健脾化湿食物如薏苡仁、赤小豆、扁豆、冬瓜等',
        '少食油腻甜腻食物',
        '控制总热量摄入'
      ],
      lifestyle: [
        '早睡早起',
        '保持心情舒畅',
        '避免久坐'
      ],
      exercise: [
        '增加有氧运动',
        '慢跑',
        '快走',
        '游泳',
        '适量出汗'
      ],
      environment: [
        '保持环境干燥通风',
        '避免潮湿环境'
      ],
      avoid: [
        '避免过度饮食',
        '避免长时间处于潮湿环境',
        '避免暴饮暴食'
      ]
    },
    [ConstitutionType.DAMP_HEAT]: {
      diet: [
        '清淡饮食',
        '多食清热利湿食物如绿豆、苦瓜、芦笋、荷叶等',
        '少食辛辣油腻食物',
        '避免烟酒'
      ],
      lifestyle: [
        '作息规律',
        '保持情绪平和',
        '避免熬夜'
      ],
      exercise: [
        '适量有氧运动',
        '游泳',
        '慢跑',
        '促进排汗'
      ],
      environment: [
        '保持环境凉爽干燥',
        '避免高温潮湿'
      ],
      avoid: [
        '避免桑拿浴',
        '避免长时间处于高温环境',
        '避免情绪激动'
      ]
    },
    [ConstitutionType.BLOOD_STASIS]: {
      diet: [
        '多食活血化瘀食物如红枣、桃仁、红花、当归、醋等',
        '少食寒凉食物',
        '适量饮食',
        '避免高脂肪食物'
      ],
      lifestyle: [
        '保持情绪舒畅',
        '避免长时间保持一个姿势',
        '保暖'
      ],
      exercise: [
        '适度有氧运动',
        '太极',
        '游泳',
        '促进血液循环'
      ],
      environment: [
        '保持环境温暖',
        '避免寒冷'
      ],
      avoid: [
        '避免受寒',
        '避免情绪抑郁',
        '避免长时间久坐或站立'
      ]
    },
    [ConstitutionType.QI_STAGNATION]: {
      diet: [
        '多食疏肝理气食物如柑橘、玫瑰花、佛手、白萝卜等',
        '饮食有规律',
        '少食油腻厚味食物',
        '少饮酒'
      ],
      lifestyle: [
        '保持心情愉快',
        '学习情绪管理',
        '适当倾诉',
        '培养兴趣爱好'
      ],
      exercise: [
        '增加户外活动',
        '太极',
        '瑜伽',
        '慢跑',
        '促进气血流通'
      ],
      environment: [
        '保持环境宽敞明亮',
        '增加社交活动'
      ],
      avoid: [
        '避免压力过大',
        '避免情绪郁闷',
        '避免沉默寡言'
      ]
    },
    [ConstitutionType.SPECIAL]: {
      diet: [
        '避免过敏原食物',
        '保持饮食清淡',
        '增加抗过敏食物如蜂蜜、苹果等',
        '记录并避免可能引起过敏的食物'
      ],
      lifestyle: [
        '保持心情舒畅',
        '避免过度疲劳',
        '注意保暖'
      ],
      exercise: [
        '温和锻炼',
        '太极',
        '瑜伽',
        '增强体质'
      ],
      environment: [
        '保持环境清洁',
        '避免过敏原',
        '使用空气净化器'
      ],
      avoid: [
        '避免接触已知过敏原',
        '避免突然的温度变化',
        '避免在花粉季节长时间户外活动'
      ]
    }
  };
  
  return recommendations[constitutionType] || null;
}

/**
 * 评估多种体质的综合状况
 * @param {Object} constitutionScores - 各体质类型的分数
 * @returns {Object} 评估结果，包含主要和次要体质
 */
function assessConstitution(constitutionScores) {
  if (!constitutionScores || typeof constitutionScores !== 'object') {
    throw new Error('评估体质需要提供有效的体质分数对象');
  }
  
  // 找出得分最高的体质作为主要体质
  let primaryConstitution = null;
  let highestScore = -1;
  
  // 次要体质（得分超过阈值的体质）
  const secondaryConstitutions = [];
  const SECONDARY_THRESHOLD = 60; // 设定次要体质的分数阈值
  
  Object.entries(constitutionScores).forEach(([type, score]) => {
    // 验证体质类型是否有效
    if (!Object.values(ConstitutionType).includes(type)) {
      throw new Error(`无效的体质类型: ${type}`);
    }
    
    // 验证分数是否为数字且在有效范围内
    if (typeof score !== 'number' || score < 0 || score > 100) {
      throw new Error(`体质分数无效: ${type}=${score}`);
    }
    
    // 更新主要体质
    if (score > highestScore) {
      highestScore = score;
      primaryConstitution = type;
    }
    
    // 添加次要体质（得分高于阈值但不是最高分）
    if (score >= SECONDARY_THRESHOLD) {
      secondaryConstitutions.push(type);
    }
  });
  
  // 从次要体质中移除主要体质（如果存在）
  const finalSecondaryConstitutions = secondaryConstitutions.filter(type => type !== primaryConstitution);
  
  // 确定体质严重程度
  let severity = 'mild';
  if (highestScore >= 80) {
    severity = 'severe';
  } else if (highestScore >= 70) {
    severity = 'moderate';
  }
  
  return {
    primaryConstitution,
    secondaryConstitutions: finalSecondaryConstitutions,
    severity,
    scores: constitutionScores
  };
}

/**
 * 创建体质评估问卷
 * @param {Object} data - 问卷数据
 * @returns {Object} 验证后的问卷对象
 */
function createConstitutionQuestionnaire(data) {
  const { error, value } = constitutionQuestionnaireSchema.validate(data);
  if (error) {
    throw new Error(`体质问卷验证失败: ${error.message}`);
  }
  return value;
}

/**
 * 记录体质评估结果
 * @param {Object} data - 评估结果数据
 * @returns {Object} 验证后的评估结果对象
 */
function recordConstitutionAssessment(data) {
  const { error, value } = constitutionAssessmentResultSchema.validate(data);
  if (error) {
    throw new Error(`体质评估结果验证失败: ${error.message}`);
  }
  return value;
}

module.exports = {
  ConstitutionType,
  TraitCategory,
  constitutionSchema,
  constitutionQuestionnaireSchema,
  constitutionAssessmentResultSchema,
  constitutionTraits,
  getConstitutionInfo,
  getConstitutionName,
  getConstitutionNameEn,
  getConstitutionDescription,
  getConstitutionRecommendations,
  assessConstitution,
  createConstitutionQuestionnaire,
  recordConstitutionAssessment
}; 
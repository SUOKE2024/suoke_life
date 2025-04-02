/**
 * 健康记录模型
 * 描述用户的健康数据记录
 */
const Joi = require('joi');
const { v4: uuidv4 } = require('uuid');

/**
 * 健康记录类型枚举
 * @type {Object}
 */
const HealthRecordType = {
  DAILY_CHECKUP: 'daily_checkup',   // 日常健康检查
  SLEEP: 'sleep',                   // 睡眠记录
  DIET: 'diet',                     // 饮食记录
  EXERCISE: 'exercise',             // 运动记录
  EMOTION: 'emotion',               // 情绪记录
  SYMPTOM: 'symptom',               // 症状记录
  MEDICATION: 'medication',         // 用药记录
  VITAL_SIGNS: 'vital_signs',       // 生命体征
  TCM_DIAGNOSIS: 'tcm_diagnosis',   // 中医诊断
  PULSE_DIAGNOSIS: 'pulse_diagnosis', // 脉诊
  TONGUE_DIAGNOSIS: 'tongue_diagnosis', // 舌诊
  CONSTITUTION_ASSESSMENT: 'constitution_assessment' // 体质评估
};

/**
 * 健康记录验证模式
 * @type {Object}
 */
const healthRecordSchema = Joi.object({
  id: Joi.string().uuid().default(() => uuidv4()),
  userId: Joi.string().uuid().required(),
  type: Joi.string().valid(...Object.values(HealthRecordType)).required(),
  timestamp: Joi.date().default(() => new Date()),
  data: Joi.object().required(),
  source: Joi.string().valid('app', 'wearable', 'external', 'manual').default('app'),
  tags: Joi.array().items(Joi.string()),
  meta: Joi.object(),
  createdAt: Joi.date().default(() => new Date()),
  updatedAt: Joi.date().default(() => new Date())
});

/**
 * 生命体征记录验证模式
 * @type {Object}
 */
const vitalSignsSchema = Joi.object({
  temperature: Joi.number().min(35).max(42),
  heartRate: Joi.number().min(30).max(220),
  respiratoryRate: Joi.number().min(8).max(30),
  bloodPressureSystolic: Joi.number().min(70).max(220),
  bloodPressureDiastolic: Joi.number().min(40).max(120),
  bloodOxygenLevel: Joi.number().min(80).max(100),
  bloodGlucose: Joi.number().min(2).max(30)
});

/**
 * 睡眠记录验证模式
 * @type {Object}
 */
const sleepSchema = Joi.object({
  startTime: Joi.date().required(),
  endTime: Joi.date().required(),
  duration: Joi.number().min(0),
  quality: Joi.number().min(1).max(5),
  deepSleepDuration: Joi.number().min(0),
  lightSleepDuration: Joi.number().min(0),
  remSleepDuration: Joi.number().min(0),
  awakeDuration: Joi.number().min(0),
  sleepLatency: Joi.number().min(0),
  sleepEfficiency: Joi.number().min(0).max(100),
  disturbances: Joi.array().items(
    Joi.object({
      time: Joi.date(),
      duration: Joi.number().min(0),
      reason: Joi.string()
    })
  )
});

/**
 * 饮食记录验证模式
 * @type {Object}
 */
const dietSchema = Joi.object({
  mealType: Joi.string().valid('breakfast', 'lunch', 'dinner', 'snack'),
  foods: Joi.array().items(
    Joi.object({
      name: Joi.string().required(),
      category: Joi.string(),
      amount: Joi.number().min(0),
      unit: Joi.string(),
      calories: Joi.number().min(0),
      protein: Joi.number().min(0),
      carbs: Joi.number().min(0),
      fat: Joi.number().min(0),
      fiber: Joi.number().min(0),
      tcmProperties: Joi.object({
        nature: Joi.string().valid('hot', 'warm', 'neutral', 'cool', 'cold'),
        taste: Joi.array().items(Joi.string().valid('sour', 'bitter', 'sweet', 'spicy', 'salty')),
        meridians: Joi.array().items(Joi.string())
      })
    })
  ),
  waterIntake: Joi.number().min(0),
  notes: Joi.string(),
  location: Joi.string(),
  hunger: Joi.number().min(1).max(5),
  satisfaction: Joi.number().min(1).max(5)
});

/**
 * 中医诊断记录验证模式
 * @type {Object}
 */
const tcmDiagnosisSchema = Joi.object({
  practitioner: Joi.string(),
  mainComplaint: Joi.string().required(),
  diagnosisMethod: Joi.string().valid('looking', 'listening', 'asking', 'touching', 'comprehensive'),
  syndrome: Joi.array().items(Joi.string()),
  meridianInvolved: Joi.array().items(Joi.string()),
  organPatterns: Joi.array().items(Joi.string()),
  disharmonyPattern: Joi.array().items(Joi.string()),
  treatmentPrinciple: Joi.string(),
  treatmentSuggestions: Joi.array().items(Joi.string()),
  herbs: Joi.array().items(
    Joi.object({
      name: Joi.string().required(),
      amount: Joi.string(),
      purpose: Joi.string()
    })
  ),
  acupointsPrescribed: Joi.array().items(Joi.string()),
  lifestyle: Joi.object({
    dietRecommendations: Joi.array().items(Joi.string()),
    exerciseRecommendations: Joi.array().items(Joi.string()),
    emotionalBalance: Joi.array().items(Joi.string()),
    restrictions: Joi.array().items(Joi.string())
  }),
  notes: Joi.string()
});

/**
 * 脉诊记录验证模式
 * @type {Object}
 */
const pulseDiagnosisSchema = Joi.object({
  leftWrist: Joi.object({
    cun: Joi.string().required(),
    guan: Joi.string().required(),
    chi: Joi.string().required()
  }),
  rightWrist: Joi.object({
    cun: Joi.string().required(),
    guan: Joi.string().required(),
    chi: Joi.string().required()
  }),
  pulseDescription: Joi.object({
    depth: Joi.string().valid('floating', 'sinking', 'hidden'),
    speed: Joi.string().valid('rapid', 'slow', 'moderate'),
    strength: Joi.string().valid('excess', 'deficient', 'moderate'),
    rhythm: Joi.string().valid('regular', 'irregular', 'knotted', 'intermittent'),
    width: Joi.string().valid('thin', 'thready', 'slippery', 'wiry', 'large'),
    length: Joi.string().valid('long', 'short'),
    texture: Joi.string().valid('slippery', 'choppy', 'fine', 'firm')
  }),
  notes: Joi.string()
});

/**
 * 舌诊记录验证模式
 * @type {Object}
 */
const tongueDiagnosisSchema = Joi.object({
  tongueColor: Joi.string().valid('pale', 'pink', 'red', 'dark-red', 'purple', 'blue'),
  tongueShape: Joi.string().valid('swollen', 'thin', 'cracked', 'stiff', 'flaccid', 'quivering', 'deviated', 'normal'),
  tongueCoating: Joi.object({
    color: Joi.string().valid('white', 'yellow', 'gray', 'black', 'none'),
    thickness: Joi.string().valid('thin', 'thick', 'none', 'partial'),
    distribution: Joi.string().valid('full', 'center', 'root', 'sides', 'peeled', 'geographic'),
    moisture: Joi.string().valid('dry', 'wet', 'slippery', 'normal')
  }),
  tongueBody: Joi.object({
    spots: Joi.boolean().default(false),
    spotLocation: Joi.string(),
    teethMarks: Joi.boolean().default(false),
    veins: Joi.string().valid('normal', 'engorged', 'purple')
  }),
  imageUrl: Joi.string().uri(),
  notes: Joi.string()
});

/**
 * 体质评估记录验证模式
 * @type {Object}
 */
const constitutionAssessmentSchema = Joi.object({
  primaryConstitution: Joi.string().required(),
  secondaryConstitutions: Joi.array().items(Joi.string()),
  scores: Joi.object({
    balanced: Joi.number().min(0).max(100),
    qiDeficiency: Joi.number().min(0).max(100),
    yangDeficiency: Joi.number().min(0).max(100),
    yinDeficiency: Joi.number().min(0).max(100),
    phlegmDampness: Joi.number().min(0).max(100),
    dampHeat: Joi.number().min(0).max(100),
    bloodStasis: Joi.number().min(0).max(100),
    qiStagnation: Joi.number().min(0).max(100),
    specialConstitution: Joi.number().min(0).max(100)
  }),
  recommendations: Joi.object({
    diet: Joi.array().items(Joi.string()),
    lifestyle: Joi.array().items(Joi.string()),
    exercise: Joi.array().items(Joi.string()),
    environment: Joi.array().items(Joi.string()),
    mentalHealth: Joi.array().items(Joi.string())
  }),
  assessmentMethod: Joi.string().valid('questionnaire', 'professional', 'self-assessment'),
  questionnaire: Joi.object(),
  notes: Joi.string()
});

/**
 * 创建健康记录
 * @param {Object} data - 健康记录数据
 * @returns {Object} 验证后的健康记录对象
 */
function createHealthRecord(data) {
  const { error, value } = healthRecordSchema.validate(data);
  if (error) {
    throw new Error(`健康记录验证失败: ${error.message}`);
  }
  
  // 根据记录类型验证特定数据
  const { type, data: recordData } = value;
  
  switch (type) {
    case HealthRecordType.VITAL_SIGNS:
      validateSpecificSchema(recordData, vitalSignsSchema, '生命体征');
      break;
    case HealthRecordType.SLEEP:
      validateSpecificSchema(recordData, sleepSchema, '睡眠记录');
      break;
    case HealthRecordType.DIET:
      validateSpecificSchema(recordData, dietSchema, '饮食记录');
      break;
    case HealthRecordType.TCM_DIAGNOSIS:
      validateSpecificSchema(recordData, tcmDiagnosisSchema, '中医诊断');
      break;
    case HealthRecordType.PULSE_DIAGNOSIS:
      validateSpecificSchema(recordData, pulseDiagnosisSchema, '脉诊记录');
      break;
    case HealthRecordType.TONGUE_DIAGNOSIS:
      validateSpecificSchema(recordData, tongueDiagnosisSchema, '舌诊记录');
      break;
    case HealthRecordType.CONSTITUTION_ASSESSMENT:
      validateSpecificSchema(recordData, constitutionAssessmentSchema, '体质评估');
      break;
  }
  
  return value;
}

/**
 * 验证特定类型的记录数据
 * @param {Object} data - 记录数据
 * @param {Joi.ObjectSchema} schema - 验证模式
 * @param {string} recordType - 记录类型名称
 */
function validateSpecificSchema(data, schema, recordType) {
  const { error } = schema.validate(data);
  if (error) {
    throw new Error(`${recordType}验证失败: ${error.message}`);
  }
}

/**
 * 更新健康记录
 * @param {Object} record - 已有健康记录
 * @param {Object} updates - 更新数据
 * @returns {Object} 更新后的健康记录
 */
function updateHealthRecord(record, updates) {
  const updatedRecord = {
    ...record,
    ...updates,
    updatedAt: new Date()
  };
  
  const { error, value } = healthRecordSchema.validate(updatedRecord);
  if (error) {
    throw new Error(`健康记录更新验证失败: ${error.message}`);
  }
  
  return value;
}

/**
 * 验证健康记录ID
 * @param {string} id - 健康记录ID
 * @returns {boolean} 是否为有效ID
 */
function isValidHealthRecordId(id) {
  const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidPattern.test(id);
}

module.exports = {
  HealthRecordType,
  healthRecordSchema,
  vitalSignsSchema,
  sleepSchema,
  dietSchema,
  tcmDiagnosisSchema,
  pulseDiagnosisSchema,
  tongueDiagnosisSchema,
  constitutionAssessmentSchema,
  createHealthRecord,
  updateHealthRecord,
  isValidHealthRecordId
}; 
/**
 * 模拟数据辅助工具
 * 用于生成测试和开发环境的模拟数据
 */

/**
 * 生成模拟ID
 * @returns {string} 生成的模拟ID
 */
function generateMockId() {
  return 'mock_' + Math.random().toString(36).substring(2, 15);
}

/**
 * 生成随机整数
 * @param {number} min - 最小值（包含）
 * @param {number} max - 最大值（包含）
 * @returns {number} 生成的随机整数
 */
function getRandomInt(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * 从数组中随机选择一项
 * @param {Array} array - 源数组
 * @returns {*} 随机选择的数组项
 */
function getRandomArrayItem(array) {
  return array[Math.floor(Math.random() * array.length)];
}

/**
 * 生成模拟日期时间
 * @param {number} daysOffset - 相对于当前时间的天数偏移
 * @returns {string} ISO格式的日期时间字符串
 */
function generateMockDate(daysOffset = 0) {
  const date = new Date();
  if (daysOffset) {
    date.setDate(date.getDate() + daysOffset);
  }
  return date.toISOString();
}

/**
 * 随机生成模拟体质类型
 * @returns {string} 体质类型
 */
function generateRandomConstitution() {
  const constitutionTypes = [
    '平和质', '气虚质', '阳虚质', '阴虚质', 
    '痰湿质', '湿热质', '血瘀质', '气郁质', '特禀质'
  ];
  return getRandomArrayItem(constitutionTypes);
}

/**
 * 生成模拟活动类型
 * @returns {string} 活动类型
 */
function generateRandomActivityType() {
  const activityTypes = [
    'walking', 'running', 'cycling', 'swimming', 
    'yoga', 'meditation', 'exercise', 'stretching', 'other'
  ];
  return getRandomArrayItem(activityTypes);
}

/**
 * 生成模拟营养素数据
 * @returns {Object} 营养素数据
 */
function generateMockNutrients() {
  return {
    protein: getRandomInt(40, 100),
    fat: getRandomInt(30, 80),
    carbohydrates: getRandomInt(100, 300),
    fiber: getRandomInt(10, 30),
    vitaminA: getRandomInt(500, 1500),
    vitaminC: getRandomInt(40, 120),
    vitaminD: getRandomInt(5, 15),
    vitaminE: getRandomInt(5, 15),
    calcium: getRandomInt(500, 1200),
    iron: getRandomInt(8, 20),
    potassium: getRandomInt(2000, 4000),
    magnesium: getRandomInt(200, 400),
    zinc: getRandomInt(5, 15)
  };
}

/**
 * 生成模拟情绪数据
 * @returns {Object} 情绪数据
 */
function generateMockMood() {
  const moodTypes = ['happy', 'calm', 'anxious', 'sad', 'energetic', 'tired', 'irritable', 'excited'];
  const selectedMood = getRandomArrayItem(moodTypes);
  
  return {
    type: selectedMood,
    intensity: getRandomInt(1, 10),
    timestamp: new Date().toISOString()
  };
}

/**
 * 生成模拟健康指标
 * @returns {Object} 健康指标数据
 */
function generateMockHealthMetrics() {
  return {
    heartRate: getRandomInt(60, 100),
    bloodPressure: {
      systolic: getRandomInt(100, 140),
      diastolic: getRandomInt(60, 90)
    },
    bloodOxygen: getRandomInt(95, 100),
    respirationRate: getRandomInt(12, 20),
    temperature: (36 + Math.random()).toFixed(1)
  };
}

module.exports = {
  generateMockId,
  getRandomInt,
  getRandomArrayItem,
  generateMockDate,
  generateRandomConstitution,
  generateRandomActivityType,
  generateMockNutrients,
  generateMockMood,
  generateMockHealthMetrics
}; 
/**
 * 日常活动模型
 * 定义日常活动相关的数据库表结构和操作
 */

const { v4: uuidv4 } = require('uuid');

// 表名
const ACTIVITIES_TABLE = 'user_daily_activities';
const ACTIVITY_METRICS_TABLE = 'user_activity_metrics';
const ACTIVITY_GOALS_TABLE = 'user_activity_goals';

/**
 * 创建活动表的SQL语句
 */
const createActivitiesTableSQL = `
  CREATE TABLE IF NOT EXISTS ${ACTIVITIES_TABLE} (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    type VARCHAR(50) NOT NULL,
    type_label VARCHAR(50),
    description TEXT,
    duration INTEGER NOT NULL COMMENT '活动持续时间(分钟)',
    distance DECIMAL(10, 2) COMMENT '活动距离(公里)',
    calories INTEGER COMMENT '消耗卡路里',
    start_time DATETIME,
    end_time DATETIME,
    location_name VARCHAR(100),
    location_coordinates JSON,
    heart_rate JSON COMMENT '心率数据',
    pace JSON COMMENT '配速数据',
    mood VARCHAR(50),
    notes TEXT,
    tags JSON,
    data JSON COMMENT '其他活动数据',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_type (type),
    INDEX idx_start_time (start_time),
    INDEX idx_created_at (created_at)
  )
`;

/**
 * 创建活动指标表的SQL语句
 */
const createActivityMetricsTableSQL = `
  CREATE TABLE IF NOT EXISTS ${ACTIVITY_METRICS_TABLE} (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    date DATE NOT NULL,
    period VARCHAR(10) NOT NULL COMMENT '日/周/月',
    total_activities INTEGER DEFAULT 0,
    total_duration INTEGER DEFAULT 0 COMMENT '总时间(分钟)',
    total_distance DECIMAL(10, 2) DEFAULT 0 COMMENT '总距离(公里)',
    total_calories INTEGER DEFAULT 0,
    activity_breakdown JSON COMMENT '活动类型细分',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX idx_user_period (user_id, period),
    INDEX idx_date (date),
    UNIQUE INDEX idx_user_date_period (user_id, date, period)
  )
`;

/**
 * 创建活动目标表的SQL语句
 */
const createActivityGoalsTableSQL = `
  CREATE TABLE IF NOT EXISTS ${ACTIVITY_GOALS_TABLE} (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    period VARCHAR(10) NOT NULL COMMENT '日/周/月',
    type VARCHAR(50) NOT NULL COMMENT '目标类型',
    target_value DECIMAL(10, 2) NOT NULL COMMENT '目标值',
    unit VARCHAR(20) NOT NULL COMMENT '单位',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    progress DECIMAL(5, 2) DEFAULT 0 COMMENT '完成百分比',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX idx_user_period (user_id, period),
    INDEX idx_status (status),
    INDEX idx_date_range (start_date, end_date)
  )
`;

/**
 * 创建活动表结构
 */
async function createTables(db) {
  await db.query(createActivitiesTableSQL);
  await db.query(createActivityMetricsTableSQL);
  await db.query(createActivityGoalsTableSQL);
}

/**
 * 创建活动记录的模式定义
 */
const activitySchema = {
  id: { type: 'string', required: false },
  user_id: { type: 'string', required: true },
  type: { 
    type: 'string', 
    required: true, 
    enum: ['walking', 'running', 'cycling', 'swimming', 'yoga', 'meditation', 'exercise', 'other']
  },
  type_label: { type: 'string', required: false },
  description: { type: 'string', required: true },
  duration: { type: 'number', required: true, min: 1 },
  distance: { type: 'number', required: false },
  calories: { type: 'number', required: false },
  start_time: { type: 'date', required: false },
  end_time: { type: 'date', required: false },
  location_name: { type: 'string', required: false },
  location_coordinates: { type: 'object', required: false },
  heart_rate: { type: 'object', required: false },
  pace: { type: 'object', required: false },
  mood: { type: 'string', required: false },
  notes: { type: 'string', required: false },
  tags: { type: 'array', required: false },
  data: { type: 'object', required: false }
};

/**
 * 创建活动指标记录的模式定义
 */
const activityMetricsSchema = {
  id: { type: 'string', required: false },
  user_id: { type: 'string', required: true },
  date: { type: 'date', required: true },
  period: { type: 'string', required: true, enum: ['day', 'week', 'month'] },
  total_activities: { type: 'number', required: false },
  total_duration: { type: 'number', required: false },
  total_distance: { type: 'number', required: false },
  total_calories: { type: 'number', required: false },
  activity_breakdown: { type: 'array', required: false }
};

/**
 * 创建活动目标记录的模式定义
 */
const activityGoalSchema = {
  id: { type: 'string', required: false },
  user_id: { type: 'string', required: true },
  period: { type: 'string', required: true, enum: ['day', 'week', 'month'] },
  type: { 
    type: 'string', 
    required: true, 
    enum: ['steps', 'distance', 'duration', 'calories', 'activities']
  },
  target_value: { type: 'number', required: true },
  unit: { type: 'string', required: true },
  start_date: { type: 'date', required: true },
  end_date: { type: 'date', required: true },
  status: { 
    type: 'string', 
    required: false, 
    enum: ['active', 'completed', 'failed', 'cancelled']
  },
  progress: { type: 'number', required: false, min: 0, max: 100 }
};

/**
 * 将活动数据转换为数据库格式
 * @param {Object} activityData - 活动数据
 * @returns {Object} 数据库格式的活动数据
 */
function formatActivityForDb(activityData) {
  const formattedData = { ...activityData };
  
  // 将驼峰命名转换为下划线命名
  if (formattedData.userId) {
    formattedData.user_id = formattedData.userId;
    delete formattedData.userId;
  }
  
  if (formattedData.typeLabel) {
    formattedData.type_label = formattedData.typeLabel;
    delete formattedData.typeLabel;
  }
  
  if (formattedData.startTime) {
    formattedData.start_time = formattedData.startTime;
    delete formattedData.startTime;
  }
  
  if (formattedData.endTime) {
    formattedData.end_time = formattedData.endTime;
    delete formattedData.endTime;
  }
  
  if (formattedData.locationName) {
    formattedData.location_name = formattedData.locationName;
    delete formattedData.locationName;
  }
  
  if (formattedData.locationCoordinates) {
    formattedData.location_coordinates = JSON.stringify(formattedData.locationCoordinates);
    delete formattedData.locationCoordinates;
  }
  
  if (formattedData.heartRate) {
    formattedData.heart_rate = JSON.stringify(formattedData.heartRate);
    delete formattedData.heartRate;
  }
  
  // 处理JSON字段
  if (formattedData.tags && Array.isArray(formattedData.tags)) {
    formattedData.tags = JSON.stringify(formattedData.tags);
  }
  
  if (formattedData.data && typeof formattedData.data === 'object') {
    formattedData.data = JSON.stringify(formattedData.data);
  }
  
  return formattedData;
}

/**
 * 将数据库活动转换为API格式
 * @param {Object} dbActivity - 数据库活动记录
 * @returns {Object} API格式的活动数据
 */
function formatActivityForApi(dbActivity) {
  const formattedActivity = { ...dbActivity };
  
  // 将下划线命名转换为驼峰命名
  if (formattedActivity.user_id) {
    formattedActivity.userId = formattedActivity.user_id;
    delete formattedActivity.user_id;
  }
  
  if (formattedActivity.type_label) {
    formattedActivity.typeLabel = formattedActivity.type_label;
    delete formattedActivity.type_label;
  }
  
  if (formattedActivity.start_time) {
    formattedActivity.startTime = formattedActivity.start_time;
    delete formattedActivity.start_time;
  }
  
  if (formattedActivity.end_time) {
    formattedActivity.endTime = formattedActivity.end_time;
    delete formattedActivity.end_time;
  }
  
  if (formattedActivity.location_name) {
    formattedActivity.locationName = formattedActivity.location_name;
    delete formattedActivity.location_name;
  }
  
  if (formattedActivity.location_coordinates) {
    try {
      formattedActivity.locationCoordinates = JSON.parse(formattedActivity.location_coordinates);
    } catch (e) {
      formattedActivity.locationCoordinates = formattedActivity.location_coordinates;
    }
    delete formattedActivity.location_coordinates;
  }
  
  if (formattedActivity.heart_rate) {
    try {
      formattedActivity.heartRate = JSON.parse(formattedActivity.heart_rate);
    } catch (e) {
      formattedActivity.heartRate = formattedActivity.heart_rate;
    }
    delete formattedActivity.heart_rate;
  }
  
  // 解析JSON字段
  if (formattedActivity.tags && typeof formattedActivity.tags === 'string') {
    try {
      formattedActivity.tags = JSON.parse(formattedActivity.tags);
    } catch (e) {
      // 保持原样
    }
  }
  
  if (formattedActivity.data && typeof formattedActivity.data === 'string') {
    try {
      formattedActivity.data = JSON.parse(formattedActivity.data);
    } catch (e) {
      // 保持原样
    }
  }
  
  return formattedActivity;
}

module.exports = {
  ACTIVITIES_TABLE,
  ACTIVITY_METRICS_TABLE,
  ACTIVITY_GOALS_TABLE,
  createTables,
  activitySchema,
  activityMetricsSchema,
  activityGoalSchema,
  formatActivityForDb,
  formatActivityForApi
}; 
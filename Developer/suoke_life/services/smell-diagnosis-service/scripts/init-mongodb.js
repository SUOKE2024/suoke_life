/**
 * MongoDB 初始化脚本
 * 在MongoDB容器启动时自动执行，创建数据库结构和初始数据
 */

// 使用气味诊断数据库
db = db.getSiblingDB('smell-diagnosis');

// 创建集合
db.createCollection('smell_analyses');
db.createCollection('smell_diagnoses');
db.createCollection('device_recordings');
db.createCollection('sessions');

// 创建索引
db.smell_analyses.createIndex({ 'sessionId': 1 });
db.smell_analyses.createIndex({ 'userId': 1 });
db.smell_analyses.createIndex({ 'createdAt': 1 });

db.smell_diagnoses.createIndex({ 'sessionId': 1 });
db.smell_diagnoses.createIndex({ 'userId': 1 });
db.smell_diagnoses.createIndex({ 'createdAt': 1 });

db.device_recordings.createIndex({ 'deviceId': 1 });
db.device_recordings.createIndex({ 'sessionId': 1 });
db.device_recordings.createIndex({ 'createdAt': 1 });

db.sessions.createIndex({ 'userId': 1 });
db.sessions.createIndex({ 'createdAt': 1 });
db.sessions.createIndex({ 'status': 1 });

// 插入示例数据
db.smell_analyses.insertOne({
  _id: ObjectId(),
  sessionId: 'sample-session-1',
  userId: 'sample-user-1',
  deviceId: 'sample-device-1',
  recordingId: 'sample-recording-1',
  analysisData: {
    compounds: [
      { name: '乙醛', concentration: 0.42, unit: 'ppm' },
      { name: '氨', concentration: 0.78, unit: 'ppm' },
      { name: '丙酮', concentration: 0.31, unit: 'ppm' }
    ],
    odorCharacteristics: {
      intensity: 7,
      quality: '酸性',
      hedonics: -2
    }
  },
  status: 'completed',
  createdAt: new Date(),
  updatedAt: new Date()
});

db.smell_diagnoses.insertOne({
  _id: ObjectId(),
  sessionId: 'sample-session-1',
  userId: 'sample-user-1',
  analysisId: 'sample-analysis-1',
  diagnosisResults: {
    tcmImplications: [
      {
        pattern: '湿热内蕴',
        confidence: 0.85
      },
      {
        pattern: '肝郁气滞',
        confidence: 0.65
      }
    ],
    recommendations: [
      '建议清淡饮食，多喝水',
      '可适当食用薏米、绿豆等清热利湿的食物',
      '保持情绪舒畅，避免暴怒'
    ]
  },
  coordinatorSubmitted: true,
  createdAt: new Date(),
  updatedAt: new Date()
});

db.sessions.insertOne({
  _id: ObjectId(),
  sessionId: 'sample-session-1',
  userId: 'sample-user-1',
  status: 'completed',
  diagnoses: ['smell', 'look'],
  createdAt: new Date(),
  updatedAt: new Date()
});

// 创建用户
db.createUser({
  user: 'smell_service',
  pwd: 'smell_service_password',
  roles: [
    {
      role: 'readWrite',
      db: 'smell-diagnosis'
    }
  ]
});

print('MongoDB 初始化完成');
print('创建了以下集合:');
print('- smell_analyses');
print('- smell_diagnoses');
print('- device_recordings');
print('- sessions');
print('插入了示例数据和创建了必要的索引'); 
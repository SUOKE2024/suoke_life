/**
 * 四诊协调服务模拟器
 * 提供模拟的四诊协调服务响应，用于本地开发和测试
 */

const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(cors());
app.use(express.json());

// 健康检查端点
app.get('/health', (req, res) => {
  res.json({
    status: 'UP',
    service: 'diagnosis-coordinator-mock',
    timestamp: new Date().toISOString()
  });
});

// 获取当前活跃的诊断会话
app.get('/api/v1/diagnosis-sessions/active', (req, res) => {
  console.log('请求活跃诊断会话');
  
  // 模拟一些活跃的诊断会话
  const sessions = [
    {
      id: 'session-001',
      userId: 'user-123',
      startTime: new Date(Date.now() - 600000).toISOString(),
      status: 'IN_PROGRESS',
      completedDiagnoses: ['INQUIRY', 'OBSERVATION'],
      pendingDiagnoses: ['AUSCULTATION', 'TOUCH'],
      results: {
        INQUIRY: {
          timestamp: new Date(Date.now() - 300000).toISOString(),
          confidence: 0.87,
          symptoms: ['疲劳', '头痛', '失眠']
        },
        OBSERVATION: {
          timestamp: new Date(Date.now() - 120000).toISOString(),
          confidence: 0.92,
          facialFeatures: ['面色苍白', '眼圈发黑'],
          tongueCondition: '舌淡红，苔薄白'
        }
      }
    }
  ];
  
  res.json({
    success: true,
    data: sessions
  });
});

// 创建新的诊断会话
app.post('/api/v1/diagnosis-sessions', (req, res) => {
  console.log('创建新的诊断会话', req.body);
  
  const { userId } = req.body;
  
  if (!userId) {
    return res.status(400).json({
      success: false,
      error: 'userId是必需的'
    });
  }
  
  // 创建一个新的诊断会话
  const newSession = {
    id: `session-${Date.now().toString(36)}`,
    userId,
    startTime: new Date().toISOString(),
    status: 'INITIALIZED',
    completedDiagnoses: [],
    pendingDiagnoses: ['INQUIRY', 'OBSERVATION', 'AUSCULTATION', 'TOUCH'],
    results: {}
  };
  
  res.status(201).json({
    success: true,
    data: newSession
  });
});

// 获取诊断指令
app.get('/api/v1/diagnosis-instructions/:sessionId/:diagnosisType', (req, res) => {
  const { sessionId, diagnosisType } = req.params;
  console.log(`获取诊断指令: ${sessionId}, ${diagnosisType}`);
  
  // 根据诊断类型返回不同的指令
  let instructions;
  
  switch(diagnosisType.toUpperCase()) {
    case 'TOUCH':
      instructions = {
        title: '触诊指导',
        steps: [
          '请准备好在一个安静、温暖的环境进行触诊',
          '确保患者手腕暴露，避免过紧的衣物',
          '轻轻按压患者的寸口脉（桡动脉），感受脉象',
          '注意记录脉搏的频率、强度、节律和形态',
          '触摸患者皮肤，感知温度和湿度',
          '如有必要，可触诊其他部位如腹部，观察是否有压痛或异常'
        ],
        notes: '触诊过程应轻柔缓慢，注意患者反应'
      };
      break;
    case 'INQUIRY':
      instructions = {
        title: '问诊指导',
        steps: [
          '询问患者的主诉',
          '了解症状的发生时间、持续时间和特点',
          '询问患者的生活习惯、饮食情况',
          '了解患者的睡眠质量',
          '询问患者的情绪状态'
        ],
        notes: '问诊应尊重患者隐私，语气温和'
      };
      break;
    case 'OBSERVATION':
      instructions = {
        title: '望诊指导',
        steps: [
          '观察患者的面色',
          '查看患者的舌象',
          '观察患者的精神状态',
          '注意患者的体态和步态'
        ],
        notes: '望诊时注意光线应充足自然'
      };
      break;
    case 'AUSCULTATION':
      instructions = {
        title: '闻切指导',
        steps: [
          '聆听患者的呼吸声',
          '注意患者说话的声音特点',
          '注意是否有异常气味'
        ],
        notes: '环境应安静，避免干扰'
      };
      break;
    default:
      return res.status(400).json({
        success: false,
        error: '不支持的诊断类型'
      });
  }
  
  res.json({
    success: true,
    data: {
      sessionId,
      diagnosisType,
      instructions
    }
  });
});

// 提交诊断结果
app.post('/api/v1/diagnosis-results', (req, res) => {
  console.log('提交诊断结果', req.body);
  
  const { sessionId, diagnosisType, results } = req.body;
  
  if (!sessionId || !diagnosisType || !results) {
    return res.status(400).json({
      success: false,
      error: 'sessionId, diagnosisType和results都是必需的'
    });
  }
  
  // 模拟处理诊断结果
  setTimeout(() => {
    res.json({
      success: true,
      data: {
        sessionId,
        diagnosisType,
        status: 'PROCESSED',
        message: `${diagnosisType}诊断结果已成功处理`,
        timestamp: new Date().toISOString()
      }
    });
  }, 500);
});

// 获取整合的诊断报告
app.get('/api/v1/diagnosis-reports/:sessionId', (req, res) => {
  const { sessionId } = req.params;
  console.log(`获取诊断报告: ${sessionId}`);
  
  // 模拟诊断报告生成
  setTimeout(() => {
    const report = {
      sessionId,
      userId: 'user-123',
      timestamp: new Date().toISOString(),
      completionStatus: 'PARTIAL', // COMPLETE, PARTIAL
      diagnoses: {
        INQUIRY: {
          completed: true,
          timestamp: new Date(Date.now() - 300000).toISOString(),
          confidence: 0.87,
          findings: ['疲劳', '头痛', '失眠', '食欲不振']
        },
        OBSERVATION: {
          completed: true,
          timestamp: new Date(Date.now() - 120000).toISOString(),
          confidence: 0.92,
          findings: ['面色苍白', '眼圈发黑', '舌淡红，苔薄白']
        },
        AUSCULTATION: {
          completed: false,
          timestamp: null,
          confidence: 0,
          findings: []
        },
        TOUCH: {
          completed: true,
          timestamp: new Date().toISOString(),
          confidence: 0.85,
          findings: ['脉沉细', '皮肤干燥', '腹部无压痛']
        }
      },
      integratedAnalysis: {
        constitutionType: '气虚质',
        primaryPatterns: ['脾胃虚弱', '气血不足'],
        secondaryPatterns: ['肝郁气滞'],
        recommendations: [
          '调理脾胃，益气养血',
          '建议服用四君子汤或八珍汤调理',
          '保持规律作息，避免过度劳累',
          '饮食宜温热，避免生冷食物'
        ]
      }
    };
    
    res.json({
      success: true,
      data: report
    });
  }, 800);
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`四诊协调服务模拟器运行在 http://localhost:${PORT}`);
});
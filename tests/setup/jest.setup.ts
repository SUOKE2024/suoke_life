/**
 * Jest 测试环境设置
 * 配置全局测试环境和模拟
 */

import { jest } from '@jest/globals';

// 设置测试超时
jest.setTimeout(30000);

// 全局测试配置
global.console = {
  ...console,
  // 在测试中静默某些日志
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: console.warn,
  error: console.error,
};

// 模拟环境变量
process.env.NODE_ENV = 'test';
process.env.AGENTIC_AI_TEST_MODE = 'true';
process.env.LOG_LEVEL = 'error';

// 模拟性能API（如果不存在）
if (typeof performance === 'undefined') {
  global.performance = {
    now: jest.fn(() => Date.now()),
    mark: jest.fn(),
    measure: jest.fn(),
    getEntriesByName: jest.fn(() => []),
    getEntriesByType: jest.fn(() => []),
    clearMarks: jest.fn(),
    clearMeasures: jest.fn()
  } as any;
}

// 模拟 EventEmitter（如果需要）
import { EventEmitter } from 'events';
global.EventEmitter = EventEmitter;

// 设置全局错误处理
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});

// 模拟网络请求
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
    headers: new Map(),
  })
) as jest.MockedFunction<typeof fetch>;

// 模拟 WebSocket（如果需要）
global.WebSocket = jest.fn(() => ({
  send: jest.fn(),
  close: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  readyState: 1, // OPEN
})) as any;

// 模拟本地存储
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn(),
};
global.localStorage = localStorageMock;
global.sessionStorage = localStorageMock;

// 模拟 IndexedDB（如果需要）
global.indexedDB = {
  open: jest.fn(),
  deleteDatabase: jest.fn(),
  cmp: jest.fn(),
} as any;

// 模拟 Crypto API
global.crypto = {
  getRandomValues: jest.fn((arr) => {
    for (let i = 0; i < arr.length; i++) {
      arr[i] = Math.floor(Math.random() * 256);
    }
    return arr;
  }),
  randomUUID: jest.fn(() => 'test-uuid-' + Math.random().toString(36).substr(2, 9)),
  subtle: {
    encrypt: jest.fn(),
    decrypt: jest.fn(),
    sign: jest.fn(),
    verify: jest.fn(),
    digest: jest.fn(),
    generateKey: jest.fn(),
    importKey: jest.fn(),
    exportKey: jest.fn(),
  }
} as any;

// 模拟 TextEncoder/TextDecoder
global.TextEncoder = class TextEncoder {
  encode(input: string): Uint8Array {
    return new Uint8Array(Buffer.from(input, 'utf8'));
  }
};

global.TextDecoder = class TextDecoder {
  decode(input: Uint8Array): string {
    return Buffer.from(input).toString('utf8');
  }
};

// 设置测试数据库连接（模拟）
global.testDatabase = {
  connect: jest.fn(() => Promise.resolve()),
  disconnect: jest.fn(() => Promise.resolve()),
  query: jest.fn(() => Promise.resolve([])),
  transaction: jest.fn((callback) => callback({
    query: jest.fn(() => Promise.resolve([])),
    commit: jest.fn(() => Promise.resolve()),
    rollback: jest.fn(() => Promise.resolve()),
  })),
};

// 模拟 Redis 连接
global.testRedis = {
  get: jest.fn(() => Promise.resolve(null)),
  set: jest.fn(() => Promise.resolve('OK')),
  del: jest.fn(() => Promise.resolve(1)),
  exists: jest.fn(() => Promise.resolve(0)),
  expire: jest.fn(() => Promise.resolve(1)),
  flushall: jest.fn(() => Promise.resolve('OK')),
};

// 模拟消息队列
global.testMessageQueue = {
  publish: jest.fn(() => Promise.resolve()),
  subscribe: jest.fn(() => Promise.resolve()),
  unsubscribe: jest.fn(() => Promise.resolve()),
  close: jest.fn(() => Promise.resolve()),
};

// 模拟文件系统操作
global.testFileSystem = {
  readFile: jest.fn(() => Promise.resolve('')),
  writeFile: jest.fn(() => Promise.resolve()),
  exists: jest.fn(() => Promise.resolve(true)),
  mkdir: jest.fn(() => Promise.resolve()),
  rmdir: jest.fn(() => Promise.resolve()),
};

// 设置测试用的智能体模拟
global.mockAgents = {
  xiaoai: {
    id: 'xiaoai',
    name: '小艾',
    type: 'health_consultant',
    capabilities: ['consultation', 'communication', 'emergency_response'],
    status: 'active',
    processTask: jest.fn(() => Promise.resolve({
      success: true,
      result: { advice: '测试建议' },
      confidence: 0.85,
      executionTime: 500
    }))
  },
  xiaoke: {
    id: 'xiaoke',
    name: '小克',
    type: 'tcm_specialist',
    capabilities: ['tcm_diagnosis', 'five_diagnosis', 'prescription'],
    status: 'active',
    processTask: jest.fn(() => Promise.resolve({
      success: true,
      result: { 
        diagnosis: '气虚血瘀',
        prescription: '补中益气汤加减',
        confidence: 0.9
      },
      confidence: 0.9,
      executionTime: 1200
    }))
  },
  laoke: {
    id: 'laoke',
    name: '老克',
    type: 'elderly_specialist',
    capabilities: ['chronic_disease', 'elderly_care', 'medication_management'],
    status: 'active',
    processTask: jest.fn(() => Promise.resolve({
      success: true,
      result: {
        riskAssessment: 'moderate',
        recommendations: ['定期监测', '药物调整'],
        monitoringPlan: {}
      },
      confidence: 0.88,
      executionTime: 800
    }))
  },
  soer: {
    id: 'soer',
    name: '索儿',
    type: 'lifestyle_optimizer',
    capabilities: ['lifestyle_advice', 'nutrition', 'exercise', 'wellness'],
    status: 'active',
    processTask: jest.fn(() => Promise.resolve({
      success: true,
      result: {
        lifestylePlan: {},
        nutritionAdvice: {},
        exerciseRecommendations: {}
      },
      confidence: 0.82,
      executionTime: 600
    }))
  }
};

// 设置测试工具模拟
global.mockTools = {
  five_diagnosis_system: {
    id: 'five_diagnosis_system',
    name: '五诊系统',
    type: 'diagnostic_tool',
    execute: jest.fn(() => Promise.resolve({
      wang: { complexion: '面色红润', tongue: '舌红苔薄' },
      wen: { voice: '声音洪亮', breathing: '呼吸平稳' },
      wen2: { sleep: '睡眠良好', appetite: '食欲正常' },
      qie: { pulse: '脉象平和', abdomen: '腹部正常' },
      suan: { constitution: '平和质', syndrome: '无明显证候' }
    }))
  },
  symptom_analyzer: {
    id: 'symptom_analyzer',
    name: '症状分析器',
    type: 'analysis_tool',
    execute: jest.fn(() => Promise.resolve({
      analysis: '症状分析结果',
      severity: 'moderate',
      recommendations: ['建议1', '建议2']
    }))
  },
  tcm_analyzer: {
    id: 'tcm_analyzer',
    name: '中医分析器',
    type: 'tcm_tool',
    execute: jest.fn(() => Promise.resolve({
      syndrome: '气血两虚',
      constitution: '气虚质',
      treatment: '补气养血'
    }))
  }
};

// 清理函数
global.testCleanup = {
  clearAllMocks: () => {
    jest.clearAllMocks();
    
    // 重置模拟对象
    Object.values(global.mockAgents).forEach(agent => {
      agent.processTask.mockClear();
    });
    
    Object.values(global.mockTools).forEach(tool => {
      tool.execute.mockClear();
    });
  },
  
  resetTestData: () => {
    // 重置测试数据
    global.testDatabase.query.mockClear();
    global.testRedis.get.mockClear();
    global.testRedis.set.mockClear();
  }
};

// 在每个测试前自动清理
beforeEach(() => {
  global.testCleanup.clearAllMocks();
});

// 在每个测试后清理
afterEach(() => {
  global.testCleanup.resetTestData();
});

// 导出测试工具函数
export const createMockTask = (overrides = {}) => ({
  id: 'test_task_' + Math.random().toString(36).substr(2, 9),
  type: 'consultation',
  description: '测试任务',
  priority: 'medium',
  context: {
    userId: 'test_user',
    sessionId: 'test_session',
    currentChannel: 'health',
    userProfile: {
      id: 'test_user',
      age: 30,
      gender: 'male',
      height: 175,
      weight: 70,
      medicalHistory: [],
      allergies: [],
      currentMedications: []
    },
    medicalHistory: [],
    currentSymptoms: [],
    environmentalFactors: {
      location: '北京',
      temperature: 25,
      humidity: 60,
      airQuality: 80,
      season: '夏季'
    },
    timestamp: new Date()
  },
  requirements: [],
  expectedOutcome: '测试结果',
  ...overrides
});

export const createMockUserProfile = (overrides = {}) => ({
  id: 'test_user_' + Math.random().toString(36).substr(2, 9),
  age: 30,
  gender: 'male',
  height: 175,
  weight: 70,
  medicalHistory: [],
  allergies: [],
  currentMedications: [],
  ...overrides
});

export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const expectEventually = async (assertion: () => void, timeout = 5000) => {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    try {
      assertion();
      return;
    } catch (error) {
      await waitFor(100);
    }
  }
  assertion(); // 最后一次尝试，如果失败会抛出错误
};
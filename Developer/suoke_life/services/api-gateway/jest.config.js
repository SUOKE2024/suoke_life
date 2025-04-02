/**
 * Jest配置文件
 */
module.exports = {
  // 测试环境
  testEnvironment: 'node',
  
  // 测试文件匹配模式
  testMatch: [
    '**/test/**/*.test.js'
  ],
  
  // 测试覆盖率配置
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/index.js'
  ],
  
  // 覆盖率阈值
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  
  // 覆盖率报告输出目录
  coverageDirectory: 'coverage',
  
  // 报告输出格式
  coverageReporters: ['text', 'lcov', 'clover'],
  
  // JUnit报告设置 (用于CI/CD)
  reporters: [
    'default',
    ['jest-junit', {
      outputDirectory: 'test-results',
      outputName: 'jest-junit.xml'
    }]
  ],
  
  // 测试超时时间
  testTimeout: 10000,
  
  // 在每个测试文件执行前运行的代码
  setupFilesAfterEnv: ['<rootDir>/test/setup.js'],
  
  // 测试文件序列化快照
  snapshotSerializers: [],

  // 模块别名
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  }
};
module.exports = {
  // 基础配置
  preset: 'react-native',
  testEnvironment: 'node',
  
  // 测试文件匹配模式
  testMatch: [
    '<rootDir>/src/__tests__/e2e/**/*.test.{js,jsx,ts,tsx}',
  ],
  
  // 模块路径映射 - 使用正确的属性名
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@components/(.*)$': '<rootDir>/src/components/$1',
    '^@screens/(.*)$': '<rootDir>/src/screens/$1',
    '^@services/(.*)$': '<rootDir>/src/services/$1',
    '^@utils/(.*)$': '<rootDir>/src/utils/$1',
    '^@types/(.*)$': '<rootDir>/src/types/$1',
    '^@agents/(.*)$': '<rootDir>/src/agents/$1',
    '^@core/(.*)$': '<rootDir>/src/core/$1',
  },
  
  // 设置文件
  setupFilesAfterEnv: [
    '<rootDir>/src/__tests__/setup/e2e-setup-simple.ts',
  ],
  
  // 转换配置
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  
  // 模块文件扩展名
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  
  // 忽略的路径
  testPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/android/',
    '<rootDir>/ios/',
  ],
  
  // 覆盖率配置
  collectCoverage: false,
  
  // 超时设置
  testTimeout: 300000, // 5分钟
  
  // 报告器配置
  reporters: ['default'],
  
  // 全局变量
  globals: {
    __DEV__: true,
    __TEST__: true,
  },
  
  // 模拟配置
  clearMocks: true,
  resetMocks: true,
  restoreMocks: true,
  
  // 详细输出
  verbose: true,
  
  // 检测打开的句柄
  detectOpenHandles: true,
  
  // 强制退出
  forceExit: true,
  
  // 最大工作进程数
  maxWorkers: 2,
  
  // 缓存目录
  cacheDirectory: '<rootDir>/.jest-cache/e2e',
}; 
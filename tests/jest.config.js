/**
 * Jest 配置文件
 * 为 Agentic AI 测试套件配置测试环境
 */

module.exports = {
  // 测试环境
  testEnvironment: 'node',
  
  // 根目录
  rootDir: '../',
  
  // 测试文件匹配模式
  testMatch: [
    '<rootDir>/tests/**/*.test.ts',
    '<rootDir>/tests/**/*.test.js'
  ],
  
  // 忽略的测试文件
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/build/'
  ],
  
  // TypeScript 支持
  preset: 'ts-jest',
  
  // 模块文件扩展名
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  
  // 模块路径映射
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@tests/(.*)$': '<rootDir>/tests/$1',
    '^@core/(.*)$': '<rootDir>/src/core/$1',
    '^@agentic/(.*)$': '<rootDir>/src/core/agentic/$1'
  },
  
  // 转换配置
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
    '^.+\\.jsx?$': 'babel-jest'
  },
  
  // 设置文件
  setupFilesAfterEnv: [
    '<rootDir>/tests/setup/jest.setup.ts'
  ],
  
  // 覆盖率配置
  collectCoverage: true,
  collectCoverageFrom: [
    'src/core/agentic/**/*.ts',
    'src/core/agentic/**/*.tsx',
    '!src/core/agentic/**/*.d.ts',
    '!src/core/agentic/**/*.test.ts',
    '!src/core/agentic/**/*.spec.ts'
  ],
  coverageDirectory: '<rootDir>/tests/coverage',
  coverageReporters: [
    'text',
    'text-summary',
    'html',
    'lcov',
    'json'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 85,
      lines: 85,
      statements: 85
    },
    './src/core/agentic/AgenticWorkflowEngine.ts': {
      branches: 90,
      functions: 95,
      lines: 95,
      statements: 95
    },
    './src/core/agentic/ReflectionSystem.ts': {
      branches: 85,
      functions: 90,
      lines: 90,
      statements: 90
    }
  },
  
  // 测试超时
  testTimeout: 30000,
  
  // 全局变量
  globals: {
    'ts-jest': {
      tsconfig: {
        compilerOptions: {
          module: 'commonjs',
          target: 'es2020',
          lib: ['es2020'],
          allowJs: true,
          skipLibCheck: true,
          esModuleInterop: true,
          allowSyntheticDefaultImports: true,
          strict: true,
          forceConsistentCasingInFileNames: true,
          moduleResolution: 'node',
          resolveJsonModule: true,
          isolatedModules: true,
          noEmit: true,
          experimentalDecorators: true,
          emitDecoratorMetadata: true
        }
      }
    }
  },
  
  // 测试套件配置
  projects: [
    {
      displayName: 'Unit Tests',
      testMatch: ['<rootDir>/tests/agentic/**/*.test.ts'],
      testEnvironment: 'node'
    },
    {
      displayName: 'Integration Tests',
      testMatch: ['<rootDir>/tests/integration/**/*.test.ts'],
      testEnvironment: 'node',
      testTimeout: 60000
    },
    {
      displayName: 'Performance Tests',
      testMatch: ['<rootDir>/tests/performance/**/*.test.ts'],
      testEnvironment: 'node',
      testTimeout: 120000
    },
    {
      displayName: 'E2E Tests',
      testMatch: ['<rootDir>/tests/e2e/**/*.test.ts'],
      testEnvironment: 'node',
      testTimeout: 180000
    }
  ],
  
  // 报告器配置
  reporters: [
    'default',
    [
      'jest-html-reporters',
      {
        publicPath: '<rootDir>/tests/reports',
        filename: 'test-report.html',
        expand: true,
        hideIcon: false,
        pageTitle: 'Agentic AI Test Report',
        logoImgPath: undefined,
        inlineSource: false
      }
    ],
    [
      'jest-junit',
      {
        outputDirectory: '<rootDir>/tests/reports',
        outputName: 'junit.xml',
        ancestorSeparator: ' › ',
        uniqueOutputName: 'false',
        suiteNameTemplate: '{filepath}',
        classNameTemplate: '{classname}',
        titleTemplate: '{title}'
      }
    ]
  ],
  
  // 详细输出
  verbose: true,
  
  // 静默模式（在CI环境中使用）
  silent: process.env.CI === 'true',
  
  // 最大工作进程数
  maxWorkers: process.env.CI ? 2 : '50%',
  
  // 缓存配置
  cache: true,
  cacheDirectory: '<rootDir>/node_modules/.cache/jest',
  
  // 清除模拟
  clearMocks: true,
  restoreMocks: true,
  resetMocks: true,
  
  // 错误处理
  errorOnDeprecated: true,
  
  // 监视模式配置
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname'
  ],
  
  // 自定义匹配器
  setupFilesAfterEnv: [
    '<rootDir>/tests/setup/jest.setup.ts',
    '<rootDir>/tests/setup/custom-matchers.ts'
  ]
};
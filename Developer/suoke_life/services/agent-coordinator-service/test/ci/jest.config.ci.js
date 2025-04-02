/**
 * CI环境中使用的Jest配置文件
 * 设置更严格的覆盖率要求和适合CI的报告格式
 */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src/', '<rootDir>/test/'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest'
  },
  testRegex: '(/__tests__/.*|(\\.|/)(test|spec))\\.tsx?$',
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  
  // 收集覆盖率信息
  collectCoverage: true,
  coverageDirectory: '<rootDir>/coverage',
  
  // 覆盖率报告格式，适合CI环境
  coverageReporters: ['json', 'lcov', 'text', 'clover', 'cobertura'],
  
  // 覆盖率阈值 - CI环境中使用更严格的要求
  coverageThreshold: {
    global: {
      branches: 75,
      functions: 80,
      lines: 80,
      statements: 80
    },
    './src/controllers/': {
      branches: 85,
      functions: 90,
      lines: 90,
      statements: 90
    },
    './src/services/': {
      branches: 80,
      functions: 85,
      lines: 85,
      statements: 85
    }
  },
  
  // 收集覆盖率的文件范围
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/types/**',
    '!src/index.ts',
    '!**/node_modules/**'
  ],
  
  // 为JUnit报告配置报告器，适合CI系统
  reporters: [
    'default',
    [
      'jest-junit',
      {
        outputDirectory: './reports',
        outputName: 'jest-junit.xml',
        classNameTemplate: '{classname}',
        titleTemplate: '{title}',
        ancestorSeparator: ' › ',
        usePathForSuiteName: 'true'
      }
    ]
  ],
  
  // 并行化测试以加快CI中的测试执行
  maxWorkers: '50%',
  
  // 更详细的测试输出
  verbose: true,
  
  // 超时设置
  testTimeout: 30000,
  
  // CI模式 - 以非交互方式运行测试
  ci: true,
  
  // 首先运行失败的测试，加快发现错误
  bail: 0,
  
  // 自定义设置
  globals: {
    'ts-jest': {
      diagnostics: {
        warnOnly: true
      }
    }
  }
}; 
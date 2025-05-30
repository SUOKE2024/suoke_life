/**
 * 索克生活APP优化配置文件
 * 自定义优化选项和参数
 */

module.exports = {
  // 启用的优化模块
  enableCodeQuality: true,      // 代码质量优化
  enableTestCoverage: true,     // 测试覆盖率提升
  enablePerformance: true,      // 性能优化
  enableArchitecture: true,     // 架构优化

  // 后处理选项
  reinstallDependencies: false, // 是否重新安装依赖
  finalLintCheck: true,         // 最终代码检查
  runTests: false,              // 运行测试套件

  // 代码质量优化配置
  codeQuality: {
    autoFixESLint: true,        // 自动修复ESLint问题
    cleanUnusedImports: true,   // 清理未使用的导入
    fixHooksDependencies: true, // 修复React Hooks依赖
    optimizeComponents: true,   // 优化组件性能
    formatCode: true,            // 统一代码格式
  },

  // 测试覆盖率配置
  testCoverage: {
    generateMissingTests: true,     // 生成缺失的测试文件
    enhanceExistingTests: true,     // 增强现有测试
    generateIntegrationTests: true, // 生成集成测试
    generatePerformanceTests: true, // 生成性能测试
    updateTestConfig: true,         // 更新测试配置
    
    // 覆盖率目标
    coverageThreshold: {
      global: {
        branches: 70,
        functions: 70,
        lines: 70,
        statements: 70,
      },
      components: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80,
      },
      services: {
        branches: 75,
        functions: 75,
        lines: 75,
        statements: 75,
      },
      hooks: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80,
      },
    },
  },

  // 性能优化配置
  performance: {
    optimizeComponents: true,     // 组件性能优化
    optimizeImages: true,         // 图片资源优化
    optimizeCodeSplitting: true,  // 代码分割优化
    optimizeMemory: true,         // 内存优化
    optimizeNetworking: true,     // 网络请求优化
    optimizeStorage: true,        // 存储优化
    
    // 性能阈值
    thresholds: {
      renderTime: 100,      // 组件渲染时间 (ms)
      responseTime: 500,    // API响应时间 (ms)
      memoryUsage: 50 * 1024 * 1024, // 内存使用 (50MB)
      bundleSize: 10 * 1024 * 1024,   // 包大小 (10MB)
    },
  },

  // 架构优化配置
  architecture: {
    optimizeDirectoryStructure: true, // 优化目录结构
    createBarrelExports: true,        // 创建统一导出文件
    optimizeDependencyInjection: true, // 优化依赖注入
    createConfigurationManager: true,  // 创建配置管理
    optimizeErrorHandling: true,      // 优化错误处理
    createTypeDefinitions: true,      // 创建类型定义
    generateArchitectureDoc: true,    // 生成架构文档
    
    // 目录结构
    requiredDirectories: [
      'src/core',
      'src/shared',
      'src/features',
      'src/infrastructure',
      'src/presentation',
    ],
  },

  // 备份配置
  backup: {
    enabled: true,                    // 启用备份
    itemsToBackup: [                 // 备份项目
      'src',
      'package.json',
      'tsconfig.json',
      '.eslintrc.js',
      'jest.config.js',
    ],
    backupLocation: '.backup',         // 备份位置
  },

  // 报告配置
  reporting: {
    generateDetailedReport: true,     // 生成详细报告
    saveReportToFile: true,          // 保存报告到文件
    reportFormat: 'json',            // 报告格式 (json|html|markdown)
    includeTimestamps: true,         // 包含时间戳
    includeMetrics: true,             // 包含性能指标
  },

  // 环境配置
  environment: {
    development: {
      enableDebugMode: true,
      verboseLogging: true,
      skipMinification: true,
    },
    production: {
      enableDebugMode: false,
      verboseLogging: false,
      skipMinification: false,
      enableOptimizations: true,
    },
  },

  // 智能体特定优化
  agents: {
    xiaoai: {
      optimizeResponseTime: true,
      enableCaching: true,
      maxCacheSize: 10 * 1024 * 1024, // 10MB
    },
    xiaoke: {
      optimizeResponseTime: true,
      enableCaching: true,
      maxCacheSize: 10 * 1024 * 1024, // 10MB
    },
    laoke: {
      optimizeResponseTime: true,
      enableCaching: true,
      maxCacheSize: 10 * 1024 * 1024, // 10MB
    },
    soer: {
      optimizeResponseTime: true,
      enableCaching: true,
      maxCacheSize: 10 * 1024 * 1024, // 10MB
    },
  },

  // 五诊系统优化
  fiveDiagnosis: {
    optimizeImageProcessing: true,    // 优化图像处理
    optimizeAudioProcessing: true,    // 优化音频处理
    enableOfflineMode: true,          // 启用离线模式
    cacheResults: true,               // 缓存诊断结果
    maxCacheAge: 24 * 60 * 60 * 1000, // 缓存有效期 (24小时)
  },

  // 区块链优化
  blockchain: {
    optimizeTransactions: true,       // 优化交易处理
    enableBatching: true,            // 启用批处理
    cacheValidation: true,           // 缓存验证结果
    maxBatchSize: 100,                // 最大批处理大小
  },
}; 
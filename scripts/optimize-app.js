#!/usr/bin/env node

/**
 * 索克生活APP - 主优化脚本
 * 统一管理所有优化任务的入口脚本
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 导入优化器
const CodeQualityOptimizer = require('./code-quality-optimizer');
const TestCoverageEnhancer = require('./test-coverage-enhancer');
const PerformanceOptimizer = require('./performance-optimizer');
const ArchitectureOptimizer = require('./architecture-optimizer');

class AppOptimizer {
  constructor() {
    this.startTime = Date.now();
    this.optimizations = [];
    this.errors = [];
    this.config = this.loadConfig();
  }

  /**
   * 运行完整的应用优化
   */
  async optimize() {
    console.log('🚀 索克生活APP全面优化开始...\n');
    console.log('=' .repeat(60));
    
    try {
      // 1. 预检查
      await this.preCheck();
      
      // 2. 代码质量优化
      if (this.config.enableCodeQuality) {
        await this.runCodeQualityOptimization();
      }
      
      // 3. 测试覆盖率提升
      if (this.config.enableTestCoverage) {
        await this.runTestCoverageEnhancement();
      }
      
      // 4. 性能优化
      if (this.config.enablePerformance) {
        await this.runPerformanceOptimization();
      }
      
      // 5. 架构优化
      if (this.config.enableArchitecture) {
        await this.runArchitectureOptimization();
      }
      
      // 6. 后处理
      await this.postProcess();
      
      // 7. 生成综合报告
      this.generateComprehensiveReport();
      
    } catch (error) {
      console.error('❌ 优化过程中出现严重错误:', error.message);
      this.errors.push(`严重错误: ${error.message}`);
      process.exit(1);
    }
  }

  /**
   * 预检查
   */
  async preCheck() {
    console.log('🔍 执行预检查...\n');
    
    // 检查Node.js版本
    const nodeVersion = process.version;
    console.log(`Node.js版本: ${nodeVersion}`);
    
    // 检查npm版本
    try {
      const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
      console.log(`npm版本: ${npmVersion}`);
    } catch (error) {
      this.errors.push('npm版本检查失败');
    }
    
    // 检查项目依赖
    if (!fs.existsSync('package.json')) {
      throw new Error('package.json文件不存在');
    }
    
    // 检查源代码目录
    if (!fs.existsSync('src')) {
      throw new Error('src目录不存在');
    }
    
    // 创建备份
    await this.createBackup();
    
    console.log('✅ 预检查完成\n');
  }

  /**
   * 创建备份
   */
  async createBackup() {
    console.log('💾 创建项目备份...');
    
    const backupDir = path.join(__dirname, '../.backup');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupPath = path.join(backupDir, `backup-${timestamp}`);
    
    if (!fs.existsSync(backupDir)) {
      fs.mkdirSync(backupDir, { recursive: true });
    }
    
    try {
      // 备份关键文件和目录
      const itemsToBackup = ['src', 'package.json', 'tsconfig.json', '.eslintrc.js'];
      
      fs.mkdirSync(backupPath, { recursive: true });
      
      for (const item of itemsToBackup) {
        if (fs.existsSync(item)) {
          const stat = fs.statSync(item);
          if (stat.isDirectory()) {
            execSync(`cp -r ${item} ${backupPath}/`, { stdio: 'pipe' });
          } else {
            execSync(`cp ${item} ${backupPath}/`, { stdio: 'pipe' });
          }
        }
      }
      
      console.log(`✅ 备份已创建: ${backupPath}`);
      this.optimizations.push(`创建备份: ${backupPath}`);
    } catch (error) {
      console.log('⚠️  备份创建失败，继续优化过程');
      this.errors.push(`备份失败: ${error.message}`);
    }
  }

  /**
   * 运行代码质量优化
   */
  async runCodeQualityOptimization() {
    console.log('🔧 开始代码质量优化...\n');
    
    try {
      const optimizer = new CodeQualityOptimizer();
      await optimizer.optimize();
      this.optimizations.push('代码质量优化完成');
    } catch (error) {
      console.error('❌ 代码质量优化失败:', error.message);
      this.errors.push(`代码质量优化失败: ${error.message}`);
    }
    
    console.log('');
  }

  /**
   * 运行测试覆盖率提升
   */
  async runTestCoverageEnhancement() {
    console.log('🧪 开始测试覆盖率提升...\n');
    
    try {
      const enhancer = new TestCoverageEnhancer();
      await enhancer.enhance();
      this.optimizations.push('测试覆盖率提升完成');
    } catch (error) {
      console.error('❌ 测试覆盖率提升失败:', error.message);
      this.errors.push(`测试覆盖率提升失败: ${error.message}`);
    }
    
    console.log('');
  }

  /**
   * 运行性能优化
   */
  async runPerformanceOptimization() {
    console.log('⚡ 开始性能优化...\n');
    
    try {
      const optimizer = new PerformanceOptimizer();
      await optimizer.optimize();
      this.optimizations.push('性能优化完成');
    } catch (error) {
      console.error('❌ 性能优化失败:', error.message);
      this.errors.push(`性能优化失败: ${error.message}`);
    }
    
    console.log('');
  }

  /**
   * 运行架构优化
   */
  async runArchitectureOptimization() {
    console.log('🏗️  开始架构优化...\n');
    
    try {
      const optimizer = new ArchitectureOptimizer();
      await optimizer.optimize();
      this.optimizations.push('架构优化完成');
    } catch (error) {
      console.error('❌ 架构优化失败:', error.message);
      this.errors.push(`架构优化失败: ${error.message}`);
    }
    
    console.log('');
  }

  /**
   * 后处理
   */
  async postProcess() {
    console.log('🔄 执行后处理...\n');
    
    try {
      // 重新安装依赖
      if (this.config.reinstallDependencies) {
        console.log('📦 重新安装依赖...');
        execSync('npm install', { stdio: 'inherit' });
        this.optimizations.push('重新安装依赖');
      }
      
      // 运行最终的代码检查
      if (this.config.finalLintCheck) {
        console.log('🔍 执行最终代码检查...');
        try {
          execSync('npm run lint', { stdio: 'pipe' });
          this.optimizations.push('最终代码检查通过');
        } catch (error) {
          console.log('⚠️  最终代码检查发现问题，请手动修复');
          this.errors.push('最终代码检查失败');
        }
      }
      
      // 运行测试
      if (this.config.runTests) {
        console.log('🧪 运行测试套件...');
        try {
          execSync('npm test', { stdio: 'pipe' });
          this.optimizations.push('测试套件运行成功');
        } catch (error) {
          console.log('⚠️  部分测试失败，请检查测试结果');
          this.errors.push('测试套件运行失败');
        }
      }
      
    } catch (error) {
      console.error('❌ 后处理失败:', error.message);
      this.errors.push(`后处理失败: ${error.message}`);
    }
    
    console.log('✅ 后处理完成\n');
  }

  /**
   * 加载配置
   */
  loadConfig() {
    const defaultConfig = {
      enableCodeQuality: true,
      enableTestCoverage: true,
      enablePerformance: true,
      enableArchitecture: true,
      reinstallDependencies: false,
      finalLintCheck: true,
      runTests: false
    };

    // 尝试从配置文件加载
    const configPath = path.join(__dirname, '../optimize.config.js');
    if (fs.existsSync(configPath)) {
      try {
        const userConfig = require(configPath);
        return { ...defaultConfig, ...userConfig };
      } catch (error) {
        console.log('⚠️  配置文件加载失败，使用默认配置');
      }
    }

    return defaultConfig;
  }

  /**
   * 生成综合报告
   */
  generateComprehensiveReport() {
    const endTime = Date.now();
    const duration = Math.round((endTime - this.startTime) / 1000);
    
    console.log('\n' + '='.repeat(60));
    console.log('📊 索克生活APP优化综合报告');
    console.log('='.repeat(60));
    
    console.log(`⏱️  总耗时: ${duration}秒`);
    console.log(`✅ 成功完成的优化: ${this.optimizations.length}项`);
    console.log(`❌ 遇到的错误: ${this.errors.length}项`);
    
    if (this.optimizations.length > 0) {
      console.log('\n✅ 成功完成的优化:');
      this.optimizations.forEach((opt, index) => {
        console.log(`  ${index + 1}. ${opt}`);
      });
    }
    
    if (this.errors.length > 0) {
      console.log('\n❌ 遇到的错误:');
      this.errors.forEach((error, index) => {
        console.log(`  ${index + 1}. ${error}`);
      });
    }
    
    // 生成优化建议
    console.log('\n💡 后续建议:');
    console.log('  1. 运行 npm run lint 检查代码质量');
    console.log('  2. 运行 npm run test:coverage 检查测试覆盖率');
    console.log('  3. 运行 npm run build 验证构建');
    console.log('  4. 查看生成的架构文档: docs/ARCHITECTURE.md');
    
    if (this.errors.length === 0) {
      console.log('\n🎉 恭喜！索克生活APP优化全部完成！');
    } else {
      console.log('\n⚠️  优化完成，但存在一些问题需要手动处理');
    }
    
    console.log('='.repeat(60));
    
    // 保存报告到文件
    this.saveReportToFile(duration);
  }

  /**
   * 保存报告到文件
   */
  saveReportToFile(duration) {
    const report = {
      timestamp: new Date().toISOString(),
      duration: duration,
      optimizations: this.optimizations,
      errors: this.errors,
      config: this.config
    };
    
    const reportPath = path.join(__dirname, '../optimization-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    console.log(`📄 详细报告已保存到: ${reportPath}`);
  }
}

// 处理命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {};
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    switch (arg) {
      case '--skip-code-quality':
        options.enableCodeQuality = false;
        break;
      case '--skip-test-coverage':
        options.enableTestCoverage = false;
        break;
      case '--skip-performance':
        options.enablePerformance = false;
        break;
      case '--skip-architecture':
        options.enableArchitecture = false;
        break;
      case '--reinstall-deps':
        options.reinstallDependencies = true;
        break;
      case '--run-tests':
        options.runTests = true;
        break;
      case '--help':
        console.log(`
索克生活APP优化脚本

用法: node scripts/optimize-app.js [选项]

选项:
  --skip-code-quality     跳过代码质量优化
  --skip-test-coverage    跳过测试覆盖率提升
  --skip-performance      跳过性能优化
  --skip-architecture     跳过架构优化
  --reinstall-deps        重新安装依赖
  --run-tests            运行测试套件
  --help                 显示帮助信息

示例:
  node scripts/optimize-app.js
  node scripts/optimize-app.js --skip-test-coverage --reinstall-deps
        `);
        process.exit(0);
    }
  }
  
  return options;
}

// 运行优化
if (require.main === module) {
  const options = parseArgs();
  const optimizer = new AppOptimizer();
  
  // 应用命令行选项
  Object.assign(optimizer.config, options);
  
  optimizer.optimize().catch(console.error);
}

module.exports = AppOptimizer; 
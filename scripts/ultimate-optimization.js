#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

/**
 * 终极优化脚本
 * 索克生活APP - 执行所有优化步骤的主控脚本
 */

class UltimateOptimizer {
  constructor() {
    this.results = [];
    this.startTime = Date.now();
    this.optimizationSteps = [
      {
        name: '文件扩展名修复',
        script: './scripts/fix-file-extensions.js',
        description: '修复包含JSX的.ts文件扩展名为.tsx',
        critical: true
      },
      {
        name: '高级语法修复',
        script: './scripts/advanced-syntax-fixer.js',
        description: '修复复杂的TypeScript语法错误',
        critical: true
      },
      {
        name: '代码质量提升',
        script: './scripts/code-quality-enhancer.js',
        description: '提升代码质量、类型安全和性能',
        critical: false
      },
      {
        name: 'TypeScript错误修复',
        script: './scripts/fix-typescript-errors.js',
        description: '智能修复TypeScript编译错误',
        critical: true
      },
      {
        name: '测试套件增强',
        script: './scripts/enhance-test-suite.js',
        description: '自动生成和增强测试用例',
        critical: false
      },
      {
        name: '性能监控集成',
        script: './scripts/integrate-performance-monitoring.js',
        description: '集成性能监控和报告',
        critical: false
      }
    ];
  }

  /**
   * 检查脚本是否存在
   */
  checkScriptExists(scriptPath) {
    return fs.existsSync(scriptPath);
  }

  /**
   * 执行单个优化步骤
   */
  async executeStep(step, index) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`🔧 步骤 ${index + 1}/${this.optimizationSteps.length}: ${step.name}`);
    console.log(`📝 描述: ${step.description}`);
    console.log(`🔥 关键性: ${step.critical ? '关键' : '可选'}`);
    console.log(`${'='.repeat(60)}`);

    const stepStartTime = Date.now();
    
    try {
      // 检查脚本是否存在
      if (!this.checkScriptExists(step.script)) {
        throw new Error(`脚本文件不存在: ${step.script}`);
      }

      // 执行脚本
      console.log(`🚀 执行脚本: ${step.script}`);
      const output = execSync(`node ${step.script}`, {
        cwd: process.cwd(),
        encoding: 'utf8',
        maxBuffer: 1024 * 1024 * 10 // 10MB buffer
      });

      const duration = Date.now() - stepStartTime;
      
      this.results.push({
        step: step.name,
        status: 'success',
        duration,
        output: output.slice(-1000), // 保留最后1000字符
        critical: step.critical
      });

      console.log(`✅ ${step.name} 完成 (耗时: ${(duration / 1000).toFixed(2)}秒)`);
      return true;

    } catch (error) {
      const duration = Date.now() - stepStartTime;
      
      this.results.push({
        step: step.name,
        status: 'failed',
        duration,
        error: error.message,
        critical: step.critical
      });

      console.error(`❌ ${step.name} 失败 (耗时: ${(duration / 1000).toFixed(2)}秒)`);
      console.error(`错误信息: ${error.message}`);
      
      if (step.critical) {
        console.error(`⚠️  关键步骤失败，但继续执行后续步骤...`);
      }
      
      return false;
    }
  }

  /**
   * 分析TypeScript错误
   */
  analyzeTypeScriptErrors() {
    try {
      execSync('npx tsc --noEmit --skipLibCheck', { 
        stdio: 'pipe',
        cwd: process.cwd()
      });
      return 0;
    } catch (error) {
      const output = error.stdout ? error.stdout.toString() : error.stderr.toString();
      const errorLines = output.split('\n').filter(line => line.includes('error TS'));
      return errorLines.length;
    }
  }

  /**
   * 运行代码质量检查
   */
  runQualityChecks() {
    const checks = [];
    
    try {
      // TypeScript检查
      const tsErrors = this.analyzeTypeScriptErrors();
      checks.push({
        name: 'TypeScript',
        errors: tsErrors,
        status: tsErrors === 0 ? 'pass' : 'fail'
      });
    } catch (error) {
      checks.push({
        name: 'TypeScript',
        status: 'error',
        message: 'TypeScript检查失败'
      });
    }

    return checks;
  }

  /**
   * 生成优化报告
   */
  generateOptimizationReport() {
    const totalDuration = Date.now() - this.startTime;
    const successfulSteps = this.results.filter(r => r.status === 'success').length;
    const failedSteps = this.results.filter(r => r.status === 'failed').length;
    const criticalFailures = this.results.filter(r => r.status === 'failed' && r.critical).length;

    console.log('\n' + '='.repeat(80));
    console.log('🎯 终极优化完成报告');
    console.log('='.repeat(80));
    
    console.log(`⏱️  总耗时: ${(totalDuration / 1000 / 60).toFixed(2)} 分钟`);
    console.log(`📊 总步骤: ${this.optimizationSteps.length}`);
    console.log(`✅ 成功步骤: ${successfulSteps}`);
    console.log(`❌ 失败步骤: ${failedSteps}`);
    console.log(`🔥 关键失败: ${criticalFailures}`);
    console.log(`📈 成功率: ${((successfulSteps / this.optimizationSteps.length) * 100).toFixed(1)}%`);

    // 显示各步骤详情
    console.log('\n📋 步骤执行详情:');
    this.results.forEach((result, index) => {
      const icon = result.status === 'success' ? '✅' : '❌';
      const critical = result.critical ? '🔥' : '📝';
      console.log(`  ${icon} ${critical} ${result.step} (${(result.duration / 1000).toFixed(2)}秒)`);
      if (result.status === 'failed') {
        console.log(`      错误: ${result.error}`);
      }
    });

    // 运行最终质量检查
    console.log('\n🔍 最终质量检查:');
    const qualityChecks = this.runQualityChecks();
    qualityChecks.forEach(check => {
      const icon = check.status === 'pass' ? '✅' : check.status === 'fail' ? '❌' : '⚠️';
      console.log(`  ${icon} ${check.name}`);
      if (check.errors !== undefined) {
        console.log(`      错误: ${check.errors}, 警告: ${check.warnings || 0}`);
      }
      if (check.message) {
        console.log(`      信息: ${check.message}`);
      }
    });

    // 保存详细报告
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalDuration: totalDuration,
        totalSteps: this.optimizationSteps.length,
        successfulSteps,
        failedSteps,
        criticalFailures,
        successRate: (successfulSteps / this.optimizationSteps.length) * 100
      },
      steps: this.results,
      qualityChecks,
      recommendations: this.generateRecommendations()
    };

    fs.writeFileSync(
      'ULTIMATE_OPTIMIZATION_REPORT.json',
      JSON.stringify(report, null, 2),
      'utf8'
    );

    console.log('\n📄 详细报告已保存到: ULTIMATE_OPTIMIZATION_REPORT.json');
    
    // 显示建议
    const recommendations = this.generateRecommendations();
    if (recommendations.length > 0) {
      console.log('\n💡 优化建议:');
      recommendations.forEach((rec, index) => {
        console.log(`  ${index + 1}. ${rec}`);
      });
    }

    // 显示下一步行动
    console.log('\n🚀 下一步行动:');
    if (criticalFailures > 0) {
      console.log('  1. 优先修复关键步骤的失败问题');
    }
    if (qualityChecks.some(c => c.status === 'fail')) {
      console.log('  2. 解决代码质量检查中发现的问题');
    }
    console.log('  3. 运行完整的测试套件验证修复效果');
    console.log('  4. 考虑手动审查复杂的语法错误');
    console.log('  5. 更新项目文档和开发指南');
  }

  /**
   * 生成优化建议
   */
  generateRecommendations() {
    const recommendations = [];
    const failedSteps = this.results.filter(r => r.status === 'failed');
    
    if (failedSteps.length > 0) {
      recommendations.push('检查失败步骤的错误日志，手动修复关键问题');
    }
    
    if (failedSteps.some(s => s.step.includes('TypeScript'))) {
      recommendations.push('考虑逐步迁移到更严格的TypeScript配置');
    }
    
    if (failedSteps.some(s => s.step.includes('测试'))) {
      recommendations.push('建立更完善的测试策略和CI/CD流程');
    }
    
    recommendations.push('定期运行优化脚本以保持代码质量');
    recommendations.push('建立代码审查流程以防止质量回退');
    
    return recommendations;
  }

  /**
   * 执行终极优化
   */
  async optimize() {
    console.log('🚀 开始索克生活APP终极优化...\n');
    console.log(`📅 开始时间: ${new Date().toLocaleString()}`);
    console.log(`📁 项目路径: ${process.cwd()}`);
    console.log(`🔧 优化步骤: ${this.optimizationSteps.length} 个`);

    // 检查项目环境
    console.log('\n🔍 检查项目环境...');
    try {
      const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      console.log(`📦 项目名称: ${packageJson.name}`);
      console.log(`📋 项目版本: ${packageJson.version}`);
    } catch (error) {
      console.warn('⚠️  无法读取package.json');
    }

    // 执行优化前的基线检查
    console.log('\n📊 执行基线检查...');
    const initialErrors = this.analyzeTypeScriptErrors();
    console.log(`🔍 初始TypeScript错误数量: ${initialErrors}`);

    // 执行所有优化步骤
    for (let i = 0; i < this.optimizationSteps.length; i++) {
      await this.executeStep(this.optimizationSteps[i], i);
      
      // 在关键步骤后进行中间检查
      if (this.optimizationSteps[i].critical) {
        const currentErrors = this.analyzeTypeScriptErrors();
        console.log(`📈 当前TypeScript错误数量: ${currentErrors}`);
      }
    }

    // 生成最终报告
    this.generateOptimizationReport();
    
    console.log('\n🎉 终极优化完成！');
    console.log('感谢使用索克生活APP优化工具！');
  }
}

// 执行优化
if (require.main === module) {
  const optimizer = new UltimateOptimizer();
  optimizer.optimize().catch(error => {
    console.error('❌ 终极优化执行失败:', error);
    process.exit(1);
  });
}

module.exports = UltimateOptimizer; 
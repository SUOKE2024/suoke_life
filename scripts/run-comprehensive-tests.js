#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');

console.log('🧪 开始运行综合测试套件...\n');

// 测试配置
const testSuites = [
  {
    name: '单元测试',
    command: 'npm test -- --testPathPattern="__tests__" --passWithNoTests',
    description: '运行所有单元测试'
  },
  {
    name: '集成测试',
    command: 'npm test -- --testPathPattern="integration" --passWithNoTests',
    description: '运行集成测试'
  },
  {
    name: '覆盖率测试',
    command: 'npm test -- --coverage --passWithNoTests',
    description: '生成测试覆盖率报告'
  }
];

// 运行测试套件
async function runTestSuite(suite) {
  console.log(`🔍 ${suite.name}: ${suite.description}`);
  console.log(`📝 命令: ${suite.command}\n`);

  try {
    const startTime = Date.now();
    const output = execSync(suite.command, { 
      encoding: 'utf8',
      stdio: 'pipe',
      maxBuffer: 1024 * 1024 * 10 // 10MB buffer
    });
    const duration = Date.now() - startTime;

    console.log(`✅ ${suite.name} 完成 (${duration}ms)`);
    
    // 提取关键信息
    if (output.includes('Tests:')) {
      const testResults = output.match(/Tests:\s+(\d+)\s+passed/);
      if (testResults) {
        console.log(`   📊 通过测试: ${testResults[1]}个`);
      }
    }

    if (output.includes('Coverage')) {
      const coverageMatch = output.match(/All files\s+\|\s+([\d.]+)/);
      if (coverageMatch) {
        console.log(`   📈 覆盖率: ${coverageMatch[1]}%`);
      }
    }

    return {
      success: true,
      duration,
      output: output.substring(0, 500) // 只保留前500字符
    };

  } catch (error) {
    console.log(`❌ ${suite.name} 失败`);
    console.log(`   错误: ${error.message.substring(0, 200)}...`);
    
    return {
      success: false,
      error: error.message.substring(0, 500)
    };
  }
}

// 主执行函数
async function main() {
  const results = [];
  let totalDuration = 0;
  let successCount = 0;

  console.log('=' .repeat(60));
  console.log('🚀 开始执行测试套件');
  console.log('=' .repeat(60));

  for (const suite of testSuites) {
    const result = await runTestSuite(suite);
    results.push({
      name: suite.name,
      ...result
    });

    if (result.success) {
      successCount++;
      totalDuration += result.duration || 0;
    }

    console.log(''); // 空行分隔
  }

  // 生成测试报告
  console.log('=' .repeat(60));
  console.log('📊 测试结果总结');
  console.log('=' .repeat(60));

  results.forEach((result, index) => {
    const status = result.success ? '✅' : '❌';
    const duration = result.duration ? `(${result.duration}ms)` : '';
    console.log(`${index + 1}. ${status} ${result.name} ${duration}`);
  });

  console.log(`\n📈 总体统计:`);
  console.log(`   成功: ${successCount}/${testSuites.length}`);
  console.log(`   成功率: ${Math.round(successCount/testSuites.length*100)}%`);
  console.log(`   总耗时: ${totalDuration}ms`);

  // 保存测试报告
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      total: testSuites.length,
      success: successCount,
      failed: testSuites.length - successCount,
      successRate: Math.round(successCount/testSuites.length*100),
      totalDuration
    },
    results
  };

  try {
    if (!fs.existsSync('reports')) {
      fs.mkdirSync('reports', { recursive: true });
    }
    
    const reportPath = `reports/test-report-${new Date().toISOString().split('T')[0]}.json`;
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n📋 详细报告已保存到: ${reportPath}`);
  } catch (error) {
    console.log('⚠️  无法保存测试报告');
  }

  // 检查覆盖率文件
  if (fs.existsSync('coverage/coverage-summary.json')) {
    try {
      const coverage = JSON.parse(fs.readFileSync('coverage/coverage-summary.json', 'utf8'));
      console.log('\n📊 覆盖率详情:');
      console.log(`   语句覆盖率: ${coverage.total.statements.pct}%`);
      console.log(`   分支覆盖率: ${coverage.total.branches.pct}%`);
      console.log(`   函数覆盖率: ${coverage.total.functions.pct}%`);
      console.log(`   行覆盖率: ${coverage.total.lines.pct}%`);
    } catch (error) {
      console.log('⚠️  无法读取覆盖率报告');
    }
  }

  console.log('\n🎉 综合测试完成！');
  
  if (successCount === testSuites.length) {
    console.log('✨ 所有测试套件都通过了！');
    process.exit(0);
  } else {
    console.log('⚠️  部分测试失败，请检查错误信息');
    process.exit(1);
  }
}

// 运行主函数
main().catch(error => {
  console.error('❌ 测试执行过程中发生错误:', error);
  process.exit(1);
}); 
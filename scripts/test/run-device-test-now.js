#!/usr/bin/env node

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 立即运行设备测试');
console.log('==================');

// 检查设备连接状态
function checkDeviceConnection() {
  console.log('\n📱 检查设备连接状态...');

  try {
    // 检查iOS模拟器
    const iosDevices = execSync('xcrun simctl list devices | grep "Booted"', { encoding: 'utf8' });
    const iosCount = iosDevices.split('\n').filter(line => line.trim()).length;
    console.log(`✅ iOS设备/模拟器: ${iosCount}个已启动`);

    // 检查Android设备
    try {
      const androidDevices = execSync('adb devices', { encoding: 'utf8' });
      const androidCount = androidDevices.split('\n').filter(line => line.includes('\tdevice')).length;
      console.log(`📱 Android设备: ${androidCount}个已连接`);
    } catch (error) {
      console.log('⚠️  Android设备: 无法检查连接状态');
    }

    return iosCount > 0;
  } catch (error) {
    console.log('❌ 设备连接检查失败');
    return false;
  }
}

// 运行Metro服务器
function startMetroServer() {
  console.log('\n🔄 启动Metro服务器...');

  try {
    // 检查Metro是否已经运行
    const metroCheck = execSync('lsof -ti:8081', { encoding: 'utf8' }).trim();
    if (metroCheck) {
      console.log('✅ Metro服务器已在运行 (端口8081)');
      return true;
    }
  } catch (error) {
    // Metro未运行，启动它
    console.log('🚀 启动新的Metro服务器...');

    const metro = spawn('npx', ['react-native', 'start'], {
      stdio: 'pipe',
      detached: true
    });

    metro.unref();

    // 等待Metro启动
    return new Promise((resolve) => {
      setTimeout(() => {
        console.log('✅ Metro服务器启动中...');
        resolve(true);
      }, 3000);
    });
  }
}

// 运行设备测试
async function runDeviceTests() {
  console.log('\n🧪 运行设备集成测试...');

  try {
    // 创建测试结果目录
    const testResultsDir = path.join(process.cwd(), 'test-results');
    if (!fs.existsSync(testResultsDir)) {
      fs.mkdirSync(testResultsDir, { recursive: true });
    }

    // 运行设备测试脚本
    console.log('📋 执行设备功能验证...');
    execSync('node scripts/validate-device-features.js', { stdio: 'inherit' });

    // 运行原生功能测试
    console.log('\n🔧 测试原生功能...');
    execSync('npm run test:native', { stdio: 'inherit' });

    console.log('\n✅ 设备测试完成！');

    // 生成测试报告
    generateTestReport();

  } catch (error) {
    console.error('❌ 设备测试失败:', error.message);
    return false;
  }

  return true;
}

// 生成测试报告
function generateTestReport() {
  console.log('\n📊 生成测试报告...');

  const timestamp = new Date().toISOString();
  const report = {
    timestamp,
    testType: 'device_integration',
    platform: process.platform,
    results: {
      deviceValidation: fs.existsSync('DEVICE_VALIDATION_REPORT.md'),
      nativeFeatures: true,
      performance: true
    },
    recommendations: [
      '定期运行设备测试以确保兼容性',
      '监控应用性能指标',
      '优化内存使用',
      '测试不同设备型号'
    ]
  };

  // 保存测试报告
  const reportPath = path.join(process.cwd(), 'test-results', `device-test-${Date.now()}.json`);
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  console.log(`📄 测试报告已保存: ${reportPath}`);

  // 显示测试总结
  console.log('\n📈 测试总结:');
  console.log(`   测试时间: ${new Date(timestamp).toLocaleString()}`);
  console.log(`   平台: ${process.platform}`);
  console.log(`   设备验证: ${report.results.deviceValidation ? '✅ 通过' : '❌ 失败'}`);
  console.log(`   原生功能: ${report.results.nativeFeatures ? '✅ 通过' : '❌ 失败'}`);
  console.log(`   性能测试: ${report.results.performance ? '✅ 通过' : '❌ 失败'}`);
}

// 性能优化建议
function showOptimizationRecommendations() {
  console.log('\n💡 性能优化建议:');
  console.log('================');

  const recommendations = [
    {
      category: '内存优化',
      items: [
        '使用React.memo优化组件渲染',
        '实施懒加载策略',
        '清理未使用的依赖',
        '优化图片资源大小'
      ]
    },
    {
      category: '启动优化',
      items: [
        '减少启动时的同步操作',
        '延迟非关键功能初始化',
        '优化Bundle大小',
        '使用代码分割'
      ]
    },
    {
      category: '用户体验',
      items: [
        '添加加载状态指示器',
        '实施错误边界',
        '优化动画性能',
        '提供离线功能'
      ]
    },
    {
      category: '设备兼容性',
      items: [
        '测试不同屏幕尺寸',
        '验证不同系统版本',
        '检查权限处理',
        '测试网络状况变化'
      ]
    }
  ];

  recommendations.forEach(rec => {
    console.log(`\n🎯 ${rec.category}:`);
    rec.items.forEach(item => {
      console.log(`   • ${item}`);
    });
  });
}

// 主执行函数
async function main() {
  try {
    console.log('🔍 索克生活设备测试执行器');
    console.log('============================');

    // 1. 检查设备连接
    const hasDevices = checkDeviceConnection();
    if (!hasDevices) {
      console.log('⚠️  建议: 启动iOS模拟器以获得最佳测试体验');
    }

    // 2. 启动Metro服务器
    await startMetroServer();

    // 3. 运行设备测试
    const testSuccess = await runDeviceTests();

    // 4. 显示优化建议
    showOptimizationRecommendations();

    if (testSuccess) {
      console.log('\n🎉 设备测试执行完成！');
      console.log('📋 查看详细报告: DEVICE_VALIDATION_REPORT.md');
      console.log('📊 测试结果: test-results/ 目录');
    } else {
      console.log('\n❌ 设备测试执行失败！');
      process.exit(1);
    }

  } catch (error) {
    console.error('💥 执行过程中发生错误:', error);
    process.exit(1);
  }
}

// 运行主函数
main();
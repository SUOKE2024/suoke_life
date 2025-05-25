#!/usr/bin/env node

const { execSync } = require('child_process');
const os = require('os');

console.log('🧪 索克生活快速测试\n');

const platform = os.platform();

function testMetroBundler() {
  console.log('🎯 测试 Metro bundler...');
  try {
    const status = execSync('curl -s http://localhost:8081/status', {
      encoding: 'utf8',
    });
    if (status.includes('packager-status:running')) {
      console.log('✅ Metro bundler 运行正常');
      return true;
    } else {
      console.log('❌ Metro bundler 未运行');
      return false;
    }
  } catch (error) {
    console.log('❌ 无法连接到 Metro bundler');
    return false;
  }
}

function testReactNativeConfig() {
  console.log('\n⚙️  测试 React Native 配置...');
  try {
    execSync('npx react-native config', { stdio: 'ignore' });
    console.log('✅ React Native 配置正常');
    return true;
  } catch (error) {
    console.log('❌ React Native 配置有问题');
    return false;
  }
}

function testIOSSimulators() {
  if (platform !== 'darwin') {
    console.log('\n🍎 iOS 模拟器测试: 跳过 (非 macOS 系统)');
    return false;
  }

  console.log('\n🍎 测试 iOS 模拟器...');
  try {
    const simulators = execSync('xcrun simctl list devices available', {
      encoding: 'utf8',
    });
    const iosDevices = simulators
      .split('\n')
      .filter((line) => line.includes('iPhone') || line.includes('iPad'));

    if (iosDevices.length > 0) {
      console.log(`✅ 找到 ${iosDevices.length} 个 iOS 模拟器`);

      // 测试启动一个模拟器
      const bootedDevices = simulators
        .split('\n')
        .filter((line) => line.includes('(Booted)'));
      if (bootedDevices.length > 0) {
        console.log(`✅ 有 ${bootedDevices.length} 个模拟器正在运行`);
      } else {
        console.log('⚠️  没有运行中的模拟器');
      }
      return true;
    } else {
      console.log('❌ 未找到 iOS 模拟器');
      return false;
    }
  } catch (error) {
    console.log('❌ 无法检查 iOS 模拟器');
    return false;
  }
}

function testProjectStructure() {
  console.log('\n📁 测试项目结构...');
  const fs = require('fs');

  const requiredFiles = [
    'package.json',
    'index.js',
    'app.json',
    'src/App.tsx',
    'android/app/build.gradle',
    'ios/Podfile',
  ];

  let allExists = true;
  requiredFiles.forEach((file) => {
    if (fs.existsSync(file)) {
      console.log(`✅ ${file}`);
    } else {
      console.log(`❌ ${file} 缺失`);
      allExists = false;
    }
  });

  return allExists;
}

function testDependencies() {
  console.log('\n📦 测试关键依赖...');
  try {
    const packageJson = require('../package.json');
    const criticalDeps = [
      'react',
      'react-native',
      '@react-navigation/native',
      '@react-navigation/bottom-tabs',
      'react-native-paper',
    ];

    let allPresent = true;
    criticalDeps.forEach((dep) => {
      if (packageJson.dependencies[dep]) {
        console.log(`✅ ${dep}: ${packageJson.dependencies[dep]}`);
      } else {
        console.log(`❌ ${dep} 缺失`);
        allPresent = false;
      }
    });

    return allPresent;
  } catch (error) {
    console.log('❌ 无法读取 package.json');
    return false;
  }
}

function generateReport(results) {
  console.log('\n📊 测试报告:');
  console.log('='.repeat(50));

  const passed = results.filter((r) => r.passed).length;
  const total = results.length;

  results.forEach((result) => {
    const status = result.passed ? '✅' : '❌';
    console.log(`${status} ${result.name}`);
  });

  console.log('='.repeat(50));
  console.log(`总计: ${passed}/${total} 项测试通过`);

  if (passed === total) {
    console.log('\n🎉 所有测试通过！项目已准备好进行开发。');
    console.log('\n🚀 下一步:');
    console.log('   1. 启动模拟器: npm run simulator list');
    console.log('   2. 启动开发环境: npm run dev');
    console.log('   3. 或者手动运行: npm run ios / npm run android');
  } else {
    console.log('\n⚠️  有些测试失败，请检查上面的错误信息。');
    console.log('\n🔧 建议的修复步骤:');
    if (!results.find((r) => r.name === 'Metro bundler').passed) {
      console.log('   • 启动 Metro: npm start');
    }
    if (!results.find((r) => r.name === 'React Native 配置').passed) {
      console.log('   • 检查 react-native.config.js');
    }
    if (!results.find((r) => r.name === '项目结构').passed) {
      console.log('   • 运行: npm run test:native');
    }
  }
}

// 运行所有测试
async function runAllTests() {
  const results = [
    { name: 'Metro bundler', passed: testMetroBundler() },
    { name: 'React Native 配置', passed: testReactNativeConfig() },
    { name: 'iOS 模拟器', passed: testIOSSimulators() },
    { name: '项目结构', passed: testProjectStructure() },
    { name: '关键依赖', passed: testDependencies() },
  ];

  generateReport(results);
}

runAllTests().catch((error) => {
  console.error('❌ 测试过程中出现错误:', error.message);
  process.exit(1);
});

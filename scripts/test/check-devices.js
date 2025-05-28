#!/usr/bin/env node

const { execSync, exec } = require('child_process');
const os = require('os');

console.log('🔍 检查索克生活测试设备环境...\n');

// 检查操作系统
const platform = os.platform();
console.log(`💻 操作系统: ${platform}`);

// 检查 Node.js 版本
const nodeVersion = process.version;
console.log(`📦 Node.js 版本: ${nodeVersion}`);

// 检查 React Native CLI
try {
  const rnVersion = execSync('npx react-native --version', {
    encoding: 'utf8',
  }).trim();
  console.log(`⚛️  React Native CLI: ${rnVersion}`);
} catch (error) {
  console.log('❌ React Native CLI 未安装');
}

console.log('\n🤖 Android 环境检查:');

// 检查 ANDROID_HOME
const androidHome = process.env.ANDROID_HOME;
if (androidHome) {
  console.log(`✅ ANDROID_HOME: ${androidHome}`);
} else {
  console.log('❌ ANDROID_HOME 环境变量未设置');
}

// 检查 ADB
try {
  const adbVersion = execSync('adb version', { encoding: 'utf8' });
  console.log('✅ ADB 已安装');

  // 检查连接的 Android 设备
  try {
    const devices = execSync('adb devices', { encoding: 'utf8' });
    const deviceLines = devices
      .split('\n')
      .filter(
        (line) => line.includes('device') && !line.includes('List of devices')
      );

    if (deviceLines.length > 0) {
      console.log(`📱 已连接的 Android 设备: ${deviceLines.length} 个`);
      deviceLines.forEach((line) => {
        const deviceId = line.split('\t')[0];
        console.log(`   - ${deviceId}`);
      });
    } else {
      console.log('📱 未检测到 Android 设备');
    }
  } catch (error) {
    console.log('❌ 无法检查 Android 设备');
  }
} catch (error) {
  console.log('❌ ADB 未安装或不在 PATH 中');
}

// 检查 Android 模拟器
try {
  const emulators = execSync('emulator -list-avds', {
    encoding: 'utf8',
  }).trim();
  if (emulators) {
    const emulatorList = emulators.split('\n').filter((line) => line.trim());
    console.log(`🎮 可用的 Android 模拟器: ${emulatorList.length} 个`);
    emulatorList.forEach((emulator) => {
      console.log(`   - ${emulator}`);
    });
  } else {
    console.log('🎮 未找到 Android 模拟器');
  }
} catch (error) {
  console.log('❌ 无法检查 Android 模拟器');
}

// iOS 检查 (仅限 macOS)
if (platform === 'darwin') {
  console.log('\n🍎 iOS 环境检查:');

  // 检查 Xcode
  try {
    const xcodeVersion = execSync('xcodebuild -version', { encoding: 'utf8' });
    console.log('✅ Xcode 已安装');
    console.log(`   版本: ${xcodeVersion.split('\n')[0]}`);
  } catch (error) {
    console.log('❌ Xcode 未安装');
  }

  // 检查 iOS 模拟器
  try {
    const simulators = execSync('xcrun simctl list devices available', {
      encoding: 'utf8',
    });
    const iosDevices = simulators
      .split('\n')
      .filter((line) => line.includes('iPhone') || line.includes('iPad'));

    if (iosDevices.length > 0) {
      console.log(`📱 可用的 iOS 模拟器: ${iosDevices.length} 个`);
      // 显示前5个设备
      iosDevices.slice(0, 5).forEach((device) => {
        const deviceName = device.trim().split('(')[0].trim();
        console.log(`   - ${deviceName}`);
      });
      if (iosDevices.length > 5) {
        console.log(`   ... 还有 ${iosDevices.length - 5} 个设备`);
      }
    } else {
      console.log('📱 未找到 iOS 模拟器');
    }
  } catch (error) {
    console.log('❌ 无法检查 iOS 模拟器');
  }

  // 检查 CocoaPods
  try {
    const podVersion = execSync('pod --version', { encoding: 'utf8' }).trim();
    console.log(`✅ CocoaPods: ${podVersion}`);
  } catch (error) {
    console.log('❌ CocoaPods 未安装');
  }
} else {
  console.log('\n🍎 iOS 环境检查: 跳过 (非 macOS 系统)');
}

console.log('\n🛠️  开发工具检查:');

// 检查 Metro bundler 状态
try {
  exec('curl -s http://localhost:8081/status', (error, stdout, stderr) => {
    if (!error && stdout.includes('packager-status:running')) {
      console.log('✅ Metro bundler 正在运行');
    } else {
      console.log('⚠️  Metro bundler 未运行 (使用 npm start 启动)');
    }
  });
} catch (error) {
  console.log('⚠️  无法检查 Metro bundler 状态');
}

// 检查 React Native Debugger
try {
  execSync('which react-native-debugger', { encoding: 'utf8' });
  console.log('✅ React Native Debugger 已安装');
} catch (error) {
  console.log('⚠️  React Native Debugger 未安装 (可选)');
}

// 检查 Flipper
try {
  execSync('which flipper', { encoding: 'utf8' });
  console.log('✅ Flipper 已安装');
} catch (error) {
  console.log('⚠️  Flipper 未安装 (可选)');
}

console.log('\n📋 快速启动命令:');
console.log('   npm start                    # 启动 Metro bundler');
console.log('   npm run android              # 运行 Android 应用');
if (platform === 'darwin') {
  console.log('   npm run ios                  # 运行 iOS 应用');
}
console.log('   npm run test:native          # 检查原生配置');

console.log('\n💡 提示:');
if (!androidHome) {
  console.log('   • 设置 ANDROID_HOME 环境变量');
}
if (platform === 'darwin') {
  console.log('   • 运行 "cd ios && pod install" 安装 iOS 依赖');
}
console.log('   • 确保至少有一个模拟器或真机连接');
console.log('   • 查看 docs/TESTING_ENVIRONMENT.md 获取详细设置指南');

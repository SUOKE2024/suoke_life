#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('🚀 启动索克生活开发环境...\n');

// 检查平台参数
const platform = process.argv[2] || 'metro';

// 项目根目录
const projectRoot = path.resolve(__dirname, '..');

// 启动Metro bundler
function startMetro() {
  console.log('📦 启动Metro Bundler...');
  const metro = spawn('npx', ['react-native', 'start'], {
    cwd: projectRoot,
    stdio: 'inherit',
    shell: true
  });

  metro.on('error', (error) => {
    console.error('❌ Metro启动失败:', error);
  });

  metro.on('close', (code) => {
    console.log(`Metro进程退出，代码: ${code}`);
  });

  return metro;
}

// 启动iOS模拟器
function startIOS() {
  console.log('📱 启动iOS模拟器...');
  const ios = spawn('npx', ['react-native', 'run-ios'], {
    cwd: projectRoot,
    stdio: 'inherit',
    shell: true
  });

  ios.on('error', (error) => {
    console.error('❌ iOS启动失败:', error);
  });

  return ios;
}

// 启动Android模拟器
function startAndroid() {
  console.log('🤖 启动Android模拟器...');
  const android = spawn('npx', ['react-native', 'run-android'], {
    cwd: projectRoot,
    stdio: 'inherit',
    shell: true
  });

  android.on('error', (error) => {
    console.error('❌ Android启动失败:', error);
  });

  return android;
}

// 主启动逻辑
async function main() {
  try {
    switch (platform) {
      case 'ios':
        startIOS();
        break;
      case 'android':
        startAndroid();
        break;
      case 'metro':
      default:
        startMetro();
        break;
    }
  } catch (error) {
    console.error('❌ 启动失败:', error);
    process.exit(1);
  }
}

// 处理退出信号
process.on('SIGINT', () => {
  console.log('\n👋 正在关闭开发服务器...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n👋 正在关闭开发服务器...');
  process.exit(0);
});

// 启动
main(); 
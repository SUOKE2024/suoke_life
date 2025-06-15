#!/usr/bin/env node

import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

// 检查平台参数
const platform = process.argv[2] || 'metro';

// 项目根目录
const projectRoot = path.resolve(__dirname, '..');

// 启动Metro bundler
function startMetro(): ChildProcess {
  const metro = spawn('npx', ['react-native', 'start'], {
    cwd: projectRoot,
    stdio: 'inherit',
    shell: true
  });

  metro.on('error', (error) => {
    console.error('Metro启动失败:', error);
  });

  metro.on('close', (code) => {
    console.log(`Metro进程退出，代码: ${code}`);
  });

  return metro;
}

// 启动iOS模拟器
function startIOS(): ChildProcess {
  const ios = spawn('npx', ['react-native', 'run-ios'], {
    cwd: projectRoot,
    stdio: 'inherit',
    shell: true
  });

  ios.on('error', (error) => {
    console.error('iOS模拟器启动失败:', error);
  });

  return ios;
}

// 启动Android模拟器
function startAndroid(): ChildProcess {
  const android = spawn('npx', ['react-native', 'run-android'], {
    cwd: projectRoot,
    stdio: 'inherit',
    shell: true
  });

  android.on('error', (error) => {
    console.error('Android模拟器启动失败:', error);
  });

  return android;
}

// 主函数
function main(): void {
  console.log('🚀 启动索克生活开发环境...');
  
  switch (platform) {
    case 'metro':
      console.log('📱 启动Metro bundler...');
      startMetro();
      break;
    case 'ios':
      console.log('🍎 启动iOS开发环境...');
      startIOS();
      break;
    case 'android':
      console.log('🤖 启动Android开发环境...');
      startAndroid();
      break;
    case 'all':
      console.log('🌟 启动完整开发环境...');
      startMetro();
      setTimeout(() => startIOS(), 3000);
      setTimeout(() => startAndroid(), 6000);
      break;
    default:
      console.log('❌ 未知平台参数');
      console.log('使用方法: npm run dev-start [metro|ios|android|all]');
      process.exit(1);
  }
}

// 检查是否为直接执行
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { startMetro, startIOS, startAndroid };
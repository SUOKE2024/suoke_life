#!/usr/bin/env node

/**
 * 开发环境配置脚本
 * 用于检查和配置React Native开发环境
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 检查并创建必要的目录结构
function ensureDirectories() {
  const dirs = [
    'android',
    'ios',
    'src/__tests__',
    'src/assets/fonts',
    'src/assets/icons',
    'src/assets/images',
  ];

  dirs.forEach((dir) => {
    if (!fs.existsSync(dir)) {
      console.log(`📁 创建目录: ${dir}`);
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

// 检查必要的配置文件
function checkConfigFiles() {
  const requiredFiles = [
    'package.json',
    'metro.config.js',
    'babel.config.js',
    'tsconfig.json',
    'jest.config.js',
    'index.js',
  ];

  console.log('\n📋 检查配置文件:');
  requiredFiles.forEach((file) => {
    if (fs.existsSync(file)) {
      console.log(`✅ ${file}`);
    } else {
      console.log(`❌ ${file} - 缺失`);
    }
  });
}

// 检查依赖安装状态
function checkDependencies() {
  console.log('\n📦 检查依赖:');

  try {
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    const nodeModulesExists = fs.existsSync('node_modules');

    if (nodeModulesExists) {
      console.log('✅ node_modules 已安装');
    } else {
      console.log('❌ node_modules 未安装，请运行 npm install');
    }

    // 检查重要依赖
    const importantDeps = [
      'react-native',
      '@react-navigation/native',
      '@reduxjs/toolkit',
      'react-redux',
    ];

    importantDeps.forEach((dep) => {
      if (packageJson.dependencies && packageJson.dependencies[dep]) {
        console.log(`✅ ${dep}: ${packageJson.dependencies[dep]}`);
      } else {
        console.log(`❌ ${dep} - 缺失`);
      }
    });
  } catch (error) {
    console.log('❌ 读取package.json失败');
  }
}

// 检查TypeScript编译
function checkTypeScript() {
  console.log('\n🔍 检查TypeScript编译:');

  try {
    execSync('npx tsc --noEmit', { stdio: 'pipe' });
    console.log('✅ TypeScript编译通过');
  } catch (error) {
    console.log('❌ TypeScript编译失败');
    console.log(error.stdout?.toString() || error.stderr?.toString());
  }
}

// 运行测试
function runTests() {
  console.log('\n🧪 运行测试:');

  try {
    const result = execSync('npm test -- --watchAll=false --passWithNoTests', {
      stdio: 'pipe',
      encoding: 'utf8',
    });
    console.log('✅ 测试通过');

    // 提取测试结果摘要
    const lines = result.split('\n');
    const summaryLine = lines.find((line) => line.includes('Test Suites:'));
    if (summaryLine) {
      console.log(`📊 ${summaryLine.trim()}`);
    }
  } catch (error) {
    console.log('❌ 测试失败');
    console.log(error.stdout || error.stderr);
  }
}

// 生成开发环境报告
function generateReport() {
  console.log('\n📋 开发环境状态报告:');

  const report = {
    timestamp: new Date().toISOString(),
    configFiles: {},
    dependencies: {},
    typescript: false,
    tests: false,
  };

  // 检查配置文件状态
  const configFiles = [
    'package.json',
    'metro.config.js',
    'babel.config.js',
    'tsconfig.json',
    'jest.config.js',
    'index.js',
  ];

  configFiles.forEach((file) => {
    report.configFiles[file] = fs.existsSync(file);
  });

  // 检查TypeScript
  try {
    execSync('npx tsc --noEmit', { stdio: 'pipe' });
    report.typescript = true;
  } catch {
    report.typescript = false;
  }

  // 检查测试
  try {
    execSync('npm test -- --watchAll=false --passWithNoTests', {
      stdio: 'pipe',
    });
    report.tests = true;
  } catch {
    report.tests = false;
  }

  // 保存报告
  fs.writeFileSync('dev-status.json', JSON.stringify(report, null, 2));
  console.log('📄 报告已保存到 dev-status.json');
}

// 主函数
function main() {
  console.log('🚀 索克生活 - 开发环境配置检查\n');

  ensureDirectories();
  checkConfigFiles();
  checkDependencies();
  checkTypeScript();
  runTests();
  generateReport();

  console.log('\n✨ 开发环境检查完成!');
  console.log('如果发现问题，请根据上述输出进行修复。');
  console.log('\n下一步建议:');
  console.log('1. 如果是新项目，运行: npx react-native init SuokeLifeApp');
  console.log('2. 配置开发环境: npx react-native doctor');
  console.log('3. 启动开发服务器: npm start');
}

// 运行脚本
if (require.main === module) {
  main();
}

module.exports = {
  ensureDirectories,
  checkConfigFiles,
  checkDependencies,
  checkTypeScript,
  runTests,
  generateReport,
};

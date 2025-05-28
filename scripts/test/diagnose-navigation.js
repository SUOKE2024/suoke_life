#!/usr/bin/env node

/**
 * 前端导航诊断脚本
 * 检查导航配置、组件导入导出、路由设置等问题
 */

const fs = require('fs');
const path = require('path');

// 颜色定义
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m'
};

function log(message, color = 'white') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkFileExists(filePath) {
  return fs.existsSync(filePath);
}

function readFileContent(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch (error) {
    return null;
  }
}

function checkExportPattern(content, componentName) {
  const patterns = [
    `export const ${componentName}`,
    `export default ${componentName}`,
    `export { ${componentName} }`,
    `export.*${componentName}`
  ];
  
  return patterns.some(pattern => {
    const regex = new RegExp(pattern);
    return regex.test(content);
  });
}

function checkImportPattern(content, componentName) {
  const patterns = [
    `import.*${componentName}.*from`,
    `import.*{.*${componentName}.*}.*from`,
    `import ${componentName} from`
  ];
  
  return patterns.some(pattern => {
    const regex = new RegExp(pattern);
    return regex.test(content);
  });
}

async function diagnoseNavigation() {
  log('🔍 前端导航诊断开始', 'cyan');
  log('================================', 'cyan');

  const issues = [];
  const warnings = [];

  // 1. 检查主要文件是否存在
  log('\n📁 检查核心文件...', 'blue');
  
  const coreFiles = [
    'src/App.tsx',
    'src/navigation/AppNavigator.tsx',
    'src/navigation/MainNavigator.tsx',
    'src/navigation/AuthNavigator.tsx',
    'index.js'
  ];

  for (const file of coreFiles) {
    if (checkFileExists(file)) {
      log(`✅ ${file}`, 'green');
    } else {
      log(`❌ ${file} - 文件不存在`, 'red');
      issues.push(`缺少核心文件: ${file}`);
    }
  }

  // 2. 检查屏幕组件
  log('\n📱 检查屏幕组件...', 'blue');
  
  const screens = [
    { name: 'HomeScreen', path: 'src/screens/main/HomeScreen.tsx', exportType: 'named' },
    { name: 'SuokeScreen', path: 'src/screens/suoke/SuokeScreen.tsx', exportType: 'default' },
    { name: 'LifeScreen', path: 'src/screens/life/LifeScreen.tsx', exportType: 'default' },
    { name: 'ProfileScreen', path: 'src/screens/profile/ProfileScreen.tsx', exportType: 'default' },
    { name: 'ExploreScreen', path: 'src/screens/explore/ExploreScreen.tsx', exportType: 'default' },
    { name: 'WelcomeScreen', path: 'src/screens/auth/WelcomeScreen.tsx', exportType: 'named' },
    { name: 'LoginScreen', path: 'src/screens/auth/LoginScreen.tsx', exportType: 'named' },
    { name: 'RegisterScreen', path: 'src/screens/auth/RegisterScreen.tsx', exportType: 'named' }
  ];

  for (const screen of screens) {
    if (checkFileExists(screen.path)) {
      const content = readFileContent(screen.path);
      if (content) {
        const hasExport = checkExportPattern(content, screen.name);
        if (hasExport) {
          log(`✅ ${screen.name} - 文件存在且有导出`, 'green');
        } else {
          log(`⚠️  ${screen.name} - 文件存在但导出可能有问题`, 'yellow');
          warnings.push(`${screen.name} 的导出模式可能不正确`);
        }
      } else {
        log(`❌ ${screen.name} - 无法读取文件内容`, 'red');
        issues.push(`无法读取 ${screen.path}`);
      }
    } else {
      log(`❌ ${screen.name} - 文件不存在: ${screen.path}`, 'red');
      issues.push(`缺少屏幕组件: ${screen.path}`);
    }
  }

  // 3. 检查导航器中的导入
  log('\n🧭 检查导航器导入...', 'blue');
  
  const mainNavigatorPath = 'src/navigation/MainNavigator.tsx';
  if (checkFileExists(mainNavigatorPath)) {
    const content = readFileContent(mainNavigatorPath);
    if (content) {
      const screenImports = [
        'HomeScreen',
        'SuokeScreen', 
        'LifeScreen',
        'ProfileScreen',
        'ExploreScreen'
      ];

      for (const screenName of screenImports) {
        const hasImport = checkImportPattern(content, screenName);
        if (hasImport) {
          log(`✅ ${screenName} - 已正确导入`, 'green');
        } else {
          log(`❌ ${screenName} - 导入缺失或错误`, 'red');
          issues.push(`MainNavigator 中缺少 ${screenName} 的导入`);
        }
      }
    }
  }

  // 4. 检查依赖包
  log('\n📦 检查导航相关依赖...', 'blue');
  
  const packageJsonPath = 'package.json';
  if (checkFileExists(packageJsonPath)) {
    const packageContent = readFileContent(packageJsonPath);
    if (packageContent) {
      const packageJson = JSON.parse(packageContent);
      const requiredDeps = [
        '@react-navigation/native',
        '@react-navigation/bottom-tabs',
        '@react-navigation/native-stack',
        '@react-navigation/stack',
        'react-native-screens',
        'react-native-safe-area-context'
      ];

      for (const dep of requiredDeps) {
        if (packageJson.dependencies[dep] || packageJson.devDependencies[dep]) {
          log(`✅ ${dep}`, 'green');
        } else {
          log(`❌ ${dep} - 依赖缺失`, 'red');
          issues.push(`缺少导航依赖: ${dep}`);
        }
      }
    }
  }

  // 5. 检查 TypeScript 配置
  log('\n⚙️  检查 TypeScript 配置...', 'blue');
  
  const tsconfigPath = 'tsconfig.json';
  if (checkFileExists(tsconfigPath)) {
    const content = readFileContent(tsconfigPath);
    if (content) {
      try {
        const tsconfig = JSON.parse(content);
        if (tsconfig.compilerOptions && tsconfig.compilerOptions.baseUrl) {
          log(`✅ TypeScript baseUrl 已配置: ${tsconfig.compilerOptions.baseUrl}`, 'green');
        } else {
          log(`⚠️  TypeScript baseUrl 未配置`, 'yellow');
          warnings.push('建议配置 TypeScript baseUrl 以支持绝对路径导入');
        }
      } catch (error) {
        log(`❌ tsconfig.json 解析失败`, 'red');
        issues.push('tsconfig.json 格式错误');
      }
    }
  }

  // 6. 检查常见的导航问题
  log('\n🔧 检查常见导航问题...', 'blue');
  
  // 检查是否有循环导入
  const appNavigatorPath = 'src/navigation/AppNavigator.tsx';
  if (checkFileExists(appNavigatorPath)) {
    const content = readFileContent(appNavigatorPath);
    if (content) {
      if (content.includes('isAuthenticated')) {
        log(`✅ 认证状态检查已实现`, 'green');
      } else {
        log(`⚠️  未发现认证状态检查`, 'yellow');
        warnings.push('建议实现认证状态检查以控制导航流程');
      }
    }
  }

  // 7. 生成诊断报告
  log('\n📊 诊断报告', 'magenta');
  log('================================', 'magenta');
  
  if (issues.length === 0 && warnings.length === 0) {
    log('🎉 恭喜！未发现导航相关问题', 'green');
  } else {
    if (issues.length > 0) {
      log(`\n❌ 发现 ${issues.length} 个问题:`, 'red');
      issues.forEach((issue, index) => {
        log(`   ${index + 1}. ${issue}`, 'red');
      });
    }
    
    if (warnings.length > 0) {
      log(`\n⚠️  发现 ${warnings.length} 个警告:`, 'yellow');
      warnings.forEach((warning, index) => {
        log(`   ${index + 1}. ${warning}`, 'yellow');
      });
    }
  }

  // 8. 提供修复建议
  if (issues.length > 0 || warnings.length > 0) {
    log('\n🛠️  修复建议:', 'cyan');
    log('================================', 'cyan');
    
    if (issues.some(issue => issue.includes('缺少屏幕组件'))) {
      log('1. 检查屏幕组件文件是否存在，路径是否正确', 'cyan');
    }
    
    if (issues.some(issue => issue.includes('导入'))) {
      log('2. 检查导入语句的语法，确保导出类型匹配（named vs default）', 'cyan');
    }
    
    if (issues.some(issue => issue.includes('依赖'))) {
      log('3. 运行 npm install 安装缺失的依赖', 'cyan');
    }
    
    log('4. 清理缓存: npm run clean', 'cyan');
    log('5. 重新安装依赖: rm -rf node_modules && npm install', 'cyan');
    log('6. 重启 Metro bundler: npm start -- --reset-cache', 'cyan');
  }

  log('\n🔍 诊断完成', 'cyan');
}

// 运行诊断
diagnoseNavigation().catch(error => {
  log(`诊断过程中发生错误: ${error.message}`, 'red');
  process.exit(1);
}); 
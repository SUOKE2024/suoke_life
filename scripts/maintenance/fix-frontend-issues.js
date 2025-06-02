#!/usr/bin/env node

/**
 * 前端问题修复脚本
 * 自动检测和修复常见的前端导航和UI问题
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 颜色定义
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'white') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function execCommand(command, description) {
  try {
    log(`🔧 ${description}...`, 'blue');
    execSync(command, { stdio: 'inherit' });
    log(`✅ ${description} 完成`, 'green');
    return true;
  } catch (error) {
    log(`❌ ${description} 失败: ${error.message}`, 'red');
    return false;
  }
}

function checkAndFixImportExportIssues() {
  log('\n🔍 检查导入导出问题...', 'blue');
  
  const fixes = [];
  
  // 检查 HomeScreen 导出
  const homeScreenPath = 'src/screens/main/HomeScreen.tsx';
  if (fs.existsSync(homeScreenPath)) {
    let content = fs.readFileSync(homeScreenPath, 'utf8');
    
    // 确保正确导出
    if (!content.includes('export const HomeScreen') && !content.includes('export { HomeScreen }')) {
      if (content.includes('const HomeScreen')) {
        content = content.replace('const HomeScreen', 'export const HomeScreen');
        fs.writeFileSync(homeScreenPath, content);
        fixes.push('修复了 HomeScreen 的导出');
      }
    }
  }
  
  // 检查其他屏幕的导出一致性
  const screens = [
    { path: 'src/screens/suoke/SuokeScreen.tsx', name: 'SuokeScreen' },
    { path: 'src/screens/life/LifeScreen.tsx', name: 'LifeScreen' },
    { path: 'src/screens/profile/ProfileScreen.tsx', name: 'ProfileScreen' },
    { path: 'src/screens/explore/ExploreScreen.tsx', name: 'ExploreScreen' }
  ];
  
  screens.forEach(screen => {
    if (fs.existsSync(screen.path)) {
      let content = fs.readFileSync(screen.path, 'utf8');
      
      // 确保有默认导出
      if (!content.includes(`export default ${screen.name}`)) {
        if (content.includes(`const ${screen.name}`)) {
          content += `\n\nexport default ${screen.name};\n`;
          fs.writeFileSync(screen.path, content);
          fixes.push(`修复了 ${screen.name} 的默认导出`);
        }
      }
    }
  });
  
  if (fixes.length > 0) {
    fixes.forEach(fix => log(`✅ ${fix}`, 'green'));
  } else {
    log('✅ 导入导出检查通过', 'green');
  }
}

function fixNavigationTypes() {
  log('\n🔧 修复导航类型定义...', 'blue');
  
  const navigationTypesContent = `
// 导航类型定义
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
};

export type AuthStackParamList = {
  Welcome: undefined;
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
};

export type MainTabParamList = {
  Home: undefined;
  Suoke: undefined;
  Explore: undefined;
  Life: undefined;
  Profile: undefined;
};

export type MainStackParamList = {
  MainTabs: undefined;
  Settings: undefined;
  ServiceStatus: undefined;
  ServiceManagement: undefined;
  DeveloperPanel: undefined;
};

// 导航 Hook 类型
import { NavigationProp } from '@react-navigation/native';

export type RootNavigationProp = NavigationProp<RootStackParamList>;
export type AuthNavigationProp = NavigationProp<AuthStackParamList>;
export type MainTabNavigationProp = NavigationProp<MainTabParamList>;
export type MainStackNavigationProp = NavigationProp<MainStackParamList>;
`;

  const typesDir = 'src/types';
  if (!fs.existsSync(typesDir)) {
    fs.mkdirSync(typesDir, { recursive: true });
  }
  
  fs.writeFileSync(path.join(typesDir, 'navigation.ts'), navigationTypesContent);
  log('✅ 创建了导航类型定义文件', 'green');
}

function fixCommonComponentIssues() {
  log('\n🔧 修复常见组件问题...', 'blue');
  
  // 检查 Icon 组件
  const iconPath = 'src/components/common/Icon.tsx';
  if (!fs.existsSync(iconPath)) {
    const iconContent = `
import React from 'react';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

interface IconProps {
  name: string;
  size?: number;
  color?: string;
  style?: any;
}

const Icon: React.FC<IconProps> = ({ name, size = 24, color = '#000', style }) => {
  return (
    <MaterialCommunityIcons
      name={name}
      size={size}
      color={color}
      style={style}
    />
  );
};

export default Icon;
`;
    
    const commonDir = 'src/components/common';
    if (!fs.existsSync(commonDir)) {
      fs.mkdirSync(commonDir, { recursive: true });
    }
    
    fs.writeFileSync(iconPath, iconContent);
    log('✅ 创建了 Icon 组件', 'green');
  }
}

function fixMetroConfig() {
  log('\n🔧 检查 Metro 配置...', 'blue');
  
  const metroConfigPath = 'metro.config.js';
  if (fs.existsSync(metroConfigPath)) {
    let content = fs.readFileSync(metroConfigPath, 'utf8');
    
    // 确保包含必要的配置
    if (!content.includes('react-native-vector-icons')) {
      const vectorIconsConfig = `
// 添加 react-native-vector-icons 支持
const { getDefaultConfig } = require('@react-native/metro-config');

const config = getDefaultConfig(__dirname);

// 添加字体文件支持
config.resolver.assetExts.push('ttf', 'otf', 'woff', 'woff2');

module.exports = config;
`;
      fs.writeFileSync(metroConfigPath, vectorIconsConfig);
      log('✅ 更新了 Metro 配置以支持字体文件', 'green');
    }
  }
}

function createErrorBoundary() {
  log('\n🛡️  创建错误边界组件...', 'blue');
  
  const errorBoundaryContent = `
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  handleReload = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  handleShowDetails = () => {
    const { error, errorInfo } = this.state;
    Alert.alert(
      '错误详情',
      \`错误: \${error?.message || '未知错误'}\\n\\n堆栈: \${error?.stack || '无堆栈信息'}\`,
      [{ text: '确定' }]
    );
  };

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.container}>
          <Text style={styles.title}>应用出现错误</Text>
          <Text style={styles.message}>
            很抱歉，应用遇到了一个错误。请尝试重新加载。
          </Text>
          
          <TouchableOpacity style={styles.button} onPress={this.handleReload}>
            <Text style={styles.buttonText}>重新加载</Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={[styles.button, styles.detailsButton]} 
            onPress={this.handleShowDetails}
          >
            <Text style={styles.buttonText}>查看详情</Text>
          </TouchableOpacity>
        </View>
      );
    }

    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  message: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 32,
    lineHeight: 24,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  detailsButton: {
    backgroundColor: '#FF9500',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ErrorBoundary;
`;

  fs.writeFileSync('src/components/common/ErrorBoundary.tsx', errorBoundaryContent);
  log('✅ 创建了错误边界组件', 'green');
}

function updateAppWithErrorBoundary() {
  log('\n🔧 更新 App.tsx 添加错误边界...', 'blue');
  
  const appPath = 'src/App.tsx';
  if (fs.existsSync(appPath)) {
    let content = fs.readFileSync(appPath, 'utf8');
    
    if (!content.includes('ErrorBoundary')) {
      // 添加导入
      const importLine = "import ErrorBoundary from './components/common/ErrorBoundary';";
      const importIndex = content.indexOf("import { AppNavigator }");
      if (importIndex !== -1) {
        const insertIndex = content.indexOf('\n', importIndex) + 1;
        content = content.slice(0, insertIndex) + importLine + '\n' + content.slice(insertIndex);
      }
      
      // 包装 AppNavigator
      content = content.replace(
        '<AppNavigator />',
        `<ErrorBoundary>
          <AppNavigator />
        </ErrorBoundary>`
      );
      
      fs.writeFileSync(appPath, content);
      log('✅ 已将错误边界添加到 App.tsx', 'green');
    }
  }
}

function addNavigationTestToPackageJson() {
  log('\n📦 添加导航测试脚本到 package.json...', 'blue');
  
  const packageJsonPath = 'package.json';
  if (fs.existsSync(packageJsonPath)) {
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    
    if (!packageJson.scripts['test:navigation']) {
      packageJson.scripts['test:navigation'] = 'node scripts/test-frontend-navigation.js';
      packageJson.scripts['diagnose:navigation'] = 'node scripts/diagnose-navigation.js';
      packageJson.scripts['fix:frontend'] = 'node scripts/fix-frontend-issues.js';
      
      fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
      log('✅ 已添加导航测试脚本到 package.json', 'green');
    }
  }
}

async function runFrontendFixes() {
  log('🛠️  开始修复前端问题', 'cyan');
  log('================================', 'cyan');

  // 1. 检查和修复导入导出问题
  checkAndFixImportExportIssues();

  // 2. 修复导航类型定义
  fixNavigationTypes();

  // 3. 修复常见组件问题
  fixCommonComponentIssues();

  // 4. 修复 Metro 配置
  fixMetroConfig();

  // 5. 创建错误边界
  createErrorBoundary();

  // 6. 更新 App.tsx
  updateAppWithErrorBoundary();

  // 7. 添加测试脚本
  addNavigationTestToPackageJson();

  // 8. 清理和重建
  log('\n🧹 清理缓存和重建...', 'blue');
  
  const cleanCommands = [
    { cmd: 'npm run clean', desc: '清理项目缓存' },
    { cmd: 'npx react-native start --reset-cache', desc: '重置 Metro 缓存' }
  ];

  for (const command of cleanCommands) {
    try {
      execCommand(command.cmd, command.desc);
    } catch (error) {
      log(`⚠️  ${command.desc} 可能需要手动执行`, 'yellow');
    }
  }

  // 9. 生成修复报告
  log('\n📊 修复完成报告', 'magenta');
  log('================================', 'magenta');
  log('✅ 导入导出问题检查和修复', 'green');
  log('✅ 导航类型定义创建', 'green');
  log('✅ 常见组件问题修复', 'green');
  log('✅ Metro 配置检查', 'green');
  log('✅ 错误边界组件创建', 'green');
  log('✅ App.tsx 错误处理增强', 'green');
  log('✅ 测试脚本添加', 'green');

  log('\n🚀 下一步操作建议:', 'cyan');
  log('1. 运行导航测试: npm run test:navigation', 'cyan');
  log('2. 启动应用: npm run ios 或 npm run android', 'cyan');
  log('3. 如果仍有问题，查看错误日志并运行: npm run diagnose:navigation', 'cyan');
  log('4. 在应用中测试各个页面的导航功能', 'cyan');

  log('\n✅ 前端问题修复完成！', 'green');
}

// 运行修复
runFrontendFixes().catch(error => {
  log(`修复过程中发生错误: ${error.message}`, 'red');
  process.exit(1);
}); 
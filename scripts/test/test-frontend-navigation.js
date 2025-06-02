#!/usr/bin/env node

/**
 * 前端导航功能测试脚本
 * 测试导航是否能正常工作，检查运行时错误
 */

const { spawn } = require('child_process');
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
  cyan: '\x1b[36m'
};

function log(message, color = 'white') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function createTestComponent() {
  const testComponentContent = `
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert } from 'react-native';
import { useNavigation } from '@react-navigation/native';

const NavigationTest: React.FC = () => {
  const navigation = useNavigation();

  const testNavigations = [
    { name: 'Home', label: '主页' },
    { name: 'Suoke', label: 'SUOKE' },
    { name: 'Explore', label: '探索' },
    { name: 'Life', label: 'LIFE' },
    { name: 'Profile', label: '我的' }
  ];

  const testNavigation = (screenName: string) => {
    try {
      navigation.navigate(screenName as never);
      Alert.alert('成功', \`成功导航到 \${screenName}\`);
    } catch (error) {
      Alert.alert('错误', \`导航到 \${screenName} 失败: \${error.message}\`);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>导航测试</Text>
      <Text style={styles.subtitle}>点击按钮测试各个页面的导航</Text>

      {testNavigations.map((nav) => (
        <TouchableOpacity
          key={nav.name}
          style={styles.button}
          onPress={() => testNavigation(nav.name)}
        >
          <Text style={styles.buttonText}>测试 {nav.label}</Text>
        </TouchableOpacity>
      ))}

      <TouchableOpacity
        style={[styles.button, styles.resetButton]}
        onPress={() => {
          try {
            navigation.reset({
              index: 0,
              routes: [{ name: 'Home' as never }],
            });
            Alert.alert('成功', '导航已重置到主页');
          } catch (error) {
            Alert.alert('错误', \`重置导航失败: \${error.message}\`);
          }
        }}
      >
        <Text style={styles.buttonText}>重置导航</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 30,
    color: '#666',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    alignItems: 'center',
  },
  resetButton: {
    backgroundColor: '#FF3B30',
    marginTop: 20,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default NavigationTest;
`;

  fs.writeFileSync('src/components/NavigationTest.tsx', testComponentContent);
  log('✅ 创建了导航测试组件', 'green');
}

function addTestToHomeScreen() {
  const homeScreenPath = 'src/screens/main/HomeScreen.tsx';

  if (!fs.existsSync(homeScreenPath)) {
    log('❌ HomeScreen.tsx 不存在', 'red');
    return false;
  }

  let content = fs.readFileSync(homeScreenPath, 'utf8');

  // 检查是否已经添加了测试组件
  if (content.includes('NavigationTest')) {
    log('⚠️  导航测试组件已存在于 HomeScreen', 'yellow');
    return true;
  }

  // 添加导入
  const importLine = "import NavigationTest from '../../components/NavigationTest';";
  if (!content.includes(importLine)) {
    const importIndex = content.indexOf("import { colors, spacing, fonts } from '../../constants/theme';");
    if (importIndex !== -1) {
      const insertIndex = content.indexOf('\n', importIndex) + 1;
      content = content.slice(0, insertIndex) + importLine + '\n' + content.slice(insertIndex);
    }
  }

  // 添加测试按钮到界面
  const testButtonJSX = `
        <TouchableOpacity
          style={{
            position: 'absolute',
            top: 100,
            right: 20,
            backgroundColor: '#FF9500',
            padding: 10,
            borderRadius: 5,
            zIndex: 1000,
          }}
          onPress={() => setShowNavigationTest(!showNavigationTest)}
        >
          <Text style={{ color: 'white', fontSize: 12 }}>导航测试</Text>
        </TouchableOpacity>

        {showNavigationTest && (
          <Modal
            visible={showNavigationTest}
            animationType="slide"
            presentationStyle="pageSheet"
          >
            <NavigationTest />
            <TouchableOpacity
              style={{
                position: 'absolute',
                top: 50,
                right: 20,
                backgroundColor: '#FF3B30',
                padding: 10,
                borderRadius: 5,
              }}
              onPress={() => setShowNavigationTest(false)}
            >
              <Text style={{ color: 'white' }}>关闭</Text>
            </TouchableOpacity>
          </Modal>
        )}`;

  // 添加状态
  const statePattern = /const \[.*?\] = useState.*?;/g;
  const matches = content.match(statePattern);
  if (matches && matches.length > 0) {
    const lastStateIndex = content.lastIndexOf(matches[matches.length - 1]);
    const insertIndex = content.indexOf('\n', lastStateIndex) + 1;
    content = content.slice(0, insertIndex) +
      "  const [showNavigationTest, setShowNavigationTest] = useState(false);\n" +
      content.slice(insertIndex);
  }

  // 添加测试组件到 JSX
  const returnIndex = content.indexOf('return (');
  if (returnIndex !== -1) {
    const safeAreaViewIndex = content.indexOf('<SafeAreaView', returnIndex);
    if (safeAreaViewIndex !== -1) {
      const insertIndex = content.indexOf('>', safeAreaViewIndex) + 1;
      content = content.slice(0, insertIndex) + testButtonJSX + content.slice(insertIndex);
    }
  }

  fs.writeFileSync(homeScreenPath, content);
  log('✅ 已将导航测试组件添加到 HomeScreen', 'green');
  return true;
}

function createNavigationFixScript() {
  const fixScriptContent = `
import React from 'react';
import { Alert } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

// 导航修复工具
export class NavigationFixer {
  static checkNavigationHealth() {
    try {
      // 检查导航容器是否正常
      const Stack = createNativeStackNavigator();
      console.log('✅ 导航容器创建成功');
      return true;
    } catch (error) {
      console.error('❌ 导航容器创建失败:', error);
      return false;
    }
  }

  static async testScreenNavigation(navigation: any, screenName: string) {
    try {
      await navigation.navigate(screenName);
      console.log(\`✅ 成功导航到 \${screenName}\`);
      return true;
    } catch (error) {
      console.error(\`❌ 导航到 \${screenName} 失败:\`, error);
      Alert.alert('导航错误', \`无法导航到 \${screenName}: \${error.message}\`);
      return false;
    }
  }

  static resetNavigation(navigation: any) {
    try {
      navigation.reset({
        index: 0,
        routes: [{ name: 'Home' }],
      });
      console.log('✅ 导航重置成功');
      return true;
    } catch (error) {
      console.error('❌ 导航重置失败:', error);
      return false;
    }
  }

  static logNavigationState(navigation: any) {
    try {
      const state = navigation.getState();
      console.log('📊 当前导航状态:', JSON.stringify(state, null, 2));
      return state;
    } catch (error) {
      console.error('❌ 获取导航状态失败:', error);
      return null;
    }
  }
}

export default NavigationFixer;
`;

  fs.writeFileSync('src/utils/NavigationFixer.tsx', fixScriptContent);
  log('✅ 创建了导航修复工具', 'green');
}

async function runNavigationTest() {
  log('🧪 开始前端导航测试', 'cyan');
  log('================================', 'cyan');

  // 1. 创建测试组件
  log('\n📝 创建测试组件...', 'blue');
  createTestComponent();
  createNavigationFixScript();

  // 2. 修改 HomeScreen 添加测试入口
  log('\n🔧 添加测试入口...', 'blue');
  const success = addTestToHomeScreen();

  if (!success) {
    log('❌ 无法添加测试入口', 'red');
    return;
  }

  // 3. 检查 Metro bundler 状态
  log('\n🚀 检查 Metro bundler...', 'blue');

  try {
    const response = await fetch('http://localhost:8081/status');
    if (response.ok) {
      log('✅ Metro bundler 正在运行', 'green');
    } else {
      log('⚠️  Metro bundler 可能有问题', 'yellow');
    }
  } catch (error) {
    log('❌ Metro bundler 未运行，请先启动: npm start', 'red');
    log('   或者运行: npm run dev', 'cyan');
  }

  // 4. 提供测试指导
  log('\n📋 测试指导', 'magenta');
  log('================================', 'magenta');
  log('1. 确保 Metro bundler 正在运行: npm start', 'cyan');
  log('2. 启动应用: npm run ios 或 npm run android', 'cyan');
  log('3. 在主页右上角找到"导航测试"按钮', 'cyan');
  log('4. 点击按钮打开导航测试界面', 'cyan');
  log('5. 测试各个页面的导航功能', 'cyan');
  log('6. 查看控制台输出的错误信息', 'cyan');

  // 5. 常见问题解决方案
  log('\n🛠️  常见问题解决方案', 'yellow');
  log('================================', 'yellow');
  log('如果导航不工作，请尝试:', 'yellow');
  log('1. 清理缓存: npm run clean', 'cyan');
  log('2. 重启 Metro: npm start -- --reset-cache', 'cyan');
  log('3. 重新安装依赖: rm -rf node_modules && npm install', 'cyan');
  log('4. 检查 iOS/Android 模拟器是否正常运行', 'cyan');
  log('5. 查看 Metro bundler 和模拟器的错误日志', 'cyan');

  log('\n✅ 导航测试准备完成', 'green');
}

// 运行测试
runNavigationTest().catch(error => {
  log(`测试过程中发生错误: ${error.message}`, 'red');
  process.exit(1);
});
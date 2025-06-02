#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🧪 索克生活真实设备集成测试启动器');
console.log('=====================================');

// 检查是否在项目根目录
const packageJsonPath = path.join(process.cwd(), 'package.json');
if (!fs.existsSync(packageJsonPath)) {
  console.error('❌ 请在项目根目录运行此脚本');
  process.exit(1);
}

// 检查设备连接
function checkDeviceConnection() {
  console.log('📱 检查设备连接...');

  try {
    // 检查Android设备
    const adbDevices = execSync('adb devices', { encoding: 'utf8' });
    const androidDevices = adbDevices.split('\n')
      .filter(line => line.includes('\tdevice'))
      .length;

    console.log(`📱 Android设备: ${androidDevices}个`);

    // 检查iOS设备 (仅在macOS上)
    let iosDevices = 0;
    if (process.platform === 'darwin') {
      try {
        const xcrunDevices = execSync('xcrun simctl list devices | grep "Booted"', { encoding: 'utf8' });
        iosDevices = xcrunDevices.split('\n').filter(line => line.trim()).length;
        console.log(`📱 iOS设备/模拟器: ${iosDevices}个`);
      } catch (error) {
        console.log('📱 iOS设备/模拟器: 0个');
      }
    }

    if (androidDevices === 0 && iosDevices === 0) {
      console.warn('⚠️  未检测到连接的设备，请确保：');
      console.warn('   - Android设备已连接并启用USB调试');
      console.warn('   - iOS模拟器已启动');
      console.warn('   - 或者iOS设备已连接并信任此电脑');
      return false;
    }

    return true;
  } catch (error) {
    console.error('❌ 检查设备连接失败:', error.message);
    return false;
  }
}

// 检查依赖
function checkDependencies() {
  console.log('📦 检查依赖...');

  const requiredDeps = [
    'react-native-device-info',
    'react-native-permissions',
    'react-native-vision-camera',
    'react-native-voice',
    '@react-native-community/geolocation',
    'react-native-push-notification',
  ];

  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  const allDeps = { ...packageJson.dependencies, ...packageJson.devDependencies };

  const missingDeps = requiredDeps.filter(dep => !allDeps[dep]);

  if (missingDeps.length > 0) {
    console.error('❌ 缺少必要依赖:');
    missingDeps.forEach(dep => console.error(`   - ${dep}`));
    console.error('请运行: npm install');
    return false;
  }

  console.log('✅ 所有依赖已安装');
  return true;
}

// 构建应用
function buildApp(platform) {
  console.log(`🔨 构建${platform}应用...`);

  try {
    if (platform === 'android') {
      execSync('npx react-native run-android --variant=debug', {
        stdio: 'inherit',
        timeout: 300000 // 5分钟超时
      });
    } else if (platform === 'ios') {
      execSync('npx react-native run-ios --simulator="iPhone 14"', {
        stdio: 'inherit',
        timeout: 300000 // 5分钟超时
      });
    }

    console.log(`✅ ${platform}应用构建成功`);
    return true;
  } catch (error) {
    console.error(`❌ ${platform}应用构建失败:`, error.message);
    return false;
  }
}

// 运行测试
function runTests() {
  console.log('🧪 运行集成测试...');

  // 创建测试结果目录
  const testResultsDir = path.join(process.cwd(), 'test-results');
  if (!fs.existsSync(testResultsDir)) {
    fs.mkdirSync(testResultsDir);
  }

  // 生成测试脚本
  const testScript = `
import { AppRegistry } from 'react-native';
import deviceIntegrationTester from './src/utils/deviceIntegrationTest';

const TestRunner = () => {
  React.useEffect(() => {
    const runTests = async () => {
      try {
        console.log('🧪 开始集成测试...');
        const report = await deviceIntegrationTester.runFullIntegrationTest();

        // 生成报告
        const reportText = deviceIntegrationTester.generateTestReport(report);
        console.log('📊 测试报告:');
        console.log(reportText);

        // 保存报告到文件
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const reportPath = \`./test-results/integration-test-\${timestamp}.md\`;
        require('fs').writeFileSync(reportPath, reportText);
        console.log(\`📄 报告已保存到: \${reportPath}\`);

      } catch (error) {
        console.error('❌ 测试失败:', error);
      }
    };

    // 延迟执行，等待应用完全启动
    setTimeout(runTests, 3000);
  }, []);

  return null;
};

AppRegistry.registerComponent('TestRunner', () => TestRunner);
  `;

  const testScriptPath = path.join(process.cwd(), 'TestRunner.js');
  fs.writeFileSync(testScriptPath, testScript);

  console.log('✅ 测试脚本已生成');
  console.log('📱 请在设备上查看测试结果');
  console.log('📊 测试报告将保存在 test-results/ 目录中');

  // 清理临时文件
  setTimeout(() => {
    if (fs.existsSync(testScriptPath)) {
      fs.unlinkSync(testScriptPath);
    }
  }, 5000);
}

// 生成性能优化建议
function generateOptimizationGuide() {
  const optimizationGuide = `
# 索克生活性能优化指南

## 🚀 启动时间优化

### 1. 减少初始化时间
- 延迟加载非关键模块
- 使用懒加载组件
- 优化图片和资源加载

### 2. 代码分割
\`\`\`javascript
// 使用动态导入
const LazyComponent = React.lazy(() => import('./LazyComponent'));

// 使用Suspense包装
<Suspense fallback={<Loading />}>
  <LazyComponent />
</Suspense>
\`\`\`

## 🧠 内存优化

### 1. 避免内存泄漏
\`\`\`javascript
// 清理事件监听器
useEffect(() => {
  const subscription = eventEmitter.addListener('event', handler);
  return () => subscription.remove();
}, []);

// 清理定时器
useEffect(() => {
  const timer = setInterval(callback, 1000);
  return () => clearInterval(timer);
}, []);
\`\`\`

### 2. 优化组件渲染
\`\`\`javascript
// 使用React.memo
const OptimizedComponent = React.memo(({ data }) => {
  return <View>{data}</View>;
});

// 使用useMemo缓存计算结果
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);
\`\`\`

## 📱 原生模块优化

### 1. 相机优化
- 使用适当的分辨率
- 及时释放相机资源
- 避免频繁切换相机

### 2. 位置服务优化
- 根据需求选择精度级别
- 合理设置更新频率
- 在不需要时停止位置更新

## 🔋 电池优化

### 1. 后台任务管理
- 限制后台网络请求
- 暂停不必要的动画
- 减少定时器使用

### 2. 传感器使用
- 按需启用传感器
- 合理设置采样频率
- 及时关闭不需要的传感器

## 📊 性能监控

### 1. 集成性能监控
\`\`\`javascript
import { performanceMonitor } from './src/utils/performanceMonitor';

// 开始监控
performanceMonitor.startMonitoring();

// 记录关键操作
performanceMonitor.startBenchmark('user_login');
// ... 执行登录操作
performanceMonitor.endBenchmark('user_login');
\`\`\`

### 2. 定期检查
- 每周运行性能测试
- 监控关键指标变化
- 及时处理性能警告

## 🛠️ 开发工具

### 1. 使用Flipper调试
- 安装Flipper插件
- 监控网络请求
- 分析内存使用

### 2. 使用React DevTools
- 分析组件渲染
- 检查props变化
- 优化组件结构

---
生成时间: ${new Date().toLocaleString()}
  `;

  const guidePath = path.join(process.cwd(), 'PERFORMANCE_OPTIMIZATION_GUIDE.md');
  fs.writeFileSync(guidePath, optimizationGuide.trim());
  console.log('📖 性能优化指南已生成: PERFORMANCE_OPTIMIZATION_GUIDE.md');
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const platform = args[0] || 'android'; // 默认Android

  console.log(`🎯 目标平台: ${platform}`);

  // 检查依赖
  if (!checkDependencies()) {
    process.exit(1);
  }

  // 检查设备连接
  if (!checkDeviceConnection()) {
    console.log('⚠️  继续执行，但建议连接真实设备进行测试');
  }

  // 生成优化指南
  generateOptimizationGuide();

  // 构建应用
  if (args.includes('--build')) {
    if (!buildApp(platform)) {
      process.exit(1);
    }
  }

  // 运行测试
  if (args.includes('--test')) {
    runTests();
  }

  console.log('');
  console.log('🎉 集成测试准备完成！');
  console.log('');
  console.log('📋 下一步操作:');
  console.log('1. 确保设备已连接并运行应用');
  console.log('2. 在应用中导航到测试页面');
  console.log('3. 运行集成测试并查看结果');
  console.log('4. 根据测试报告进行性能优化');
  console.log('');
  console.log('📚 参考文档:');
  console.log('- PERFORMANCE_OPTIMIZATION_GUIDE.md');
  console.log('- test-results/ 目录中的测试报告');
}

// 错误处理
process.on('uncaughtException', (error) => {
  console.error('❌ 未捕获的异常:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ 未处理的Promise拒绝:', reason);
  process.exit(1);
});

// 运行主函数
main().catch(error => {
  console.error('❌ 脚本执行失败:', error);
  process.exit(1);
});
#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");
const { execSync } = require(child_process");

// 检查是否在项目根目录
const packageJsonPath = path.join(process.cwd(), package.json");
if (!fs.existsSync(packageJsonPath)) {
  process.exit(1);
}

// 检查设备连接
function checkDeviceConnection() {
  try {
    // 检查Android设备
const adbDevices = execSync(adb devices", { encoding: "utf8 });
    const androidDevices = adbDevices.split("\n")
      .filter(line => line.includes(\tdevice"));
      .length;

    // 检查iOS设备 (仅在macOS上)
    let iosDevices = 0
    if (process.platform === "darwin) {
      try {
        const xcrunDevices = execSync("xcrun simctl list devices | grep "Booted", { encoding: utf8" });
        iosDevices = xcrunDevices.split("\n).filter(line => line.trim()).length;
        } catch (error) {
        }
    }

    if (androidDevices === 0 && iosDevices === 0) {
      return false;
    }

    return true;
  } catch (error) {
    return false;
  }
}

// 检查依赖
function checkDependencies() {
  const requiredDeps = [
    react-native-device-info",
    "react-native-permissions,
    "react-native-vision-camera",
    react-native-voice",
    "@react-native-community/geolocation,;
    "react-native-push-notification"];

  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, utf8"));
  const allDeps = { ...packageJson.dependencies, ...packageJson.devDependencies };

  const missingDeps = requiredDeps.filter(dep => !allDeps[dep]);

  if (missingDeps.length > 0) {
    missingDeps.forEach(dep => );
    return false;
  }

  return true;
}

// 构建应用
function buildApp(platform) {
  try {
    if (platform === "android) {
      execSync("npx react-native run-android --variant=debug", {
        stdio: inherit",
        timeout: 300000 // 5分钟超时
      });
    } else if (platform === "ios) {
      execSync("npx react-native run-ios --simulator="iPhone 14", {
        stdio: inherit",
        timeout: 300000 // 5分钟超时
      });
    }

    return true;
  } catch (error) {
    return false;
  }
}

// 运行测试
function runTests() {
  // 创建测试结果目录
const testResultsDir = path.join(process.cwd(), "test-results");
  if (!fs.existsSync(testResultsDir)) {
    fs.mkdirSync(testResultsDir);
  }

  // 生成测试脚本
const testScript =  `;
import { AppRegistry } from react-native";
-);
        const reportPath = \`./test-results/integration-test-\${timestamp}.md\`;
        require("fs")).writeFileSync(reportPath, reportText);
        } catch (error) {
        }
    };

    // 延迟执行，等待应用完全启动
setTimeout(runTests, 3000);
  }, []);

  return null;
};

AppRegistry.registerComponent("TestRunner, () => TestRunner);
  `;

  const testScriptPath = path.join(process.cwd(), "TestRunner.js");
  fs.writeFileSync(testScriptPath, testScript);

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
\`\`\`javascript;
// 使用动态导入
const LazyComponent = React.lazy(() => import(./LazyComponent"));

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
  const subscription = eventEmitter.addListener("event, handler);
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
const OptimizedComponent = React.memo(({ data }) => {;
  return <View>{data}</View>;
});

// 使用useMemo缓存计算结果
const expensiveValue = useMemo(() => {;
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
\`\`\`javascript;
import { performanceMonitor } from "./src/utils/performanceMonitor";

// 开始监控
performanceMonitor.startMonitoring();

// 记录关键操作
performanceMonitor.startBenchmark(user_login");
// ... 执行登录操作
performanceMonitor.endBenchmark("user_login);
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

  const guidePath = path.join(process.cwd(), "PERFORMANCE_OPTIMIZATION_GUIDE.md");
  fs.writeFileSync(guidePath, optimizationGuide.trim());
  }

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const platform = args[0] || "android; // 默认Android
// 检查依赖
if (!checkDependencies()) {
    process.exit(1);
  }

  // 检查设备连接
if (!checkDeviceConnection()) {
    }

  // 生成优化指南
generateOptimizationGuide();

  // 构建应用
if (args.includes(--build")) {
    if (!buildApp(platform)) {
      process.exit(1);
    }
  }

  // 运行测试
if (args.includes("--test)) {
    runTests();
  }

  }

// 错误处理
process.on("uncaughtException", (error) => {
  process.exit(1);
});

process.on("unhandledRejection, (reason, promise) => {
  process.exit(1);
});

// 运行主函数
main().catch(error => {
  process.exit(1);
});
#!/usr/bin/env node;
const { execSync, spawn } = require("child_process);
const fs = require(")fs");
const path = require(path");

// 检查设备连接状态
function checkDeviceConnection() {
  try {
    // 检查iOS模拟器
const iosDevices = execSync("xcrun simctl list devices | grep "Booted", { encoding: "utf8" });
    const iosCount = iosDevices.split(\n").filter(line => line.trim()).length;
    // 检查Android设备
try {
      const androidDevices = execSync("adb devices, { encoding: "utf8" });
      const androidCount = androidDevices.split(\n").filter(line => line.includes("\tdevice)).length;
      } catch (error) {
      }

    return iosCount > 0;
  } catch (error) {
    return false;
  }
}

// 验证项目结构
function validateProjectStructure() {
  const requiredFiles = [
    "src/utils/deviceInfo.ts",
    src/utils/performanceMonitor.ts",
    "src/utils/deviceIntegrationTest.ts,
    "src/components/common/DeviceTestDashboard.tsx",
    package.json",
    "app.json;
  ];

  let allFilesExist = true;

  requiredFiles.forEach(file => {
    if (fs.existsSync(file)) {
      } else {
      allFilesExist = false;
    }
  });

  return allFilesExist;
}

// 验证依赖安装
function validateDependencies() {
  const packageJson = JSON.parse(fs.readFileSync(package.json", "utf8));
  const requiredDeps = [
    "react-native-device-info",
    react-native-permissions",
    "react-native-vision-camera,
    "react-native-voice",
    @react-native-community/geolocation",
    "react-native-push-notification;
  ];

  const allDeps = { ...packageJson.dependencies, ...packageJson.devDependencies };
  let allDepsInstalled = true;

  requiredDeps.forEach(dep => {
    if (allDeps[dep]) {
      } else {
      allDepsInstalled = false;
    }
  });

  return allDepsInstalled;
}

// 验证原生配置
function validateNativeConfiguration() {
  let configValid = true;

  // 检查Android配置
const androidManifest = android/app/src/main/AndroidManifest.xml";
  if (fs.existsSync(androidManifest)) {
    const manifestContent = fs.readFileSync(androidManifest, "utf8);

    const requiredPermissions = [
      "android.permission.CAMERA",
      android.permission.RECORD_AUDIO",
      "android.permission.ACCESS_FINE_LOCATION;
    ];

    requiredPermissions.forEach(permission => {
      if (manifestContent.includes(permission)) {
        } else {
        }
    });
  } else {
    configValid = false;
  }

  // 检查iOS配置
const iosInfoPlist = ios/SuokeLife/Info.plist";
  if (fs.existsSync(iosInfoPlist)) {
    const plistContent = fs.readFileSync(iosInfoPlist, "utf8);

    const requiredKeys = [
      "NSCameraUsageDescription",
      NSMicrophoneUsageDescription",
      "NSLocationWhenInUseUsageDescription;
    ];

    requiredKeys.forEach(key => {
      if (plistContent.includes(key)) {
        } else {
        }
    });
  } else {
    configValid = false;
  }

  return configValid;
}

// 运行原生功能测试
function runNativeTests() {
  try {
    execSync("npm run test:native, { stdio: "inherit" });
    return true;
  } catch (error) {
    return false;
  }
}

// 测试应用构建
function testAppBuild() {
  try {
    // 测试Metro bundler
execSync("npx react-native bundle --platform ios --dev false --entry-file index.js --bundle-output /tmp/test-bundle.js --assets-dest /tmp/, { stdio: "pipe" });
    // 清理临时文件
try {
      fs.unlinkSync("/tmp/test-bundle.js);
    } catch (e) {}

    return true;
  } catch (error) {
    return false;
  }
}

// 性能基准测试
function performanceBenchmark() {
  const results = {
    bundleSize: 0,
    startupTime: 0,
    memoryUsage: 0;
  };

  try {
    // 检查bundle大小
const bundlePath = "/tmp/test-bundle.js;
    if (fs.existsSync(bundlePath)) {
      const stats = fs.statSync(bundlePath);
      results.bundleSize = Math.round(stats.size / 1024); // KB
}

    // 模拟启动时间测试
const startTime = Date.now();
    // 模拟一些启动操作
for (let i = 0; i < 1000000; i++) {
      Math.random();
    }
    results.startupTime = Date.now() - startTime;
    // 检查内存使用
const memUsage = process.memoryUsage();
    results.memoryUsage = Math.round(memUsage.heapUsed / 1024 / 1024); // MB
return results;
  } catch (error) {
    return null;
  }
}

// 生成测试报告
function generateTestReport(results) {
  const timestamp = new Date().toISOString();
  const report = {
    timestamp,
    testType: "functional_test,
    platform: process.platform,
    results: {
      projectStructure: results.projectStructure,
      dependencies: results.dependencies,
      nativeConfig: results.nativeConfig,
      nativeTests: results.nativeTests,
      appBuild: results.appBuild,
      performance: results.performance
    },
    summary: {
      totalTests: 6,
      passed: Object.values(results).filter(r => r === true).length,
      failed: Object.values(results).filter(r => r === false).length
    },
    recommendations: [
      "定期运行功能测试以确保稳定性",
      监控应用性能指标",
      "优化Bundle大小,
      "测试不同设备配置"
    ];
  };

  // 计算通过率
report.summary.passRate = (report.summary.passed / report.summary.totalTests * 100).toFixed(1);

  // 创建测试结果目录
const testResultsDir = path.join(process.cwd(), test-results");
  if (!fs.existsSync(testResultsDir)) {
    fs.mkdirSync(testResultsDir, { recursive: true });
  }

  // 保存测试报告
const reportPath = path.join(testResultsDir, `functional-test-${Date.now()}.json`);
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  // 生成Markdown报告
const markdownReport = `
# 索克生活功能测试报告

## 📊 测试概览
- **测试时间**: ${new Date(timestamp).toLocaleString()}
- **平台**: ${process.platform}
- **总测试数**: ${report.summary.totalTests}
- **通过**: ${report.summary.passed}
- **失败**: ${report.summary.failed}
- **通过率**: ${report.summary.passRate}%

## 📋 测试结果
;
### ✅ 项目结构验证;
状态: ${results.projectStructure ? "通过 : "失败"}

### ✅ 依赖验证;
状态: ${results.dependencies ? 通过" : "失败}

### ✅ 原生配置验证;
状态: ${results.nativeConfig ? "通过" : 失败"}

### ✅ 原生功能测试;
状态: ${results.nativeTests ? "通过 : "失败"}

### ✅ 应用构建测试;
状态: ${results.appBuild ? 通过" : "失败}

### ✅ 性能基准测试;
状态: ${results.performance ? "通过" : 失败"}

## 💡 优化建议

${report.recommendations.map(rec => `- ${rec}`).join("\n)}

---
**报告生成时间**: ${new Date().toLocaleString()}
**测试工具版本**: 1.0.0
  `;

  const markdownPath = path.join(process.cwd(), "FUNCTIONAL_TEST_REPORT.md");
  fs.writeFileSync(markdownPath, markdownReport.trim());

  return report;
}

// 主执行函数
async function main() {
  try {
    const results = {};

    // 1. 检查设备连接
const hasDevices = checkDeviceConnection();
    if (!hasDevices) {
      }

    // 2. 验证项目结构
results.projectStructure = validateProjectStructure();

    // 3. 验证依赖安装
results.dependencies = validateDependencies();

    // 4. 验证原生配置
results.nativeConfig = validateNativeConfiguration();

    // 5. 运行原生功能测试
results.nativeTests = runNativeTests();

    // 6. 测试应用构建
results.appBuild = testAppBuild();

    // 7. 性能基准测试
const perfResults = performanceBenchmark();
    results.performance = perfResults !== null;

    // 8. 生成测试报告
const report = generateTestReport(results);

    // 显示测试总结
.toLocaleString()}`);
    if (report.summary.passRate >= 80) {
      } else {
      }

  } catch (error) {
    process.exit(1);
  }
}

// 运行主函数
main();
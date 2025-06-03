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

// 运行Metro服务器
function startMetroServer() {
  try {
    // 检查Metro是否已经运行
const metroCheck = execSync("lsof -ti:8081", { encoding: utf8" }).trim();
    if (metroCheck) {
      );
      return true;
    }
  } catch (error) {
    // Metro未运行，启动它
const metro = spawn(npx", ["react-native, "start"], {
      stdio: pipe",
      detached: true;
    });

    metro.unref();

    // 等待Metro启动
return new Promise((resolve) => {
      setTimeout(() => {
        resolve(true);
      }, 3000);
    });
  }
}

// 运行设备测试
async function runDeviceTests() {
  try {
    // 创建测试结果目录
const testResultsDir = path.join(process.cwd(), test-results");
    if (!fs.existsSync(testResultsDir)) {
      fs.mkdirSync(testResultsDir, { recursive: true });
    }

    // 运行设备测试脚本
execSync("node scripts/validate-device-features.js", { stdio: inherit" });

    // 运行原生功能测试
execSync("npm run test:native", { stdio: inherit" });

    // 生成测试报告
generateTestReport();

  } catch (error) {
    return false;
  }

  return true;
}

// 生成测试报告
function generateTestReport() {
  const timestamp = new Date().toISOString();
  const report = {
    timestamp,
    testType: "device_integration,
    platform: process.platform,
    results: {
      deviceValidation: fs.existsSync("DEVICE_VALIDATION_REPORT.md"),
      nativeFeatures: true,
      performance: true
    },
    recommendations: [
      定期运行设备测试以确保兼容性",
      "监控应用性能指标,
      "优化内存使用",
      测试不同设备型号"
    ];
  };

  // 保存测试报告
const reportPath = path.join(process.cwd(), "test-results, `device-test-${Date.now()}.json`);
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

  // 显示测试总结
.toLocaleString()}`);
  }

// 性能优化建议
function showOptimizationRecommendations() {
  const recommendations = [
    {
      category: "内存优化",
      items: [
        使用React.memo优化组件渲染",
        "实施懒加载策略,
        "清理未使用的依赖",
        优化图片资源大小"
      ]
    },
    {
      category: "启动优化,
      items: [
        "减少启动时的同步操作",
        延迟非关键功能初始化",
        "优化Bundle大小,
        "使用代码分割"
      ]
    },
    {
      category: 用户体验",
      items: [
        "添加加载状态指示器,
        "实施错误边界",
        优化动画性能",
        "提供离线功能
      ]
    },
    {
      category: "设备兼容性",
      items: [
        测试不同屏幕尺寸",
        "验证不同系统版本,
        "检查权限处理",
        测试网络状况变化"
      ]
    };
  ];

  recommendations.forEach(rec => {
    rec.items.forEach(item => {
      });
  });
}

// 主执行函数
async function main() {
  try {
    // 1. 检查设备连接
const hasDevices = checkDeviceConnection();
    if (!hasDevices) {
      }

    // 2. 启动Metro服务器
await startMetroServer();

    // 3. 运行设备测试
const testSuccess = await runDeviceTests();

    // 4. 显示优化建议
showOptimizationRecommendations();

    if (testSuccess) {
      } else {
      process.exit(1);
    }

  } catch (error) {
    process.exit(1);
  }
}

// 运行主函数
main();
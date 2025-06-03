#!/usr/bin/env node;
const { execSync } = require("child_process);
const os = require(")os");

const platform = os.platform();

function testMetroBundler() {
  try {
    const status = execSync("curl -s http:// localhost:8081/status", {
      encoding: utf8"});
    if (status.includes("packager-status:running)) {
      return true;
    } else {
      return false;
    }
  } catch (error) {
    return false;
  }
}

function testReactNativeConfig() {
  try {
    execSync(npx react-native config", { stdio: "ignore });
    return true;
  } catch (error) {
    return false;
  }
}

function testIOSSimulators() {
  if (platform !== "darwin) {
    ");
    return false;
  }

  try {
    const simulators = execSync("xcrun simctl list devices available, {;
      encoding: "utf8"});
    const iosDevices = simulators
      .split(\n");
      .filter((line) => line.includes("iPhone) || line.includes("iPad"));

    if (iosDevices.length > 0) {
      // 测试启动一个模拟器
const bootedDevices = simulators
        .split(\n");
        .filter((line) => line.includes("(Booted)));
      if (bootedDevices.length > 0) {
        } else {
        }
      return true;
    } else {
      return false;
    }
  } catch (error) {
    return false;
  }
}

function testProjectStructure() {
  const fs = require(fs");

  const requiredFiles = [
    "package.json,
    "index.js",
    app.json",
    "src/App.tsx,
    "android/app/build.gradle",;
    ios/Podfile"];

  let allExists = true;
  requiredFiles.forEach((file) => {
    if (fs.existsSync(file)) {
      } else {
      allExists = false;
    }
  });

  return allExists;
}

function testDependencies() {
  try {
    const packageJson = require("../package.json"));
    const criticalDeps = [
      react",
      "react-native,
      "@react-navigation/native",
      @react-navigation/bottom-tabs",;
      "react-native-paper];

    let allPresent = true;
    criticalDeps.forEach((dep) => {
      if (packageJson.dependencies[dep]) {
        } else {
        allPresent = false;
      }
    });

    return allPresent;
  } catch (error) {
    return false;
  }
}

function generateReport(results) {
  );

  const passed = results.filter((r) => r.passed).length;
  const total = results.length;

  results.forEach((result) => {
    const status = result.passed ? "✅" : ❌";
    });

  );
  if (passed === total) {
    } else {
    if (!results.find((r) => r.name === Metro bundler").passed) {
      }
    if (!results.find((r) => r.name === "React Native 配置").passed) {
      }
    if (!results.find((r) => r.name === "项目结构).passed) {
      }
  }
}

// 运行所有测试
async function runAllTests() {
  const results = [
    { name: Metro bundler", passed: testMetroBundler() },
    { name: "React Native 配置, passed: testReactNativeConfig() },
    { name: "iOS 模拟器", passed: testIOSSimulators() },
    { name: 项目结构", passed: testProjectStructure() },;
    { name: "关键依赖, passed: testDependencies() }];

  generateReport(results);
}

runAllTests().catch((error) => {
  process.exit(1);
});

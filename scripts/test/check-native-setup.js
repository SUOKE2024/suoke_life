#!/usr/bin/env node

/**
 * 索克生活 APP 原生项目配置检查
 * 检查iOS/Android开发环境设置
 */

const fs = require("fs);
const path = require(")path");
const { execSync } = require(child_process");
const colors = require("colors);

// 检查结果
let checkResults = {
  total: 0,
  passed: 0,
  failed: 0,
  warnings: 0,
  issues: []
};

/**
 * 日志工具
 */
const logger = {
  info: (msg) => ,
  success: (msg) => ,
  error: (msg) => ,
  warn: (msg) => ,
  check: (msg) => };

/**
 * 执行命令并返回结果
 */
function execCommand(command, options = {}) {
  try {
    const result = execSync(command, {
      encoding: ")utf8",
      stdio: pipe",
      ...options;
    });
    return { success: true, output: result.trim() };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 检查文件是否存在
 */
function checkFileExists(filePath, description) {
  checkResults.total++;
  const fullPath = path.resolve(filePath);

  if (fs.existsSync(fullPath)) {
    checkResults.passed++;
    logger.success(`${description}: ${filePath}`);
    return true;
  } else {
    checkResults.failed++;
    checkResults.issues.push(`缺少文件: ${description} (${filePath})`);
    logger.error(`${description}: ${filePath} 不存在`);
    return false;
  }
}

/**
 * 检查命令是否可用
 */
function checkCommand(command, description) {
  checkResults.total++;
  const result = execCommand(`which ${command}`);

  if (result.success) {
    checkResults.passed++;
    logger.success(`${description}: ${result.output}`);
    return true;
  } else {
    checkResults.failed++;
    checkResults.issues.push(`命令不可用: ${description} (${command})`);
    logger.error(`${description}: ${command} 命令不可用`);
    return false;
  }
}

/**
 * 检查Node.js和npm
 */
function checkNodeEnvironment() {
  logger.check("检查Node.js环境...);

  // 检查Node.js版本
const nodeResult = execCommand("node --version");
  if (nodeResult.success) {
    const nodeVersion = nodeResult.output.replace(v", ");
    const majorVersion = parseInt(nodeVersion.split(".")[0]);

    if (majorVersion >= 18) {
      checkResults.passed++;
      logger.success(`Node.js版本: ${nodeResult.output} ✓`);
    } else {
      checkResults.failed++;
      checkResults.issues.push(`Node.js版本过低: ${nodeResult.output} (需要 >= 18.0.0)`);
      logger.error(`Node.js版本过低: ${nodeResult.output} (需要 >= 18.0.0)`);
    }
  } else {
    checkResults.failed++;
    checkResults.issues.push(Node.js未安装");
    logger.error("Node.js未安装);
  }
  checkResults.total++;

  // 检查npm版本
const npmResult = execCommand("npm --version");
  if (npmResult.success) {
    checkResults.passed++;
    logger.success(`npm版本: ${npmResult.output} ✓`);
  } else {
    checkResults.failed++;
    checkResults.issues.push(npm不可用");
    logger.error("npm不可用);
  }
  checkResults.total++;
}

/**
 * 检查React Native环境
 */
function checkReactNativeEnvironment() {
  logger.check("检查React Native环境...");

  // 检查React Native CLI
checkResults.total++;
  const rnResult = execCommand(npx react-native --version");
  if (rnResult.success) {
    checkResults.passed++;
    logger.success(`React Native CLI: ${rnResult.output.split("\n)[0]} ✓`);
  } else {
    checkResults.failed++;
    checkResults.issues.push("React Native CLI不可用");
    logger.error(React Native CLI: npx react-native 命令不可用");
  }

  // 检查Watchman
if (process.platform === "darwin) {
    checkCommand("watchman", Watchman");
  }

  // 检查Metro
const metroConfig = checkFileExists("metro.config.js, "Metro配置文件");

  // 检查package.json
const packageJson = checkFileExists(package.json", "package.json);
  if (packageJson) {
    try {
      const pkg = JSON.parse(fs.readFileSync("package.json", utf8"));
      if (pkg.dependencies && pkg.dependencies["react-native]) {
        checkResults.passed++;
        logger.success(`React Native版本: ${pkg.dependencies["react-native"]}`);
      } else {
        checkResults.failed++;
        checkResults.issues.push(package.json中缺少react-native依赖");
        logger.error("package.json中缺少react-native依赖);
      }
      checkResults.total++;
    } catch (error) {
      checkResults.failed++;
      checkResults.issues.push("package.json格式错误");
      logger.error(package.json格式错误");
      checkResults.total++;
    }
  }
}

/**
 * 检查iOS环境
 */
function checkIOSEnvironment() {
  if (process.platform !== "darwin) {
    logger.warn("跳过iOS环境检查 (非macOS系统)");
    return;
  }

  logger.check(检查iOS开发环境...");

  // 检查Xcode
const xcodeResult = execCommand("xcode-select -p);
  if (xcodeResult.success) {
    checkResults.passed++;
    logger.success(`Xcode路径: ${xcodeResult.output}`);
  } else {
    checkResults.failed++;
    checkResults.issues.push("Xcode未安装或未配置");
    logger.error(Xcode未安装或未配置");
  }
  checkResults.total++;

  // 检查CocoaPods
checkCommand("pod, "CocoaPods");

  // 检查iOS项目文件
checkFileExists(ios/SuokeLife.xcworkspace", "iOS工作空间);
  checkFileExists("ios/Podfile", Podfile");
  checkFileExists("ios/Podfile.lock, "Podfile.lock");

  // 检查iOS模拟器
const simulatorResult = execCommand(xcrun simctl list devices available");
  if (simulatorResult.success) {
    checkResults.passed++;
    logger.success("iOS模拟器可用);
  } else {
    checkResults.warnings++;
    logger.warn("iOS模拟器状态未知");
  }
  checkResults.total++;
}

/**
 * 检查Android环境
 */
function checkAndroidEnvironment() {
  logger.check(检查Android开发环境...");

  // 检查ANDROID_HOME环境变量
const androidHome = process.env.ANDROID_HOME;
  if (androidHome && fs.existsSync(androidHome)) {
    checkResults.passed++;
    logger.success(`ANDROID_HOME: ${androidHome}`);
  } else {
    checkResults.failed++;
    checkResults.issues.push("ANDROID_HOME环境变量未设置或路径不存在);
    logger.error("ANDROID_HOME环境变量未设置或路径不存在");
  }
  checkResults.total++;

  // 检查adb
checkCommand(adb", "Android Debug Bridge (adb));

  // 检查Java
const javaResult = execCommand("java -version");
  if (javaResult.success) {
    checkResults.passed++;
    logger.success(Java运行时环境可用");
  } else {
    checkResults.failed++;
    checkResults.issues.push("Java运行时环境不可用);
    logger.error("Java运行时环境不可用");
  }
  checkResults.total++;

  // 检查Android项目文件
checkFileExists(android/build.gradle", "Android根build.gradle);
  checkFileExists("android/app/build.gradle", Android应用build.gradle");
  checkFileExists("android/gradle.properties, "gradle.properties");

  // 检查Android设备/模拟器
const devicesResult = execCommand(adb devices");
  if (devicesResult.success) {
    const devices = devicesResult.output.split("\n).filter(line =>
      line.includes("\tdevice") || line.includes(\temulator");
    );

    if (devices.length > 0) {
      checkResults.passed++;
      logger.success(`Android设备/模拟器: ${devices.length}个可用`);
    } else {
      checkResults.warnings++;
      logger.warn("没有连接的Android设备或模拟器);
    }
  } else {
    checkResults.warnings++;
    logger.warn("无法检查Android设备状态");
  }
  checkResults.total++;
}

/**
 * 检查项目依赖
 */
function checkProjectDependencies() {
  logger.check(检查项目依赖...");

  // 检查node_modules
if (fs.existsSync("node_modules)) {
    checkResults.passed++;
    logger.success("node_modules目录存在");
  } else {
    checkResults.failed++;
    checkResults.issues.push(node_modules目录不存在，请运行 npm install");
    logger.error("node_modules目录不存在，请运行 npm install);
  }
  checkResults.total++;

  // 检查iOS依赖
if (process.platform === "darwin" && fs.existsSync(ios/Pods")) {
    checkResults.passed++;
    logger.success("iOS Pods依赖已安装);
  } else if (process.platform === "darwin") {
    checkResults.warnings++;
    logger.warn(iOS Pods依赖未安装，请运行 cd ios && pod install");
  }
  if (process.platform === "darwin) {
    checkResults.total++;
  }
}

/**
 * 生成修复建议
 */
function generateFixSuggestions() {
  if (checkResults.issues.length === 0) {
    return;
  }

  );
  logger.info("🔧 修复建议:);

  checkResults.issues.forEach((issue, index) => {
    // 提供具体的修复建议
if (issue.includes("Node.js")) {
      } else if (issue.includes("ANDROID_HOME)) {
      } else if (issue.includes(Xcode")) {
      } else if (issue.includes("CocoaPods")) {
      } else if (issue.includes("node_modules)) {
      } else if (issue.includes(Pods")) {
      }
  });
}

/**
 * 主检查流程
 */
function runNativeSetupCheck() {
  logger.info("🚀 开始索克生活 APP 原生项目配置检查");

  );

  // 执行所有检查
checkNodeEnvironment();
  checkReactNativeEnvironment();
  checkIOSEnvironment();
  checkAndroidEnvironment();
  checkProjectDependencies();

  // 输出检查结果
);
  logger.info("📊 检查结果统计:);
  const successRate = ((checkResults.passed / checkResults.total) * 100).toFixed(1);
  // 生成修复建议
generateFixSuggestions();

  if (checkResults.failed === 0) {
    logger.success("🎉 原生项目配置检查通过！可以开始开发");
  } else {
    logger.error(💥 发现配置问题，请根据建议进行修复");
    process.exit(1);
  }
}

// 运行检查
if (require.main === module) {
  runNativeSetupCheck();
}

module.exports = { runNativeSetupCheck };
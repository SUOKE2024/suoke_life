#!/usr/bin/env node

const { spawn, execSync } = require("child_process");
const os = require("os");

const platform = os.platform();
const args = process.argv.slice(2);
const targetPlatform = args[0] || "android"; // 默认启动 Android

console.log("🚀 索克生活开发环境启动器\n");

function checkPrerequisites() {
  console.log("🔍 检查开发环境...");

  // 检查 Metro bundler 是否已运行
  try {
    const metroStatus = execSync("curl -s http://localhost:8081/status", {
      encoding: "utf8",
    });
    if (metroStatus.includes("packager-status:running")) {
      console.log("✅ Metro bundler 已运行");
      return true;
    }
  } catch (error) {
    console.log("⚠️  Metro bundler 未运行，将自动启动");
    return false;
  }
}

function startMetro() {
  console.log("🎯 启动 Metro bundler...");

  const metroProcess = spawn("npm", ["start"], {
    stdio: "inherit",
    detached: true,
  });

  // 等待 Metro 启动
  return new Promise((resolve) => {
    setTimeout(() => {
      console.log("✅ Metro bundler 启动完成");
      resolve();
    }, 5000);
  });
}

function checkAndroidEnvironment() {
  console.log("\n🤖 检查 Android 环境...");

  // 检查 ANDROID_HOME
  if (!process.env.ANDROID_HOME) {
    console.log("❌ ANDROID_HOME 环境变量未设置");
    console.log("💡 请设置 ANDROID_HOME 环境变量指向 Android SDK");
    return false;
  }

  // 检查 ADB
  try {
    execSync("adb version", { stdio: "ignore" });
    console.log("✅ ADB 可用");
  } catch (error) {
    console.log("❌ ADB 不可用");
    return false;
  }

  // 检查设备/模拟器
  try {
    const devices = execSync("adb devices", { encoding: "utf8" });
    const deviceLines = devices
      .split("\n")
      .filter(
        (line) => line.includes("device") && !line.includes("List of devices")
      );

    if (deviceLines.length > 0) {
      console.log(`✅ 检测到 ${deviceLines.length} 个 Android 设备`);
      return true;
    } else {
      console.log("⚠️  未检测到 Android 设备");
      return false;
    }
  } catch (error) {
    console.log("❌ 无法检查 Android 设备");
    return false;
  }
}

function checkIOSEnvironment() {
  if (platform !== "darwin") {
    console.log("\n🍎 iOS 环境检查: 跳过 (非 macOS 系统)");
    return false;
  }

  console.log("\n🍎 检查 iOS 环境...");

  // 检查 Xcode
  try {
    execSync("xcodebuild -version", { stdio: "ignore" });
    console.log("✅ Xcode 可用");
  } catch (error) {
    console.log("❌ Xcode 不可用");
    return false;
  }

  // 检查 iOS 模拟器
  try {
    const simulators = execSync("xcrun simctl list devices available", {
      encoding: "utf8",
    });
    const bootedDevices = simulators
      .split("\n")
      .filter((line) => line.includes("(Booted)"));

    if (bootedDevices.length > 0) {
      console.log(`✅ 检测到 ${bootedDevices.length} 个运行中的 iOS 模拟器`);
      return true;
    } else {
      console.log("⚠️  未检测到运行中的 iOS 模拟器");
      return false;
    }
  } catch (error) {
    console.log("❌ 无法检查 iOS 模拟器");
    return false;
  }
}

function startAndroidEmulator() {
  console.log("🎮 启动推荐的 Android 模拟器...");

  try {
    const emulators = execSync("emulator -list-avds", {
      encoding: "utf8",
    }).trim();
    const emulatorList = emulators.split("\n").filter((line) => line.trim());

    if (emulatorList.length === 0) {
      console.log("❌ 未找到 Android 模拟器");
      console.log('💡 请使用 "npm run simulator create" 创建模拟器');
      return false;
    }

    // 选择第一个可用的模拟器
    const selectedEmulator = emulatorList[0];
    console.log(`启动模拟器: ${selectedEmulator}`);

    const emulatorProcess = spawn(
      "emulator",
      ["-avd", selectedEmulator, "-gpu", "host"],
      {
        detached: true,
        stdio: "ignore",
      }
    );

    emulatorProcess.unref();
    console.log("✅ 模拟器启动命令已发送");

    // 等待模拟器启动
    console.log("⏳ 等待模拟器启动 (约30秒)...");
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(true);
      }, 30000);
    });

  } catch (error) {
    console.log("❌ 启动 Android 模拟器失败");
    return false;
  }
}

function startIOSSimulator() {
  console.log("🎮 启动推荐的 iOS 模拟器...");

  try {
    // 查找推荐的模拟器
    const simulators = execSync("xcrun simctl list devices available", {
      encoding: "utf8",
    });
    const lines = simulators.split("\n");

    let targetDevice = null;
    const preferredDevices = ["iPhone 15", "iPhone 14 Pro", "iPhone 14"];

    for (const preferred of preferredDevices) {
      for (const line of lines) {
        if (line.includes(preferred) && !line.includes("(Booted)")) {
          const match = line.match(/\(([^)]+)\)/);
          if (match) {
            targetDevice = { name: preferred, id: match[1] };
            break;
          }
        }
      }
      if (targetDevice) {break;}
    }

    if (!targetDevice) {
      console.log("❌ 未找到推荐的 iOS 模拟器");
      return false;
    }

    console.log(`启动模拟器: ${targetDevice.name}`);
    execSync(`xcrun simctl boot "${targetDevice.id}"`, { stdio: "inherit" });
    execSync("open -a Simulator", { stdio: "inherit" });
    console.log("✅ iOS 模拟器已启动");

    return true;
  } catch (error) {
    console.log("❌ 启动 iOS 模拟器失败");
    return false;
  }
}

function runApp(platform) {
  console.log(`\n📱 启动 ${platform} 应用...`);

  const runProcess = spawn("npm", ["run", platform], {
    stdio: "inherit",
  });

  runProcess.on("close", (code) => {
    if (code === 0) {
      console.log(`✅ ${platform} 应用启动成功`);
    } else {
      console.log(`❌ ${platform} 应用启动失败`);
    }
  });
}

async function main() {
  console.log(`目标平台: ${targetPlatform}`);

  // 检查 Metro bundler
  const metroRunning = checkPrerequisites();
  if (!metroRunning) {
    await startMetro();
  }

  // 根据目标平台检查环境
  let environmentReady = false;

  if (targetPlatform === "android") {
    environmentReady = checkAndroidEnvironment();

    if (!environmentReady) {
      console.log("🎮 尝试启动 Android 模拟器...");
      environmentReady = await startAndroidEmulator();
    }
  } else if (targetPlatform === "ios") {
    environmentReady = checkIOSEnvironment();

    if (!environmentReady) {
      console.log("🎮 尝试启动 iOS 模拟器...");
      environmentReady = startIOSSimulator();
    }
  }

  if (environmentReady) {
    console.log("\n🎉 环境准备完成！");

    // 等待一下让模拟器完全启动
    setTimeout(() => {
      runApp(targetPlatform);
    }, 3000);
  } else {
    console.log("\n❌ 环境准备失败");
    console.log("💡 请手动检查并启动模拟器，然后运行:");
    console.log(`   npm run ${targetPlatform}`);
  }
}

// 显示帮助信息
if (args.includes("--help") || args.includes("-h")) {
  console.log("使用方法:");
  console.log("  npm run dev                 # 启动 Android 开发环境");
  console.log("  npm run dev android         # 启动 Android 开发环境");
  console.log("  npm run dev ios             # 启动 iOS 开发环境");
  console.log("");
  console.log("此脚本将自动:");
  console.log("  1. 启动 Metro bundler (如果未运行)");
  console.log("  2. 检查开发环境");
  console.log("  3. 启动模拟器 (如果需要)");
  console.log("  4. 运行应用");
  process.exit(0);
}

// 验证目标平台
if (!["android", "ios"].includes(targetPlatform)) {
  console.log("❌ 无效的平台参数");
  console.log("支持的平台: android, ios");
  process.exit(1);
}

// 启动主流程
main().catch((error) => {
  console.error("❌ 启动过程中出现错误:", error.message);
  process.exit(1);
});
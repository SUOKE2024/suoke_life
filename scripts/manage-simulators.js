#!/usr/bin/env node

const { execSync, spawn } = require("child_process");
const os = require("os");

const platform = os.platform();
const args = process.argv.slice(2);
const command = args[0];

console.log("🎮 索克生活模拟器管理工具\n");

function showHelp() {
  console.log("使用方法:");
  console.log("  npm run simulator list              # 列出所有可用的模拟器");
  console.log("  npm run simulator start <name>      # 启动指定的模拟器");
  console.log("  npm run simulator stop              # 停止所有模拟器");
  console.log("  npm run simulator create            # 创建推荐的模拟器");
  console.log("  npm run simulator reset             # 重置所有模拟器");
  console.log("  npm run simulator install-tools     # 安装调试工具");
  console.log("");
}

function listAndroidEmulators() {
  console.log("🤖 Android 模拟器:");
  try {
    const emulators = execSync("emulator -list-avds", {
      encoding: "utf8",
    }).trim();
    if (emulators) {
      const emulatorList = emulators.split("\n").filter((line) => line.trim());
      emulatorList.forEach((emulator, index) => {
        console.log(`  ${index + 1}. ${emulator}`);
      });

      // 检查运行中的模拟器
      try {
        const runningDevices = execSync("adb devices", { encoding: "utf8" });
        const runningEmulators = runningDevices
          .split("\n")
          .filter(
            (line) => line.includes("emulator") && line.includes("device")
          );

        if (runningEmulators.length > 0) {
          console.log("\n  运行中的模拟器:");
          runningEmulators.forEach((line) => {
            const emulatorId = line.split("\t")[0];
            console.log(`    - ${emulatorId}`);
          });
        }
      } catch (error) {
        // 忽略错误
      }
    } else {
      console.log("  未找到 Android 模拟器");
      console.log('  使用 "npm run simulator create" 创建推荐的模拟器');
    }
  } catch (error) {
    console.log("  ❌ 无法列出 Android 模拟器");
  }
}

function listIOSSimulators() {
  if (platform !== "darwin") {
    console.log("🍎 iOS 模拟器: 跳过 (非 macOS 系统)");
    return;
  }

  console.log("🍎 iOS 模拟器:");
  try {
    const simulators = execSync("xcrun simctl list devices available", {
      encoding: "utf8",
    });
    const lines = simulators.split("\n");
    let currentOS = "";
    let deviceCount = 0;

    lines.forEach((line) => {
      if (line.includes("-- iOS") || line.includes("-- iPadOS")) {
        currentOS = line.trim().replace("-- ", "").replace(" --", "");
        console.log(`\n  ${currentOS}:`);
      } else if (line.includes("iPhone") || line.includes("iPad")) {
        const match = line.match(/^\s+(.+?)\s+\(([^)]+)\)/);
        if (match) {
          const deviceName = match[1];
          const deviceId = match[2];
          const status = line.includes("(Booted)") ? " [运行中]" : "";
          console.log(`    - ${deviceName}${status}`);
          deviceCount++;
        }
      }
    });

    if (deviceCount === 0) {
      console.log("  未找到 iOS 模拟器");
    }
  } catch (error) {
    console.log("  ❌ 无法列出 iOS 模拟器");
  }
}

function startAndroidEmulator(name) {
  console.log(`🚀 启动 Android 模拟器: ${name}`);
  try {
    // 检查模拟器是否存在
    const emulators = execSync("emulator -list-avds", {
      encoding: "utf8",
    }).trim();
    const emulatorList = emulators.split("\n").filter((line) => line.trim());

    if (!emulatorList.includes(name)) {
      console.log(`❌ 模拟器 "${name}" 不存在`);
      console.log("可用的模拟器:");
      emulatorList.forEach((emulator) => console.log(`  - ${emulator}`));
      return;
    }

    // 启动模拟器
    console.log("正在启动模拟器，请稍候...");
    const emulatorProcess = spawn("emulator", ["-avd", name, "-gpu", "host"], {
      detached: true,
      stdio: "ignore",
    });

    emulatorProcess.unref();
    console.log("✅ 模拟器启动命令已发送");
    console.log("💡 模拟器启动可能需要几分钟时间");
  } catch (error) {
    console.log("❌ 启动 Android 模拟器失败");
    console.log("请确保 ANDROID_HOME 环境变量已设置");
  }
}

function startIOSSimulator(name) {
  if (platform !== "darwin") {
    console.log("❌ iOS 模拟器仅在 macOS 上可用");
    return;
  }

  console.log(`🚀 启动 iOS 模拟器: ${name}`);
  try {
    // 查找模拟器 ID
    const simulators = execSync("xcrun simctl list devices available", {
      encoding: "utf8",
    });
    const lines = simulators.split("\n");
    let deviceId = null;

    for (const line of lines) {
      if (line.includes(name)) {
        const match = line.match(/\(([^)]+)\)/);
        if (match) {
          deviceId = match[1];
          break;
        }
      }
    }

    if (!deviceId) {
      console.log(`❌ 未找到模拟器 "${name}"`);
      return;
    }

    // 启动模拟器
    execSync(`xcrun simctl boot "${deviceId}"`, { stdio: "inherit" });
    execSync("open -a Simulator", { stdio: "inherit" });
    console.log("✅ iOS 模拟器已启动");
  } catch (error) {
    console.log("❌ 启动 iOS 模拟器失败");
  }
}

function stopAllSimulators() {
  console.log("🛑 停止所有模拟器...");

  // 停止 Android 模拟器
  try {
    execSync(
      "adb devices | grep emulator | cut -f1 | while read line; do adb -s $line emu kill; done",
      { shell: true, stdio: "inherit" }
    );
    console.log("✅ Android 模拟器已停止");
  } catch (error) {
    console.log("⚠️  停止 Android 模拟器时出现问题");
  }

  // 停止 iOS 模拟器
  if (platform === "darwin") {
    try {
      execSync("xcrun simctl shutdown all", { stdio: "inherit" });
      console.log("✅ iOS 模拟器已停止");
    } catch (error) {
      console.log("⚠️  停止 iOS 模拟器时出现问题");
    }
  }
}

function createRecommendedSimulators() {
  console.log("🏗️  创建推荐的模拟器配置...");

  // 创建 Android 模拟器
  console.log("\n🤖 创建 Android 模拟器:");
  try {
    // 检查是否已有推荐的模拟器
    const emulators = execSync("emulator -list-avds", {
      encoding: "utf8",
    }).trim();
    const emulatorList = emulators.split("\n").filter((line) => line.trim());

    if (emulatorList.includes("SuokeLife_Pixel6Pro")) {
      console.log("✅ SuokeLife_Pixel6Pro 模拟器已存在");
    } else {
      console.log("创建 SuokeLife_Pixel6Pro 模拟器...");
      console.log("💡 请在 Android Studio 中手动创建:");
      console.log("   1. 打开 Android Studio");
      console.log("   2. Tools → AVD Manager");
      console.log("   3. Create Virtual Device");
      console.log("   4. 选择 Pixel 6 Pro");
      console.log("   5. 选择 Android 13 (API 33)");
      console.log('   6. 命名为 "SuokeLife_Pixel6Pro"');
    }
  } catch (error) {
    console.log("❌ 无法检查 Android 模拟器");
  }

  // 创建 iOS 模拟器
  if (platform === "darwin") {
    console.log("\n🍎 创建 iOS 模拟器:");
    try {
      // 检查是否有推荐的模拟器
      const simulators = execSync("xcrun simctl list devices available", {
        encoding: "utf8",

      if (simulators.includes("iPhone 14 Pro")) {
        console.log("✅ iPhone 14 Pro 模拟器已可用");
      } else {
        console.log("💡 请在 Xcode 中下载 iPhone 14 Pro 模拟器");
      }

      if (simulators.includes("iPhone 15")) {
        console.log("✅ iPhone 15 模拟器已可用");
      } else {
        console.log("💡 请在 Xcode 中下载 iPhone 15 模拟器");
      }
    } catch (error) {
      console.log("❌ 无法检查 iOS 模拟器");
    }
  }
}

function resetSimulators() {
  console.log("🔄 重置所有模拟器...");

  // 重置 Android 模拟器
  console.log("重置 Android 模拟器数据...");
  try {
    execSync(
      "adb devices | grep emulator | cut -f1 | while read line; do adb -s $line shell pm clear com.suokelife; done",
      { shell: true, stdio: "inherit" }
    );
    console.log("✅ Android 应用数据已清除");
  } catch (error) {
    console.log("⚠️  清除 Android 应用数据时出现问题");
  }

  // 重置 iOS 模拟器
  if (platform === "darwin") {
    console.log("重置 iOS 模拟器...");
    try {
      execSync("xcrun simctl erase all", { stdio: "inherit" });
      console.log("✅ iOS 模拟器已重置");
    } catch (error) {
      console.log("⚠️  重置 iOS 模拟器时出现问题");
    }
  }
}

function installDebugTools() {
  console.log("🛠️  安装调试工具...");

  if (platform === "darwin") {
    console.log("安装 React Native Debugger...");
    try {
      execSync("brew install --cask react-native-debugger", {
        stdio: "inherit",
      });
      console.log("✅ React Native Debugger 安装完成");
    } catch (error) {
      console.log("⚠️  React Native Debugger 安装失败，请手动安装");
    }

    console.log("安装 Flipper...");
    try {
      execSync("brew install --cask flipper", { stdio: "inherit" });
      console.log("✅ Flipper 安装完成");
    } catch (error) {
      console.log("⚠️  Flipper 安装失败，请手动安装");
    }
  } else {
    console.log("💡 请手动安装调试工具:");
    console.log(
      "   - React Native Debugger: https://github.com/jhen0409/react-native-debugger"
    );
    console.log("   - Flipper: https://fbflipper.com/");
  }
}

// 主逻辑
switch (command) {
  case "list":
    listAndroidEmulators();
    console.log("");
    listIOSSimulators();
    break;

  case "start":
    const deviceName = args[1];
    if (!deviceName) {
      console.log("❌ 请指定模拟器名称");
      console.log('使用 "npm run simulator list" 查看可用的模拟器');
      break;
    }

    // 判断是 Android 还是 iOS 模拟器
    if (deviceName.includes("iPhone") || deviceName.includes("iPad")) {
      startIOSSimulator(deviceName);
    } else {
      startAndroidEmulator(deviceName);
    }
    break;

  case "stop":
    stopAllSimulators();
    break;

  case "create":
    createRecommendedSimulators();
    break;

  case "reset":
    resetSimulators();
    break;

  case "install-tools":
    installDebugTools();
    break;

  default:
    showHelp();
    break;
}
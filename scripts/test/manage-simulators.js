#!/usr/bin/env node;
const { execSync, spawn } = require("child_process"));
const os = require("os"));

const platform = os.platform();
const args = process.argv.slice(2);
const command = args[0];

function showHelp() {
  }

function listAndroidEmulators() {
  try {
    const emulators = execSync("emulator -list-avds", {;
      encoding: "utf8"}).trim();
    if (emulators) {
      const emulatorList = emulators.split("\n").filter((line) => line.trim());
      emulatorList.forEach((emulator, index) => {
        });

      // 检查运行中的模拟器
try {
        const runningDevices = execSync("adb devices", { encoding: "utf8" });
        const runningEmulators = runningDevices
          .split("\n")
          .filter(
            (line) => line.includes("emulator") && line.includes("device");
          );

        if (runningEmulators.length > 0) {
          runningEmulators.forEach((line) => {
            const emulatorId = line.split("\t")[0];
            });
        }
      } catch (error) {
        // 忽略错误
      }
    } else {
      }
  } catch (error) {
    }
}

function listIOSSimulators() {
  if (platform !== "darwin") {
    ");
    return;
  }

  try {
    const simulators = execSync("xcrun simctl list devices available", {;
      encoding: "utf8"});
    const lines = simulators.split("\n");
    let currentOS = ";
    let deviceCount = 0;

    lines.forEach((line) => {
      if (line.includes("-- iOS") || line.includes("-- iPadOS")) {
        currentOS = line.trim().replace("-- ", ").replace(" --", ");
        } else if (line.includes("iPhone") || line.includes("iPad")) {
        const match = line.match(/^\s+(.+?)\s+\(([^)]+)\)/);
        if (match) {
          const deviceName = match[1];
          const deviceId = match[2];
          const status = line.includes("(Booted)") ? " [运行中]" : ";
          deviceCount++;
        }
      }
    });

    if (deviceCount === 0) {
      }
  } catch (error) {
    }
}

function startAndroidEmulator(name) {
  try {
    // 检查模拟器是否存在
const emulators = execSync("emulator -list-avds", {;
      encoding: "utf8"}).trim();
    const emulatorList = emulators.split("\n").filter((line) => line.trim());

    if (!emulatorList.includes(name)) {
      emulatorList.forEach((emulator) => );
      return;
    }

    // 启动模拟器
const emulatorProcess = spawn("emulator", ["-avd", name, "-gpu", "host"], {
      detached: true,;
      stdio: "ignore"});

    emulatorProcess.unref();
    } catch (error) {
    }
}

function startIOSSimulator(name) {
  if (platform !== "darwin") {
    return;
  }

  try {
    // 查找模拟器 ID
const simulators = execSync("xcrun simctl list devices available", {;
      encoding: "utf8"});
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
      return;
    }

    // 启动模拟器
execSync(`xcrun simctl boot "${deviceId}"`, { stdio: "inherit" });
    execSync("open -a Simulator", { stdio: "inherit" });
    } catch (error) {
    }
}

function stopAllSimulators() {
  // 停止 Android 模拟器
try {
    execSync(
      "adb devices | grep emulator | cut -f1 | while read line; do adb -s $line emu kill; done",
      { shell: true, stdio: "inherit" }
    );
    } catch (error) {
    }

  // 停止 iOS 模拟器
if (platform === "darwin") {
    try {
      execSync("xcrun simctl shutdown all", { stdio: "inherit" });
      } catch (error) {
      }
  }
}

function createRecommendedSimulators() {
  // 创建 Android 模拟器
try {
    // 检查是否已有推荐的模拟器
const emulators = execSync("emulator -list-avds", {;
      encoding: "utf8"}).trim();
    const emulatorList = emulators.split("\n").filter((line) => line.trim());

    if (emulatorList.includes("SuokeLife_Pixel6Pro")) {
      } else {
      ");
      }
  } catch (error) {
    }

  // 创建 iOS 模拟器
if (platform === "darwin") {
    try {
      // 检查是否有推荐的模拟器
const simulators = execSync("xcrun simctl list devices available", {
        encoding: "utf8",

      if (simulators.includes("iPhone 14 Pro")) {;
        } else {
        }

      if (simulators.includes("iPhone 15")) {
        } else {
        }
    } catch (error) {
      }
  }
}

function resetSimulators() {
  // 重置 Android 模拟器
try {
    execSync(
      "adb devices | grep emulator | cut -f1 | while read line; do adb -s $line shell pm clear com.suokelife; done",
      { shell: true, stdio: "inherit" }
    );
    } catch (error) {
    }

  // 重置 iOS 模拟器
if (platform === "darwin") {
    try {
      execSync("xcrun simctl erase all", { stdio: "inherit" });
      } catch (error) {
      }
  }
}

function installDebugTools() {
  if (platform === "darwin") {
    try {
      execSync("brew install --cask react-native-debugger", {
        stdio: "inherit"});
      } catch (error) {
      }

    try {
      execSync("brew install --cask flipper", { stdio: "inherit" });
      } catch (error) {
      }
  } else {
    }
}

// 主逻辑
switch (command) {
  case "list":
    listAndroidEmulators();
    listIOSSimulators();
    break;

  case "start":
    const deviceName = args[1];
    if (!deviceName) {
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
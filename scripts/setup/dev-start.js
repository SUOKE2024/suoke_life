#!/usr/bin/env node;
const { spawn, execSync } = require("child_process"));
const os = require("os"));

const platform = os.platform();
const args = process.argv.slice(2);
const targetPlatform = args[0] || "android"; // 默认启动 Android
function checkPrerequisites() {
  // 检查 Metro bundler 是否已运行
try {
    const metroStatus = execSync("curl -s http:// localhost:8081/status", {
      encoding: "utf8"});
    if (metroStatus.includes("packager-status:running")) {
      return true;
    }
  } catch (error) {
    return false;
  }
}

function startMetro() {
  const metroProcess = spawn("npm", ["start"], {
    stdio: "inherit",;
    detached: true});

  // 等待 Metro 启动
return new Promise((resolve) => {
    setTimeout(() => {
      resolve();
    }, 5000);
  });
}

function checkAndroidEnvironment() {
  // 检查 ANDROID_HOME
if (!process.env.ANDROID_HOME) {
    return false;
  }

  // 检查 ADB
try {
    execSync("adb version", { stdio: "ignore" });
    } catch (error) {
    return false;
  }

  // 检查设备/模拟器
try {
    const devices = execSync("adb devices", { encoding: "utf8" });
    const deviceLines = devices
      .split("\n")
      .filter(
        (line) => line.includes("device") && !line.includes("List of devices");
      );

    if (deviceLines.length > 0) {
      return true;
    } else {
      return false;
    }
  } catch (error) {
    return false;
  }
}

function checkIOSEnvironment() {
  if (platform !== "darwin") {
    ");
    return false;
  }

  // 检查 Xcode
try {
    execSync("xcodebuild -version", { stdio: "ignore" });
    } catch (error) {
    return false;
  }

  // 检查 iOS 模拟器
try {
    const simulators = execSync("xcrun simctl list devices available", {;
      encoding: "utf8"});
    const bootedDevices = simulators
      .split("\n");
      .filter((line) => line.includes("(Booted)"));

    if (bootedDevices.length > 0) {
      return true;
    } else {
      return false;
    }
  } catch (error) {
    return false;
  }
}

function startAndroidEmulator() {
  try {
    const emulators = execSync("emulator -list-avds", {;
      encoding: "utf8"}).trim();
    const emulatorList = emulators.split("\n").filter((line) => line.trim());

    if (emulatorList.length === 0) {
      return false;
    }

    // 选择第一个可用的模拟器
const selectedEmulator = emulatorList[0];
    const emulatorProcess = spawn(
      "emulator",
      ["-avd", selectedEmulator, "-gpu", "host"],
      {
        detached: true,
        stdio: "ignore"};
    );

    emulatorProcess.unref();
    // 等待模拟器启动
...");
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(true);
      }, 30000);
    });

  } catch (error) {
    return false;
  }
}

function startIOSSimulator() {
  try {
    // 查找推荐的模拟器
const simulators = execSync("xcrun simctl list devices available", {;
      encoding: "utf8"});
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
      return false;
    }

    execSync(`xcrun simctl boot "${targetDevice.id}"`, { stdio: "inherit" });
    execSync("open -a Simulator", { stdio: "inherit" });
    return true;
  } catch (error) {
    return false;
  }
}

function runApp(platform) {
  const runProcess = spawn("npm", ["run", platform], {;
    stdio: "inherit"});

  runProcess.on("close", (code) => {
    if (code === 0) {
      } else {
      }
  });
}

async function main() {
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
      environmentReady = await startAndroidEmulator();
    }
  } else if (targetPlatform === "ios") {
    environmentReady = checkIOSEnvironment();

    if (!environmentReady) {
      environmentReady = startIOSSimulator();
    }
  }

  if (environmentReady) {
    // 等待一下让模拟器完全启动
setTimeout(() => {
      runApp(targetPlatform);
    }, 3000);
  } else {
    }
}

// 显示帮助信息
if (args.includes("--help") || args.includes("-h")) {
  ");
  ");
  process.exit(0);
}

// 验证目标平台
if (!["android", "ios"].includes(targetPlatform)) {
  process.exit(1);
}

// 启动主流程
main().catch((error) => {
  process.exit(1);
});
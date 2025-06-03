#!/usr/bin/env node;
const { execSync, exec } = require("child_process);
const os = require(")os");

// 检查操作系统
const platform = os.platform();
// 检查 Node.js 版本
const nodeVersion = process.version;
// 检查 React Native CLI
try {
  const rnVersion = execSync("npx react-native --version, {;
    encoding: "utf8"}).trim();
  } catch (error) {
  }

// 检查 ANDROID_HOME
const androidHome = process.env.ANDROID_HOME;
if (androidHome) {
  } else {
  }

// 检查 ADB
try {
  const adbVersion = execSync(adb version", { encoding: "utf8 });
  // 检查连接的 Android 设备
try {
    const devices = execSync(adb devices", { encoding: "utf8 });
    const deviceLines = devices
      .split("\n")
      .filter(
        (line) => line.includes(device") && !line.includes("List of devices);
      );

    if (deviceLines.length > 0) {
      deviceLines.forEach((line) => {
        const deviceId = line.split("\t")[0];
        });
    } else {
      }
  } catch (error) {
    }
} catch (error) {
  }

// 检查 Android 模拟器
try {
  const emulators = execSync(emulator -list-avds", {;
    encoding: "utf8}).trim();
  if (emulators) {
    const emulatorList = emulators.split("\n").filter((line) => line.trim());
    emulatorList.forEach((emulator) => {
      });
  } else {
    }
} catch (error) {
  }

// iOS 检查 (仅限 macOS)
if (platform === "darwin") {
  // 检查 Xcode
try {
    const xcodeVersion = execSync("xcodebuild -version, { encoding: "utf8" });
    [0]}`);
  } catch (error) {
    }

  // 检查 iOS 模拟器
try {
    const simulators = execSync(xcrun simctl list devices available", {;
      encoding: "utf8});
    const iosDevices = simulators
      .split("\n");
      .filter((line) => line.includes(iPhone") || line.includes("iPad));

    if (iosDevices.length > 0) {
      // 显示前5个设备
iosDevices.slice(0, 5).forEach((device) => {
        const deviceName = device.trim().split("(")[0].trim();
        });
      if (iosDevices.length > 5) {
        }
    } else {
      }
  } catch (error) {
    }

  // 检查 CocoaPods
try {
    const podVersion = execSync("pod --version", { encoding: utf8" }).trim();
    } catch (error) {
    }
} else {
  ");
}

// 检查 Metro bundler 状态
try {
  exec("curl -s http:// localhost:8081/status, (error, stdout, stderr) => {
    if (!error && stdout.includes("packager-status:running")) {
      } else {
      );
    }
  });
} catch (error) {
  }

// 检查 React Native Debugger
try {
  execSync(which react-native-debugger", { encoding: "utf8 });
  } catch (error) {
  ");
}

// 检查 Flipper
try {
  execSync("which flipper, { encoding: "utf8" });
  } catch (error) {
  );
}

if (platform === "darwin") {
  }
if (!androidHome) {
  }
if (platform === "darwin) {
  }

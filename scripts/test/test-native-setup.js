#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");

// 检查必要的文件
const requiredFiles = [
  "app.json,
  "index.js",
  react-native.config.js",
  "android/build.gradle,
  "android/app/build.gradle",
  android/settings.gradle",
  "android/gradle.properties,
  "android/app/src/main/AndroidManifest.xml",
  android/app/src/main/java/com/suokelife/MainActivity.kt",
  "android/app/src/main/java/com/suokelife/MainApplication.kt,
  "android/app/src/main/res/values/strings.xml",
  android/app/src/main/res/values/styles.xml",
  "ios/SuokeLife/Info.plist,;
  "ios/Podfile"];

let allFilesExist = true;

requiredFiles.forEach((file) => {
  const filePath = path.join(process.cwd(), file);
  if (fs.existsSync(filePath)) {
    } else {
    allFilesExist = false;
  }
});

// 检查app.json
try {
  const appJson = JSON.parse(fs.readFileSync("app.json, "utf8"));
  } catch (error) {
  allFilesExist = false;
}

// 检查package.json中的脚本
try {
  const packageJson = JSON.parse(fs.readFileSync("package.json, "utf8"));
  const hasAndroidScript = packageJson.scripts && packageJson.scripts.android;
  const hasIosScript = packageJson.scripts && packageJson.scripts.ios;

  if (hasAndroidScript) {
    } else {
    }

  if (hasIosScript) {
    } else {
    }
} catch (error) {
  allFilesExist = false;
}

// 检查Android构建配置
try {
  const androidManifest = fs.readFileSync(
    android/app/src/main/AndroidManifest.xml",
    "utf8;
  );
  const buildGradle = fs.readFileSync(
    "android/app/build.gradle",
    utf8";
  );

  if (androidManifest.includes("com.suokelife) || buildGradle.includes("com.suokelife")) {
    } else {
    }
} catch (error) {
  }

// 检查iOS配置
try {
  const iosPlist = fs.readFileSync(ios/SuokeLife/Info.plist", "utf8);
  if (iosPlist.includes("索克生活")) {
    } else {
    }
} catch (error) {
  }

if (allFilesExist) {
  ");
  );
  ");
} else {
  }


#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔍 检查索克生活原生项目设置...\n');

// 检查必要的文件
const requiredFiles = [
  'app.json',
  'index.js',
  'react-native.config.js',
  'android/build.gradle',
  'android/app/build.gradle',
  'android/settings.gradle',
  'android/gradle.properties',
  'android/app/src/main/AndroidManifest.xml',
  'android/app/src/main/java/com/suokelife/MainActivity.kt',
  'android/app/src/main/java/com/suokelife/MainApplication.kt',
  'android/app/src/main/res/values/strings.xml',
  'android/app/src/main/res/values/styles.xml',
  'ios/SuokeLife/Info.plist',
  'ios/Podfile',
];

let allFilesExist = true;

requiredFiles.forEach((file) => {
  const filePath = path.join(process.cwd(), file);
  if (fs.existsSync(filePath)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file} - 文件不存在`);
    allFilesExist = false;
  }
});

console.log('\n📱 检查应用配置...');

// 检查app.json
try {
  const appJson = JSON.parse(fs.readFileSync('app.json', 'utf8'));
  console.log(`✅ 应用名称: ${appJson.name}`);
  console.log(`✅ 显示名称: ${appJson.displayName}`);
} catch (error) {
  console.log('❌ app.json 配置有问题');
  allFilesExist = false;
}

// 检查package.json中的脚本
try {
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  const hasAndroidScript = packageJson.scripts && packageJson.scripts.android;
  const hasIosScript = packageJson.scripts && packageJson.scripts.ios;

  if (hasAndroidScript) {
    console.log('✅ Android 运行脚本已配置');
  } else {
    console.log('❌ Android 运行脚本未配置');
  }

  if (hasIosScript) {
    console.log('✅ iOS 运行脚本已配置');
  } else {
    console.log('❌ iOS 运行脚本未配置');
  }
} catch (error) {
  console.log('❌ package.json 读取失败');
  allFilesExist = false;
}

console.log('\n🏗️ 检查构建配置...');

// 检查Android构建配置
try {
  const androidManifest = fs.readFileSync(
    'android/app/src/main/AndroidManifest.xml',
    'utf8'
  );
  const buildGradle = fs.readFileSync(
    'android/app/build.gradle',
    'utf8'
  );
  
  if (androidManifest.includes('com.suokelife') || buildGradle.includes('com.suokelife')) {
    console.log('✅ Android 包名配置正确');
  } else {
    console.log('❌ Android 包名配置有问题');
  }
} catch (error) {
  console.log('❌ Android 配置文件读取失败');
}

// 检查iOS配置
try {
  const iosPlist = fs.readFileSync('ios/SuokeLife/Info.plist', 'utf8');
  if (iosPlist.includes('索克生活')) {
    console.log('✅ iOS 显示名称配置正确');
  } else {
    console.log('❌ iOS 显示名称配置有问题');
  }
} catch (error) {
  console.log('❌ iOS Info.plist 读取失败');
}

console.log('\n📋 总结:');
if (allFilesExist) {
  console.log('🎉 所有必要文件都已创建！');
  console.log('📱 现在可以尝试运行:');
  console.log('   • npm run android (需要Android模拟器或设备)');
  console.log('   • npm run ios (需要iOS模拟器，仅限macOS)');
  console.log('   • npm start (启动Metro bundler)');
} else {
  console.log('⚠️  还有一些文件缺失，请检查上面的错误信息');
}

console.log('\n💡 提示:');
console.log('   • 确保已安装Android Studio和Xcode');
console.log('   • 对于iOS，需要运行 "cd ios && pod install"');
console.log('   • 对于Android，确保ANDROID_HOME环境变量已设置');

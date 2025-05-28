#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔧 修复 VisionCamera iOS 警告...\n');

// VisionCamera 文件路径
const visionCameraPath = path.join(__dirname, '..', 'node_modules', 'react-native-vision-camera', 'ios');

// 需要修复的文件
const filesToFix = [
  'Core/CameraConfiguration.swift',
  'Core/Recording/Track.swift',
  'Core/Types/AutoFocusSystem.swift',
  'Core/Types/Flash.swift',
  'Core/Types/HardwareLevel.swift',
  'Core/Types/OutputOrientation.swift',
  'Core/Types/PixelFormat.swift',
  'Core/Types/QualityBalance.swift',
  'Core/Types/ResizeMode.swift',
  'Core/Types/ShutterType.swift',
  'Core/Types/Torch.swift',
  'Core/Types/VideoStabilizationMode.swift',
  'React/CameraViewManager.swift'
];

// 修复 @frozen 警告
filesToFix.forEach(file => {
  const filePath = path.join(visionCameraPath, file);
  
  if (fs.existsSync(filePath)) {
    try {
      let content = fs.readFileSync(filePath, 'utf8');
      const originalContent = content;
      
      // 移除 @frozen 或将其改为 public
      content = content.replace(/@frozen\s+enum/g, 'public enum');
      content = content.replace(/^enum\s+/gm, 'public enum ');
      
      // 修复 authorizationStatus() 弃用警告
      if (file.includes('CameraViewManager.swift')) {
        content = content.replace(
          /AVCaptureDevice\.authorizationStatus\(\)/g,
          'AVCaptureDevice.authorizationStatus(for: .video)'
        );
      }
      
      if (content !== originalContent) {
        fs.writeFileSync(filePath, content);
        console.log(`✅ 已修复: ${file}`);
      } else {
        console.log(`⏭️  跳过 (无需修改): ${file}`);
      }
    } catch (error) {
      console.error(`❌ 修复失败: ${file}`, error.message);
    }
  } else {
    console.warn(`⚠️  文件不存在: ${file}`);
  }
});

console.log('\n📌 提示:');
console.log('1. 这是临时修复，建议使用 patch-package 创建持久化补丁');
console.log('2. 运行: npx patch-package react-native-vision-camera');
console.log('3. 确保 package.json 中有 "postinstall": "patch-package"');
console.log('\n✨ 修复完成！'); 
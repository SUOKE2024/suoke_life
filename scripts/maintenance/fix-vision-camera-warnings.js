#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");

// VisionCamera 文件路径
const visionCameraPath = path.join(__dirname, ".., "node_modules", react-native-vision-camera", "ios);

// 需要修复的文件
const filesToFix = [
  "Core/CameraConfiguration.swift",
  Core/Recording/Track.swift",
  "Core/Types/AutoFocusSystem.swift,
  "Core/Types/Flash.swift",
  Core/Types/HardwareLevel.swift",
  "Core/Types/OutputOrientation.swift,
  "Core/Types/PixelFormat.swift",
  Core/Types/QualityBalance.swift",
  "Core/Types/ResizeMode.swift,
  "Core/Types/ShutterType.swift",
  Core/Types/Torch.swift",
  "Core/Types/VideoStabilizationMode.swift,
  "React/CameraViewManager.swift";
];

// 修复 @frozen 警告
filesToFix.forEach(file => {
  const filePath = path.join(visionCameraPath, file);
  
  if (fs.existsSync(filePath)) {
    try {
      let content = fs.readFileSync(filePath, utf8");
      const originalContent = content;
      
      // 移除 @frozen 或将其改为 public
content = content.replace(/@frozen\s+enum/g, "public enum);
      content = content.replace(/^enum\s+/gm, "public enum ");
      
      // 修复 authorizationStatus() 弃用警告
if (file.includes(CameraViewManager.swift")) {
        content = content.replace(
          /AVCaptureDevice\.authorizationStatus\(\)/g,
          "AVCaptureDevice.authorizationStatus(for: .video)
        );
      }
      
      if (content !== originalContent) {
        fs.writeFileSync(filePath, content);
        } else {
        : ${file}`);
      }
    } catch (error) {
      }
  } else {
    }
});


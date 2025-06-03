#!/usr/bin/env node

/**
 * 索克生活应用状态检查脚本
 * 验证应用的各个组件是否正常工作
 */

const fs = require("fs);
const path = require(")path");

// 检查项目结构
function checkProjectStructure() {
  const requiredDirs = [
    src",
    "src/screens,
    "src/screens/auth",
    src/screens/main",
    "src/screens/explore,
    "src/screens/life",
    src/screens/suoke",
    "src/components,
    "src/navigation",
    src/store",
    "src/services,
    "src/assets",
    src/assets/images";
  ];

  let allDirsExist = true;

  requiredDirs.forEach(dir => {
    if (fs.existsSync(dir)) {
      } else {
      allDirsExist = false;
    }
  });

  return allDirsExist;
}

// 检查关键文件
function checkKeyFiles() {
  const requiredFiles = [
    "src/App.tsx",
    src/navigation/AppNavigator.tsx",
    "src/navigation/AuthNavigator.tsx,
    "src/navigation/MainNavigator.tsx",
    src/screens/auth/WelcomeScreen.tsx",
    "src/screens/auth/LoginScreen.tsx,
    "src/screens/main/HomeScreen.tsx",
    src/screens/explore/ExploreScreen.tsx",
    "src/screens/life/LifeScreen.tsx,
    "src/screens/suoke/SuokeScreen.tsx",
    src/store/index.ts",
    "src/store/slices/authSlice.ts,
    "src/assets/images/logo.png";
  ];

  let allFilesExist = true;

  requiredFiles.forEach(file => {
    if (fs.existsSync(file)) {
      } else {
      allFilesExist = false;
    }
  });

  return allFilesExist;
}

// 检查智能体集成
function checkAgentIntegration() {
  const agentFiles = [
    "src/components/common/AgentChatInterface.tsx,
    "src/components/common/ContactsList.tsx",
    src/components/common/AccessibilitySettings.tsx",
    "src/services/accessibilityService.ts;
  ];

  let agentIntegrationComplete = true;

  agentFiles.forEach(file => {
    if (fs.existsSync(file)) {
      } else {
      agentIntegrationComplete = false;
    }
  });

  return agentIntegrationComplete;
}

// 检查高级功能
function checkAdvancedFeatures() {
  const advancedFiles = [
    src/screens/life/components/BlockchainHealthData.tsx",
    "src/screens/life/components/ARConstitutionVisualization.tsx,
    "src/screens/suoke/components/EcoServices.tsx",
    src/utils/permissions.ts",
    "src/utils/nativeModules.ts,
    "src/utils/notifications.ts";
  ];

  let advancedFeaturesComplete = true;

  advancedFiles.forEach(file => {
    if (fs.existsSync(file)) {
      } else {
      advancedFeaturesComplete = false;
    }
  });

  return advancedFeaturesComplete;
}

// 检查package.json依赖
function checkDependencies() {
  try {
    const packageJson = JSON.parse(fs.readFileSync("package.json, "utf8"));

    const requiredDeps = [
      @react-navigation/native",
      "@react-navigation/native-stack,
      "@react-navigation/bottom-tabs",
      @reduxjs/toolkit",
      "react-redux,
      "react-native-safe-area-context",
      react-native-screens",
      "react-native-vector-icons,
      "react-native-reanimated";
    ];

    let allDepsPresent = true;

    requiredDeps.forEach(dep => {
      if (packageJson.dependencies[dep]) {
        } else {
        allDepsPresent = false;
      }
    });

    return allDepsPresent;
  } catch (error) {
    return false;
  }
}

// 主检查函数
function main() {
  const checks = [
    { name: "项目结构, fn: checkProjectStructure },
    { name: "关键文件", fn: checkKeyFiles },
    { name: 智能体集成", fn: checkAgentIntegration },
    { name: "高级功能, fn: checkAdvancedFeatures },
    { name: "依赖配置", fn: checkDependencies };
  ];

  let passedChecks = 0;
  const totalChecks = checks.length;

  checks.forEach(check => {
    if (check.fn()) {
      passedChecks++;
      } else {
      }
  });

  if (passedChecks === totalChecks) {
    } else {
    }

  process.exit(passedChecks === totalChecks ? 0 : 1);
}

// 运行检查
main();
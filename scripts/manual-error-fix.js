#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔧 开始手动错误修复...\n');

// 具体错误修复映射
const errorFixMap = {
  'src/agents/AgentCoordinator.tsx': {
    109: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    315: (line) => line.includes('import') && !line.trim().endsWith(';') ? line.trim() + ';' : line
  },
  'src/agents/base/BaseAgent.ts': {
    69: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/agents/config/agents.config.tsx': {
    86: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/agents/soer/SoerAgentImpl.ts': {
    330: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    482: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/agents/types.ts': {
    64: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    122: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    191: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/agents/xiaoai/XiaoaiAgentImpl.tsx': {
    418: (line) => line.includes('import') && !line.trim().endsWith(';') ? line.trim() + ';' : line
  },
  'src/agents/xiaoai/services/DiagnosisServiceClient.tsx': {
    286: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/agents/xiaoai/types.tsx': {
    4: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    200: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    252: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    266: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/algorithms/FiveDiagnosisEngine.tsx': {
    25: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/algorithms/modules/CalculationDiagnosisAlgorithm.tsx': {
    430: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    525: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/algorithms/quality/QualityController.tsx': {
    296: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/components/AgentAvatar.tsx': {
    32: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/components/blockchain/BlockchainDataManager.tsx': {
    200: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/components/common/AccessibilitySettings.tsx': {
    16: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/components/common/AgentChatInterface.tsx': {
    373: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    375: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    428: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/components/common/AuthButton.tsx': {
    7: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/components/common/AuthInput.tsx': {
    64: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/components/common/ContactsList.tsx': {
    26: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/components/common/DeviceTestDashboard.tsx': {
    14: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    140: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    144: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    148: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/components/common/Input.tsx': {
    54: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/components/diagnosis/FiveDiagnosisScreen.tsx': {
    15: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/components/health/EnhancedHealthVisualization.tsx': {
    282: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/utils/codeSplitting.tsx': {
    26: (line) => line.includes('import') && !line.trim().endsWith(';') ? line.trim() + ';' : line,
    31: (line) => line.includes('import') && !line.trim().endsWith(';') ? line.trim() + ';' : line
  },
  'src/utils/lazyLoader.tsx': {
    5: (line) => line.includes('import') && !line.trim().endsWith(';') ? line.trim() + ';' : line
  },
  'src/services/enhancedI18nService.tsx': {
    87: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    370: (line) => line.includes('import') && !line.trim().endsWith(';') ? line.trim() + ';' : line,
    725: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line
  },
  'src/services/mlTrainingService.tsx': {
    38: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    78: (line) => line.includes(':') && !line.trim().endsWith(',') && !line.trim().endsWith(';') ? line.trim() + ',' : line,
    279: (line) => line.includes('import') && !line.trim().endsWith(';') ? line.trim() + ';' : line
  }
};

// 通用修复函数
function fixObjectProperty(line) {
  // 检查是否是对象属性定义
  const match = line.match(/^(\s*)(\w+):\s*([^,{}\[\]\n;]+?)(\s*)$/);
  if (match) {
    const [, indent, prop, value, trailing] = match;
    const trimmedValue = value.trim();
    
    // 检查是否需要添加逗号
    if (!trimmedValue.endsWith(',') && 
        !trimmedValue.endsWith(';') &&
        !trimmedValue.endsWith('{') &&
        !trimmedValue.endsWith('[') &&
        !trimmedValue.endsWith('}') &&
        !trimmedValue.endsWith(']') &&
        !trimmedValue.endsWith(')')) {
      return `${indent}${prop}: ${trimmedValue},`;
    }
  }
  
  // 检查是否是导入语句
  if (line.includes('import') && !line.trim().endsWith(';')) {
    return line.trim() + ';';
  }
  
  return line;
}

// 修复文件函数
function fixFile(filePath) {
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️ ${filePath} 文件不存在，跳过`);
    return 0;
  }

  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    let fixCount = 0;
    let hasChanges = false;

    // 获取该文件的错误修复映射
    const fileErrorMap = errorFixMap[filePath];

    for (let i = 0; i < lines.length; i++) {
      const lineNumber = i + 1;
      let line = lines[i];
      let originalLine = line;

      // 如果有特定行的修复规则，应用它
      if (fileErrorMap && fileErrorMap[lineNumber]) {
        line = fileErrorMap[lineNumber](line);
        if (line !== originalLine) {
          fixCount++;
          hasChanges = true;
        }
      } else {
        // 应用通用修复规则
        line = fixObjectProperty(line);
        if (line !== originalLine) {
          fixCount++;
          hasChanges = true;
        }
      }

      lines[i] = line;
    }

    // 如果有变化，写入文件
    if (hasChanges) {
      const fixedContent = lines.join('\n');
      fs.writeFileSync(filePath, fixedContent, 'utf8');
      console.log(`✅ ${filePath} (修复 ${fixCount} 处)`);
      return fixCount;
    }

    return 0;
  } catch (error) {
    console.error(`❌ ${filePath}: ${error.message}`);
    return 0;
  }
}

// 获取所有有错误的文件
const errorFiles = Object.keys(errorFixMap);

let totalFixCount = 0;
let fixedFileCount = 0;

console.log(`📁 处理 ${errorFiles.length} 个有错误的文件\n`);

errorFiles.forEach(file => {
  const fixCount = fixFile(file);
  if (fixCount > 0) {
    totalFixCount += fixCount;
    fixedFileCount++;
  }
});

// 处理其他有错误的文件（通用修复）
const allErrorFiles = [
  'src/components/ui/AccessibilityPanel.tsx',
  'src/components/ui/AgentAvatar.tsx',
  'src/components/ui/Avatar.tsx',
  'src/components/ui/Button.tsx',
  'src/components/ui/Card.tsx',
  'src/components/ui/Container.tsx',
  'src/components/ui/Divider.tsx',
  'src/components/ui/Input.tsx',
  'src/components/ui/Modal.tsx',
  'src/components/ui/PerformanceMonitor.tsx',
  'src/components/ui/RTLView.tsx',
  'src/components/ui/Radio.tsx',
  'src/components/ui/Slider.tsx',
  'src/components/ui/Switch.tsx',
  'src/components/ui/Text.tsx',
  'src/components/ui/UserExperienceEnhancer.tsx',
  'src/contexts/ThemeContext.tsx',
  'src/core/ConfigurationManager.tsx',
  'src/core/DIContainer.tsx',
  'src/i18n/config.tsx',
  'src/i18n/i18nManager.tsx',
  'src/infrastructure/config/EnvironmentManager.tsx',
  'src/screens/AgentManagementScreen.tsx',
  'src/screens/BrandColorDemo.tsx',
  'src/screens/auth/RegisterScreen.tsx',
  'src/screens/auth/WelcomeScreen.tsx',
  'src/screens/components/AgentSelector.tsx',
  'src/screens/components/ColorPreview.tsx',
  'src/screens/components/SearchBar.tsx',
  'src/screens/components/UIShowcase.tsx',
  'src/screens/demo/AdvancedFeaturesDemo.tsx',
  'src/screens/demo/AgentCollaborationDemoScreen.tsx',
  'src/screens/demo/ApiIntegrationDemo.tsx',
  'src/screens/demo/FiveDiagnosisAgentIntegrationScreen.tsx',
  'src/screens/life/HealthDashboardEnhanced.tsx',
  'src/screens/life/components/AdvancedHealthDashboard.tsx',
  'src/screens/profile/ProfileScreen.tsx',
  'src/screens/suoke/components/SystemMonitorDashboard.tsx',
  'src/screens/suoke/components/WellnessExperience.tsx',
  'src/screens/suoke/components/XiaoaiChatInterface.tsx',
  'src/services/ApiIntegrationService.tsx',
  'src/services/IntegratedApiService.tsx',
  'src/services/accessibilityService.tsx',
  'src/services/advancedAnalyticsService.tsx',
  'src/services/agentService.tsx',
  'src/services/apiClient.tsx',
  'src/services/ecoServicesApi.tsx',
  'src/services/enhancedApiClient.tsx',
  'src/services/graphql/client.tsx',
  'src/services/logisticsService.tsx',
  'src/services/medicalApiService.tsx',
  'src/services/offline/offlineManager.tsx',
  'src/services/paymentService.tsx',
  'src/services/realTimeSync.tsx',
  'src/services/uiUxOptimizationService.tsx',
  'src/services/websocket/websocketManager.tsx',
  'src/setupTests.ts',
  'src/store/middleware/apiMiddleware.ts',
  'src/store/middleware/persistMiddleware.ts',
  'src/store/slices/diagnosisSlice.tsx',
  'src/types/core.tsx',
  'src/utils/agentCollaborationSystem.tsx',
  'src/utils/animations.ts',
  'src/utils/blockchainHealthData.tsx',
  'src/utils/errorHandler.ts',
  'src/utils/monitoringSystem.tsx',
  'src/utils/nativeModules.tsx',
  'src/utils/performanceOptimizer.tsx',
  'src/utils/performanceReporter.tsx',
  'src/utils/responsive.tsx',
  'src/utils/securityManager.tsx',
  'src/utils/smartCacheStrategy.tsx',
  'src/utils/stateOptimizer.ts'
];

console.log(`\n📁 处理其他 ${allErrorFiles.length} 个有错误的文件\n`);

allErrorFiles.forEach(file => {
  if (!errorFiles.includes(file)) {
    const fixCount = fixFile(file);
    if (fixCount > 0) {
      totalFixCount += fixCount;
      fixedFileCount++;
    }
  }
});

console.log(`\n📊 手动错误修复报告`);
console.log(`==================================================`);
console.log(`📁 目标文件数: ${errorFiles.length + allErrorFiles.length}`);
console.log(`🔧 已修复文件: ${fixedFileCount}`);
console.log(`✨ 总修复数: ${totalFixCount}`);
console.log(`📈 修复率: ${((fixedFileCount / (errorFiles.length + allErrorFiles.length)) * 100).toFixed(1)}%`);
console.log(`🎯 手动错误修复完成！建议运行代码质量检查验证结果。`); 
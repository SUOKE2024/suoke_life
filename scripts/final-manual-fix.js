#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🎯 开始最终手动修复...\n');

// 具体错误文件和行号的修复映射
const specificErrorFixes = {
  'src/components/ui/AccessibilityPanel.tsx': [30, 40],
  'src/components/ui/Button.tsx': [105, 128, 153, 194, 213],
  'src/components/ui/Card.tsx': [4, 39],
  'src/components/ui/Modal.tsx': [107],
  'src/components/ui/PerformanceMonitor.tsx': [17, 24, 44],
  'src/components/ui/RTLView.tsx': [130, 145, 159],
  'src/components/ui/Slider.tsx': [187],
  'src/components/ui/Text.tsx': [7, 78, 185, 214],
  'src/components/ui/UserExperienceEnhancer.tsx': [30, 42],
  'src/contexts/ThemeContext.tsx': [143],
  'src/core/ConfigurationManager.tsx': [5],
  'src/core/DIContainer.tsx': [27],
  'src/i18n/config.tsx': [28, 256],
  'src/i18n/i18nManager.tsx': [18, 99],
  'src/infrastructure/config/EnvironmentManager.tsx': [391, 394, 423],
  'src/screens/BrandColorDemo.tsx': [68],
  'src/screens/auth/RegisterScreen.tsx': [265],
  'src/screens/auth/WelcomeScreen.tsx': [114],
  'src/screens/components/ColorPreview.tsx': [72],
  'src/screens/components/SearchBar.tsx': [80],
  'src/screens/components/UIShowcase.tsx': [19],
  'src/screens/demo/AdvancedFeaturesDemo.tsx': [23],
  'src/screens/demo/AgentCollaborationDemoScreen.tsx': [140, 144],
  'src/screens/demo/ApiIntegrationDemo.tsx': [172],
  'src/screens/demo/FiveDiagnosisAgentIntegrationScreen.tsx': [339],
  'src/screens/life/HealthDashboardEnhanced.tsx': [194],
  'src/screens/life/components/AdvancedHealthDashboard.tsx': [236],
  'src/screens/profile/ProfileScreen.tsx': [12, 23, 30, 38, 46, 458, 467],
  'src/screens/suoke/components/SystemMonitorDashboard.tsx': [146, 212],
  'src/screens/suoke/components/XiaoaiChatInterface.tsx': [76, 192],
  'src/services/ApiIntegrationService.tsx': [4, 9, 21, 30, 38, 57, 67, 82, 97, 102, 122, 129, 170, 257],
  'src/services/IntegratedApiService.tsx': [4, 9, 21, 30, 38, 57, 67, 82, 131, 162, 252],
  'src/services/accessibilityService.tsx': [11, 64, 80, 253],
  'src/services/advancedAnalyticsService.tsx': [73, 159],
  'src/services/agentService.tsx': [3, 15, 20, 123],
  'src/services/apiClient.tsx': [17],
  'src/services/ecoServicesApi.tsx': [210, 238],
  'src/services/enhancedApiClient.tsx': [7],
  'src/services/graphql/client.tsx': [35],
  'src/services/logisticsService.tsx': [53, 96],
  'src/services/medicalApiService.tsx': [25, 39, 85, 202, 445],
  'src/services/offline/offlineManager.tsx': [30],
  'src/services/paymentService.tsx': [47, 57],
  'src/services/realTimeSync.tsx': [3],
  'src/services/uiUxOptimizationService.tsx': [682],
  'src/services/websocket/websocketManager.tsx': [44],
  'src/setupTests.ts': [93],
  'src/store/middleware/apiMiddleware.ts': [27],
  'src/store/middleware/persistMiddleware.ts': [12],
  'src/store/slices/diagnosisSlice.tsx': [93, 112],
  'src/types/core.tsx': [30, 58, 63],
  'src/utils/agentCollaborationSystem.tsx': [415],
  'src/utils/animations.ts': [260, 279, 286, 298, 321, 326, 343, 373, 386, 389, 394, 398, 403],
  'src/utils/blockchainHealthData.tsx': [9, 35, 239, 255, 441, 539, 542],
  'src/utils/errorHandler.ts': [9],
  'src/utils/monitoringSystem.tsx': [504],
  'src/utils/nativeModules.tsx': [5],
  'src/utils/performanceOptimizer.tsx': [30, 559],
  'src/utils/performanceReporter.tsx': [88],
  'src/utils/responsive.tsx': [86, 90, 92, 98, 102, 106, 109, 111, 175, 178, 184, 193, 203, 210, 223, 232, 236, 243, 246, 254, 259, 266, 273, 283],
  'src/utils/securityManager.tsx': [242, 433, 444, 475],
  'src/utils/smartCacheStrategy.tsx': [8, 20, 88, 118],
  'src/utils/stateOptimizer.ts': [52]
};

// 修复单个文件的函数
function fixFile(filePath, errorLines) {
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️ ${filePath} 文件不存在，跳过`);
    return 0;
  }

  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    let fixCount = 0;
    let hasChanges = false;

    // 修复指定行的错误
    errorLines.forEach(lineNumber => {
      const index = lineNumber - 1; // 转换为0基索引
      if (index >= 0 && index < lines.length) {
        const line = lines[index];
        const originalLine = line;

        // 检查是否是对象属性定义
        const propertyMatch = line.match(/^(\s*)(\w+):\s*([^,{}\[\]\n;]+?)(\s*)$/);
        if (propertyMatch) {
          const [, indent, prop, value, trailing] = propertyMatch;
          const trimmedValue = value.trim();

          // 检查下一行是否是同级属性或对象结束
          const nextLine = lines[index + 1];
          if (nextLine) {
            const nextPropertyMatch = nextLine.match(/^(\s*)(\w+):/);
            const nextCloseBrace = nextLine.trim().match(/^[}\]]/);

            // 如果下一行是同级属性且当前行没有逗号
            if (nextPropertyMatch && !trimmedValue.endsWith(',') && !trimmedValue.endsWith(';')) {
              const currentIndent = indent.length;
              const nextIndent = nextPropertyMatch[1].length;

              if (currentIndent === nextIndent) {
                lines[index] = `${indent}${prop}: ${trimmedValue},`;
                fixCount++;
                hasChanges = true;
              }
            }
          }
        }

        // 检查是否是接口属性定义
        const interfaceMatch = line.match(/^(\s*)(\w+)(\??):\s*([^,{}\[\]\n;]+?)(\s*)$/);
        if (interfaceMatch) {
          const [, indent, prop, optional, type, trailing] = interfaceMatch;
          const trimmedType = type.trim();

          // 检查下一行
          const nextLine = lines[index + 1];
          if (nextLine) {
            const nextInterfaceMatch = nextLine.match(/^(\s*)(\w+)(\??):/);
            const nextCloseBrace = nextLine.trim().match(/^[}\]]/);

            if (nextInterfaceMatch && !trimmedType.endsWith(',') && !trimmedType.endsWith(';')) {
              const currentIndent = indent.length;
              const nextIndent = nextInterfaceMatch[1].length;

              if (currentIndent === nextIndent) {
                lines[index] = `${indent}${prop}${optional}: ${trimmedType},`;
                fixCount++;
                hasChanges = true;
              }
            }
          }
        }
      }
    });

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

// 通用修复函数（用于没有具体行号的文件）
function fixFileGeneric(filePath) {
  if (!fs.existsSync(filePath)) {
    return 0;
  }

  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    let fixCount = 0;
    let hasChanges = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const nextLine = lines[i + 1];

      if (nextLine) {
        // 检查对象属性定义
        const propertyMatch = line.match(/^(\s*)(\w+):\s*([^,{}\[\]\n;]+?)(\s*)$/);
        const nextPropertyMatch = nextLine.match(/^(\s*)(\w+):/);
        const nextCloseBrace = nextLine.trim().match(/^[}\]]/);

        if (propertyMatch && nextPropertyMatch && !nextCloseBrace) {
          const [, indent, prop, value] = propertyMatch;
          const trimmedValue = value.trim();

          const currentIndent = indent.length;
          const nextIndent = nextPropertyMatch[1].length;

          if (currentIndent === nextIndent &&
              !trimmedValue.endsWith(',') &&
              !trimmedValue.endsWith(';') &&
              !trimmedValue.endsWith('{') &&
              !trimmedValue.endsWith('[')) {
            lines[i] = `${indent}${prop}: ${trimmedValue},`;
            fixCount++;
            hasChanges = true;
          }
        }
      }
    }

    if (hasChanges) {
      const fixedContent = lines.join('\n');
      fs.writeFileSync(filePath, fixedContent, 'utf8');
      console.log(`✅ ${filePath} (通用修复 ${fixCount} 处)`);
      return fixCount;
    }

    return 0;
  } catch (error) {
    console.error(`❌ ${filePath}: ${error.message}`);
    return 0;
  }
}

let totalFixCount = 0;
let fixedFileCount = 0;

console.log(`📁 处理 ${Object.keys(specificErrorFixes).length} 个有具体错误的文件\n`);

// 修复有具体错误行号的文件
Object.entries(specificErrorFixes).forEach(([filePath, errorLines]) => {
  const fixCount = fixFile(filePath, errorLines);
  if (fixCount > 0) {
    totalFixCount += fixCount;
    fixedFileCount++;
  }
});

console.log(`\n📊 最终手动修复报告`);
console.log(`==================================================`);
console.log(`📁 目标文件数: ${Object.keys(specificErrorFixes).length}`);
console.log(`🔧 已修复文件: ${fixedFileCount}`);
console.log(`✨ 总修复数: ${totalFixCount}`);
console.log(`📈 修复率: ${((fixedFileCount / Object.keys(specificErrorFixes).length) * 100).toFixed(1)}%`);
console.log(`🎯 最终手动修复完成！建议运行代码质量检查验证结果。`);
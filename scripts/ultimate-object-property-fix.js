#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const glob = require('glob');

console.log('🎯 开始终极对象属性修复...\n');

// 终极对象属性修复规则
const ultimateFixRules = [
  // 修复对象属性定义中缺少逗号的情况（最精确的匹配）
  {
    name: '对象属性定义缺少逗号',
    pattern: /^(\s*)(\w+):\s*([^,{}\[\]\n;]+?)(\s*\n\s*)(\w+):/gm,
    replacement: (match, indent1, prop1, value1, newline, prop2) => {
      const trimmedValue = value1.trim();
      // 检查是否已经有逗号、分号或其他结束符
      if (!trimmedValue.endsWith(',') && !trimmedValue.endsWith(';') && 
          !trimmedValue.endsWith('{') && !trimmedValue.endsWith('[') &&
          !trimmedValue.endsWith('}') && !trimmedValue.endsWith(']') &&
          !trimmedValue.endsWith(')')) {
        return `${indent1}${prop1}: ${trimmedValue},${newline}${prop2}:`;
      }
      return match;
    }
  },

  // 修复接口定义中的属性缺少逗号
  {
    name: '接口属性定义缺少逗号',
    pattern: /^(\s*)(\w+)(\??):\s*([^,{}\[\]\n;]+?)(\s*\n\s*)(\w+)(\??):(\s*)/gm,
    replacement: (match, indent1, prop1, optional1, type1, newline, prop2, optional2, colon) => {
      const trimmedType = type1.trim();
      if (!trimmedType.endsWith(',') && !trimmedType.endsWith(';') &&
          !trimmedType.endsWith('{') && !trimmedType.endsWith('[') &&
          !trimmedType.endsWith('}') && !trimmedType.endsWith(']')) {
        return `${indent1}${prop1}${optional1}: ${trimmedType},${newline}${prop2}${optional2}:${colon}`;
      }
      return match;
    }
  },

  // 修复对象字面量中的属性缺少逗号
  {
    name: '对象字面量属性缺少逗号',
    pattern: /^(\s*)(['"`]?\w+['"`]?):\s*([^,{}\[\]\n;]+?)(\s*\n\s*)(['"`]?\w+['"`]?):/gm,
    replacement: (match, indent1, prop1, value1, newline, prop2) => {
      const trimmedValue = value1.trim();
      if (!trimmedValue.endsWith(',') && !trimmedValue.endsWith(';') &&
          !trimmedValue.endsWith('{') && !trimmedValue.endsWith('[') &&
          !trimmedValue.endsWith('}') && !trimmedValue.endsWith(']')) {
        return `${indent1}${prop1}: ${trimmedValue},${newline}${prop2}:`;
      }
      return match;
    }
  },

  // 修复函数参数定义中的缺少逗号
  {
    name: '函数参数缺少逗号',
    pattern: /^(\s*)(\w+):\s*([^,{}\[\]\n;)]+?)(\s*\n\s*)(\w+):/gm,
    replacement: (match, indent1, param1, type1, newline, param2) => {
      const trimmedType = type1.trim();
      if (!trimmedType.endsWith(',') && !trimmedType.endsWith(';') &&
          !trimmedType.endsWith('{') && !trimmedType.endsWith('[') &&
          !trimmedType.endsWith('}') && !trimmedType.endsWith(']')) {
        return `${indent1}${param1}: ${trimmedType},${newline}${param2}:`;
      }
      return match;
    }
  },

  // 修复导入语句缺少分号
  {
    name: '导入语句缺少分号',
    pattern: /(import\s+[^;\n]+)(?!\s*;)(\n)/g,
    replacement: '$1;$2'
  },

  // 修复导出语句缺少分号
  {
    name: '导出语句缺少分号',
    pattern: /(export\s+[^;\n{]+)(?!\s*;)(\n)/g,
    replacement: '$1;$2'
  }
];

// 深度分析和修复对象属性
function deepAnalyzeAndFix(content) {
  const lines = content.split('\n');
  const fixedLines = [];
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    const nextLine = lines[i + 1];
    
    if (nextLine) {
      // 检查当前行是否是对象属性定义
      const currentMatch = line.match(/^(\s*)(\w+):\s*([^,{}\[\]\n;]+?)$/);
      const nextMatch = nextLine.match(/^(\s*)(\w+):/);
      const nextCloseBrace = nextLine.trim().match(/^[}\]]/);
      
      if (currentMatch && nextMatch && !nextCloseBrace) {
        const [, indent, prop, value] = currentMatch;
        const trimmedValue = value.trim();
        
        // 检查缩进级别是否相同（同级属性）
        const currentIndent = indent.length;
        const nextIndent = nextMatch[1].length;
        
        if (currentIndent === nextIndent && 
            !trimmedValue.endsWith(',') && 
            !trimmedValue.endsWith(';') &&
            !trimmedValue.endsWith('{') &&
            !trimmedValue.endsWith('[') &&
            !trimmedValue.endsWith('}') &&
            !trimmedValue.endsWith(']') &&
            !trimmedValue.endsWith(')')) {
          line = `${indent}${prop}: ${trimmedValue},`;
        }
      }
      
      // 检查接口定义
      const interfaceMatch = line.match(/^(\s*)(\w+)(\??):\s*([^,{}\[\]\n;]+?)$/);
      const nextInterfaceMatch = nextLine.match(/^(\s*)(\w+)(\??):/);
      
      if (interfaceMatch && nextInterfaceMatch && !nextCloseBrace) {
        const [, indent, prop, optional, type] = interfaceMatch;
        const trimmedType = type.trim();
        
        const currentIndent = indent.length;
        const nextIndent = nextInterfaceMatch[1].length;
        
        if (currentIndent === nextIndent && 
            !trimmedType.endsWith(',') && 
            !trimmedType.endsWith(';') &&
            !trimmedType.endsWith('{') &&
            !trimmedType.endsWith('[') &&
            !trimmedType.endsWith('}') &&
            !trimmedType.endsWith(']')) {
          line = `${indent}${prop}${optional}: ${trimmedType},`;
        }
      }

      // 检查StyleSheet对象属性
      const styleMatch = line.match(/^(\s*)(\w+):\s*\{$/);
      const nextStyleMatch = nextLine.match(/^(\s*)(\w+):\s*\{/);
      
      if (styleMatch && nextStyleMatch) {
        const currentIndent = styleMatch[1].length;
        const nextIndent = nextStyleMatch[1].length;
        
        if (currentIndent === nextIndent) {
          // 在前一行添加逗号
          if (i > 0 && !fixedLines[fixedLines.length - 1].endsWith(',')) {
            const prevLine = fixedLines[fixedLines.length - 1];
            if (prevLine.trim().endsWith('}')) {
              fixedLines[fixedLines.length - 1] = prevLine.replace(/}$/, '},');
            }
          }
        }
      }
    }
    
    fixedLines.push(line);
  }
  
  return fixedLines.join('\n');
}

// 特定文件的精确修复规则
const specificFileRules = {
  'src/agents/AgentCoordinator.tsx': (content) => {
    // 修复特定的语法错误
    content = content.replace(/return;(\s*\n\s*})/g, 'return;$1');
    content = content.replace(/(import\s+[^;\n]+)(?!\s*;)(\n)/g, '$1;$2');
    return content;
  },

  'src/agents/xiaoai/XiaoaiAgentImpl.tsx': (content) => {
    // 修复导入语句
    content = content.replace(/(import\s+[^;\n]+)(?!\s*;)(\n)/g, '$1;$2');
    return content;
  },

  'src/services/enhancedI18nService.tsx': (content) => {
    // 修复导入语句
    content = content.replace(/(import\s+[^;\n]+)(?!\s*;)(\n)/g, '$1;$2');
    return content;
  },

  'src/services/mlTrainingService.tsx': (content) => {
    // 修复导入语句
    content = content.replace(/(import\s+[^;\n]+)(?!\s*;)(\n)/g, '$1;$2');
    return content;
  },

  'src/utils/codeSplitting.tsx': (content) => {
    // 修复导入语句
    content = content.replace(/(import\s+[^;\n]+)(?!\s*;)(\n)/g, '$1;$2');
    return content;
  },

  'src/utils/lazyLoader.tsx': (content) => {
    // 修复导入语句
    content = content.replace(/(import\s+[^;\n]+)(?!\s*;)(\n)/g, '$1;$2');
    return content;
  }
};

// 获取有错误的文件列表（从代码质量检查报告中提取）
const errorFiles = [
  'src/agents/AgentCoordinator.tsx',
  'src/agents/base/BaseAgent.ts',
  'src/agents/config/agents.config.tsx',
  'src/agents/soer/SoerAgentImpl.ts',
  'src/agents/types.ts',
  'src/agents/xiaoai/XiaoaiAgentImpl.tsx',
  'src/agents/xiaoai/services/DiagnosisServiceClient.tsx',
  'src/agents/xiaoai/types.tsx',
  'src/algorithms/FiveDiagnosisEngine.tsx',
  'src/algorithms/modules/CalculationDiagnosisAlgorithm.tsx',
  'src/algorithms/quality/QualityController.tsx',
  'src/components/AgentAvatar.tsx',
  'src/components/blockchain/BlockchainDataManager.tsx',
  'src/components/common/AccessibilitySettings.tsx',
  'src/components/common/AgentChatInterface.tsx',
  'src/components/common/AuthButton.tsx',
  'src/components/common/AuthInput.tsx',
  'src/components/common/ContactsList.tsx',
  'src/components/common/DeviceTestDashboard.tsx',
  'src/components/common/Input.tsx',
  'src/components/diagnosis/FiveDiagnosisScreen.tsx',
  'src/components/health/EnhancedHealthVisualization.tsx',
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
  'src/services/enhancedI18nService.tsx',
  'src/services/graphql/client.tsx',
  'src/services/logisticsService.tsx',
  'src/services/medicalApiService.tsx',
  'src/services/mlTrainingService.tsx',
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
  'src/utils/codeSplitting.tsx',
  'src/utils/errorHandler.ts',
  'src/utils/lazyLoader.tsx',
  'src/utils/monitoringSystem.tsx',
  'src/utils/nativeModules.tsx',
  'src/utils/performanceOptimizer.tsx',
  'src/utils/performanceReporter.tsx',
  'src/utils/responsive.tsx',
  'src/utils/securityManager.tsx',
  'src/utils/smartCacheStrategy.tsx',
  'src/utils/stateOptimizer.ts'
];

let totalFixCount = 0;
let fixedFileCount = 0;

console.log(`📁 处理 ${errorFiles.length} 个有错误的文件\n`);

errorFiles.forEach(file => {
  if (!fs.existsSync(file)) {
    console.log(`⚠️ ${file} 文件不存在，跳过`);
    return;
  }

  try {
    let content = fs.readFileSync(file, 'utf8');
    let originalContent = content;
    let fileFixCount = 0;

    // 应用特定文件修复规则
    if (specificFileRules[file]) {
      const beforeContent = content;
      content = specificFileRules[file](content);
      if (content !== beforeContent) {
        fileFixCount += 1;
      }
    }

    // 应用终极修复规则
    ultimateFixRules.forEach(rule => {
      if (typeof rule.replacement === 'function') {
        const beforeContent = content;
        content = content.replace(rule.pattern, rule.replacement);
        if (content !== beforeContent) {
          fileFixCount += 1;
        }
      } else {
        const beforeMatches = content.match(rule.pattern);
        if (beforeMatches) {
          content = content.replace(rule.pattern, rule.replacement);
          const afterMatches = content.match(rule.pattern);
          const fixedCount = (beforeMatches ? beforeMatches.length : 0) - (afterMatches ? afterMatches.length : 0);
          if (fixedCount > 0) {
            fileFixCount += fixedCount;
          }
        }
      }
    });

    // 应用深度分析和修复
    const beforeDeepFix = content;
    content = deepAnalyzeAndFix(content);
    if (content !== beforeDeepFix) {
      fileFixCount += 1;
    }

    // 最终清理
    content = content.replace(/\s+$/gm, ''); // 清理行尾空格
    content = content.replace(/;;+/g, ';'); // 清理多余分号
    content = content.replace(/,,+/g, ','); // 清理多余逗号
    content = content.replace(/,(\s*[}\]])/g, '$1'); // 清理对象/数组末尾多余逗号
    content = content.replace(/,(\s*\))/g, '$1'); // 清理函数参数末尾多余逗号

    // 如果内容有变化，写入文件
    if (content !== originalContent) {
      fs.writeFileSync(file, content, 'utf8');
      console.log(`✅ ${file} (修复 ${fileFixCount} 处)`);
      totalFixCount += fileFixCount;
      fixedFileCount++;
    }

  } catch (error) {
    console.error(`❌ ${file}: ${error.message}`);
  }
});

console.log(`\n📊 终极对象属性修复报告`);
console.log(`==================================================`);
console.log(`📁 目标文件数: ${errorFiles.length}`);
console.log(`🔧 已修复文件: ${fixedFileCount}`);
console.log(`✨ 总修复数: ${totalFixCount}`);
console.log(`📈 修复率: ${((fixedFileCount / errorFiles.length) * 100).toFixed(1)}%`);
console.log(`🎯 终极对象属性修复完成！建议运行代码质量检查验证结果。`); 
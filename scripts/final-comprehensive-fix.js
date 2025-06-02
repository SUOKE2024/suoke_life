#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🎯 开始最终综合修复...\n');

// 最终综合修复规则
const finalComprehensiveRules = [
  // 修复接口定义中的属性缺少分号或逗号
  {
    name: '接口属性定义修复',
    pattern: /^(\s*)(\w+)(\??):\s*([^,;{}\[\]\n]+?)([\s]*)([\n])/gm,
    replacement: (match, indent, prop, optional, type, space, newline) => {
      const trimmedType = type.trim();
      // 检查是否已经有分号或逗号
      if (!trimmedType.endsWith(';') && !trimmedType.endsWith(',')) {
        return `${indent}${prop}${optional}: ${trimmedType};${newline}`;
      }
      return match;
    }
  },

  // 修复对象字面量中的属性缺少逗号
  {
    name: '对象字面量属性修复',
    pattern: /^(\s*)(['\"`]?\w+['\"`]?):\s*([^,{}\[\]\n;]+?)([\s]*)([\n]\s*)(['\"`]?\w+['\"`]?|[\}])/gm,
    replacement: (match, indent, prop, value, space, newline, nextProp) => {
      const trimmedValue = value.trim();
      // 如果下一个是属性名（不是}），且当前值没有逗号，则添加逗号
      if (nextProp !== '}' && !trimmedValue.endsWith(',') && !trimmedValue.endsWith(';')) {
        return `${indent}${prop}: ${trimmedValue},${newline}${nextProp}`;
      }
      return match;
    }
  },

  // 修复函数参数中的类型定义
  {
    name: '函数参数类型修复',
    pattern: /(\w+):\s*([^,)]+?)(\s*)([,)])/g,
    replacement: (match, param, type, space, delimiter) => {
      const trimmedType = type.trim();
      return `${param}: ${trimmedType}${delimiter}`;
    }
  },

  // 修复数组类型定义
  {
    name: '数组类型定义修复',
    pattern: /:\s*([^,;{}\[\]\n]+?)\[\](\s*[,;]?)/g,
    replacement: ': $1[]$2'
  },

  // 修复泛型类型定义
  {
    name: '泛型类型定义修复',
    pattern: /:\s*(\w+)<([^>]+?)>(\s*[,;]?)/g,
    replacement: ': $1<$2>$3'
  },

  // 修复联合类型定义
  {
    name: '联合类型定义修复',
    pattern: /:\s*([^,;{}\[\]\n|]+?)\s*\|\s*([^,;{}\[\]\n|]+?)(\s*[,;]?)/g,
    replacement: ': $1 | $2$3'
  },

  // 修复可选属性定义
  {
    name: '可选属性定义修复',
    pattern: /(\w+)\?\s*:\s*([^,;{}\[\]\n]+?)(\s*[,;]?)/g,
    replacement: '$1?: $2$3'
  },

  // 修复方法定义
  {
    name: '方法定义修复',
    pattern: /^(\s*)(\w+)\s*\(\s*([^)]*?)\s*\)\s*:\s*([^,;{}\[\]\n]+?)(\s*[,;]?)/gm,
    replacement: '$1$2($3): $4$5'
  },

  // 修复导入语句缺少分号
  {
    name: '导入语句分号修复',
    pattern: /^(import\s+.*?from\s+['\"][^'\"]*['\"])(\s*)$/gm,
    replacement: '$1;$2'
  },

  // 修复导出语句缺少分号
  {
    name: '导出语句分号修复',
    pattern: /^(export\s+.*?)(\s*)$/gm,
    replacement: (match, exportStmt, space) => {
      if (!exportStmt.trim().endsWith(';') && !exportStmt.includes('{')) {
        return `${exportStmt};${space}`;
      }
      return match;
    }
  },

  // 修复变量声明缺少分号
  {
    name: '变量声明分号修复',
    pattern: /^(\s*)(const|let|var)\s+([^=]+?)\s*=\s*([^;\n]+?)(\s*)$/gm,
    replacement: (match, indent, keyword, varName, value, space) => {
      const trimmedValue = value.trim();
      if (!trimmedValue.endsWith(';')) {
        return `${indent}${keyword} ${varName.trim()} = ${trimmedValue};${space}`;
      }
      return match;
    }
  }
];

// 特殊文件修复规则
const specialFileRules = {
  'src/components/ui/Button.tsx': [
    {
      pattern: /^(\s*)(\w+):\s*([^,{}\[\]\n;]+?)([\s]*)([\n]\s*)(\w+|[\}])/gm,
      replacement: (match, indent, prop, value, space, newline, next) => {
        if (next !== '}' && !value.trim().endsWith(',')) {
          return `${indent}${prop}: ${value.trim()},${newline}${next}`;
        }
        return match;
      }
    }
  ],
  'src/utils/responsive.tsx': [
    {
      pattern: /^(\s*)(\w+):\s*([^,{}\[\]\n;]+?)([\s]*)([\n]\s*)(\w+|[\}])/gm,
      replacement: (match, indent, prop, value, space, newline, next) => {
        if (next !== '}' && !value.trim().endsWith(',')) {
          return `${indent}${prop}: ${value.trim()},${newline}${next}`;
        }
        return match;
      }
    }
  ],
  'src/utils/animations.ts': [
    {
      pattern: /^(\s*)(\w+):\s*([^,{}\[\]\n;]+?)([\s]*)([\n]\s*)(\w+|[\}])/gm,
      replacement: (match, indent, prop, value, space, newline, next) => {
        if (next !== '}' && !value.trim().endsWith(',')) {
          return `${indent}${prop}: ${value.trim()},${newline}${next}`;
        }
        return match;
      }
    }
  ]
};

// 修复文件函数
function fixFile(filePath) {
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️ ${filePath} 文件不存在，跳过`);
    return 0;
  }

  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let fixCount = 0;
    let originalContent = content;

    // 应用通用修复规则
    finalComprehensiveRules.forEach(rule => {
      const beforeLength = content.length;
      if (typeof rule.replacement === 'function') {
        content = content.replace(rule.pattern, rule.replacement);
      } else {
        content = content.replace(rule.pattern, rule.replacement);
      }
      const afterLength = content.length;
      if (beforeLength !== afterLength) {
        fixCount++;
      }
    });

    // 应用特殊文件规则
    if (specialFileRules[filePath]) {
      specialFileRules[filePath].forEach(rule => {
        const beforeLength = content.length;
        content = content.replace(rule.pattern, rule.replacement);
        const afterLength = content.length;
        if (beforeLength !== afterLength) {
          fixCount++;
        }
      });
    }

    // 如果有变化，写入文件
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content, 'utf8');
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
const errorFiles = [
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

console.log(`\n📊 最终综合修复报告`);
console.log(`==================================================`);
console.log(`📁 目标文件数: ${errorFiles.length}`);
console.log(`🔧 已修复文件: ${fixedFileCount}`);
console.log(`✨ 总修复数: ${totalFixCount}`);
console.log(`📈 修复率: ${((fixedFileCount / errorFiles.length) * 100).toFixed(1)}%`);
console.log(`🎯 最终综合修复完成！建议运行代码质量检查验证结果。`); 
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// UI组件目录
const UI_COMPONENTS_DIR = path.join(__dirname, '../components/ui');

// 预期的UI组件列表
const EXPECTED_COMPONENTS = [
  // 基础组件
  'Avatar',
  'Badge',
  'Button',
  'Card',
  'Container',
  'Divider',
  'Input',
  'Loading',
  'Modal',
  'Text',

  // 表单组件
  'Radio',
  'Slider',
  'Switch',
  'DatePicker',
  'TimePicker',
  'ColorPicker',
  'ImagePicker',
  'FileUpload',

  // 交互组件
  'Tooltip',
  'Rating',
  'Progress',
  'Calendar',
  'Chip',
  'Accordion',
  'Stepper',
  'Tabs',
  'Drawer',
  'Popover',

  // 反馈组件
  'Skeleton',
  'ErrorBoundary',
  'Badge',
  'Notification',
  'Toast',

  // 状态组件
  'LoadingState',
  'ErrorState',
  'EmptyState',
  'RefreshControl',
  'PullToRefresh',

  // 数据展示组件
  'Table',
  'DataDisplay',
  'StatCard',
  'Chart',

  // 搜索和过滤
  'SearchBar',
  'SearchFilter',
  'Pagination',

  // 特色组件
  'AccessibilityPanel',
  'AgentAvatar',
  'EnhancedButton',
  'PerformanceMonitor',
  'ThemeToggle',
];

// 检查组件文件是否存在
function checkComponentFiles() {
  const existingComponents = [];
  const missingComponents = [];

  EXPECTED_COMPONENTS.forEach((component) => {
    const componentPath = path.join(UI_COMPONENTS_DIR, `${component}.tsx`);
    if (fs.existsSync(componentPath)) {
      existingComponents.push(component);
    } else {
      missingComponents.push(component);
    }
  });

  return { existingComponents, missingComponents };
}

// 检查组件导出
function checkComponentExports() {
  const indexPath = path.join(UI_COMPONENTS_DIR, 'index.ts');

  if (!fs.existsSync(indexPath)) {
    return { exported: [], notExported: EXPECTED_COMPONENTS };
  }

  const indexContent = fs.readFileSync(indexPath, 'utf8');
  const exported = [];
  const notExported = [];

  EXPECTED_COMPONENTS.forEach((component) => {
    if (
      indexContent.includes(`export { ${component} }`) ||
      indexContent.includes(`export { default as ${component} }`)
    ) {
      exported.push(component);
    } else {
      notExported.push(component);
    }
  });

  return { exported, notExported };
}

// 检查组件质量
function checkComponentQuality() {
  const qualityReport = {
    withTests: [],
    withoutTests: [],
    withTypes: [],
    withoutTypes: [],
    withDocs: [],
    withoutDocs: [],
  };

  EXPECTED_COMPONENTS.forEach((component) => {
    const componentPath = path.join(UI_COMPONENTS_DIR, `${component}.tsx`);
    const testPath = path.join(
      UI_COMPONENTS_DIR,
      '__tests__',
      `${component}.test.tsx`
    );
    const docsPath = path.join(
      __dirname,
      '../docs/components',
      `${component}.md`
    );

    if (fs.existsSync(componentPath)) {
      const content = fs.readFileSync(componentPath, 'utf8');

      // 检查测试文件
      if (fs.existsSync(testPath)) {
        qualityReport.withTests.push(component);
      } else {
        qualityReport.withoutTests.push(component);
      }

      // 检查TypeScript类型
      if (content.includes('interface') && content.includes('Props')) {
        qualityReport.withTypes.push(component);
      } else {
        qualityReport.withoutTypes.push(component);
      }

      // 检查文档
      if (fs.existsSync(docsPath)) {
        qualityReport.withDocs.push(component);
      } else {
        qualityReport.withoutDocs.push(component);
      }
    }
  });

  return qualityReport;
}

// 生成报告
function generateReport() {
  console.log('🔍 索克生活 UI 组件库完成度检查报告');
  console.log('='.repeat(50));

  const { existingComponents, missingComponents } = checkComponentFiles();
  const { exported, notExported } = checkComponentExports();
  const qualityReport = checkComponentQuality();

  // 基本统计
  const totalComponents = EXPECTED_COMPONENTS.length;
  const existingCount = existingComponents.length;
  const exportedCount = exported.length;
  const completionRate = ((existingCount / totalComponents) * 100).toFixed(1);
  const exportRate = ((exportedCount / totalComponents) * 100).toFixed(1);

  console.log(`\n📊 总体统计:`);
  console.log(`   预期组件总数: ${totalComponents}`);
  console.log(`   已实现组件: ${existingCount} (${completionRate}%)`);
  console.log(`   已导出组件: ${exportedCount} (${exportRate}%)`);

  // 缺失组件
  if (missingComponents.length > 0) {
    console.log(`\n❌ 缺失组件 (${missingComponents.length}):`);
    missingComponents.forEach((component) => {
      console.log(`   - ${component}`);
    });
  }

  // 未导出组件
  if (notExported.length > 0) {
    console.log(`\n⚠️  未导出组件 (${notExported.length}):`);
    notExported.forEach((component) => {
      console.log(`   - ${component}`);
    });
  }

  // 质量报告
  console.log(`\n📋 质量报告:`);
  console.log(
    `   有类型定义: ${qualityReport.withTypes.length}/${existingCount}`
  );
  console.log(
    `   有测试文件: ${qualityReport.withTests.length}/${existingCount}`
  );
  console.log(
    `   有文档说明: ${qualityReport.withDocs.length}/${existingCount}`
  );

  if (qualityReport.withoutTypes.length > 0) {
    console.log(`\n🔧 缺少类型定义:`);
    qualityReport.withoutTypes.forEach((component) => {
      console.log(`   - ${component}`);
    });
  }

  if (qualityReport.withoutTests.length > 0) {
    console.log(`\n🧪 缺少测试文件:`);
    qualityReport.withoutTests.forEach((component) => {
      console.log(`   - ${component}`);
    });
  }

  // 完成度评估
  console.log(`\n🎯 完成度评估:`);
  if (completionRate >= 95) {
    console.log(`   ✅ 优秀! UI组件库基本完成 (${completionRate}%)`);
  } else if (completionRate >= 80) {
    console.log(`   🟡 良好! 大部分组件已完成 (${completionRate}%)`);
  } else if (completionRate >= 60) {
    console.log(`   🟠 一般! 还需要继续完善 (${completionRate}%)`);
  } else {
    console.log(`   🔴 需要努力! 组件库还不完整 (${completionRate}%)`);
  }

  // 下一步建议
  console.log(`\n💡 下一步建议:`);
  if (missingComponents.length > 0) {
    console.log(`   1. 优先实现缺失的核心组件`);
  }
  if (notExported.length > 0) {
    console.log(`   2. 修复组件导出问题`);
  }
  if (qualityReport.withoutTypes.length > 0) {
    console.log(`   3. 完善组件类型定义`);
  }
  if (qualityReport.withoutTests.length > 0) {
    console.log(`   4. 添加组件测试用例`);
  }

  console.log(`\n🎉 继续加油，目标100%完成度!`);
  console.log('='.repeat(50));
}

// 运行检查
if (require.main === module) {
  generateReport();
}

module.exports = {
  checkComponentFiles,
  checkComponentExports,
  checkComponentQuality,
  generateReport,
};
